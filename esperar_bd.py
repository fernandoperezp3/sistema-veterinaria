import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "veterinaria.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import veterinaria
import MySQLdb

host = os.environ.get("DB_HOST", "127.0.0.1")
if host == "localhost":
    host = "127.0.0.1"
port = int(os.environ.get("DB_PORT", "3306"))
user = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASSWORD", "")
name = os.environ.get("DB_NAME", "sistema_veterinaria_db")
limite = int(sys.argv[1]) if len(sys.argv) > 1 else 60

inicio = time.time()
ultimo_error = None
while time.time() - inicio < limite:
    try:
        conexion = MySQLdb.connect(host=host, port=port, user=user, passwd=password, connect_timeout=3)
        cursor = conexion.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("SELECT VERSION()")
        print(f"   MySQL listo ({cursor.fetchone()[0]}) en {host}:{port}")
        conexion.close()
        sys.exit(0)
    except Exception as e:
        ultimo_error = e
        time.sleep(2)

print(f"   MySQL no responde en {host}:{port} despues de {limite}s: {ultimo_error}")
sys.exit(1)
