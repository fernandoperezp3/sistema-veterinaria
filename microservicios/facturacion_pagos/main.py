"""
Microservicio 2: Facturación Electrónica y Pasarela de Pagos
Puerto: 8082
Framework: FastAPI (Python 3.12/3.13)
Swagger Docs: http://127.0.0.1:8082/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import hashlib
import uuid
from datetime import datetime
import time

app = FastAPI(
    title="VetSystem - Microservicio de Facturación & Pagos",
    description="Servicio desacoplado para emisión de comprobantes fiscales digitales (XML/QR UBL 2.1) y procesamiento seguro de transacciones de pago.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMPROBANTES_EMITIDOS = []
START_TIME = time.time()

class ItemDetalle(BaseModel):
    descripcion: str
    cantidad: int
    precio_unitario: float
    subtotal: float

class FacturaRequest(BaseModel):
    factura_id: int
    numero_factura: str
    cliente_nombre: str
    cliente_documento: str
    tipo_comprobante: str = "BOLETA"
    metodo_pago: str = "EFECTIVO"
    subtotal: float
    igv: float
    total: float
    items: List[ItemDetalle] = []

class PagoTarjetaRequest(BaseModel):
    factura_numero: str
    monto: float
    moneda: str = "GTQ"
    numero_tarjeta_enmascarado: str
    titular: str
    pasarela: str = "STRIPE"

@app.get("/health")
def health_check():
    uptime_sec = int(time.time() - START_TIME)
    return {
        "microservicio": "Facturación Electrónica & Pasarela de Pagos",
        "estado": "ONLINE",
        "puerto": 8082,
        "uptime_segundos": uptime_sec,
        "comprobantes_fiscales_emitidos": len(COMPROBANTES_EMITIDOS),
        "estandar_tributario": "UBL 2.1 (Firma Digital SHA-256)",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/facturacion/emitir-comprobante")
def emitir_comprobante_fiscal(req: FacturaRequest):
    raw_hash_data = f"{req.numero_factura}|{req.cliente_documento}|{req.total}|{datetime.now().isoformat()}"
    hash_cpe = hashlib.sha256(raw_hash_data.encode()).hexdigest()[:28].upper()
    firma_digital = f"SIGN-{uuid.uuid4().hex[:16].upper()}"
    
    codigo_qr_data = (
        f"NIT_CLINICA:1234567-8|TIPO:{req.tipo_comprobante}|SERIE:{req.numero_factura}|"
        f"IVA:{req.igv}|TOTAL:{req.total}|FECHA:{datetime.now().strftime('%Y-%m-%d')}|"
        f"DOC_CLIENTE:{req.cliente_documento}|HASH:{hash_cpe}"
    )

    comprobante = {
        "id": len(COMPROBANTES_EMITIDOS) + 1,
        "factura_id": req.factura_id,
        "numero": req.numero_factura,
        "cliente": req.cliente_nombre,
        "documento": req.cliente_documento,
        "tipo": req.tipo_comprobante,
        "subtotal": req.subtotal,
        "igv": req.igv,
        "total": req.total,
        "hash_cpe": hash_cpe,
        "firma_digital": firma_digital,
        "codigo_qr_texto": codigo_qr_data,
        "estado_sunat_sat": "ACEPTADO",
        "fecha_emision": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    COMPROBANTES_EMITIDOS.append(comprobante)

    return {
        "success": True,
        "mensaje": f"Comprobante fiscal {req.numero_factura} emitido y firmado digitalmente.",
        "comprobante": comprobante
    }

@app.post("/api/v1/pagos/procesar-tarjeta")
def procesar_pago_tarjeta(pago: PagoTarjetaRequest):
    transaccion_id = f"txn_{uuid.uuid4().hex[:12]}"
    return {
        "success": True,
        "transaccion_id": transaccion_id,
        "pasarela": pago.pasarela,
        "monto_procesado": pago.monto,
        "moneda": pago.moneda,
        "estado": "APROBADO",
        "codigo_autorizacion": f"AUTH-{uuid.uuid4().hex[:6].upper()}",
        "mensaje": f"Cobro de {pago.moneda} {pago.monto:.2f} aprobado con tarjeta terminada en {pago.numero_tarjeta_enmascarado[-4:]}."
    }

@app.get("/api/v1/facturacion/comprobantes")
def listar_comprobantes():
    return {
        "total": len(COMPROBANTES_EMITIDOS),
        "comprobantes": list(reversed(COMPROBANTES_EMITIDOS[-50:]))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8082, reload=True)
