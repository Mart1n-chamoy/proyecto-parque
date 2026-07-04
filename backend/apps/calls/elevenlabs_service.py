"""
apps/calls/elevenlabs_service.py

Servicio de integración con ElevenLabs Conversational AI.
Maneja los 4 flujos principales:
  1. Configuración del agente
  2. CRUD de lotes de llamadas
  3. Ejecución del proceso de llamadas por lote
  4. Obtención de resultados (audio + transcripción)
"""

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsService:
    """
    Cliente para ElevenLabs Conversational AI API.
    Usa httpx directamente para tener control total sobre los requests.
    """

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.agent_id = os.getenv("ELEVENLABS_AGENT_ID", "")
        self.base_url = ELEVENLABS_BASE_URL

    def _headers(self) -> dict:
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.api_key and self.agent_id)

    # ─────────────────────────────────────────────
    # FLUJO 1 - Configuración: obtener info del agente
    # ─────────────────────────────────────────────

    def get_agent(self) -> dict:
        """
        Retorna la configuración actual del agente de ElevenLabs.
        Útil para verificar que el agente esté bien configurado antes
        de lanzar un lote.

        GET /v1/convai/agents/{agent_id}
        """
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def update_agent_prompt(self, system_prompt: str, first_message: str) -> dict:
        """
        Actualiza el prompt del sistema y el primer mensaje del agente.
        Útil si querés cambiar el texto de cobranza sin tocar el panel de EL.

        PATCH /v1/convai/agents/{agent_id}
        """
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        payload = {
            "conversation_config": {
                "agent": {
                    "prompt": {"prompt": system_prompt},
                    "first_message": first_message,
                }
            }
        }
        with httpx.Client(timeout=30) as client:
            resp = client.patch(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

    # ─────────────────────────────────────────────
    # FLUJO 2 - CRUD: listar y consultar lotes
    # ─────────────────────────────────────────────

    def list_batches(self) -> list[dict]:
        """
        Lista todos los lotes de llamadas en ElevenLabs.

        GET /v1/convai/batches
        """
        url = f"{self.base_url}/convai/batches"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json().get("batches", [])

    def get_batch(self, el_batch_id: str) -> dict:
        """
        Obtiene el estado y detalle de un lote específico.
        Incluye el estado individual de cada llamada dentro del lote.

        GET /v1/convai/batches/{batch_id}
        """
        url = f"{self.base_url}/convai/batches/{el_batch_id}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    # ─────────────────────────────────────────────
    # FLUJO 3 - Ejecución: crear y lanzar un lote
    # ─────────────────────────────────────────────

    def create_batch(
        self,
        recipients: list[dict],
        scheduled_time: Optional[str] = None,
    ) -> str:
        """
        Crea y lanza un lote de llamadas en ElevenLabs.

        Cada recipient DEBE tener:
          - phone_number (str): número en formato E.164, ej: "+541155667788"

        Columnas extra del CSV se pasan como variables dinámicas al agente:
          - name       → {{name}} en el prompt
          - amount     → {{amount}} en el prompt
          - currency   → {{currency}} en el prompt

        Retorna el batch_id de ElevenLabs.

        POST /v1/convai/batches
        """
        if not self.is_configured():
            raise ValueError(
                "ELEVENLABS_API_KEY o ELEVENLABS_AGENT_ID no configurados. "
                "Verificar variables de entorno."
            )

        payload = {
            "agent_id": self.agent_id,
            "call_recipients": [
                {
                    "phone_number": r["phone_number"],
                    "agent_variable_values": {
                        "name":     r.get("name", "Cliente"),
                        "amount":   str(r.get("amount", "")),
                        "currency": r.get("currency", "ARS"),
                    },
                }
                for r in recipients
            ],
        }

        if scheduled_time:
            # ISO 8601: "2025-08-01T14:00:00Z"
            payload["scheduled_time"] = scheduled_time

        url = f"{self.base_url}/convai/batches"
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()

        el_batch_id = data.get("batch_id") or data.get("id")
        logger.info(f"Lote creado en ElevenLabs: {el_batch_id} ({len(recipients)} destinatarios)")
        return el_batch_id

    # ─────────────────────────────────────────────
    # FLUJO 4 - Resultados: obtener audio y transcripción
    # ─────────────────────────────────────────────

    def get_conversation(self, conversation_id: str) -> dict:
        """
        Obtiene el detalle completo de una conversación finalizada.
        Incluye: transcript, duración, outcome, metadata.

        GET /v1/convai/conversations/{conversation_id}
        """
        url = f"{self.base_url}/convai/conversations/{conversation_id}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def get_conversation_audio(self, conversation_id: str) -> bytes:
        """
        Descarga el audio de una conversación como bytes MP3.
        Guardar luego en media/calls/ o S3.

        GET /v1/convai/conversations/{conversation_id}/audio
        """
        url = f"{self.base_url}/convai/conversations/{conversation_id}/audio"
        with httpx.Client(timeout=60) as client:
            resp = client.get(url, headers={"xi-api-key": self.api_key})
            resp.raise_for_status()
            return resp.content

    def extract_transcript_text(self, conversation_data: dict) -> str:
        """
        Extrae el texto del transcript de la respuesta de la API.
        ElevenLabs devuelve el transcript como lista de turnos.

        Formato de retorno:
          "Agente: Hola, le llamo de...\nCliente: Sí, ¿quién habla?"
        """
        transcript_lines = []
        turns = conversation_data.get("transcript", [])
        for turn in turns:
            role = "Agente" if turn.get("role") == "agent" else "Cliente"
            text = turn.get("message", "")
            if text:
                transcript_lines.append(f"{role}: {text}")
        return "\n".join(transcript_lines)


# Singleton — importar desde cualquier lado con:
# from apps.calls.elevenlabs_service import elevenlabs_service
elevenlabs_service = ElevenLabsService()
