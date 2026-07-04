"""
apps/calls/webhook_views.py

Webhook para recibir notificaciones de ElevenLabs cuando una llamada termina.

ElevenLabs hace un POST a esta URL con los datos de la conversación.
Configurar la URL del webhook en el panel de ElevenLabs:
  https://elevenlabs.io/app/conversational-ai → tu agente → Webhooks
  → agregar: https://tu-dominio.com/webhooks/elevenlabs/

Agregar en urls.py principal:
  path("webhooks/", include("apps.calls.webhook_urls")),
"""

import logging
import hashlib
import hmac
import os
import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.calls.tasks import fetch_call_results

logger = logging.getLogger(__name__)

ELEVENLABS_WEBHOOK_SECRET = os.getenv("ELEVENLABS_WEBHOOK_SECRET", "")


@method_decorator(csrf_exempt, name="dispatch")
class ElevenLabsWebhookView(View):
    """
    POST /webhooks/elevenlabs/

    ElevenLabs notifica cuando una conversación termina.
    Payload de ejemplo:
    {
      "type": "conversation.ended",
      "conversation_id": "conv_abc123",
      "agent_id": "agent_xyz",
      "status": "done",
      "metadata": {
        "phone_number": "+541155667788",
        "call_duration_secs": 45
      },
      "analysis": {
        "call_successful": true,
        "outcome": "payment_arranged"
      }
    }
    """

    def post(self, request):
        # 1. Verificar firma del webhook (seguridad)
        if ELEVENLABS_WEBHOOK_SECRET:
            if not self._verify_signature(request):
                logger.warning("Webhook ElevenLabs: firma inválida")
                return JsonResponse({"error": "Unauthorized"}, status=401)

        # 2. Parsear payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        event_type = payload.get("type", "")
        logger.info(f"Webhook ElevenLabs recibido: {event_type}")

        # 3. Manejar evento de conversación finalizada
        if event_type == "conversation.ended":
            conv_id      = payload.get("conversation_id")
            phone_number = payload.get("metadata", {}).get("phone_number")

            if conv_id and phone_number:
                # Buscar el batch al que pertenece esta llamada
                batch_id = self._find_batch_id(phone_number, conv_id)

                if batch_id:
                    # Lanzar tarea para bajar audio + transcript
                    fetch_call_results.delay(
                        el_conversation_id=conv_id,
                        phone_number=phone_number,
                        batch_id=batch_id,
                    )
                    logger.info(
                        f"Tarea fetch_call_results lanzada: "
                        f"conv={conv_id} phone={phone_number} batch={batch_id}"
                    )
                else:
                    logger.warning(
                        f"No se encontró batch para conv={conv_id} phone={phone_number}"
                    )
            else:
                logger.warning(f"Webhook sin conversation_id o phone_number: {payload}")

        return JsonResponse({"received": True})

    def _verify_signature(self, request) -> bool:
        """
        Verifica la firma HMAC-SHA256 del webhook de ElevenLabs.
        ElevenLabs envía la firma en el header: ElevenLabs-Signature
        """
        signature_header = request.headers.get("ElevenLabs-Signature", "")
        if not signature_header:
            return False

        expected = hmac.new(
            ELEVENLABS_WEBHOOK_SECRET.encode(),
            request.body,
            hashlib.sha256,
        ).hexdigest()

        # El header viene como "sha256=<hash>"
        received = signature_header.replace("sha256=", "")
        return hmac.compare_digest(expected, received)

    def _find_batch_id(self, phone_number: str, conv_id: str) -> int | None:
        """
        Busca el batch_id de la llamada con ese número de teléfono
        que esté en estado "in_progress".
        """
        try:
            from apps.calls.models import Call
            call = (
                Call.objects
                .filter(client__phone=phone_number, status="in_progress")
                .select_related("batch")
                .latest("id")
            )
            return call.batch_id
        except Exception:
            return None
