from django import forms
from apps.clientes.models import Cliente, Mascota


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombres', 'apellidos', 'dni', 'telefono', 'email', 'direccion']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DPI / Documento'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección'}),
        }


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'sexo', 'fecha_nacimiento', 'peso_actual', 'color', 'microchip', 'foto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la mascota'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'raza': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Raza (opcional)'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'peso_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Kg'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Color/pelaje'}),
            'microchip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de microchip'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombres', 'apellidos', 'dni', 'telefono', 'direccion']
        labels = {'dni': 'DPI / Documento', 'telefono': 'Teléfono', 'direccion': 'Dirección'}
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de DPI'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '5555-5555'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
