"""
apps/calls/tasks.py

Tareas Celery para el procesamiento asincrónico de lotes de llamadas.

Flujo completo:
  1. process_call_batch(batch_id)   → lanza el lote en ElevenLabs
  2. check_batch_completion()       → tarea periódica (cada 5 min) que revisa
                                       el estado de todos los lotes en curso
  3. fetch_call_results(...)        → descarga audio + transcripción por llamada
  4. retry_failed_call(call_id)     → reintenta una llamada fallida

Requisito: Celery + Redis ya configurados en proyecto_cobranza/celery.py
"""

import os
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# TAREA 1: Lanzar lote en ElevenLabs
# ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_call_batch(self, batch_id: int):
    """
    Toma un BatchCall de la DB, arma la lista de recipients a partir
    de los clientes asociados, y lanza el lote en ElevenLabs.

    Llamar desde la view con:
        process_call_batch.delay(batch.id)
    """
    # Import acá adentro para evitar import circular con Django
    from apps.calls.models import CallBatch, Call
    from apps.calls.elevenlabs_service import elevenlabs_service

    try:
        batch = CallBatch.objects.get(id=batch_id)
    except CallBatch.DoesNotExist:
        logger.error(f"BatchCall {batch_id} no encontrado")
        return

    if batch.status != "pending":
        logger.warning(f"BatchCall {batch_id} no está en estado pending (estado: {batch.status})")
        return

    # Armar lista de destinatarios desde las llamadas del lote
    calls = Call.objects.filter(batch=batch).select_related("client")

    if not calls.exists():
        logger.error(f"BatchCall {batch_id} no tiene llamadas asociadas")
        batch.status = "failed"
        batch.save(update_fields=["status"])
        return

    recipients = []
    for call in calls:
        client = call.client
        if not client.phone:
            logger.warning(f"Cliente {client.id} sin teléfono, omitiendo")
            continue
        recipients.append({
            "phone_number": client.phone,   # debe ser formato E.164: +5491155...
            "name": f"{client.first_name} {client.last_name}".strip(),
            "amount":       str(client.debt_amount or ""),
            "currency":     getattr(client, "currency", "ARS"),
            # Guardamos el call.id para matchear cuando lleguen los resultados
            "_call_id":     call.id,
        })

    if not recipients:
        logger.error(f"BatchCall {batch_id}: ningún destinatario válido")
        batch.status = "failed"
        batch.save(update_fields=["status"])
        return

    # Lanzar el lote en ElevenLabs
    try:
        el_batch_id = elevenlabs_service.create_batch(recipients)
    except Exception as exc:
        logger.error(f"Error al crear lote en ElevenLabs: {exc}")
        # Reintenta hasta 3 veces con delay de 60s
        raise self.retry(exc=exc)

    # Actualizar estado en DB
    batch.elevenlabs_batch_id = el_batch_id
    batch.status = "processing"
    batch.started_at = timezone.now()
    batch.save(update_fields=["elevenlabs_batch_id", "status", "started_at"])

    # Marcar todas las llamadas del lote como "in_progress"
    calls.update(status="in_progress")

    logger.info(
        f"BatchCall {batch_id} lanzado correctamente. "
        f"ElevenLabs batch_id: {el_batch_id}. "
        f"Destinatarios: {len(recipients)}"
    )
    return el_batch_id


# ─────────────────────────────────────────────────────────────────
# TAREA 2: Tarea periódica — revisar estado de lotes en curso
# ─────────────────────────────────────────────────────────────────

@shared_task
def check_batch_completion():
    """
    Tarea periódica (configurada en celery.py para correr cada 5 min).
    Revisa todos los BatchCall en estado "processing" y consulta
    ElevenLabs para ver si terminaron.

    Cuando un lote completa, lanza fetch_call_results() para cada
    llamada finalizada.
    """
    from apps.calls.models import CallBatch
    from apps.calls.elevenlabs_service import elevenlabs_service

    batches_en_curso = CallBatch.objects.filter(status="processing")

    if not batches_en_curso.exists():
        logger.debug("check_batch_completion: no hay lotes en curso")
        return

    for batch in batches_en_curso:
        if not batch.elevenlabs_batch_id:
            continue

        try:
            el_batch = elevenlabs_service.get_batch(batch.elevenlabs_batch_id)
        except Exception as exc:
            logger.error(f"Error consultando lote {batch.elevenlabs_batch_id}: {exc}")
            continue

        el_status = el_batch.get("status", "")
        calls_data = el_batch.get("recipients", el_batch.get("call_recipients", []))

        # Procesar cada llamada individual del lote
        for call_data in calls_data:
            conv_id     = call_data.get("conversation_id")
            call_status = call_data.get("status")
            phone       = call_data.get("phone_number","")

            if phone and not phone.startswith("+"):
                phone = "+" + phone
            if call_status == "completed" and conv_id:
                fetch_call_results.delay(
                    el_conversation_id=conv_id,
                    phone_number=phone,
                    batch_id=batch.id,
                )

        # Si el lote completo terminó, actualizar el BatchCall
        if el_status in ("completed", "done", "finished"):
            batch.status = "completed"
            # Asegurarse de disparar fetch para todas las llamadas completadas
            for call_data in calls_data:
                conv_id = call_data.get("conversation_id")
                call_status = call_data.get("status")
                phone = call_data.get("phone_number", "")
                if not phone.startswith("+"):
                    phone = "+" + phone
                if call_status == "completed" and conv_id:
                    fetch_call_results.delay(
                        el_conversation_id=conv_id,
                        phone_number=phone,
                        batch_id=batch.id,
                    )
            batch.completed_at = timezone.now()
            batch.save(update_fields=["status", "completed_at"])
            logger.info(f"BatchCall {batch.id} completado")

        elif el_status == "failed":
            batch.status = "failed"
            batch.save(update_fields=["status"])
            logger.warning(f"BatchCall {batch.id} falló en ElevenLabs")


