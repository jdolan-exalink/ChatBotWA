# ✅ INTEGRATION CHECKLIST - State Machine Handoff

**Verificación punto por punto de la integración**

---

## 📦 Archivos Modificados

### ✅ 1. `/services/clinic-bot-api/models.py`

**✓ Agregado**: Tabla `ConversationState`
```python
class ConversationState(Base):
    __tablename__ = "conversation_states"
    # columnas: id, phone_number (UNIQUE), current_state, handoff_active, 
    # is_blocked, assigned_agent_id, assigned_agent_name, ticket_id,
    # collected_data, metadata, started_at, last_message_at, 
    # handoff_started_at, closed_at
```
**Estado**: ✅ DONE

**✓ Agregado**: Tabla `AgentAssignment`
```python
class AgentAssignment(Base):
    __tablename__ = "agent_assignments"
    # columnas: id, conversation_id, agent_id, phone_number, ticket_id,
    # status, notes, resolution, started_at, ended_at
```
**Estado**: ✅ DONE

**✓ Modificado**: Clase `BotConfig`
```python
# Nuevas columnas:
handoff_enabled: bool = True
handoff_inactivity_minutes: int = 120
waiting_agent_message: str
in_agent_message: str
handoff_message: str
closed_message: str
```
**Estado**: ✅ DONE

---

### ✅ 2. `/services/clinic-bot-api/schemas.py`

**✓ Agregado**: `ConversationStateResponse`
```python
class ConversationStateResponse(BaseModel):
    id, phone_number, current_state, handoff_active,
    assigned_agent_id, assigned_agent_name, ticket_id,
    last_message_at, handoff_started_at, closed_at, is_blocked
```
**Estado**: ✅ DONE

**✓ Agregado**: `StartHandoffRequest`
```python
class StartHandoffRequest(BaseModel):
    phone_number: str
    collected_data: dict = None
    agent_id: int = None
    agent_name: str = None
```
**Estado**: ✅ DONE

**✓ Agregado**: `CloseHandoffRequest`
```python
class CloseHandoffRequest(BaseModel):
    phone_number: str
    resolution: str = None
    notes: str = None
```
**Estado**: ✅ DONE

**✓ Agregado**: `AgentAssignmentResponse`
```python
class AgentAssignmentResponse(BaseModel):
    ticket_id, agent_id, agent_name, status, assigned_at
```
**Estado**: ✅ DONE

---

### ✅ 3. `/services/clinic-bot-api/conversation_manager.py` (NUEVA)

**✓ Crear archivo**: `conversation_manager.py`

**✓ Implementar clase**: `ConversationManager`

**✓ Métodos implementados** (12 métodos estáticos):

| # | Método | Firma | Retorna |
|----|--------|-------|---------|
| 1 | `get_or_create_conversation` | `(db, phone_number, initial_state="BOT_MENU")` | `ConversationState` |
| 2 | `get_conversation` | `(db, phone_number)` | `ConversationState \| None` |
| 3 | `change_state` | `(db, phone_number, new_state)` | `ConversationState` |
| 4 | `reset_to_menu` | `(db, phone_number)` | `ConversationState` |
| 5 | `start_handoff` | `(db, request: StartHandoffRequest)` | `ConversationState` |
| 6 | `assign_agent` | `(db, phone_number, agent_id, agent_name)` | `ConversationState` |
| 7 | `close_handoff` | `(db, phone_number, request: CloseHandoffRequest)` | `ConversationState` |
| 8 | `collect_data` | `(db, phone_number, key, value)` | `ConversationState` |
| 9 | `update_last_message` | `(db, phone_number)` | `ConversationState` |
| 10 | `close_by_inactivity` | `(db, inactivity_minutes)` | `list[ConversationState]` |
| 11 | `set_blocked` | `(db, phone_number, reason)` | `ConversationState` |
| 12 | `to_response` | `(conv: ConversationState)` | `ConversationStateResponse` |

**✓ Función global**: `should_skip_bot_menu`
```python
def should_skip_bot_menu(db: Session, phone_number: str) -> bool:
    """Retorna True si NO debe mostrar menú"""
    # True si: BLACKLISTED o (handoff_active Y en WAITING_AGENT/IN_AGENT)
```
**Estado**: ✅ DONE

---

### ✅ 4. `/services/clinic-bot-api/app.py`

**✓ Agregado: Import**
```python
from conversation_manager import ConversationManager
```
**Ubicación**: Línea ~27 (con otros imports de módulos del proyecto)

**✓ Modificado: Webhook handler**
**Ubicación**: Línea ~1370 (después del blocklist check)

**Código insertado**:
```python
# ===== ESTADO MACHINE: FILTRO DE HANDOFF =====
should_skip_menu = ConversationManager.should_skip_bot_menu(db, chat_id)
if should_skip_menu:
    print(f"[WEBHOOK] Handoff activo para {chat_id}")
    conv = ConversationManager.get_conversation(db, chat_id)
    
    if conv and conv.current_state == "WAITING_AGENT":
        waiting_msg = cfg.waiting_agent_message or "⏳ Esperando..."
        await send_whatsapp_text(chat_id, waiting_msg)
        return {"ok": True, "status": "waiting_for_agent"}
    
    if conv and conv.current_state == "IN_AGENT":
        ConversationManager.update_last_message(db, chat_id)
        return {"ok": True, "status": "in_agent_mode"}
    
    if conv and conv.current_state == "BLACKLISTED":
        return {"ok": True, "status": "blacklisted"}
    
    return {"ok": True, "status": "handoff_active"}
```

**Orden de ejecución en webhook**:
1. Validaciones básicas ✅ (existentes)
2. Blocklist check ✅ (existente)
3. **🔑 NUEVO: Filtro handoff** ← AQUÍ
4. Filtro país ✅ (existente)
5. Filtro área ✅ (existente)
6. Off-hours ✅ (existente)
7. Router de menú ✅ (existente)

**Estado**: ✅ DONE

---

## 🔍 Verificación de Imports

### Verificar que ConversationManager importa correctamente:

```python
# En app.py (línea ~27)
from conversation_manager import ConversationManager

# En webhook (línea ~1370)
should_skip_menu = ConversationManager.should_skip_bot_menu(db, chat_id)
```

**Verificación**:
```bash
python3 -c "from conversation_manager import ConversationManager; print('✅ OK')"
```

**Resultado esperado**: ✅ OK

---

## 🗄️ Base de Datos

### Verificar tablas creadas:

```bash
sqlite3 data/chatbot.sql ".tables"
```

**Debe incluir**:
- ✅ `conversation_states`
- ✅ `agent_assignments`

### Verificar esquema:

```bash
sqlite3 data/chatbot.sql ".schema conversation_states"
```

**Debe tener índice UNIQUE**:
```sql
CREATE UNIQUE INDEX idx_phone_number ON conversation_states(phone_number);
```

---

## 🎯 Estados Validos

**Los 6 estados definidos**:

```python
STATES = {
    "BOT_MENU": "El bot guía con menús",
    "COLLECTING_DATA": "El bot recopila datos",
    "WAITING_AGENT": "Esperando asignación a operador",
    "IN_AGENT": "En conversación con operador",
    "CLOSED": "Ticket cerrado, vuelve a bot",
    "BLACKLISTED": "Número en lista negra"
}
```

---

## 🚀 Funciones Críticas

### 1. Filtro de Webhook (CRÍTICO)

```python
should_skip_bot_menu(db, chat_id) → bool
```

**¿Cuándo se ejecuta?**: En CADA mensaje del webhook
**¿Qué hace?**:
- Retorna `True` si NO debe mostrar menú
- Retorna `False` si debe mostrar menú

**Casos**:
- ✅ Usuario nuevo → `False` (usa menú)
- ✅ En `BOT_MENU` → `False` (usa menú)
- ✅ En `WAITING_AGENT` → `True` (salta menú)
- ✅ En `IN_AGENT` → `True` (salta menú)
- ✅ En `BLACKLISTED` → `True` (rechaza)

### 2. Iniciar Handoff

```python
ConversationManager.start_handoff(db, request) → ConversationState
```

**Qué hace**:
- Genera ticket: `TKT-XXXXXXXX`
- Cambia estado → `WAITING_AGENT`
- Activa flag `handoff_active = True`

**Entrada**:
```python
StartHandoffRequest(
    phone_number="+543424438150",
    collected_data={"nombre": "Juan", "email": "juan@..."},
    agent_id=5,  # opcional
    agent_name="Carlos"  # opcional
)
```

### 3. Asignar Operario

```python
ConversationManager.assign_agent(db, phone_number, agent_id, agent_name) → ConversationState
```

**Qué hace**:
- Cambia estado → `IN_AGENT`
- Asigna operario: `assigned_agent_id`, `assigned_agent_name`
- Crea registro en `AgentAssignment`

### 4. Cerrar Handoff

```python
ConversationManager.close_handoff(db, phone_number, request) → ConversationState
```

**Qué hace**:
- Cambia estado → `CLOSED`
- Desactiva flag `handoff_active = False`
- Registra timestamp `closed_at`
- Cierra `AgentAssignment`

### 5. Cierre Automático

```python
ConversationManager.close_by_inactivity(db, inactivity_minutes=120) → list[ConversationState]
```

**Qué hace**:
- Busca conversaciones sin actividad > `inactivity_minutes`
- Las cierra automáticamente
- Usa `last_message_at` para tracking

**⚠️ NOTA**: Debe ejecutarse periódicamente (cada 5-10 min):
```bash
# Opción 1: CRON externo llamando a endpoint
GET /api/admin/cleanup-inactive?minutes=120

# Opción 2: APScheduler (dentro de app.py)
# (No implementado aún, TODO)
```

---

## 📊 Flujo de Datos

### Flujo 1: Usuario Normal (BOT_MENU)

```
Usuario envía mensaje
↓
Webhook recibe: {"from": "+54...", "body": "Hola"}
↓
should_skip_bot_menu(db, "+54...") = False
↓
Mostrar menú
↓
Usuario ve opciones
```

### Flujo 2: Usuario en Handoff (WAITING_AGENT)

```
Bot hace: ConversationManager.start_handoff(db, request)
↓
Estado: WAITING_AGENT
handoff_active: True
↓
Usuario envía mensaje
↓
Webhook recibe: {"from": "+54...", "body": "¿Cuánto?"}
↓
should_skip_bot_menu(db, "+54...") = True
↓
conv.current_state = "WAITING_AGENT"
↓
Responder solo: "⏳ Estamos buscando..."
↓
NO mostrar menú
```

### Flujo 3: Usuario con Operario (IN_AGENT)

```
Operario hace: ConversationManager.assign_agent(db, "+54...", ...)
↓
Estado: IN_AGENT
assigned_agent_id: 5
↓
Usuario envía mensaje
↓
Webhook: should_skip_bot_menu = True
↓
conv.current_state = "IN_AGENT"
↓
Pasar a endpoint de operario (no mostrar menú)
↓
Operario responde
```

---

## 📋 Checklist de Integración

### Pre-Integración
- [ ] Hacer backup de `data/chatbot.sql`
- [ ] Hacer backup de `services/clinic-bot-api/app.py`

### Archivos Modificados
- [x] ✅ `models.py` - Nuevas tablas agregadas
- [x] ✅ `schemas.py` - Nuevas schemas agregadas
- [x] ✅ `conversation_manager.py` - Nuevo archivo creado
- [x] ✅ `app.py` - Import + filtro en webhook

