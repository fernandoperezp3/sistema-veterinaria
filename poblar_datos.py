"""
Script de datos de demostración para el Sistema Veterinaria
Ejecutar con: python poblar_datos.py
"""
import os
import sys
import django
from datetime import date, timedelta, time

# Fix encoding Windows
sys.stdout.reconfigure(encoding='utf-8')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veterinaria.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from apps.clientes.models import Cliente, Mascota
from apps.inventario.models import Categoria, Proveedor, Producto, Movimiento
from apps.agenda.models import Cita
from apps.medico.models import HistoriaClinica, Vacuna, Receta, DetalleReceta
from apps.facturacion.models import Factura, DetalleFactura, Caja
from apps.configuracion.models import Configuracion

print(">>> Iniciando carga de datos de demostracion...")

# ─── 1. VETERINARIOS (Staff) ────────────────────────────────────────────────
print("\n👨‍⚕️ Creando veterinarios...")

def get_or_create_vet(username, first, last, email):
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.first_name = first
        user.last_name = last
        user.email = email
        user.is_staff = True
        user.set_password('vet123456')
        user.save()
        print(f"   ✓ Veterinario: {first} {last}")
    return user

vet1 = get_or_create_vet('dr_garcia', 'Carlos', 'García López', 'cgarcia@vetclinica.com')
vet2 = get_or_create_vet('dra_morales', 'Ana', 'Morales Ruiz', 'amorales@vetclinica.com')

# ─── 2. CLIENTES Y MASCOTAS ──────────────────────────────────────────────────
print("\n👥 Creando clientes y mascotas...")

clientes_data = [
    ('María',   'López Gómez',    '1234567890', '5512-3456', 'maria.lopez@gmail.com',   'Zona 10, Ciudad de Guatemala'),
    ('Carlos',  'Martínez Díaz',  '2345678901', '5523-4567', 'cmartinez@hotmail.com',   'Mixco, Guatemala'),
    ('Sofía',   'Ramírez Pérez',  '3456789012', '5534-5678', 'sofia.ramirez@yahoo.com', 'Villa Nueva, Guatemala'),
    ('Luis',    'Hernández Soto', '4567890123', '5545-6789', 'lhernandez@gmail.com',    'Zona 1, Guatemala'),
    ('Ana',     'Torres Vidal',   '5678901234', '5556-7890', 'ana.torres@outlook.com',  'San Miguel Petapa'),
    ('Pedro',   'Castro Fuentes', '6789012345', '5567-8901', 'pcastro@gmail.com',       'Amatitlán, Guatemala'),
    ('Laura',   'Jiménez Cruz',   '7890123456', '5578-9012', 'ljimenez@gmail.com',      'Zona 15, Guatemala'),
    ('Roberto', 'Flores Lima',    '8901234567', '5589-0123', 'rflores@hotmail.com',     'Fraijanes, Guatemala'),
    ('Carmen',  'Vega Solano',    '9012345678', '5590-1234', 'carmen.vega@gmail.com',   'Santa Catarina Pinula'),
    ('Miguel',  'Ortiz Ruano',    '0123456789', '5501-2345', 'miguel.ortiz@yahoo.com',  'Zona 7, Guatemala'),
]

mascotas_data = [
    ('Max',    'CANINO', 'Labrador Retriever',  'M', 3, 28.5, 'Amarillo'),
    ('Luna',   'FELINO', 'Siamés',              'H', 2,  4.2, 'Crema con puntas oscuras'),
    ('Rocky',  'CANINO', 'Bulldog Francés',     'M', 4, 12.0, 'Atigrado'),
    ('Mimi',   'FELINO', 'Persa',               'H', 1,  3.8, 'Blanco'),
    ('Thor',   'CANINO', 'Golden Retriever',    'M', 5, 32.0, 'Dorado'),
    ('Kira',   'CANINO', 'Beagle',              'H', 2, 10.5, 'Tricolor'),
    ('Simba',  'FELINO', 'Maine Coon',          'M', 3,  6.5, 'Naranja atigrado'),
    ('Bella',  'CANINO', 'Poodle',              'H', 6,  7.2, 'Blanco'),
    ('Coco',   'AVE',    'Loro Nuca Amarilla',  'M', 8, 0.45, 'Verde con amarillo'),
    ('Nala',   'CANINO', 'Husky Siberiano',     'H', 1, 18.0, 'Blanco y gris'),
    ('Oliver', 'FELINO', 'Gato Doméstico',      'M', 4,  5.1, 'Negro'),
    ('Canela', 'CANINO', 'Dachshund',           'H', 3,  8.8, 'Canela'),
    ('Paco',   'AVE',    'Perico',              'M', 2, 0.08, 'Verde'),
    ('Lola',   'CANINO', 'Shih Tzu',            'H', 2,  5.5, 'Blanco y dorado'),
    ('Tigre',  'FELINO', 'Bengalí',             'M', 5,  7.3, 'Manchas marrones'),
]