# ─────────────────────────────────────────────────────────────────
# TAREA 3: Bajar audio + transcripción de una conversación
# ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def fetch_call_results(self, el_conversation_id: str, phone_number: str, batch_id: int):
    """
    Descarga el audio y la transcripción de una conversación finalizada
    y los guarda en la DB.

    Busca la Call correspondiente por teléfono + lote, guarda
    el transcript en el campo transcript_text y el audio en media/calls/.
    """
    from apps.calls.models import Call, CallBatch
    from apps.calls.elevenlabs_service import elevenlabs_service

    # Buscar la Call en la DB
    try:
        batch = CallBatch.objects.get(id=batch_id)
        # Buscar con o sin el + al inicio
        phone_variants = [phone_number, phone_number.lstrip("+")]
        call  = Call.objects.get(batch=batch, client__phone__in=phone_variants)
    except (CallBatch.DoesNotExist, Call.DoesNotExist, Call.MultipleObjectsReturned):
        logger.error(
            f"No se encontró Call para batch={batch_id}, phone={phone_number}"
        )
        return

    # Ya procesada
    if call.elevenlabs_conversation_id:
        return

    try:
        # Obtener datos de la conversación
        conv_data = elevenlabs_service.get_conversation(el_conversation_id)

        # Extraer transcripción como texto plano
        transcript = elevenlabs_service.extract_transcript_text(conv_data)

        # Extraer outcome del análisis de ElevenLabs (si está disponible)
        analysis = conv_data.get("analysis", {})
        outcome  = analysis.get("call_successful") or analysis.get("outcome", "unknown")

        # Detectar si fue buzón de voz por el transcript
        voicemail_keywords = [
            "contestador", "voicemail", "buzon", "buzón",
            "despues del tono", "después del tono",
            "deja tu mensaje", "dejá tu mensaje", "dejar un mensaje",
            "no disponible", "no esta disponible", "no está disponible",
            "leave a message", "not available", "after the tone",
            "at the beep", "record your message"
        ]
        transcript_lower = transcript.lower()
        summary_lower = (analysis.get("transcript_summary") or "").lower()
        is_voicemail = (
            any(kw in transcript_lower for kw in voicemail_keywords) or
            any(kw in summary_lower for kw in ["voicemail", "contestador", "buzón"])
        )
        if is_voicemail:
            outcome = "voicemail"
            call_status_override = "failed"

        else:
            call_status_override = "completed"
        # Guardar audio en media/calls/{call_id}.mp3
        audio_bytes   = elevenlabs_service.get_conversation_audio(el_conversation_id)
        audio_filename = _save_audio_file(call.id, audio_bytes)

        # Actualizar la llamada en DB
        call.elevenlabs_conversation_id = el_conversation_id
        call.transcript = transcript
        call.audio_file      = audio_filename
        call.outcome         = str(outcome)
        call.status          = call_status_override
        call.duration = conv_data.get("metadata", {}).get("call_duration_secs")
        call.completed_at    = timezone.now()
        call.save()

        logger.info(f"Resultados guardados para Call {call.id} (conv: {el_conversation_id})")

    except Exception as exc:
        logger.error(f"Error obteniendo resultados de conversación {el_conversation_id}: {exc}")
        raise self.retry(exc=exc)


