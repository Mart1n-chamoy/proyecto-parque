from django.db import models
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """Modelo para cliente con deuda"""
    first_name = models.CharField(_('Nombre'), max_length=100)
    last_name = models.CharField(_('Apellido'), max_length=100)
    phone = models.CharField(_('Teléfono'), max_length=20, unique=True)
    email = models.EmailField(_('Email'), blank=True, null=True)
    debt_amount = models.DecimalField(_('Monto de Deuda'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_('Creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Actualizado'), auto_now=True)
    is_active = models.BooleanField(_('Activo'), default=True)

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"
