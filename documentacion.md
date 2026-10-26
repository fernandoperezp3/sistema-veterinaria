# Manual Técnico y de Usuario - Sistema Veterinario "VetSystem"

## 1. Tecnologías de Desarrollo
El sistema ha sido desarrollado utilizando un stack tecnológico moderno, robusto y escalable, ideal para aplicaciones web empresariales:

*   **Lenguaje de Programación (Backend):** Python 3
*   **Framework Web:** Django (MVT - Model View Template)
*   **Base de Datos:** MySQL / MariaDB
*   **Frontend (Interfaz de Usuario):**
    *   HTML5 / CSS3
    *   Bootstrap 5 (Framework CSS)
    *   JavaScript Vanilla (Para interactividad y librerías)
    *   Chart.js (Para gráficos estadísticos interactivos)
    *   FontAwesome (Iconografía)
*   **Arquitectura:** Monolítica con renderizado del lado del servidor (SSR).

---

## 2. Funcionalidades del Sistema
El sistema VetSystem está compuesto por módulos integrados que cubren todas las necesidades operativas de una clínica veterinaria:

### 2.1. Panel de Control (Dashboard)
*   Visualización en tiempo real de métricas clave (KPIs): Total de mascotas, clientes, citas de hoy e ingresos del día.
*   Gráficos estadísticos dinámicos (Pacientes por especie, Citas por estado, Rendimiento mensual).
*   Tablas resumen interactivas de los próximos eventos.

### 2.2. Gestión de Clientes y Mascotas
*   Registro completo de propietarios (Datos personales, contacto, ubicación).
*   Registro detallado de mascotas asociadas a cada cliente (Nombre, especie, raza, peso, fecha de nacimiento, foto).

### 2.3. Agenda Médica
*   Calendario interactivo para programar, reprogramar y cancelar turnos.
*   Manejo de distintos tipos de citas (Consulta general, vacunación, peluquería, cirugía).
*   Control de estados (Pendiente, Confirmada, Cancelada, Atendida).

### 2.4. Área Clínica (Médico)
*   **Historia Clínica:** Registro evolutivo de cada paciente. Incluye motivo de consulta, examen físico detallado (peso, temperatura, frecuencia cardíaca/respiratoria), diagnóstico y tratamiento.
*   **Vacunaciones:** Control del esquema de vacunación, lote de vacunas y fechas de próximas dosis recomendadas.
*   **Telemedicina:** Plataforma integrada para registrar consultas virtuales a distancia y adjuntar enlaces de videollamada.

### 2.5. Peluquería (Grooming)
*   Gestión de órdenes de servicio estético para mascotas.
*   Control de fecha y hora de inicio/fin del servicio, observaciones y estado del progreso (En curso, Terminado).

### 2.6. Gestión Comercial e Inventario
*   **Inventario:** Catálogo completo de productos, medicamentos y accesorios.
*   Control riguroso de stock (Stock actual vs. Stock mínimo).
*   Kárdex de movimientos: Registro automático de entradas (compras) y salidas (ventas/uso interno).
*   **Facturación:** Emisión de comprobantes de pago detallados, selección de métodos de pago (Efectivo, Tarjeta, Transferencia) y cálculo automático de IGV/IVA.
*   **Control de Caja:** Apertura y cierre diario de caja registradora de la clínica, calculando el dinero inicial, los ingresos del día y el arqueo final.

### 2.7. Reportes y Business Intelligence (BI)
*   Generación de reportes tabulares y gráficos financieros.
*   Filtros dinámicos por rango de fechas para analizar el rendimiento económico mensual o diario de la veterinaria.

### 2.8. Sistema y Seguridad
*   **Configuración Global:** Personalización de los datos de la clínica (Nombre, Logo corporativo, Moneda local, Contacto, Colores de la interfaz).
*   **Usuarios:** Creación de perfiles de acceso (Administradores, Cajeros, Veterinarios).
*   **Mantenimiento:** Herramienta interna para realizar Backups (Copias de seguridad) directos de la base de datos SQL, Restauración de backups y Reseteo del sistema (limpieza de datos transaccionales para iniciar en limpio).

