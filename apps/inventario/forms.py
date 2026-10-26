from django import forms
from apps.inventario.models import Producto, Proveedor, Categoria, Movimiento


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'telefono', 'email', 'direccion', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Persona de contacto'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'categoria', 'proveedor', 'descripcion',
                  'precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo',
                  'fecha_vencimiento', 'is_active']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código (opcional)'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'tipo', 'cantidad', 'motivo', 'comprobante']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motivo del movimiento'}),
            'comprobante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° comprobante (opcional)'}),
        }
        help_texts = {
            'cantidad': 'En "Ajuste de Inventario" la cantidad es el nuevo stock total del producto.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(is_active=True).order_by('nombre')

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get('producto')
        tipo = cleaned.get('tipo')
        cantidad = cleaned.get('cantidad')
        if cantidad is not None:
            if tipo in ('ENTRADA', 'SALIDA') and cantidad <= 0:
                self.add_error('cantidad', 'La cantidad debe ser mayor a cero.')
            if tipo == 'AJUSTE' and cantidad < 0:
                self.add_error('cantidad', 'El stock no puede ser negativo.')
            if tipo == 'SALIDA' and producto and cantidad > producto.stock_actual:
                self.add_error('cantidad', f'Stock insuficiente. Disponible: {producto.stock_actual}.')
        return cleaned
