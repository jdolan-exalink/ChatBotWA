# ✅ HANDOFF IMPLEMENTATION - PRINTABLE CHECKLIST

**Print this & cross off each item as you complete it**

---

## 🔧 PRE-INTEGRATION (Before Starting)

- [ ] Backup `data/chatbot.sql`
- [ ] Backup `services/clinic-bot-api/app.py`
- [ ] Backup `services/clinic-bot-api/models.py`
- [ ] Create development branch (git checkout -b handoff-state-machine)

---

## 📦 FILES TO VERIFY

### New Files (Should Exist)
- [ ] `services/clinic-bot-api/conversation_manager.py` exists
- [ ] File size ~350 lines
- [ ] Imports work: `python3 -c "from conversation_manager import ConversationManager"`

### Modified Files (Check Changes)
- [ ] `services/clinic-bot-api/models.py` has `ConversationState` table
- [ ] `services/clinic-bot-api/models.py` has `AgentAssignment` table
- [ ] `services/clinic-bot-api/models.py` has new `BotConfig` fields
- [ ] `services/clinic-bot-api/schemas.py` has `ConversationStateResponse`
- [ ] `services/clinic-bot-api/schemas.py` has `StartHandoffRequest`
- [ ] `services/clinic-bot-api/app.py` imports `ConversationManager` (line ~27)
- [ ] `services/clinic-bot-api/app.py` has `should_skip_bot_menu()` call in webhook (line ~1370)

---

## 🗄️ DATABASE SETUP

### Verify Tables Exist
```bash
sqlite3 data/chatbot.sql ".tables"
```
- [ ] Output includes `conversation_states`
- [ ] Output includes `agent_assignments`

### Verify Table Schema
```bash
sqlite3 data/chatbot.sql ".schema conversation_states"
```
- [ ] Has column: `phone_number` (UNIQUE)
- [ ] Has column: `current_state`
- [ ] Has column: `handoff_active`
- [ ] Has column: `ticket_id`

```bash
sqlite3 data/chatbot.sql ".schema agent_assignments"
```
- [ ] Table exists
- [ ] Has column: `status`
- [ ] Has column: `agent_id`

### Verify BotConfig Fields
```bash
sqlite3 data/chatbot.sql "PRAGMA table_info(bot_config);" | grep handoff
```
- [ ] Has `handoff_enabled`
- [ ] Has `handoff_inactivity_minutes`
- [ ] Has messages fields (optional)

---

## 🎯 CODE VALIDATION

### Test Imports
```bash
cd /opt/clinic-whatsapp-bot/services/clinic-bot-api
python3 << 'EOF'
from conversation_manager import ConversationManager, should_skip_bot_menu
from models import ConversationState, AgentAssignment
from schemas import ConversationStateResponse, StartHandoffRequest
print("✅ All imports successful!")
EOF
```
- [ ] No ImportError
- [ ] No SyntaxError

### Test App Loads
```bash
python3 -c "from app import app; print('✅ app.py loads OK')"
```
- [ ] No errors

### Lint Check (Optional)
```bash
python3 -m pylint conversation_manager.py --disable=all --enable=E,F
```
- [ ] No errors (only warnings OK)

---

## 🧪 FUNCTIONALITY TESTS

### Test 1: Create Conversation
```bash
python3 << 'EOF'
from database import SessionLocal
from conversation_manager import ConversationManager

db = SessionLocal()
conv = ConversationManager.get_or_create_conversation(db, "+543424438150")
assert conv.current_state == "BOT_MENU"
assert conv.phone_number == "+543424438150"
print("✅ Test 1: Create conversation - PASSED")
db.close()
EOF
```
- [ ] Test passed

### Test 2: Start Handoff
```bash
python3 << 'EOF'
from database import SessionLocal
from conversation_manager import ConversationManager
from schemas import StartHandoffRequest

db = SessionLocal()
request = StartHandoffRequest(phone_number="+543424438151")
conv = ConversationManager.start_handoff(db, request)
assert conv.current_state == "WAITING_AGENT"
assert conv.handoff_active == True
assert conv.ticket_id is not None
print("✅ Test 2: Start handoff - PASSED")
db.close()
EOF
```
- [ ] Test passed