---

## 3. Instalación y Configuración Local
Para ejecutar el sistema en una computadora nueva (con Windows), siga estos pasos:

### Prerrequisitos
1.  Instalar **Python 3.10 o superior** (asegurarse de marcar la casilla "Add Python to PATH" durante la instalación).
2.  Instalar un servidor local de bases de datos como **XAMPP**, **WAMP** o instalar **MySQL Server** de forma independiente.

### Paso a paso
1.  **Preparar la Base de Datos:**
    *   Inicie su servidor MySQL (ej. abrir panel de XAMPP e iniciar "MySQL").
    *   Abra phpMyAdmin o la consola MySQL y cree una base de datos vacía llamada: `sistema_veterinaria_db`.
2.  **Configurar el Proyecto:**
    *   Copie la carpeta del código fuente (`sistema-veterinaria`) en su computadora (ej. en `C:\Webs\Python\sistema-veterinaria`).
    *   Abra la terminal (Símbolo del sistema o PowerShell) y navegue hasta la carpeta del proyecto:
        `cd C:\Webs\Python\sistema-veterinaria`
3.  **Entorno Virtual y Dependencias (Recomendado):**
    *   Cree un entorno virtual (solo la primera vez): `python -m venv venv`
    *   Active el entorno virtual: `venv\Scripts\activate`
    *   Instale las librerías necesarias: `pip install -r requirements.txt` (o instale `django`, `mysqlclient`, etc., si no hay requirements).
4.  **Migrar la Base de Datos:**
    *   Construya las tablas en MySQL ejecutando:
        `python manage.py makemigrations`
        `python manage.py migrate`

---

## 4. Cómo Ejecutar la Aplicación (Modo Desarrollo)
Cada vez que desee encender el sistema para trabajar localmente, siga estos dos sencillos pasos desde el Símbolo del Sistema (CMD) o PowerShell:

1.  Navegue a la carpeta y active el entorno virtual:
    `cd C:\Webs\Python\sistema-veterinaria`
    `venv\Scripts\activate`
2.  Encienda el servidor local de Django:
    `python manage.py runserver`
3.  Abra su navegador web preferido y visite la siguiente dirección:
    **http://127.0.0.1:8080/**

---

## 5. Credenciales de Acceso (Usuario Administrador)
Si es la primera vez que instala el sistema, debe crear un Superusuario maestro.
Con el entorno virtual activado, ejecute:

`python manage.py createsuperuser`

Siga las instrucciones en la pantalla de la consola:
*   **Username (Usuario):** admin
*   **Email:** (puede dejarlo en blanco presionando Enter)
*   **Password (Contraseña):** admin123 *(Nota: al escribir la contraseña en la consola, no se verán los caracteres por seguridad, pero sí se están registrando).*
*   **Password (Confirmación):** admin123

Utilice estas credenciales en la pantalla de inicio de sesión de la aplicación web.

---

## 6. Recomendación de Hosting y Despliegue a Producción

Para llevar esta aplicación a internet para que funcione 24/7, la recomendación ideal, buscando la mejor relación calidad/precio para aplicaciones en Django, es utilizar un plan **VPS (Servidor Privado Virtual)** o un servicio PaaS.

**Las mejores opciones:**
1.  **DigitalOcean (Droplet) / Linode / Vultr** (Recomendado - Mayor control y economía, ~$5 - $10 USD/mes).
2.  **PythonAnywhere** (Excelente para principiantes en Python, muy fácil despliegue, plan básico ~$5 USD/mes).
3.  **Railway.app / Render** (Modernos, sincronización directa con GitHub, cobran por uso).

### Guía Paso a Paso para Despliegue (Ejemplo General para VPS con Ubuntu Server)

Para un VPS (como DigitalOcean), la arquitectura estándar de producción es: **Gunicorn (Servidor de aplicaciones) + Nginx (Proxy Inverso) + MySQL/PostgreSQL**.

