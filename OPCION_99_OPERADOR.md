# 🔴 OPCIÓN 99 - Chatear con un Operador

**Feature Completo: Transferencia Inmediata a Operario Humano**

---

## 📋 Resumen

Se ha agregado la **opción 99** en el menú principal del bot que permite a los usuarios solicitar hablar con un operario real de forma inmediata.

Cuando el usuario escribe:
```
99
```

El bot:
1. ✅ Reconoce la solicitud
2. ✅ Genera un ticket único (TKT-XXXXXXXX)
3. ✅ Inicia el estado HANDOFF
4. ✅ Responde con confirmación y número de ticket
5. ✅ Se pone en modo "espera operario"
6. ✅ No muestra más opciones de menú

---

## 🎯 Cómo Funciona

### Paso 1: Usuario Ve la Opción
```
¡Hola! 👋 Bienvenido/a a la Clínica. UOM Seccional Santa Fe
Para continuar, respondé con el número de opción:

1️⃣ Turnos
2️⃣ Asuntos laborales
3️⃣ Farmacia
4️⃣ Afiliaciones
5️⃣ Discapacidad
6️⃣ Bocas de expendio
7️⃣ Compra de Orden de Consulta

🔴 **99 - Chatear con un Operador**
↩️ En cualquier momento podés escribir **0** para volver al menú principal.
```

### Paso 2: Usuario Escribe 99
```
Usuario: 99
```

### Paso 3: Bot Inicia Handoff
```
El bot:
1. Llama: ConversationManager.start_handoff()
2. Genera ticket automático
3. Cambia estado a WAITING_AGENT
4. Responde con confirmación
```

### Paso 4: Bot Responde
```
📞 **Se ha iniciado transferencia a un operador**

✅ Tu número de ticket: **TKT-A1B2C3D4**

⏳ Por favor espera a que un operario se comunique contigo.
Esto generalmente toma unos minutos.

Gracias por tu paciencia 😊
```

### Paso 5: Usuario Espera
```
Webhook activa filtro should_skip_bot_menu() = True
↓
No muestra más menú
↓
Responde con: "⏳ Estamos buscando un operatio..."
```

### Paso 6: Operario Acepta Ticket
```
Endpoint: ConversationManager.assign_agent()
↓
Estado cambia a: IN_AGENT
↓
Operario recibe mensajes del usuario
```

---

## 🔧 Implementación Técnica

### 1. Cambio en MenuP.MD
```markdown
🔴 **99 - Chatear con un Operador**
```

### 2. Cambio en get_menu_section() (app.py)
```python
# Si pide chatear con operador (99) iniciar handoff
if user_input == "99":
    print(f"[MENU] Usuario solicita operario")
    return "handoff_request", "handoff"
```

### 3. Lógica en Webhook
```python
# Si usuario seleccionó opción 99 (Chatear con Operador)
if state.get("section") == "handoff" and answer == "handoff_request":
    # Iniciar handoff usando ConversationManager
    request = StartHandoffRequest(phone_number=chat_id)
    conv = ConversationManager.start_handoff(db, request)
    
    # Responder con ticket
    answer = f"📞 Transferencia iniciada. Ticket: {conv.ticket_id}"
```

---

## 🎯 Estados Involucrados

```
Usuario selecciona 99
    ↓
    get_menu_section() retorna ("handoff_request", "handoff")
    ↓
    Webhook detecta section == "handoff"
    ↓
    ConversationManager.start_handoff(db, request)
    ├─ Genera ticket_id
    ├─ Estado → WAITING_AGENT
    ├─ handoff_active = True
    └─ Persiste en BD
    ↓
    Bot responde: "Ticket: TKT-XXXXXXXX"
    ↓
    Usuario en estado WAITING_AGENT
    ├─ Filtro should_skip_bot_menu() = True
    ├─ No muestra menú
    └─ Muestra: "Esperando operario..."
    ↓
    Operario acepta (assign_agent)
    ├─ Estado → IN_AGENT
    └─ Mensajes pasan al operario
    ↓
    Operario resuelve (close_handoff)
    ├─ Estado → CLOSED
    └─ Próximo mensaje vuelve a menú
```

---

## 📊 Flujo Completo en Diagrama

```
┌─────────────────────────────────────────────────────────┐
│                    USUARIO                              │
└──────────────────────┬──────────────────────────────────┘
                       │ Escribe: 99
                       ↓
┌──────────────────────────────────────────────────────────┐
│                  WEBHOOK (app.py)                        │
│                                                          │
│  1. Recibe mensaje: "99"                               │
│  2. Llama: get_menu_section("99", "main")              │
│  3. Obtiene: ("handoff_request", "handoff")            │
│  4. Detecta: section == "handoff"                       │
│  5. Llama: ConversationManager.start_handoff()         │
│  6. Genera: TKT-A1B2C3D4                               │
│  7. Estado: WAITING_AGENT                              │
│  8. Responde: "Tu ticket: TKT-A1B2C3D4"                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │   BD: conversation_states    │
        │   phone_number: +543...      │
        │   current_state: WAITING_    │
        │   AGENT                      │
        │   ticket_id: TKT-A1B2C3D4    │
        │   handoff_active: True       │
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │   USUARIO ESPERA             │
        │   - No ve menú               │
        │   - Ve: "Esperando..."       │
        │   - Ticket: TKT-A1B2C3D4     │
        └──────────────┬───────────────┘
                       │
                       ↓ (Operario acepta)
        ┌──────────────────────────────┐
        │   assign_agent()             │
        │   - Estado: IN_AGENT         │
        │   - Operario: Carlos (ID: 5) │
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │   CONVERSACIÓN ACTIVA        │
        │   - Usuario → Operario       │
        │   - Sin interferencia del bot│
        │   - Ticket: TKT-A1B2C3D4     │
        └──────────────┬───────────────┘
                       │
                       ↓ (Operario resuelve)
        ┌──────────────────────────────┐
        │   close_handoff()            │
        │   - Estado: CLOSED           │
        │   - Registro de resolución   │
        └──────────────┬───────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │   CONVERSACIÓN FINALIZADA    │
        │   - Próximo mensaje: MENÚ    │
        │   - Vuelve a BOT_MENU        │
        └──────────────────────────────┘
```