### Test 3: Filter Returns Correct Value
```bash
python3 << 'EOF'
from database import SessionLocal
from conversation_manager import should_skip_bot_menu

db = SessionLocal()

# New user = False (use menu)
skip1 = should_skip_bot_menu(db, "+543424438200")
assert skip1 == False

# Create and handoff
from conversation_manager import ConversationManager
from schemas import StartHandoffRequest
ConversationManager.get_or_create_conversation(db, "+543424438201")
req = StartHandoffRequest(phone_number="+543424438201")
ConversationManager.start_handoff(db, req)

# In handoff = True (skip menu)
skip2 = should_skip_bot_menu(db, "+543424438201")
assert skip2 == True

print("✅ Test 3: Filter logic - PASSED")
db.close()
EOF
```
- [ ] Test passed

### Test 4: Close Handoff
```bash
python3 << 'EOF'
from database import SessionLocal
from conversation_manager import ConversationManager
from schemas import StartHandoffRequest, CloseHandoffRequest

db = SessionLocal()
req = StartHandoffRequest(phone_number="+543424438152")
ConversationManager.start_handoff(db, req)

close_req = CloseHandoffRequest(resolution="test")
conv = ConversationManager.close_handoff(db, "+543424438152", close_req)
assert conv.current_state == "CLOSED"

print("✅ Test 4: Close handoff - PASSED")
db.close()
EOF
```
- [ ] Test passed

---

## ⚙️ CONFIGURATION

### Set BotConfig
```bash
sqlite3 /opt/clinic-whatsapp-bot/data/chatbot.sql << 'EOF'
UPDATE bot_config SET
  handoff_enabled = 1,
  handoff_inactivity_minutes = 120
WHERE id = 1;
EOF
```
- [ ] Commands executed without error

### Verify Configuration
```bash
sqlite3 /opt/clinic-whatsapp-bot/data/chatbot.sql "SELECT handoff_enabled, handoff_inactivity_minutes FROM bot_config WHERE id = 1;"
```
- [ ] Output shows: 1|120 (or your configured values)

---

## 🔒 SECURITY CHECKLIST

- [ ] No hardcoded passwords in code
- [ ] No secrets in logs
- [ ] phone_number validated (starts with +)
- [ ] Database has proper FK constraints
- [ ] Agent ID validated exists before assigning

---

## 📊 PERFORMANCE CHECK

### Database Indexes
```bash
sqlite3 /opt/clinic-whatsapp-bot/data/chatbot.sql "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='conversation_states';"
```
- [ ] Has `idx_phone_number` (or similar)

### Table Sizes (Optional)
```bash
sqlite3 /opt/clinic-whatsapp-bot/data/chatbot.sql "SELECT COUNT(*) FROM conversation_states;"
```
- [ ] Query completes quickly (<1 sec)

---

## 📱 WEBHOOK INTEGRATION

### Verify Filter Location
```bash
grep -n "should_skip_bot_menu" /opt/clinic-whatsapp-bot/services/clinic-bot-api/app.py
```
- [ ] Line number found (should be ~1370)
- [ ] It's AFTER blocklist check (line ~1365)
- [ ] It's BEFORE country filter

### Check Filter Logic
```bash
grep -A 3 "should_skip_bot_menu(db" /opt/clinic-whatsapp-bot/services/clinic-bot-api/app.py | head -5
```
- [ ] Filter is called
- [ ] Followed by conditional logic

---

## 🚀 DEPLOYMENT READINESS

### Code Quality
- [ ] No TODO comments left
- [ ] No debug print statements
- [ ] All error handling in place
- [ ] Logging active

### Documentation
- [ ] HANDOFF_IMPLEMENTATION_COMPLETE.md exists
- [ ] QUICK_REFERENCE.md exists
- [ ] HANDOFF_TESTING_GUIDE.md exists

### Testing
- [ ] All 4 basic tests pass
- [ ] No unhandled exceptions
- [ ] Logging shows proper flow

### Configuration
- [ ] BotConfig updated in DB
- [ ] All required fields set
- [ ] No default values causing issues

---

## ✅ FINAL VERIFICATION