clientes_creados = []
for nombres, apellidos, dni, tel, email, dir in clientes_data:
    cliente, created = Cliente.objects.get_or_create(
        dni=dni,
        defaults={'nombres': nombres, 'apellidos': apellidos, 'telefono': tel, 'email': email, 'direccion': dir},
    )
    clientes_creados.append(cliente)
    if created:
        print(f"   ✓ Cliente: {nombres} {apellidos}")

mascotas_creadas = []
hoy = date.today()
for i, (nombre, especie, raza, sexo, anios, peso, color) in enumerate(mascotas_data):
    cliente = clientes_creados[i % len(clientes_creados)]
    fnac = hoy - timedelta(days=anios * 365)
    mascota, created = Mascota.objects.get_or_create(
        nombre=nombre, cliente=cliente,
        defaults={'especie': especie, 'raza': raza, 'sexo': sexo, 'fecha_nacimiento': fnac, 'peso_actual': peso, 'color': color},
    )
    mascotas_creadas.append(mascota)
    if created:
        print(f"   ✓ Mascota: {nombre} ({especie}) — {cliente.nombres}")

# ─── 3. INVENTARIO ───────────────────────────────────────────────────────────
print("\n📦 Creando inventario...")

cat_med, _ = Categoria.objects.get_or_create(nombre='Medicamentos', defaults={'descripcion': 'Fármacos y antibióticos'})
cat_vac, _ = Categoria.objects.get_or_create(nombre='Vacunas',      defaults={'descripcion': 'Vacunas preventivas'})
cat_ins, _ = Categoria.objects.get_or_create(nombre='Insumos',      defaults={'descripcion': 'Material de uso médico'})
cat_ali, _ = Categoria.objects.get_or_create(nombre='Alimentos',    defaults={'descripcion': 'Alimentos y suplementos'})

prov1, _ = Proveedor.objects.get_or_create(ruc='10123456789', defaults={
    'nombre': 'DistribuidoraVet Guatemala', 'telefono': '2255-1234', 'email': 'ventas@distvet.com.gt'})
prov2, _ = Proveedor.objects.get_or_create(ruc='20234567890', defaults={
    'nombre': 'MediPet S.A.', 'telefono': '2266-5678', 'email': 'pedidos@medipet.com.gt'})

productos_info = [
    ('MED-001', 'Amoxicilina 500mg (frasco 30 caps)',    cat_med, prov1,  45.00,  85.00, 50, 10),
    ('MED-002', 'Meloxicam 1mg/ml Inyectable 10ml',      cat_med, prov1,  38.00,  70.00, 30,  5),
    ('MED-003', 'Ivermectina 1% solución 50ml',          cat_med, prov2,  22.00,  45.00, 40,  8),
    ('VAC-001', 'Vacuna Parvovirus + Distemper (dosis)',  cat_vac, prov2,  55.00, 120.00, 25,  5),
    ('VAC-002', 'Vacuna Rabia Canina (dosis)',            cat_vac, prov2,  40.00,  90.00, 30,  5),
    ('VAC-003', 'Vacuna Triple Felina (dosis)',           cat_vac, prov2,  48.00, 110.00, 20,  5),
    ('INS-001', 'Jeringas 3ml desechables (caja x100)',  cat_ins, prov1,  35.00,  60.00, 150, 20),
    ('INS-002', 'Guantes de látex talla M (caja x50)',   cat_ins, prov1,  28.00,  50.00, 100, 15),
    ('ALI-001', 'Alimento Royal Canin Adulto 15kg',      cat_ali, prov1, 180.00, 280.00, 12,   3),
    ('ALI-002', 'Alimento Hills Science Diet 3kg',       cat_ali, prov2,  95.00, 155.00,  8,   3),
]