**Paso 1: Preparar el Servidor**
1. Acceda a su VPS mediante SSH: `ssh root@ip_del_servidor`
2. Actualice los paquetes del servidor: `apt update && apt upgrade -y`
3. Instale dependencias de sistema: `apt install python3-pip python3-venv nginx mysql-server libmysqlclient-dev -y`

**Paso 2: Configurar la Base de Datos en el Servidor**
1. Entre a MySQL: `mysql -u root`
2. Cree la base de datos y un usuario seguro:
   `CREATE DATABASE sistema_veterinaria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
   `CREATE USER 'vet_user'@'localhost' IDENTIFIED BY 'TuContraSegura123!';`
   `GRANT ALL PRIVILEGES ON sistema_veterinaria_db.* TO 'vet_user'@'localhost';`
   `FLUSH PRIVILEGES; EXIT;`

**Paso 3: Subir el Código y Preparar Entorno**
1. Transfiera los archivos de su proyecto al servidor (usando FTP/FileZilla, SCP, o clonando desde GitHub). Colóquelo en `/var/www/sistema-veterinaria/`
2. Navegue al directorio: `cd /var/www/sistema-veterinaria`
3. Cree y active un entorno virtual: `python3 -m venv venv` y `source venv/bin/activate`
4. Instale las librerías de Python e incluya el servidor de producción: `pip install -r requirements.txt gunicorn`
5. Edite su archivo `settings.py` para producción:
   * Cambie `DEBUG = False`
   * Añada la IP o Dominio del servidor: `ALLOWED_HOSTS = ['midominio.com', 'IP_DEL_SERVIDOR']`
   * Actualice las credenciales en `DATABASES` para que coincidan con el Paso 2.
6. Ejecute migraciones y recolecte archivos estáticos:
   `python manage.py migrate`
   `python manage.py collectstatic`

**Paso 4: Configurar Gunicorn como Servicio del Sistema (Para que nunca se apague)**
1. Cree un archivo de servicio: `nano /etc/systemd/system/gunicorn.service`
2. Pegue esta configuración básica:
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=root
   Group=www-data
   WorkingDirectory=/var/www/sistema-veterinaria
   Environment="PATH=/var/www/sistema-veterinaria/venv/bin"
   ExecStart=/var/www/sistema-veterinaria/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/sistema-veterinaria/sistema_veterinaria.sock veterinaria.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```
3. Inicie el servicio: `systemctl start gunicorn` y `systemctl enable gunicorn`

**Paso 5: Configurar Nginx (Para recibir a los usuarios por el puerto 80)**
1. Cree un archivo de configuración Nginx: `nano /etc/nginx/sites-available/sistema_veterinaria`
2. Agregue el siguiente bloque (cambie su_dominio.com):
   ```nginx
   server {
       listen 80;
       server_name su_dominio.com IP_DEL_SERVIDOR;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /var/www/sistema-veterinaria;
       }
       
       location /media/ {
           root /var/www/sistema-veterinaria;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/sistema-veterinaria/sistema_veterinaria.sock;
       }
   }
   ```
3. Active el sitio: `ln -s /etc/nginx/sites-available/sistema_veterinaria /etc/nginx/sites-enabled`
4. Reinicie Nginx: `systemctl restart nginx`

**Paso final:** Si va a su navegador y digita la IP de su servidor o su dominio, el sistema VetSystem estará disponible públicamente, de manera robusta y segura.

---

## 6. Arquitectura Tecnológica: Monolito Modular con Microservicios Satélite

Para maximizar la escalabilidad, alta disponibilidad y tolerancia a fallos sin perder la agilidad de desarrollo, el sistema **VetSystem** implementa una arquitectura híbrida compuesta por:
*   **Núcleo Central (Core Monolith):** Desarrollado en Python con Django, encargado del renderizado de interfaces (MVT), la lógica de negocio clínica, autenticación, control de accesos y la gestión transaccional principal.
*   **Microservicios Satélite Desacoplados:** Microservicios independientes construidos con **FastAPI** y **WebSockets**, corriendo en puertos dedicados y comunicados vía HTTP/REST y sockets bidireccionales.