### Full Integration Test
```bash
# Simulate a complete flow
python3 << 'EOF'
from database import SessionLocal
from conversation_manager import ConversationManager, should_skip_bot_menu
from schemas import StartHandoffRequest, CloseHandoffRequest

db = SessionLocal()
phone = "+543424438999"

# 1. Create
conv = ConversationManager.get_or_create_conversation(db, phone)
print(f"1️⃣ Created: {conv.current_state}")

# 2. Check filter
skip = should_skip_bot_menu(db, phone)
print(f"2️⃣ Filter: skip={skip} (should be False)")

# 3. Start handoff
req = StartHandoffRequest(phone_number=phone)
conv = ConversationManager.start_handoff(db, req)
print(f"3️⃣ Handoff: {conv.current_state} (should be WAITING_AGENT)")

# 4. Check filter again
skip = should_skip_bot_menu(db, phone)
print(f"4️⃣ Filter: skip={skip} (should be True)")

# 5. Assign operator
conv = ConversationManager.assign_agent(db, phone, 1, "Test Operator")
print(f"5️⃣ Assigned: {conv.current_state} (should be IN_AGENT)")

# 6. Close
conv = ConversationManager.close_handoff(db, phone)
print(f"6️⃣ Closed: {conv.current_state} (should be CLOSED)")

# 7. Check filter one more time
skip = should_skip_bot_menu(db, phone)
print(f"7️⃣ Filter: skip={skip} (should be False)")

if all([
    conv.current_state == "CLOSED",
    skip == False
]):
    print("\n✅ FULL INTEGRATION TEST PASSED!")
else:
    print("\n❌ TEST FAILED")
    
db.close()
EOF
```
- [ ] All 7 steps show correct values
- [ ] Final message: ✅ FULL INTEGRATION TEST PASSED

---

## 🎉 COMPLETION CHECKLIST

- [ ] All code changes verified
- [ ] All database tables created
- [ ] All imports work
- [ ] All 4 basic tests pass
- [ ] Full integration test passes
- [ ] Configuration updated in DB
- [ ] Documentation files exist
- [ ] No errors in logs
- [ ] Ready for operator endpoints development
- [ ] Backup restored if needed (no longer needed if everything works)

---

## 📝 NOTES FOR YOUR TEAM

```
Handoff State Machine Implementation Status:

✅ COMPLETED:
- State machine with 6 states
- Database schema (2 new tables)
- Webhook integration filter
- Ticket generation system
- All core methods
- Comprehensive logging
- Full documentation
- Test suite

⏳ TODO (for next phase):
- Operator API endpoints (3-4 endpoints)
- Operator dashboard UI
- Background scheduler for auto-close
- WebSocket for real-time notifications
- Monitoring/alerting

📞 KEY CONTACT POINTS:
- State machine: ConversationManager class
- Filter: should_skip_bot_menu() function
- Database: conversation_states table
- Webhook: app.py line ~1370
```

---

## 🗂️ DOCUMENT REFERENCE

If you need to go back and check something:

| What | File |
|------|------|
| Overall status | EXECUTIVE_SUMMARY.md |
| What changed | WHAT_WAS_DELIVERED.md |
| Operator guide | HANDOFF_QUICK_START.md |
| Implementation details | HANDOFF_IMPLEMENTATION_COMPLETE.md |
| Code snippets | QUICK_REFERENCE.md |
| Step-by-step setup | INTEGRATION_CHECKLIST.md |
| Validation tests | HANDOFF_TESTING_GUIDE.md |
| Documentation index | STATE_MACHINE_HANDOFF_README.md |

---

**Print this page, complete all checkboxes, celebrate when done! 🎉**

**Expected time**: 30-45 minutes (if everything works)

---

## 🆘 If Something Fails

1. **Check logs**: grep for `[WEBHOOK]` or errors
2. **Verify imports**: `python3 -c "from conversation_manager import ..."`
3. **Check DB**: Verify tables exist
4. **Reset**: Delete test data, start over
5. **Review**: See HANDOFF_TESTING_GUIDE.md for troubleshooting

---

**CHECKLIST COMPLETE? → NEXT STEP: Build operator API endpoints using QUICK_REFERENCE.md**