productos_creados = []
for cod, nom, cat, prov, pc, pv, stock, min_stock in productos_info:
    prod, created = Producto.objects.get_or_create(
        codigo=cod,
        defaults={'nombre': nom, 'categoria': cat, 'proveedor': prov,
                  'precio_compra': pc, 'precio_venta': pv,
                  'stock_actual': 0, 'stock_minimo': min_stock},
    )
    productos_creados.append(prod)
    if created:
        print(f"   ✓ Producto: {nom}")
        Movimiento.objects.create(producto=prod, tipo='ENTRADA', cantidad=stock, motivo='Stock inicial de apertura')

# ─── 4. CITAS ────────────────────────────────────────────────────────────────
print("\n📅 Creando citas...")

citas_info = [
    (0,  vet1, -30, time(9, 0),  'CONSULTA',  'COMPLETADA', 'Revisión general y pesaje'),
    (1,  vet2, -25, time(10,30), 'VACUNACION','COMPLETADA', 'Vacuna triple felina anual'),
    (2,  vet1, -20, time(8, 0),  'CONSULTA',  'COMPLETADA', 'Dermatitis crónica — seguimiento'),
    (3,  vet2, -18, time(11, 0), 'VACUNACION','COMPLETADA', 'Primera dosis de vacunas gatito'),
    (4,  vet1, -15, time(14, 0), 'CONTROL',   'COMPLETADA', 'Control post-operatorio'),
    (5,  vet2, -12, time(9, 30), 'CONSULTA',  'COMPLETADA', 'Vómitos y pérdida de apetito'),
    (6,  vet1, -10, time(10, 0), 'GROOMING',  'COMPLETADA', 'Baño, corte y limpieza de oídos'),
    (7,  vet2,  -8, time(16, 0), 'CONSULTA',  'COMPLETADA', 'Revisión dental — cálculo'),
    (8,  vet1,  -5, time(11,30), 'CONSULTA',  'COMPLETADA', 'Revisión general loro'),
    (9,  vet2,  -3, time(9, 0),  'VACUNACION','COMPLETADA', 'Antirrábica primer año'),
    (10, vet1,  -2, time(10, 0), 'CONSULTA',  'COMPLETADA', 'Herida en pata delantera'),
    (11, vet2,  -1, time(15, 0), 'GROOMING',  'COMPLETADA', 'Baño especial y corte de uñas'),
    (12, vet1,   0, time(9, 0),  'CONSULTA',  'PENDIENTE',  'Revisión general perico'),
    (13, vet2,   0, time(11, 0), 'VACUNACION','EN_ESPERA',  'Vacunas cachorra — 2da dosis'),
    (0,  vet1,   0, time(14,30), 'CONTROL',   'PENDIENTE',  'Control mensual labrador'),
    (2,  vet2,   1, time(9, 30), 'CONSULTA',  'PENDIENTE',  'Seguimiento dermatitis'),
    (4,  vet1,   2, time(10, 0), 'CIRUGIA',   'PENDIENTE',  'Esterilización programada'),
    (6,  vet2,   3, time(8, 30), 'GROOMING',  'PENDIENTE',  'Baño y corte de pelo'),
    (9,  vet1,   5, time(11, 0), 'CONSULTA',  'PENDIENTE',  'Chequeo post-vacuna'),
    (14, vet2,   7, time(15, 0), 'VACUNACION','PENDIENTE',  'Vacuna triple felina — 1ra dosis'),
]

citas_creadas = []
for m_idx, vet, dias, hora, tipo, estado, motivo in citas_info:
    mascota = mascotas_creadas[m_idx]
    fecha_cita = hoy + timedelta(days=dias)
    cita, created = Cita.objects.get_or_create(
        mascota=mascota, fecha=fecha_cita, hora=hora,
        defaults={'veterinario': vet, 'tipo': tipo, 'estado': estado, 'motivo': motivo},
    )
    citas_creadas.append(cita)
    if created:
        print(f"   ✓ Cita: {mascota.nombre} — {fecha_cita} [{estado}]")

# ─── 5. HISTORIAS CLÍNICAS ───────────────────────────────────────────────────
print("\n📋 Creando historias clínicas...")

