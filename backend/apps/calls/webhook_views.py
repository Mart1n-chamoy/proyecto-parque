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
    def get(self, request):
        """ElevenLabs verifica el endpoint con GET antes de enviar eventos."""
        return JsonResponse({"status": "ok"})

    def post(self, request):
        # 1. Verificar firma del webhook (seguridad)
#        if ELEVENLABS_WEBHOOK_SECRET:
 #           if not self._verify_signature(request):
  #              logger.warning("Webhook ElevenLabs: firma inválida")
   #             return JsonResponse({"error": "Unauthorized"}, status=401)

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


ELEVENLABS_TOOL_SECRET = os.getenv("ELEVENLABS_TOOL_SECRET", "")

# Template de WhatsApp para el enlace de pago. Es el mismo link para todos
# los clientes (se identifican con su DNI en el portal), así que el
# template no necesita variables.
PAYMENT_LINK_TEMPLATE_NAME = os.getenv("WHATSAPP_PAYMENT_LINK_TEMPLATE", "enlace_pago_cobranzas")
PAYMENT_LINK_TEMPLATE_LANGUAGE = os.getenv("WHATSAPP_PAYMENT_LINK_TEMPLATE_LANGUAGE", "es_AR")
# Header de imagen del template enlace_pago_cobranzas (logo de Parque de
# Descanso). Se manda en CADA envío, no alcanza con haberla subido una
# sola vez al crear el template en Meta.
PAYMENT_LINK_HEADER_IMAGE_URL = os.getenv(
    "WHATSAPP_PAYMENT_LINK_HEADER_IMAGE_URL",
    "https://comercialsl.com/static/dashboard/img/parque-descanso-header.png",
)


@method_decorator(csrf_exempt, name="dispatch")
class SendPaymentLinkToolView(View):
    """
    POST /webhooks/send-payment-link/

    Tool (server tool / webhook) que el agente de ElevenLabs llama cuando
    el cliente pide que le manden el enlace de pago por WhatsApp — ya sea
    que estén hablando por WhatsApp o por una llamada de voz.

    Body esperado (JSON):
        {"conversation_id": "conv_xxxxx"}

    OJO: usamos conversation_id (no el número de teléfono directo) a
    propósito. Probamos pedirle a la IA que escriba el número tomándolo
    de system__caller_id / client_phone / etc., y en la práctica el
    modelo terminaba mandando el texto literal "{{system__caller_id}}"
    en vez del valor real — la sintaxis {{...}} solo se resuelve
    automáticamente en otros campos (como el primer mensaje), no cuando
    el LLM arma los argumentos de un tool call.

    La forma confiable: el parámetro conversation_id se configura en
    ElevenLabs con "Tipo de valor" = Dynamic Variable (no "LLM Prompt"),
    apuntando a system__conversation_id. Así lo resuelve la propia
    plataforma, sin pasar por el razonamiento del modelo. Nosotros
    después buscamos el teléfono real consultando la conversación.

    Configurar en ElevenLabs → Agente → Tools → enviar_enlace_pago:
        URL:     https://tu-dominio.com/webhooks/send-payment-link/
        Método:  POST
        Headers: X-Tool-Secret: <mismo valor que ELEVENLABS_TOOL_SECRET>
        Body → parámetro "conversation_id":
            Tipo de dato: String
            Tipo de valor: Dynamic Variable → system__conversation_id
    """

    @staticmethod
    def _extract_phone_number(conversation: dict) -> str | None:
        """
        Busca el número de teléfono/WhatsApp del cliente en la respuesta
        de GET /v1/convai/conversations/{id}. Prueba varios campos porque
        la forma exacta cambia según el canal (WhatsApp vs llamada).
        """
        metadata = conversation.get("metadata") or {}

        whatsapp_meta = metadata.get("whatsapp") or {}
        if whatsapp_meta.get("whatsapp_user_id"):
            return whatsapp_meta["whatsapp_user_id"]

        phone_call_meta = metadata.get("phone_call") or {}
        for key in ("external_number", "caller_number", "from_number", "phone_number"):
            if phone_call_meta.get(key):
                return phone_call_meta[key]

        # Fallback universal: en los casos que probamos, coincide con el
        # número real tanto para WhatsApp como (previsiblemente) llamadas.
        if conversation.get("user_id"):
            return conversation["user_id"]

        return None

    def post(self, request):
        # Verificación del secreto compartido — sin esto, cualquiera que
        # encuentre la URL podría hacer que mandemos WhatsApps gratis.
        if ELEVENLABS_TOOL_SECRET:
            provided = request.headers.get("X-Tool-Secret", "")
            if not hmac.compare_digest(provided, ELEVENLABS_TOOL_SECRET):
                logger.warning("SendPaymentLinkTool: secreto inválido o ausente")
                return JsonResponse(
                    {"success": False, "error": "unauthorized"}, status=401
                )
        else:
            logger.warning(
                "ELEVENLABS_TOOL_SECRET no configurado — el endpoint de "
                "enlace de pago está sin protección. Configuralo en el .env."
            )

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalid_json"}, status=400)

        conversation_id = (payload.get("conversation_id") or "").strip()
        if not conversation_id:
            return JsonResponse(
                {"success": False, "error": "falta conversation_id"}, status=400
            )

        from apps.calls.elevenlabs_service import elevenlabs_service

        try:
            conversation = elevenlabs_service.get_conversation(conversation_id)
        except Exception as exc:
            logger.error(f"Error consultando conversación {conversation_id}: {exc}")
            return JsonResponse({
                "success": False,
                "error": "No pude consultar los datos de la conversación.",
            }, status=502)

        phone_number = self._extract_phone_number(conversation)
        if not phone_number:
            logger.error(
                f"No se encontró número de teléfono en la conversación {conversation_id}"
            )
            return JsonResponse({
                "success": False,
                "error": "No encontré el número de teléfono del cliente en esta conversación.",
            }, status=422)

        try:
            elevenlabs_service.send_whatsapp_message(
                phone_number=phone_number,
                template_name=PAYMENT_LINK_TEMPLATE_NAME,
                template_language=PAYMENT_LINK_TEMPLATE_LANGUAGE,
                template_params=[],
                header_image_url=PAYMENT_LINK_HEADER_IMAGE_URL,
            )
            logger.info(f"Enlace de pago enviado por WhatsApp a {phone_number}")
            return JsonResponse({
                "success": True,
                "message": "El enlace de pago se envió correctamente por WhatsApp.",
            })
        except Exception as exc:
            logger.error(f"Error enviando enlace de pago a {phone_number}: {exc}")
            return JsonResponse({
                "success": False,
                "error": "No se pudo enviar el enlace por WhatsApp en este momento.",
            }, status=502)


