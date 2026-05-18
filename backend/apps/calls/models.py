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

    class Meta:
        verbose_name = _('Llamada')
        verbose_name_plural = _('Llamadas')
        ordering = ['-created_at']

    def __str__(self):
        return f"Llamada a {self.client.phone} ({self.status})"