### Post-Integración
- [ ] Ejecutar Test 1: Imports
- [ ] Ejecutar Test 2: Database
- [ ] Ejecutar Test 3: Ciclo completo
- [ ] Ejecutar Test 4: Inactividad
- [ ] Ejecutar Test 5: Filtro
- [ ] Ejecutar Test 6: Webhook

### Configuración
- [ ] Actualizar `BotConfig` en BD (handoff_enabled, messages)
- [ ] Configurar `handoff_inactivity_minutes` (default: 120)

### Endpoints a Crear (TODO)
- [ ] `POST /api/conversations/handoff/start`
- [ ] `POST /api/conversations/{phone}/assign`
- [ ] `POST /api/conversations/{phone}/close`
- [ ] `GET /api/conversations/active`
- [ ] `GET /api/admin/cleanup-inactive`

### Background Tasks (TODO)
- [ ] Scheduler para `close_by_inactivity()` c/5 min

---

## 🔧 Cambios en BD

### Migration Manual (si no está automatizado):

```sql
-- Crear tabla conversation_states
CREATE TABLE IF NOT EXISTS conversation_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number VARCHAR UNIQUE NOT NULL,
    current_state VARCHAR NOT NULL,
    handoff_active BOOLEAN DEFAULT 0,
    is_blocked BOOLEAN DEFAULT 0,
    block_reason VARCHAR,
    assigned_agent_id INTEGER,
    assigned_agent_name VARCHAR,
    ticket_id VARCHAR,
    collected_data TEXT,
    metadata TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    handoff_started_at TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE UNIQUE INDEX idx_phone_number ON conversation_states(phone_number);

-- Crear tabla agent_assignments
CREATE TABLE IF NOT EXISTS agent_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    agent_id INTEGER,
    phone_number VARCHAR,
    ticket_id VARCHAR,
    status VARCHAR,
    notes TEXT,
    resolution TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- Agregar columnas a bot_config
ALTER TABLE bot_config ADD COLUMN handoff_enabled BOOLEAN DEFAULT 1;
ALTER TABLE bot_config ADD COLUMN handoff_inactivity_minutes INTEGER DEFAULT 120;
ALTER TABLE bot_config ADD COLUMN waiting_agent_message VARCHAR;
ALTER TABLE bot_config ADD COLUMN in_agent_message VARCHAR;
ALTER TABLE bot_config ADD COLUMN handoff_message VARCHAR;
ALTER TABLE bot_config ADD COLUMN closed_message VARCHAR;
```

---

## 🧪 Test Rápido

### Test 1: Verificar imports
```bash
cd /opt/clinic-whatsapp-bot/services/clinic-bot-api
python3 -c "from conversation_manager import ConversationManager, should_skip_bot_menu; print('✅ OK')"
```

### Test 2: Verificar tablas
```bash
sqlite3 /opt/clinic-whatsapp-bot/data/chatbot.sql "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('conversation_states', 'agent_assignments');"
```

**Resultado esperado**:
```
conversation_states
agent_assignments
```

### Test 3: Probar un ciclo
```bash
python3 /tmp/test_handoff.py
```

---

## 📞 Soporte

### Si hay errores:

1. **ImportError**: Verificar que `conversation_manager.py` está en `services/clinic-bot-api/`
2. **DatabaseError**: Ejecutar migraciones SQL manualmente
3. **StateError**: Verificar que los 6 estados están bien definidos

### Logs útiles:

```
[WEBHOOK] Handoff activo para +54...  → Filtro activado
[WEBHOOK] Estado WAITING_AGENT  → Usuario esperando
[WEBHOOK] Estado IN_AGENT  → Operario atendiendo
```

---

**Documentación**: HANDOFF_IMPLEMENTATION_COMPLETE.md  
**Testing**: HANDOFF_TESTING_GUIDE.md  
**Operario**: HANDOFF_QUICK_START.md  
**Esta checklist**: INTEGRATION_CHECKLIST.md
