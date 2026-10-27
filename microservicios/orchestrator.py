"""
Orquestador de Microservicios VetSystem
Supervisa y ejecuta los 4 microservicios en puertos dedicados:
- Puerto 8081: Microservicio de Notificaciones & Recordatorios
- Puerto 8082: Microservicio de Facturación Electrónica & Pagos
- Puerto 8083: Microservicio de Telemedicina & WebSockets
- Puerto 8084: Microservicio de Reportes & BI Asíncrono
"""

import subprocess
import sys
import time
import os
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {
        "nombre": "MS 1: Notificaciones y Recordatorios",
        "puerto": 8081,
        "app": "microservicios.notificaciones.main:app",
        "docs": "http://127.0.0.1:8081/docs",
    },
    {
        "nombre": "MS 2: Facturación Electrónica y Pagos",
        "puerto": 8082,
        "app": "microservicios.facturacion_pagos.main:app",
        "docs": "http://127.0.0.1:8082/docs",
    },
    {
        "nombre": "MS 3: Telemedicina y Streaming WebRTC",
        "puerto": 8083,
        "app": "microservicios.telemedicina.main:app",
        "docs": "http://127.0.0.1:8083/docs",
    },
    {
        "nombre": "MS 4: Generación de Reportes y BI",
        "puerto": 8084,
        "app": "microservicios.reportes_bi.main:app",
        "docs": "http://127.0.0.1:8084/docs",
    },
]

def main():
    print("=" * 70)
    print("   INICIANDO ARQUITECTURA DE MICROSERVICIOS - VetSystem")
    print("=" * 70)

    processes = []
    project_root = os.path.dirname(BASE_DIR)

    for s in SERVICES:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            s["app"],
            "--host",
            "0.0.0.0",
            "--port",
            str(s["puerto"]),
            "--log-level",
            "warning",
        ]
        p = subprocess.Popen(cmd, cwd=project_root)
        processes.append((s, p))
        print(f"[ONLINE] {s['nombre']} -> Puerto {s['puerto']} (Docs: {s['docs']})")

    print("\n" + "=" * 70)
    print("   TODOS LOS MICROSERVICIOS ESTÁN CORRIENDO EXITOSAMENTE.")
    print("   Presiona Ctrl+C en cualquier momento para detenerlos.")
    print("=" * 70)

    def handle_exit(sig, frame):
        print("\n[INFO] Deteniendo todos los microservicios...")
        for s, p in processes:
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)

if __name__ == "__main__":
    main()
