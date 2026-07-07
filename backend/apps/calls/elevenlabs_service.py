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
    # FLUJO 1 - Configuración
    # ─────────────────────────────────────────────

    def get_agent(self) -> dict:
        """GET /v1/convai/agents/{agent_id}"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def update_agent_prompt(self, system_prompt: str, first_message: str) -> dict:
        """PATCH /v1/convai/agents/{agent_id}"""
        url = f"{self.base_url}/convai/agents/{self.agent_id}"
        payload = {
            "conversation_config": {
                "agent": {
                    "prompt": {"prompt": system_prompt},
                    "first_message": first_message,
                }
            }
        }
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.patch(url, headers=self._headers(), json=payload)
            resp.raise_for_status()
            return resp.json()

    # ─────────────────────────────────────────────
    # FLUJO 2 - CRUD lotes
    # ─────────────────────────────────────────────

    def list_batches(self) -> list[dict]:
        """GET /v1/convai/batch-calling/workspace"""
        url = f"{self.base_url}/convai/batch-calling/workspace"
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json().get("batches", [])

    def get_batch(self, el_batch_id: str) -> dict:
        """GET /v1/convai/batch-calling/{batch_id}"""
        url = f"{self.base_url}/convai/batch-calling/{el_batch_id}"
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    # ─────────────────────────────────────────────
    # FLUJO 3 - Ejecución
    # ─────────────────────────────────────────────

    def create_batch(
        self,
        recipients: list[dict],
        scheduled_time: Optional[str] = None,
    ) -> str:
        """
        POST /v1/convai/batch-calling/submit

        Cada recipient debe tener:
          - phone_number (str): formato E.164, ej: "+5492616XXXXXX"
          - name, amount, currency: variables dinámicas del agente
        """
        if not self.is_configured():
            raise ValueError(
                "ELEVENLABS_API_KEY o ELEVENLABS_AGENT_ID no configurados."
            )

        payload = {
            "call_name": f"Cobranza {len(recipients)} destinatarios",
            "agent_id": self.agent_id,
            "recipients": [
                {
                    "phone_number": r["phone_number"],
                    "dynamic_variables": {
                        "name":     r.get("name", "Cliente"),
                        "amount":   str(r.get("amount", "")),
                        "currency": r.get("currency", "ARS"),
                    },
                }
                for r in recipients
            ],
        }

        if scheduled_time:
            payload["scheduled_time"] = scheduled_time

        url = f"{self.base_url}/convai/batch-calling/submit"
        with httpx.Client(timeout=60, follow_redirects=True) as client:
            resp = client.post(url, headers=self._headers(), json=payload)
            # Mostrar detalle del error si falla
            if resp.is_error:
                logger.error(f"ElevenLabs error {resp.status_code}: {resp.text}")
            resp.raise_for_status()
            data = resp.json()

        el_batch_id = data.get("batch_id") or data.get("id")
        logger.info(f"Lote creado: {el_batch_id} ({len(recipients)} destinatarios)")
        return el_batch_id

    # ─────────────────────────────────────────────
    # FLUJO 4 - Resultados
    # ─────────────────────────────────────────────

    def get_conversation(self, conversation_id: str) -> dict:
        """GET /v1/convai/conversations/{conversation_id}"""
        url = f"{self.base_url}/convai/conversations/{conversation_id}"
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            resp = client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def get_conversation_audio(self, conversation_id: str) -> bytes:
        """GET /v1/convai/conversations/{conversation_id}/audio"""
        url = f"{self.base_url}/convai/conversations/{conversation_id}/audio"
        with httpx.Client(timeout=60, follow_redirects=True) as client:
            resp = client.get(url, headers={"xi-api-key": self.api_key})
            resp.raise_for_status()
            return resp.content

    def extract_transcript_text(self, conversation_data: dict) -> str:
        """Convierte el transcript de ElevenLabs a texto plano."""
        lines = []
        for turn in conversation_data.get("transcript", []):
            role = "Agente" if turn.get("role") == "agent" else "Cliente"
            text = turn.get("message", "")
            if text:
                lines.append(f"{role}: {text}")
        return "\n".join(lines)


# Singleton
elevenlabs_service = ElevenLabsService()
