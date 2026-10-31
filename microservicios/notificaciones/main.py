"""
Microservicio 1: Notificaciones y Recordatorios Automáticos
Puerto: 8081
Framework: FastAPI (Python 3.12/3.13)
Swagger Docs: http://127.0.0.1:8081/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from urllib.parse import quote
import re
import time

app = FastAPI(
    title="VetSystem - Microservicio de Notificaciones",
    description="Servicio desacoplado para envío asíncrono de recordatorios de citas, alertas de vacunación y avisos vía WhatsApp/SMS/Email.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NOTIFICACIONES_LOG = []
START_TIME = time.time()
CODIGO_PAIS = "502"


def enlace_whatsapp(telefono, mensaje):
    numero = re.sub(r"\D", "", telefono or "")
    if not numero or set(numero) == {"0"}:
        return None
    if len(numero) == 8:
        numero = CODIGO_PAIS + numero
    return f"https://wa.me/{numero}?text={quote(mensaje)}"

class CitaNotificationRequest(BaseModel):
    cita_id: int
    cliente_nombre: str
    telefono: str
    email: Optional[str] = None
    mascota_nombre: str
    fecha: str
    hora: str
    motivo: Optional[str] = "Consulta General"
    canal: Optional[str] = "WHATSAPP"
    enlace_videollamada: Optional[str] = None

class VacunaNotificationRequest(BaseModel):
    vacuna_id: int
    cliente_nombre: str
    telefono: str
    mascota_nombre: str
    vacuna_nombre: str
    fecha_limite: str

@app.get("/health")
def health_check():
    uptime_sec = int(time.time() - START_TIME)
    return {
        "microservicio": "Notificaciones & Recordatorios",
        "estado": "ONLINE",
        "puerto": 8081,
        "uptime_segundos": uptime_sec,
        "notificaciones_procesadas": len(NOTIFICACIONES_LOG),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/notificaciones/cita")
def notificar_cita(req: CitaNotificationRequest):
    if req.enlace_videollamada:
        mensaje = (
            f"Hola {req.cliente_nombre}, le recordamos la videoconsulta de su mascota {req.mascota_nombre} "
            f"el día {req.fecha} a las {req.hora} con Clínica VetSystem. Motivo: {req.motivo}. "
            f"Ingrese a la videollamada aquí: {req.enlace_videollamada} "
            f"(si aparece un aviso de seguridad, elija Avanzado y luego Continuar)."
        )
    else:
        mensaje = (
            f"Hola {req.cliente_nombre}, le recordamos la cita para su mascota {req.mascota_nombre} "
            f"el día {req.fecha} a las {req.hora} en Clínica VetSystem. Motivo: {req.motivo}."
        )
    
    registro = {
        "id": len(NOTIFICACIONES_LOG) + 1,
        "tipo": "TELECONSULTA" if req.enlace_videollamada else "CITA",
        "cita_id": req.cita_id,
        "destinatario": req.cliente_nombre,
        "telefono": req.telefono,
        "canal": req.canal,
        "mensaje": mensaje,
        "enlace_whatsapp": enlace_whatsapp(req.telefono, mensaje),
        "estado": "PREPARADO",
        "fecha_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    NOTIFICACIONES_LOG.append(registro)
    
    return {
        "success": True,
        "mensaje": f"Notificación preparada para {req.canal}",
        "detalle": registro
    }

@app.post("/api/v1/notificaciones/vacuna")
def notificar_vacuna(req: VacunaNotificationRequest):
    mensaje = (
        f"Aviso Preventivo: Su mascota {req.mascota_nombre} tiene programada su vacuna "
        f"'{req.vacuna_nombre}' próxima a vencer el {req.fecha_limite}. Agende su cita en VetSystem."
    )
    
    registro = {
        "id": len(NOTIFICACIONES_LOG) + 1,
        "tipo": "VACUNA",
        "vacuna_id": req.vacuna_id,
        "destinatario": req.cliente_nombre,
        "telefono": req.telefono,
        "canal": "WHATSAPP",
        "mensaje": mensaje,
        "enlace_whatsapp": enlace_whatsapp(req.telefono, mensaje),
        "estado": "PREPARADO",
        "fecha_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    NOTIFICACIONES_LOG.append(registro)
    
    return {
        "success": True,
        "mensaje": "Alerta de vacunación preparada para WhatsApp",
        "detalle": registro
    }

@app.get("/api/v1/notificaciones/historial")
def obtener_historial():
    return {
        "total": len(NOTIFICACIONES_LOG),
        "historial": list(reversed(NOTIFICACIONES_LOG[-50:]))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)
