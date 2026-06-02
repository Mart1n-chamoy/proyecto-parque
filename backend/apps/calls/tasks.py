"""
Celery tasks para procesamiento asincrónico de llamadas
"""

import logging
from django.utils import timezone
from celery import shared_task

from apps.calls.models import Call, CallBatch
from apps.calls.elevenlabs_service import elevenlabs_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_call_audio(self, call_id: int, text: str, voice_key: str = 'spanish_male'):
    """
    Tarea para generar audio de una llamada de forma asincrónica
    
    Args:
        call_id: ID de la llamada
        text: Texto a convertir en audio
        voice_key: Tipo de voz a usar
    """
    try:
        call = Call.objects.get(id=call_id)
        
        # Actualizar estado a "en progreso"
        call.status = 'in_progress'
        call.started_at = timezone.now()
        call.save()
        
        # Generar audio
        audio_bytes = elevenlabs_service.text_to_speech(text, voice_key)
        
        if audio_bytes:
            # Guardar archivo de audio
            filename = f"call_{call_id}_{timezone.now().timestamp()}.mp3"
            filepath = f"calls/{call.client.id}/{filename}"
            
            call.audio_file.save(filepath, audio_bytes)
            call.status = 'completed'
            call.completed_at = timezone.now()
            call.transcript = text
            call.save()
            
            logger.info(f"Audio generado exitosamente para llamada {call_id}")
        else:
            raise Exception("No se pudo generar el audio")
    
    except Call.DoesNotExist:
        logger.error(f"Llamada {call_id} no encontrada")
    except Exception as exc:
        logger.error(f"Error generando audio: {str(exc)}")
        # Reintentar tarea
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True)
def process_call_batch(self, batch_id: int):
    """
    Tarea para procesar un lote de llamadas
    
    Args:
        batch_id: ID del lote de llamadas
    """
    try:
        batch = CallBatch.objects.get(id=batch_id)
        
        # Actualizar estado del lote
        batch.status = 'processing'
        batch.started_at = timezone.now()
        batch.save()
        
        # Procesar todas las llamadas del lote
        calls = batch.calls.filter(status='pending')
        
        for call in calls:
            # Generar texto de llamada
            text = f"Hola {call.client.first_name}, este es un aviso de cobranza"
            
            # Crear tarea asincrónica para generar audio
            generate_call_audio.delay(call.id, text)
        
        logger.info(f"Lote {batch_id} iniciado con {calls.count()} llamadas")
    
    except CallBatch.DoesNotExist:
        logger.error(f"Lote {batch_id} no encontrado")
    except Exception as exc:
        logger.error(f"Error procesando lote: {str(exc)}")


@shared_task
def check_batch_completion():
    """
    Tarea periódica para verificar si los lotes están completados
    Se ejecuta cada 5 minutos
    """
    try:
        # Buscar lotes en procesamiento
        processing_batches = CallBatch.objects.filter(status='processing')
        
        for batch in processing_batches:
            # Contar llamadas pendientes
            pending_calls = batch.calls.filter(status='pending').count()
            processed_calls = batch.calls.exclude(status='pending').count()
            
            # Actualizar contador
            batch.processed_clients = processed_calls
            batch.save()
            
            # Si no hay llamadas pendientes, marcar como completado
            if pending_calls == 0 and processed_calls > 0:
                batch.status = 'completed'
                batch.completed_at = timezone.now()
                batch.save()
                logger.info(f"Lote {batch.id} completado")
    
    except Exception as exc:
        logger.error(f"Error en check_batch_completion: {str(exc)}")


@shared_task(bind=True, max_retries=2)
def retry_failed_call(self, call_id: int):
    """
    Tarea para reintentar una llamada fallida
    
    Args:
        call_id: ID de la llamada a reintentar
    """
    try:
        call = Call.objects.get(id=call_id)
        
        if call.status != 'failed':
            logger.warning(f"Llamada {call_id} no está en estado fallido")
            return
        
        # Resetear estado a pendiente
        call.status = 'pending'
        call.error_message = ''
        call.save()
        
        # Generar audio nuevamente
        text = f"Hola {call.client.first_name}, este es un aviso de cobranza"
        generate_call_audio.delay(call.id, text)
        
        logger.info(f"Llamada {call_id} reenviada")
    
    except Call.DoesNotExist:
        logger.error(f"Llamada {call_id} no encontrada")
    except Exception as exc:
        logger.error(f"Error reintentando llamada: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)
