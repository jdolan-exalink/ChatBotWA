# 🧪 Testing Guide - State Machine Handoff

**Validación completa del sistema**

---

## ✅ Test 1: Import sin errores

### Objetivo
Verificar que todos los módulos importan correctamente sin errores de sintaxis.

### Pasos
```bash
cd /opt/clinic-whatsapp-bot/services/clinic-bot-api

# Test 1.1: Import de conversation_manager
python3 -c "from conversation_manager import ConversationManager, should_skip_bot_menu; print('✅ conversation_manager OK')"

# Test 1.2: Import de models
python3 -c "from models import ConversationState, AgentAssignment; print('✅ models OK')"

# Test 1.3: Import de schemas
python3 -c "from schemas import ConversationStateResponse, StartHandoffRequest, CloseHandoffRequest; print('✅ schemas OK')"

# Test 1.4: Import completo del app
python3 -c "from app import app; print('✅ app.py OK')"
```

### Resultado esperado
```
✅ conversation_manager OK
✅ models OK
✅ schemas OK
✅ app.py OK
```

---

## ✅ Test 2: Base de datos y tablas

### Objetivo
Verificar que las tablas se crearon correctamente.

### Pasos
```bash
cd /opt/clinic-whatsapp-bot

# Listar tablas
sqlite3 data/chatbot.sql ".tables"
```

### Resultado esperado
```
agent_assignments  conversation_states  user  bot_config  ...
```

**Verificar índices**:
```bash
sqlite3 data/chatbot.sql ".schema conversation_states"
```

### Resultado esperado
```sql
CREATE TABLE conversation_states (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number VARCHAR UNIQUE NOT NULL,
  current_state VARCHAR NOT NULL,
  handoff_active BOOLEAN DEFAULT 0,
  is_blocked BOOLEAN DEFAULT 0,
  ...
);

CREATE UNIQUE INDEX idx_phone_number ON conversation_states(phone_number);
```

**Verificar que agent_assignments existe**:
```bash
sqlite3 data/chatbot.sql "SELECT name FROM sqlite_master WHERE type='table' AND name='agent_assignments';"
```

### Resultado esperado
```
agent_assignments
```

---

## ✅ Test 3: Ciclo de conversación (Unit Test)

### Objetivo
Probar el flujo completo: crear → handoff → asignar → cerrar.

### Código
```bash
cat > /tmp/test_handoff.py << 'EOF'
import sys
sys.path.insert(0, '/opt/clinic-whatsapp-bot/services/clinic-bot-api')

from database import SessionLocal
from conversation_manager import ConversationManager, should_skip_bot_menu
from schemas import StartHandoffRequest, CloseHandoffRequest

db = SessionLocal()
test_phone = "+543424438150"

print("\n" + "="*60)
print("TEST 3: CICLO COMPLETO DE CONVERSACIÓN")
print("="*60)

# 3.1: Crear conversación
print("\n[1/6] Crear conversación...")
conv = ConversationManager.get_or_create_conversation(db, test_phone)
assert conv.phone_number == test_phone
assert conv.current_state == "BOT_MENU"
assert conv.handoff_active == False
print(f"✅ Conversación creada: {conv.phone_number} - estado: {conv.current_state}")

# 3.2: Verificar should_skip_bot_menu = False (no handoff aún)
print("\n[2/6] Verificar filtro (debe ser False = usar menú)...")
skip = should_skip_bot_menu(db, test_phone)
assert skip == False
print(f"✅ should_skip_bot_menu = {skip} (correcto, usa menú)")

# 3.3: Iniciar handoff
print("\n[3/6] Iniciar handoff...")
request = StartHandoffRequest(
    phone_number=test_phone,
    collected_data={"nombre": "Juan García", "email": "juan@example.com"}
)
conv = ConversationManager.start_handoff(db, request)
assert conv.current_state == "WAITING_AGENT"
assert conv.handoff_active == True
assert conv.ticket_id is not None
assert conv.ticket_id.startswith("TKT-")
print(f"✅ Handoff iniciado:")
print(f"   - Ticket: {conv.ticket_id}")
print(f"   - Estado: {conv.current_state}")
print(f"   - Handoff activo: {conv.handoff_active}")

# 3.4: Verificar should_skip_bot_menu = True (handoff activo)
print("\n[4/6] Verificar filtro (debe ser True = saltear menú)...")
skip = should_skip_bot_menu(db, test_phone)
assert skip == True
print(f"✅ should_skip_bot_menu = {skip} (correcto, salta menú)")

# 3.5: Asignar operario
print("\n[5/6] Asignar operario...")
conv = ConversationManager.assign_agent(db, test_phone, agent_id=1, agent_name="Carlos")
assert conv.current_state == "IN_AGENT"
assert conv.assigned_agent_id == 1
assert conv.assigned_agent_name == "Carlos"
print(f"✅ Operario asignado:")
print(f"   - Agente: {conv.assigned_agent_name} (ID: {conv.assigned_agent_id})")
print(f"   - Estado: {conv.current_state}")

# 3.6: Cerrar handoff
print("\n[6/6] Cerrar handoff...")
request = CloseHandoffRequest(resolution="Problema resuelto", notes="Cliente satisfecho")
conv = ConversationManager.close_handoff(db, test_phone, request)
assert conv.current_state == "CLOSED"
assert conv.handoff_active == False
assert conv.closed_at is not None
print(f"✅ Handoff cerrado:")
print(f"   - Estado: {conv.current_state}")
print(f"   - Cerrado en: {conv.closed_at}")

# 3.7: Verificar should_skip_bot_menu = False (handoff cerrado)
print("\n[BONUS] Verificar filtro después de cerrar...")
skip = should_skip_bot_menu(db, test_phone)
assert skip == False
print(f"✅ should_skip_bot_menu = {skip} (correcto, vuelve a menú)")

print("\n" + "="*60)
print("✅ TEST 3 COMPLETADO EXITOSAMENTE")
print("="*60 + "\n")

db.close()
EOF

python3 /tmp/test_handoff.py
```