### Detalle de los Microservicios Implementados

| Microservicio | Puerto | Stack Tecnológico | Responsabilidad y Endpoints |
| :--- | :---: | :--- | :--- |
| **MS 1: Notificaciones y Recordatorios** | `8081` | FastAPI, Pydantic, Uvicorn | Envío asíncrono de recordatorios de citas y alertas de vacunación por WhatsApp/SMS/Email.<br>• `POST /api/v1/notificaciones/cita`<br>• `POST /api/v1/notificaciones/vacuna` |
| **MS 2: Facturación Electrónica y Pagos** | `8082` | FastAPI, Hashlib SHA-256, UBL 2.1 | Emisión de comprobantes fiscales electrónicos con firma digital, cálculo de código QR tributario y procesamiento de cobros con tarjeta.<br>• `POST /api/v1/facturacion/emitir-comprobante`<br>• `POST /api/v1/pagos/procesar-tarjeta` |
| **MS 3: Telemedicina y Streaming WebRTC** | `8083` | FastAPI, WebSockets, WebRTC P2P | Servidor de señalización y canales WebSocket para consultas virtuales veterinarias y chat en vivo.<br>• `POST /api/v1/telemedicina/crear-sala`<br>• `WSS /ws/sala/{sala_id}`<br>• Interfaz WebRTC: `/sala/{sala_id}` |
| **MS 4: Generación Asíncrona de Reportes y BI** | `8084` | FastAPI, ReportLab, BackgroundTasks | Procesamiento en segundo plano de balances financieros, cálculo de KPIs y exportación a PDF sin saturar el hilo web de Django.<br>• `POST /api/v1/reportes/balance-pdf`<br>• `GET /api/v1/reportes/descargar/{filename}` |

### Tolerancia a Fallos y Alta Disponibilidad
El cliente de integración (`apps/core/services_client.py`) implementa timeouts estrictos y manejo de excepciones resiliente. Si alguno de los microservicios se encuentra apagado o en mantenimiento, el sistema principal de Django **continúa operando con total normalidad**, registrando las citas o comprobantes en la base de datos local y notificando preventivamente al usuario.

---

## 7. Flujo de Comunicación de Punta a Punta (Ciclo de Vida de la Petición)

A continuación se detalla el ciclo completo que sigue una solicitud desde que el usuario digita el dominio en su navegador hasta que visualiza la respuesta en pantalla:

```
[Usuario / Navegador]
       │  (1. Digita https://vetsystem.com)
       ▼
[Cloudflare DNS Anycast] ────► (2. Resuelve IP del Servidor)
       │  (3. TLS 1.3 / HTTP/2 + WAF)
       ▼
[Nginx Reverse Proxy :80/:443] ───► (4. Sirve /static/ y /media/ directamente)
       │  (5. Proxy Pass WSGI / Socket UNIX)
       ▼
[Gunicorn Application Server] ───► (6. Prefork Workers de Python)
       │
       ▼
[Django Core (settings / urls.py)]
       ├── (7. Pipeline de Middlewares: Security, CSRF, Session, Auth)
       ├── (8. Router de URLs hacia la Vista del Módulo: agenda, medico, etc.)
       │
       ├──► [MySQL 8.0 / MariaDB] ──── (9. Consultas ACID vía Django ORM)
       ├──► [Redis 7 Cache / Broker] ─ (10. Caché de sesión y cola de mensajes)
       │
       └──► [Microservicios Satélite :8081 - :8084]
                  ├── MS 1 (8081): Despacho de WhatsApp al crear cita o vacuna
                  ├── MS 2 (8082): Timbrado fiscal SHA-256 de factura
                  ├── MS 3 (8083): Creación de sala WebRTC para teleconsulta
                  └── MS 4 (8084): Tarea en segundo plano para PDF de balance
       │
       ▼
[Motor MVT (Renderizado HTML Server-Side)]
       │  (11. HTTP Response 200 viaja de regreso: Django ➔ Gunicorn ➔ Nginx ➔ Navegador)
       ▼
[Navegador del Usuario]
       │  (12. Pintado final del DOM, CSS Bootstrap 5 y gráficos Chart.js)
```

