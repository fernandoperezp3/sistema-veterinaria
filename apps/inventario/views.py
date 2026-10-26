from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.inventario.models import Producto, Proveedor, Categoria, Movimiento
from apps.inventario.forms import ProductoForm, ProveedorForm, MovimientoForm, CategoriaForm


@login_required
def producto_lista(request):
    q = request.GET.get('q', '')
    productos = Producto.objects.select_related('categoria', 'proveedor').order_by('nombre')
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(categoria__nombre__icontains=q))
    stock_bajo = sum(1 for p in Producto.objects.filter(is_active=True) if p.necesita_reposicion)
    return render(request, 'inventario/productos.html', {
        'productos': productos, 'q': q, 'stock_bajo': stock_bajo
    })


@login_required
def producto_crear(request):
    form = ProductoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto registrado correctamente.')
        return redirect('producto_lista')
    return render(request, 'inventario/producto_form.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('producto_lista')
    return render(request, 'inventario/producto_form.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})


@login_required
def producto_estado(request, pk):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=pk)
        producto.is_active = not producto.is_active
        producto.save()
        estado_str = "activado" if producto.is_active else "desactivado"
        messages.success(request, f'Producto "{producto.nombre}" {estado_str}.')
    return redirect('producto_lista')


@login_required
def proveedor_lista(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'inventario/proveedores.html', {'proveedores': proveedores})


@login_required
def proveedor_crear(request):
    form = ProveedorForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Proveedor registrado.')
        return redirect('proveedor_lista')
    return render(request, 'inventario/proveedor_form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})


@login_required
def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    if form.is_valid():
        form.save()
        messages.success(request, 'Proveedor actualizado.')
        return redirect('proveedor_lista')
    return render(request, 'inventario/proveedor_form.html', {'form': form, 'titulo': 'Editar Proveedor'})


@login_required
def movimiento_lista(request):
    movimientos = Movimiento.objects.select_related('producto').order_by('-fecha')[:100]
    return render(request, 'inventario/movimientos.html', {'movimientos': movimientos})


@login_required
def movimiento_crear(request):
    form = MovimientoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Movimiento registrado. Stock actualizado.')
        return redirect('movimiento_lista')
    return render(request, 'inventario/movimiento_form.html', {'form': form, 'titulo': 'Registrar Movimiento'})


@login_required
def categoria_lista(request):
    categorias = Categoria.objects.prefetch_related('productos').order_by('nombre')
    return render(request, 'inventario/categorias.html', {'categorias': categorias})


@login_required
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoría creada.')
        return redirect('categoria_lista')
    return render(request, 'inventario/categoria_form.html', {'form': form, 'titulo': 'Nueva Categoría'})


@login_required
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        messages.success(request, 'Categoría actualizada.')
        return redirect('categoria_lista')
    return render(request, 'inventario/categoria_form.html', {'form': form, 'titulo': 'Editar Categoría'})