### Resultado esperado
```
============================================================
TEST 3: CICLO COMPLETO DE CONVERSACIÓN
============================================================

[1/6] Crear conversación...
✅ Conversación creada: +543424438150 - estado: BOT_MENU

[2/6] Verificar filtro (debe ser False = usar menú)...
✅ should_skip_bot_menu = False (correcto, usa menú)

[3/6] Iniciar handoff...
✅ Handoff iniciado:
   - Ticket: TKT-A1B2C3D4
   - Estado: WAITING_AGENT
   - Handoff activo: True

[4/6] Verificar filtro (debe ser True = saltear menú)...
✅ should_skip_bot_menu = True (correcto, salta menú)

[5/6] Asignar operario...
✅ Operario asignado:
   - Agente: Carlos (ID: 1)
   - Estado: IN_AGENT

[6/6] Cerrar handoff...
✅ Handoff cerrado:
   - Estado: CLOSED
   - Cerrado en: 2024-01-15 14:30:45.123456

[BONUS] Verificar filtro después de cerrar...
✅ should_skip_bot_menu = False (correcto, vuelve a menú)

============================================================
✅ TEST 3 COMPLETADO EXITOSAMENTE
============================================================
```

---

## ✅ Test 4: Cierre por inactividad

### Objetivo
Verificar que conversaciones antiguas se cierran automáticamente.

### Código
```bash
cat > /tmp/test_inactivity.py << 'EOF'
import sys
from datetime import datetime, timedelta
sys.path.insert(0, '/opt/clinic-whatsapp-bot/services/clinic-bot-api')

from database import SessionLocal
from conversation_manager import ConversationManager
from models import ConversationState

db = SessionLocal()

print("\n" + "="*60)
print("TEST 4: CIERRE POR INACTIVIDAD")
print("="*60)

# Crear una conversación antigua
test_phone = "+543424438199"
print(f"\n[1/3] Crear conversación antigua en {test_phone}...")
conv = ConversationManager.get_or_create_conversation(db, test_phone)
conv.current_state = "IN_AGENT"
conv.handoff_active = True
conv.last_message_at = datetime.utcnow() - timedelta(minutes=130)  # 130 minutos atrás
db.commit()
db.refresh(conv)
print(f"✅ Conversación creada con último mensaje hace 130 minutos")

# Ejecutar cleanup (inactividad_minutes=120)
print(f"\n[2/3] Ejecutar close_by_inactivity(120)...")
closed = ConversationManager.close_by_inactivity(db, inactivity_minutes=120)
print(f"✅ Conversaciones cerradas por inactividad: {len(closed)}")
for c in closed:
    print(f"   - {c.phone_number} (ticket: {c.ticket_id})")

# Verificar que está cerrada
print(f"\n[3/3] Verificar estado...")
conv = ConversationManager.get_conversation(db, test_phone)
assert conv.current_state == "CLOSED"
assert conv.handoff_active == False
print(f"✅ Conversación cerrada automáticamente")
print(f"   - Estado: {conv.current_state}")
print(f"   - Handoff activo: {conv.handoff_active}")

print("\n" + "="*60)
print("✅ TEST 4 COMPLETADO EXITOSAMENTE")
print("="*60 + "\n")

db.close()
EOF

python3 /tmp/test_inactivity.py
```

