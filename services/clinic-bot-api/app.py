import asyncio
import base64
import os
import time
import json
from email.mime.text import MIMEText
from typing import Any, Optional
from datetime import datetime, timedelta

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importar módulos del proyecto
from database import init_db, get_db, SessionLocal, engine
from models import Base, User, BotConfig, CountryFilter, Holiday, HolidayMenu, WhatsAppBlockList
from schemas import (
    UserLogin, UserCreate, UserResponse, TokenResponse, BotConfigUpdate,
    BotConfigResponse, HolidayCreate, HolidayResponse, HolidayMenuCreate,
    HolidayMenuResponse, PasswordChangeRequest, PasswordResetRequest
)
from security import (
    hash_password, verify_password, create_access_token, get_current_user,
    get_current_admin, decode_token
)
from pages import get_login_page, get_dashboard_page, get_user_panel_page

# ======================== CONFIG =========================
PORT = int(os.getenv("PORT", "8088"))
WAHA_URL = os.getenv("WAHA_URL", "http://waha:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://10.1.1.10:8089")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "clinic-bot")
EVOLUTION_MANAGER_URL = os.getenv("EVOLUTION_MANAGER_URL", "http://10.1.1.10:8089/manager/")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://10.1.1.39:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lfm2:latest")

CLINIC_KB_PATH = os.getenv("CLINIC_KB_PATH", "/app/data/MenuP.MD")
RUNTIME_CFG_PATH = os.getenv("RUNTIME_CFG_PATH", "/app/data/runtime_config.json")
N8N_EVENT_WEBHOOK = os.getenv("N8N_EVENT_WEBHOOK", "")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", ALERT_EMAIL_TO)

SOLUTION_NAME = os.getenv("SOLUTION_NAME", "Clínica")

# Estado global
_last_status = {"connected": None, "last_alert_at": 0}
_evo_qr_cache = {"png": None, "updated_at": 0}
_bot_paused = False
_chat_state: dict[str, dict] = {}
_chats_today: set[str] = set()  # Chats únicos de hoy
_chats_date = None  # Fecha de los chats actuales
CHAT_IDLE_RESET_SEC = int(os.getenv("CHAT_IDLE_RESET_SEC", "180"))

