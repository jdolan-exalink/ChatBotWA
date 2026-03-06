# 🔥 QUICK REFERENCE - Handoff State Machine

**Copy-paste ready code snippets**

---

## 🔴 OPCIÓN 99 - CHATEAR CON OPERADOR (Para Usuarios)

**El usuario simplemente escribe:**
```
99
```

**¿Qué sucede automáticamente?**
1. Webhook detecta el "99"
2. `get_menu_section()` retorna ("handoff_request", "handoff")
3. Se ejecuta `ConversationManager.start_handoff()`
4. Se genera ticket automático (TKT-XXXXXXXX)
5. Usuario recibe confirmación con ticket
6. Entra en modo WAITING_AGENT (sin menú)
7. Operario puede aceptar y atender

**El usuario VE:**
```
Usuario: 99

Bot: 📞 **Se ha iniciado transferencia a un operador**
     ✅ Tu número de ticket: TKT-A1B2C3D4
     ⏳ Por favor espera a que un operario se comunique contigo.
```

📖 **Documentación completa**: [OPCION_99_OPERADOR.md](OPCION_99_OPERADOR.md)

---

## 🎯 The One Filter That Controls Everything

```python
# Put this in your webhook BEFORE showing any menu
from conversation_manager import ConversationManager

if ConversationManager.should_skip_bot_menu(db, chat_id):
    # User is in handoff - DON'T show menu
    # Handle as: waiting, in_agent, or blacklisted
    pass
else:
    # User is normal - SHOW menu
    show_menu()
```

---

## 📱 How to Initiate Handoff

### In your bot logic (when user asks for operator):

```python
from conversation_manager import ConversationManager
from schemas import StartHandoffRequest

# Create handoff request
request = StartHandoffRequest(
    phone_number="+543424438150",
    collected_data={
        "nombre": user_name,
        "email": user_email,
        "consulta": user_query
    }
    # agent_id and agent_name are optional
)

# Initiate handoff
conv = ConversationManager.start_handoff(db, request)

# Now conv has:
# - current_state = "WAITING_AGENT"
# - ticket_id = "TKT-A1B2C3D4" (auto-generated)
# - handoff_active = True
# - collected_data = {"nombre": "...", ...}

# Respond to user
await send_whatsapp_text(chat_id, 
    "📞 Estamos iniciando tu transferencia a un operario... "
    f"Número de ticket: {conv.ticket_id}"
)
```

---

## 👤 How Operator Accepts Ticket

### In operator dashboard/API:

```python
from conversation_manager import ConversationManager

# Operator clicks "Accept" for ticket TKT-A1B2C3D4
phone_number = "+543424438150"
agent_id = 5  # The operator's user.id
agent_name = "Carlos Pérez"

# Assign operator
conv = ConversationManager.assign_agent(db, phone_number, agent_id, agent_name)

# Now conv has:
# - current_state = "IN_AGENT"
# - assigned_agent_id = 5
# - assigned_agent_name = "Carlos Pérez"
# - AgentAssignment record created

# Respond to user
await send_whatsapp_text(phone_number,
    f"✅ Un operario te atiende: {agent_name}"
)

# And notify operator (WebSocket or polling)
notify_operator(agent_id, f"Ticket {conv.ticket_id} asignado a ti")
```

---

## 💬 How Messages Flow During Handoff

### In webhook, when user sends message during IN_AGENT state:

```python
from conversation_manager import ConversationManager

# User sends message
text = msg.get("body")
chat_id = msg.get("from")

# Check if in handoff
if ConversationManager.should_skip_bot_menu(db, chat_id):
    conv = ConversationManager.get_conversation(db, chat_id)
    
    if conv.current_state == "IN_AGENT":
        # Update activity timer (for inactivity auto-close)
        ConversationManager.update_last_message(db, chat_id)
        
        # Forward message to operator (via separate endpoint)
        forward_to_operator(chat_id, text)
        
        # Don't show menu
        return {"ok": True, "status": "forwarded_to_operator"}
```

---

## ❌ How to Close/Resolve Handoff

### In operator dashboard when operator clicks "Resolve":

