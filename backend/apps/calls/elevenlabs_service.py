"""
Servicio de integración con ElevenLabs API
Maneja la síntesis de voz y generación de audio para las llamadas
"""

import os
import logging
from pathlib import Path
from typing import Optional

from elevenlabs.client import ElevenLabs

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """
    Servicio para interactuar con ElevenLabs API
    Responsable de:
    - Generar audio desde texto
    - Gestionar voces
    - Guardar archivos de audio
    """
    
    def __init__(self):
        self.api_key = os.environ.get('ELEVENLABS_API_KEY')
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY no configurada")
            self.client = None
        else:
            self.client = ElevenLabs(api_key=self.api_key)
        
        # Configuración de voces disponibles
        self.voices = {
            'spanish_male': '21m00Tcm4TlvDq8ikWAM',  # Diego (Spanish)
            'spanish_female': 'EXAVITQu4vr4xnSDxMaL',  # Bella (Spanish)
            'english_male': 'pNInz6obpgDQGcFmaJgB',  # Adam
            'english_female': 'EXAVITQu4vr4xnSDxMaL',  # Bella
        }
        
        self.default_voice = 'spanish_male'
    
    def is_configured(self) -> bool:
        """Verificar si ElevenLabs está configurado"""
        return self.client is not None
    
    def get_available_voices(self):
        """Obtener lista de voces disponibles"""
        if not self.is_configured():
            return None
        
        try:
            return self.client.voices.get_all()
        except Exception as e:
            logger.error(f"Error al obtener voces: {str(e)}")
            return None
    
    def text_to_speech(
        self,
        text: str,
        voice_key: str = None,
        output_path: Optional[Path] = None,
    ) -> Optional[bytes]:
        """
        Convertir texto a audio usando ElevenLabs
        
        Args:
            text: Texto a convertir en audio
            voice_key: Clave de la voz a usar (ej: 'spanish_male')
            output_path: Ruta donde guardar el archivo de audio
        
        Returns:
            Audio bytes si tiene éxito, None si hay error
        """
        if not self.is_configured():
            logger.error("ElevenLabs no está configurado")
            return None
        
        if not text or not text.strip():
            logger.error("Texto vacío")
            return None
        
        if voice_key is None:
            voice_key = self.default_voice
        
        voice_id = self.voices.get(voice_key)
        if not voice_id:
            logger.error(f"Voz desconocida: {voice_key}")
            voice_id = self.voices[self.default_voice]
        
        try:
            # Generar audio desde texto
            audio_data = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_monolingual_v1",
            )
            
            # Si se especifica ruta, guardar archivo
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    for chunk in audio_data:
                        f.write(chunk)
                
                logger.info(f"Audio guardado en: {output_path}")
                return audio_data
            
            return audio_data
        
        except Exception as e:
            logger.error(f"Error en text_to_speech: {str(e)}")
            return None
    
    def get_voice_preview(self, voice_key: str = None) -> Optional[bytes]:
        """
        Obtener una preview de una voz
        
        Args:
            voice_key: Clave de la voz
        
        Returns:
            Audio bytes del preview
        """
        if not self.is_configured():
            return None
        
        if voice_key is None:
            voice_key = self.default_voice
        
        voice_id = self.voices.get(voice_key, self.voices[self.default_voice])
        
        try:
            # Texto de ejemplo para preview
            preview_text = "Hola, soy una voz de prueba de ElevenLabs"
            
            return self.text_to_speech(preview_text, voice_key)
        
        except Exception as e:
            logger.error(f"Error en get_voice_preview: {str(e)}")
            return None


# Instancia global del servicio
elevenlabs_service = ElevenLabsService()
