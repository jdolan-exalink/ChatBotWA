# 🚀 Implementación Completa: State Machine para Bot→Human Handoff

**Fecha**: 2024 | **Estado**: ✅ COMPLETADO | **Versión**: 1.0

---

## 📋 Resumen Ejecutivo

Se ha implementado un **sistema de gestión de estados (State Machine)** completo para facilitar la transición de conversaciones entre el bot automatizado y operarios humanos, con soporte para:

- ✅ 6 estados de conversación bien definidos
- ✅ Filtro crítico en webhook para saltear menú durante handoff
- ✅ Generación automática de tickets (TKT-XXXXXXXX)
- ✅ Cierre automático por inactividad (configurable)
- ✅ Marcaje de números bloqueados
- ✅ Persistencia en base de datos de todos los estados

---

## 🎯 Los 6 Estados y Sus Transiciones

```
BOT_MENU (por defecto)
    ↓↑
COLLECTING_DATA (bot recopila datos)
    ↓
WAITING_AGENT (esperando asignación)
    ↓
IN_AGENT (operario atendiendo)
    ↓
CLOSED (ticket cerrado)

BLACKLISTED (número bloqueado) ← desde cualquier estado
```

### Descripción de cada estado:

| Estado | Descripción | Menú Activo | Mensajes Pasados al Operario |
|--------|-------------|-----------|-----|
| **BOT_MENU** | Bot muestra menú principal (por defecto) | ✅ Sí | ❌ No |
| **COLLECTING_DATA** | Bot recopila datos en formularios | ✅ Sí | ❌ No |
| **WAITING_AGENT** | Usuario espera asignación a operario | ❌ No, envía "esperando..." | ❌ No |
| **IN_AGENT** | Operario atendiendo, mensajes se pasan | ❌ No | ✅ Sí |
| **CLOSED** | Ticket cerrado, vuelve a BOT_MENU | ✅ Sí | ❌ No |
| **BLACKLISTED** | Número bloqueado, no responde | ❌ No | ❌ No |

---

## 📂 Archivos Modificados

### 1. **models.py** - Nuevas Tablas
Se agregaron dos nuevas tablas SQLAlchemy:

#### `ConversationState` (tabla principal)
```python
class ConversationState(Base):
    __tablename__ = "conversation_states"
    
    id: int (PK)
    phone_number: str (UNIQUE, INDEX) ← Identificador principal
    current_state: str                  ← BOT_MENU|COLLECTING_DATA|WAITING_AGENT|IN_AGENT|CLOSED|BLACKLISTED
    handoff_active: bool                ← True si está en handoff
    is_blocked: bool                    ← True si está bloqueado
    block_reason: str                   ← Razón del bloqueo
    
    # Asignación de operario
    assigned_agent_id: int              ← FK a User.id
    assigned_agent_name: str            ← Nombre del operario
    
    # Tracking
    ticket_id: str                      ← TKT-XXXXXXXX (único por conversación)
    collected_data: JSON                ← Datos recopilados {key: value}
    metadata: JSON                      ← Información contextual
    
    # Timestamps
    started_at: datetime                ← Cuándo comenzó
    last_message_at: datetime           ← Último mensaje (para inactividad)
    handoff_started_at: datetime        ← Cuándo comenzó handoff
    closed_at: datetime                 ← Cuándo se cerró
```

#### `AgentAssignment` (tabla de seguimiento de operarios)
```python
class AgentAssignment(Base):
    __tablename__ = "agent_assignments"
    
    id: int (PK)
    conversation_id: int (FK)           ← Conversación relacionada
    agent_id: int (FK)                  ← Operario asignado
    phone_number: str                   ← Número del usuario
    ticket_id: str                      ← Número de ticket (dupe para query rápido)
    status: str                         ← ASSIGNED|IN_PROGRESS|CLOSED
    notes: str                          ← Notas del operario
    resolution: str                     ← Cómo se resolvió
    
    # Timestamps
    started_at: datetime                ← Cuándo comenzó la asignación
    ended_at: datetime                  ← Cuándo finalizó
```

### 2. **schemas.py** - Validation Schemas (Pydantic)
Se agregaron nuevas schemas para validación:

```python
class ConversationStateResponse:
    id, phone_number, current_state, handoff_active, 
    assigned_agent_id, assigned_agent_name, ticket_id,
    last_message_at, handoff_started_at, closed_at, is_blocked

class StartHandoffRequest:
    phone_number: str                   ← Requerido
    collected_data: dict                ← Datos al iniciar handoff
    agent_id: int (opcional)            ← Operario (si se asigna directo)
    agent_name: str (opcional)

class CloseHandoffRequest:
    phone_number: str
    resolution: str (opcional)          ← Cómo se resolvió
    notes: str (opcional)               ← Notas del operario

class AgentAssignmentResponse:
    ticket_id, agent_id, agent_name, status, assigned_at
```

### 3. **conversation_manager.py** - Nueva Clase Gestor (NUEVO FILE)
Archivo nuevo con 12 métodos estáticos que implementan toda la lógica de estado:

```python
class ConversationManager:
    
    # ===== LECTURAS =====
    @staticmethod
    def get_or_create_conversation(db, phone_number, initial_state="BOT_MENU")
        → ConversationState (crea si no existe)
    
    @staticmethod
    def get_conversation(db, phone_number) 
        → ConversationState | None
    
    @staticmethod
    def should_skip_bot_menu(db, phone_number) 
        → bool (🔑 FILTRO CRÍTICO para webhook)
    
    # ===== TRANSICIONES DE ESTADO =====
    @staticmethod
    def change_state(db, phone_number, new_state) 
        → ConversationState (con logging)
    
    @staticmethod
    def reset_to_menu(db, phone_number) 
        → ConversationState (vuelve a BOT_MENU)
    
    # ===== FLUJO HANDOFF =====
    @staticmethod
    def start_handoff(db, request: StartHandoffRequest) 
        → ConversationState (WAITING_AGENT + ticket)
    
    @staticmethod
    def assign_agent(db, phone_number, agent_id, agent_name) 
        → ConversationState (IN_AGENT + AgentAssignment)
    
    @staticmethod
    def close_handoff(db, phone_number, request) 
        → ConversationState (CLOSED)
    
    # ===== DATOS Y CICLO =====
    @staticmethod
    def collect_data(db, phone_number, key, value) 
        → ConversationState (acumula JSON)
    
    @staticmethod
    def update_last_message(db, phone_number)
        → ConversationState (reset timer inactividad)
    
    @staticmethod
    def close_by_inactivity(db, inactivity_minutes)
        → list[ConversationState] (cierra abandonadas)
    
    @staticmethod
    def set_blocked(db, phone_number, reason)
        → ConversationState (BLACKLISTED)
    
    # ===== RESPUESTAS =====
    @staticmethod
    def to_response(conv: ConversationState)
        → ConversationStateResponse (serialization)


# ===== FUNCIÓN GLOBAL =====
def should_skip_bot_menu(db: Session, phone_number: str) -> bool:
    """
    Filtro CRÍTICO para el webhook
    Retorna True = SALTEAR menú, False = usar menú
    """
    # True si: BLACKLISTED o (handoff_active Y en WAITING_AGENT/IN_AGENT)
```

### 4. **app.py** - Integración Webhook
Se modificó el webhook handler para integrar el filtro:

**Ubicación**: Línea ~1370 (DESPUÉS del blocklist check, ANTES del country filter)

**Código agregado**:
```python
# Import en el top del archivo
from conversation_manager import ConversationManager

# En el webhook (línea ~1370):
should_skip_menu = ConversationManager.should_skip_bot_menu(db, chat_id)
if should_skip_menu:
    print(f"[WEBHOOK] Handoff activo para {chat_id}")
    conv = ConversationManager.get_conversation(db, chat_id)
    
    if conv and conv.current_state == "WAITING_AGENT":
        # Enviar "estamos buscando operario"
        await send_whatsapp_text(chat_id, waiting_msg)
        return {"ok": True, "status": "waiting_for_agent"}
    
    if conv and conv.current_state == "IN_AGENT":
        # Registrar actividad, pasar a endpoint de operario
        ConversationManager.update_last_message(db, chat_id)
        return {"ok": True, "status": "in_agent_mode"}
    
    # ... (casos CLOSED, BLACKLISTED)
    return {"ok": True, "status": "handoff_active"}
```

### 5. **BotConfig** (enhancedModelo de Configuración)
Se agregaron estos parámetros configurables:

```python
class BotConfig:
    # Handoff settings
    handoff_enabled: bool = True
    handoff_inactivity_minutes: int = 120  # Auto-close después de 120 min inactivos
    
    # Mensajes personalizables
    waiting_agent_message: str = "⏳ Estamos buscando un operario..."
    in_agent_message: str = "✅ Te atiende un operario en breve..."
    handoff_message: str = "Iniciando transferencia a operario..."
    closed_message: str = "Gracias por tu contacto. Estamos listos para ayudarte nuevamente."
```

