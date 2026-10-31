# VetSystem — Sistema Veterinario

Django 6 + MySQL + 4 microservicios FastAPI (8081–8084).

## Requisitos

- Python 3.12 o superior (marcar "Add Python to PATH")
- MySQL o MariaDB (XAMPP sirve) en `localhost:3306`, usuario `root` sin contraseña
- Base de datos creada: `sistema_veterinaria_db` (utf8mb4)

## Instalación (una sola vez)

1. Encender MySQL.
2. Ejecutar `scripts\instalar.bat` (crea `venv`, instala dependencias y aplica migraciones).
3. Crear el administrador:
   ```
   venv\Scripts\python manage.py createsuperuser
   ```
4. Opcional, cargar datos de demostración:
   ```
   venv\Scripts\python poblar_datos.py
   ```

## Ejecutar

- `scripts\iniciar_sistema_completo.bat` → microservicios + Django y abre http://127.0.0.1:8080
- Desde VS Code: panel *Run and Debug* → **Sistema completo (Django + Microservicios)**

## VS Code

Ejecutar una vez `scripts\configurar_vscode.bat` (copia `vscode_config\*.json` a `.vscode`).
Luego abrir la carpeta en VS Code: el intérprete queda en `venv\Scripts\python.exe`
(si no, `Ctrl+Shift+P` → *Python: Select Interpreter* → `venv`).

## Variables de entorno (opcionales)

| Variable | Valor por defecto |
|---|---|
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | `sistema_veterinaria_db` / `root` / vacío / `localhost` / `3306` |
| `DB_ENGINE=sqlite` | Usa SQLite en lugar de MySQL (pruebas rápidas) |
| `DJANGO_DEBUG` | `True` |
| `DJANGO_SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | valores del proyecto |

## Moneda e impuesto

Se configuran en **Configuración** (solo administradores): símbolo de moneda,
nombre del impuesto (IGV / IVA) y porcentaje. Las facturas usan esos valores.

## Docker

```
docker compose up --build
```
App en http://localhost (Nginx) o http://localhost:8080. MySQL del contenedor queda en el puerto 3306 del host.