def _save_audio_file(call_id: int, audio_bytes: bytes) -> str:
    """
    Guarda los bytes de audio en media/calls/ y retorna el path relativo.
    """
    import os
    from django.conf import settings

    audio_dir = os.path.join(settings.MEDIA_ROOT, "calls")
    os.makedirs(audio_dir, exist_ok=True)

    filename   = f"call_{call_id}.mp3"
    filepath   = os.path.join(audio_dir, filename)

    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    return f"calls/{filename}"


# ─────────────────────────────────────────────────────────────────
# TAREA 4: Reintentar una llamada fallida
# ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def retry_failed_call(self, call_id: int):
    """
    Reintenta una llamada individual que falló.
    Crea un lote de un solo destinatario en ElevenLabs.

    Llamar desde la view /api/calls/{id}/retry/ con:
        retry_failed_call.delay(call.id)
    """
    from apps.calls.models import Call
    from apps.calls.elevenlabs_service import elevenlabs_service

    try:
        call = Call.objects.select_related("client", "batch").get(id=call_id)
    except Call.DoesNotExist:
        logger.error(f"Call {call_id} no encontrada para retry")
        return

    client = call.client

    if not client.phone:
        logger.error(f"Cliente {client.id} no tiene teléfono, no se puede reintentar")
        return

    recipients = [{
        "phone_number": client.phone,
        "name": f"{client.first_name} {client.last_name}".strip(),
        "amount":       str(client.debt_amount or ""),
        "currency":     getattr(client, "currency", "ARS"),
    }]

    try:
        el_batch_id = elevenlabs_service.create_batch(recipients)
        call.status = "in_progress"
        call.retry_count = (call.retry_count or 0) + 1
        call.save(update_fields=["status", "retry_count"])
        logger.info(f"Reintento de Call {call_id} lanzado. EL batch: {el_batch_id}")
    except Exception as exc:
        logger.error(f"Error en reintento de Call {call_id}: {exc}")
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────────────────────────
# TAREA 5: Enviar lote de mensajes de WhatsApp
# ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def process_whatsapp_batch(self, batch_id: int):
    """
    Envía un mensaje de WhatsApp (con template aprobado en Meta) a cada
    cliente del lote. A diferencia de las llamadas, el envío de WhatsApp
    es síncrono por destinatario (no hay un "batch job" en ElevenLabs
    para WhatsApp), así que este task resuelve el lote completo.

    Llamar desde la view con:
        process_whatsapp_batch.delay(batch.id)
    """
    from apps.calls.models import CallBatch, Call
    from apps.calls.elevenlabs_service import elevenlabs_service

    try:
        batch = CallBatch.objects.get(id=batch_id)
    except CallBatch.DoesNotExist:
        logger.error(f"CallBatch {batch_id} no encontrado")
        return

    if batch.channel != "whatsapp":
        logger.warning(f"CallBatch {batch_id} no es de canal whatsapp (es '{batch.channel}')")
        return

    if not batch.whatsapp_template_name:
        logger.error(f"CallBatch {batch_id} no tiene whatsapp_template_name configurado")
        batch.status = "failed"
        batch.save(update_fields=["status"])
        return

    calls = Call.objects.filter(batch=batch, channel="whatsapp").select_related("client")

    if not calls.exists():
        logger.error(f"CallBatch {batch_id} no tiene mensajes de WhatsApp asociados")
        batch.status = "failed"
        batch.save(update_fields=["status"])
        return

    batch.status = "processing"
    batch.started_at = timezone.now()
    batch.save(update_fields=["status", "started_at"])

    sent, failed = 0, 0

    for call in calls:
        client = call.client
        if not client.phone:
            logger.warning(f"Cliente {client.id} sin teléfono, omitiendo")
            continue

        # NOTA: plantilla01 y plantilla03 (las únicas aprobadas hoy en Meta)
        # no tienen variables {{1}}, {{2}}, así que no mandamos template_params.
        # Cuando exista un template con variables (ej: nombre + monto + vencimiento),
        # reemplazar esta lista por los valores reales en el orden del template:
        #   template_params = [f"{client.first_name} {client.last_name}".strip(), str(client.debt_amount or "")]
        template_params = []

        # Estas sí son necesarias siempre: las usa el first_message/prompt
        # del agente (mismas variables que en create_batch() para llamadas).
        dynamic_variables = {
            "name":     f"{client.first_name} {client.last_name}".strip() or "Cliente",
            "amount":   str(client.debt_amount or ""),
            "currency": getattr(client, "currency", "ARS"),
            "client_phone": client.phone,
        }

        call.status = "in_progress"
        call.started_at = timezone.now()
        call.save(update_fields=["status", "started_at"])

        try:
            result = elevenlabs_service.send_whatsapp_message(
                phone_number=client.phone,
                template_name=batch.whatsapp_template_name,
                template_language=batch.whatsapp_template_language or "es",
                template_params=template_params,
                dynamic_variables=dynamic_variables,
            )
            call.whatsapp_message_id = result.get("message_id") or result.get("id")
            call.status = "completed"
            call.outcome = "sent"
            call.completed_at = timezone.now()
            call.save(update_fields=[
                "whatsapp_message_id", "status", "outcome", "completed_at"
            ])
            sent += 1
        except Exception as exc:
            logger.error(f"Error enviando WhatsApp a {client.phone}: {exc}")
            call.status = "failed"
            call.outcome = "send_error"
            call.error_message = str(exc)
            call.completed_at = timezone.now()
            call.save(update_fields=[
                "status", "outcome", "error_message", "completed_at"
            ])
            failed += 1

    batch.status = "completed"
    batch.processed_clients = sent + failed
    batch.completed_at = timezone.now()
    batch.save(update_fields=["status", "processed_clients", "completed_at"])

    logger.info(
        f"CallBatch {batch_id} (whatsapp) finalizado. Enviados: {sent}, fallidos: {failed}"
    )
    return {"sent": sent, "failed": failed}