```python
from conversation_manager import ConversationManager
from schemas import CloseHandoffRequest

phone_number = "+543424438150"

# Create close request
request = CloseHandoffRequest(
    phone_number=phone_number,
    resolution="Problema resuelto - usuario satisfecho",
    notes="Se explicó el proceso de facturación"
)

# Close handoff
conv = ConversationManager.close_handoff(db, phone_number, request)

# Now conv has:
# - current_state = "CLOSED"
# - handoff_active = False
# - closed_at = datetime.now()
# - AgentAssignment.status = "CLOSED"

# Respond to user
await send_whatsapp_text(phone_number,
    "✅ Tu consulta ha sido resuelta. "
    "Gracias por comunicarte con nosotros. "
    "Puedes volver a contactarnos cuando quieras."
)
```

---

## 🚫 How to Block a Number

```python
from conversation_manager import ConversationManager

phone_number = "+543424438150"

# Block a user
conv = ConversationManager.set_blocked(db, phone_number, "Spam/acoso")

# Now conv has:
# - current_state = "BLACKLISTED"
# - is_blocked = True
# - block_reason = "Spam/acoso"

# If there was handoff active, it closes it automatically
# Webhook will reject messages from this number
```

---

## 🔄 How to Unblock a Number

```python
from conversation_manager import ConversationManager

phone_number = "+543424438150"

# Reset to menu (unblock)
conv = ConversationManager.reset_to_menu(db, phone_number)

# Now conv has:
# - current_state = "BOT_MENU"
# - handoff_active = False
# - is_blocked = False

# User can now use bot again
```

---

## ⏱️ How to Auto-Close Inactive Conversations

### Run periodically (every 5-10 minutes):

```python
from conversation_manager import ConversationManager

# Get BotConfig for inactivity time
cfg = get_bot_config(db)
inactivity_minutes = cfg.handoff_inactivity_minutes  # default 120

# Close conversations inactive for > inactivity_minutes
closed = ConversationManager.close_by_inactivity(db, inactivity_minutes)

# Returns list of closed conversations
for conv in closed:
    print(f"Closed: {conv.phone_number} (ticket: {conv.ticket_id})")
    # Optionally notify admin
    log_to_admin(f"Conversión {conv.ticket_id} cerrada por inactividad")
```

### Option 1: CRON external job
```bash
# In crontab (every 5 minutes):
*/5 * * * * curl "https://yourapi.com/api/cleanup-inactive?minutes=120" 
```

### Option 2: APScheduler in FastAPI
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def cleanup_task():
    try:
        db = SessionLocal()
        closed = ConversationManager.close_by_inactivity(db, 120)
        db.close()
    except Exception as e:
        print(f"Cleanup error: {e}")

scheduler.add_job(cleanup_task, 'interval', minutes=5)
scheduler.start()

# Add this to your app startup
@app.on_event("startup")
async def startup_event():
    scheduler.start()
```

---

## 📊 How to Get Conversation State

```python
from conversation_manager import ConversationManager

phone_number = "+543424438150"

# Get conversation (creates if not exists)
conv = ConversationManager.get_or_create_conversation(db, phone_number)

# Check state
print(f"State: {conv.current_state}")
print(f"Handoff active: {conv.handoff_active}")
print(f"Assigned agent: {conv.assigned_agent_name}")
print(f"Ticket: {conv.ticket_id}")
print(f"Last message: {conv.last_message_at}")

# Convert to API response
from conversation_manager import ConversationManager
response = ConversationManager.to_response(conv)
# response is now a ConversationStateResponse (Pydantic model)
```

---

## 📈 How to Track Conversation Data

```python
from conversation_manager import ConversationManager

phone_number = "+543424438150"

# Collect data during conversation
ConversationManager.collect_data(db, phone_number, "product_name", "Plan Basic")
ConversationManager.collect_data(db, phone_number, "issue_type", "Billing")

# Later, get the conversation
conv = ConversationManager.get_conversation(db, phone_number)
collected = json.loads(conv.collected_data)
print(collected)
# Output: {"product_name": "Plan Basic", "issue_type": "Billing"}
```

---

## 🔧 Configuration (BotConfig)

```python
# Set configuration in database
cfg = get_bot_config(db)

# Handoff settings
cfg.handoff_enabled = True
cfg.handoff_inactivity_minutes = 120  # Auto-close after 2 hours

# Messages
cfg.waiting_agent_message = "⏳ Estamos buscando un operario..."
cfg.in_agent_message = "✅ Un operario te atiende ahora."
cfg.handoff_message = "📞 Transferencia iniciada..."
cfg.closed_message = "Gracias por tu contacto."

