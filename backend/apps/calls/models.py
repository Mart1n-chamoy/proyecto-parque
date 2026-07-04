from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.clients.models import Client


class CallBatch(models.Model):
    """Modelo para lotes de llamadas"""
    STATUS_CHOICES = [
        ('pending', _('Pendiente')),
        ('processing', _('Procesando')),
        ('completed', _('Completado')),
        ('failed', _('Fallido')),
    ]

    name = models.CharField(_('Nombre del Lote'), max_length=255)
    description = models.TextField(_('Descripción'), blank=True)
    status = models.CharField(_('Estado'), max_length=20, choices=STATUS_CHOICES, default='pending')
    total_clients = models.IntegerField(_('Total de Clientes'), default=0)
    processed_clients = models.IntegerField(_('Clientes Procesados'), default=0)
    created_at = models.DateTimeField(_('Creado'), auto_now_add=True)
    started_at = models.DateTimeField(_('Iniciado'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completado'), null=True, blank=True)

    # Integración ElevenLabs
    elevenlabs_batch_id = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="ID del lote en ElevenLabs"
    )
    celery_task_id = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="ID de la tarea Celery que procesó este lote"
    )
    started_at = models.DateTimeField(
        blank=True, null=True
    )
    completed_at = models.DateTimeField(
        blank=True, null=True
    )

    class Meta:
        verbose_name = _('Lote de Llamadas')
        verbose_name_plural = _('Lotes de Llamadas')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"


class Call(models.Model):
    """Modelo para llamadas individuales"""
    STATUS_CHOICES = [
        ('pending', _('Pendiente')),
        ('in_progress', _('En Progreso')),
        ('completed', _('Completada')),
        ('failed', _('Fallida')),
    ]

    batch = models.ForeignKey(CallBatch, on_delete=models.CASCADE, related_name='calls')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='calls')
    status = models.CharField(_('Estado'), max_length=20, choices=STATUS_CHOICES, default='pending')
    duration = models.IntegerField(_('Duración (segundos)'), null=True, blank=True)
    transcript = models.TextField(_('Transcripción'), blank=True)
    audio_file = models.FileField(_('Archivo de Audio'), upload_to='calls/%Y/%m/%d/', null=True, blank=True)
    error_message = models.TextField(_('Mensaje de Error'), blank=True)
    created_at = models.DateTimeField(_('Creado'), auto_now_add=True)
    started_at = models.DateTimeField(_('Iniciado'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Completado'), null=True, blank=True)

    # Integración ElevenLabs
    elevenlabs_conversation_id = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="ID de conversación en ElevenLabs"
    )
    transcript_text = models.TextField(
        blank=True, null=True,
        help_text="Transcripción completa de la llamada"
    )
    audio_file = models.FileField(
        upload_to="calls/", blank=True, null=True,
        help_text="Archivo de audio MP3 de la llamada"
    )
    duration_seconds = models.IntegerField(
        blank=True, null=True,
        help_text="Duración de la llamada en segundos"
    )
    outcome = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Resultado según ElevenLabs (ej: payment_arranged, no_answer)"
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Cantidad de reintentos realizados"
    )
    completed_at = models.DateTimeField(
        blank=True, null=True
    )

    class Meta:
        verbose_name = _('Llamada')
        verbose_name_plural = _('Llamadas')
        ordering = ['-created_at']

    def __str__(self):
        return f"Llamada a {self.client.phone} ({self.status})"
