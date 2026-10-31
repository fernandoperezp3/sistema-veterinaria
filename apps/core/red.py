import re
import socket
from urllib.parse import quote

CODIGO_PAIS = "502"


def ip_lan():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def host_publico(request):
    host = request.get_host().split(":")[0]
    if host in ("localhost", "127.0.0.1", "::1"):
        ip = ip_lan()
        if ip:
            host = f"{ip}.nip.io"
    return host


def ruta_sala(enlace):
    if enlace and "/sala/" in enlace:
        return "/sala/" + enlace.split("/sala/", 1)[1].split("?")[0]
    return None


def host_sala(request):
    host = request.get_host().split(":")[0]
    if host.endswith(".nip.io"):
        return host[: -len(".nip.io")]
    if host in ("localhost", "127.0.0.1", "::1"):
        return ip_lan() or host
    return host


def enlace_sala_publico(request, enlace, rol):
    ruta = ruta_sala(enlace)
    if not ruta:
        return enlace
    host = host_sala(request)
    if request.is_secure():
        return f"https://{host}{ruta}?rol={rol}"
    return f"http://{host}:8083{ruta}?rol={rol}"


def enlace_whatsapp(telefono, mensaje):
    numero = re.sub(r"\D", "", telefono or "")
    if not numero or set(numero) == {"0"}:
        return None
    if len(numero) == 8:
        numero = CODIGO_PAIS + numero
    return f"https://wa.me/{numero}?text={quote(mensaje)}"
