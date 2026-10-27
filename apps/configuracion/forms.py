from django import forms
from apps.configuracion.models import Configuracion


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = [
            'nombre_empresa', 'slogan', 'logo',
            'simbolo_moneda', 'nombre_moneda', 'nombre_impuesto', 'porcentaje_impuesto', 'ruc',
            'telefono', 'telefono2', 'email', 'sitio_web',
            'direccion', 'ciudad', 'pais',
            'color_primario',
        ]
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la clínica'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Eslogan o descripción corta'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'simbolo_moneda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Q'}),
            'nombre_moneda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quetzales'}),
            'nombre_impuesto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IGV / IVA'}),
            'porcentaje_impuesto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+51 999 999 999'}),
            'telefono2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono alternativo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@veterinaria.com'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://miveterinaria.com'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Av. Principal 123'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lima'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Perú'}),
            'color_primario': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }
