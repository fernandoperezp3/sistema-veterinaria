"""
Cliente de Integración con Microservicios Satélite para VetSystem
Permite al monolito Django consumir los microservicios desacoplados:
- MS 1: Notificaciones (Puerto 8081)
- MS 2: Facturación & Pagos (Puerto 8082)
- MS 3: Telemedicina & WebSockets (Puerto 8083)
- MS 4: Reportes & BI (Puerto 8084)

Tolerante a fallos: Si los microservicios están apagados, el sistema no falla
y continúa su operación normal en Django con un log preventivo.
"""

import os
import time

import requests
from django.conf import settings

HOST = getattr(settings, "MICROSERVICES_HOST", "127.0.0.1")


def _servicio(clave, puerto, nombre, icono, color):
    base = os.environ.get(f"MS_{clave.upper()}_URL", f"http://{HOST}:{puerto}").rstrip("/")
    return {
        "nombre": nombre,
        "url": base,
        "health": f"{base}/health",
        "docs": f"http://127.0.0.1:{puerto}/docs",
        "puerto": puerto,
        "icono": icono,
        "color": color,
    }


class MicroservicesClient:
    SERVICES = {
        'notificaciones': _servicio('notificaciones', 8081, 'Notificaciones y Recordatorios', 'fa-bell', 'primary'),
        'facturacion': _servicio('facturacion', 8082, 'Facturación Electrónica & Pagos', 'fa-file-invoice-dollar', 'success'),
        'telemedicina': _servicio('telemedicina', 8083, 'Telemedicina & Streaming WebRTC', 'fa-video', 'info'),
        'reportes': _servicio('reportes', 8084, 'Reportes Asíncronos & BI', 'fa-chart-pie', 'warning'),
    }

    @classmethod
    def ping_all(cls):
        """Verifica en tiempo real la salud y latencia de los 4 microservicios."""
        estados = {}
        for key, s in cls.SERVICES.items():
            t0 = time.time()
            try:
                res = requests.get(s['health'], timeout=1.5)
                latencia_ms = int((time.time() - t0) * 1000)
                if res.status_code == 200:
                    data = res.json()
                    estados[key] = {
                        **s,
                        'estado': 'ONLINE',
                        'online': True,
                        'latencia_ms': latencia_ms,
                        'data': data
                    }
                else:
                    estados[key] = {
                        **s,
                        'estado': f'ERROR {res.status_code}',
                        'online': False,
                        'latencia_ms': latencia_ms,
                        'data': {}
                    }
            except Exception:
                estados[key] = {
                    **s,
                    'estado': 'OFFLINE',
                    'online': False,
                    'latencia_ms': None,
                    'data': {}
                }
        return estados

    @classmethod
    def notificar_cita(cls, cita_id, cliente_nombre, telefono, mascota_nombre, fecha, hora, motivo):
        """Envía petición asíncrona al Microservicio de Notificaciones."""
        payload = {
            "cita_id": cita_id,
            "cliente_nombre": cliente_nombre,
            "telefono": str(telefono or "000000000"),
            "mascota_nombre": mascota_nombre,
            "fecha": fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha),
            "hora": hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)[:5],
            "motivo": motivo or "Consulta General",
            "canal": "WHATSAPP"
        }
        try:
            res = requests.post(f"{cls.SERVICES['notificaciones']['url']}/api/v1/notificaciones/cita", json=payload, timeout=2.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @classmethod
    def notificar_vacuna(cls, vacuna_id, cliente_nombre, telefono, mascota_nombre, vacuna_nombre, fecha_limite):
        """Envía alerta de vacuna al Microservicio de Notificaciones."""
        payload = {
            "vacuna_id": vacuna_id,
            "cliente_nombre": cliente_nombre,
            "telefono": str(telefono or "000000000"),
            "mascota_nombre": mascota_nombre,
            "vacuna_nombre": vacuna_nombre,
            "fecha_limite": str(fecha_limite)
        }
        try:
            res = requests.post(f"{cls.SERVICES['notificaciones']['url']}/api/v1/notificaciones/vacuna", json=payload, timeout=2.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @classmethod
    def emitir_comprobante_fiscal(cls, factura_id, numero, cliente_nombre, documento, total, igv, subtotal, items=None):
        """Envía solicitud de timbrado digital y firma fiscal al Microservicio de Facturación."""
        payload = {
            "factura_id": factura_id,
            "numero_factura": numero,
            "cliente_nombre": cliente_nombre or "Cliente General",
            "cliente_documento": documento or "00000000",
            "tipo_comprobante": "BOLETA",
            "subtotal": float(subtotal),
            "igv": float(igv),
            "total": float(total),
            "items": items or []
        }
        try:
            res = requests.post(f"{cls.SERVICES['facturacion']['url']}/api/v1/facturacion/emitir-comprobante", json=payload, timeout=2.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @classmethod
    def procesar_pago_tarjeta(cls, numero_factura, monto, titular, tarjeta="4242", moneda="GTQ"):
        payload = {
            "factura_numero": numero_factura,
            "monto": float(monto),
            "moneda": moneda,
            "numero_tarjeta_enmascarado": f"**** **** **** {tarjeta[-4:]}",
            "titular": titular or "Cliente General",
            "pasarela": "STRIPE",
        }
        try:
            res = requests.post(f"{cls.SERVICES['facturacion']['url']}/api/v1/pagos/procesar-tarjeta", json=payload, timeout=2.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @classmethod
    def historial(cls, servicio, ruta):
        try:
            res = requests.get(f"{cls.SERVICES[servicio]['url']}{ruta}", timeout=1.5)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    @classmethod
    def crear_sala_telemedicina(cls, cita_id, veterinario, paciente, propietario):
        """Genera una sala virtual en el Microservicio de Telemedicina."""
        payload = {
            "cita_id": cita_id,
            "veterinario": veterinario,
            "paciente": paciente,
            "propietario": propietario
        }
        try:
            res = requests.post(f"{cls.SERVICES['telemedicina']['url']}/api/v1/telemedicina/crear-sala", json=payload, timeout=2.0)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None
