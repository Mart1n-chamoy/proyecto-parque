"""
apps/calls/views_batch.py

Views para los endpoints de lotes de llamadas.
Este archivo extiende/reemplaza la lógica de batches en views.py existente.

Endpoints que maneja:
  POST /api/calls/batches/             → crear lote desde lista de clients
  POST /api/calls/batches/{id}/start/  → lanzar lote a ElevenLabs (async)
  GET  /api/calls/batches/{id}/status/ → consultar estado en ElevenLabs
  GET  /api/calls/batches/{id}/results/→ ver resultados de todas las llamadas
"""

import logging
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404

from apps.calls.tasks import process_call_batch, fetch_call_results
from apps.calls.elevenlabs_service import elevenlabs_service

logger = logging.getLogger(__name__)


class BatchStartView(APIView):
    """
    POST /api/calls/batches/{id}/start/

    Lanza el procesamiento asincrónico del lote.
    Devuelve inmediatamente — Celery hace el trabajo en background.
    """

    def post(self, request, pk):
        from apps.calls.models import BatchCall

        batch = get_object_or_404(BatchCall, pk=pk)

        if batch.status not in ("pending", "failed"):
            return Response(
                {
                    "error": f"El lote está en estado '{batch.status}'. "
                             "Solo se pueden iniciar lotes en estado 'pending' o 'failed'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not elevenlabs_service.is_configured():
            return Response(
                {
                    "error": "ElevenLabs no configurado. "
                             "Verificar ELEVENLABS_API_KEY y ELEVENLABS_AGENT_ID en .env"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Lanzar la tarea Celery (no bloquea)
        task = process_call_batch.delay(batch.id)

        # Marcar como "queued" para que el frontend sepa que está en cola
        batch.status = "pending"
        batch.celery_task_id = task.id
        batch.save(update_fields=["status", "celery_task_id"])

        return Response(
            {
                "id":      batch.id,
                "status":  "processing",
                "task_id": task.id,
                "message": f"Lote iniciado. Se procesarán las llamadas en background. "
                           f"Consultá el estado en /api/calls/batches/{batch.id}/status/",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class BatchStatusView(APIView):
    """
    GET /api/calls/batches/{id}/status/

    Consulta el estado actual del lote: tanto en DB como en ElevenLabs.
    Úsalo para polling desde el frontend.
    """

    def get(self, request, pk):
        from apps.calls.models import BatchCall, Call

        batch = get_object_or_404(BatchCall, pk=pk)

        # Datos locales de la DB
        total     = Call.objects.filter(batch=batch).count()
        completed = Call.objects.filter(batch=batch, status="completed").count()
        failed    = Call.objects.filter(batch=batch, status="failed").count()
        pending   = total - completed - failed

        response_data = {
            "id":                   batch.id,
            "status":               batch.status,
            "elevenlabs_batch_id":  batch.elevenlabs_batch_id,
            "total_calls":          total,
            "completed_calls":      completed,
            "failed_calls":         failed,
            "pending_calls":        pending,
            "started_at":           batch.started_at,
            "completed_at":         batch.completed_at,
        }

        # Si el lote tiene ID de ElevenLabs, consultar estado en tiempo real
        if batch.elevenlabs_batch_id and batch.status == "processing":
            try:
                el_data = elevenlabs_service.get_batch(batch.elevenlabs_batch_id)
                response_data["elevenlabs_status"] = el_data.get("status")
            except Exception as exc:
                logger.warning(f"No se pudo consultar ElevenLabs para batch {pk}: {exc}")
                response_data["elevenlabs_status"] = "unavailable"

        return Response(response_data)


class BatchResultsView(APIView):
    """
    GET /api/calls/batches/{id}/results/

    Devuelve los resultados de todas las llamadas del lote:
    estado, transcripción y URL del audio.
    """

    def get(self, request, pk):
        from apps.calls.models import BatchCall, Call

        batch = get_object_or_404(BatchCall, pk=pk)
        calls = (
            Call.objects
            .filter(batch=batch)
            .select_related("client")
            .order_by("id")
        )

        results = []
        for call in calls:
            audio_url = None
            if call.audio_file:
                audio_url = request.build_absolute_uri(f"/media/{call.audio_file}")

            results.append({
                "call_id":              call.id,
                "client_name":          call.client.name,
                "client_phone":         call.client.phone,
                "status":               call.status,
                "outcome":              call.outcome,
                "duration_seconds":     call.duration_seconds,
                "transcript":           call.transcript_text,
                "audio_url":            audio_url,
                "elevenlabs_conv_id":   call.elevenlabs_conversation_id,
                "completed_at":         call.completed_at,
            })

        return Response({
            "batch_id": batch.id,
            "status":   batch.status,
            "results":  results,
        })


class ManualFetchResultView(APIView):
    """
    POST /api/calls/{id}/fetch-results/

    Dispara manualmente la descarga de audio + transcript para una
    llamada específica. Útil para debugging o si el webhook no llegó.
    """

    def post(self, request, pk):
        from apps.calls.models import Call

        call = get_object_or_404(Call, pk=pk)

        el_conv_id = request.data.get("elevenlabs_conversation_id") or \
                     call.elevenlabs_conversation_id

        if not el_conv_id:
            return Response(
                {"error": "Falta elevenlabs_conversation_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = fetch_call_results.delay(
            el_conversation_id=el_conv_id,
            phone_number=call.client.phone,
            batch_id=call.batch_id,
        )

        return Response({
            "message": "Descarga de resultados iniciada en background",
            "task_id": task.id,
        }, status=status.HTTP_202_ACCEPTED)