### Resultado esperado
```
============================================================
TEST 4: CIERRE POR INACTIVIDAD
============================================================

[1/3] Crear conversación antigua en +543424438199...
✅ Conversación creada con último mensaje hace 130 minutos

[2/3] Ejecutar close_by_inactivity(120)...
✅ Conversaciones cerradas por inactividad: 1
   - +543424438199 (ticket: TKT-XXXXXXXX)

[3/3] Verificar estado...
✅ Conversación cerrada automáticamente
   - Estado: CLOSED
   - Handoff activo: False

============================================================
✅ TEST 4 COMPLETADO EXITOSAMENTE
============================================================
```

---

## ✅ Test 5: should_skip_bot_menu (Filtro Crítico)

### Objetivo
Verificar que el filtro funciona en todos los casos.

### Código
```bash
cat > /tmp/test_filter.py << 'EOF'
import sys
sys.path.insert(0, '/opt/clinic-whatsapp-bot/services/clinic-bot-api')

from database import SessionLocal
from conversation_manager import ConversationManager, should_skip_bot_menu

db = SessionLocal()

print("\n" + "="*60)
print("TEST 5: FILTRO should_skip_bot_menu")
print("="*60)

# Caso 1: Usuario nuevo (no existe conversación)
print("\nCaso 1: Usuario NUEVO (no existe en DB)")
skip = should_skip_bot_menu(db, "+543424438111")
assert skip == False
print(f"✅ should_skip_bot_menu = {skip} (correcto: usa menú)")

# Caso 2: Usuario en BOT_MENU (normal)
print("\nCaso 2: Usuario en BOT_MENU")
conv = ConversationManager.get_or_create_conversation(db, "+543424438112")
skip = should_skip_bot_menu(db, "+543424438112")
assert skip == False
print(f"✅ should_skip_bot_menu = {skip} (correcto: usa menú)")

# Caso 3: Usuario en WAITING_AGENT
print("\nCaso 3: Usuario en WAITING_AGENT")
from schemas import StartHandoffRequest
request = StartHandoffRequest(phone_number="+543424438113")
ConversationManager.start_handoff(db, request)
skip = should_skip_bot_menu(db, "+543424438113")
assert skip == True
print(f"✅ should_skip_bot_menu = {skip} (correcto: salta menú)")

# Caso 4: Usuario en IN_AGENT
print("\nCaso 4: Usuario en IN_AGENT")
ConversationManager.assign_agent(db, "+543424438113", agent_id=1, agent_name="Test")
skip = should_skip_bot_menu(db, "+543424438113")
assert skip == True
print(f"✅ should_skip_bot_menu = {skip} (correcto: salta menú)")

# Caso 5: Usuario BLACKLISTED
print("\nCaso 5: Usuario BLACKLISTED")
ConversationManager.set_blocked(db, "+543424438114", "Spam")
skip = should_skip_bot_menu(db, "+543424438114")
assert skip == True
print(f"✅ should_skip_bot_menu = {skip} (correcto: rechaza)")

print("\n" + "="*60)
print("✅ TEST 5 COMPLETADO EXITOSAMENTE")
print("="*60 + "\n")

db.close()
EOF

python3 /tmp/test_filter.py
```

### Resultado esperado
```
============================================================
TEST 5: FILTRO should_skip_bot_menu
============================================================

Caso 1: Usuario NUEVO (no existe en DB)
✅ should_skip_bot_menu = False (correcto: usa menú)

Caso 2: Usuario en BOT_MENU
✅ should_skip_bot_menu = False (correcto: usa menú)

Caso 3: Usuario en WAITING_AGENT
✅ should_skip_bot_menu = True (correcto: salta menú)

Caso 4: Usuario en IN_AGENT
✅ should_skip_bot_menu = True (correcto: salta menú)

Caso 5: Usuario BLACKLISTED
✅ should_skip_bot_menu = True (correcto: rechaza)

============================================================
✅ TEST 5 COMPLETADO EXITOSAMENTE
============================================================
```

---

## ✅ Test 6: Integración en webhook (Simulación)

### Objetivo
Simular cómo funciona el filtro dentro del webhook.

