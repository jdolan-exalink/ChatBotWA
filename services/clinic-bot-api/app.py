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
import shutil
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import init_db, get_db, SessionLocal, engine
from models import Base, User, BotConfig, Holiday, HolidayMenu, WhatsAppBlockList, ConversationState, DailyChatContact, WahaRuntimeState
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
HUMAN_MODE_DEFAULT_HOURS = int(os.getenv("HUMAN_MODE_DEFAULT_HOURS", "12"))
HUMAN_MODE_WAITING_AGENT_HOURS = int(os.getenv("HUMAN_MODE_WAITING_AGENT_HOURS", "2"))

# ──────────────────────────────────────────────────────────────
#  ESTADO GLOBAL (en memoria)
# ──────────────────────────────────────────────────────────────
_bot_paused   = False
_chat_nav: dict[str, dict] = {}   # estado de navegación por chat
_last_status  = {
    "connected": None,
    "last_alert_at": 0,
    "start_time": int(time.time()),
    "connected_since": None,
    "disconnected_since": int(time.time()),
}

# ──────────────────────────────────────────────────────────────
#  CACHÉ EN MEMORIA  (elimina consultas DB en el hot path)
#  El webhook recibe cientos de mensajes — cada query a SQLite
#  bloquea el event loop y apila requests. Los cachemos y solo
#  tocamos DB cuando los datos realmente cambian.
# ──────────────────────────────────────────────────────────────
_cfg_cache: tuple = (0.0, None)                # (timestamp, BotConfig|None) TTL 10s
_CFG_CACHE_TTL: float = 10.0                   # segundos antes de re-leer DB
_off_hours_cache: tuple = (0.0, False)         # (timestamp, resultado) TTL 30s
_blocklist_set: set = set()                    # teléfonos bloqueados
_blocklist_loaded: bool = False                # ¿ya leimos de DB?
_menu_cache: tuple = (0.0, "")                 # (mtime, contenido MenuP.MD)

# ──────────────────────────────────────────────────────────────
#  CLIENTE HTTP GLOBAL PARA WAHA
#  Un solo cliente reutilizado con pool acotado → evita saturar
#  el event loop con cientos de conexiones simultáneas.
# ──────────────────────────────────────────────────────────────
_waha_client: httpx.AsyncClient | None = None
_waha_reconnect_attempts = 0          # contador de reconexión
_waha_last_reconnect_time = 0         # timestamp última reconexión
_waha_force_reconnect = False         # flag para forzar reconexión
_waha_session_op_lock = asyncio.Lock()  # serializa restart/stop/start/delete+create
_waha_last_session_op_at = 0.0          # timestamp último cambio de sesión
_waha_last_connect_request_at = 0.0     # debounce de /bot/connect
_WAHA_SESSION_OP_COOLDOWN_SEC = 8.0
_WAHA_CONNECT_DEBOUNCE_SEC = 3.0


def _get_runtime_state(db: Session) -> WahaRuntimeState:
    row = db.query(WahaRuntimeState).first()
    if not row:
        row = WahaRuntimeState(connected_since_epoch=None, disconnected_since_epoch=int(time.time()))
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _sync_connection_timestamps(prev_connected: bool | None, connected: bool, db: Session | None = None) -> None:
    """Mantiene marcas de tiempo de conexión/desconexión para mostrar uptime."""
    now = int(time.time())

    persisted_connected_since = None
    runtime_row = None
    if db is not None:
        try:
            runtime_row = _get_runtime_state(db)
            persisted_connected_since = runtime_row.connected_since_epoch
        except Exception:
            runtime_row = None

    if prev_connected is None:
        if connected:
            _last_status["connected_since"] = persisted_connected_since or now
            _last_status["disconnected_since"] = None
            if runtime_row is not None and not runtime_row.connected_since_epoch:
                runtime_row.connected_since_epoch = _last_status["connected_since"]
                runtime_row.disconnected_since_epoch = None
                db.commit()
        else:
            _last_status["connected_since"] = None
            _last_status["disconnected_since"] = now
            if runtime_row is not None:
                runtime_row.disconnected_since_epoch = now
                db.commit()
        return

    if prev_connected != connected:
        if connected:
            _last_status["connected_since"] = now
            _last_status["disconnected_since"] = None
            if runtime_row is not None:
                runtime_row.connected_since_epoch = now
                runtime_row.disconnected_since_epoch = None
                db.commit()
        else:
            _last_status["connected_since"] = None
            _last_status["disconnected_since"] = now
            if runtime_row is not None:
                runtime_row.connected_since_epoch = None
                runtime_row.disconnected_since_epoch = now
                db.commit()

def _get_waha_client() -> httpx.AsyncClient:
    """Retorna el cliente global; lo crea si no existe aún.
    Timeouts generosos (10-15s) para evitar falsos negativos con WAHA.
    """
    global _waha_client
    if _waha_client is None or _waha_client.is_closed:
        _logc("[HTTP] Recreando cliente HTTP WAHA")
        _waha_client = httpx.AsyncClient(
            base_url=WAHA_URL,
            timeout=httpx.Timeout(
                connect=10.0,    # 10s para conectar (WAHA puede estar lento)
                read=15.0,       # 15s para leer (WhatsApp puede tardar)
                write=15.0,      # 15s para escribir
                pool=10.0,       # 10s esperando en cola
            ),
            limits=httpx.Limits(
                max_connections=20,        # nunca más de 20 sockets a WAHA
                max_keepalive_connections=10,
                keepalive_expiry=60,       # mantener conexiones 60s
            ),
            # Follow redirects automáticamente
            follow_redirects=True,
        )
    return _waha_client

def _reset_waha_client():
    """Fuerza recreación del cliente HTTP en la próxima solicitud."""
    global _waha_client, _waha_force_reconnect
    _waha_client = None
    _waha_force_reconnect = False
    _logc("[HTTP] Cliente HTTP marcado para recreación")


def _waha_session_op_recent() -> bool:
    return (time.time() - _waha_last_session_op_at) < _WAHA_SESSION_OP_COOLDOWN_SEC


async def _waha_restart_session(reason: str = "unknown") -> bool:
    """Restart protegido para evitar operaciones concurrentes sobre WAHA."""
    global _waha_last_session_op_at
    if _waha_session_op_lock.locked():
        _log(f"[CONNECT] restart omitido ({reason}): operación en curso")
        return True
    if _waha_session_op_recent():
        _log(f"[CONNECT] restart omitido ({reason}): cooldown activo")
        return True

    async with _waha_session_op_lock:
        _waha_last_session_op_at = time.time()
        try:
            c = _get_waha_client()
            r = await c.post(
                f"/api/sessions/{WAHA_SESSION}/restart",
                headers=_waha_headers(), json={},
                timeout=httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=10.0)
            )
            _log(f"[CONNECT] restart ({reason}) -> {r.status_code}")
            return r.status_code < 400
        except Exception as e:
            _logc(f"[ERROR] restart ({reason}): {e}")
            return False