@method_decorator(csrf_exempt, name="dispatch")
class CustomerLookupToolView(View):
    """
    POST /webhooks/customer-lookup/

    Tool (server tool / webhook) para el agente de ElevenLabs: devuelve
    nombre, monto y moneda del cliente que está hablando en la conversación.

    Se usa cuando el CLIENTE inicia el contacto (WhatsApp entrante o llamada
    entrante). En las campañas que iniciamos nosotros ya mandamos esos datos
    como variables dinámicas, pero en un contacto entrante nadie se las pasa
    al agente y el prompt terminaba mostrando las llaves sin reemplazar.

    Body esperado (JSON):
        {"conversation_id": "conv_xxxxx"}

    Igual que el tool del enlace de pago, se identifica por conversation_id
    (resuelto por la plataforma como system__conversation_id) y no por un
    teléfono que tenga que escribir el modelo. Después buscamos el teléfono
    real consultando la conversación y lo comparamos con nuestros clientes.

    Respuesta:
        {"found": true,  "name": "...", "amount": "131.134", "currency": "ARS", "note": "..."}
        {"found": false, "message": "..."}

    Detalles de la búsqueda:
      * Los teléfonos se guardan tal cual vienen en el CSV (con o sin "+", con
        o sin el 9 de celulares argentinos, con espacios). Por eso se comparan
        solo los dígitos y solo los últimos 10 (código de área + número).
      * Solo se consideran clientes activos.
      * Si el número coincide con más de un cliente, NO se devuelve ninguno:
        preferimos no revelar la deuda de la persona equivocada.
    """

    MIN_DIGITS = 10

    @staticmethod
    def _digits(value) -> str:
        return "".join(ch for ch in str(value or "") if ch.isdigit())

    def _find_clients(self, phone_number: str) -> list:
        from django.db.models import CharField, F, Func, Value
        from apps.clients.models import Client

        digits = self._digits(phone_number)
        if len(digits) < self.MIN_DIGITS:
            return []

        # regexp_replace(phone, '[^0-9]', '', 'g') -> solo dígitos, en la base
        only_digits = Func(
            F("phone"), Value("[^0-9]"), Value(""), Value("g"),
            function="regexp_replace", output_field=CharField(),
        )
        return list(
            Client.objects
            .filter(is_active=True)
            .annotate(phone_digits=only_digits)
            .filter(phone_digits__endswith=digits[-10:])[:2]
        )

    def post(self, request):
        if ELEVENLABS_TOOL_SECRET:
            provided = request.headers.get("X-Tool-Secret", "")
            if not hmac.compare_digest(provided, ELEVENLABS_TOOL_SECRET):
                logger.warning("CustomerLookupTool: secreto inválido o ausente")
                return JsonResponse(
                    {"found": False, "error": "unauthorized"}, status=401
                )
        else:
            logger.warning(
                "ELEVENLABS_TOOL_SECRET no configurado — el endpoint de "
                "consulta de cliente está sin protección. Configuralo en el .env."
            )

        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"found": False, "error": "invalid_json"}, status=400)

        conversation_id = (payload.get("conversation_id") or "").strip()
        if not conversation_id:
            return JsonResponse(
                {"found": False, "error": "falta conversation_id"}, status=400
            )

        from apps.calls.elevenlabs_service import elevenlabs_service

        try:
            conversation = elevenlabs_service.get_conversation(conversation_id)
        except Exception as exc:
            logger.error(f"CustomerLookupTool: error consultando conversación {conversation_id}: {exc}")
            return JsonResponse({
                "found": False,
                "error": "No pude consultar los datos de la conversación.",
            }, status=502)

        phone_number = SendPaymentLinkToolView._extract_phone_number(conversation)
        if not phone_number:
            logger.error(f"CustomerLookupTool: sin teléfono en la conversación {conversation_id}")
            return JsonResponse({
                "found": False,
                "message": "No pude identificar el número de teléfono de esta conversación.",
            })

        clients = self._find_clients(phone_number)

        if len(clients) > 1:
            logger.warning(
                f"CustomerLookupTool: el número de la conversación {conversation_id} "
                f"coincide con más de un cliente; no se devuelve ninguno"
            )
            clients = []

        if not clients:
            logger.info(f"CustomerLookupTool: conversación {conversation_id} -> sin coincidencia")
            return JsonResponse({
                "found": False,
                "message": "No encontré una cuenta asociada a este número.",
            })

        client = clients[0]

        def _fecha(d):
            return d.strftime("%d/%m/%Y") if d else None

        # Ojo: no se loguea el monto ni el resto de los datos de la cuenta,
        # solo el resultado de la búsqueda (a qué cliente correspondió).
        logger.info(f"CustomerLookupTool: conversación {conversation_id} -> cliente {client.id}")
        return JsonResponse({
            "found": True,
            "name": f"{client.first_name} {client.last_name}".strip(),
            "amount": elevenlabs_service.format_amount(client.debt_amount),
            "currency": getattr(client, "currency", "ARS"),
            # Datos ampliados de la cuenta (pueden venir vacíos si el
            # archivo que se cargó no tenía esas columnas).
            "numero_registro": client.registro,
            "documento": client.documento,
            "parcela": client.parcela,
            "descripcion_deuda": client.description,
            "periodo": (
                f"{client.semestre} {client.anio}".strip()
                if (client.semestre or client.anio) else None
            ),
            "fecha_vencimiento": _fecha(client.due_date),
            "fecha_ultimo_pago": _fecha(client.last_payment_date),
            "note": (
                "Todavía no sabés si quien escribe es el titular: confirmá que "
                "hablás con esa persona antes de mencionar el monto o cualquier "
                "dato de la cuenta. Cualquier campo de datos ampliados que venga "
                "en null significa que no está cargado — nunca lo inventes, decí "
                "que no tenés ese dato a mano y que un asesor lo puede confirmar."
            ),
        })
