from django.db import models
from apps.agenda.models import Cita
from django.contrib.auth.models import User

class ServicioGrooming(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='grooming')
    peluquero = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True})
    
    # Checklists de servicios realizados
    bano = models.BooleanField(default=False, verbose_name="Baño")
    corte_pelo = models.BooleanField(default=False, verbose_name="Corte de Pelo")
    corte_unas = models.BooleanField(default=False, verbose_name="Corte de Uñas")
    limpieza_oidos = models.BooleanField(default=False, verbose_name="Limpieza de Oídos")
    glandulas = models.BooleanField(default=False, verbose_name="Cepillado Glándulas Anales")
    perfume = models.BooleanField(default=False, verbose_name="Perfume/Lazo")
    
    observaciones = models.TextField(blank=True, null=True, help_text="Ej: Presencia de pulgas, alergias de piel")
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Servicio Grooming - {self.cita.mascota.nombre}"
