# 🚀 QUICK START - Sistema de Handoff

**Para Operarios & Administradores**

---

## 📌 ¿Qué es el Handoff?

El "handoff" significa que un usuario que estaba hablando con el bot pasa a hablar con un **operario humano** (tú).

**Flujo simple**:
```
Usuario → Bot limita menús → Espera operario → TÚ le atiendes
```

---

## 🎯 Las 6 Situaciones (Estados)

Cuando veas un usuario, estará en UNO de estos estados:

| 🔵 | Estado | ¿Qué significa? | ¿Qué hago? |
|----|----|----|----|
| 1️⃣ | `BOT_MENU` | Hablando con bot (menú normal) | ❌ No interrumpir |
| 2️⃣ | `COLLECTING_DATA` | Bot recopilando datos | ❌ No interrumpir |
| 3️⃣ | `WAITING_AGENT` | **⚠️ Esperando TU respuesta** | ✅ **ATENDER AHORA** |
| 4️⃣ | `IN_AGENT` | **👤 Ya estoy atendiendo** | ✅ Continuar |
| 5️⃣ | `CLOSED` | Operario cerró el ticket | ❌ Terminado |
| 6️⃣ | `BLACKLISTED` | **🚫 Número bloqueado** | ❌ Rechazar |

---

## 📱 Ciclo Típico

### Paso 1: Usuario solicita operario
Usuario escribe: *"Necesito hablar con un operario"*
↓
Bot reconoce y hace:
- Genera ticket: `TKT-A1B2C3D4`
- Estado → `WAITING_AGENT`
- Responde: "⏳ Buscando operario..."

### Paso 2: Tú lo recibes (en tu dashboard)
Ves en la pantalla:
```
[TKT-A1B2C3D4] +543424438150 - Cliente quiere atención
Estado: WAITING_AGENT
Datos: nombre=Juan, email=juan@...
Esperando desde: 2m 30s
```

### Paso 3: Aceptas el ticket
Haces clic en **"Aceptar Ticket"**
↓
Se ejecuta:
- Estado → `IN_AGENT`
- Tu ID se asigna
- Responde al usuario: "✅ Un operario te atiende..."

### Paso 4: Conversación
Intercambias mensajes normalmente:
- Usuario escribe
- Tú respondes
- (El bot NO interfiere)

### Paso 5: Cierras el ticket
Haces clic en **"Resolver Ticket"**
↓
Se ejecuta:
- Estado → `CLOSED`
- Responde: "Gracias por tu contacto..."
- Siguiente mensaje del usuario → vuelve al bot

---

## 🎑 Operaciones Rápidas

### ✅ Ver tickets pendientes
**Endpoint** (o panel):
```
GET /api/admin/conversations/active?state=WAITING_AGENT
```

**Respuesta**:
```json
[
  {
    "ticket_id": "TKT-A1B2C3D4",
    "phone_number": "+543424438150",
    "current_state": "WAITING_AGENT",
    "user_name": "Juan",
    "waiting_since": "2024-01-15T14:30:00Z",
    "collected_data": {
      "nombre": "Juan García",
      "email": "juan@gmail.com"
    }
  }
]
```

### ✅ Aceptar un ticket
**Endpoint**:
```
POST /api/operator/assign
Content-Type: application/json

{
  "ticket_id": "TKT-A1B2C3D4",
  "agent_id": 5,
  "agent_name": "Carlos Pérez"
}
```

**Bajo el capó**: `ConversationManager.assign_agent(...)`

### ✅ Enviar un mensaje
**Endpoint**:
```
POST /api/operator/send-message
{
  "ticket_id": "TKT-A1B2C3D4",
  "message": "Hola Juan, ¿en qué puedo ayudarte?"
}
```

### ✅ Resolver y cerrar
**Endpoint**:
```
POST /api/operator/close-ticket
{
  "ticket_id": "TKT-A1B2C3D4",
  "resolution": "Problema resuelto",
  "notes": "Cliente satisfecho"
}
```

**Bajo el capó**: `ConversationManager.close_handoff(...)`

---

## ⏱️ Auto-Cierre por Inactividad

