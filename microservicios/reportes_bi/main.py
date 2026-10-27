"""
Microservicio 4: Generación Asíncrona de Reportes y Business Intelligence
Puerto: 8084
Framework: FastAPI + ReportLab (Python 3.12/3.13)
Swagger Docs: http://127.0.0.1:8084/docs
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from datetime import datetime
import time

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

app = FastAPI(
    title="VetSystem - Microservicio de Reportes & BI",
    description="Servicio desacoplado para procesamiento asíncrono y exportación de balances contables, fichas clínicas y reportes en PDF/Excel sin bloquear el servidor web principal.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()
REPORTES_DIR = os.path.join(os.path.dirname(__file__), "generados")
os.makedirs(REPORTES_DIR, exist_ok=True)

TAREAS_PROCESADAS = []

class BalanceRequest(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    generado_por: str = "Administrador"
    total_ingresos: float
    total_egresos: float
    citas_atendidas: int
    simbolo_moneda: str = "Q"

@app.get("/health")
def health_check():
    uptime_sec = int(time.time() - START_TIME)
    return {
        "microservicio": "Generación de Reportes & BI Asíncrono",
        "estado": "ONLINE",
        "puerto": 8084,
        "uptime_segundos": uptime_sec,
        "reportes_generados": len(TAREAS_PROCESADAS),
        "motor_pdf": "ReportLab 5.0",
        "timestamp": datetime.now().isoformat()
    }

def generar_pdf_tarea(filename: str, req: BalanceRequest):
    filepath = os.path.join(REPORTES_DIR, filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    w, h = letter

    # Encabezado Corporativo
    c.setFillColor(colors.HexColor("#0F172A"))
    c.rect(0, h - 80, w, 80, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, h - 45, "CLÍNICA VETERINARIA 'VetSystem'")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 65, f"Reporte Financiero y Operativo | Rango: {req.fecha_inicio} al {req.fecha_fin}")

    # Cuerpo del reporte
    c.setFillColor(colors.HexColor("#1E293B"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h - 120, "Resumen General del Período")

    c.setFont("Helvetica", 11)
    c.drawString(40, h - 150, f"Generado por: {req.generado_por}")
    c.drawString(40, h - 170, f"Fecha de emisión: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(40, h - 190, f"Total de Citas Médicas Atendidas: {req.citas_atendidas}")

    # Tabla de métricas
    c.setFillColor(colors.HexColor("#F1F5F9"))
    c.roundRect(40, h - 310, w - 80, 100, 8, fill=True, stroke=True)

    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, h - 235, "Concepto Económico")
    c.drawString(350, h - 235, "Monto (GTQ)")

    c.setFont("Helvetica", 11)
    c.drawString(60, h - 260, "(+) Total Ingresos por Servicios y Ventas:")
    c.drawString(350, h - 260, f"{req.simbolo_moneda} {req.total_ingresos:.2f}")

    c.drawString(60, h - 280, "(-) Total Gastos Operativos y Compras:")
    c.drawString(350, h - 280, f"{req.simbolo_moneda} {req.total_egresos:.2f}")

    balance_neto = req.total_ingresos - req.total_egresos
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#059669") if balance_neto >= 0 else colors.HexColor("#DC2626"))
    c.drawString(60, h - 300, "(=) Balance Neto de Utilidad:")
    c.drawString(350, h - 300, f"{req.simbolo_moneda} {balance_neto:.2f}")

    # Pie de página
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.setFont("Helvetica", 9)
    c.drawString(40, 40, "Documento emitido asíncronamente por el Microservicio de BI de VetSystem.")

    c.showPage()
    c.save()

@app.post("/api/v1/reportes/balance-pdf")
def solicitar_balance_pdf(req: BalanceRequest, background_tasks: BackgroundTasks):
    task_id = f"rep_{uuid.uuid4().hex[:8]}"
    filename = f"balance_{req.fecha_inicio}_{req.fecha_fin}_{task_id}.pdf"
    
    background_tasks.add_task(generar_pdf_tarea, filename, req)
    
    registro = {
        "task_id": task_id,
        "filename": filename,
        "tipo": "BALANCE_FINANCIERO_PDF",
        "estado": "EN_PROCESAMIENTO",
        "url_descarga": f"http://127.0.0.1:8084/api/v1/reportes/descargar/{filename}",
        "fecha_solicitud": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    TAREAS_PROCESADAS.append(registro)

    return {
        "success": True,
        "mensaje": "Tarea de generación de reporte enviada al worker en segundo plano.",
        "detalle": registro
    }

@app.get("/api/v1/reportes/descargar/{filename}")
def descargar_reporte(filename: str):
    filename = os.path.basename(filename)
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Archivo inválido.")
    filepath = os.path.join(REPORTES_DIR, filename)
    if not os.path.exists(filepath):
        time.sleep(0.5)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="El archivo aún se está generando o no existe.")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)

@app.get("/api/v1/reportes/historial")
def listar_reportes():
    return {
        "total": len(TAREAS_PROCESADAS),
        "tareas": list(reversed(TAREAS_PROCESADAS[-50:]))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8084, reload=True)