historias_info = [
    (0,  vet1, 'Revisión general', 'Paciente activo, come bien, sin síntomas.', 28.5, 38.5, 88, 22, 'Rosadas', '< 2 seg',
     'Paciente en buen estado de salud general.', 'Desparasitación interna. Continuar dieta balanceada.', None),
    (1,  vet2, 'Aplicación vacuna triple', 'Gatita traída para vacunación anual. Sin antecedentes.', 4.2, 38.2, 140, 24, 'Rosadas', '< 2 seg',
     'Paciente sana, apta para vacunación.', 'Vacuna triple felina aplicada. Sin reacciones adversas.', 'Próxima dosis en 12 meses.'),
    (5,  vet2, 'Gastroenteritis aguda', 'Vómitos 3 veces al día y rechazo de alimento por 48 horas.', 10.5, 39.1, 100, 26, 'Pálidas', '2-3 seg',
     'Gastroenteritis aguda. Posible intoxicación alimentaria.', 'Ayuno 12h, dieta blanda. Metronidazol 250mg c/12h x 5 días.', 'Revisión en 5 días si no mejora.'),
    (7,  vet2, 'Limpieza dental', 'Mal aliento y dificultad para masticar desde hace 2 semanas.', 7.2, 38.3, 80, 20, 'Rosadas', '< 2 seg',
     'Periodontitis grado II. Cálculo dental generalizado.', 'Limpieza dental bajo anestesia. Extracción de 2 piezas. Antibiótico profiláctico.', 'Cepillado dental diario.'),
]

for m_idx, vet, motivo, anam, peso, temp, fc, fr, muc, tlc, diag, trat, obs in historias_info:
    mascota = mascotas_creadas[m_idx]
    cita_completada = next((c for c in citas_creadas if c.mascota == mascota and c.estado == 'COMPLETADA'), None)
    if not HistoriaClinica.objects.filter(mascota=mascota).exists():
        h = HistoriaClinica.objects.create(
            mascota=mascota, cita=cita_completada, veterinario=vet,
            motivo_consulta=motivo, anamnesis=anam,
            peso=peso, temperatura=temp, frecuencia_cardiaca=fc,
            frecuencia_respiratoria=fr, mucosas=muc, tiempo_llenado_capilar=tlc,
            diagnostico=diag, tratamiento=trat, observaciones=obs or '',
            proxima_cita=hoy + timedelta(days=30),
        )
        receta = Receta.objects.create(historia_clinica=h, indicaciones_generales='Administrar con alimento. Completar tratamiento.')
        if m_idx == 5:
            DetalleReceta.objects.create(receta=receta, medicamento='Metronidazol 250mg', dosis='1 tableta', frecuencia='Cada 12 horas', duracion='5 días', cantidad=10)
            DetalleReceta.objects.create(receta=receta, medicamento='Suero oral', dosis='20ml/kg', frecuencia='Cada 6 horas', duracion='2 días', cantidad=2)
        print(f"   ✓ Historia clínica: {mascota.nombre}")

# ─── 6. VACUNAS ──────────────────────────────────────────────────────────────
print("\n💉 Creando registro de vacunas...")

vacunas_info = [
    (0,  vet1, 'Parvovirus + Distemper', 'LOT-2024-A1', -180, 185),
    (0,  vet1, 'Rabia Canina',           'LOT-2024-B2', -365,   0),
    (1,  vet2, 'Triple Felina',          'LOT-2024-C3',  -25, 340),
    (4,  vet1, 'Parvovirus + Distemper', 'LOT-2024-A2',  -90, 275),
    (4,  vet1, 'Rabia Canina',           'LOT-2024-B3',  -90, 275),
    (5,  vet2, 'Parvovirus + Distemper', 'LOT-2024-A3',  -60, 305),
    (9,  vet2, 'Rabia Canina',           'LOT-2024-B4',   -3, 362),
    (13, vet2, 'Parvovirus + Distemper', 'LOT-2024-A4',  -10, 355),
]

for m_idx, vet, nombre, lote, dias_aplic, dias_prox in vacunas_info:
    mascota = mascotas_creadas[m_idx]
    f_aplic = hoy + timedelta(days=dias_aplic)
    f_prox  = hoy + timedelta(days=dias_prox) if dias_prox > 0 else None
    if not Vacuna.objects.filter(mascota=mascota, nombre_vacuna=nombre, fecha_aplicacion=f_aplic).exists():
        Vacuna.objects.create(
            mascota=mascota, veterinario=vet, nombre_vacuna=nombre,
            lote=lote, fecha_aplicacion=f_aplic, fecha_proxima_dosis=f_prox,
        )
        print(f"   ✓ Vacuna: {nombre} → {mascota.nombre}")

# ─── 7. FACTURAS ─────────────────────────────────────────────────────────────
print("\n🧾 Creando facturas...")