# ======================== FASTAPI APP =========================
app = FastAPI(
    title="WA-BOT",
    version="1.0.1",
    description="Sistema integral de chatbot WhatsApp con gestión de usuarios y administración"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar BD
@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(monitor_loop())
    asyncio.create_task(init_default_admin())
    asyncio.create_task(ensure_waha_session())

async def init_default_admin():
    """Crear usuarios admin y usuario por defecto si no existen"""
    await asyncio.sleep(1)
    db = SessionLocal()
    try:
        # Crear admin si no existe
        admin = db.query(User).filter(User.is_admin == True).first()
        if not admin:
            default_admin = User(
                username="admin",
                email="admin@clinic.local",
                hashed_password=hash_password("admin123"),
                full_name="Administrador",
                is_admin=True,
                is_active=True
            )
            db.add(default_admin)
            print("✅ Admin creado. Usuario: admin, Contraseña: admin123")
        
        # Crear usuario regular si no existe
        user = db.query(User).filter(User.username == "usuario").first()
        if not user:
            default_user = User(
                username="usuario",
                email="usuario@clinic.local",
                hashed_password=hash_password("usuario123"),
                full_name="Usuario",
                is_admin=False,
                is_active=True
            )
            db.add(default_user)
            print("✅ Usuario creado. Usuario: usuario, Contraseña: usuario123")
            
        # Crear config por defecto
        cfg = db.query(BotConfig).first()
        if not cfg:
            default_config = BotConfig(
                solution_name=SOLUTION_NAME,
                menu_title=SOLUTION_NAME,
                opening_time="08:00",
                closing_time="16:00",
                off_hours_enabled=False,
                ollama_url=OLLAMA_URL,
                ollama_model=OLLAMA_MODEL,
                admin_idle_timeout_sec=900
            )
            db.add(default_config)
        
        db.commit()
    except Exception as e:
        print(f"⚠️ Error al crear usuarios por defecto: {e}")
    finally:
        db.close()

async def ensure_waha_session():
    """Asegurar que la sesión de WAHA esté iniciada"""
    await asyncio.sleep(3)  # Esperar a que WAHA esté listo
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            headers = {"X-API-Key": WAHA_API_KEY}
            # Verificar estado de la sesión
            resp = await client.get(f"{WAHA_URL}/api/sessions/{WAHA_SESSION}", headers=headers)
            if resp.status_code == 200:
                session_data = resp.json()
                status = session_data.get("status", "")
                print(f"[STARTUP] Sesión WAHA status: {status}")
                
                # Si no está WORKING, intentar iniciarla
                if status not in ["WORKING", "STARTING"]:
                    print(f"[STARTUP] Iniciando sesión WAHA {WAHA_SESSION}...")
                    start_resp = await client.post(
                        f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start",
                        headers=headers,
                        json={}
                    )
                    if start_resp.status_code in [200, 201]:
                        print(f"[STARTUP] ✅ Sesión WAHA iniciada correctamente")
                    else:
                        print(f"[STARTUP] ⚠️ Error al iniciar sesión: {start_resp.status_code}")
            else:
                print(f"[STARTUP] ⚠️ No se pudo verificar sesión WAHA: {resp.status_code}")
    except Exception as e:
        print(f"[STARTUP] ⚠️ Error en ensure_waha_session: {e}")


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
        with open(RUNTIME_CFG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_runtime_cfg(cfg: dict):
    os.makedirs(os.path.dirname(RUNTIME_CFG_PATH), exist_ok=True)
    with open(RUNTIME_CFG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def waha_headers() -> dict:
    return {"X-API-Key": WAHA_API_KEY} if WAHA_API_KEY else {}

def evo_headers() -> dict:
    return {"Authorization": f"Bearer {EVOLUTION_API_KEY}"} if EVOLUTION_API_KEY else {}

async def waha_get(path: str):
    async with httpx.AsyncClient(timeout=20) as c:
        return await c.get(f"{WAHA_URL}{path}", headers=waha_headers())

async def waha_post(path: str, data: dict):
    print(f"[WAHA_POST] POST {WAHA_URL}{path}")
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(f"{WAHA_URL}{path}", json=data, headers=waha_headers())
            print(f"[WAHA_POST] Respuesta status: {r.status_code}")
            return r
    except Exception as e:
        print(f"[WAHA_POST] Error: {e}")
        raise

def _extract_qr_from_any(obj: Any) -> bytes | None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in {"qr", "qr_code", "qrcode"} and isinstance(v, str):
                try:
                    return base64.b64decode(v)
                except Exception:
                    pass
    return None

# ======================== WHATSAPP SESSION =========================
async def waha_session_info() -> dict[str, Any]:
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

# ======================== BOT LOGIC =========================
def get_bot_config(db: Session) -> BotConfig:
    cfg = db.query(BotConfig).first()
    if not cfg:
        cfg = BotConfig(
            solution_name=SOLUTION_NAME,
            menu_title=SOLUTION_NAME,
            opening_time="08:00",
            closing_time="16:00",
        )
        db.add(cfg)
        db.commit()
    return cfg

def is_off_hours(db: Session) -> bool:
    """Verificar si estamos fuera de horarios o es fin de semana/feriado"""
    cfg = get_bot_config(db)
    if not cfg.off_hours_enabled:
        return False
    
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    # Verificar si es fuera de horarios
    if cfg.opening_time and cfg.closing_time:
        if current_time < cfg.opening_time or current_time > cfg.closing_time:
            return True
    
    # Verificar si es fin de semana (5=sábado, 6=domingo)
    if now.weekday() >= 5:
        return True
    
    # Verificar si es feriado
    holiday = db.query(Holiday).filter(
        Holiday.date == now.strftime("%Y-%m-%d")
    ).first()
    if holiday:
        return True
    
    return False

async def ollama_reply(user_text: str, db: Session) -> str:
    print(f"[OLLAMA] Iniciando ollama_reply")
    cfg = get_bot_config(db)
    print(f"[OLLAMA] Config obtenida: model={cfg.ollama_model}")
    system = (
        f"Sos el asistente oficial de {cfg.solution_name} en WhatsApp. "
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
    print(f"[OLLAMA] System prompt preparado, {len(system)} chars")
    body = {
        "model": cfg.ollama_model or OLLAMA_MODEL,
        "stream": False,
        "system": system,
        "prompt": user_text,
        "options": {"temperature": 0.2, "num_ctx": 8192},
    }
    print(f"[OLLAMA] Enviando POST a {cfg.ollama_url or OLLAMA_URL}/api/generate")
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{cfg.ollama_url or OLLAMA_URL}/api/generate", json=body)
            print(f"[OLLAMA] Respuesta recibida: status={r.status_code}")
            r.raise_for_status()
            response = r.json().get("response", "Estoy procesando tu consulta.").strip()
            print(f"[OLLAMA] Response obtenida: {len(response)} chars")
            return response
    except Exception as e:
        error_msg = f"Disculpa, no puedo procesar tu consulta en este momento. Error: {str(e)[:50]}"
        print(f"[OLLAMA] Error: {e}")
        return error_msg

async def get_menu_section(user_input: str, current_section: str, db: Session) -> tuple[str, str]:
    """
    Buscar en el menú la sección correspondiente a la entrada del usuario.
    Soporta navegación multinivel: main -> menu_X -> menu_X_Y -> menu_X_Y_Z
    
    Retorna (respuesta, nueva_sección)
    """
    kb = kb_text()
    lines = kb.split('\n')
    
    # Normalizar entrada del usuario
    user_input = user_input.strip()
    
    # Si pide volver al menú (0) siempre volver al principal
    if user_input == "0":
        menu_lines = []
        for line in lines:
            menu_lines.append(line)
            if line.startswith('---'):
                break
        return '\n'.join(menu_lines).strip(), "main"
    
    # Si no es un número, rechazar
    if not user_input.isdigit():
        return "❌ Debes escribir un número o 0 para volver.", current_section
    
    # Obtener path actual como lista: menu_1_2_3 -> ['1', '2', '3']
    if current_section == "main":
        path_parts = []
    else:
        path_parts = current_section.replace("menu_", "").split("_")
    
    # Nuevo path será: path_parts + [user_input]
    new_path = path_parts + [user_input]
    expected_marker = ".".join(new_path)
    
    # Calcular el número de # basado en la profundidad
    # Profundidad 1 (menu principal) -> ##  (level 2)
    # Profundidad 2 (submenu) -> ### (level 3)
    # Profundidad 3 (sub-submenu) -> #### (level 4)
    next_level = len(new_path) + 1
    heading = "#" * next_level
    
    # Buscar la sección con el marcador esperado
    for i, line in enumerate(lines):
        # Verificar si la línea comienza con el número correcto de #
        if line.startswith(heading + " "):
            # Extraer el texto después del heading
            line_text = line[next_level:].strip()
            # Buscar si el marcador está en esta línea
            if line_text.startswith(expected_marker):
                section_start = i
                section_end = len(lines)
                
                # Buscar el final de esta sección (siguiente heading del mismo nivel o superior)
                for j in range(i + 1, len(lines)):
                    j_line = lines[j]
                    if j_line.startswith("#") and not j_line.startswith("#" * (next_level + 1)):
                        section_end = j
                        break
                
                # Extraer sección sin los sub-headings del siguiente nivel
                section_lines = []
                for j in range(section_start, section_end):
                    line = lines[j]
                    
                    # No incluir headings del siguiente nivel más profundo
                    if line.startswith("#" * (next_level + 1) + " "):
                        break
                    
                    section_lines.append(line)
                
                # Limpiar líneas vacías al final
                while section_lines and not section_lines[-1].strip():
                    section_lines.pop()
                
                new_section_id = f"menu_{'_'.join(new_path)}"
                return '\n'.join(section_lines).strip(), new_section_id
    
    # Si no encontró la sección, retornar error
    return f"❌ Opción {user_input} no disponible. Escribe 0 para volver.", current_section

async def send_whatsapp_text(chat_id: str, text: str):
    print(f"[SEND_WHA] Intentando enviar a {chat_id}: {text[:50]}...")
    payloads = [
        ("/api/sendText", {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
        (f"/api/{WAHA_SESSION}/sendText", {"chatId": chat_id, "text": text}),
        ("/api/messages/text", {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
    ]
    last_err = None
    for path, pl in payloads:
        try:
            print(f"[SEND_WHA] Intentando {path} con payload {pl}")
            result = await waha_post(path, pl)
            print(f"[SEND_WHA] Éxito con {path}: {result.status_code}")
            return
        except Exception as e:
            print(f"[SEND_WHA] Error con {path}: {e}")
            last_err = e
    print(f"[SEND_WHA] Todos los intentos fallaron: {last_err}")
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

# ======================== AUTH ENDPOINTS =========================
@app.post("/api/auth/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario (solo admin puede crear usuarios)"""
    # Verificar si el usuario ya existe
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_admin=user_data.is_admin,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token({"sub": new_user.username, "is_admin": new_user.is_admin})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )

@app.post("/api/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login de usuario"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": user.username, "is_admin": user.is_admin})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtener datos del usuario actual"""
    user = db.query(User).filter(User.username == current_user["username"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse.from_orm(user)

@app.post("/api/auth/change-password")
async def change_password(
    req: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    user = db.query(User).filter(User.username == current_user["username"]).first()
    
    if not verify_password(req.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    
    user.hashed_password = hash_password(req.new_password)
    db.commit()
    
    return {"ok": True, "message": "Contraseña actualizada"}

# ======================== ADMIN ENDPOINTS =========================
@app.get("/api/admin/users")
async def list_users(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios (solo admin)"""
    users = db.query(User).all()
    return [UserResponse.from_orm(u) for u in users]

@app.post("/api/admin/users")
async def create_user(
    user_data: UserCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario (solo admin)"""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        is_admin=user_data.is_admin,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)

@app.put("/api/admin/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar un usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.email = user_data.email
    user.full_name = user_data.full_name
    user.is_admin = user_data.is_admin
    if user_data.password:
        user.hashed_password = hash_password(user_data.password)
    
    db.commit()
    return UserResponse.from_orm(user)

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar un usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Prevenir eliminar el único admin
    if user.is_admin:
        admin_count = db.query(User).filter(User.is_admin == True).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="No puedes eliminar el único admin")
    
    db.delete(user)
    db.commit()
    
    return {"ok": True, "message": "Usuario eliminado"}

@app.post("/api/admin/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    req: PasswordResetRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Resetear contraseña de un usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.hashed_password = hash_password(req.new_password)
    db.commit()
    
    return {"ok": True, "message": "Contraseña reseteada"}

@app.post("/api/admin/users/{user_id}/toggle-pause")
async def toggle_user_pause(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Pausar/reanudar acceso de usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.is_paused = not user.is_paused
    db.commit()
    
    return {"ok": True, "user": UserResponse.from_orm(user)}

# ======================== BOT CONFIG ENDPOINTS =========================
@app.get("/api/config")
async def get_config(db: Session = Depends(get_db)):
    """Obtener configuración del bot"""
    import os
    cfg = get_bot_config(db)
    
    # Leer menús desde archivos
    menu_content = ""
    if os.path.exists('data/MenuP.MD'):
        with open('data/MenuP.MD', 'r', encoding='utf-8') as f:
            menu_content = f.read()
    
    offhours_content = ""
    if os.path.exists('data/MenuF.MD'):
        with open('data/MenuF.MD', 'r', encoding='utf-8') as f:
            offhours_content = f.read()
    
    # Convertir a diccionario y agregar contenidos
    result = BotConfigResponse.from_orm(cfg)
    result_dict = result.model_dump()
    result_dict['menu_content'] = menu_content
    result_dict['off_hours_message'] = offhours_content
    
    return result_dict

@app.put("/api/config")
async def update_config(
    config_data: BotConfigUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar configuración del bot (solo admin)"""
    cfg = get_bot_config(db)
    
    if config_data.solution_name:
        cfg.solution_name = config_data.solution_name
    if config_data.menu_title:
        cfg.menu_title = config_data.menu_title
    if config_data.opening_time:
        cfg.opening_time = config_data.opening_time
    if config_data.closing_time:
        cfg.closing_time = config_data.closing_time
    if config_data.sat_opening_time:
        cfg.sat_opening_time = config_data.sat_opening_time
    if config_data.sat_closing_time:
        cfg.sat_closing_time = config_data.sat_closing_time
    if config_data.off_hours_enabled is not None:
        cfg.off_hours_enabled = config_data.off_hours_enabled
    if config_data.off_hours_message:
        cfg.off_hours_message = config_data.off_hours_message
    if config_data.country_filter_enabled is not None:
        cfg.country_filter_enabled = config_data.country_filter_enabled
    if config_data.country_codes:
        cfg.country_codes = config_data.country_codes
    if config_data.area_filter_enabled is not None:
        cfg.area_filter_enabled = config_data.area_filter_enabled
    if config_data.area_codes:
        cfg.area_codes = config_data.area_codes
    if config_data.ollama_url:
        cfg.ollama_url = config_data.ollama_url
    if config_data.ollama_model:
        cfg.ollama_model = config_data.ollama_model
    if config_data.admin_idle_timeout_sec:
        cfg.admin_idle_timeout_sec = config_data.admin_idle_timeout_sec
    
    db.commit()
    db.refresh(cfg)
    
    return BotConfigResponse.from_orm(cfg)

@app.put("/api/config/menu")
async def update_menu(
    req: Request,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar contenido del menú principal"""
    import os
    try:
        body = await req.json()
        content = body.get('content', '')
        
        if not content or not content.strip():
            return {'ok': False, 'error': 'El contenido del menú no puede estar vacío'}, 400
        
        # Crear directorio data si no existe
        os.makedirs('data', exist_ok=True)
        
        # Guardar en archivo
        with open('data/MenuP.MD', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {'ok': True, 'bytes': len(content), 'saved_to': 'data/MenuP.MD'}
    except Exception as e:
        print(f"[ERROR] en update_menu: {e}")
        return {'ok': False, 'error': str(e)}, 500

@app.put("/api/config/offhours")
async def update_offhours(
    req: Request,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar menú fuera de horario"""
    import os
    try:
        body = await req.json()
        content = body.get('content', '')
        
        if not content or not content.strip():
            return {'ok': False, 'error': 'El contenido no puede estar vacío'}, 400
        
        # Crear directorio data si no existe
        os.makedirs('data', exist_ok=True)
        
        # Guardar en archivo
        with open('data/MenuF.MD', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {'ok': True, 'bytes': len(content), 'saved_to': 'data/MenuF.MD'}
    except Exception as e:
        print(f"[ERROR] en update_offhours: {e}")
        return {'ok': False, 'error': str(e)}, 500

# ======================== HOLIDAYS ENDPOINTS =========================
@app.get("/api/holidays")
async def list_holidays(db: Session = Depends(get_db)):
    """Listar todos los feriados"""
    holidays = db.query(Holiday).all()
    return [HolidayResponse.from_orm(h) for h in holidays]

@app.post("/api/holidays")
async def create_holiday(
    holiday_data: HolidayCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear un nuevo feriado (solo admin)"""
    existing = db.query(Holiday).filter(Holiday.date == holiday_data.date).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feriado ya existe en esa fecha")
    
    holiday = Holiday(
        date=holiday_data.date,
        name=holiday_data.name,
        description=holiday_data.description
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    
    return HolidayResponse.from_orm(holiday)

@app.delete("/api/holidays/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar un feriado (solo admin)"""
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Feriado no encontrado")
    
    db.delete(holiday)
    db.commit()
    
    return {"ok": True, "message": "Feriado eliminado"}

# ======================== HOLIDAY MENUS ENDPOINTS =========================
@app.get("/api/holiday-menus")
async def list_holiday_menus(db: Session = Depends(get_db)):
    """Listar menús de fuera de horario"""
    menus = db.query(HolidayMenu).all()
    return [HolidayMenuResponse.from_orm(m) for m in menus]

@app.post("/api/holiday-menus")
async def create_holiday_menu(
    menu_data: HolidayMenuCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear menú de fuera de horario (solo admin)"""
    menu = HolidayMenu(
        name=menu_data.name,
        content=menu_data.content
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    
    return HolidayMenuResponse.from_orm(menu)

@app.put("/api/holiday-menus/{menu_id}")
async def update_holiday_menu(
    menu_id: int,
    menu_data: HolidayMenuCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar menú de fuera de horario (solo admin)"""
    menu = db.query(HolidayMenu).filter(HolidayMenu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    menu.name = menu_data.name
    menu.content = menu_data.content
    
    db.commit()
    db.refresh(menu)
    
    return HolidayMenuResponse.from_orm(menu)

@app.delete("/api/holiday-menus/{menu_id}")
async def delete_holiday_menu(
    menu_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar menú de fuera de horario (solo admin)"""
    menu = db.query(HolidayMenu).filter(HolidayMenu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    db.delete(menu)
    db.commit()
    
    return {"ok": True, "message": "Menú eliminado"}

# ======================== WHATSAPP BLOCKLIST ENDPOINTS =========================
@app.get("/api/blocklist")
async def list_blocklist(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listar números bloqueados"""
    blocked = db.query(WhatsAppBlockList).all()
    return [
        {
            "id": b.id,
            "phone_number": b.phone_number,
            "reason": b.reason,
            "blocked_at": b.blocked_at
        }
        for b in blocked
    ]

@app.post("/api/blocklist")
async def add_to_blocklist(
    req: Request,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Agregar número a blocklist"""
    try:
        body = await req.json()
        phone_number = body.get('phone_number')
        reason = body.get('reason', 'No especificado')
        
        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number requerido")
        
        # Verificar si ya existe
        existing = db.query(WhatsAppBlockList).filter(
            WhatsAppBlockList.phone_number == phone_number
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Número ya está bloqueado")
        
        block = WhatsAppBlockList(
            phone_number=phone_number,
            reason=reason
        )
        db.add(block)
        db.commit()
        db.refresh(block)
        
        return {
            "ok": True,
            "id": block.id,
            "phone_number": block.phone_number,
            "reason": block.reason,
            "blocked_at": block.blocked_at
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] en add_to_blocklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/blocklist/{block_id}")
async def remove_from_blocklist(
    block_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Remover número de blocklist"""
    block = db.query(WhatsAppBlockList).filter(WhatsAppBlockList.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Registro de bloqueo no encontrado")
    
    db.delete(block)
    db.commit()
    
    return {"ok": True, "message": "Número desbloqueado"}

# ======================== BOT CONTROL ENDPOINTS =========================
@app.get("/health")
async def health():
    info = await waha_session_info()
    return {
        "ok": True,
        "provider": "waha",
        "instance": WAHA_SESSION,
        "info": info,
    }

@app.get("/status")
async def status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estado del bot (requiere autenticación)"""
    global _chats_today
    info = await waha_session_info()
    s = str(info).lower()
    connected = any(x in s for x in ["working", "connected", "authenticated", "open"]) and "qr" not in s
    qr = await waha_qr_bytes() if not connected else None
    _last_status["connected"] = connected
    cfg = get_bot_config(db)
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
        "solution_name": cfg.solution_name,
        "off_hours": is_off_hours(db),
        "chats_today": len(_chats_today),
        "info": safe_info,
    }

@app.get("/qr")
async def qr():
    b = await waha_qr_bytes()
    if not b:
        raise HTTPException(404, "QR not available")
    return Response(content=b, media_type="image/png")

@app.post('/bot/pause')
async def bot_pause(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Pausar el bot (requiere autenticación)"""
    global _bot_paused
    _bot_paused = True
    cfg = get_bot_config(db)
    return {'ok': True, 'paused': _bot_paused}

@app.post('/bot/resume')
async def bot_resume(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Reanudar el bot (requiere autenticación)"""
    global _bot_paused
    _bot_paused = False
    cfg = get_bot_config(db)
    return {'ok': True, 'paused': _bot_paused}

@app.post('/bot/connect')
async def bot_connect_whatsapp(current_user: Optional[dict] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Iniciar conexión con WhatsApp"""
    tries = [
        # Intentar crear una nueva sesión
        ("POST", f"{WAHA_URL}/api/sessions", {
            "name": WAHA_SESSION,
            "start": True,
            "config": {}
        }),
        # O iniciar una sesión existente
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/start", {}),
        ("POST", f"{WAHA_URL}/api/sessions/{WAHA_SESSION}/restart", {}),
        # Rutas alternativas
        ("POST", f"{WAHA_URL}/api/sessions", {"name": WAHA_SESSION}),
    ]
    
    async with httpx.AsyncClient(timeout=20) as c:
        for method, url, payload in tries:
            try:
                r = await c.request(method, url, headers=waha_headers(), json=payload)
                if r.status_code < 400:
                    return {'ok': True, 'status': r.status_code, 'message': 'Conexión iniciada'}
            except Exception as e:
                print(f"Error trying {url}: {e}")
                pass
    
    return {'ok': False, 'message': 'No se pudo conectar a WAHA'}

@app.post('/bot/logout')
async def bot_logout_whatsapp(current_user: Optional[dict] = Depends(get_current_user), db: Session = Depends(get_db)):
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

# ======================== MENU ENDPOINTS =========================
@app.get('/menu')
async def get_menu(db: Session = Depends(get_db)):
    return {'menu': kb_text()}

@app.post('/menu/save')
async def save_menu(req: Request, current_admin: dict = Depends(get_current_admin)):
    body = await req.json()
    text = body.get('menu', '')
    save_kb_text(text)
    return {'ok': True, 'bytes': len(text)}

# ======================== N8N WEBHOOK BRIDGE =========================
@app.post('/api/menu-action')
async def menu_action(
    req: Request,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ejecutar una acción de menú conectada a n8n
    
    Body esperado:
    {
        "action_id": "create_appointment",
        "chat_id": "5491234567890",
        "user_data": {...},
        "context": {...}
    }
    """
    try:
        body = await req.json()
        action_id = body.get('action_id')
        chat_id = body.get('chat_id')
        user_data = body.get('user_data', {})
        context = body.get('context', {})
        
        # Buscar configuración del webhook de n8n para esta acción
        # Por ahora retornamos un placeholder para que se configure
        print(f"[N8N] Acción solicitada: {action_id} para {chat_id}")
        
        return {
            'ok': True,
            'action_id': action_id,
            'message': f'Acción {action_id} procesada',
            'status': 'pending'
        }
    except Exception as e:
        print(f"[N8N] Error: {e}")
        return {'ok': False, 'error': str(e)}, 400

# ======================== WEBHOOK (BOT MESSAGES) =========================
@app.post('/webhook')
async def webhook(req: Request, db: Session = Depends(get_db)):
    global _bot_paused, _chat_state, _chats_today, _chats_date
    
    from datetime import date
    today = str(date.today())
    
    # Resetear contador si es un día diferente
    if _chats_date != today:
        _chats_today = set()
        _chats_date = today
    
    data = await req.json()
    print(f"[WEBHOOK] Recibido: {data}")

    # Espejo a n8n si está configurado
    if N8N_EVENT_WEBHOOK:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                await c.post(N8N_EVENT_WEBHOOK, json={"source": "waha", "payload": data})
        except Exception:
            pass

    if _bot_paused:
        print(f"[WEBHOOK] Bot pausado")
        return {"ok": True, "paused": True}

    msg = data.get("payload") or data.get("message") or data
    chat_id = msg.get("from") or msg.get("chatId") or msg.get("chat_id")
    text = msg.get("body") or msg.get("text") or (msg.get("message") if isinstance(msg.get("message"), str) else None)

    print(f"[WEBHOOK] chat_id={chat_id}, text={text}, paused={_bot_paused}")
    
    if not chat_id or not text:
        print(f"[WEBHOOK] Ignorado - sin chat_id o text")
        return {"ok": True, "ignored": True}

    # Registrar chat único del día
    _chats_today.add(chat_id)

    # Obtener configuración para filtros
    cfg = get_bot_config(db)
    
    # Verificar filtros antispam
    block = db.query(WhatsAppBlockList).filter(WhatsAppBlockList.phone_number == chat_id).first()
    if block:
        return {"ok": True, "blocked": True, "reason": "Número bloqueado"}
    
    # Verificar filtro por país
    if cfg.country_filter_enabled and cfg.country_codes:
        allowed_codes = [c.strip() for c in cfg.country_codes.split(",")]
        # Extraer código de país del número (primeros caracteres después del +)
        has_allowed_code = any(chat_id.startswith(code) for code in allowed_codes)
        if not has_allowed_code:
            # Número no coincide con los códigos permitidos
            return {"ok": True, "filtered": True, "reason": "País no permitido"}
    
    # Verificar filtro por localidad/área
    if cfg.area_filter_enabled and cfg.area_codes:
        allowed_areas = [a.strip() for a in cfg.area_codes.split(",")]
        # Buscar si algún patrón de área está en el número
        has_allowed_area = any(area in chat_id for area in allowed_areas)
        if not has_allowed_area:
            # Número no coincide con las áreas permitidas
            return {"ok": True, "filtered": True, "reason": "Área no permitida"}

    now_ts = int(time.time())
    state = _chat_state.get(chat_id, {"step": "main", "section": "main", "last_ts": now_ts, "first_time": True})

    # Resetear flujo si el usuario fue inactivo demasiado tiempo
    if now_ts - int(state.get("last_ts", now_ts)) > CHAT_IDLE_RESET_SEC:
        state = {"step": "main", "section": "main", "last_ts": now_ts, "first_time": True}

    # Verificar si es fuera de horarios
    off_hours = is_off_hours(db)
    print(f"[WEBHOOK] off_hours={off_hours}")
    if off_hours:
        # Usar menú de fuera de horarios
        # Primero intentar leer MenuF.MD (archivo de fuera de horarios)
        try:
            import os
            if os.path.exists('data/MenuF.MD'):
                with open('data/MenuF.MD', 'r', encoding='utf-8') as f:
                    answer = f.read()
                    print(f"[WEBHOOK] Leyendo MenuF.MD para fuera de horarios")
            else:
                # Si no existe MenuF.MD, usar menú de BD o mensaje por defecto
                menu = db.query(HolidayMenu).filter(HolidayMenu.is_active == True).first()
                if menu:
                    answer = menu.content
                else:
                    answer = cfg.off_hours_message or f"Atendemos de {cfg.opening_time} a {cfg.closing_time}"
        except Exception as e:
            print(f"[WEBHOOK] Error leyendo MenuF.MD: {e}")
            menu = db.query(HolidayMenu).filter(HolidayMenu.is_active == True).first()
            if menu:
                answer = menu.content
            else:
                answer = cfg.off_hours_message or f"Atendemos de {cfg.opening_time} a {cfg.closing_time}"
        print(f"[WEBHOOK] Usando respuesta off_hours: {answer[:50]}")
    else:
        # En la PRIMERA VEZ siempre mostrar menú principal
        if state.get("first_time", True):
            kb = kb_text()
            lines = kb.split('\n')
            menu_lines = []
            for line in lines:
                menu_lines.append(line)
                # Detener en el primer separador ---
                if line.startswith('---'):
                    break
            answer = '\n'.join(menu_lines).strip()
            state["first_time"] = False
            state["section"] = "main"
            print(f"[WEBHOOK] Primera vez - Mostrando menú principal ({len(answer)} chars)")
        else:
            # Usuario seleccionó una opción del menú - buscar en el archivo
            current_section = state.get("section", "main")
            print(f"[WEBHOOK] Buscando opción en menú: {text} (sección actual: {current_section})")
            answer, new_section = await get_menu_section(text, current_section, db)
            state["section"] = new_section
            print(f"[WEBHOOK] Respuesta del menú: {answer[:60]} (nueva sección: {new_section})")

    new_state = state.copy()
    new_state["last_ts"] = now_ts
    _chat_state[chat_id] = new_state

    print(f"[WEBHOOK] Enviando respuesta: {answer[:50]}")
    try:
        await send_whatsapp_text(chat_id, answer)
        print(f"[WEBHOOK] Respuesta enviada exitosamente")
    except Exception as e:
        print(f"[WEBHOOK] Error enviando respuesta: {e}")
    
    return {"ok": True}

# ======================== PAGES =========================
@app.get("/")
async def root():
    """Redirigir raíz a login"""
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return get_login_page()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard - sin requerir auth en GET (la auth se hace en JS)"""
    return get_dashboard_page()

@app.get("/user-panel", response_class=HTMLResponse)
async def user_panel_page():
    """Panel de usuario - sin requerir auth en GET (la auth se hace en JS)"""
    return get_user_panel_page()

# Iniciar aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