---

## 🔑 El Filtro Crítico: `should_skip_bot_menu()`

Este es el **corazón** del sistema. Se ejecuta EN CADA MENSAJE del webhook, ANTES de cualquier lógica de menú:

```python
def should_skip_bot_menu(db: Session, phone_number: str) -> bool:
    conv = ConversationManager.get_conversation(db, phone_number)
    
    if not conv:
        return False  # Nuevo usuario, usar menú
    
    # REGLA 1: Si está bloqueado, no responder
    if conv.current_state == "BLACKLISTED" or conv.is_blocked:
        return True
    
    # REGLA 2: Si está en handoff ACTIVO, saltear menú
    if conv.handoff_active and conv.current_state in ["WAITING_AGENT", "IN_AGENT"]:
        return True
    
    return False  # Por defecto, usar menú
```

**Orden de ejecución en webhook**:
1. ✅ Validaciones básicas (fromMe, grupo, estado, sin texto)
2. ✅ Blocklist check (tabla WhatsAppBlockList)
3. **🔑 AQUÍ: Filtro handoff** (NEW - 2024)
4. ✅ filtro país (country_filter_enabled)
5. ✅ Filtro área (area_filter_enabled)
6. ✅ Off-hours (MenuF.MD)
7. ✅ Router de menú (kb_text())

---

## 📊 Flujo de Conversación Típica

### Escenario: Usuario → Bot → Operario

```
1️⃣  Usuario envía mensaje
    ↓
2️⃣  Webhook recibe mensaje
    ↓
3️⃣  NUEVA: Check should_skip_bot_menu()
    └─→ False (primer mensaje) → continuar
    ↓
4️⃣  Mostrar menú principal (BOT_MENU)
    ↓
5️⃣  Usuario selecciona opción
    ↓
6️⃣  Bot puede:
    a) Responder directamente
    b) Cambiar a COLLECTING_DATA y pedir datos
    ↓
7️⃣  Bot determina: "necesita operario"
    ↓
8️⃣  Bot llama: start_handoff()
    └─→ state = WAITING_AGENT
    └─→ ticket = TKT-A1B2C3D4
    └─→ handoff_active = True
    ↓
9️⃣  Usuario envía mensaje mientras espera
    ↓
🔟 NUEVA: should_skip_bot_menu() = True (handoff activo)
    ↓
🔑 Webhook responde con mensaje de espera
    └─→ "Estamos buscando operario..."
    ↓
1️⃣1️⃣ Operario ve ticket
    ↓
1️⃣2️⃣ Operario acepta y llama: assign_agent()
    └─→ state = IN_AGENT
    └─→ assigned_agent_id = 5
    └─→ AgentAssignment.status = IN_PROGRESS
    ↓
1️⃣3️⃣ Usuario envía mensaje
    ↓
1️⃣4️⃣ should_skip_bot_menu() = True
    ↓
1️⃣5️⃣ Webhook registra en IN_AGENT, pasa a endpoint de operario
    ↓
1️⃣6️⃣ Operario responde (en panel aparte)
    ↓
1️⃣7️⃣ Operario resuelve y llama: close_handoff()
    └─→ state = CLOSED
    └─→ handoff_active = False
    └─→ AgentAssignment.status = CLOSED
    ↓
1️⃣8️⃣ Usuario envía nuevo mensaje
    ↓
1️⃣9️⃣ should_skip_bot_menu() = False (handoff cerrado)
    ↓
2️⃣0️⃣ Vuelve a mostrar menú (BOT_MENU)
```

---

## 🛠️ Configuración Necesaria

### En BotConfig (tabla bot_config en DB):

```sql
UPDATE bot_config SET
  handoff_enabled = 1,                                      -- Habilitar/deshabilitar handoff
  handoff_inactivity_minutes = 120,                         -- Minutes inactivity before auto-close
  waiting_agent_message = '⏳ Estamos buscando un operario para atenderte...',
  in_agent_message = '✅ Un operario te está atendiendo ahora.',
  handoff_message = '📞 Iniciando transferencia a operario...',
  closed_message = 'Gracias por tu contacto. ¡Que tengas un buen día!'
WHERE id = 1;
```

---

## ⏱️ Cierre Automático por Inactividad

El método `close_by_inactivity()` busca conversaciones antiguas:

