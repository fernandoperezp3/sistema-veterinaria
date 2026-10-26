"""
Generador Maestro de Arquitectura Tecnológica para Sistema Veterinario "VetSystem"
Genera:
1. arquitectura_vetsystem.png (Imagen PNG ultra HD 300 DPI con conectores y flujo gráfico)
2. arquitectura_vetsystem.pdf (Documento PDF vectorial de alta calidad)
3. arquitectura_vetsystem.drawio (Archivo nativo XML para abrir en Draw.io / diagrams.net)
4. arquitectura_vetsystem.html (Vista web interactiva con panel y botones de exportación)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import xml.etree.ElementTree as ET

# -------------------------------------------------------------------------
# 1. GENERACIÓN DE IMAGEN PNG DE ALTA RESOLUCIÓN CON PILLOW
# -------------------------------------------------------------------------
def create_png_diagram(output_path="arquitectura_vetsystem.png"):
    W, H = 2700, 1720
    img = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)

    # Cargar Fuentes del sistema
    font_bold_path = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg_path = "C:/Windows/Fonts/segoeui.ttf"
    font_semi_path = "C:/Windows/Fonts/seguisb.ttf"

    f_title = ImageFont.truetype(font_bold_path, 34)
    f_subtitle = ImageFont.truetype(font_reg_path, 19)
    f_badge = ImageFont.truetype(font_bold_path, 15)
    f_header = ImageFont.truetype(font_bold_path, 19)
    f_card_title = ImageFont.truetype(font_bold_path, 17)
    f_card_sub = ImageFont.truetype(font_semi_path, 13)
    f_body = ImageFont.truetype(font_reg_path, 12.5)
    f_connector = ImageFont.truetype(font_bold_path, 11)
    f_step_num = ImageFont.truetype(font_bold_path, 14)
    f_step_title = ImageFont.truetype(font_bold_path, 14)
    f_step_text = ImageFont.truetype(font_reg_path, 12.5)

    # Header Superior
    draw.rectangle([(0, 0), (W, 110)], fill=(15, 23, 42, 255)) # Dark Slate
    draw.text((60, 22), "ARQUITECTURA TECNOLÓGICA Y FLUJO DE COMUNICACIÓN", font=f_title, fill=(255, 255, 255, 255))
    draw.text((60, 68), "SISTEMA DE GESTIÓN VETERINARIA 'VetSystem'  |  ARQUITECTURA: MONOLITO MODULAR DJANGO + MICROSERVICIOS SATÉLITE", font=f_subtitle, fill=(148, 163, 184, 255))
    
    # Metadata Badge
    draw.rounded_rectangle([(W - 520, 28), (W - 60, 82)], radius=8, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=2)
    draw.text((W - 500, 42), "Stack: Python 3.12 / Django 6 / MySQL / Nginx / Redis / Celery", font=f_badge, fill=(56, 189, 248, 255))

    # Definir Columnas
    cols = [
        {"x1": 50,   "x2": 420,  "title": "1. CAPA CLIENTE / FRONTEND", "color": (59, 130, 246), "bg": (239, 246, 255)},
        {"x1": 500,  "x2": 920,  "title": "2. CAPA RED, EDGE Y PROXY",  "color": (16, 185, 129), "bg": (236, 253, 245)},
        {"x1": 1000, "x2": 1580, "title": "3. CORE BACKEND (DJANGO)",   "color": (99, 102, 241), "bg": (238, 242, 255)},
        {"x1": 1660, "x2": 2100, "title": "4. MICROSERVICIOS PROPUESTOS","color": (217, 70, 239), "bg": (253, 244, 255)},
        {"x1": 2180, "x2": 2650, "title": "5. PERSISTENCIA Y DATOS",    "color": (245, 158, 11), "bg": (254, 243, 199)},
    ]

    top_y = 140
    bottom_y = 1210

    for col in cols:
        draw.rounded_rectangle([(col["x1"], top_y), (col["x2"], bottom_y)], radius=16, fill=col["bg"], outline=col["color"], width=2)
        draw.rounded_rectangle([(col["x1"], top_y), (col["x2"], top_y + 44)], radius=14, fill=col["color"])
        draw.text((col["x1"] + 20, top_y + 11), col["title"], font=f_header, fill=(255, 255, 255, 255))

    # Helper para dibujar tarjetas internas
    def draw_card(x1, y1, x2, y2, title, subtitle, items, border_color, badge=""):
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=12, fill=(255, 255, 255, 255), outline=border_color, width=2)
        draw.rounded_rectangle([(x1, y1), (x2, y1 + 34)], radius=10, fill=(241, 245, 249, 255))
        draw.text((x1 + 16, y1 + 7), title, font=f_card_title, fill=(15, 23, 42, 255))
        if badge:
            bx2 = x2 - 12
            bx1 = bx2 - 90
            draw.rounded_rectangle([(bx1, y1 + 5), (bx2, y1 + 29)], radius=6, fill=border_color)
            draw.text((bx1 + 10, y1 + 8), badge, font=f_card_sub, fill=(255, 255, 255, 255))
        
        if subtitle:
            draw.text((x1 + 16, y1 + 42), subtitle, font=f_card_sub, fill=(71, 85, 105, 255))
        
        curr_y = y1 + (64 if subtitle else 44)
        for it in items:
            draw.ellipse([(x1 + 16, curr_y + 5), (x1 + 22, curr_y + 11)], fill=border_color)
            draw.text((x1 + 28, curr_y), it, font=f_body, fill=(51, 65, 85, 255))
            curr_y += 24

    # ------------------ COLUMNA 1: FRONTEND ------------------
    draw_card(70, 205, 400, 480, 
              "Navegador Web (Cliente)", 
              "Dispositivos: PC Clínica / Tablet / Móvil", 
              [
                  "Usuario teclea: https://vetsystem.com",
                  "Roles: Veterinario, Recepción, Admin, Dueño",
                  "Interfaz SPA / SSR Híbrida",
                  "Formularios de citas, historias y pagos",
                  "Consumo de APIs REST (Fetch/AJAX)"
              ], 
              (59, 130, 246), "Browser")

    draw_card(70, 510, 400, 800, 
              "Tecnologías de UI / Cliente", 
              "Stack Frontend Integrado", 
              [
                  "HTML5 Semántico + CSS3",
                  "Bootstrap 5 (Framework CSS Responsivo)",
                  "JavaScript Vanilla (Interacciones DOM)",
                  "Chart.js (Métricas clínicas y KPIs)",
                  "FontAwesome 6 (Iconografía médica)",
                  "SweetAlert2 (Alertas y confirmaciones)"
              ], 
              (37, 99, 235), "UI Tech")

    draw_card(70, 830, 400, 1170, 
              "Acciones del Usuario", 
              "Operaciones en la Clínica", 
              [
                  "Programar / Atender Cita (Agenda)",
                  "Registrar Historia Clínica y Vacunas",
                  "Control de Inventario y Medicamentos",
                  "Cobro de Facturas y Cierre de Caja",
                  "Videollamadas de Telemedicina",
                  "Exportar Reportes a PDF / Excel"
              ], 
              (30, 64, 175), "Módulos")

    # ------------------ COLUMNA 2: RED / EDGE / PROXY ------------------
    draw_card(520, 205, 900, 430, 
              "DNS & Edge CDN", 
              "Proveedor: Cloudflare / Route 53", 
              [
                  "Resolución de Dominio: IP Pública Anycast",
                  "Certificado SSL/TLS (HTTPS Puerto 443)",
                  "Mitigación de Ataques DDoS y Web Firewall",
                  "Caché estático perimetral (CDN Edge)"
              ], 
              (16, 185, 129), "DNS / SSL")

    draw_card(520, 460, 900, 830, 
              "Servidor Web Nginx 1.24", 
              "Proxy Inverso & Gateway", 
              [
                  "Terminación TLS / SSL (Let's Encrypt)",
                  "Enrutador de Tráfico y Balanceador:",
                  "  • /static/ -> Disco Nginx (CSS/JS)",
                  "  • /media/ -> Disco Nginx (Fotos/PDFs)",
                  "  • /api/v1/... -> Microservicios",
                  "  • /ws/... -> WebSockets Telemedicina",
                  "  • Demás rutas -> Core Django (Gunicorn)",
                  "Compresión Gzip / Brotli y HTTP/2"
              ], 
              (5, 150, 105), "Nginx")

    draw_card(520, 860, 900, 1170, 
              "Seguridad Perimetral", 
              "Políticas de Protección", 
              [
                  "Protección contra ataques CSRF / XSS",
                  "Cabeceras de Seguridad: HSTS, CSP, X-Frame",
                  "Rate Limiting (Control de tasa de peticiones)",
                  "Logs de Acceso e IPs en tiempo real"
              ], 
              (4, 120, 87), "WAF")

    # ------------------ COLUMNA 3: CORE BACKEND (DJANGO) ------------------
    draw_card(1020, 205, 1560, 420, 
              "Servidor WSGI (Gunicorn 21.x)", 
              "Python Application Server", 
              [
                  "Administrador de procesos concurrentes (Workers)",
                  "Protocolo WSGI (Web Server Gateway Interface)",
                  "Manejo de hilos asíncronos y timeouts",
                  "Socket UNIX / TCP local (127.0.0.1:8080)"
              ], 
              (99, 102, 241), "WSGI")

    draw_card(1020, 450, 1560, 860, 
              "Framework Web Django 6.0", 
              "Núcleo de Negocio (Monolito Modular)", 
              [
                  "Middlewares: Security, Session, CSRF, Auth",
                  "Enrutador de URLs (veterinaria/urls.py)",
                  "Módulos Activos (Apps):",
                  "  • agenda: Citas médicas y peluquería",
                  "  • clientes: Propietarios y expedientes",
                  "  • medico: Historias, consultas y vacunas",
                  "  • inventario: Medicinas, stock y kárdex",
                  "  • facturacion: Comprobantes y caja diaria",
                  "  • grooming: Órdenes estéticas",
                  "  • usuarios: Roles (Veterinario/Admin/Cajero)",
                  "Motor de Plantillas MVT + API JSON"
              ], 
              (79, 70, 229), "Django")

    draw_card(1020, 890, 1560, 1170, 
              "Capa ORM & Tareas Internas", 
              "Django ORM / QuerySet API", 
              [
                  "Mapeo Objeto-Relacional (Modelos Django)",
                  "Transacciones Atómicas (ACID Compliant)",
                  "Pool de conexiones y optimización QuerySet",
                  "Emisor de eventos hacia Redis (Celery Client)"
              ], 
              (67, 56, 202), "ORM")

    # ------------------ COLUMNA 4: MICROSERVICIOS PROPUESTOS ------------------
    draw_card(1680, 205, 2080, 420, 
              "MS 1: Notificaciones", 
              "Python (FastAPI) + Twilio / WhatsApp", 
              [
                  "Recordatorios automáticos de citas",
                  "Alertas de vacunas próximas a vencer",
                  "Envío de correos (SendGrid / SMTP)",
                  "Consumo asíncrono desde colas Redis"
              ], 
              (217, 70, 239), "MS 1")

    draw_card(1680, 450, 2080, 670, 
              "MS 2: Facturación & Pagos", 
              "Node.js / FastAPI + Stripe API", 
              [
                  "Emisión de Comprobantes Fiscales (SAT/SUNAT)",
                  "Firma digital de XML y QR tributario",
                  "Pasarela de cobro con tarjeta de crédito",
                  "Webhooks de confirmación de pago"
              ], 
              (192, 38, 211), "MS 2")

    draw_card(1680, 700, 2080, 920, 
              "MS 3: Telemedicina & Video", 
              "Node.js + Socket.IO + WebRTC", 
              [
                  "Salas de videollamada para consultas remotas",
                  "Chat en tiempo real veterinario - dueño",
                  "Señalización WebRTC (Peer-to-Peer)",
                  "Cifrado E2E de audio y video"
              ], 
              (162, 28, 175), "MS 3")

    draw_card(1680, 950, 2080, 1170, 
              "MS 4: Reportes & BI", 
              "Celery Worker + ReportLab", 
              [
                  "Generación pesada de balances en PDF",
                  "Exportación de Kárdex e Inventario a Excel",
                  "Cálculo de KPIs financieros mensuales",
                  "Procesamiento asíncrono sin bloquear la web"
              ], 
              (134, 25, 143), "MS 4")

    # ------------------ COLUMNA 5: PERSISTENCIA Y DATOS ------------------
    draw_card(2200, 205, 2630, 520, 
              "Base de Datos Relacional", 
              "MySQL 8.0 / MariaDB 10.x", 
              [
                  "Esquema: sistema_veterinaria_db",
                  "Tablas maestras y transaccionales:",
                  "  • Clientes, Mascotas, Citas",
                  "  • Historias Clínicas, Vacunas",
                  "  • Medicamentos, Movimientos Kárdex",
                  "  • Facturas, Detalles, Caja Chica",
                  "Integridad Referencial e Índices B-Tree"
              ], 
              (245, 158, 11), "MySQL")

    draw_card(2200, 550, 2630, 850, 
              "Caché & Message Broker", 
              "Redis 7.x (En Memoria)", 
              [
                  "Caché de sesiones de usuarios activos",
                  "Caché de consultas pesadas de Dashboard",
                  "Colas de mensajería (Message Broker):",
                  "  • Cola tareas Celery",
                  "  • Cola de notificaciones WhatsApp",
                  "Pub/Sub para eventos en tiempo real"
              ], 
              (217, 119, 6), "Redis")

    draw_card(2200, 880, 2630, 1170, 
              "Almacenamiento de Archivos", 
              "Local Media / Object Storage S3", 
              [
                  "Carpeta /media/:",
                  "  • Fotos de mascotas y expedientes",
                  "  • Logotipo de la veterinaria",
                  "  • Recetas médicas y consentimientos",
                  "Carpeta /backups/:",
                  "  • Respaldos SQL automatizados (.sql)"
              ], 
              (180, 83, 9), "Storage")

    # -------------------------------------------------------------------------
    # DIBUJAR FLECHAS Y CONECTORES DE FLUJO EN LOS ESPACIOS ENTRE COLUMNAS
    # -------------------------------------------------------------------------
    def draw_flow_arrow(x1, y1, x2, y2, label, color, dashed=False, label_below=False):
        if dashed:
            dist = math.hypot(x2 - x1, y2 - y1)
            steps = int(dist / 10)
            for s in range(0, steps, 2):
                sx = x1 + (x2 - x1) * (s / steps)
                sy = y1 + (y2 - y1) * (s / steps)
                ex = x1 + (x2 - x1) * ((s + 1) / steps)
                ey = y1 + (y2 - y1) * ((s + 1) / steps)
                draw.line([(sx, sy), (ex, ey)], fill=color, width=3)
        else:
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)

        angle = math.atan2(y2 - y1, x2 - x1)
        arr_len = 12
        p1 = (x2 - arr_len * math.cos(angle - math.pi / 6), y2 - arr_len * math.sin(angle - math.pi / 6))
        p2 = (x2 - arr_len * math.cos(angle + math.pi / 6), y2 - arr_len * math.sin(angle + math.pi / 6))
        draw.polygon([(x2, y2), p1, p2], fill=color)

        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            bbox = draw.textbbox((0, 0), label, font=f_connector)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            ly = my + 10 if label_below else my - th - 12
            draw.rounded_rectangle([(mx - tw/2 - 6, ly - 3), (mx + tw/2 + 6, ly + th + 4)], radius=4, fill=(255, 255, 255, 240), outline=color, width=1)
            draw.text((mx - tw/2, ly), label, font=f_connector, fill=color)

    # 1. Entre Cliente y Red
    draw_flow_arrow(420, 280, 500, 280, "(1) HTTPS :443", (37, 99, 235))
    draw_flow_arrow(500, 680, 420, 680, "(11) HTTP 200", (16, 185, 129), dashed=True, label_below=True)

    # 2. Entre Red y Django Core
    draw_flow_arrow(920, 310, 1000, 310, "(4) proxy_pass", (99, 102, 241))
    draw_flow_arrow(920, 630, 1000, 630, "(5) WSGI Request", (79, 70, 229))

    # 3. Entre Django Core y Microservicios
    draw_flow_arrow(1580, 310, 1660, 310, "(9) Async Tasks", (217, 70, 239))
    draw_flow_arrow(1580, 560, 1660, 560, "Webhooks / Pay", (192, 38, 211))
    draw_flow_arrow(1580, 1060, 1660, 1060, "PDF / Excel Queue", (134, 25, 143))

    # 4. Entre Microservicios / Django y Persistencia
    draw_flow_arrow(2100, 360, 2180, 360, "(8) SQL Query", (245, 158, 11))
    draw_flow_arrow(2100, 680, 2180, 680, "Broker / Cache", (217, 119, 6))

    # -------------------------------------------------------------------------
    # 2. SECCIÓN INFERIOR: FLUJO DE COMUNICACIÓN PASO A PASO (E2E)
    # -------------------------------------------------------------------------
    flow_y1 = 1240
    flow_y2 = 1660
    draw.rounded_rectangle([(50, flow_y1), (W - 50, flow_y2)], radius=16, fill=(241, 245, 249, 255), outline=(100, 116, 139, 255), width=2)
    draw.rounded_rectangle([(50, flow_y1), (W - 50, flow_y1 + 44)], radius=14, fill=(30, 41, 59, 255))
    draw.text((70, flow_y1 + 11), "FLUJO DE COMUNICACIÓN PASO A PASO (CICLO DE VIDA DE LA PETICIÓN DESDE QUE EL USUARIO ESCRIBE EL DOMINIO)", font=f_header, fill=(255, 255, 255, 255))

    steps = [
        ("1", "Solicitud Inicial", "Usuario teclea https://vetsystem.clinica.com en el navegador."),
        ("2", "Resolución DNS", "DNS Cloudflare traduce el nombre de dominio a la IP pública."),
        ("3", "Handshake HTTPS", "Conexión segura TLS 1.3 con Nginx en puerto 443. Valida certificado SSL."),
        ("4", "Inspección Nginx", "Nginx sirve estáticos directos (/static/, /media/) o reenvía a Gunicorn."),
        ("5", "Traspaso WSGI", "Gunicorn recibe la solicitud HTTP y la transforma en objeto WSGI para Django."),
        ("6", "Filtro Middlewares", "Django valida seguridad: sesión de usuario, permisos RBAC y token CSRF."),
        ("7", "Enrutador URLs", "urls.py inspecciona la ruta y despacha al módulo (ej. apps.medico)."),
        ("8", "Consulta ORM / BD", "La vista consulta o guarda datos mediante Django ORM en MySQL y Redis."),
        ("9", "Microservicios", "Si la acción requiere tareas pesadas (WhatsApp o PDF), delega vía Redis Broker."),
        ("10", "Renderizado MVT", "Django ensambla el HTML con los datos usando plantillas o devuelve JSON API."),
        ("11", "Retorno de Respuesta", "HTTP 200 viaja en reversa: Django hacia Gunicorn, Nginx y al Navegador."),
        ("12", "Pintado en Cliente", "Navegador parsea el DOM con Bootstrap 5 y dibuja gráficos Chart.js.")
    ]

    # Cuadrícula 4 columnas x 3 filas
    step_w = 600
    step_h = 100
    start_sx = 75
    start_sy = flow_y1 + 60

    for idx, (num, stitle, sdesc) in enumerate(steps):
        col_idx = idx % 4
        row_idx = idx // 4
        sx = start_sx + col_idx * 635
        sy = start_sy + row_idx * 115

        # Tarjeta del paso
        draw.rounded_rectangle([(sx, sy), (sx + step_w, sy + step_h)], radius=8, fill=(255, 255, 255, 255), outline=(203, 213, 225, 255), width=1)
        # Círculo número
        draw.ellipse([(sx + 14, sy + 16), (sx + 48, sy + 50)], fill=(37, 99, 235, 255))
        draw.text((sx + (25 if len(num)==1 else 20), sy + 22), num, font=f_step_num, fill=(255, 255, 255, 255))
        
        # Título
        draw.text((sx + 62, sy + 14), stitle, font=f_step_title, fill=(15, 23, 42, 255))
        
        # Descripción
        words = sdesc.split(" ")
        line1, line2 = "", ""
        for w in words:
            if len(line1) + len(w) < 58:
                line1 += w + " "
            else:
                line2 += w + " "
        draw.text((sx + 62, sy + 42), line1.strip(), font=f_step_text, fill=(71, 85, 105, 255))
        if line2:
            draw.text((sx + 62, sy + 65), line2.strip(), font=f_step_text, fill=(100, 116, 139, 255))

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"[OK] Diagrama PNG generado: {output_path}")


# -------------------------------------------------------------------------
# 2. GENERACIÓN DE DOCUMENTO PDF VECTORIAL CON REPORTLAB
# -------------------------------------------------------------------------
def create_pdf_diagram(output_path="arquitectura_vetsystem.pdf", png_source="arquitectura_vetsystem.png"):
    c = canvas.Canvas(output_path, pagesize=landscape(A3))
    page_w, page_h = landscape(A3)

    margin = 14
    render_w = page_w - (margin * 2)
    render_h = page_h - (margin * 2)
    
    c.drawImage(png_source, margin, margin, width=render_w, height=render_h)
    c.showPage()
    c.save()
    print(f"[OK] Diagrama PDF generado: {output_path}")


# -------------------------------------------------------------------------
# 3. GENERACIÓN DEL ARCHIVO NATIVO DRAW.IO (.drawio XML)
# -------------------------------------------------------------------------
def create_drawio_file(output_path="arquitectura_vetsystem.drawio"):
    root = ET.Element("mxfile", host="app.diagrams.net", modified="2026-10-15T00:00:00.000Z", agent="VetSystem Architecture Generator", version="21.0.0", type="device")
    diagram = ET.SubElement(root, "diagram", id="vetsystem-arch-full", name="Arquitectura VetSystem")
    model = ET.SubElement(diagram, "mxGraphModel", dx="1920", dy="1080", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1920", pageHeight="1080", background="#F8FAFC")
    root_cell = ET.SubElement(model, "root")

    ET.SubElement(root_cell, "mxCell", id="0")
    ET.SubElement(root_cell, "mxCell", id="1", parent="0")

    def add_node(cid, val, style, x, y, w, h, parent="1"):
        cell = ET.SubElement(root_cell, "mxCell", id=cid, value=val, style=style, vertex="1", parent=parent)
        geo = ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h))
        geo.set("as", "geometry")
        return cell

    def add_edge(eid, val, style, source, target):
        cell = ET.SubElement(root_cell, "mxCell", id=eid, value=val, style=style, edge="1", parent="1", source=source, target=target)
        geo = ET.SubElement(cell, "mxGeometry", relative="1")
        geo.set("as", "geometry")
        return cell

    # Título Principal
    add_node("title", "<b>ARQUITECTURA TECNOLÓGICA WEB - SISTEMA VETERINARIO &quot;VetSystem&quot;</b><br/><font style='font-size: 13px; font-weight: normal; color: #94A3B8;'>Monolito Modular Django 6 + Microservicios Satélite + Nginx + MySQL + Redis (12 Pasos E2E)</font>", 
             "text;html=1;strokeColor=none;fillColor=#0F172A;align=left;verticalAlign=middle;spacingLeft=30;rounded=1;fontColor=#FFFFFF;fontSize=18;fontFamily=Segoe UI;", 
             40, 20, 1840, 65)

    # 5 Columnas
    swimlanes = [
        ("c1", "<b>1. CAPA CLIENTE / FRONTEND</b>", "#EFF6FF", "#3B82F6", 40, 105, 330, 680),
        ("c2", "<b>2. CAPA RED &amp; PROXY (EDGE)</b>", "#ECFDF5", "#10B981", 400, 105, 330, 680),
        ("c3", "<b>3. CORE BACKEND (DJANGO)</b>", "#EEF2FF", "#6366F1", 760, 105, 420, 680),
        ("c4", "<b>4. MICROSERVICIOS PROPUESTOS</b>", "#FDF4FF", "#D946EF", 1210, 105, 330, 680),
        ("c5", "<b>5. PERSISTENCIA Y DATOS</b>", "#FEF3C7", "#F59E0B", 1570, 105, 310, 680),
    ]

    for cid, name, fill, stroke, x, y, w, h in swimlanes:
        add_node(cid, name, f"swimlane;startSize=40;rounded=1;arcSize=8;fillColor={fill};strokeColor={stroke};strokeWidth=2;fontFamily=Segoe UI;fontSize=13;fontColor=#0F172A;align=center;", x, y, w, h)

    # Nodos
    add_node("n_browser", "<b>Navegador Web (Cliente)</b><br/><font style='font-size:11px;color:#475569;'>• Chrome / Edge / Mobile<br/>• Petición HTTPS: vetsystem.com<br/>• Roles: Veterinario, Recepción, Admin</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#3B82F6;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             60, 160, 290, 100)

    add_node("n_ui_tech", "<b>Tecnologías Frontend</b><br/><font style='font-size:11px;color:#475569;'>• HTML5 Semántico + CSS3<br/>• Bootstrap 5 (Responsive UI)<br/>• JavaScript Vanilla (Fetch API)<br/>• Chart.js (KPIs Clínicos)<br/>• FontAwesome 6</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#2563EB;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             60, 280, 290, 120)

    add_node("n_ui_mod", "<b>Módulos de Usuario</b><br/><font style='font-size:11px;color:#475569;'>• Agenda de Citas y Turnos<br/>• Historias Clínicas y Vacunas<br/>• Inventario y Medicamentos<br/>• Facturación y Cierre de Caja<br/>• Telemedicina en Vivo</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1D4ED8;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             60, 420, 290, 130)

    add_node("n_dns", "<b>DNS &amp; CDN (Cloudflare)</b><br/><font style='font-size:11px;color:#475569;'>• Resolución de dominio a IP Pública<br/>• Terminación SSL/TLS (HTTPS)<br/>• Mitigación DDoS / WAF</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#10B981;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             420, 160, 290, 100)

    add_node("n_nginx", "<b>Servidor Web Nginx 1.24</b><br/><font style='font-size:11px;color:#475569;'>• Proxy Inverso &amp; Gateway<br/>• Sirve /static/ y /media/ directos<br/>• proxy_pass a Gunicorn (WSGI)<br/>• Redirección a Microservicios<br/>• WebSockets Proxy (/ws/)</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             420, 280, 290, 140)

    add_node("n_waf", "<b>Seguridad Perimetral</b><br/><font style='font-size:11px;color:#475569;'>• Protección CSRF, XSS, HSTS<br/>• Rate Limiting de peticiones<br/>• Compresión Gzip / Brotli</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#047857;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             420, 440, 290, 100)

    add_node("n_gunicorn", "<b>Servidor WSGI (Gunicorn 21.x)</b><br/><font style='font-size:11px;color:#475569;'>• Manejador de Procesos Python (Workers)<br/>• Protocolo WSGI a Django<br/>• Socket UNIX / 127.0.0.1:8080</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#6366F1;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             780, 160, 380, 90)

    add_node("n_django", "<b>Framework Django 6.0 (Core)</b><br/><font style='font-size:11px;color:#475569;'>• Middlewares (Auth, Session, CSRF)<br/>• urls.py Router Principal<br/>• Apps: agenda, clientes, medico,<br/>  inventario, facturacion, grooming, usuarios<br/>• Django Template Engine (SSR) + API JSON</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#4F46E5;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             780, 270, 380, 150)

    add_node("n_orm", "<b>Django ORM &amp; Celery Client</b><br/><font style='font-size:11px;color:#475569;'>• Mapeo Objeto-Relacional Modelos<br/>• Transacciones atómicas seguras<br/>• Despacho de tareas asíncronas a Redis</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#4338CA;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             780, 440, 380, 100)

    add_node("n_ms1", "<b>MS 1: Notificaciones</b><br/><font style='font-size:11px;color:#475569;'>• FastAPI + Twilio/WhatsApp<br/>• Recordatorios citas y vacunas</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D946EF;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=10;",
             1230, 160, 290, 80)

    add_node("n_ms2", "<b>MS 2: Facturación &amp; Pagos</b><br/><font style='font-size:11px;color:#475569;'>• Node.js/FastAPI + Stripe<br/>• Firma Comprobante Fiscal SAT/SUNAT</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#C026D3;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=10;",
             1230, 260, 290, 80)

    add_node("n_ms3", "<b>MS 3: Telemedicina &amp; Video</b><br/><font style='font-size:11px;color:#475569;'>• Node.js + Socket.IO + WebRTC<br/>• Salas de consulta y chat en vivo</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#A21CAF;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=10;",
             1230, 360, 290, 80)

    add_node("n_ms4", "<b>MS 4: Reportes &amp; BI Asíncrono</b><br/><font style='font-size:11px;color:#475569;'>• Celery Worker + ReportLab<br/>• Generación pesada PDFs y Excel</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#86198F;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=10;",
             1230, 460, 290, 80)

    add_node("n_mysql", "<b>Base de Datos MySQL 8.0</b><br/><font style='font-size:11px;color:#475569;'>• BD: sistema_veterinaria_db<br/>• Tablas: Mascotas, Clientes, Citas,<br/>  Historias Clínicas, Kárdex, Facturas<br/>• Integridad Referencial ACID</font>",
             "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#FFFFFF;strokeColor=#F59E0B;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             1590, 160, 270, 120)

    add_node("n_redis", "<b>Redis 7.x (En Memoria)</b><br/><font style='font-size:11px;color:#475569;'>• Caché de sesiones de usuario<br/>• Message Broker para Celery y MS<br/>• Colas Pub/Sub en tiempo real</font>",
             "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#FFFFFF;strokeColor=#D97706;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             1590, 300, 270, 110)

    add_node("n_storage", "<b>Almacenamiento Archivos</b><br/><font style='font-size:11px;color:#475569;'>• /media/: Fotos mascotas, logos<br/>• /backups/: Copias SQL automáticas</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#B45309;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=15;",
             1590, 430, 270, 90)

    add_edge("e1", "<b>(1) Solicitud HTTPS</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#3B82F6;strokeWidth=2;fontColor=#1D4ED8;fontSize=11;", "n_browser", "n_dns")
    add_edge("e2", "<b>(2) Resuelve IP</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#10B981;strokeWidth=2;fontColor=#047857;fontSize=11;", "n_dns", "n_nginx")
    add_edge("e3", "<b>(4) proxy_pass</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6366F1;strokeWidth=2;fontColor=#4338CA;fontSize=11;", "n_nginx", "n_gunicorn")
    add_edge("e4", "<b>(5) WSGI Env</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#6366F1;strokeWidth=2;fontColor=#4338CA;fontSize=11;", "n_gunicorn", "n_django")
    add_edge("e5", "<b>(8) SQL Queries</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#F59E0B;strokeWidth=2;fontColor=#B45309;fontSize=11;", "n_django", "n_mysql")
    add_edge("e6", "<b>(9) Broker / Caché</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#D97706;strokeWidth=2;fontColor=#B45309;fontSize=11;", "n_django", "n_redis")
    add_edge("e7", "<b>Cola Tareas</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#D946EF;strokeWidth=2;fontColor=#86198F;fontSize=11;", "n_redis", "n_ms1")
    add_edge("e8", "<b>(11) Respuesta HTTP</b>", "edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#10B981;strokeWidth=2;dashed=1;fontColor=#047857;fontSize=11;exitX=0;exitY=0.7;entryX=1;entryY=0.7;", "n_nginx", "n_browser")

    add_node("box_lifecycle", "<b>CICLO DE VIDA DE LA PETICIÓN Y FLUJO DE COMUNICACIÓN PASO A PASO (E2E)</b><br/><font style='font-size:12px;color:#334155;'>"
             + "<b>[1] Navegador:</b> Usuario teclea https://vetsystem.clinica.com. "
             + "<b>[2] DNS Cloudflare:</b> Resuelve la IP pública y valida SSL. "
             + "<b>[3] Conexión HTTPS:</b> Negociación TLS 1.3 con Nginx (Puerto 443). "
             + "<b>[4] Nginx Proxy:</b> Filtra estáticos directos o reenvía dinámica a Gunicorn. "
             + "<b>[5] Gunicorn WSGI:</b> Transforma petición HTTP y la pasa a Django. "
             + "<b>[6] Middlewares:</b> Django valida autenticación, sesión y token CSRF. "
             + "<b>[7] urls.py:</b> Enruta al controlador correspondiente (agenda, medico, facturacion). "
             + "<b>[8] Django ORM:</b> Consulta/persiste datos en MySQL y consulta caché en Redis. "
             + "<b>[9] Microservicios:</b> Despacha tareas pesadas asíncronas vía Redis (WhatsApp, SAT, PDFs). "
             + "<b>[10] Render MVT:</b> Django genera la plantilla HTML con Bootstrap o responde JSON API. "
             + "<b>[11] Retorno:</b> Respuesta HTTP 200 viaja en reversa (Django -&gt; Gunicorn -&gt; Nginx -&gt; Cliente). "
             + "<b>[12] Navegador:</b> El navegador renderiza el DOM, aplica estilos Bootstrap y dibuja gráficos Chart.js."
             + "</font>",
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#64748B;strokeWidth=2;fontFamily=Segoe UI;align=left;spacingLeft=20;spacingRight=20;",
             40, 805, 1840, 160)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"[OK] Archivo Draw.io generado: {output_path}")


# -------------------------------------------------------------------------
# 4. GENERACIÓN DE VISTA WEB INTERACTIVA (HTML/SVG)
# -------------------------------------------------------------------------
def create_html_diagram(output_path="arquitectura_vetsystem.html"):
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arquitectura Tecnológica - Sistema Veterinario "VetSystem"</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-canvas: #f8fafc;
            --c-blue: #3b82f6;
            --c-emerald: #10b981;
            --c-indigo: #6366f1;
            --c-purple: #d946ef;
            --c-amber: #f59e0b;
            --text-dark: #0f172a;
            --text-muted: #64748b;
        }
        body {
            background-color: var(--bg-canvas);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            color: var(--text-dark);
        }
        .header-bar {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: white;
            padding: 24px 32px;
            border-bottom: 4px solid var(--c-blue);
        }
        .tier-column {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 2px solid transparent;
            transition: transform 0.2s, box-shadow 0.2s;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .tier-column:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        .tier-header {
            padding: 16px 20px;
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
            color: white;
            font-weight: 700;
            font-size: 1.05rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .tier-body {
            padding: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .card-component {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 14px 16px;
            position: relative;
        }
        .card-component h6 {
            font-weight: 700;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .card-component .tech-badge {
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 20px;
            font-weight: 600;
        }
        .card-component ul {
            margin: 8px 0 0 0;
            padding-left: 18px;
            font-size: 0.84rem;
            color: #334155;
        }
        .card-component ul li {
            margin-bottom: 3px;
        }
        .tier-1 { border-color: #bfdbfe; }
        .tier-1 .tier-header { background: #2563eb; }
        .tier-2 { border-color: #a7f3d0; }
        .tier-2 .tier-header { background: #059669; }
        .tier-3 { border-color: #c7d2fe; }
        .tier-3 .tier-header { background: #4f46e5; }
        .tier-4 { border-color: #f5d0fe; }
        .tier-4 .tier-header { background: #c026d3; }
        .tier-5 { border-color: #fde68a; }
        .tier-5 .tier-header { background: #d97706; }

        .lifecycle-container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
            margin-top: 30px;
        }
        .step-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 14px;
            height: 100%;
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        .step-circle {
            background: #2563eb;
            color: white;
            min-width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.85rem;
        }
        .step-content h6 {
            margin: 0 0 4px 0;
            font-weight: 700;
            font-size: 0.88rem;
        }
        .step-content p {
            margin: 0;
            font-size: 0.8rem;
            color: #64748b;
            line-height: 1.35;
        }
        @media print {
            .no-print { display: none !important; }
            body { background: white; }
            .tier-column { box-shadow: none; border: 1px solid #cbd5e1; }
        }
    </style>
</head>
<body>

    <header class="header-bar d-flex justify-content-between align-items-center flex-wrap">
        <div>
            <h2 class="mb-1 fw-bold"><i class="fa-solid fa-network-wired text-info me-2"></i> Arquitectura Tecnológica Web - VetSystem</h2>
            <p class="mb-0 text-secondary" style="font-size: 0.95rem;">
                Diagrama de Componentes, Microservicios Propuestos y Flujo de Comunicación E2E (12 Pasos)
            </p>
        </div>
        <div class="no-print mt-2 mt-md-0 d-flex gap-2">
            <a href="arquitectura_vetsystem.pdf" download class="btn btn-danger btn-sm px-3 fw-semibold">
                <i class="fa-solid fa-file-pdf me-1"></i> Descargar PDF
            </a>
            <a href="arquitectura_vetsystem.png" download class="btn btn-primary btn-sm px-3 fw-semibold">
                <i class="fa-solid fa-image me-1"></i> Descargar PNG
            </a>
            <a href="arquitectura_vetsystem.drawio" download class="btn btn-warning btn-sm px-3 fw-semibold text-dark">
                <i class="fa-solid fa-project-diagram me-1"></i> Archivo Draw.io
            </a>
            <button onclick="window.print()" class="btn btn-outline-light btn-sm px-3">
                <i class="fa-solid fa-print me-1"></i> Imprimir
            </button>
        </div>
    </header>

    <div class="container-fluid px-4 py-4">

        <div class="row g-3">
            
            <!-- Columna 1: Cliente / Frontend -->
            <div class="col-12 col-xl">
                <div class="tier-column tier-1">
                    <div class="tier-header">
                        <i class="fa-solid fa-desktop"></i> 1. Capa Cliente
                    </div>
                    <div class="tier-body">
                        <div class="card-component">
                            <h6>Navegador Web <span class="tech-badge bg-primary text-white">Browser</span></h6>
                            <div class="text-muted small">Dispositivos: PC Clínica / Tablet / Móvil</div>
                            <ul>
                                <li>Petición: <code>https://vetsystem.com</code></li>
                                <li>Roles: Veterinario, Recepción, Admin</li>
                                <li>Renderizado MVT / AJAX Dinámico</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Tecnologías Frontend <span class="tech-badge bg-secondary text-white">Stack</span></h6>
                            <ul>
                                <li><strong>HTML5 Semántico</strong> + CSS3</li>
                                <li><strong>Bootstrap 5</strong> (CSS Framework)</li>
                                <li><strong>JavaScript Vanilla</strong> (Fetch API)</li>
                                <li><strong>Chart.js</strong> (Métricas clínicas)</li>
                                <li><strong>FontAwesome 6</strong> (Iconografía)</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Vistas de Usuario <span class="tech-badge bg-info text-dark">UI</span></h6>
                            <ul>
                                <li>Agenda y Calendario de Citas</li>
                                <li>Ficha Clínica y Vacunación</li>
                                <li>Kárdex y Venta de Fármacos</li>
                                <li>Comprobantes y Cierre de Caja</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Columna 2: Red, Edge & Proxy -->
            <div class="col-12 col-xl">
                <div class="tier-column tier-2">
                    <div class="tier-header">
                        <i class="fa-solid fa-shield-halved"></i> 2. Red & Proxy
                    </div>
                    <div class="tier-body">
                        <div class="card-component">
                            <h6>DNS & CDN <span class="tech-badge bg-success text-white">Cloudflare</span></h6>
                            <ul>
                                <li>Resolución DNS de dominio a IP pública</li>
                                <li>Terminación SSL/TLS (HTTPS Puerto 443)</li>
                                <li>Mitigación DDoS y Web Application Firewall</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Servidor Nginx 1.24 <span class="tech-badge bg-dark text-white">Proxy Inverso</span></h6>
                            <ul>
                                <li><strong>/static/ y /media/:</strong> Servidos directos</li>
                                <li><strong>proxy_pass:</strong> Envío a Gunicorn (WSGI)</li>
                                <li><strong>/api/v1/:</strong> Ruteo a Microservicios</li>
                                <li><strong>/ws/:</strong> Proxy WebSockets Telemedicina</li>
                                <li>Compresión Gzip y HTTP/2</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Seguridad Perimetral <span class="tech-badge bg-secondary text-white">Security</span></h6>
                            <ul>
                                <li>Cabeceras HSTS, CSP y X-Frame</li>
                                <li>Protección contra CSRF y XSS</li>
                                <li>Rate Limiting contra fuerza bruta</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Columna 3: Core Backend (Django) -->
            <div class="col-12 col-xl">
                <div class="tier-column tier-3">
                    <div class="tier-header">
                        <i class="fa-brands fa-python"></i> 3. Core Django
                    </div>
                    <div class="tier-body">
                        <div class="card-component">
                            <h6>Servidor WSGI <span class="tech-badge bg-indigo text-white" style="background:#6366f1;">Gunicorn 21</span></h6>
                            <ul>
                                <li>Administrador de procesos Python Workers</li>
                                <li>Conexión mediante socket UNIX / TCP local</li>
                                <li>Manejo de concurrencia y timeouts</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Núcleo Django 6.0 <span class="tech-badge bg-success text-white">Monolito</span></h6>
                            <ul>
                                <li><strong>Middlewares:</strong> Auth, Session, CSRF</li>
                                <li><strong>apps.agenda:</strong> Citas y turnos</li>
                                <li><strong>apps.clientes:</strong> Pacientes y dueños</li>
                                <li><strong>apps.medico:</strong> Historias y vacunas</li>
                                <li><strong>apps.inventario:</strong> Fármacos y stock</li>
                                <li><strong>apps.facturacion:</strong> Comprobantes y caja</li>
                                <li><strong>apps.grooming:</strong> Peluquería</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Django ORM <span class="tech-badge bg-primary text-white">Data Layer</span></h6>
                            <ul>
                                <li>Mapeo Objeto-Relacional Modelos</li>
                                <li>Transacciones atómicas (ACID)</li>
                                <li>Cliente Celery / Despacho a Redis</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Columna 4: Microservicios Satélite -->
            <div class="col-12 col-xl">
                <div class="tier-column tier-4">
                    <div class="tier-header">
                        <i class="fa-solid fa-cubes"></i> 4. Microservicios
                    </div>
                    <div class="tier-body">
                        <div class="card-component">
                            <h6>MS 1: Notificaciones <span class="tech-badge bg-purple text-white" style="background:#c026d3;">FastAPI</span></h6>
                            <ul>
                                <li>Recordatorios de citas vía WhatsApp API</li>
                                <li>Alertas de vacunas por vencer (Email/SMS)</li>
                                <li>Consumo asíncrono desde cola Redis</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>MS 2: Facturación & Pagos <span class="tech-badge bg-purple text-white" style="background:#a21caf;">Node / API</span></h6>
                            <ul>
                                <li>Firma digital XML de comprobante fiscal</li>
                                <li>Pasarela de cobros en línea (Stripe/Culqi)</li>
                                <li>Webhooks de conciliación bancaria</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>MS 3: Telemedicina <span class="tech-badge bg-purple text-white" style="background:#86198f;">WebRTC</span></h6>
                            <ul>
                                <li>Consultas virtuales por videollamada</li>
                                <li>Chat en tiempo real veterinario-dueño</li>
                                <li>Node.js + WebSockets + Janus Gateway</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>MS 4: Reportes & BI <span class="tech-badge bg-dark text-white">Celery Worker</span></h6>
                            <ul>
                                <li>Generación pesada de balances PDF (ReportLab)</li>
                                <li>Exportación masiva de Kárdex a Excel</li>
                                <li>Procesamiento en background sin congelar web</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Columna 5: Persistencia y Datos -->
            <div class="col-12 col-xl">
                <div class="tier-column tier-5">
                    <div class="tier-header">
                        <i class="fa-solid fa-database"></i> 5. Persistencia
                    </div>
                    <div class="tier-body">
                        <div class="card-component">
                            <h6>Base de Datos MySQL <span class="tech-badge bg-warning text-dark">RDBMS</span></h6>
                            <ul>
                                <li><strong>Esquema:</strong> <code>sistema_veterinaria_db</code></li>
                                <li>Tablas: Pacientes, Citas, Consultas, Kárdex, Facturas, Usuarios</li>
                                <li>Integridad referencial y transacciones ACID</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Redis 7.x (En Memoria) <span class="tech-badge bg-danger text-white">In-Memory</span></h6>
                            <ul>
                                <li>Caché de sesiones de usuarios activos</li>
                                <li>Caché de KPIs del Dashboard</li>
                                <li>Message Broker para Celery y Microservicios</li>
                            </ul>
                        </div>
                        <div class="card-component">
                            <h6>Almacenamiento de Archivos <span class="tech-badge bg-secondary text-white">Storage</span></h6>
                            <ul>
                                <li><code>/media/</code> Fotos de mascotas y logos</li>
                                <li><code>/backups/</code> Respaldos SQL (.sql)</li>
                                <li>Consentimientos y recetas firmadas</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- Sección Inferior: Flujo de Comunicación (12 Pasos) -->
        <div class="lifecycle-container">
            <h5 class="fw-bold mb-4 text-dark d-flex align-items-center gap-2">
                <i class="fa-solid fa-route text-primary"></i> 
                Flujo de Comunicación E2E (Ciclo de Vida de la Petición: del Dominio a la Respuesta)
            </h5>
            
            <div class="row g-3">
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">1</div>
                        <div class="step-content">
                            <h6>Solicitud Inicial</h6>
                            <p>El usuario ingresa <code>https://vetsystem.clinica.com</code> en su navegador web.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">2</div>
                        <div class="step-content">
                            <h6>Resolución DNS</h6>
                            <p>El DNS (Cloudflare) traduce el nombre de dominio a la IP pública del servidor.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">3</div>
                        <div class="step-content">
                            <h6>Handshake HTTPS</h6>
                            <p>Conexión segura TLS 1.3 al puerto 443 de Nginx. Se verifica el certificado SSL.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">4</div>
                        <div class="step-content">
                            <h6>Inspección Nginx</h6>
                            <p>Nginx sirve estáticos directos (CSS/JS) o hace <code>proxy_pass</code> a Gunicorn.</p>
                        </div>
                    </div>
                </div>

                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">5</div>
                        <div class="step-content">
                            <h6>Traspaso WSGI</h6>
                            <p>Gunicorn toma la petición HTTP y la entrega al core de Django como entorno WSGI.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">6</div>
                        <div class="step-content">
                            <h6>Middlewares</h6>
                            <p>Django valida seguridad: sesión de usuario activa, permisos RBAC y token CSRF.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">7</div>
                        <div class="step-content">
                            <h6>Enrutador URLs</h6>
                            <p><code>urls.py</code> ejecuta la vista del módulo correspondiente (ej. <code>apps.medico</code>).</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">8</div>
                        <div class="step-content">
                            <h6>Consulta ORM</h6>
                            <p>La vista consulta o guarda datos mediante Django ORM contra MySQL (y caché Redis).</p>
                        </div>
                    </div>
                </div>

                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">9</div>
                        <div class="step-content">
                            <h6>Microservicios</h6>
                            <p>Si es tarea pesada (WhatsApp, SAT o PDF), se despacha en segundo plano a Redis.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">10</div>
                        <div class="step-content">
                            <h6>Renderizado MVT</h6>
                            <p>Django ensambla el HTML final con datos usando su motor de plantillas o responde JSON API.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">11</div>
                        <div class="step-content">
                            <h6>Retorno de Respuesta</h6>
                            <p>HTTP 200 viaja de regreso: Django &rarr; Gunicorn &rarr; Nginx &rarr; Navegador.</p>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-6 col-lg-3">
                    <div class="step-box">
                        <div class="step-circle">12</div>
                        <div class="step-content">
                            <h6>Pintado en Cliente</h6>
                            <p>El navegador renderiza el DOM, aplica Bootstrap 5 y dibuja gráficos con Chart.js.</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>

    </div>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Archivo HTML interactivo generado: {output_path}")

if __name__ == "__main__":
    import shutil
    create_png_diagram("arquitectura_vetsystem.png")
    create_pdf_diagram("arquitectura_vetsystem.pdf", "arquitectura_vetsystem.png")
    create_drawio_file("arquitectura_vetsystem.drawio")
    create_html_diagram("arquitectura_vetsystem.html")
    
    os.makedirs("static", exist_ok=True)
    for fn in ["arquitectura_vetsystem.png", "arquitectura_vetsystem.pdf", "arquitectura_vetsystem.drawio", "arquitectura_vetsystem.html"]:
        shutil.copy(fn, os.path.join("static", fn))
        
    print("\nTODOS LOS ENTREGABLES HAN SIDO REGENERADOS Y SINCRONIZADOS EXITOSAMENTE.")
