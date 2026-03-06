"""
WA-BOT - Sistema de chatbot WhatsApp con handoff a operador
Basado en especificaciones WAHA-DOC.md:
  - Menú automático multinivel
  - Opción 99: transferir a operador humano (12h)
  - Opción 98: volver al bot
  - En modo humano: IGNORAR mensajes (no responder, no sendSeen)
"""
import asyncio
import base64
import calendar
import json
import os
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from sqlalchemy.orm import Session

from database import init_db, get_db, SessionLocal, engine
from models import Base, User, BotConfig, Holiday, HolidayMenu, WhatsAppBlockList, ConversationState
from schemas import (
    UserLogin, UserCreate, UserResponse, TokenResponse, BotConfigUpdate,
    BotConfigResponse, HolidayCreate, HolidayResponse, HolidayMenuCreate,
    HolidayMenuResponse, PasswordChangeRequest, PasswordResetRequest, UserUpdate
)
from security import hash_password, verify_password, create_access_token, get_current_user, get_current_admin
from pages import get_login_page, get_dashboard_page, get_user_panel_page, get_user_config_page

# ──────────────────────────────────────────────────────────────
#  CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────
PORT            = int(os.getenv("PORT", "8088"))
WAHA_URL        = os.getenv("WAHA_URL", "http://waha:3000")
WAHA_API_KEY    = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION    = os.getenv("WAHA_SESSION", "default")
OLLAMA_URL      = os.getenv("OLLAMA_URL", "http://10.1.1.39:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "lfm2:latest")
CLINIC_KB_PATH  = os.getenv("CLINIC_KB_PATH", "/app/data/MenuP.MD")
N8N_EVENT_WEBHOOK = os.getenv("N8N_EVENT_WEBHOOK", "")
GOOGLE_CLIENT_ID      = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET  = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN  = os.getenv("GOOGLE_REFRESH_TOKEN", "")
ALERT_EMAIL_TO  = os.getenv("ALERT_EMAIL_TO", "")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", ALERT_EMAIL_TO)
SOLUTION_NAME   = os.getenv("SOLUTION_NAME", "Clínica")
CHAT_IDLE_RESET_SEC = int(os.getenv("CHAT_IDLE_RESET_SEC", "180"))

# ──────────────────────────────────────────────────────────────
#  ESTADO GLOBAL (en memoria)
# ──────────────────────────────────────────────────────────────
_bot_paused   = False
_chat_nav: dict[str, dict] = {}   # estado de navegación por chat
_chats_today: set[str] = set()
_chats_date   = None
_last_status  = {"connected": None, "last_alert_at": 0}

# ──────────────────────────────────────────────────────────────
#  APP
# ──────────────────────────────────────────────────────────────
app = FastAPI(title="WA-BOT", version="2.1.2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────
#  STARTUP
# ──────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(_init_defaults())
    asyncio.create_task(_monitor_loop())

async def _init_defaults():
    await asyncio.sleep(1)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.is_admin == True).first():
            db.add(User(
                username="admin", email="admin@clinic.local",
                hashed_password=hash_password("admin123"),
                full_name="Administrador", is_admin=True, is_active=True
            ))
            print("[INIT] Admin creado: admin / admin123")
        if not db.query(User).filter(User.username == "usuario").first():
            db.add(User(
                username="usuario", email="usuario@clinic.local",
                hashed_password=hash_password("usuario123"),
                full_name="Usuario", is_admin=False, is_active=True
            ))
            print("[INIT] Usuario creado: usuario / usuario123")
        if not db.query(BotConfig).first():
            db.add(BotConfig(
                solution_name=SOLUTION_NAME, menu_title=SOLUTION_NAME,
                opening_time="08:00", closing_time="16:00",
                off_hours_enabled=True,
                ollama_url=OLLAMA_URL, ollama_model=OLLAMA_MODEL,
                admin_idle_timeout_sec=900
            ))
            print("[INIT] Config por defecto creada")
        db.commit()
    except Exception as e:
        print(f"[INIT] Error: {e}")
        db.rollback()
    finally:
        db.close()

async def _monitor_loop():
    while True:
        try:
            info = await _waha_session_info()
            s = str(info).lower()
            connected = any(x in s for x in ["working", "connected", "authenticated"]) and "qr" not in s
            prev = _last_status["connected"]
            _last_status["connected"] = connected
            if prev is True and not connected:
                now = int(time.time())
                if now - _last_status["last_alert_at"] > 300:
                    _last_status["last_alert_at"] = now
                    await _send_alert_email(
                        "[ALERTA] WhatsApp desconectado",
                        "El bot se desconectó. Reescanear QR desde el panel web."
                    )
        except Exception:
            pass
        await asyncio.sleep(30)

# ──────────────────────────────────────────────────────────────
#  HELPERS - ARCHIVOS
# ──────────────────────────────────────────────────────────────
def _data_path(filename: str) -> str:
    if os.path.isabs(filename):
        return filename
    if os.path.exists("/app/data"):
        return os.path.join("/app/data", filename)
    return os.path.join(os.path.dirname(__file__), "data", filename)

def _read_menu() -> str:
    try:
        with open(CLINIC_KB_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def _write_menu(text: str):
    with open(CLINIC_KB_PATH, "w", encoding="utf-8") as f:
        f.write(text)

# ──────────────────────────────────────────────────────────────
#  HELPERS - WAHA
# ──────────────────────────────────────────────────────────────
def _waha_headers() -> dict:
    return {"X-API-Key": WAHA_API_KEY} if WAHA_API_KEY else {}

async def _waha_get(path: str):
    async with httpx.AsyncClient(timeout=20) as c:
        return await c.get(f"{WAHA_URL}{path}", headers=_waha_headers())

async def _waha_post(path: str, data: dict):
    async with httpx.AsyncClient(timeout=20) as c:
        return await c.post(f"{WAHA_URL}{path}", json=data, headers=_waha_headers())

async def _waha_session_info() -> dict:
    for p in [f"/api/sessions/{WAHA_SESSION}", "/api/sessions"]:
        try:
            r = await _waha_get(p)
            d = r.json()
            if isinstance(d, dict) and d.get("name") == WAHA_SESSION:
                return d
            if isinstance(d, list):
                for s in d:
                    if s.get("name") == WAHA_SESSION:
                        return s
                if d: return d[0]
            if isinstance(d, dict):
                return d
        except Exception:
            pass
    return {"name": WAHA_SESSION, "status": "unknown"}

async def _waha_qr() -> bytes | None:
    """Tries multiple WAHA QR endpoints. Returns PNG bytes or None."""
    paths = [
        f"/api/{WAHA_SESSION}/auth/qr?format=image",
        f"/api/sessions/{WAHA_SESSION}/auth/qr?format=image",
        f"/api/{WAHA_SESSION}/auth/qr",
        f"/api/sessions/{WAHA_SESSION}/qr",
    ]
    for p in paths:
        try:
            r = await _waha_get(p)
            ct = r.headers.get("content-type", "")
            if "image" in ct:
                return r.content
            # Some WAHA versions return JSON with base64 value
            if "json" in ct:
                data = r.json()
                raw = data.get("value") or data.get("data") or data.get("qr")
                if raw and isinstance(raw, str):
                    # Strip possible data URL prefix
                    if "," in raw:
                        raw = raw.split(",", 1)[1]
                    return base64.b64decode(raw)
        except Exception:
            pass
    return None

async def _send_wha(chat_id: str, text: str):
    """Envía texto por WhatsApp. Solo llamar desde flujo BOT, nunca en human mode."""
    if not text or not text.strip():
        print(f"[SEND] Bloqueado - texto vacío para {chat_id}")
        return
    print(f"[SEND] → {chat_id}: {text[:80]}")
    for path, payload in [
        ("/api/sendText",                 {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
        (f"/api/{WAHA_SESSION}/sendText", {"chatId": chat_id, "text": text}),
        ("/api/messages/text",            {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
    ]:
        try:
            r = await _waha_post(path, payload)
            if r.status_code < 400:
                print(f"[SEND] OK via {path}")
                return
        except Exception as e:
            print(f"[SEND] Error en {path}: {e}")
    print(f"[SEND] FALLIDO para {chat_id}")

# ──────────────────────────────────────────────────────────────
#  HELPERS - EMAIL
# ──────────────────────────────────────────────────────────────
async def _send_alert_email(subject: str, body: str):
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REFRESH_TOKEN and ALERT_EMAIL_TO):
        return
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            tr = await c.post("https://oauth2.googleapis.com/token", data={
                "client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": GOOGLE_REFRESH_TOKEN, "grant_type": "refresh_token",
            })
            access = tr.json()["access_token"]
            msg = MIMEText(body, "plain", "utf-8")
            msg["to"] = ALERT_EMAIL_TO
            msg["from"] = ALERT_EMAIL_FROM or ALERT_EMAIL_TO
            msg["subject"] = subject
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            await c.post("https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                         headers={"Authorization": f"Bearer {access}"}, json={"raw": raw})
    except Exception as e:
        print(f"[EMAIL] Error: {e}")

# ──────────────────────────────────────────────────────────────
#  HELPERS - CONFIG
# ──────────────────────────────────────────────────────────────
def _get_cfg(db: Session) -> BotConfig:
    cfg = db.query(BotConfig).first()
    if not cfg:
        cfg = BotConfig(solution_name=SOLUTION_NAME, menu_title=SOLUTION_NAME,
                        opening_time="08:00", closing_time="16:00")
        db.add(cfg); db.commit()
    return cfg

def _is_off_hours(db: Session) -> bool:
    import pytz
    cfg = _get_cfg(db)
    if not cfg.off_hours_enabled:
        return False
    try:
        tz = pytz.timezone(cfg.timezone or "America/Argentina/Buenos_Aires")
    except Exception:
        tz = pytz.UTC
    now = datetime.now(tz)
    if db.query(Holiday).filter(Holiday.date == now.strftime("%Y-%m-%d")).first():
        return True
    t = now.strftime("%H:%M")
    dow = now.weekday()
    if dow >= 5:
        o, c = cfg.sat_opening_time or "10:00", cfg.sat_closing_time or "14:00"
    else:
        o, c = cfg.opening_time or "08:00", cfg.closing_time or "16:00"
    off = t < o or t > c
    print(f"[HOURS] {now.strftime('%A %H:%M')} | {o}-{c} | fuera={off}")
    return off

# ──────────────────────────────────────────────────────────────
#  HUMAN MODE  (WAHA-DOC §5, §8, §9, §11)
#
#  Todas las operaciones leen/escriben directo a la BD.
#  NO se usa caché para evitar inconsistencias.
# ──────────────────────────────────────────────────────────────
def _is_human_mode(db: Session, chat_id: str) -> bool:
    """True si el chat está en modo operador activo (no expirado)."""
    row = db.query(ConversationState).filter(
        ConversationState.phone_number == chat_id
    ).first()
    if not row or not row.human_mode or row.human_mode_expire is None:
        return False

    expire = row.human_mode_expire
    now_utc = datetime.utcnow()

    # Comparación segura: convertir a timestamp Unix para evitar
    # problemas entre datetime naive y aware según el driver de BD.
    try:
        exp_ts = calendar.timegm(expire.timetuple())
        now_ts = calendar.timegm(now_utc.timetuple())
        active = exp_ts > now_ts
    except Exception:
        active = True   # conservador: asumir activo ante error

    if not active:
        # Expiró → limpiar automáticamente (WAHA-DOC §11)
        row.human_mode = False
        row.human_mode_expire = None
        row.handoff_active = False
        row.current_state = "BOT_MENU"
        db.commit()
        print(f"[HUMAN] Expirado para {chat_id} → bot")
    return active

def _start_human_mode(db: Session, chat_id: str) -> str:
    """Activa modo humano por 12h. Retorna ticket_id."""
    import uuid
    row = db.query(ConversationState).filter(
        ConversationState.phone_number == chat_id
    ).first()
    if not row:
        row = ConversationState(phone_number=chat_id)
        db.add(row)
    ticket = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    row.human_mode         = True
    row.human_mode_expire  = datetime.utcnow() + timedelta(hours=12)
    row.current_state      = "WAITING_AGENT"
    row.handoff_active     = True
    row.handoff_started_at = datetime.utcnow()
    row.ticket_id          = ticket
    row.last_message_at    = datetime.utcnow()
    db.commit()
    print(f"[HUMAN] Activado {chat_id} | ticket={ticket} | expire={row.human_mode_expire}")
    return ticket

def _exit_human_mode(db: Session, chat_id: str):
    """Desactiva modo humano (opción 98)."""
    row = db.query(ConversationState).filter(
        ConversationState.phone_number == chat_id
    ).first()
    if row:
        row.human_mode        = False
        row.human_mode_expire = None
        row.handoff_active    = False
        row.current_state     = "BOT_MENU"
        row.last_message_at   = datetime.utcnow()
        db.commit()
        print(f"[HUMAN] Desactivado {chat_id}")

# ──────────────────────────────────────────────────────────────
#  MENU  (navegación jerárquica Markdown)
# ──────────────────────────────────────────────────────────────
def _menu_main() -> str:
    """Devuelve el bloque inicial del menú (hasta primer ---)."""
    lines = _read_menu().split("\n")
    out = []
    for ln in lines:
        out.append(ln)
        if ln.startswith("---"):
            break
    return "\n".join(out).strip()

def _menu_nav(choice: str, section: str) -> tuple[str, str]:
    """Navega la jerarquía de menú. Devuelve (respuesta, nueva_seccion)."""
    if not choice.isdigit():
        return "", section   # texto libre → silent ignore

    lines   = _read_menu().split("\n")
    path    = [] if section == "main" else section.replace("menu_", "").split("_")
    npath   = path + [choice]
    marker  = ".".join(npath)
    depth   = len(npath) + 1
    hpfx    = "#" * depth + " "

    for i, ln in enumerate(lines):
        if not ln.startswith(hpfx):
            continue
        if not ln[depth:].strip().startswith(marker):
            continue
        # Sección encontrada — extraer hasta el próximo heading del mismo nivel
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if lines[j].startswith("#") and not lines[j].startswith("#" * (depth + 1)):
                end = j; break
        chunk = []
        for j in range(i, end):
            if j > i and lines[j].startswith("#" * (depth + 1) + " "):
                break
            chunk.append(lines[j])
        while chunk and not chunk[-1].strip():
            chunk.pop()
        return "\n".join(chunk).strip(), f"menu_{'_'.join(npath)}"

    return f"❌ Opción {choice} no disponible. Escribe *0* para volver al menú.", section

# ──────────────────────────────────────────────────────────────
#  WEBHOOK  — motor del bot (WAHA-DOC §3, §5, §8, §9)
# ──────────────────────────────────────────────────────────────
@app.post("/webhook")
async def webhook(req: Request, db: Session = Depends(get_db)):
    global _bot_paused, _chat_nav, _chats_today, _chats_date

    # 1. Parsear payload ─────────────────────────────────────────
    data = await req.json()
    msg     = data.get("payload") or data.get("message") or data
    chat_id = (msg.get("from") or msg.get("chatId") or msg.get("chat_id") or "").strip()
    raw_txt = msg.get("body") or msg.get("text") or ""
    if not isinstance(raw_txt, str):
        raw_txt = ""
    text = raw_txt.strip()

    print(f"[WH] chat={chat_id!r} text={text!r}")

    # 2. Filtros de ruido ────────────────────────────────────────
    if msg.get("fromMe"):
        return {"ok": True, "i": "from_me"}
    if not chat_id or not text:
        return {"ok": True, "i": "empty"}
    if any(x in chat_id for x in ("status@", "@status", "broadcast")):
        return {"ok": True, "i": "status"}
    if "@g.us" in chat_id:
        return {"ok": True, "i": "group"}
    if text.lower() in {"estado", "estados", "status"}:
        return {"ok": True, "i": "status_text"}

    # 3. Bot pausado ─────────────────────────────────────────────
    if _bot_paused:
        return {"ok": True, "paused": True}

    # 4. Contador diario ─────────────────────────────────────────
    from datetime import date as _d
    today = str(_d.today())
    if _chats_date != today:
        _chats_today = set(); _chats_date = today
    _chats_today.add(chat_id)

    # 5. HUMAN MODE ──────────────────────────────────────────────
    #
    #  WAHA-DOC §8: si mode == "human" && expire > now → ignorar.
    #  WAHA-DOC §9: NO ejecutar sendSeen.
    #  WAHA-DOC §14: opción 98 permite salir.
    #
    in_human = _is_human_mode(db, chat_id)
    print(f"[WH] human_mode={in_human}")

    if in_human:
        if text == "98":
            # WAHA-DOC §14: "98 volver al bot"
            _exit_human_mode(db, chat_id)
            _chat_nav.pop(chat_id, None)
            await _send_wha(chat_id,
                "✅ *Volviste al menú automático.*\n\n"
                "Escribe *0* para ver el menú principal.")
        else:
            # WAHA-DOC §9: NO responder, NO sendSeen
            print(f"[WH] HUMAN_MODE activo → ignorando '{text}'")
        return {"ok": True, "status": "human_mode"}

    # 6. Opción 98 fuera de human mode → silencio ────────────────
    if text == "98":
        print(f"[WH] 98 sin human_mode activo → ignorar")
        return {"ok": True, "i": "98_outside_human"}

    # 7. Opción 99: activar modo humano ──────────────────────────
    #  WAHA-DOC §5: guardar estado HUMAN, enviar mensaje, suspender bot.
    if text == "99":
        ticket = _start_human_mode(db, chat_id)
        _chat_nav.pop(chat_id, None)
        await _send_wha(chat_id,
            "📞 *Se ha iniciado transferencia a un operador*\n\n"
            f"✅ Tu número de ticket: *{ticket}*\n\n"
            "⏳ Por favor espera a que un operario se comunique contigo.\n"
            "Esto generalmente toma unos minutos.\n\n"
            "Gracias por tu paciencia 😊\n\n"
            "_(Escribe *98* en cualquier momento para volver al menú automático)_"
        )
        return {"ok": True, "status": "handoff", "ticket": ticket}

    # 8. Filtros de acceso ───────────────────────────────────────
    cfg = _get_cfg(db)

    if db.query(WhatsAppBlockList).filter(WhatsAppBlockList.phone_number == chat_id).first():
        return {"ok": True, "blocked": True}

    if cfg.country_filter_enabled and cfg.country_codes:
        codes = [c.strip() for c in cfg.country_codes.split(",")]
        if not any(chat_id.startswith(c) for c in codes):
            return {"ok": True, "filtered": "country"}

    if cfg.area_filter_enabled and cfg.area_codes:
        areas = [a.strip() for a in cfg.area_codes.split(",")]
        if not any(a in chat_id for a in areas):
            return {"ok": True, "filtered": "area"}

    # 9. Flujo normal del bot ────────────────────────────────────
    now_ts = int(time.time())
    nav    = _chat_nav.get(chat_id, {"section": "main", "ts": now_ts, "new": True})

    # Resetear si inactivo demasiado tiempo
    if now_ts - nav.get("ts", now_ts) > CHAT_IDLE_RESET_SEC:
        nav = {"section": "main", "ts": now_ts, "new": True}

    answer = ""

    # 9a. Fuera de horario
    if _is_off_hours(db):
        p = _data_path("MenuF.MD")
        try:
            with open(p, "r", encoding="utf-8") as f:
                answer = f.read()
        except Exception:
            m = db.query(HolidayMenu).filter(HolidayMenu.is_active == True).first()
            answer = m.content if m else (cfg.off_hours_message or "🕐 Estamos fuera de horario.")

    # 9b. Primera visita o timeout → menú principal
    elif nav.get("new") or text == "0":
        answer = _menu_main()
        nav["section"] = "main"
        nav["new"] = False

    # 9c. Navegar menú
    else:
        answer, new_section = _menu_nav(text, nav.get("section", "main"))
        nav["section"] = new_section

    nav["ts"] = now_ts
    _chat_nav[chat_id] = nav

    if answer:
        await _send_wha(chat_id, answer)

    return {"ok": True}


# ──────────────────────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────────────────────
@app.post("/api/auth/register")
async def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Usuario ya existe")
    u = User(username=data.username, email=data.email,
             hashed_password=hash_password(data.password),
             full_name=data.full_name, is_admin=data.is_admin, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    tk = create_access_token({"sub": u.username, "is_admin": u.is_admin})
    return TokenResponse(access_token=tk, token_type="bearer", user=UserResponse.from_orm(u))

@app.post("/api/auth/login")
async def login(creds: UserLogin, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == creds.username).first()
    if not u or not verify_password(creds.password, u.hashed_password):
        raise HTTPException(401, "Credenciales inválidas")
    if not u.is_active:
        raise HTTPException(403, "Usuario inactivo")
    u.last_login = datetime.utcnow(); db.commit(); db.refresh(u)
    tk = create_access_token({"sub": u.username, "is_admin": u.is_admin})
    return TokenResponse(access_token=tk, token_type="bearer", user=UserResponse.from_orm(u))

@app.get("/api/auth/me")
async def get_me(cu=Depends(get_current_user), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == cu["username"]).first()
    if not u: raise HTTPException(404, "No encontrado")
    return UserResponse.from_orm(u)

@app.post("/api/auth/change-password")
async def change_password(req: PasswordChangeRequest, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == cu["username"]).first()
    if not verify_password(req.old_password, u.hashed_password):
        raise HTTPException(401, "Contraseña incorrecta")
    u.hashed_password = hash_password(req.new_password); db.commit()
    return {"ok": True}

# ──────────────────────────────────────────────────────────────
#  ADMIN
# ──────────────────────────────────────────────────────────────
@app.get("/api/admin/users")
async def list_users(ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    return [UserResponse.from_orm(u) for u in db.query(User).all()]

@app.post("/api/admin/users")
async def create_user(data: UserCreate, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Ya existe")
    u = User(username=data.username, email=data.email,
             hashed_password=hash_password(data.password),
             full_name=data.full_name, is_admin=data.is_admin, is_active=True)
    db.add(u); db.commit(); db.refresh(u)
    return UserResponse.from_orm(u)

@app.put("/api/admin/users/{uid}")
async def update_user(uid: int, data: UserUpdate, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == uid).first()
    if not u: raise HTTPException(404, "No encontrado")
    if data.email: u.email = data.email
    if data.full_name: u.full_name = data.full_name
    if data.password: u.hashed_password = hash_password(data.password)
    if data.is_active is not None: u.is_active = data.is_active
    db.commit()
    return UserResponse.from_orm(u)

@app.delete("/api/admin/users/{uid}")
async def delete_user(uid: int, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == uid).first()
    if not u: raise HTTPException(404, "No encontrado")
    if u.is_admin and db.query(User).filter(User.is_admin == True).count() <= 1:
        raise HTTPException(400, "No se puede eliminar el único admin")
    db.delete(u); db.commit()
    return {"ok": True}

@app.post("/api/admin/users/{uid}/reset-password")
async def reset_pw(uid: int, req: PasswordResetRequest, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == uid).first()
    if not u: raise HTTPException(404, "No encontrado")
    u.hashed_password = hash_password(req.new_password); db.commit()
    return {"ok": True}

@app.post("/api/admin/users/{uid}/toggle-pause")
async def toggle_pause(uid: int, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == uid).first()
    if not u: raise HTTPException(404, "No encontrado")
    u.is_paused = not u.is_paused; db.commit()
    return {"ok": True, "user": UserResponse.from_orm(u)}

# ──────────────────────────────────────────────────────────────
#  BOT CONFIG
# ──────────────────────────────────────────────────────────────
@app.get("/api/config")
async def get_config(db: Session = Depends(get_db)):
    cfg = _get_cfg(db)
    r = BotConfigResponse.from_orm(cfg).model_dump()
    for key, fname in [("menu_content", "MenuP.MD"), ("off_hours_message", "MenuF.MD")]:
        p = _data_path(fname)
        r[key] = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    return r

@app.put("/api/config")
async def update_config(data: BotConfigUpdate, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    cfg = _get_cfg(db)
    for f in ["solution_name","menu_title","opening_time","closing_time","sat_opening_time",
              "sat_closing_time","off_hours_enabled","off_hours_message","country_filter_enabled",
              "country_codes","area_filter_enabled","area_codes","ollama_url","ollama_model",
              "admin_idle_timeout_sec"]:
        v = getattr(data, f, None)
        if v is not None: setattr(cfg, f, v)
    db.commit(); db.refresh(cfg)
    return BotConfigResponse.from_orm(cfg)

@app.put("/api/config/menu")
async def update_menu_file(req: Request, ca=Depends(get_current_admin)):
    body = await req.json(); content = body.get("content", "")
    if not content.strip(): raise HTTPException(400, "Vacío")
    p = _data_path("MenuP.MD"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    return {"ok": True, "bytes": len(content)}

@app.put("/api/config/offhours")
async def update_offhours_file(req: Request, ca=Depends(get_current_admin)):
    body = await req.json(); content = body.get("content", "")
    if not content.strip(): raise HTTPException(400, "Vacío")
    p = _data_path("MenuF.MD"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    return {"ok": True, "bytes": len(content)}

# ──────────────────────────────────────────────────────────────
#  HOLIDAYS
# ──────────────────────────────────────────────────────────────
@app.get("/api/holidays")
async def list_holidays(db: Session = Depends(get_db)):
    return [HolidayResponse.from_orm(h) for h in db.query(Holiday).all()]

@app.post("/api/holidays")
async def create_holiday(data: HolidayCreate, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Holiday).filter(Holiday.date == data.date).first():
        raise HTTPException(400, "Feriado ya existe")
    h = Holiday(date=data.date, name=data.name, description=data.description)
    db.add(h); db.commit(); db.refresh(h)
    return HolidayResponse.from_orm(h)

@app.delete("/api/holidays/{hid}")
async def delete_holiday(hid: int, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(Holiday).filter(Holiday.id == hid).first()
    if not h: raise HTTPException(404, "No encontrado")
    db.delete(h); db.commit()
    return {"ok": True}

# ──────────────────────────────────────────────────────────────
#  HOLIDAY MENUS
# ──────────────────────────────────────────────────────────────
@app.get("/api/holiday-menus")
async def list_hmenus(db: Session = Depends(get_db)):
    return [HolidayMenuResponse.from_orm(m) for m in db.query(HolidayMenu).all()]

@app.post("/api/holiday-menus")
async def create_hmenu(data: HolidayMenuCreate, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    m = HolidayMenu(name=data.name, content=data.content)
    db.add(m); db.commit(); db.refresh(m)
    return HolidayMenuResponse.from_orm(m)

@app.put("/api/holiday-menus/{mid}")
async def update_hmenu(mid: int, data: HolidayMenuCreate, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    m = db.query(HolidayMenu).filter(HolidayMenu.id == mid).first()
    if not m: raise HTTPException(404, "No encontrado")
    m.name = data.name; m.content = data.content; db.commit(); db.refresh(m)
    return HolidayMenuResponse.from_orm(m)

@app.delete("/api/holiday-menus/{mid}")
async def delete_hmenu(mid: int, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    m = db.query(HolidayMenu).filter(HolidayMenu.id == mid).first()
    if not m: raise HTTPException(404, "No encontrado")
    db.delete(m); db.commit()
    return {"ok": True}

# ──────────────────────────────────────────────────────────────
#  BLOCKLIST
# ──────────────────────────────────────────────────────────────
@app.get("/api/blocklist")
async def list_blocklist(cu=Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": b.id, "phone_number": b.phone_number, "reason": b.reason,
             "blocked_at": b.blocked_at} for b in db.query(WhatsAppBlockList).all()]

@app.post("/api/blocklist")
async def add_blocklist(req: Request, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    body = await req.json(); phone = body.get("phone_number")
    if not phone: raise HTTPException(400, "phone_number requerido")
    if db.query(WhatsAppBlockList).filter(WhatsAppBlockList.phone_number == phone).first():
        raise HTTPException(400, "Ya bloqueado")
    b = WhatsAppBlockList(phone_number=phone, reason=body.get("reason", ""))
    db.add(b); db.commit(); db.refresh(b)
    return {"ok": True, "id": b.id}

@app.delete("/api/blocklist/{bid}")
async def del_blocklist(bid: int, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(WhatsAppBlockList).filter(WhatsAppBlockList.id == bid).first()
    if not b: raise HTTPException(404, "No encontrado")
    db.delete(b); db.commit()
    return {"ok": True}

# ──────────────────────────────────────────────────────────────
#  BOT CONTROL
# ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"ok": True, "provider": "waha", "instance": WAHA_SESSION}

@app.get("/version")
async def version():
    return {"version": "2.1.2", "name": "WA-BOT"}

@app.get("/status")
async def status(cu=Depends(get_current_user), db: Session = Depends(get_db)):
    info = await _waha_session_info()
    s = str(info).lower()
    eng = info.get("engine", {})
    eng_state = str(eng.get("state", "")).lower() if isinstance(eng, dict) else ""
    connected = eng_state == "connected" and info.get("me") is not None and "qr" not in s
    qr = await _waha_qr() if not connected else None
    cfg = _get_cfg(db)
    return {
        "provider": "waha", "instance": WAHA_SESSION,
        "connected": connected, "has_qr": qr is not None,
        "paused": _bot_paused,
        "solution_name": cfg.solution_name,
        "off_hours": _is_off_hours(db),
        "chats_today": len(_chats_today),
        "info": {"name": info.get("name", WAHA_SESSION), "status": info.get("status")},
    }

@app.get("/qr")
async def qr_image():
    b = await _waha_qr()
    if not b: raise HTTPException(404, "QR no disponible")
    return Response(content=b, media_type="image/png")

@app.get("/api/debug/status")
async def debug_status(cu=Depends(get_current_user)):
    return {"raw_info": await _waha_session_info()}

@app.post("/bot/pause")
async def bot_pause(cu=Depends(get_current_user)):
    global _bot_paused; _bot_paused = True
    return {"ok": True, "paused": True}

@app.post("/bot/resume")
async def bot_resume(cu=Depends(get_current_user)):
    global _bot_paused; _bot_paused = False
    return {"ok": True, "paused": False}

async def _waha_delete_and_recreate() -> bool:
    """DELETE session + POST to recreate fresh → forces QR generation."""
    async with httpx.AsyncClient(timeout=20) as c:
        try:
            rd = await c.delete(
                f"{WAHA_URL}/api/sessions/{WAHA_SESSION}",
                headers=_waha_headers()
            )
            print(f"[CONNECT] DELETE session: {rd.status_code}")
        except Exception as e:
            print(f"[CONNECT] DELETE error (ok to ignore): {e}")

        await asyncio.sleep(2)  # let WAHA clean up before recreating

        try:
            r = await c.post(
                f"{WAHA_URL}/api/sessions",
                headers=_waha_headers(),
                json={"name": WAHA_SESSION, "start": True}
            )
            print(f"[CONNECT] create session: {r.status_code}")
            if r.status_code < 400:
                await asyncio.sleep(3)  # give WAHA time to boot QR
                return True
        except Exception as e:
            print(f"[CONNECT] create error: {e}")

        # Fallback: restart
        try:
            r = await c.post(
                f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/restart",
                headers=_waha_headers(), json={}
            )
            print(f"[CONNECT] restart fallback: {r.status_code}")
            if r.status_code < 400:
                await asyncio.sleep(3)
                return True
        except Exception as e:
            print(f"[CONNECT] restart fallback error: {e}")
    return False


@app.post("/bot/connect")
async def bot_connect(cu=Depends(get_current_user)):
    info = await _waha_session_info()
    status_str = str(info.get("status", "")).upper()
    print(f"[CONNECT] session status: {status_str}")

    # STARTING → WAHA is booting, wait a moment and check for QR
    if status_str == "STARTING":
        await asyncio.sleep(4)
        return {"ok": True, "status": status_str}

    # SCAN_QR_CODE → QR might already be valid, but could be expired.
    # Check if QR image is actually retrievable; if not, force a new one.
    if status_str == "SCAN_QR_CODE":
        qr_bytes = await _waha_qr()
        if qr_bytes:
            print(f"[CONNECT] QR already available, reusing")
            return {"ok": True, "status": status_str}
        # QR expired → force new session
        print(f"[CONNECT] SCAN_QR_CODE but QR expired → recreating session")
        ok = await _waha_delete_and_recreate()
        return {"ok": ok, "status": "recreated"}

    # WORKING → simple restart (keeps stored auth, just reconnects)
    if status_str == "WORKING":
        async with httpx.AsyncClient(timeout=15) as c:
            try:
                r = await c.post(
                    f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/restart",
                    headers=_waha_headers(), json={}
                )
                print(f"[CONNECT] restart (working): {r.status_code}")
                return {"ok": r.status_code < 400}
            except Exception as e:
                print(f"[CONNECT] restart error: {e}")
                return {"ok": False}

    # FAILED or any other state → DELETE + recreate fresh (generates QR)
    ok = await _waha_delete_and_recreate()
    return {"ok": ok}

@app.post("/bot/logout")
async def bot_logout(cu=Depends(get_current_user)):
    """Logout: DELETE session from WAHA (clears auth) then recreate stopped."""
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.delete(
                f"{WAHA_URL}/api/sessions/{WAHA_SESSION}",
                headers=_waha_headers()
            )
            print(f"[LOGOUT] DELETE session: {r.status_code}")
            return {"ok": r.status_code < 400}
        except Exception as e:
            print(f"[LOGOUT] error: {e}")
    return {"ok": False}

# ──────────────────────────────────────────────────────────────
#  MENÚ (compatibilidad legacy)
# ──────────────────────────────────────────────────────────────
@app.get("/menu")
async def get_menu():
    return {"menu": _read_menu()}

@app.post("/menu/save")
async def save_menu_legacy(req: Request, ca=Depends(get_current_admin)):
    body = await req.json(); _write_menu(body.get("menu", ""))
    return {"ok": True}

@app.post("/api/menu-action")
async def menu_action(req: Request, ca=Depends(get_current_admin)):
    body = await req.json()
    return {"ok": True, "action_id": body.get("action_id"), "status": "pending"}

# ──────────────────────────────────────────────────────────────
#  PÁGINAS WEB
# ──────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root(): return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(): return get_login_page()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(): return get_dashboard_page()

@app.get("/user-panel", response_class=HTMLResponse)
async def user_panel_page(): return get_user_panel_page()

@app.get("/user-config", response_class=HTMLResponse)
async def user_config_page(): return get_user_config_page()

# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