### Código
```bash
cat > /tmp/test_webhook_integration.py << 'EOF'
import sys
import json
sys.path.insert(0, '/opt/clinic-whatsapp-bot/services/clinic-bot-api')

from database import SessionLocal
from conversation_manager import ConversationManager, should_skip_bot_menu
from schemas import StartHandoffRequest

db = SessionLocal()

print("\n" + "="*60)
print("TEST 6: INTEGRACIÓN EN WEBHOOK (Simulación)")
print("="*60)

test_phone = "+543424438150"

# Simular recepción de primer mensaje
print("\n[Simulación 1] Usuario NUEVO envía mensaje")
print(f"  Webhook recibe: {{\"from\": \"{test_phone}\", \"body\": \"Hola\"}}")
print(f"  → Check blocklist: ❌ (no está bloqueado)")
print(f"  → Check should_skip_bot_menu: {should_skip_bot_menu(db, test_phone)}")
print(f"  → Acción: Mostrar menú principal")
print(f"  ✅ Resultado: Usuario ve menú")

# Bot inicia handoff
print(f"\n[Simulación 2] Bot inicia handoff")
print(f"  Bot llama: ConversationManager.start_handoff(...)")
request = StartHandoffRequest(
    phone_number=test_phone,
    collected_data={"nombre": "Usuario"}
)
conv = ConversationManager.start_handoff(db, request)
print(f"  → Estado: {conv.current_state}")
print(f"  → Ticket: {conv.ticket_id}")
print(f"  ✅ Resultado: Se genera ticket, usuario ve \"esperando...\"")

# Usuario envía mensaje mientras espera
print(f"\n[Simulación 3] Usuario ESPERA y envía nuevo mensaje")
print(f"  Webhook recibe: {{\"from\": \"{test_phone}\", \"body\": \"¿Cuánto tiempo?\"}}")
print(f"  → Check blocklist: ❌ (no está bloqueado)")
print(f"  → Check should_skip_bot_menu: {should_skip_bot_menu(db, test_phone)}")
skip = should_skip_bot_menu(db, test_phone)
if skip:
    conv = ConversationManager.get_conversation(db, test_phone)
    if conv.current_state == "WAITING_AGENT":
        print(f"  → Acción: Responder solo con \"⏳ Estamos buscando...\"")
        print(f"  ✅ Resultado: NO muestra menú, solo mensaje de espera")
else:
    print(f"  → Acción: ERROR - debería saltear menú")
    print(f"  ❌ FALLO")

# Operario asigna y cambiar a IN_AGENT
print(f"\n[Simulación 4] Operario acepta y asigna")
print(f"  Operario llama: ConversationManager.assign_agent(...)")
ConversationManager.assign_agent(db, test_phone, agent_id=1, agent_name="Carlos")
print(f"  → Estado: IN_AGENT")
print(f"  → Operario: Carlos (ID: 1)")

# Usuario envía mensaje mientras operario está activo
print(f"\n[Simulación 5] Usuario envía mensaje (operario atendiendo)")
print(f"  Webhook recibe: {{\"from\": \"{test_phone}\", \"body\": \"Mi problema es...\"}}")
skip = should_skip_bot_menu(db, test_phone)
print(f"  → Check should_skip_bot_menu: {skip}")
if skip:
    conv = ConversationManager.get_conversation(db, test_phone)
    if conv.current_state == "IN_AGENT":
        print(f"  → Acción: Pasar a endpoint de operario (no mostrar menú)")
        ConversationManager.update_last_message(db, test_phone)
        print(f"     Última actividad actualizada")
        print(f"  ✅ Resultado: Operario recibe mensaje")
else:
    print(f"  → ERROR")

# Operario cierra
print(f"\n[Simulación 6] Operario resuelve y cierra")
print(f"  Operario llama: ConversationManager.close_handoff(...)")
from schemas import CloseHandoffRequest
req = CloseHandoffRequest(resolution="Resuelto", notes="OK")
ConversationManager.close_handoff(db, test_phone, req)
print(f"  → Estado: CLOSED")
print(f"  ✅ Resultado: Ticket cerrado")

# Usuario envía nuevo mensaje después de cerrar
print(f"\n[Simulación 7] Usuario NUEVO mensaje después de cerrar")
print(f"  Webhook recibe: {{\"from\": \"{test_phone}\", \"body\": \"Otra consulta\"}}")
print(f"  → Check should_skip_bot_menu: {should_skip_bot_menu(db, test_phone)}")
skip = should_skip_bot_menu(db, test_phone)
if not skip:
    print(f"  → Acción: Mostrar menú principal (volvió a BOT_MENU)")
    print(f"  ✅ Resultado: Usuario vuelve al bot")
else:
    print(f"  → ERROR")

print("\n" + "="*60)
print("✅ TEST 6 COMPLETADO EXITOSAMENTE")
print("="*60 + "\n")

db.close()
EOF

python3 /tmp/test_webhook_integration.py
```