async def _waha_stop_start_session(reason: str = "unknown") -> bool:
    """Stop+start protegido para recuperación agresiva sin carreras."""
    global _waha_last_session_op_at
    if _waha_session_op_lock.locked():
        _log(f"[CONNECT] stop+start omitido ({reason}): operación en curso")
        return True
    if _waha_session_op_recent():
        _log(f"[CONNECT] stop+start omitido ({reason}): cooldown activo")
        return True

    async with _waha_session_op_lock:
        _waha_last_session_op_at = time.time()
        try:
            c = _get_waha_client()
            await c.post(f"/api/sessions/{WAHA_SESSION}/stop", headers=_waha_headers(), json={})
            await asyncio.sleep(2)
            r = await c.post(f"/api/sessions/{WAHA_SESSION}/start", headers=_waha_headers(), json={})
            _log(f"[CONNECT] stop+start ({reason}) -> {r.status_code}")
            return r.status_code < 400
        except Exception as e:
            _logc(f"[ERROR] stop+start ({reason}): {e}")
            return False

# ──────────────────────────────────────────────────────────────
#  LOGGING
#  Modo operativo (debug_mode=False): solo [CHAT] y [ERROR]
#  Modo debug   (debug_mode=True):  todos los logs detallados
# ──────────────────────────────────────────────────────────────
_debug_mode: bool = False  # sincronizado desde BotConfig.debug_mode

def _log(msg: str) -> None:
    """Log de debug: solo imprime cuando debug_mode está activo."""
    if _debug_mode:
        print(msg)

def _logc(msg: str) -> None:
    """Log crítico: siempre imprime (chats + errores, ambos modos)."""
    print(msg)

# ──────────────────────────────────────────────────────────────
#  APP
# ──────────────────────────────────────────────────────────────
app = FastAPI(title="WA-BOT", version="2.2.7")
app.add_middleware(GZipMiddleware, minimum_size=500)   # comprimir respuestas >500B
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
    _get_waha_client()              # pre-inicializar el cliente HTTP
    # Warm-up del backend bcrypt: la primera llamada a passlib con bcrypt>=4.x
    # puede fallar silenciosamente. Este dummy-call fuerza la inicialización
    # del handler antes de que llegue el primer login real.
    try:
        from security import hash_password, verify_password
        _dummy_hash = hash_password("warmup")
        verify_password("warmup", _dummy_hash)
    except Exception:
        pass
    asyncio.create_task(_init_defaults())
    asyncio.create_task(_monitor_loop())

@app.on_event("shutdown")
async def shutdown():
    global _waha_client
    if _waha_client and not _waha_client.is_closed:
        await _waha_client.aclose()

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
            _log("[INIT] Admin creado: admin / admin123")
        if not db.query(User).filter(User.username == "usuario").first():
            db.add(User(
                username="usuario", email="usuario@clinic.local",
                hashed_password=hash_password("usuario123"),
                full_name="Usuario", is_admin=False, is_active=True
            ))
            _log("[INIT] Usuario creado: usuario / usuario123")
        if not db.query(BotConfig).first():
            db.add(BotConfig(
                solution_name=SOLUTION_NAME, menu_title=SOLUTION_NAME,
                opening_time="08:00", closing_time="16:00",
                sat_opening_time="10:00", sat_closing_time="14:00",
                sat_enabled=True, sun_enabled=False,
                off_hours_enabled=True,
                ollama_url=OLLAMA_URL, ollama_model=OLLAMA_MODEL,
                admin_idle_timeout_sec=900
            ))
            _log("[INIT] Config por defecto creada")
        db.commit()
        _sync_debug_mode(db)   # carga debug_mode al arrancar
        _preload_caches(db)    # pre-carga config, blocklist, menú y off-hours
    except Exception as e:
        _logc(f"[ERROR] init: {e}")
        db.rollback()
    finally:
        db.close()

async def _monitor_loop():
    """Monitor de conexión WAHA con reconexión automática inteligente.

    Estrategia de reconexión:
    - Detecta caída cada 10 segundos (no 30s)
    - Reintenta con backoff exponencial: 1s, 2s, 4s, 8s, 16s, 30s (máx)
    - Después de 5 intentos fallidos, envía alerta
    - Resetear contador al reconectar exitosamente
    """
    global _waha_reconnect_attempts, _waha_last_reconnect_time
    reconnect_delays = [1, 2, 4, 8, 16, 30, 30, 30]  # backoff exponencial, máx 30s

    _logc("[MONITOR] Iniciando loop de monitoreo WAHA...")

    while True:
        try:
            info = await _waha_session_info()
            status_str = str(info.get("status", "")).upper()
            s = str(info).lower()
            eng = info.get("engine", {})
            eng_state = str(eng.get("state", "UNKNOWN")).upper()

            # Verificar conexión de manera más robusta
            connected = (
                (status_str in ("WORKING", "CONNECTED", "AUTHENTICATED")) or
                (eng_state == "CONNECTED")
            ) and "qr" not in s

            prev = _last_status["connected"]
            _last_status["connected"] = connected
            db_sync = SessionLocal()
            try:
                _sync_connection_timestamps(prev, connected, db_sync)
            finally:
                db_sync.close()

            # Log inicial y cambios de estado
            if prev is None:  # Primer chequeo
                _logc(f"[MONITOR] Estado inicial: status={status_str}, engine={eng_state}, connected={connected}")
            elif prev != connected:  # Cambio de estado
                if connected:
                    _logc(f"[MONITOR] ✓ RECONNECTADO: status={status_str}, engine={eng_state}")
                else:
                    _logc(f"[MONITOR] ✗ DESCONECTADO: status={status_str}, engine={eng_state}")

            if not connected and status_str not in ("STARTING", "SCAN_QR_CODE"):
                # Sesión caída → intentar reconexión
                now = int(time.time())

                # Evitar tormenta de operaciones de sesión en paralelo
                if _waha_session_op_lock.locked() or _waha_session_op_recent():
                    _log("[MONITOR] Operación de sesión en curso/cooldown, se difiere reconexión")
                    await asyncio.sleep(10)
                    continue

                # Calcular delay según intentos
                delay_idx = min(_waha_reconnect_attempts, len(reconnect_delays) - 1)
                delay = reconnect_delays[delay_idx]

                # Evitar reconexiones muy seguidas
                if now - _waha_last_reconnect_time < delay:
                    await asyncio.sleep(10)
                    continue

                _waha_reconnect_attempts += 1
                _waha_last_reconnect_time = now

                _logc(f"[MONITOR] Sesión caída (status={status_str}), intento #{_waha_reconnect_attempts}")

                # Estrategia de reconexión escalonada
                recon_ok = False

                # Intento 1-2: restart simple (mantiene auth)
                if _waha_reconnect_attempts <= 2:
                    recon_ok = await _waha_restart_session("monitor")
                    if recon_ok:
                        _logc("[MONITOR] Restart exitoso, esperando reconexión...")

                # Intento 3-4: stop + start (más agresivo)
                if not recon_ok and 2 < _waha_reconnect_attempts <= 4:
                    recon_ok = await _waha_stop_start_session("monitor")
                    if recon_ok:
                        _logc("[MONITOR] Stop+Start exitoso, esperando reconexión...")

                # Intento 5+: recreate completo (borra auth, genera QR)
                if not recon_ok and _waha_reconnect_attempts > 4:
                    _logc("[MONITOR] Intentando recreación completa de sesión (requerirá QR)")
                    ok = await _waha_delete_and_recreate()
                    if ok:
                        recon_ok = True
                        _logc("[MONITOR] Recreación completada, esperando QR...")

                # Enviar alerta después de 5 intentos fallidos
                if _waha_reconnect_attempts >= 5 and not recon_ok:
                    now = int(time.time())
                    if now - _last_status["last_alert_at"] > 300:  # 5 min entre alertas
                        _last_status["last_alert_at"] = now
                        await _send_alert_email(
                            "[ALERTA] WhatsApp desconectado",
                            f"El bot se desconectó y no pudo reconectarse automáticamente después de {_waha_reconnect_attempts} intentos.\n"
                            f"Último status reportado: {status_str}\n\n"
                            "Acciones recomendadas:\n"
                            "1. Verificar que WAHA esté corriendo\n"
                            "2. Revisar logs de WAHA\n"
                            "3. Reescanear QR desde el panel web"
                        )

            elif connected:
                if prev is not True:
                    _logc(f"[MONITOR] ✓ Sesión reconectada OK (status={status_str})")
                # Resetear contador al reconectar
                if _waha_reconnect_attempts > 0:
                    _logc(f"[MONITOR] Resetear contador de reconexión (era {_waha_reconnect_attempts})")
                _waha_reconnect_attempts = 0

        except httpx.ConnectError as e:
            # WAHA no responde en absoluto
            _logc(f"[MONITOR] WAHA no disponible (ConnectError): {e}")
            _waha_reconnect_attempts += 1
            _waha_last_reconnect_time = int(time.time())
        except httpx.TimeoutException as e:
            # WAHA responde pero muy lento
            _logc(f"[MONITOR] WAHA timeout: {e}")
            _waha_reconnect_attempts += 1
            _waha_last_reconnect_time = int(time.time())
        except Exception as e:
            _logc(f"[MONITOR] Error inesperado: {e}")

        await asyncio.sleep(10)  # Chequear cada 10 segundos

