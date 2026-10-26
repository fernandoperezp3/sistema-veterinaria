"""
Configuración de Producción Servidor WSGI Gunicorn 21
Sistema Veterinario "VetSystem"
"""

import multiprocessing
import os

# Dirección de enlace
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8080")

# Concurrencia de Workers (Fórmula estándar: (2 * CPUs) + 1)
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000

# Timeouts
timeout = 120
keepalive = 5

# Logs
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Rendimiento y reciclaje de memoria
max_requests = 1000
max_requests_jitter = 50