---

## 📱 Experiencia del Usuario

### Escenario Típico

```bash
# 1. Usuario ve el menú inicial
Bot: "¡Hola! ¿Qué necesita?
     1️⃣ Turnos
     2️⃣ Asuntos laborales
     ...
     🔴 99 - Chatear con un Operador"

# 2. Usuario no quiere contestar preguntas
Usuario: "99"

# 3. Bot confirma y genera ticket
Bot: "📞 Se ha iniciado transferencia a un operador
     ✅ Tu número de ticket: TKT-A1B2C3D4
     ⏳ Por favor espera..."

# 4. Usuario envía un mensaje mientras espera
Usuario: "¿Cuánto tiempo debo esperar?"

# 5. Bot responde que está esperando (no muestra menú)
Bot: "⏳ Estamos buscando un operario para atenderte..."

# 6. Operario acepta el ticket (en su panel)
Operario: [Click] "Aceptar"

# 7. Operario y usuario conversan
Usuario: "Mi problema es..."
Operario: "Veo. Déjame ayudarte con..."
Usuario: "Perfecto, gracias"
Operario: "De nada, queda resuelto"

# 8. Operario cierra
Operario: [Click] "Resolver ticket"

# 9. Usuario envía nuevo mensaje
Usuario: "Gracias"

# 10. Vuelve al menú principal
Bot: "¡Hola! ¿Qué necesita?
     1️⃣ Turnos..."
```

---

## 🔐 Seguridad & Validación

✅ Solo números válidos activan handoff (99)  
✅ Ticket único generado (UUID)  
✅ Estado persistido en BD  
✅ Filtro webhook previene menú durante handoff  
✅ Auto-cierre por inactividad  
✅ Logging de todos los eventos  

---

## ⏱️ Auto-Cierre

Si el usuario está en WAITING_AGENT o IN_AGENT y **no hay actividad por 120 minutos**:
- El ticket se cierra automáticamente
- Estado → CLOSED
- Próximo mensaje vuelve a menú
- Log de cierre registrado

**Configuración** (en BotConfig):
```python
handoff_inactivity_minutes = 120  # Cambiar según necesidad
```

---

## 📊 Métricas & Tracking

Cada ticket tiene:
- `ticket_id`: TKT-XXXXXXXX (único)
- `phone_number`: +543424438150 (del usuario)
- `current_state`: WAITING_AGENT → IN_AGENT → CLOSED
- `assigned_agent_id`: ID del operario
- `started_at`: Cuándo comenzó
- `last_message_at`: Última actividad
- `closed_at`: Cuándo se cerró
- `collected_data`: Datos recopilados
- `notes`: Notas del operario

**Para analytics/reporting**, consultar tabla `conversation_states`

---

## 🚀 Comando Para Activar

La opción está **ya activada** en el menú. Usuario solo escribe:
```
99
```

No se requiere ningún comando especial o gatillo.

---

## 🔧 Si No Funciona

### Problema: Opción 99 no aparece en menú
**Solución**: Verificar que `MenuP.MD` contiene la línea:
```
🔴 **99 - Chatear con un Operador**
```

### Problema: Usuario escribe 99 pero no inicia handoff
**Solución**: Verificar que `get_menu_section()` tiene:
```python
if user_input == "99":
    return "handoff_request", "handoff"
```

### Problema: No se genera ticket
**Solución**: Verificar que webhook detecta `section == "handoff"` y llama:
```python
ConversationManager.start_handoff(db, request)
```

### Debugging
```bash
# Ver logs
grep "\[MENU\] Usuario solicita operario" app.log

# Ver estado en BD
sqlite3 data/chatbot.sql "SELECT phone_number, current_state, ticket_id FROM conversation_states ORDER BY started_at DESC LIMIT 10;"
```

---

## 📚 Documentos Relacionados

- **HANDOFF_IMPLEMENTATION_COMPLETE.md** - Arquitectura completa
- **HANDOFF_QUICK_START.md** - Guía para operarios
- **QUICK_REFERENCE.md** - Code snippets
- **conversation_manager.py** - Implementación

---

## ✅ Estado

| Item | Estado |
|------|--------|
| Opción en menú | ✅ Implementada |
| Detección en webhook | ✅ Implementada |
| Inicio de handoff | ✅ Implementada |
| Estado WAITING_AGENT | ✅ Implementada |
| Filtro should_skip_bot_menu | ✅ Implementada |
| Auto-cierre por inactividad | ✅ Implementada |
| Documentación | ✅ Completa |
| Testing | ✅ Incluido |

---

**Implementado**: 2026-03-05  
**Status**: ✅ PRODUCCIÓN LISTA  
**Testing**: Incluido en HANDOFF_TESTING_GUIDE.md  

---

## 🎉 Resumen

**La opción 99 permite a los usuarios:**
✅ Omutsir menú y hablar directo con operario  
✅ Obtener número de ticket para referencia  
✅ No ser interrumpidos por el bot  
✅ Conversar con operario humano directamente  

**La implementación:**
✅ Es segura (validación en todos los niveles)  
✅ Es escalable (DB persiste todo)  
✅ Es automática (auto-cierre por inactividad)  
✅ Es monitoresable (logs + BD)  

¡**Listo para producción!**