# ──────────────────────────────────────────────────────────────
#  HELPERS - ARCHIVOS
# ──────────────────────────────────────────────────────────────
def _data_path(filename: str) -> str:
    if os.path.isabs(filename):
        return filename
    if os.path.exists("/app/data"):
        return os.path.join("/app/data", filename)
    return os.path.join(os.path.dirname(__file__), "data", filename)


def _backup_file_path(path: str) -> str:
    return f"{path}.bak"


def _write_text_with_backup(path: str, content: str) -> None:
    """Guarda archivo y conserva backup de la version previa."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bak = _backup_file_path(path)
    if os.path.exists(path):
        shutil.copyfile(path, bak)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _restore_previous_text(path: str) -> str:
    """Restaura backup y hace swap para permitir deshacer la restauracion."""
    bak = _backup_file_path(path)
    if not os.path.exists(bak):
        raise FileNotFoundError("No hay backup disponible")

    with open(bak, "r", encoding="utf-8") as f:
        previous = f.read()

    current = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            current = f.read()

    with open(path, "w", encoding="utf-8") as f:
        f.write(previous)
    with open(bak, "w", encoding="utf-8") as f:
        f.write(current)

    return previous

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
    return await _get_waha_client().get(path, headers=_waha_headers())

async def _waha_post(path: str, data: dict):
    return await _get_waha_client().post(path, json=data, headers=_waha_headers())

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


def _extract_qr_from_any(data: dict) -> bytes | None:
    """Extrae QR base64 desde distintos esquemas JSON de WAHA."""
    if not isinstance(data, dict):
        return None

    for key in ("qrcode", "qr", "base64", "code", "value", "data"):
        raw = data.get(key)
        if isinstance(raw, str) and raw:
            try:
                if raw.startswith("data:image") and "," in raw:
                    raw = raw.split(",", 1)[1]
                return base64.b64decode(raw)
            except Exception:
                pass

    for parent in ("qrcode", "qrCode", "qr", "data"):
        node = data.get(parent)
        if isinstance(node, dict):
            for key in ("base64", "qr", "code", "value", "data"):
                raw = node.get(key)
                if isinstance(raw, str) and raw:
                    try:
                        if raw.startswith("data:image") and "," in raw:
                            raw = raw.split(",", 1)[1]
                        return base64.b64decode(raw)
                    except Exception:
                        pass
    return None

async def _waha_qr() -> bytes | None:
    """Obtiene el QR de WAHA. Solo funciona cuando la sesión está en SCAN_QR_CODE.
    Retorna PNG bytes o None. Usa únicamente rutas confirmadas para esta versión de WAHA."""
    client = _get_waha_client()
    # Compatibilidad entre versiones de WAHA (free/webjs) y respuestas JSON.
    paths = [
        f"/api/{WAHA_SESSION}/auth/qr?format=image",
        f"/api/{WAHA_SESSION}/auth/qr",
        f"/api/{WAHA_SESSION}/auth/qr?format=RAW",
        f"/api/sessions/{WAHA_SESSION}/qr",
        f"/api/{WAHA_SESSION}/qr",
    ]

    async def _try(p: str) -> bytes | None:
        try:
            r = await client.get(p, headers=_waha_headers(),
                                 timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0))
            if r.status_code >= 400:
                return None

            ct = r.headers.get("content-type", "")
            if "image" in ct and r.content:
                _logc(f"[QR] Obtenido desde {p} (image, {len(r.content)} bytes)")
                return r.content
            if "json" in ct:
                decoded = _extract_qr_from_any(r.json())
                if decoded:
                    _logc(f"[QR] Obtenido desde {p} (base64, {len(decoded)} bytes)")
                    return decoded
        except httpx.TimeoutException:
            _log(f"[QR] Timeout en {p}")
        except Exception as e:
            _log(f"[QR] Error en {p}: {e}")
        return None

    # Probar rutas en secuencia evita picos de carga por consultas paralelas
    # cuando el frontend hace polling.
    for p in paths:
        qr = await _try(p)
        if qr:
            return qr
    return None

async def _waha_healthcheck() -> bool:
    """Verifica si WAHA responde. Retorna True si está disponible.

    Usa /api/sessions en lugar de /health porque /health requiere Plus.
    """
    try:
        c = _get_waha_client()
        # Usar /api/sessions que siempre funciona (no requiere Plus)
        r = await c.get(
            "/api/sessions",
            headers=_waha_headers(),
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
        )
        # Si responde 200, WAHA está disponible
        return r.status_code < 400
    except httpx.ConnectError:
        return False
    except Exception:
        return False

async def _send_wha(chat_id: str, text: str):
    """Envía texto por WhatsApp.

    Solo llamar desde flujo BOT, nunca en human mode.
    Intenta enviar directamente, si falla reconecta y reintenta.
    """
    if not text or not text.strip():
        _log(f"[SEND] Bloqueado - texto vacío para {chat_id}")
        return

    _logc(f"[CHAT] → {chat_id}: {text[:80]}")
    client = _get_waha_client()

    # Intentar enviar por múltiples rutas
    for path, payload in [
        ("/api/sendText",                 {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
        (f"/api/{WAHA_SESSION}/sendText", {"chatId": chat_id, "text": text}),
        ("/api/messages/text",            {"session": WAHA_SESSION, "chatId": chat_id, "text": text}),
    ]:
        try:
            r = await client.post(
                path,
                json=payload,
                headers=_waha_headers(),
                timeout=httpx.Timeout(connect=10.0, read=15.0, write=15.0, pool=10.0)
            )
            if r.status_code < 400:
                _log(f"[SEND] OK via {path}")
                return
            # Si falla con 4xx/5xx, loguear y intentar siguiente ruta
            _log(f"[SEND] Error {r.status_code} via {path}")
        except httpx.TimeoutException:
            _logc(f"[SEND] Timeout en {path}")
            # Intentar reconectar y continuar con la siguiente ruta
            _reset_waha_client()
            await asyncio.sleep(1)
            client = _get_waha_client()
        except httpx.ConnectError as e:
            _logc(f"[SEND] ConnectError en {path}: {e}")
            # Intentar reconectar y continuar con la siguiente ruta
            _reset_waha_client()
            await asyncio.sleep(1)
            client = _get_waha_client()
        except Exception as e:
            _logc(f"[SEND] Error en {path}: {e}")
            # Intentar reconectar y continuar con la siguiente ruta
            _reset_waha_client()
            await asyncio.sleep(1)
            client = _get_waha_client()

    _logc(f"[SEND] No enviado para {chat_id} (todas las rutas fallaron)")

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
        _logc(f"[ERROR] email: {e}")

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

def _get_cfg_cached(db: Session) -> BotConfig:
    """Config con caché TTL de 10s. Todos los workers releen DB tras ese tiempo."""
    global _cfg_cache
    ts, cfg = _cfg_cache
    if cfg is None or time.time() - ts > _CFG_CACHE_TTL:
        cfg = _get_cfg(db)
        _cfg_cache = (time.time(), cfg)
    return cfg

def _invalidate_cfg_cache():
    """Invalida el caché de config y off-hours al guardar cambios."""
    global _cfg_cache, _off_hours_cache
    _cfg_cache = (0.0, None)
    _off_hours_cache = (0.0, False)

def _sync_debug_mode(db: Session) -> None:
    """Lee debug_mode desde DB y actualiza el global en memoria."""
    global _debug_mode
    try:
        cfg = _get_cfg(db)
        _debug_mode = bool(getattr(cfg, "debug_mode", False))
    except Exception:
        pass

def _is_off_hours(db: Session) -> bool:
    import pytz
    cfg = _get_cfg_cached(db)
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
    dow = now.weekday()  # 0=Lunes ... 5=Sábado, 6=Domingo
    if dow == 6:          # Domingo
        if not getattr(cfg, 'sun_enabled', False):
            _log(f"[HOURS] Domingo — cerrado todo el día")
            return True
        o, c = cfg.sat_opening_time or "10:00", cfg.sat_closing_time or "14:00"
    elif dow == 5:        # Sábado
        if not getattr(cfg, 'sat_enabled', True):
            _log(f"[HOURS] Sábado — cerrado todo el día")
            return True
        o, c = cfg.sat_opening_time or "10:00", cfg.sat_closing_time or "14:00"
    else:                 # Lunes a Viernes
        o, c = cfg.opening_time or "08:00", cfg.closing_time or "16:00"
    off = t < o or t > c
    _log(f"[HOURS] {now.strftime('%A %H:%M')} | {o}-{c} | fuera={off}")
    return off

def _is_off_hours_cached(db: Session) -> bool:
    """Calcula off-hours con caché de 30s. Recalcula solo cuando cambia la hora."""
    global _off_hours_cache
    now_ts = time.time()
    last_ts, last_val = _off_hours_cache
    if now_ts - last_ts < 30:   # caché válido por 30 segundos
        return last_val
    result = _is_off_hours(db)
    _off_hours_cache = (now_ts, result)
    return result

def _normalize_phone(phone: str) -> str:
    """Normaliza un número de teléfono a dígitos puros (sin +, @c.us, espacios)."""
    return phone.split("@")[0].lstrip("+").replace(" ", "").strip()

def _get_blocklist(db: Session) -> set:
    """Blocklist cacheada. Se carga una vez y se actualiza en add/delete."""
    global _blocklist_set, _blocklist_loaded
    if not _blocklist_loaded:
        try:
            rows = db.query(WhatsAppBlockList).all()
            _blocklist_set = {_normalize_phone(r.phone_number) for r in rows}
            _blocklist_loaded = True
        except Exception:
            pass
    return _blocklist_set


def _local_today_str(db: Session) -> str:
    import pytz
    cfg = _get_cfg_cached(db)
    try:
        tz = pytz.timezone(cfg.timezone or "America/Argentina/Buenos_Aires")
    except Exception:
        tz = pytz.UTC
    return datetime.now(tz).strftime("%Y-%m-%d")


def _track_chat_today(db: Session, chat_id: str) -> None:
    """Registra un chat unico por dia; ignora duplicados de forma segura."""
    phone = _normalize_phone(chat_id)
    if not phone:
        return

    row = DailyChatContact(day=_local_today_str(db), phone_number=phone)
    try:
        db.add(row)
        db.commit()
    except IntegrityError:
        db.rollback()
    except Exception as e:
        db.rollback()
        _log(f"[METRICS] Error track_chat_today: {e}")


def _count_chats_today(db: Session) -> int:
    return db.query(DailyChatContact).filter(DailyChatContact.day == _local_today_str(db)).count()

def _get_menu_cached() -> str:
    """Lee menú desde archivo; recachea automáticamente si el archivo cambió (mtime)."""
    global _menu_cache
    p = _data_path("MenuP.MD")
    try:
        mtime = os.path.getmtime(p)
    except OSError:
        mtime = 0.0
    last_mtime, content = _menu_cache
    if mtime != last_mtime or not content:
        content = _read_menu()
        _menu_cache = (mtime, content)
    return content

def _invalidate_menu_cache():
    global _menu_cache
    _menu_cache = (0.0, "")

def _preload_caches(db: Session):
    """Pre-carga todos los cachés al arrancar para respuesta instantánea desde el primer mensaje."""
    _get_cfg_cached(db)
    _get_blocklist(db)
    _get_menu_cached()
    _is_off_hours_cached(db)

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
        _logc(f"[HUMAN] Expirado para {chat_id} → bot")
    return active

def _start_human_mode(db: Session, chat_id: str, duration_hours: int = HUMAN_MODE_DEFAULT_HOURS) -> str:
    """Activa modo humano por N horas. Retorna ticket_id."""
    import uuid
    row = db.query(ConversationState).filter(
        ConversationState.phone_number == chat_id
    ).first()
    if not row:
        row = ConversationState(phone_number=chat_id)
        db.add(row)
    ticket = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    row.human_mode         = True
    row.human_mode_expire  = datetime.utcnow() + timedelta(hours=duration_hours)
    row.current_state      = "WAITING_AGENT"
    row.handoff_active     = True
    row.handoff_started_at = datetime.utcnow()
    row.ticket_id          = ticket
    row.last_message_at    = datetime.utcnow()
    db.commit()
    _logc(f"[HUMAN] Activado {chat_id} | ticket={ticket} | duration={duration_hours}h | expire={row.human_mode_expire}")
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
        _logc(f"[HUMAN] Desactivado {chat_id}")


def _start_human_mode_silent(db: Session, chat_id: str):
    """Activa/renueva modo humano sin enviar mensaje automático al usuario."""
    row = db.query(ConversationState).filter(
        ConversationState.phone_number == chat_id
    ).first()
    if not row:
        row = ConversationState(phone_number=chat_id)
        db.add(row)

    now = datetime.utcnow()
    row.human_mode = True
    row.human_mode_expire = now + timedelta(hours=12)
    row.handoff_active = True
    row.current_state = "IN_AGENT"
    if not row.handoff_started_at:
        row.handoff_started_at = now
    row.last_message_at = now
    db.commit()
    _logc(f"[HUMAN] Activado por operador {chat_id} | expire={row.human_mode_expire}")


def _touch_human_mode_timeout(db: Session, chat_id: str):
    """Renueva timeout de modo humano por actividad de chat."""
    row = db.query(ConversationState).filter(
        ConversationState.phone_number == chat_id
    ).first()
    if not row or not row.human_mode:
        return
    now = datetime.utcnow()
    # Mientras espera operador, mantener ventana corta; con operador activo, ventana estándar.
    duration_hours = HUMAN_MODE_WAITING_AGENT_HOURS if row.current_state == "WAITING_AGENT" else HUMAN_MODE_DEFAULT_HOURS
    row.human_mode_expire = now + timedelta(hours=duration_hours)
    row.last_message_at = now
    db.commit()


def _is_turnos_waiting_section(section: str) -> bool:
    """True para secciones de selección final de médico dentro de turnos (ej: menu_1_1)."""
    if not section or not section.startswith("menu_1_"):
        return False
    parts = section.split("_")
    return len(parts) == 3 and parts[2].isdigit()


def _extract_operator_target_chat_id(msg: dict) -> str:
    """Intenta obtener el chat destino cuando WAHA reporta un mensaje fromMe."""
    candidates = [
        msg.get("chatId"),
        msg.get("chat_id"),
        msg.get("to"),
        msg.get("recipient"),
        msg.get("recipientId"),
        msg.get("from"),
    ]
    for raw in candidates:
        if not isinstance(raw, str):
            continue
        cid = raw.strip()
        if not cid:
            continue
        if any(x in cid for x in ("status@", "@status", "broadcast", "@g.us")):
            continue
        if "@c.us" in cid:
            return cid
    return ""

# ──────────────────────────────────────────────────────────────
#  MENU  (navegación jerárquica Markdown)
# ──────────────────────────────────────────────────────────────
def _menu_main() -> str:
    """Devuelve el bloque inicial del menú (hasta primer ---)."""
    lines = _get_menu_cached().split("\n")
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

    lines   = _get_menu_cached().split("\n")
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

def _sync_process_message(chat_id: str, text: str) -> str:
    """
    Toda la lógica síncrona con DB. Corre en thread pool.
    Devuelve el mensaje a enviar (str vacío = no enviar nada).
    """
    global _chat_nav
    db = SessionLocal()
    try:
        # 4. Contador diario persistente en DB
        _track_chat_today(db, chat_id)

        # 5. HUMAN MODE
        in_human = _is_human_mode(db, chat_id)
        _log(f"[WH] human_mode={in_human}")

        if in_human:
            if text == "98":
                _exit_human_mode(db, chat_id)
                _chat_nav.pop(chat_id, None)
                return (
                    "✅ *Volviste al menú automático.*\n\n"
                    "Escribe *0* para ver el menú principal."
                )
            else:
                _touch_human_mode_timeout(db, chat_id)
                _log(f"[WH] HUMAN_MODE activo → ignorando '{text}'")
                return ""

        # 6. 98 fuera de human mode → silencio
        if text == "98":
            _log(f"[WH] 98 sin human_mode activo → ignorar")
            return ""

        # 7. Opción 99: activar modo humano
        if text == "99":
            current_section = _chat_nav.get(chat_id, {}).get("section", "main")
            duration_hours = HUMAN_MODE_WAITING_AGENT_HOURS if _is_turnos_waiting_section(current_section) else HUMAN_MODE_DEFAULT_HOURS
            ticket = _start_human_mode(db, chat_id, duration_hours=duration_hours)
            _chat_nav.pop(chat_id, None)
            return (
                "📞 *Se ha iniciado transferencia a un operador*\n\n"
                f"✅ Tu número de ticket: *{ticket}*\n\n"
                "⏳ Por favor espera a que un operario se comunique contigo.\n"
                "Esto generalmente toma unos minutos.\n\n"
                f"⌛ Tiempo máximo de espera en este estado: *{duration_hours} horas*.\n\n"
                "Gracias por tu paciencia 😊\n\n"
                "_(Escribe *98* en cualquier momento para volver al menú automático)_"
            )

        # 8. Filtros de acceso
        cfg = _get_cfg_cached(db)
        if _normalize_phone(chat_id) in _get_blocklist(db):
            return ""
        if cfg.country_filter_enabled and cfg.country_codes:
            codes = [c.strip() for c in cfg.country_codes.split(",")]
            if not any(chat_id.startswith(c) for c in codes):
                return ""
        if cfg.area_filter_enabled and cfg.area_codes:
            areas = [a.strip() for a in cfg.area_codes.split(",")]
            if not any(a in chat_id for a in areas):
                return ""

        # 9. Flujo normal del bot
        now_ts = int(time.time())
        nav    = _chat_nav.get(chat_id, {"section": "main", "ts": now_ts, "new": True})
        if now_ts - nav.get("ts", now_ts) > CHAT_IDLE_RESET_SEC:
            nav = {"section": "main", "ts": now_ts, "new": True}

        answer = ""

        # 9a. Fuera de horario
        if _is_off_hours_cached(db):
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
        return answer

    except Exception as e:
        _logc(f"[ERROR] _sync_process_message {chat_id}: {e}")
        return ""
    finally:
        db.close()


async def _handle_message(chat_id: str, text: str):
    """
    Wrapper async: corre lógica síncrona en thread pool y luego
    envía la respuesta por WAHA (async). El event loop queda libre
    durante toda la ejecución síncrona.
    """
    try:
        # DB + lógica → thread pool (no bloquea el event loop)
        answer = await asyncio.to_thread(_sync_process_message, chat_id, text)
        # Envío HTTP → async
        if answer:
            await _send_wha(chat_id, answer)
    except Exception as e:
        _logc(f"[ERROR] _handle_message {chat_id}: {e}")


@app.post("/webhook")
async def webhook(req: Request):
    global _bot_paused
    import sys

    # 1. Parsear payload ─────────────────────────────────────────
    data = await req.json()

    # Descartar estados/stories de WhatsApp antes de parsear nada más
    event_type = data.get("event", "")
    if "status" in event_type.lower():
        return {"ok": True, "i": "status_event"}

    msg = data.get("payload") or data.get("message") or data

    # Si el operador inicia/escribe un chat desde WhatsApp Web, activar modo humano
    # para ese número y evitar respuestas automáticas del bot.
    if msg.get("fromMe"):
        op_chat_id = _extract_operator_target_chat_id(msg)
        if not op_chat_id:
            return {"ok": True, "i": "from_me_no_chat"}
        db = SessionLocal()
        try:
            _start_human_mode_silent(db, op_chat_id)
            _chat_nav.pop(op_chat_id, None)
        finally:
            db.close()
        return {"ok": True, "i": "from_me_human_mode", "chat": op_chat_id}

    chat_id = (msg.get("from") or msg.get("chatId") or msg.get("chat_id") or "").strip()

    # Filtro temprano de estados (antes del log para no ensuciar consola)
    if any(x in chat_id for x in ("status@", "@status", "broadcast")):
        return {"ok": True, "i": "status"}

    raw_txt = msg.get("body") or msg.get("text") or ""
    if not isinstance(raw_txt, str):
        raw_txt = ""
    text = raw_txt.strip()

    msg_log = f"[CHAT] ← {chat_id!r}: {text!r}"
    print(msg_log, flush=True)
    sys.stdout.flush()

    # 2. Filtros de ruido (sin DB) ───────────────────────────────
    if not chat_id or not text:
        return {"ok": True, "i": "empty"}
    if "@g.us" in chat_id:
        return {"ok": True, "i": "group"}
    if text.lower() in {"estado", "estados", "status"}:
        return {"ok": True, "i": "status_text"}

    # 3. Bot pausado ─────────────────────────────────────────────
    if _bot_paused:
        return {"ok": True, "paused": True}

    # Log de procesamiento
    proc_log = f"[WEBHOOK] Procesando: {chat_id} -> {text[:50]}"
    print(proc_log, flush=True)
    sys.stdout.flush()

    # Programar procesamiento en thread pool y retornar 200 inmediatamente.
    # WAHA solo necesita el 200 rápido; el bot responde por su cuenta.
    asyncio.create_task(_handle_message(chat_id, text))
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


@app.post("/api/human-mode/close")
async def close_human_mode_chat(req: Request, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    """Fuerza el cierre de modo humano para un número/chat específico."""
    body = await req.json()
    raw = str(body.get("phone_number") or body.get("chat_id") or "").strip()
    if not raw:
        raise HTTPException(400, "phone_number requerido")

    normalized = _normalize_phone(raw)
    candidates = [raw, normalized, f"{normalized}@c.us"]

    row = None
    for c in candidates:
        if not c:
            continue
        row = db.query(ConversationState).filter(ConversationState.phone_number == c).first()
        if row:
            break

    if not row:
        return {"ok": True, "closed": False, "detail": "No existe conversación para ese número"}

    if not row.human_mode:
        return {"ok": True, "closed": False, "detail": "El chat ya está en modo bot", "phone_number": row.phone_number}

    target = row.phone_number
    _exit_human_mode(db, target)
    # Limpiar posibles variantes en cache de navegación
    _chat_nav.pop(target, None)
    _chat_nav.pop(normalized, None)
    _chat_nav.pop(f"{normalized}@c.us", None)

    return {"ok": True, "closed": True, "phone_number": target}

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
              "sat_closing_time","sat_enabled","sun_enabled","off_hours_enabled","off_hours_message",
              "country_filter_enabled","country_codes","area_filter_enabled","area_codes",
              "ollama_url","ollama_model","admin_idle_timeout_sec","debug_mode"]:
        v = getattr(data, f, None)
        if v is not None: setattr(cfg, f, v)

    # Mantener sincronizado el archivo que usa el runtime para mensaje fuera de horario
    if data.off_hours_message is not None:
        p = _data_path("MenuF.MD")
        _write_text_with_backup(p, data.off_hours_message)

    db.commit(); db.refresh(cfg)
    _sync_debug_mode(db)   # actualiza el global en memoria
    _invalidate_cfg_cache()    # limpia caché para próxima lectura
    return BotConfigResponse.from_orm(cfg)

@app.put("/api/config/menu")
async def update_menu_file(req: Request, ca=Depends(get_current_admin)):
    body = await req.json(); content = body.get("content", "")
    if not content.strip(): raise HTTPException(400, "Vacío")
    p = _data_path("MenuP.MD")
    _write_text_with_backup(p, content)
    _invalidate_menu_cache()    # fuerza recarga en próximo acceso
    return {"ok": True, "bytes": len(content)}


@app.post("/api/config/menu/restore")
async def restore_menu_file(ca=Depends(get_current_admin)):
    p = _data_path("MenuP.MD")
    try:
        restored = _restore_previous_text(p)
    except FileNotFoundError:
        raise HTTPException(404, "No hay backup de menú para restaurar")
    _invalidate_menu_cache()
    return {"ok": True, "bytes": len(restored)}

@app.put("/api/config/offhours")
async def update_offhours_file(req: Request, ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    body = await req.json()
    content = body.get("content", body.get("off_hours_message", ""))
    if not content.strip(): raise HTTPException(400, "Vacío")
    p = _data_path("MenuF.MD")
    _write_text_with_backup(p, content)

    # Sincronizar también la configuración en DB para consistencia de API
    cfg = _get_cfg(db)
    cfg.off_hours_message = content
    if "off_hours_enabled" in body and body.get("off_hours_enabled") is not None:
        cfg.off_hours_enabled = bool(body.get("off_hours_enabled"))
    db.commit()
    _invalidate_cfg_cache()

    return {"ok": True, "bytes": len(content)}


@app.post("/api/config/offhours/restore")
async def restore_offhours_file(ca=Depends(get_current_admin), db: Session = Depends(get_db)):
    p = _data_path("MenuF.MD")
    try:
        restored = _restore_previous_text(p)
    except FileNotFoundError:
        raise HTTPException(404, "No hay backup de fuera de hora para restaurar")

    cfg = _get_cfg(db)
    cfg.off_hours_message = restored
    db.commit()
    _invalidate_cfg_cache()
    return {"ok": True, "bytes": len(restored)}

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
    normalized = _normalize_phone(phone)
    if not normalized: raise HTTPException(400, "phone_number inválido")
    if db.query(WhatsAppBlockList).filter(WhatsAppBlockList.phone_number == normalized).first():
        raise HTTPException(400, "Ya bloqueado")
    b = WhatsAppBlockList(phone_number=normalized, reason=body.get("reason", ""))
    db.add(b); db.commit(); db.refresh(b)
    _blocklist_set.add(normalized)   # actualiza caché en memoria
    return {"ok": True, "id": b.id}

@app.delete("/api/blocklist/{bid}")
async def del_blocklist(bid: int, cu=Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(WhatsAppBlockList).filter(WhatsAppBlockList.id == bid).first()
    if not b: raise HTTPException(404, "No encontrado")
    phone_to_remove = _normalize_phone(b.phone_number)
    db.delete(b); db.commit()
    _blocklist_set.discard(phone_to_remove)   # actualiza caché en memoria
    return {"ok": True}

# ──────────────────────────────────────────────────────────────
#  BOT CONTROL
# ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"ok": True, "provider": "waha", "instance": WAHA_SESSION}

@app.get("/version")
async def version():
    return {"version": "2.2.7", "name": "WA-BOT"}

@app.get("/status")
async def status(cu=Depends(get_current_user), db: Session = Depends(get_db)):
    info = await _waha_session_info()
    s = str(info).lower()
    eng = info.get("engine", {}) if isinstance(info.get("engine"), dict) else {}
    session_status = str(info.get("status", "")).upper()
    eng_state = str(eng.get("state") or "").upper()

    # Lógica de conexión alineada con el monitor loop.
    # WEBJS no siempre reporta engine.state; usamos el campo 'status' de la sesión.
    connected = (
        session_status in ("WORKING", "CONNECTED", "AUTHENTICATED") or
        eng_state == "CONNECTED"
    ) and "scan_qr_code" not in s

    # Sincronizar transición también desde endpoint para no depender
    # exclusivamente del monitor loop en casos de arranque reciente.
    prev = _last_status.get("connected")
    _last_status["connected"] = connected
    _sync_connection_timestamps(prev, connected, db)

    connected_since = _last_status.get("connected_since")
    connection_uptime_seconds = int(time.time()) - int(connected_since) if connected and connected_since else 0

    # QR disponible solo cuando la sesión espera escaneo.
    # STARTING todavía no está lista para QR y pedirlo genera 422 en WAHA.
    needs_qr = not connected and session_status in ("SCAN_QR_CODE", "FAILED")
    qr = await _waha_qr() if needs_qr else None

    if not connected:
        _logc(f"[STATUS] Desconectado (status={session_status}, eng_state={eng_state}), QR disponible={qr is not None}")
    else:
        _log(f"[STATUS] Conectado (status={session_status})")

    cfg = _get_cfg(db)
    return {
        "provider": "waha", "instance": WAHA_SESSION,
        "connected": connected, "has_qr": qr is not None,
        "connected_since": connected_since,
        "connection_uptime_seconds": connection_uptime_seconds,
        "paused": _bot_paused,
        "solution_name": cfg.solution_name,
        "off_hours": _is_off_hours(db),
        "chats_today": _count_chats_today(db),
        "info": {"name": info.get("name", WAHA_SESSION), "status": info.get("status")},
    }

@app.get("/api/waha/status")
async def waha_status(cu=Depends(get_current_user)):
    """Estado detallado de WAHA para el panel de admin."""
    try:
        info = await _waha_session_info()
        eng = info.get("engine", {})

        # Información detallada de la sesión
        session_info = {
            "name": info.get("name", WAHA_SESSION),
            "status": info.get("status", "UNKNOWN"),
            "engine": eng.get("engine", "UNKNOWN") if isinstance(eng, dict) else "UNKNOWN",
            "engine_state": eng.get("state", "UNKNOWN") if isinstance(eng, dict) else "UNKNOWN",
            "wweb_version": eng.get("WWebVersion", "") if isinstance(eng, dict) else "",
            "me": info.get("me"),  # Información del usuario conectado
            "config": info.get("config"),
            "presence": info.get("presence"),
            "timestamps": info.get("timestamps", {}),
        }

        # Determinar estado de conexión
        status_str = str(info.get("status", "")).upper()
        eng_state = str(eng.get("state", "")).upper() if isinstance(eng, dict) else ""

        connected = (
            status_str in ("WORKING", "CONNECTED", "AUTHENTICATED") or
            eng_state == "CONNECTED"
        ) and "qr" not in str(info).lower()

        prev = _last_status.get("connected")
        _last_status["connected"] = connected
        _sync_connection_timestamps(prev, connected, db)

        connected_since = _last_status.get("connected_since")
        connection_uptime_seconds = int(time.time()) - int(connected_since) if connected and connected_since else 0

        # Intentar obtener QR solo cuando WAHA realmente está en estado de escaneo
        needs_qr = not connected and status_str in ("SCAN_QR_CODE", "FAILED")
        qr_available = False
        if needs_qr:
            qr_bytes = await _waha_qr()
            qr_available = qr_bytes is not None

        # Calcular uptime aproximado (desde que inició el bot)
        uptime_seconds = int(time.time()) - int(_last_status.get("start_time", time.time()))

        return {
            "connected": connected,
            "qr_available": qr_available,
            "connected_since": connected_since,
            "connection_uptime_seconds": connection_uptime_seconds,
            "session": session_info,
            "reconnect_attempts": _waha_reconnect_attempts,
            "last_status": _last_status,
            "uptime_seconds": uptime_seconds,
            "waha_url": WAHA_URL,
            "waha_session": WAHA_SESSION,
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "waha_url": WAHA_URL,
            "waha_session": WAHA_SESSION,
        }

@app.get("/qr")
async def qr_image():
    """Obtiene el QR de WAHA para escanear.

    Solo devuelve QR cuando la sesión está esperando escaneo (SCAN_QR_CODE).
    Si la sesión ya está conectada (WORKING), devuelve 404 sin tocar nada.
    Si no hay QR pero la sesión está en estado válido, intenta recrearla.
    """
    # Verificar estado actual antes de intentar cualquier cosa
    info = await _waha_session_info()
    session_status = str(info.get("status", "")).upper()
    eng = info.get("engine", {}) if isinstance(info.get("engine"), dict) else {}
    eng_state = str(eng.get("state") or "").upper()

    already_connected = (
        session_status in ("WORKING", "CONNECTED", "AUTHENTICATED") or
        eng_state == "CONNECTED"
    )

    # Si ya está conectado no hay QR — responder 404 sin tocar la sesión
    if already_connected:
        _log(f"[QR] Sesión ya conectada (status={session_status}), sin QR")
        raise HTTPException(404, "Sesión ya conectada, no hay QR disponible")

    # STARTING: WAHA aún inicializando, no intentar rutas de QR todavía.
    if session_status == "STARTING":
        _log("[QR] WAHA en STARTING, QR aún no disponible")
        raise HTTPException(503, "QR aún no disponible, reintentá en unos segundos")

    # Intento 1: Obtener QR existente (con breve retry para WAHA inestable)
    for _ in range(3):
        b = await _waha_qr()
        if b:
            return Response(content=b, media_type="image/png")
        await asyncio.sleep(1)

    # Solo intentar recrear si la sesión está en estado problemático
    if session_status == "SCAN_QR_CODE":
        # A veces WAHA tarda en generar QR tras pasar a SCAN_QR_CODE.
        _log(f"[QR] WAHA en {session_status}, QR aún no disponible")
        raise HTTPException(503, "QR aún no disponible, reintentá en unos segundos")

    # Sesión en estado FAILED u otro estado problemático → recrear
    _logc(f"[QR] Sesión en estado {session_status}, intentando recreación...")
    ok = await _waha_delete_and_recreate()
    if ok:
        await asyncio.sleep(5)
        b = await _waha_qr()
        if b:
            _logc("[QR] QR generado exitosamente después de recreate")
            return Response(content=b, media_type="image/png")

    raise HTTPException(404, "QR no disponible - Verificar que WAHA esté corriendo")

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

async def _waha_delete_and_recreate(force: bool = False) -> bool:
    """DELETE session + POST to recreate fresh → forces QR generation."""
    global _waha_last_session_op_at

    if _waha_session_op_lock.locked():
        _log("[CONNECT] recreate omitido: operación en curso")
        return True
    if not force and _waha_session_op_recent():
        _log("[CONNECT] recreate omitido: cooldown activo")
        return True

    async with _waha_session_op_lock:
        _waha_last_session_op_at = time.time()
        c = _get_waha_client()
        try:
            rd = await c.delete(
                f"/api/sessions/{WAHA_SESSION}",
                headers=_waha_headers()
            )
            _log(f"[CONNECT] DELETE session: {rd.status_code}")
        except Exception as e:
            _log(f"[CONNECT] DELETE error (ok to ignore): {e}")

        await asyncio.sleep(1)  # let WAHA clean up before recreating

        try:
            r = await c.post(
                f"/api/sessions",
                headers=_waha_headers(),
                json={
                    "name": WAHA_SESSION,
                    "start": True,
                    "config": {
                        "ignore": {
                            "status": True,
                            "broadcast": False,
                            "groups": False,
                            "channels": False
                        }
                    }
                }
            )
            _log(f"[CONNECT] create session: {r.status_code}")
            if r.status_code < 400:
                return True  # el frontend hace polling, no necesitamos esperar aquí
        except Exception as e:
            _logc(f"[ERROR] CONNECT create: {e}")

        # Fallback: restart (dentro del mismo lock)
        try:
            r = await c.post(
                f"/api/sessions/{WAHA_SESSION}/restart",
                headers=_waha_headers(), json={}
            )
            _log(f"[CONNECT] restart fallback: {r.status_code}")
            return r.status_code < 400
        except Exception as e:
            _logc(f"[ERROR] CONNECT restart fallback: {e}")
            return False


@app.post("/bot/connect")
async def bot_connect(cu=Depends(get_current_user)):
    global _waha_last_connect_request_at

    now = time.time()
    if now - _waha_last_connect_request_at < _WAHA_CONNECT_DEBOUNCE_SEC:
        return {"ok": True, "status": "debounced"}
    _waha_last_connect_request_at = now

    if _waha_session_op_lock.locked():
        return {"ok": True, "status": "busy"}

    info = await _waha_session_info()
    status_str = str(info.get("status", "")).upper()
    _log(f"[CONNECT] session status: {status_str}")

    # STARTING → WAHA is booting; retornamos inmediato, el frontend hace polling
    if status_str == "STARTING":
        return {"ok": True, "status": status_str}

    # SCAN_QR_CODE → QR might already be valid, but could be expired.
    # Check if QR image is actually retrievable; if not, force a new one.
    if status_str == "SCAN_QR_CODE":
        qr_bytes = await _waha_qr()
        if qr_bytes:
            _log(f"[CONNECT] QR already available, reusing")
            return {"ok": True, "status": status_str}
        # QR expired → force new session
        _logc(f"[CONNECT] SCAN_QR_CODE pero QR expirado → recreando sesión")
        ok = await _waha_delete_and_recreate()
        return {"ok": ok, "status": "recreated"}

    # WORKING → simple restart (keeps stored auth, just reconnects)
    if status_str == "WORKING":
        ok = await _waha_restart_session("bot-connect-working")
        return {"ok": ok}

    # FAILED or any other state → DELETE + recreate fresh (generates QR)
    ok = await _waha_delete_and_recreate()
    return {"ok": ok}

@app.post("/bot/logout")
async def bot_logout(cu=Depends(get_current_user)):
    """Logout: DELETE session from WAHA (clears auth) then recreate stopped."""
    try:
        c = _get_waha_client()
        r = await c.delete(
            f"/api/sessions/{WAHA_SESSION}",
            headers=_waha_headers()
        )
        _log(f"[LOGOUT] DELETE session: {r.status_code}")
        return {"ok": r.status_code < 400}
    except Exception as e:
        _logc(f"[ERROR] LOGOUT: {e}")
    return {"ok": False}

# ──────────────────────────────────────────────────────────────
#  MENÚ (compatibilidad legacy)
# ──────────────────────────────────────────────────────────────
@app.get("/menu")
async def get_menu():
    return {"menu": _get_menu_cached()}

@app.post("/menu/save")
async def save_menu_legacy(req: Request, ca=Depends(get_current_admin)):
    body = await req.json(); _write_menu(body.get("menu", ""))
    _invalidate_menu_cache()    # fuerza recarga en próximo acceso
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
