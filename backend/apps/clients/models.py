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

    # Datos ampliados de la cuenta (columnas opcionales del Excel/CSV:
    # REGISTRO, DOCUMENTO, AÑO, SEMESTRE, ULTFECHAPAGO, DESCRIPCION,
    # PARCELA, FECHAVTO). Todos opcionales: los archivos simples de
    # siempre (solo phone_number/name/amount) siguen funcionando igual.
    registro = models.CharField(_('N° de registro'), max_length=50, blank=True, null=True)
    documento = models.CharField(_('Documento'), max_length=50, blank=True, null=True)
    anio = models.IntegerField(_('Año'), blank=True, null=True)
    semestre = models.CharField(_('Semestre'), max_length=50, blank=True, null=True)
    last_payment_date = models.DateField(_('Fecha del último pago'), blank=True, null=True)
    description = models.CharField(_('Descripción'), max_length=255, blank=True, null=True)
    parcela = models.CharField(_('Parcela'), max_length=50, blank=True, null=True)
    due_date = models.DateField(_('Fecha de vencimiento'), blank=True, null=True)

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"