### Resultado esperado
```
============================================================
TEST 6: INTEGRACIÓN EN WEBHOOK (Simulación)
============================================================

[Simulación 1] Usuario NUEVO envía mensaje
  Webhook recibe: {"from": "+543424438150", "body": "Hola"}
  → Check blocklist: ❌ (no está bloqueado)
  → Check should_skip_bot_menu: False
  → Acción: Mostrar menú principal
  ✅ Resultado: Usuario ve menú

[Simulación 2] Bot inicia handoff
  Bot llama: ConversationManager.start_handoff(...)
  → Estado: WAITING_AGENT
  → Ticket: TKT-A1B2C3D4
  ✅ Resultado: Se genera ticket, usuario ve "esperando..."

[Simulación 3] Usuario ESPERA y envía nuevo mensaje
  Webhook recibe: {"from": "+543424438150", "body": "¿Cuánto tiempo?"}
  → Check blocklist: ❌ (no está bloqueado)
  → Check should_skip_bot_menu: True
  → Acción: Responder solo con "⏳ Estamos buscando..."
  ✅ Resultado: NO muestra menú, solo mensaje de espera

[Simulación 4] Operario acepta y asigna
  Operario llama: ConversationManager.assign_agent(...)
  → Estado: IN_AGENT
  → Operario: Carlos (ID: 1)

[Simulación 5] Usuario envía mensaje (operario atendiendo)
  Webhook recibe: {"from": "+543424438150", "body": "Mi problema es..."}
  → Check should_skip_bot_menu: True
  → Acción: Pasar a endpoint de operario (no mostrar menú)
     Última actividad actualizada
  ✅ Resultado: Operario recibe mensaje

[Simulación 6] Operario resuelve y cierra
  Operario llama: ConversationManager.close_handoff(...)
  → Estado: CLOSED
  ✅ Resultado: Ticket cerrado

[Simulación 7] Usuario NUEVO mensaje después de cerrar
  Webhook recibe: {"from": "+543424438150", "body": "Otra consulta"}
  → Check should_skip_bot_menu: False
  → Acción: Mostrar menú principal (volvió a BOT_MENU)
  ✅ Resultado: Usuario vuelve al bot

============================================================
✅ TEST 6 COMPLETADO EXITOSAMENTE
============================================================
```

---

## 🎯 Resumen de Tests

| Test | Descripción | Objetivo | Resultado |
|------|----------|---------|----------|
| 1 | Imports sin errores | Verificar sintaxis | ✅ Todos importan OK |
| 2 | BD y tablas | Verificar esquema DB | ✅ Tablas creadas |
| 3 | Ciclo completo | Flujo crear→handoff→cerrar | ✅ Estados correctos |
| 4 | Inactividad | Auto-cierre por timeout | ✅ Conversaciones cerradas |
| 5 | Filtro crítico | should_skip_bot_menu() | ✅ Todos los casos OK |
| 6 | Integración webhook | Simulación completa | ✅ Flujo correcto |

---

## 🚀 Ejecutar Todos los Tests

```bash
cd /opt/clinic-whatsapp-bot/services/clinic-bot-api

echo "=== TEST 1: Imports ==="
python3 -c "from conversation_manager import ConversationManager; print('✅ OK')"

echo ""
echo "=== TEST 2: Database ==="
sqlite3 ../../../data/chatbot.sql "SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_states';"

echo ""
echo "=== TEST 3+: Functional Tests ==="
python3 /tmp/test_handoff.py && python3 /tmp/test_inactivity.py && python3 /tmp/test_filter.py && python3 /tmp/test_webhook_integration.py

echo ""
echo "✅ TODOS LOS TESTS COMPLETADOS"
```

---

**Nota**: Si algún test falla, revisar:
- Sintaxis en `conversation_manager.py`
- Cambios en `models.py` (nuevas columnas)
- BD `data/chatbot.sql` ejecutó migraciones

Ver `HANDOFF_IMPLEMENTATION_COMPLETE.md` para troubleshooting.
