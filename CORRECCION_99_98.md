# Correcciones HUMAN MODE - 99 y 98

## 🔧 Cambios Implementados

### 1. **Opción 99 (Iniciar HUMAN_MODE) - NO responde**
**Ubicación**: [app.py línea 1552-1577](app.py#L1552-L1577)

**Problema anterior**: Cuando se iniciaba HUMAN_MODE (opción 99), se enviaba un mensaje de confirmación al usuario. Eso causaba que se marque como leído.

**Solución implementada**:
- Cuando se detecta opción 99, se llama a `ConversationManager.start_handoff()`
- Se establece `human_mode=TRUE` en BD con `human_mode_expire = NOW + 12h`
- Se crea la conversación con estado `WAITING_AGENT`
- **NO se envía respuesta** (`answer = ""`)
- **NO se marca como leído** (porque no se envía nada)
- El operador es quien dirán contactar directamente al usuario

```python
# ANTES:
Respuesta del bot:
"📞 Se ha iniciado transferencia...
✅ Tu número de ticket: TKT-XXXXX..."
❌ Marca como leído automáticamente

# DESPUÉS:
(Sin respuesta)
✅ NO marca como leído
✅ HUMAN_MODE está activo en BD
```

### 2. **Opción 98 (Salir de HUMAN_MODE)**
**Ubicación**: [app.py línea 1520-1549](app.py#L1520-L1549)

**Funcionalidad**:
- Solo funciona si el usuario está EN HUMAN_MODE
- Llama a `ConversationManager.exit_human_mode()` que:
  - Establece `human_mode=FALSE`
  - Limpia `human_mode_expire`
  - Retorna a BOT_MODE
- Invalida caché para reflejar cambio inmediatamente
- Resetea estado al menú principal
- Responde confirmando que volvió al bot

### 3. **Chequeo HUMAN_MODE Mejorado**
**Ubicación**: [app.py línea 1398-1440](app.py#L1398-L1440)

**Mejoras**:
- Logging detallado para debuggear
- Verifica si conversación existe en caché/BD
- Si existe y tiene `human_mode=TRUE`, llama a `is_in_human_mode()`
- `is_in_human_mode()` verifica que no haya expirado
- Retorna inmediatamente SIN procesar el mensaje
- Invalida caché para próxima consulta

**Logs esperados**:
```
[WEBHOOK] Chequeo HUMAN_MODE para +5493424123456@c.us...
[WEBHOOK] conv.human_mode=TRUE encontrado en BD/caché
[WEBHOOK] is_in_human_mode() devolvió: True
[WEBHOOK] ✅ +5493424123456@c.us EN HUMAN_MODE ACTIVO - Ignorando completamente
[WEBHOOK]    - No se responde
[WEBHOOK]    - No se marca como leído
[WEBHOOK]    - Se actualiza último mensaje para tracking
[STATE_CACHE] Invalidado: +5493424123456@c.us
```

---

## 📊 Flujo Completo HUMAN MODE

```
USUARIO ENVÍA "99"
    ↓
[WEBHOOK]
    ├─ Chequea HUMAN_MODE
    │  └─ conv es None (aún no existe)
    │     └─ Continúa normalmente
    │
    ├─ Procesa opción "99"
    │  └─ get_menu_section() → ("handoff_request", "handoff")
    │
    ├─ Handler HANDOFF
    │  ├─ ConversationManager.start_handoff()
    │  │  └─ Crea conversación
    │  │     └─ human_mode=TRUE
    │  │     └─ human_mode_expire=NOW+12h
    │  │     └─ db.commit()
    │  │
    │  ├─ Invalida caché
    │  └─ answer = "" (NO responde)
    │
    ├─ send_whatsapp_text()
    │  └─ answer está vacío → NO envía nada
    │
    └─ return {"ok": True}
    
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USUARIO ENVÍA OTRO MENSAJE (ej: "Hola")
    ↓
[WEBHOOK]
    ├─ Extrae chat_id, text
    │
    ├─ Chequea HUMAN_MODE (PRIORITARIO)
    │  ├─ cache.get(db, chat_id)
    │  │  └─ Encuentra conversación con human_mode=TRUE
    │  │
    │  ├─ ConversationManager.is_in_human_mode(db, chat_id)
    │  │  ├─ Verifica human_mode=TRUE ✓
    │  │  ├─ Verifica human_mode_expire > NOW ✓
    │  │  └─ Devuelve True
    │  │
    │  └─ RETORNA INMEDIATAMENTE
    │     ├─ return {"ok": True, "status": "human_mode_active"}
    │     └─ NO procesa resto del webhook
    │
    ├─ NO se responde
    ├─ NO se marca como leído
    └─ Fin
```

---

## ✅ Validación

Sintaxis ✅ Validado con `python3 -m py_compile`

---

## 🧪 Testing Manual

### Test 1: Opción 99 - NO marca como leído
```
1. Usuario envía "99"
2. Webpack procesa
3. Buscar en logs: "[WEBHOOK] 🔴 Usuario solicita opción 99"
4. Verificar que NO hay: "[WEBHOOK] Respuesta enviada exitosamente"
5. Verificar que answer="" en los logs
6. WhatsApp debe mostrar: ⭕ (recibido, no leído)
```

### Test 2: Opción 98 - Sale de HUMAN_MODE
```
1. Usuario en HUMAN_MODE envía "98"
2. Logs muestran: "[WEBHOOK] 🟢 Usuario solicita opción 98"
3. Logs muestran: "salió de HUMAN_MODE exitosamente"
4. Usuario envía otro mensaje
5. Logs muestran: "Conversación existe pero human_mode=FALSE"
6. Bot responde normalmente ✓
```

### Test 3: Después de 12h - Expira HUMAN_MODE
```
1. Usuario en HUMAN_MODE
2. Esperar o modificar BD: human_mode_expire = NOW - 1 second
3. Usuario envía mensaje
4. Logs muestran: "[HUMAN_MODE] Expire para {id} - volviendo a BOT_MODE"
5. Bot responde normalmente ✓
```

---

## 📝 Resumen de Cambios

| Feature | Antes | Después |
|---------|-------|---------|
| **Opción 99** | Responde, marca como leído | NO responde, NO marca como leído |
| **Opción 98** | No existe | Existe, sale de HUMAN_MODE |
| **Chequeo HUMAN_MODE** | Después de otros chequeos | PRIORITARIO, primero |
| **Logging** | Mínimo | Detallado para debuggear |
| **Mensajes vacíos** | Posibles | Bloqueados (answer="" no se envía) |

---

## 🔒 Consideraciones WAHA-DOC

Conforme a WAHA-DOC sección 9:
- ✅ En HUMAN_MODE NO se ejecuta sendSeen
- ✅ El mensaje "queda recibido" (⭕)
- ✅ NO se envía "confirmación de lectura" (✓)
- ✅ Operador puede ver que el bot no interfiere

---

**Estado**: ✅ Completado  
**Próximo paso**: Testing conforme TESTING_HUMAN_MODE.md