# ─────────────────────────────────────────────────────────────────
# TAREA 6: Reintentar un mensaje de WhatsApp fallido
# ─────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def retry_failed_whatsapp(self, call_id: int):
    """
    Reintenta el envío de un mensaje de WhatsApp que falló.

    Llamar desde la view /api/calls/{id}/retry/ con:
        retry_failed_whatsapp.delay(call.id)
    """
    from apps.calls.models import Call
    from apps.calls.elevenlabs_service import elevenlabs_service

    try:
        call = Call.objects.select_related("client", "batch").get(id=call_id)
    except Call.DoesNotExist:
        logger.error(f"Call {call_id} no encontrada para retry de WhatsApp")
        return

    client = call.client
    batch = call.batch

    if not client.phone:
        logger.error(f"Cliente {client.id} no tiene teléfono, no se puede reintentar")
        return

    if not batch.whatsapp_template_name:
        logger.error(f"CallBatch {batch.id} no tiene whatsapp_template_name configurado")
        return

    # NOTA: plantilla01 y plantilla03 no tienen variables. Ver comentario
    # equivalente en process_whatsapp_batch si agregan un template con {{1}}, {{2}}...
    template_params = []

    dynamic_variables = {
        "name":     f"{client.first_name} {client.last_name}".strip() or "Cliente",
        "amount":   str(client.debt_amount or ""),
        "currency": getattr(client, "currency", "ARS"),
        "client_phone": client.phone,
    }

    try:
        result = elevenlabs_service.send_whatsapp_message(
            phone_number=client.phone,
            template_name=batch.whatsapp_template_name,
            template_language=batch.whatsapp_template_language or "es",
            template_params=template_params,
            dynamic_variables=dynamic_variables,
        )
        call.whatsapp_message_id = result.get("message_id") or result.get("id")
        call.status = "completed"
        call.outcome = "sent"
        call.retry_count = (call.retry_count or 0) + 1
        call.completed_at = timezone.now()
        call.save(update_fields=[
            "whatsapp_message_id", "status", "outcome", "retry_count", "completed_at"
        ])
        logger.info(f"Reintento de WhatsApp Call {call_id} exitoso")
    except Exception as exc:
        logger.error(f"Error en reintento de WhatsApp Call {call_id}: {exc}")
        call.retry_count = (call.retry_count or 0) + 1
        call.error_message = str(exc)
        call.save(update_fields=["retry_count", "error_message"])
        raise self.retry(exc=exc)


@shared_task
def retry_failed_calls_auto():
    """
    Tarea diaria (9:00 AM) que reintenta llamadas fallidas o voicemail
    que aún no fueron reintentadas y tienen más de 24hs.
    Máximo 1 reintento por llamada.
    """
    from apps.calls.models import Call, CallBatch
    from apps.calls.elevenlabs_service import elevenlabs_service
    import datetime
    from django.utils import timezone

    hace_24hs = timezone.now() - datetime.timedelta(hours=24)

    calls_a_reintentar = Call.objects.filter(
        status="failed",
        retry_count=0,
        created_at__lte=hace_24hs,
    ).select_related("client", "batch")

    total = calls_a_reintentar.count()
    logger.info(f"retry_failed_calls_auto: {total} llamadas a reintentar")

    for call in calls_a_reintentar:
        if not call.client.phone:
            continue
        try:
            if call.channel == "whatsapp":
                retry_failed_whatsapp.delay(call.id)
            else:
                retry_failed_call.delay(call.id)
            logger.info(f"Reintento programado para Call {call.id} ({call.channel}) - {call.client.phone}")
        except Exception as e:
            logger.error(f"Error programando reintento para Call {call.id}: {e}")

    return f"Reintentos programados: {total}"