admin = User.objects.filter(is_superuser=True).first()
cajero_nombre = f"{admin.first_name} {admin.last_name}".strip() if admin else "Administrador"

config = Configuracion.get_config()
tasa = float(config.tasa_impuesto)

facturas_info = [
    (0,  'F-2026-001', 'EFECTIVO',      [('Consulta médica general', 80.00, 1), ('Desparasitante interno', 45.00, 1)]),
    (1,  'F-2026-002', 'TARJETA',       [('Vacuna triple felina', 110.00, 1), ('Consulta de vacunación', 50.00, 1)]),
    (2,  'F-2026-003', 'TRANSFERENCIA', [('Consulta dermatología', 100.00, 1), ('Shampoo medicado', 65.00, 1)]),
    (3,  'F-2026-004', 'EFECTIVO',      [('Vacunas gatito paquete completo', 200.00, 1)]),
    (4,  'F-2026-005', 'TARJETA',       [('Control post-operatorio', 60.00, 1), ('Analgésico Meloxicam', 70.00, 1)]),
    (5,  'F-2026-006', 'EFECTIVO',      [('Consulta gastroenteritis', 80.00, 1), ('Metronidazol tratamiento', 45.00, 2)]),
    (6,  'F-2026-007', 'TRANSFERENCIA', [('Servicio de Grooming completo', 150.00, 1)]),
    (7,  'F-2026-008', 'TARJETA',       [('Limpieza dental con anestesia', 450.00, 1), ('Antibiótico profiláctico', 85.00, 1)]),
    (8,  'F-2026-009', 'EFECTIVO',      [('Consulta loro revision general', 80.00, 1)]),
    (9,  'F-2026-010', 'EFECTIVO',      [('Vacuna antirrábica', 90.00, 1), ('Consulta general', 50.00, 1)]),
    (0,  'F-2026-011', 'TARJETA',       [('Alimento Royal Canin 15kg', 280.00, 1)]),
    (10, 'F-2026-012', 'TRANSFERENCIA', [('Consulta herida pata', 100.00, 1), ('Antibiótico Amoxicilina', 85.00, 1), ('Curación y vendaje', 40.00, 1)]),
]

for c_idx, nro, metodo, items in facturas_info:
    if Factura.objects.filter(numero=nro).exists():
        continue
    cliente = clientes_creados[c_idx % len(clientes_creados)]
    subtotal = sum(p * q for _, p, q in items)
    igv = round(subtotal * tasa, 2)
    total = round(subtotal + igv, 2)
    factura = Factura.objects.create(
        cliente=cliente, numero=nro, metodo_pago=metodo,
        subtotal=subtotal, igv=igv, total=total,
        estado='PAGADA', cajero=cajero_nombre,
    )
    for desc, precio, cant in items:
        DetalleFactura.objects.create(
            factura=factura, descripcion=desc,
            precio_unitario=precio, cantidad=cant, subtotal=precio * cant,
        )
    print(f"   ✓ Factura {nro}: {config.simbolo_moneda}{total:.2f} — {cliente.nombres}")

# ─── 8. CAJA ─────────────────────────────────────────────────────────────────
print("\n💰 Creando caja del día...")
from django.db.models import Sum
from django.utils import timezone
ingresos_hoy = Factura.objects.filter(fecha__date=timezone.localdate(), estado='PAGADA').aggregate(t=Sum('total'))['t'] or 0
caja, created = Caja.objects.get_or_create(
    fecha=timezone.localdate(),
    defaults={'monto_inicial': 500.00, 'total_ingresos': ingresos_hoy, 'total_egresos': 0.00, 'monto_final': 500 + ingresos_hoy, 'cerrada': False},
)
if created:
    print(f"   ✓ Caja del día {hoy} creada")

print("\n" + "="*55)
print("✅ ¡Datos de demostración cargados exitosamente!")
print("="*55)
print(f"   👥 Clientes:          {Cliente.objects.count()}")
print(f"   🐾 Mascotas:          {Mascota.objects.count()}")
print(f"   📦 Productos:         {Producto.objects.count()}")
print(f"   📅 Citas totales:     {Cita.objects.count()}")
print(f"   📋 Historias clín.:   {HistoriaClinica.objects.count()}")
print(f"   💉 Vacunas:           {Vacuna.objects.count()}")
print(f"   🧾 Facturas:          {Factura.objects.count()}")
print("="*55)