### Paso a Paso Detallado:
1. **Petición Inicial:** El usuario abre el navegador web e ingresa `https://vetsystem.com/agenda/`.
2. **Resolución de Nombres DNS:** Los servidores Anycast de Cloudflare traducen el nombre de dominio a la dirección IP pública de nuestro servidor.
3. **Capa Edge y Seguridad:** Cloudflare verifica las reglas del WAF (filtrado anti-DDoS), negocia el certificado SSL/TLS y transmite el tráfico cifrado al servidor VPS.
4. **Proxy Inverso Nginx:** Nginx recibe la conexión por el puerto 443. Si la petición corresponde a activos estáticos (`/static/` o `/media/`), Nginx los entrega directamente desde disco con compresión Gzip sin sobrecargar Python. Si es una petición dinámica, la redirige a Gunicorn.
5. **Servidor de Aplicación Gunicorn:** Gunicorn administra un pool de trabajadores (workers) en Python, recibiendo la solicitud a través de un socket UNIX o TCP local.
6. **Pipeline de Middlewares en Django:** La petición atraviesa capas automáticas de seguridad: validación HTTPS, verificación de tokens CSRF, lectura de cookies de sesión y autenticación del usuario actual.
7. **Enrutamiento:** `veterinaria/urls.py` analiza la ruta y delega el control a la función de vista correspondiente (ej: `agenda_lista` o `cita_crear`).
8. **Capa de Datos (ORM y MySQL):** La vista ejecuta consultas optimizadas mediante el ORM de Django hacia MySQL (`sistema_veterinaria_db`), recuperando pacientes, turnos e historiales clínicos.
9. **Despacho a Microservicios:** Si la acción del usuario dispara un evento desacoplado (como agendar una cita o emitir una boleta), el cliente `MicroservicesClient` realiza una llamada REST asíncrona hacia el microservicio correspondiente (puertos 8081, 8082, 8083 o 8084).
10. **Renderizado del Template:** Django combina los datos del modelo con las plantillas HTML (`templates/agenda/lista.html`), ensamblando el documento final.
11. **Retorno de la Respuesta HTTP:** La respuesta viaja de vuelta: Django $\rightarrow$ Gunicorn $\rightarrow$ Nginx $\rightarrow$ Cloudflare $\rightarrow$ Navegador del cliente.
12. **Pintado en el Cliente:** El navegador interpreta el HTML, aplica las hojas de estilo de Bootstrap 5 y ejecuta los scripts de Chart.js para dibujar los gráficos interactivos del panel.

---

## 8. Entregables de la Tarea Académica

En la carpeta raíz del proyecto y en el módulo web `/microservicios/` se encuentran disponibles los archivos oficiales listos para su entrega y presentación:

1. **`arquitectura_vetsystem.png`:** Diagrama arquitectónico en Ultra Alta Definición (300 DPI, 2700 x 1720 px), con diseño corporativo, 5 capas tecnológicas identificadas y el flujo enumerado de 12 pasos.
2. **`arquitectura_vetsystem.pdf`:** Documento vectorial en formato apaisado (Landscape A3) generado con ReportLab, ideal para impresión o adjuntar en plataformas académicas (Moodle, Canvas, Teams).
3. **`arquitectura_vetsystem.drawio`:** Archivo nativo en formato XML para abrir, editar y personalizar directamente en [Draw.io / diagrams.net](https://app.diagrams.net).
4. **`arquitectura_vetsystem.html`:** Dashboard web interactivo con visualizador del diagrama y botones directos de descarga.
5. **`iniciar_sistema_completo.bat`:** Script de encendido automático con un clic para levantar simultáneamente los 4 microservicios y el servidor web Django.