Si un usuario **no responde en 120 minutos** (configurable):
- El bot automáticamente cierra el ticket
- Estado → `CLOSED`
- Conversación vuelve a `BOT_MENU`

**Para cambiar tiempo inactivo** (en DB):
```sql
UPDATE bot_config SET handoff_inactivity_minutes = 60 WHERE id = 1;
```
Ahora se cierra después de 1 hora sin mensajes.

---

## 🔴 Casos Especiales

### 🚫 Número Bloqueado (BLACKLISTED)

Si un número está en la lista negra:
```python
ConversationManager.set_blocked(db, "+543424438150", "Spam/acoso")
```

Efecto:
- Bot RECHAZA completamente
- No envía ningún menú
- Webhook retorna `{"status": "blacklisted"}`

**Para desbloquear**:
```python
ConversationManager.reset_to_menu(db, "+543424438150")
# Vuelve a BOT_MENU
```

### 💤 Usuario Se Queda Esperando

Si usuario envía mensaje mientras espera (`WAITING_AGENT`):
```
Usuario: "¿Cuánto más debo esperar?"
↓
Webhook recibe:
- should_skip_bot_menu(db, chat_id) = True
- Estado = WAITING_AGENT
- Responde: "⏳ Estamos buscando un operario. Por favor espera..."
↓
No le muestra menú, solo espera
```

---

## 📊 Ver Estado de Una Conversación

```sql
-- Ver conversación específica
SELECT * FROM conversation_states 
WHERE phone_number = '+543424438150';

-- Resultado:
-- id=1, phone_number=+543424438150, current_state=IN_AGENT
-- assigned_agent_id=5, ticket_id=TKT-A1B2C3D4, handoff_active=1
```

---

## 🎛️ Configuración

### Cambiar Mensajes de Respuesta Automática

En `BotConfig`:
```python
cfg.waiting_agent_message = "En breve te atiende un operario. Gracias por esperar 🙏"
cfg.in_agent_message = "Ya tienes un operario conmigo. Veamos cómo te ayudo."
cfg.closed_message = "Gracias por contactarnos. ¡Hasta pronto!"
```

---

## 🧪 Test Todo Funciona

### 1. Crear una conversación de PRUEBA:
```python
from conversation_manager import ConversationManager
from database import SessionLocal

db = SessionLocal()

# Crear conversación
conv = ConversationManager.get_or_create_conversation(db, "+543424438150")
print(f"✅ Creada: {conv.phone_number} - Estado: {conv.current_state}")

# Iniciar handoff
request = StartHandoffRequest(
    phone_number="+543424438150",
    collected_data={"nombre": "Test User"}
)
conv = ConversationManager.start_handoff(db, request)
print(f"✅ Handoff iniciado: {conv.ticket_id} - Estado: {conv.current_state}")

# Asignar operario
conv = ConversationManager.assign_agent(db, "+543424438150", agent_id=5, agent_name="TestOp")
print(f"✅ Operario asignado: {conv.assigned_agent_name} - Estado: {conv.current_state}")

# Cerrar
conv = ConversationManager.close_handoff(db, "+543424438150")
print(f"✅ Ticket cerrado - Estado: {conv.current_state}")
```

---

## 🔍 Logs para Debugging

Mira los logs de la aplicación para ver:
```
[WEBHOOK] Handoff activo para +543424438150 - saltando router de menús
[WEBHOOK] Estado WAITING_AGENT - enviando mensaje de espera
[WEBHOOK] Estado IN_AGENT con operario asignado - mensaje en modo handoff
```

---

## 📞 Flujo Resumido (1 Página)

```
1. Usuario pide operario
   ↓
2. Bot: current_state = WAITING_AGENT (generando ticket)
   ↓
3. Operario ve ticket en dashboard
   ↓
4. Operario clica "Aceptar"
   ↓
5. Bot: current_state = IN_AGENT (operario asignado)
   ↓
6. Mensajes pasan directo entre usuario ↔️ operario
   ↓
7. Operario clica "Cerrar"
   ↓
8. Bot: current_state = CLOSED
   ↓
9. Próximo mensaje del usuario vuelve a menú
```

---

**¿Preguntas?** Ver `HANDOFF_IMPLEMENTATION_COMPLETE.md` para documentación técnica completa.