```python
# Cierra automaaticamente las conversaciones sin actividad
abandoned = ConversationManager.close_by_inactivity(db, inactivity_minutes=120)
# Retorna lista de conversaciones cerradas
```

**Requerimiento**: Este método debe llamarse periódicamente (cada 5-10 minutos) via:
- ❌ APScheduler (fondo)
- ❌ Background task de FastAPI
- ✅ Endpoint GET `/api/admin/cleanup-inactive` llamado por CRON externo

---

## 📡 Endpoints Futuros Recomendados

Para completar el sistema, se sugiere crear:

### 1. Operario (Human-Facing)
```
POST /api/operator/receive-message
├─ Recibe un mensaje de usuario en WAITING_AGENT/IN_AGENT
├─ Notifica al operario en tiempo real (WebSocket o polling)

POST /api/operator/send-message
├─ Operario envía respuesta a usuario
├─ Actualiza AgentAssignment.last_activity_at
```

### 2. Admin
```
GET /api/admin/conversations/active
├─ Lista conversaciones en handoff (WAITING_AGENT, IN_AGENT)

GET /api/admin/conversations/{phone_number}
├─ Detalle de conversación, historial, operario asignado

POST /api/admin/conversations/{phone_number}/handoff/start
├─ Inicia handoff manual para un número

POST /api/admin/conversations/{phone_number}/close
├─ Cierra manualmente una conversación

GET /api/admin/cleanup-inactive?minutes=120
├─ Ejecuta cierre por inactividad (para CRON)
```

### 3. Public API
```
GET /api/conversations/{phone_number}/status
├─ Estado actual (para integraciones externas)
```

---

## 🧪 Testing Básico

Para verificar que funciona:

```bash
# 1. Verificar que las tablas existen
sqlite3 data/chatbot.sql ".tables"
# → debe mostrar conversation_states y agent_assignments

# 2. Verificar import sin errores
cd services/clinic-bot-api
python -c "from conversation_manager import ConversationManager; print('✅ OK')"

# 3. Verificar que app.py carga sin errores
python -m pytest app.py --collect-only
# o
python app.py  # debería iniciar sin errores de import
```

---

## 🔍 Debugging

### Logs importantes:
- `[WEBHOOK] Handoff activo para +543424438150` → Filtro activado
- `[WEBHOOK] Estado WAITING_AGENT - enviando mensaje de espera` → Usuario esperando
- `[WEBHOOK] Estado IN_AGENT con operario asignado` → Operario atendiendo

### Queries útiles:
```sql
-- Ver conversaciones activas en handoff
SELECT phone_number, current_state, assigned_agent_id, ticket_id 
FROM conversation_states 
WHERE handoff_active = 1;

-- Ver tickets cerrados por inactividad
SELECT ticket_id, phone_number, closed_at 
FROM conversation_states 
WHERE current_state = 'CLOSED' 
ORDER BY closed_at DESC 
LIMIT 10;

-- Ver operarios más activos
SELECT agent_id, COUNT(*) as tickets_cerrados 
FROM agent_assignments 
WHERE status = 'CLOSED' 
GROUP BY agent_id 
ORDER BY tickets_cerrados DESC;
```

---

## ✅ Checklist de Implementación

- [x] Nnuevas tablas: ConversationState, AgentAssignment
- [x] Nuevas schemas Pydantic
- [x] Clase ConversationManager con 12 métodos
- [x] Filtro should_skip_bot_menu() en webhook
- [x] Import en app.py
- [x] Configuración en BotConfig
- [x] Logging en DEBUG para troubleshooting
- [ ] Endpoints para operarios (TODO)
- [ ] Endpoints para admin (TODO)
- [ ] Scheduler para inactivity cleanup (TODO)
- [ ] Dashboard de tickets activos (TODO)
- [ ] Tests unitarios (TODO)

---

## 📚 Próximos Pasos

1. **Pruebas**: Simular un flujo completo bot → operario → cerrado
2. **Endpoints de operario**: Crear interfaz para que operarios reciban/envíen mensajes
3. **Scheduler**: Programar `close_by_inactivity()` cada 5 min
4. **Dashboard**: UI para admin ver tickets activos y cerrados
5. **Documentación de operario**: Guía de cómo usar el sistema

---

**Documentación generada**: 2024  
**Responsable**: Sistema de Handoff - Clinic Bot v2024  
**Soporte**: Ver CHANGELOG.md para cambios recientes
