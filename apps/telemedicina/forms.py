from django import forms
from django.db import models
from django.utils import timezone
from apps.telemedicina.models import ConsultaVirtual
from apps.agenda.models import Cita

class ConsultaVirtualForm(forms.ModelForm):
    class Meta:
        model = ConsultaVirtual
        fields = ['cita', 'plataforma', 'enlace_reunion', 'codigo_acceso', 'estado_conexion', 'notas_preliminares']
        widgets = {
            'cita': forms.Select(attrs={'class': 'form-select'}),
            'plataforma': forms.Select(attrs={'class': 'form-select'}),
            'enlace_reunion': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/...'}),
            'codigo_acceso': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_conexion': forms.Select(attrs={'class': 'form-select'}),
            'notas_preliminares': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.localdate()
        base = models.Q(tipo='CONSULTA', consulta_virtual__isnull=True, is_active=True, fecha__gte=hoy)
        if self.instance and self.instance.pk:
            base = base | models.Q(pk=self.instance.cita_id)
        self.fields['cita'].queryset = Cita.objects.filter(base).select_related('mascota__cliente').order_by('fecha', 'hora')
        self.fields['cita'].label_from_instance = lambda c: (
            f"{c.fecha:%d/%m/%Y} {c.hora:%H:%M} · {c.mascota.nombre} · {c.mascota.cliente.nombre_completo} · {c.motivo}"
        )
