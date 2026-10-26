"""
Microservicio 3: Telemedicina y Streaming en Tiempo Real
Puerto: 8083
Framework: FastAPI + WebSockets (Python 3.12/3.13)
Swagger Docs: http://127.0.0.1:8083/docs
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import json
import html
from datetime import datetime
import time

app = FastAPI(
    title="VetSystem - Microservicio de Telemedicina",
    description="Servicio de señalización WebRTC y WebSockets para consultas virtuales veterinarias y chat en vivo.",
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
SALAS_ACTIVAS: Dict[str, dict] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict, sender: WebSocket):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != sender:
                    await connection.send_text(json.dumps(message))

manager = ConnectionManager()

class CrearSalaRequest(BaseModel):
    cita_id: int
    veterinario: str
    paciente: str
    propietario: str

@app.get("/health")
def health_check():
    uptime_sec = int(time.time() - START_TIME)
    total_conexiones = sum(len(c) for c in manager.active_connections.values())
    return {
        "microservicio": "Telemedicina & WebRTC Gateway",
        "estado": "ONLINE",
        "puerto": 8083,
        "uptime_segundos": uptime_sec,
        "salas_creadas": len(SALAS_ACTIVAS),
        "conexiones_activas": total_conexiones,
        "protocolos": ["WebSockets (WSS)", "WebRTC Signaling"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/telemedicina/crear-sala")
def crear_sala(req: CrearSalaRequest):
    sala_id = f"vet-{req.cita_id}-{uuid.uuid4().hex[:6]}"
    url_acceso = f"http://127.0.0.1:8083/sala/{sala_id}"
    
    sala_data = {
        "sala_id": sala_id,
        "cita_id": req.cita_id,
        "veterinario": req.veterinario,
        "paciente": req.paciente,
        "propietario": req.propietario,
        "url_acceso": url_acceso,
        "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "DISPONIBLE"
    }
    SALAS_ACTIVAS[sala_id] = sala_data
    
    return {
        "success": True,
        "mensaje": "Sala de teleconsulta creada exitosamente.",
        "sala": sala_data
    }

@app.websocket("/ws/sala/{sala_id}")
async def websocket_endpoint(websocket: WebSocket, sala_id: str):
    # Además del chat, este canal sirve de señalización WebRTC (join / offer / answer / ice / leave)
    await manager.connect(sala_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            await manager.broadcast_to_room(sala_id, message_data, sender=websocket)
    except WebSocketDisconnect:
        manager.disconnect(sala_id, websocket)
        try:
            await manager.broadcast_to_room(sala_id, {"type": "leave"}, sender=websocket)
        except Exception:
            pass


SALA_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Teleconsulta VetSystem - Sala __SALA_ID__</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0f172a; color: white; font-family: 'Segoe UI', sans-serif; }
        .video-box { background: #1e293b; border-radius: 12px; height: 350px; display: flex; align-items: center; justify-content: center; position: relative; border: 2px solid #334155; overflow: hidden; }
        .video-box video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; background: #000; display: none; }
        .video-box.activo video { display: block; }
        .video-box.activo .placeholder-cam { display: none; }
        .video-box .badge { z-index: 2; }
        #videoLocal { transform: scaleX(-1); }
        .chat-box { background: #1e293b; border-radius: 12px; height: 500px; display: flex; flex-direction: column; border: 1px solid #334155; }
        .chat-messages { flex-grow: 1; padding: 15px; overflow-y: auto; font-size: 0.9rem; }
        .msg-in { background: #334155; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; }
        .msg-out { background: #2563eb; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; width: fit-content; max-width: 80%; align-self: flex-end; margin-left: auto; }
    </style>
</head>
<body class="py-4">
    <div class="container">
        <div class="d-flex flex-wrap gap-2 justify-content-between align-items-center mb-3 border-bottom pb-2 border-secondary">
            <div>
                <h4 class="mb-0 text-info"><i class="fa-solid fa-video me-2"></i> Sala de Telemedicina: __SALA_ID__</h4>
                <small class="text-secondary">Paciente: <strong>__PACIENTE__</strong> | Dueño: <strong>__PROPIETARIO__</strong> | Médico: <strong>__VETERINARIO__</strong></small>
            </div>
            <span id="estadoConexion" class="badge bg-secondary px-3 py-2"><i class="fa-solid fa-circle me-1" style="font-size: 8px;"></i> Esperando al otro participante...</span>
        </div>

        <div class="row g-3">
            <div class="col-md-8">
                <div class="row g-2 mb-3">
                    <div class="col-6">
                        <div class="video-box" id="boxLocal">
                            <video id="videoLocal" autoplay playsinline muted></video>
                            <div class="text-center text-secondary placeholder-cam">
                                <i id="iconoLocal" class="fa-solid fa-3x mb-2"></i>
                                <div id="textoLocal">Activando tu cámara...</div>
                            </div>
                            <span id="etiquetaLocal" class="badge position-absolute bottom-0 start-0 m-2"></span>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="video-box" id="boxRemoto">
                            <video id="videoRemoto" autoplay playsinline></video>
                            <div class="text-center text-secondary placeholder-cam">
                                <i id="iconoRemoto" class="fa-solid fa-3x mb-2"></i>
                                <div>Esperando conexión...</div>
                            </div>
                            <span id="etiquetaRemoto" class="badge position-absolute bottom-0 start-0 m-2"></span>
                        </div>
                    </div>
                </div>
                <div class="bg-dark p-3 rounded d-flex flex-wrap justify-content-center gap-3">
                    <button id="btnAudio" class="btn btn-secondary" onclick="toggleAudio()"><i class="fa-solid fa-microphone me-1"></i> Silenciar</button>
                    <button id="btnVideo" class="btn btn-secondary" onclick="toggleVideo()"><i class="fa-solid fa-video me-1"></i> Apagar video</button>
                    <button class="btn btn-danger" onclick="finalizar()"><i class="fa-solid fa-phone-slash me-1"></i> Finalizar Consulta</button>
                </div>
            </div>

            <div class="col-md-4">
                <div class="chat-box">
                    <div class="p-2 border-bottom border-secondary bg-secondary bg-opacity-25 fw-bold">
                        <i class="fa-solid fa-comments me-1"></i> Chat en Tiempo Real (WebSocket)
                    </div>
                    <div id="messages" class="chat-messages d-flex flex-column"></div>
                    <div class="p-2 border-top border-secondary d-flex gap-2">
                        <input id="inputMsg" type="text" class="form-control form-control-sm bg-dark text-white border-secondary" placeholder="Escribe un mensaje...">
                        <button onclick="enviarMensaje()" class="btn btn-primary btn-sm"><i class="fa-solid fa-paper-plane"></i></button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const salaId = __SALA_ID_JS__;
        const ROL = new URLSearchParams(location.search).get('rol') === 'cliente' ? 'cliente' : 'vet';
        const ROLES = {
            vet:     { nombre: 'Veterinario', icono: 'fa-user-doctor', badge: 'bg-primary' },
            cliente: { nombre: 'Dueño',       icono: 'fa-paw',         badge: 'bg-warning text-dark' },
        };
        const YO = ROLES[ROL];
        const OTRO = ROLES[ROL === 'vet' ? 'cliente' : 'vet'];
        const ICE_CONFIG = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };

        let socket = null;
        let pc = null;
        let localStream = null;
        let iceEnEspera = [];
        let cola = Promise.resolve();  // procesa la señalización en orden

        const $ = id => document.getElementById(id);

        // ── Interfaz ──────────────────────────────────────────────
        function prepararEtiquetas() {
            $('iconoLocal').classList.add(YO.icono, ROL === 'vet' ? 'text-primary' : 'text-warning');
            $('iconoRemoto').classList.add(OTRO.icono, ROL === 'vet' ? 'text-warning' : 'text-primary');
            $('etiquetaLocal').className += ' ' + YO.badge;
            $('etiquetaLocal').textContent = 'Tú (' + YO.nombre + ')';
            $('etiquetaRemoto').className += ' ' + OTRO.badge;
            $('etiquetaRemoto').textContent = OTRO.nombre;
        }

        function agregarMensaje(autor, texto, clase, colorAutor) {
            const box = $('messages');
            const div = document.createElement('div');
            div.className = clase;
            const small = document.createElement('small');
            small.className = 'fw-bold ' + colorAutor;
            small.textContent = autor + ':';
            div.appendChild(small);
            div.appendChild(document.createElement('br'));
            div.appendChild(document.createTextNode(texto));
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }
        const sistema = texto => agregarMensaje('Sistema', texto, 'msg-in', 'text-info');

        function mostrarEstado(texto, color) {
            const el = $('estadoConexion');
            el.className = 'badge px-3 py-2 ' + color;
            el.innerHTML = '<i class="fa-solid fa-circle me-1" style="font-size: 8px;"></i> ';
            el.appendChild(document.createTextNode(texto));
        }

        // ── Cámara y micrófono ───────────────────────────────────
        async function iniciarMedia() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                $('textoLocal').textContent = 'Navegador sin acceso a cámara';
                sistema('El navegador no permite usar la cámara en esta dirección. Abre la sala desde http://127.0.0.1 o con HTTPS.');
                return;
            }
            try {
                localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            } catch (err) {
                try {
                    localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    sistema('No se pudo usar la cámara (' + err.name + '). Participas solo con audio.');
                } catch (err2) {
                    sistema('No se pudo acceder a cámara ni micrófono (' + err.name + '). Igual podrás ver y oír al otro participante.');
                }
            }
            if (localStream && localStream.getVideoTracks().length) {
                $('videoLocal').srcObject = localStream;
                $('boxLocal').classList.add('activo');
            } else {
                $('textoLocal').textContent = 'Cámara no disponible';
            }
        }

        // ── WebRTC ───────────────────────────────────────────────
        function crearConexion() {
            if (pc) pc.close();
            iceEnEspera = [];
            pc = new RTCPeerConnection(ICE_CONFIG);

            if (localStream) {
                localStream.getTracks().forEach(t => pc.addTrack(t, localStream));
            } else {
                pc.addTransceiver('video', { direction: 'recvonly' });
                pc.addTransceiver('audio', { direction: 'recvonly' });
            }

            pc.onicecandidate = e => { if (e.candidate) enviar({ type: 'ice', candidate: e.candidate }); };
            pc.ontrack = e => {
                const video = $('videoRemoto');
                if (!video.srcObject) video.srcObject = new MediaStream();
                video.srcObject.addTrack(e.track);
                if (e.track.kind === 'video') $('boxRemoto').classList.add('activo');
            };
            pc.onconnectionstatechange = () => {
                const s = pc.connectionState;
                if (s === 'connected') mostrarEstado('En llamada con ' + OTRO.nombre, 'bg-success');
                else if (s === 'connecting') mostrarEstado('Conectando...', 'bg-warning text-dark');
                else if (s === 'failed') { mostrarEstado('Falló la conexión', 'bg-danger'); sistema('No se pudo establecer la videollamada.'); }
                else if (s === 'disconnected') mostrarEstado('Conexión inestable...', 'bg-warning text-dark');
            };
        }

        function limpiarRemoto() {
            if (pc) { pc.close(); pc = null; }
            $('videoRemoto').srcObject = null;
            $('boxRemoto').classList.remove('activo');
            mostrarEstado('Esperando al otro participante...', 'bg-secondary');
        }

        async function aplicarIceEnEspera() {
            for (const c of iceEnEspera) { try { await pc.addIceCandidate(c); } catch (e) { console.warn(e); } }
            iceEnEspera = [];
        }

        async function manejarSenal(d) {
            if (d.type === 'join') {
                // Quien ya estaba en la sala inicia la llamada
                sistema((d.nombre || 'Un participante') + ' se unió a la sala.');
                crearConexion();
                await pc.setLocalDescription(await pc.createOffer());
                enviar({ type: 'offer', sdp: pc.localDescription, nombre: YO.nombre });
            } else if (d.type === 'offer') {
                crearConexion();
                await pc.setRemoteDescription(d.sdp);
                await aplicarIceEnEspera();
                await pc.setLocalDescription(await pc.createAnswer());
                enviar({ type: 'answer', sdp: pc.localDescription });
            } else if (d.type === 'answer') {
                if (!pc) return;
                await pc.setRemoteDescription(d.sdp);
                await aplicarIceEnEspera();
            } else if (d.type === 'ice') {
                if (pc && pc.remoteDescription) await pc.addIceCandidate(d.candidate);
                else iceEnEspera.push(d.candidate);
            } else if (d.type === 'leave') {
                if (pc) sistema(OTRO.nombre + ' salió de la sala.');
                limpiarRemoto();
            } else if (d.chat) {
                agregarMensaje(d.usuario, d.chat, 'msg-in', 'text-warning');
            }
        }

        function enviar(obj) {
            if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(obj));
        }

        function conectarSocket() {
            const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(wsProtocol + '//' + location.host + '/ws/sala/' + encodeURIComponent(salaId));
            socket.onopen = () => {
                sistema('Conectado a la sala segura como ' + YO.nombre + '.');
                enviar({ type: 'join', nombre: YO.nombre });
            };
            socket.onmessage = ev => {
                const d = JSON.parse(ev.data);
                cola = cola.then(() => manejarSenal(d)).catch(err => console.error('Señalización:', err));
            };
            socket.onclose = () => mostrarEstado('Desconectado del servidor', 'bg-danger');
        }

        // ── Controles ────────────────────────────────────────────
        function toggleAudio() {
            const pistas = localStream ? localStream.getAudioTracks() : [];
            if (!pistas.length) return;
            const activo = !pistas[0].enabled;
            pistas.forEach(t => t.enabled = activo);
            $('btnAudio').className = 'btn ' + (activo ? 'btn-secondary' : 'btn-warning');
            $('btnAudio').innerHTML = activo
                ? '<i class="fa-solid fa-microphone me-1"></i> Silenciar'
                : '<i class="fa-solid fa-microphone-slash me-1"></i> Activar micrófono';
        }

        function toggleVideo() {
            const pistas = localStream ? localStream.getVideoTracks() : [];
            if (!pistas.length) return;
            const activo = !pistas[0].enabled;
            pistas.forEach(t => t.enabled = activo);
            $('boxLocal').classList.toggle('activo', activo);
            $('textoLocal').textContent = 'Video apagado';
            $('btnVideo').className = 'btn ' + (activo ? 'btn-secondary' : 'btn-warning');
            $('btnVideo').innerHTML = activo
                ? '<i class="fa-solid fa-video me-1"></i> Apagar video'
                : '<i class="fa-solid fa-video-slash me-1"></i> Encender video';
        }

        function finalizar() {
            enviar({ type: 'leave' });
            if (pc) { pc.close(); pc = null; }
            if (localStream) localStream.getTracks().forEach(t => t.stop());
            if (socket) socket.close();
            window.close();
            document.body.innerHTML = '<div class="container text-center py-5"><i class="fa-solid fa-circle-check fa-3x text-success mb-3"></i>'
                + '<h4>Consulta finalizada</h4><p class="text-secondary">Ya puedes cerrar esta pestaña.</p></div>';
        }

        $('inputMsg').addEventListener('keypress', e => { if (e.key === 'Enter') enviarMensaje(); });
        function enviarMensaje() {
            const input = $('inputMsg');
            const txt = input.value.trim();
            if (!txt) return;
            enviar({ chat: txt, usuario: YO.nombre });
            agregarMensaje('Tú', txt, 'msg-out', 'text-light');
            input.value = '';
        }

        window.addEventListener('beforeunload', () => enviar({ type: 'leave' }));

        (async () => {
            prepararEtiquetas();
            await iniciarMedia();
            conectarSocket();
        })();
    </script>
</body>
</html>"""


@app.get("/sala/{sala_id}", response_class=HTMLResponse)
def vista_sala_videollamada(sala_id: str):
    sala = SALAS_ACTIVAS.get(sala_id, {
        "veterinario": "Dr. Veterinario",
        "paciente": "Mascota",
        "propietario": "Cliente"
    })

    contenido = (SALA_HTML
        .replace("__SALA_ID_JS__", json.dumps(sala_id).replace("<", "\\u003c"))
        .replace("__SALA_ID__", html.escape(sala_id))
        .replace("__PACIENTE__", html.escape(str(sala.get("paciente"))))
        .replace("__PROPIETARIO__", html.escape(str(sala.get("propietario"))))
        .replace("__VETERINARIO__", html.escape(str(sala.get("veterinario")))))
    return HTMLResponse(content=contenido)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8083, reload=True)