db.commit()
```

---

## 🧪 Quick Test

```python
from database import SessionLocal
from conversation_manager import ConversationManager, should_skip_bot_menu

db = SessionLocal()

# Test 1: New user
skip = should_skip_bot_menu(db, "+5431234567890")
assert skip == False  # Should use menu for new user

# Test 2: Start handoff
from schemas import StartHandoffRequest
request = StartHandoffRequest(phone_number="+5431234567890")
conv = ConversationManager.start_handoff(db, request)
assert conv.current_state == "WAITING_AGENT"

# Test 3: Check filter now returns True
skip = should_skip_bot_menu(db, "+5431234567890")
assert skip == True  # Should skip menu during handoff

# Test 4: Assign operator
conv = ConversationManager.assign_agent(db, "+5431234567890", 5, "Carlos")
assert conv.current_state == "IN_AGENT"

# Test 5: Close
conv = ConversationManager.close_handoff(db, "+5431234567890")
assert conv.current_state == "CLOSED"

# Test 6: Filter returns False again
skip = should_skip_bot_menu(db, "+5431234567890")
assert skip == False  # Menu shows again after close

print("✅ All tests passed!")
```

---

## 🚨 Error Handling

```python
from conversation_manager import ConversationManager

try:
    conv = ConversationManager.start_handoff(db, request)
except Exception as e:
    print(f"Error starting handoff: {e}")
    # Log and notify admin
    notify_admin(f"Handoff error: {str(e)}")
    # Don't crash - respond to user
    await send_whatsapp_text(chat_id, 
        "Oops, error procesando tu solicitud. "
        "Por favor intenta de nuevo."
    )
```

---

## 📝 Common Patterns

### Pattern 1: Async wrapper
```python
async def start_handoff_async(db: Session, request):
    conv = ConversationManager.start_handoff(db, request)
    await send_whatsapp_text(
        request.phone_number,
        f"📞 Iniziando transferencia... TKT: {conv.ticket_id}"
    )
    return conv
```

### Pattern 2: Webhook integration
```python
# In your webhook handler
should_skip = ConversationManager.should_skip_bot_menu(db, chat_id)

if should_skip:
    conv = ConversationManager.get_conversation(db, chat_id)
    state = conv.current_state
    
    if state == "WAITING_AGENT":
        await send_whatsapp_text(chat_id, "⏳ Esperando operario...")
    elif state == "IN_AGENT":
        await forward_to_operator(chat_id, text)
    elif state == "BLACKLISTED":
        # Don't respond
        pass
    
    return {"ok": True}

# Normal menu
show_menu()
```

### Pattern 3: API endpoint
```python
@app.post("/api/op/accept-ticket")
async def accept_ticket(request: dict, db: Session = Depends(get_db)):
    phone = request["phone_number"]
    agent_id = request["agent_id"]
    
    conv = ConversationManager.assign_agent(db, phone, agent_id, "Operator")
    
    return {
        "ok": True,
        "ticket_id": conv.ticket_id,
        "state": conv.current_state
    }
```

---

## 🔍 Debugging Checklist

- [ ] Import works: `from conversation_manager import ConversationManager`
- [ ] Filter in webhook: `should_skip_bot_menu(db, chat_id)`
- [ ] Table exists: Check `sqlite3 .tables | grep conversation_states`
- [ ] State is valid: One of BOT_MENU, COLLECTING_DATA, WAITING_AGENT, IN_AGENT, CLOSED, BLACKLISTED
- [ ] Logs show: `[WEBHOOK] Handoff activo`
- [ ] Phone format: "+543424438150" (with +)
- [ ] Agent exists: Check `SELECT id FROM user WHERE id = agent_id`

---

## 📞 If It's Not Working

1. **Check import**: `python3 -c "from conversation_manager import ConversationManager"`
2. **Check DB**: `sqlite3 data/chatbot.sql "SELECT COUNT(*) FROM conversation_states;"`
3. **Check state**: `SELECT current_state FROM conversation_states WHERE phone_number = '+54...';`
4. **Check logs**: Look for `[WEBHOOK] Handoff activo` or error messages
5. **Reset all**: 
   ```python
   ConversationManager.reset_to_menu(db, "+54...")
   ```

---

**More details**: See HANDOFF_IMPLEMENTATION_COMPLETE.md  
**Full guide**: See HANDOFF_QUICK_START.md  
**Testing**: See HANDOFF_TESTING_GUIDE.md
