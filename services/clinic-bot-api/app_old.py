import asyncio
import base64
import os
import time
from email.mime.text import MIMEText
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

PORT = int(os.getenv("PORT", "8088"))

# Legacy WA bridge (still used for send/receive pipeline)
WAHA_URL = os.getenv("WAHA_URL", "http://waha:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")

# Evolution API (source of truth for connection status + QR)
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://10.1.1.10:8089")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "clinic-bot")
EVOLUTION_MANAGER_URL = os.getenv("EVOLUTION_MANAGER_URL", "http://10.1.1.10:8089/manager/")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://10.1.1.39:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lfm2:latest")

CLINIC_KB_PATH = os.getenv("CLINIC_KB_PATH", "/app/kb/clinic_menu.md")
N8N_EVENT_WEBHOOK = os.getenv("N8N_EVENT_WEBHOOK", "")
RUNTIME_CFG_PATH = os.getenv("RUNTIME_CFG_PATH", "/app/kb/runtime_config.json")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_COOKIE = "clinic_admin_auth"
ADMIN_LAST_ACTIVE_COOKIE = "clinic_admin_last"
ADMIN_IDLE_TIMEOUT_SEC = int(os.getenv("ADMIN_IDLE_TIMEOUT_SEC", "900"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", ALERT_EMAIL_TO)

app = FastAPI(title="clinic-whatsapp-bot", version="0.2.0")
_last_status = {"connected": None, "last_alert_at": 0}
_evo_qr_cache = {"png": None, "updated_at": 0}
_bot_paused = False


def kb_text() -> str:
    try:
        with open(CLINIC_KB_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def save_kb_text(text: str):
    with open(CLINIC_KB_PATH, "w", encoding="utf-8") as f:
        f.write(text)


def load_runtime_cfg() -> dict:
    try:
        import json
        with open(RUNTIME_CFG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_runtime_cfg(cfg: dict):
    import json
    os.makedirs(os.path.dirname(RUNTIME_CFG_PATH), exist_ok=True)
    with open(RUNTIME_CFG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def runtime_ollama_url() -> str:
    return load_runtime_cfg().get('ollama_url') or OLLAMA_URL


def runtime_ollama_model() -> str:
    return load_runtime_cfg().get('ollama_model') or OLLAMA_MODEL


def runtime_admin_idle_timeout_sec() -> int:
    cfg = load_runtime_cfg()
    try:
        return int(cfg.get('admin_idle_timeout_sec', ADMIN_IDLE_TIMEOUT_SEC))
    except Exception:
        return ADMIN_IDLE_TIMEOUT_SEC


def runtime_menu_title() -> str:
    cfg = load_runtime_cfg()
    return str(cfg.get('menu_title') or 'Clínica')


def runtime_admin_password() -> str:
    cfg = load_runtime_cfg()
    return str(cfg.get('admin_password') or ADMIN_PASSWORD)


_chat_state: dict[str, dict] = {}
CHAT_IDLE_RESET_SEC = int(os.getenv("CHAT_IDLE_RESET_SEC", "180"))


def menu_main() -> str:
    title = runtime_menu_title()
    return (
        f"🏥 *{title}*\n"
        "Bienvenido/a 👋\n\n"
        "📝 *Atención por texto únicamente*\n"
        "No atendemos llamadas ni audios por este canal.\n\n"
        "Elegí una opción:\n"
        "1️⃣ Turnos\n"
        "2️⃣ Asuntos laborales\n"
        "3️⃣ Farmacia\n"
        "4️⃣ Afiliaciones\n"
        "5️⃣ Discapacidad\n"
        "6️⃣ Bocas de expendio\n\n"
        "↩️ Escribí *0* para volver al menú principal."
    )


def _turnos_menu() -> str:
    return (
        "🗓️ *Turnos*\n\n"
        "Seleccioná especialidad:\n"
        "1️⃣ Clínica Médica\n"
        "2️⃣ Aparato Digestivo\n"
        "3️⃣ Ginecología y Obstetricia\n"
        "4️⃣ Odontología\n"
        "5️⃣ Nutrición\n"
        "6️⃣ Terapia Ocupacional\n"
        "7️⃣ Psicología\n"
        "8️⃣ Pediatría\n\n"
        "↩️ 0 para menú principal"
    )


def _iconize_professional(name: str) -> str:
    n = (name or "").strip()
    l = n.lower()
    if l.startswith("dra") or l.startswith("lic"):
        return f"👩‍⚕️ {n}"
    if l.startswith("dr") or l.startswith("od"):
        return f"👨‍⚕️ {n}"
    return f"🩺 {n}"


def _turno_derivacion(especialidad: str, profesional: str, detalle: str) -> str:
    prof = _iconize_professional(profesional)
    return (
        "✅ *Solicitud de turno registrada*\n\n"
        f"• Especialidad: {especialidad}\n"
        f"• Profesional: {prof}\n"
        f"• Detalle: {detalle}\n\n"
        "Para continuar, enviá:\n"
        "• Nombre y apellido\n"
        "• DNI\n"
        "• Teléfono\n"
        "• Motivo de consulta\n\n"
        "👩‍💼 Un operador te responde por este mismo chat.\n\n"
        "↩️ Para volver al menú principal, presioná 0"
    )


def menu_response(user_text: str, state: dict | None = None) -> tuple[str | None, dict]:
    s = dict(state or {})
    t = (user_text or "").strip().lower()
    t = t.replace("opcion", "").replace("opción", "").strip()

    if t in {"hola", "menu", "menú", "inicio", "0"}:
        return menu_main(), {"step": "main"}

    step = s.get("step", "main")

    # MAIN
    if step == "main":
        if t in {"1", "turnos"}:
            return _turnos_menu(), {"step": "turnos"}
        if t in {"2", "asuntos laborales", "laborales"}:
            return (
                "🧾 *Asuntos laborales*\n\n"
                "🕘 08:00 a 16:00\n"
                "☎️ 4580099 / 4593304 (int. 1109)\n"
                "💬 *Abrir chat:*\n"
                "1️⃣ wa.me/5493425016120\n"
                "2️⃣ wa.me/5493424438163\n"
                "3️⃣ wa.me/5493425442025\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"3", "farmacia"}:
            return (
                "💊 *Farmacia*\n\n"
                "🕘 08:00 a 16:00\n"
                "☎️ 4580099 / 4593304 (int. 1122)\n"
                "💬 *Abrir chat:* wa.me/5493424483057\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"4", "afiliaciones"}:
            return (
                "🪪 *Afiliaciones*\n\n"
                "🕘 08:00 a 16:00\n"
                "☎️ 4580099 / 4593304 (int. 1107)\n"
                "💬 *Abrir chat:* wa.me/5493426506301\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"5", "discapacidad"}:
            return (
                "♿ *Discapacidad*\n\n"
                "🕘 08:00 a 13:30\n"
                "☎️ 4580099 / 4593304 (int. 1104)\n"
                "💬 *Abrir chat:* wa.me/5493425667161\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"6", "bocas", "bocas de expendio"}:
            return (
                "📍 *Bocas de expendio*\n\n"
                "1️⃣ Recreo Sur\n"
                "2️⃣ Santo Tomé\n"
                "3️⃣ Ver ambas\n\n"
                "↩️ 0 para menú principal"
            ), {"step": "bocas"}

    # BOCAS
    if step == "bocas":
        if t in {"1", "recreo", "61", "6.1"}:
            return (
                "🏢 *Recreo Sur*\n\n"
                "🕘 08:00 a 16:00\n"
                "📍 Juan de Garay 4791\n"
                "💬 *Abrir chat:* wa.me/5493425013622\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"2", "santo tome", "santo tomé", "62", "6.2"}:
            return (
                "🏢 *Santo Tomé*\n\n"
                "🕘 09:00 a 15:00\n"
                "📍 República de Irak 3556\n"
                "💬 *Abrir chat:* wa.me/5493424673443\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"3", "ambas", "63", "6.3"}:
            return (
                "📌 *Bocas disponibles*\n\n"
                "1️⃣ Recreo Sur · wa.me/5493425013622\n"
                "2️⃣ Santo Tomé · wa.me/5493424673443\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}

    # TURNOS (avoid loop by state)
    if step == "turnos":
        if t in {"1", "clinica medica", "clínica médica", "11", "1.1"}:
            return (
                "🩺 *Clínica Médica*\n\n"
                "Elegí profesional:\n"
                "1️⃣ 👩‍⚕️ Dra. Gómez Vanesa\n"
                "• Atención: Martes 09:00–11:00\n"
                "• Modalidad: orden de llegada\n\n"
                "2️⃣ 👨‍⚕️ Dr. Aramayo Alejandro\n"
                "• Atención: Miércoles 09:30–12:30\n"
                "• Lunes/Viernes: consultar\n"
                "• Modalidad: orden de llegada\n\n"
                "3️⃣ 👩‍⚕️ Dra. Sánchez Teresa\n"
                "• Atención: Lunes/Jueves/Viernes 11:00–13:30\n"
                "• Turnos en el día: 4593304 / 4580099 (int. 1101-1102)\n"
                "⚠️ No se otorgan turnos por WhatsApp\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "turnos_11"}
        if t in {"2", "aparato digestivo", "12", "1.2"}:
            return _turno_derivacion("Aparato Digestivo", "Dr. Aramayo Alejandro", "Miércoles 09:30–12:30 · orden de llegada"), {"step": "main"}
        if t in {"3", "ginecologia", "ginecología", "13", "1.3"}:
            return _turno_derivacion("Ginecología y Obstetricia", "Dr. Bosquiazzo Leandro", "Lunes 13:30 · orden de llegada (agendado previo)"), {"step": "main"}
        if t in {"4", "odontologia", "odontología", "14", "1.4"}:
            return (
                "😁 *Odontología*\n\n"
                "1️⃣ 👩‍⚕️ Od. Herrera Ma. José\n"
                "2️⃣ 👩‍⚕️ Od. Mondini Evangelina\n\n"
                "• Turnos desde 14:00\n"
                "• Tel: 4593304 / 4580099 (int. 1101-1102)\n"
                "⚠️ No se otorgan turnos por WhatsApp\n\n"
                "↩️ Para volver al menú principal, presioná 0"
            ), {"step": "main"}
        if t in {"5", "nutricion", "nutrición", "15", "1.5"}:
            return _turno_derivacion("Nutrición", "Lic. Escandell Macarena", "Miércoles · con anticipación"), {"step": "main"}
        if t in {"6", "terapia ocupacional", "16", "1.6"}:
            return _turno_derivacion("Terapia Ocupacional", "Lic. Reina Lucila", "Día/horario a convenir"), {"step": "main"}
        if t in {"7", "psicologia", "psicología", "17", "1.7"}:
            return _turno_derivacion("Psicología", "Lic. Figoli Lucila", "Lunes y Viernes · con anticipación"), {"step": "main"}
        if t in {"8", "pediatria", "pediatría", "18", "1.8"}:
            return _turno_derivacion("Pediatría", "Dr. Taborda Guillermo", "Lunes/Miércoles/Viernes 11:30–12:30 · orden de llegada"), {"step": "main"}

    if step == "turnos_11":
        if t == "1":
            return _turno_derivacion("Clínica Médica", "Dra. Gómez Vanesa", "Martes 09:00–11:00 · orden de llegada"), {"step": "main"}
        if t == "2":
            return _turno_derivacion("Clínica Médica", "Dr. Aramayo Alejandro", "Miércoles 09:30–12:30 · orden de llegada"), {"step": "main"}
        if t == "3":
            return _turno_derivacion("Clínica Médica", "Dra. Sánchez Teresa", "L/J/V 11:00–13:30 · turnos por teléfono"), {"step": "main"}

    return None, s


def waha_headers():
    h = {}
    if WAHA_API_KEY:
        h["X-API-KEY"] = WAHA_API_KEY
    return h


def evo_headers():
    h = {}
    if EVOLUTION_API_KEY:
        h["apikey"] = EVOLUTION_API_KEY
    return h


async def waha_get(path: str):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(f"{WAHA_URL}{path}", headers=waha_headers())
        r.raise_for_status()
        return r


async def waha_post(path: str, payload: dict):
    async with httpx.AsyncClient(timeout=25) as c:
        r = await c.post(f"{WAHA_URL}{path}", headers=waha_headers(), json=payload)
        r.raise_for_status()
        return r


async def evo_get(path: str):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(f"{EVOLUTION_URL}{path}", headers=evo_headers())
        r.raise_for_status()
        return r


async def evo_instance_info() -> dict[str, Any]:
    try:
        r = await evo_get("/instance/fetchInstances")
        arr = r.json() if isinstance(r.json(), list) else []
        for i in arr:
            if i.get("name") == EVOLUTION_INSTANCE:
                return i
        return {"name": EVOLUTION_INSTANCE, "connectionStatus": "not_found"}
    except Exception as e:
        return {"name": EVOLUTION_INSTANCE, "connectionStatus": "error", "error": str(e)}


def _extract_qr_from_any(data: dict) -> bytes | None:
    for k in ["qrcode", "qr", "base64", "code"]:
        val = data.get(k)
        if isinstance(val, str) and val:
            if val.startswith("data:image"):
                val = val.split(",", 1)[1]
            try:
                return base64.b64decode(val)
            except Exception:
                pass
    for parent in ["qrcode", "qrCode", "data"]:
        obj = data.get(parent)
        if isinstance(obj, dict):
            for k in ["base64", "qr", "code"]:
                val = obj.get(k)
                if isinstance(val, str) and val:
                    if val.startswith("data:image"):
                        val = val.split(",", 1)[1]
                    try:
                        return base64.b64decode(val)
                    except Exception:
                        pass
    return None


async def evolution_qr_bytes() -> bytes | None:
    # 1) try direct connect endpoint
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{EVOLUTION_URL}/instance/connect/{EVOLUTION_INSTANCE}", headers=evo_headers())
            if r.status_code < 400:
                ctype = r.headers.get("content-type", "")
                if "image" in ctype:
                    _evo_qr_cache["png"] = r.content
                    _evo_qr_cache["updated_at"] = int(time.time())
                    return r.content
                if "json" in ctype:
                    b = _extract_qr_from_any(r.json())
                    if b:
                        _evo_qr_cache["png"] = b
                        _evo_qr_cache["updated_at"] = int(time.time())
                        return b
    except Exception:
        pass

    # 2) force refresh and retry connect
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            await c.post(f"{EVOLUTION_URL}/instance/restart/{EVOLUTION_INSTANCE}", headers=evo_headers())
            await asyncio.sleep(1.2)
            r2 = await c.get(f"{EVOLUTION_URL}/instance/connect/{EVOLUTION_INSTANCE}", headers=evo_headers())
            if r2.status_code < 400 and "json" in r2.headers.get("content-type", ""):
                b = _extract_qr_from_any(r2.json())
                if b:
                    _evo_qr_cache["png"] = b
                    _evo_qr_cache["updated_at"] = int(time.time())
                    return b
    except Exception:
        pass

    if _evo_qr_cache.get("png") and int(time.time()) - int(_evo_qr_cache.get("updated_at", 0)) < 600:
        return _evo_qr_cache.get("png")
    return None


async def waha_session_info() -> dict[str, Any]:
    # Try multiple WAHA endpoints depending on version
    candidates = [
        f"/api/sessions/{WAHA_SESSION}",
        "/api/sessions",
        f"/api/{WAHA_SESSION}",
    ]
    for p in candidates:
        try:
            r = await waha_get(p)
            data = r.json()
            if isinstance(data, dict):
                if data.get("name") == WAHA_SESSION or data.get("session") == WAHA_SESSION:
                    return data
                if "sessions" in data and isinstance(data["sessions"], list):
                    for s in data["sessions"]:
                        if s.get("name") == WAHA_SESSION:
                            return s
                return data
            if isinstance(data, list):
                for s in data:
                    if s.get("name") == WAHA_SESSION:
                        return s
                if data:
                    return data[0]
        except Exception:
            continue
    return {"name": WAHA_SESSION, "status": "unknown"}


async def waha_qr_bytes() -> bytes | None:
    candidates = [
        f"/api/{WAHA_SESSION}/auth/qr?format=image",
        f"/api/sessions/{WAHA_SESSION}/qr",
        f"/api/{WAHA_SESSION}/qr",
    ]
    for p in candidates:
        try:
            r = await waha_get(p)
            ctype = r.headers.get("content-type", "")
            if "image" in ctype:
                return r.content
            data = r.json()
            b = _extract_qr_from_any(data if isinstance(data, dict) else {})
            if b:
                return b
        except Exception:
            continue
    return None


async def ollama_reply(user_text: str) -> str:
    system = (
        "Sos el asistente oficial de una clínica en WhatsApp. "
        "Respondé en español rioplatense, claro, breve y prolijo.\n"
        "Reglas de formato OBLIGATORIAS para WhatsApp:\n"
        "1) Usá texto simple y legible, con emojis útiles (1-4 por mensaje).\n"
        "2) NO uses markdown de links tipo [texto](url).\n"
        "3) Si hay link, escribilo plano: https://wa.me/...\n"
        "4) Para resaltar, usá *negrita* solo en títulos cortos.\n"
        "5) Usá bullets con '•' y líneas cortas.\n"
        "6) Cerrá con una pregunta breve de continuidad.\n"
        "7) Nunca inventes horarios/coberturas/precios.\n\n"
        "Plantilla recomendada:\n"
        "[emoji] *Título*\n"
        "• Horario: ...\n"
        "• Teléfono: ...\n"
        "• WhatsApp: ...\n"
        "• Link directo: https://wa.me/...\n\n"
        "BASE DE CONOCIMIENTO:\n" + kb_text()
    )
    body = {
        "model": runtime_ollama_model(),
        "stream": False,
        "system": system,
        "prompt": user_text,
        "options": {"temperature": 0.2, "num_ctx": 8192},
    }
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{runtime_ollama_url()}/api/generate", json=body)
        r.raise_for_status()
        return r.json().get("response", "Estoy procesando tu consulta.").strip()


async def send_whatsapp_text(chat_id: str, text: str):
    payloads = [
        ("/api/sendText", {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
        (f"/api/{WAHA_SESSION}/sendText", {"chatId": chat_id, "text": text}),
        ("/api/messages/text", {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
    ]
    last_err = None
    for path, pl in payloads:
        try:
            await waha_post(path, pl)
            return
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed send whatsapp text: {last_err}")


async def send_alert_email(subject: str, body: str):
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REFRESH_TOKEN and ALERT_EMAIL_TO):
        return

    async with httpx.AsyncClient(timeout=30) as c:
        tr = await c.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": GOOGLE_REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
        )
        tr.raise_for_status()
        access = tr.json()["access_token"]

        msg = MIMEText(body, "plain", "utf-8")
        msg["to"] = ALERT_EMAIL_TO
        msg["from"] = ALERT_EMAIL_FROM or ALERT_EMAIL_TO
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        sr = await c.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={"Authorization": f"Bearer {access}"},
            json={"raw": raw},
        )
        sr.raise_for_status()


async def monitor_loop():
    while True:
        try:
            info = await waha_session_info()
            s = str(info).lower()
            connected = any(x in s for x in ["working", "connected", "authenticated", "open"]) and "qr" not in s
            prev = _last_status["connected"]
            _last_status["connected"] = connected

            if prev is True and connected is False:
                now = int(time.time())
                if now - _last_status["last_alert_at"] > 300:
                    _last_status["last_alert_at"] = now
                    await send_alert_email(
                        "[ALERTA] WhatsApp bot desconectado",
                        "El bot de clínica se desconectó. Reescanear QR desde el panel web.",
                    )
        except Exception:
            pass
        await asyncio.sleep(30)


def is_admin(req: Request) -> bool:
    if req.cookies.get(ADMIN_COOKIE, "") != "1":
        return False
    try:
        last = int(req.cookies.get(ADMIN_LAST_ACTIVE_COOKIE, "0"))
    except Exception:
        return False
    if int(time.time()) - last > runtime_admin_idle_timeout_sec():
        return False
    return True


@app.on_event("startup")
async def startup():
    asyncio.create_task(monitor_loop())


@app.get("/health")
async def health():
    info = await waha_session_info()
    return {
        "ok": True,
        "provider": "waha",
        "instance": WAHA_SESSION,
        "info": info,
        "ollama": runtime_ollama_url(),
        "model": runtime_ollama_model(),
    }


@app.get("/status")
async def status():
    info = await waha_session_info()
    s = str(info).lower()
    connected = any(x in s for x in ["working", "connected", "authenticated", "open"]) and "qr" not in s
    qr = await waha_qr_bytes() if not connected else None
    _last_status["connected"] = connected
    safe_info = {
        "name": info.get("name", WAHA_SESSION),
        "status": info.get("status") or info.get("state") or info.get("session", {}).get("status"),
    }
    return {
        "provider": "waha",
        "instance": WAHA_SESSION,
        "connected": connected,
        "has_qr": qr is not None,
        "paused": _bot_paused,
        "info": safe_info,
    }


@app.get("/qr")
async def qr():
    b = await waha_qr_bytes()
    if not b:
        raise HTTPException(404, "QR not available")
    return Response(content=b, media_type="image/png")


@app.get("/", response_class=HTMLResponse)
async def page():
    return """
    <html>
    <head>
      <meta charset='utf-8'/>
      <meta name='viewport' content='width=device-width, initial-scale=1'/>
      <title>Clinic Bot Console</title>
      <style>
        body{font-family:Inter,Arial;background:#0b1020;color:#e9eeff;margin:0;padding:20px}
        .wrap{max-width:1000px;margin:auto}
        .card{background:#131a36;border:1px solid #2a376f;border-radius:12px;padding:16px;margin-bottom:14px}
        .row{display:flex;gap:12px;flex-wrap:wrap}
        .pill{padding:6px 10px;border-radius:999px;background:#22306a;display:inline-block}
        a{color:#9dc1ff}
        img{max-width:320px;border:1px solid #2a376f;border-radius:8px}
      </style>
    </head>
    <body>
      <div class='wrap'>
        <h2>Clinic WhatsApp Bot Console</h2>
        <div class='card'>
          <div id='st'>Cargando estado...</div>
          <div class='row' style='margin-top:8px'>
            <a href='/status' target='_blank'>JSON status</a>
            <a href='/admin'>Admin menú</a>
            <button onclick='act("pause")'>⏸️ Pausar bot</button>
            <button onclick='act("resume")'>▶️ Reanudar bot</button>
            <button onclick='act("logout")'>🚪 Cerrar sesión WhatsApp</button>
          </div>
        </div>
        <div class='card'>
          <h3>QR de reconexión (real)</h3>
          <div id='qrWrap'>Cargando...</div>
        </div>
      </div>
      <script>
        async function load(){
          const s = await fetch('/status').then(r=>r.json());
          const ok = s.connected;
          document.getElementById('st').innerHTML = `
            <div><b>Provider:</b> ${s.provider}</div>
            <div><b>Instancia:</b> ${s.instance}</div>
            <div><b>Estado:</b> <span class='pill'>${ok?'🟢 Conectado':'🔴 Desconectado'}</span></div>
            <div><b>Bot:</b> <span class='pill'>${s.paused?'⏸️ Pausado':'▶️ Activo'}</span></div>
          `;
          const q = document.getElementById('qrWrap');
          if(!ok){
            if(s.has_qr){
              q.innerHTML = `<img src='/qr?ts=${Date.now()}'/><p>Escaneá este QR desde el WhatsApp del bot.</p>`;
            } else {
              q.innerHTML = `<p>Aún no llegó QR desde la API. Reintentando automáticamente...</p>`;
            }
          }else{
            q.innerHTML = '<p>Conectado. QR no requerido.</p>';
          }
        }
        async function act(kind){
          await fetch('/bot/' + kind, {method:'POST'});
          await load();
        }
        load();
        setInterval(load, 7000);
      </script>
    </body>
    </html>
    """


@app.get('/menu')
async def get_menu():
    return {'menu': kb_text()}


@app.post('/bot/pause')
async def bot_pause():
    global _bot_paused
    _bot_paused = True
    return {'ok': True, 'paused': _bot_paused}


@app.post('/bot/resume')
async def bot_resume():
    global _bot_paused
    _bot_paused = False
    return {'ok': True, 'paused': _bot_paused}


@app.post('/bot/logout')
async def bot_logout_whatsapp():
    # try stop/logout session against WAHA
    tries = [
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/stop", {}),
        ("POST", f"{WAHA_URL}/api/sessions/stop", {"name": WAHA_SESSION}),
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/logout", {}),
    ]
    async with httpx.AsyncClient(timeout=20) as c:
        for method, url, payload in tries:
            try:
                r = await c.request(method, url, headers=waha_headers(), json=payload)
                if r.status_code < 400:
                    return {'ok': True, 'status': r.status_code}
            except Exception:
                pass
    return {'ok': False}


@app.get('/admin', response_class=HTMLResponse)
async def admin(req: Request):
    if not is_admin(req):
        return """
        <html><body style='font-family:Inter,Arial;padding:20px;background:#0b1020;color:#e9eeff'>
          <h2>Admin login</h2>
          <p>Ingresá la contraseña de configuración. La sesión expira por inactividad.</p>
          <form id='f' method='post' action='/admin/login'>
            <input id='p' style='padding:8px;border-radius:8px' type='password' name='password' placeholder='Contraseña' />
            <button style='padding:8px 12px;border-radius:8px' type='submit'>Entrar</button>
          </form>
        </body></html>
        """

    txt = kb_text().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html = f"""
    <html><body style='font-family:Inter,Arial;padding:20px;background:#0b1020;color:#e9eeff'>
      <h2>Admin · Clínica Bot</h2>
      <p style='opacity:.85'>Sesión admin activa (expira por inactividad en {runtime_admin_idle_timeout_sec()//60} min).</p>
      <p>
        <a style='color:#9dc1ff' href='/admin/evolution'>Panel WhatsApp (operador)</a>
        &nbsp;|&nbsp;
        <a style='color:#9dc1ff' href='/status' target='_blank'>Status JSON</a>
        &nbsp;|&nbsp;
        <a style='color:#9dc1ff' href='/admin/logout'>Salir</a>
      </p>
      <h3>⚙️ Runtime IA</h3>
      <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;max-width:900px'>
        <input id='ou' placeholder='Ollama URL' style='padding:8px;border-radius:8px'/>
        <div>
          <input id='om' placeholder='Modelo' style='padding:8px;border-radius:8px;width:100%'/>
          <select id='oms' style='padding:8px;border-radius:8px;margin-top:6px;width:100%' onchange='pickModel()'></select>
        </div>
        <input id='mt' placeholder='Título del menú (ej: Clínica / Centro Médico / Farmacia)' style='padding:8px;border-radius:8px;grid-column:1 / span 2'/>
      </div>
      <div style='margin-top:8px'>
        <label>⏱️ Timeout admin (seg): <input id='to' type='number' min='60' step='30' style='padding:6px;border-radius:8px;width:120px'/></label>
      </div>
      <div style='margin-top:8px'>
        <button onclick='saveRuntime()' style='padding:8px 12px;border-radius:8px'>Guardar runtime</button>
        <button onclick='checkRuntime()' style='padding:8px 12px;border-radius:8px'>Verificar conexión</button>
        <span id='rt'></span>
      </div>

      <h3>🔐 Seguridad admin</h3>
      <div style='display:flex;gap:8px;flex-wrap:wrap;align-items:center'>
        <input id='np' type='password' placeholder='Nueva contraseña admin' style='padding:8px;border-radius:8px;min-width:260px'/>
        <button onclick='savePass()' style='padding:8px 12px;border-radius:8px'>Cambiar contraseña</button>
        <span id='ps'></span>
      </div>

      <h3>🧾 Editor de menú</h3>
      <textarea id='m' style='width:100%;height:58vh;background:#131a36;color:#e9eeff;border:1px solid #2a376f;border-radius:10px;padding:10px'>{txt}</textarea><br/>
      <button onclick='cancelEdit()' style='padding:8px 12px;border-radius:8px'>Cancelar</button>
      <button onclick='save()' style='padding:8px 12px;border-radius:8px'>Guardar</button>
      <span id='s'></span>
      <script>
      let original = document.getElementById('m').value;
      function cancelEdit(){{ document.getElementById('m').value = original; document.getElementById('s').innerText='Cancelado'; }}
      async function save(){{
        const r=await fetch('/admin/menu/save',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{menu:document.getElementById('m').value}})}});
        if(r.ok){{ original=document.getElementById('m').value; document.getElementById('s').innerText='Guardado ✅'; }}
        else {{ document.getElementById('s').innerText='Error'; }}
      }}
      async function loadRuntime(){{
        const r = await fetch('/admin/runtime');
        const j = await r.json();
        document.getElementById('ou').value = j.ollama_url || '';
        document.getElementById('om').value = j.ollama_model || '';
        document.getElementById('to').value = j.admin_idle_timeout_sec || 900;
        document.getElementById('mt').value = j.menu_title || 'Clínica';
        await loadModels();
      }}
      async function loadModels(){{
        const r = await fetch('/admin/runtime/models');
        const j = await r.json();
        const sel = document.getElementById('oms');
        const models = j.models || [];
        sel.innerHTML = models.length ? models.map(m=>`<option value='${{m.name}}'>${{m.name}}</option>`).join('') : `<option value=''>Sin modelos detectados</option>`;
      }}
      function pickModel(){{
        const v = document.getElementById('oms').value;
        if(v) document.getElementById('om').value = v;
      }}
      async function saveRuntime(){{
        const r = await fetch('/admin/runtime', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{ollama_url:document.getElementById('ou').value, ollama_model:document.getElementById('om').value, admin_idle_timeout_sec:Number(document.getElementById('to').value||900), menu_title:document.getElementById('mt').value}})}});
        document.getElementById('rt').innerText = r.ok ? 'Guardado ✅' : 'Error';
      }}
      async function checkRuntime(){{
        const r = await fetch('/admin/runtime/check');
        const j = await r.json();
        document.getElementById('rt').innerText = j.ok ? `Conectado ✅ (${{j.models}} modelos)` : ('Error ❌ ' + (j.error || ''));
      }}
      async function savePass(){{
        const p=document.getElementById('np').value||'';
        const r=await fetch('/admin/password', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{password:p}})}});
        document.getElementById('ps').innerText = r.ok ? 'Contraseña actualizada ✅' : 'Error';
      }}
      loadRuntime();
      </script>
    </body></html>
    """
    resp = HTMLResponse(html)
    now = str(int(time.time()))
    resp.set_cookie(ADMIN_COOKIE, "1", httponly=True, max_age=runtime_admin_idle_timeout_sec())
    resp.set_cookie(ADMIN_LAST_ACTIVE_COOKIE, now, httponly=True, max_age=runtime_admin_idle_timeout_sec())
    return resp


@app.post('/admin/login')
async def admin_login(req: Request):
    from urllib.parse import parse_qs
    from fastapi.responses import RedirectResponse
    raw = (await req.body()).decode('utf-8', errors='ignore')
    pwd = parse_qs(raw).get('password', [''])[0]
    if pwd != runtime_admin_password():
        raise HTTPException(401, 'invalid password')
    now = str(int(time.time()))
    resp = RedirectResponse(url='/admin', status_code=303)
    resp.set_cookie(ADMIN_COOKIE, "1", httponly=True, max_age=runtime_admin_idle_timeout_sec())
    resp.set_cookie(ADMIN_LAST_ACTIVE_COOKIE, now, httponly=True, max_age=runtime_admin_idle_timeout_sec())
    return resp


@app.get('/admin/logout')
async def admin_logout():
    from fastapi.responses import RedirectResponse
    resp = RedirectResponse(url='/', status_code=303)
    resp.delete_cookie(ADMIN_COOKIE)
    resp.delete_cookie(ADMIN_LAST_ACTIVE_COOKIE)
    return resp


@app.post('/admin/password')
async def set_admin_password(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    body = await req.json()
    newp = str(body.get('password', '')).strip()
    if len(newp) < 6:
        raise HTTPException(400, 'password too short')
    cfg = load_runtime_cfg()
    cfg['admin_password'] = newp
    save_runtime_cfg(cfg)
    return {'ok': True}


@app.post('/admin/menu/save')
async def set_menu_admin(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    body = await req.json()
    text = body.get('menu', '')
    save_kb_text(text)
    return {'ok': True, 'bytes': len(text)}


@app.get('/admin/runtime')
async def get_runtime(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    cfg = load_runtime_cfg()
    return {
        'ollama_url': cfg.get('ollama_url', OLLAMA_URL),
        'ollama_model': cfg.get('ollama_model', OLLAMA_MODEL),
        'admin_idle_timeout_sec': runtime_admin_idle_timeout_sec(),
        'menu_title': cfg.get('menu_title', 'Clínica'),
    }


@app.post('/admin/runtime')
async def set_runtime(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    body = await req.json()
    cfg = load_runtime_cfg()
    if body.get('ollama_url'):
        cfg['ollama_url'] = str(body.get('ollama_url')).strip()
    if body.get('ollama_model'):
        cfg['ollama_model'] = str(body.get('ollama_model')).strip()
    if body.get('admin_idle_timeout_sec') is not None:
        try:
            cfg['admin_idle_timeout_sec'] = max(60, int(body.get('admin_idle_timeout_sec')))
        except Exception:
            pass
    if body.get('menu_title') is not None:
        t = str(body.get('menu_title')).strip()
        cfg['menu_title'] = t if t else 'Clínica'
    save_runtime_cfg(cfg)
    return {'ok': True, 'cfg': cfg}


@app.get('/admin/runtime/models')
async def runtime_models(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    url = runtime_ollama_url()
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(f"{url}/api/tags")
            r.raise_for_status()
            data = r.json()
            return {'ok': True, 'models': data.get('models', [])}
    except Exception as e:
        return {'ok': False, 'models': [], 'error': str(e)}


@app.get('/admin/runtime/check')
async def check_runtime(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    url = runtime_ollama_url()
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(f"{url}/api/tags")
            r.raise_for_status()
            data = r.json()
            models = len(data.get('models', []))
            return {'ok': True, 'models': models, 'url': url}
    except Exception as e:
        return {'ok': False, 'url': url, 'error': str(e)}


@app.get('/admin/evolution', response_class=HTMLResponse)
async def admin_evolution(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    html = """
    <html><body style='font-family:Inter,Arial;padding:20px;background:#0b1020;color:#e9eeff'>
      <h2>Admin · WhatsApp (WAHA)</h2>
      <p><a style='color:#9dc1ff' href='/admin'>← Volver</a></p>
      <div style='display:flex;gap:8px;flex-wrap:wrap'>
        <button onclick='action("connect")' style='padding:8px 12px;border-radius:8px'>Forzar connect</button>
        <button onclick='action("restart")' style='padding:8px 12px;border-radius:8px'>Restart instancia</button>
        <button onclick='reload()' style='padding:8px 12px;border-radius:8px'>Refrescar estado</button>
      </div>
      <pre id='st' style='background:#131a36;border:1px solid #2a376f;padding:10px;margin-top:10px;border-radius:10px'></pre>
      <h3>QR actual</h3>
      <div id='qr'>Cargando...</div>
      <script>
      async function reload(){
        const s = await fetch('/status').then(r=>r.json());
        document.getElementById('st').textContent = JSON.stringify(s, null, 2);
        if(!s.connected){
          if(s.has_qr){
            document.getElementById('qr').innerHTML = `<img src='/qr?ts=${Date.now()}' style='max-width:360px;border:1px solid #2a376f;border-radius:8px'/>`;
          } else {
            document.getElementById('qr').innerHTML = 'Sin QR por API todavía. Usá "Forzar connect" y refrescá.';
          }
        } else {
          document.getElementById('qr').innerHTML = 'Conectado ✅';
        }
      }
      async function action(kind){
        await fetch('/admin/evolution/' + kind, {method:'POST'});
        await reload();
      }
      reload();
      setInterval(reload, 7000);
      </script>
    </body></html>
    """
    resp = HTMLResponse(html)
    now = str(int(time.time()))
    resp.set_cookie(ADMIN_COOKIE, "1", httponly=True, max_age=runtime_admin_idle_timeout_sec())
    resp.set_cookie(ADMIN_LAST_ACTIVE_COOKIE, now, httponly=True, max_age=runtime_admin_idle_timeout_sec())
    return resp


@app.post('/admin/evolution/connect')
async def admin_evo_connect(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    # keep route path for compatibility, but action runs against WAHA
    tries = [
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start", {}),
        ("POST", f"{WAHA_URL}/api/sessions/start", {"name": WAHA_SESSION}),
        ("POST", f"{WAHA_URL}/api/{WAHA_SESSION}/start", {}),
    ]
    last = None
    async with httpx.AsyncClient(timeout=20) as c:
        for method, url, payload in tries:
            try:
                r = await c.request(method, url, headers=waha_headers(), json=payload)
                if r.status_code < 400:
                    return {"ok": True, "status": r.status_code, "body": r.text[:500]}
                last = f"{r.status_code}: {r.text[:120]}"
            except Exception as e:
                last = str(e)
    return {"ok": False, "error": last}


@app.post('/admin/evolution/restart')
async def admin_evo_restart(req: Request):
    if not is_admin(req):
        raise HTTPException(401, 'unauthorized')
    # keep route path for compatibility, but action runs against WAHA
    steps = [
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/stop", {}),
        ("POST", f"{WAHA_URL}/api/sessions/stop", {"name": WAHA_SESSION}),
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start", {}),
        ("POST", f"{WAHA_URL}/api/sessions/start", {"name": WAHA_SESSION}),
    ]
    results = []
    async with httpx.AsyncClient(timeout=20) as c:
        for method, url, payload in steps:
            try:
                r = await c.request(method, url, headers=waha_headers(), json=payload)
                results.append({"url": url, "status": r.status_code})
            except Exception as e:
                results.append({"url": url, "error": str(e)})
    ok = any(x.get("status", 500) < 400 for x in results)
    return {"ok": ok, "results": results}


@app.post('/evolution/webhook')
async def evolution_webhook(req: Request):
    data = await req.json()
    # capture QR from events when Evolution emits it
    b = _extract_qr_from_any(data if isinstance(data, dict) else {})
    if b:
        _evo_qr_cache['png'] = b
        _evo_qr_cache['updated_at'] = int(time.time())

    # mirror to n8n if configured
    if N8N_EVENT_WEBHOOK:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                await c.post(N8N_EVENT_WEBHOOK, json={"source": "evolution", "payload": data})
        except Exception:
            pass
    return {"ok": True, "qr_cached": b is not None}


@app.post('/webhook')
async def webhook(req: Request):
    data = await req.json()

    # fire-and-forget event mirror to n8n
    if N8N_EVENT_WEBHOOK:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                await c.post(N8N_EVENT_WEBHOOK, json={"source": "waha", "payload": data})
        except Exception:
            pass

    if _bot_paused:
        return {"ok": True, "paused": True}

    msg = data.get("payload") or data.get("message") or data
    chat_id = msg.get("from") or msg.get("chatId") or msg.get("chat_id")
    text = msg.get("body") or msg.get("text") or (msg.get("message") if isinstance(msg.get("message"), str) else None)

    if not chat_id or not text:
        return {"ok": True, "ignored": True}

    now_ts = int(time.time())
    state = _chat_state.get(chat_id, {"step": "main", "last_ts": now_ts})

    # reset flow if user was idle for too long
    if now_ts - int(state.get("last_ts", now_ts)) > CHAT_IDLE_RESET_SEC:
        state = {"step": "main", "last_ts": now_ts}
        # if user says anything after timeout, show fresh main menu
        if (text or "").strip().lower() not in {"0", "menu", "menú", "inicio", "hola"}:
            await send_whatsapp_text(chat_id, "⏱️ Reiniciamos la conversación por inactividad.\n\n" + menu_main())
            _chat_state[chat_id] = {"step": "main", "last_ts": now_ts}
            return {"ok": True, "reset": True}

    templated, new_state = menu_response(text, state)
    new_state["last_ts"] = now_ts
    _chat_state[chat_id] = new_state

    if templated:
        answer = templated
    else:
        answer = await ollama_reply(text)

    await send_whatsapp_text(chat_id, answer)
    return {"ok": True}
