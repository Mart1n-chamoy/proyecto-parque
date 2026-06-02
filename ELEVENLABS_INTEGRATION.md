# 🎙️ Integración ElevenLabs API

Este documento describe la integración de ElevenLabs API con el proyecto para síntesis de voz en las llamadas automatizadas.

## 📋 Descripción

ElevenLabs proporciona una API de síntesis de voz (Text-to-Speech) que convierte texto en audio natural. Se ha integrado para:

- Generar audio de llamadas desde texto
- Procesar lotes de llamadas de forma asincrónica
- Reintentar llamadas fallidas
- Soportar múltiples idiomas y voces

## 🔧 Componentes Implementados

### 1. **ElevenLabsService** (`apps/calls/elevenlabs_service.py`)

Servicio encargado de:
- Inicializar cliente de ElevenLabs
- Convertir texto a audio
- Gestionar voces disponibles
- Guardar archivos de audio

```python
from apps.calls.elevenlabs_service import elevenlabs_service

# Generar audio
audio_bytes = elevenlabs_service.text_to_speech(
    text="Hola, esto es una prueba",
    voice_key='spanish_male'
)
```

### 2. **Celery Tasks** (`apps/calls/tasks.py`)

Tareas asincrónicas para:
- `generate_call_audio()` - Generar audio de una llamada
- `process_call_batch()` - Procesar un lote completo
- `check_batch_completion()` - Verificar lotes completados
- `retry_failed_call()` - Reintentar llamadas fallidas

## 🎤 Voces Disponibles

```python
'spanish_male'      # Diego (Español masculino)
'spanish_female'    # Bella (Español femenino)
'english_male'      # Adam (Inglés masculino)
'english_female'    # Bella (Inglés femenino)
```

## 🔌 Configuración

### Variables de Entorno

```env
# .env
ELEVENLABS_API_KEY=tu_api_key_aqui
```

### Instalación de Dependencias

El paquete `elevenlabs` ya está en `requirements.txt`:

```bash
pip install elevenlabs==0.2.13
```

## 📊 Flujo de Procesamiento

```
Usuario crea lote
    ↓
POST /api/calls/batches/{id}/start/
    ↓
Celery: process_call_batch()
    ↓
Por cada llamada:
  Celery: generate_call_audio()
    ↓
    ElevenLabs API: text_to_speech()
    ↓
    Guardar audio en BD
    ↓
    Actualizar estado de llamada
```

## 🚀 Uso en Endpoints

### Iniciar un Lote (Asincrónico)

```bash
POST /api/calls/batches/1/start/

Respuesta:
{
  "id": 1,
  "status": "processing",
  "message": "Lote iniciado. El procesamiento ocurre en segundo plano."
}
```

El procesamiento ocurre en background, sin bloquear el servidor.

### Reintentar Llamada Fallida

```bash
POST /api/calls/123/retry/

Respuesta:
{
  "id": 123,
  "status": "pending",
  "message": "Llamada en cola para reintentar"
}
```

## 📁 Almacenamiento de Audio

Los archivos de audio se guardan en:

```
media/
└── calls/
    └── {client_id}/
        └── call_{call_id}_{timestamp}.mp3
```

## 🔍 Monitoreo de Tareas

### Ver tareas en cola

```bash
# Conectar a Redis
redis-cli

# Ver tareas pendientes
KEYS celery*
```

### Ver logs de Celery

```bash
docker logs proyecto-parque-celery-1 -f
```

## ⚙️ Configuración de Celery

En `proyecto_cobranza/celery.py` (ya configurado):

```python
app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND'),
    timezone='America/Argentina/Buenos_Aires',
)
```

Tareas periódicas:

```python
app.conf.beat_schedule = {
    'check-batch-completion': {
        'task': 'apps.calls.tasks.check_batch_completion',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}
```

## 🛠️ Desarrollo y Pruebas

### Prueba Local (sin Celery)

Si quieres probar sin usar Celery, puedes ejecutar tareas sincronamente:

```python
from apps.calls.tasks import generate_call_audio

# Ejecutar sincronamente (no recomendado en prod)
generate_call_audio(call_id=1, text="Hola", voice_key='spanish_male')
```

### Prueba del Servicio

```bash
cd backend

python manage.py shell

from apps.calls.elevenlabs_service import elevenlabs_service

# Verificar configuración
print(elevenlabs_service.is_configured())

# Generar audio de prueba
audio = elevenlabs_service.text_to_speech("Hola mundo", "spanish_male")
```

## 📝 Manejo de Errores

El servicio maneja automáticamente:
- API key no configurada
- Errores de conexión
- Reintentos automáticos (max 3 intentos)
- Logging detallado de errores

## 🔐 Seguridad

- API key almacenada en variables de entorno
- No se guarda en el código fuente
- Validación de entrada antes de enviar a API
- Rate limiting por parte de ElevenLabs

## 📚 Recursos

- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Celery Documentation](https://docs.celeryproject.io/)

## 🚨 Limitaciones Actuales

- ElevenLabs es un servicio de pago
- Hay límites de caracteres según plan
- Las tareas se pierden si Redis se reinicia (sin persistencia)
- No hay almacenamiento de transcripciones de llamadas reales aún

## 🔮 Próximas Mejoras

- [ ] Reconocimiento de voz (Speech-to-Text)
- [ ] Grabación de llamadas reales
- [ ] Análisis de sentimiento
- [ ] Persistencia de Redis
- [ ] Webhooks para actualizaciones en tiempo real
- [ ] Dashboard de monitoreo
