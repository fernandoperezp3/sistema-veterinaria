from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Configuracion(models.Model):
    """Modelo singleton para la configuración global del sistema."""
    nombre_empresa = models.CharField(max_length=150, default='VetSystem')
    slogan = models.CharField(max_length=200, blank=True, null=True)
    logo = models.ImageField(upload_to='configuracion/', blank=True, null=True)
    
    # Moneda
    simbolo_moneda = models.CharField(max_length=10, default='Q', help_text='Ej: Q, $, €')
    nombre_moneda = models.CharField(max_length=50, default='Quetzales', blank=True)

    nombre_impuesto = models.CharField(max_length=20, default='IGV', help_text='Ej: IGV, IVA')
    porcentaje_impuesto = models.DecimalField(
        max_digits=5, decimal_places=2, default=18,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Porcentaje aplicado a las facturas. Ej: 18 (Perú), 12 (Guatemala)',
    )
    
    # Identificación fiscal
    ruc = models.CharField(max_length=20, blank=True, null=True, verbose_name='NIT')
    
    # Contacto
    telefono = models.CharField(max_length=30, blank=True, null=True)
    telefono2 = models.CharField(max_length=30, blank=True, null=True, verbose_name='Teléfono alternativo')
    email = models.EmailField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    
    # Dirección
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Perú', blank=True)
    
    # Personalización visual
    color_primario = models.CharField(max_length=7, default='#0bb8c8', help_text='Color hexadecimal Ej: #0bb8c8')

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuración'

    def __str__(self):
        return self.nombre_empresa

    @classmethod
    def get_config(cls):
        """Retorna la única instancia de configuración, creándola si no existe."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def tasa_impuesto(self):
        return Decimal(self.porcentaje_impuesto or 0) / Decimal('100')

    def save(self, *args, **kwargs):
        # Garantizar que solo exista una instancia (singleton)
        self.pk = 1
        super().save(*args, **kwargs)
