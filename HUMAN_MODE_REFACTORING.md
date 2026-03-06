# Refactorización de HUMAN MODE - Análisis de Problemas

## 🔴 PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **Duplicidad de Estados (CRÍTICO)**
**Problema**: El estado se maneja en DOS lugares simultáneamente:
- `_chat_state[chat_id]` (diccionario en memoria, en app.py línea 89)
- `ConversationState` (en base de datos, en conversation_manager.py)

**Impacto**:
- Inconsistencias entre lo que cree el webhook y lo que hay en BD
- Si el webhook reinicia, TODOS los estados en memoria se pierden
- Comportamiento impredecible en HUMAN_MODE

**Ejemplo de error**:
```
Webhook inicia HUMAN_MODE → actualiza _chat_state[chat_id]
Bot recibe mensaje → chequea is_in_human_mode() (desde BD, OK)
Bot debe ignorar mensaje → pero _chat_state[chat_id] puede tener "section": "main"
→ Riesgo de procesar el mensaje erróneamente
```

### 2. **Sin Control de sendSeen en HUMAN_MODE (CRÍTICO)**
**Problema**: Según WAHA-DOC.md línea 9:
> En modo operador NO ejecutar: POST /api/sendSeen

**Evidencia en código**:
- No hay validación de `human_mode` antes de llamar a `send_whatsapp_text()`
- `send_whatsapp_text()` probablemente marca los mensajes como leídos automáticamente
- **RESULTADO**: El operador ve que el bot leyó el mensaje (❌ INCORRECTO)

### 3. **Diccionario _chat_state Sin Límite (MEMORY LEAK)**
**Problema**: Línea 89 en app.py
```python
_chat_state: dict[str, dict] = {}
```

**Impacto**:
- Cada chat nuevo se agrega y **NUNCA se elimina**
- Después de millones de mensajes = crash por falta de memoria
- En 12 horas con 1000 chats = 1000 entradas en memoria
- Si se ejecuta durante semanas = DISASTER

### 4. **Sincronización Débil de Last Message Time**
**Problema**: Línea 1422 en app.py
```python
if ConversationManager.is_in_human_mode(db, chat_id):
    print(f"[WEBHOOK] ✅ {chat_id} en HUMAN_MODE - retornando")
    ConversationManager.update_last_message(db, chat_id)  # Se actualiza en BD
    return {"ok": True}
```

**Impacto**:
- El `_chat_state[chat_id]` **NO se actualiza** con `last_ts`
- Si el usuario envía 100 mensajes en HUMAN_MODE, `_chat_state` está desactualizado
- Riesgo a timestamp corrompido

### 5. **No se Manual Exit (opción 98) Sincroniza con _chat_state**
**Problema**: Línea 453-454 en app.py
```python
if text == "98":
    ConversationManager.exit_human_mode(db, phone_number)
```

**Impacto**:
- `exit_human_mode()` actualiza BD pero NO actualiza `_chat_state[chat_id]`
- El webhook sigue creyendo que estamos en HUMAN_MODE por garbage en memoria
- Usuario intenta mensajear, pero webhook lo ignora

### 6. **Falta de Logging Detallado en HUMAN_MODE**
**Problema**: No hay forma de debuggear qué pasó exactamente:
- ¿Cuándo expiró human_mode_expire?
- ¿El mensaje llegó a la plataforma?
- ¿Cuál fue el último estado guardado?

---

## ✅ SOLUCIÓN: REFACTORIZACIÓN PROPUESTA

### Principio: **SINGLE SOURCE OF TRUTH = BASE DE DATOS**

#### Cambio 1: Eliminar `_chat_state` Global
- ❌ Usar solo `_chat_state` en memoria
- ✅ Usar `ConversationState` como única fuente de verdad
- ✅ Cachear SOLO por máx 5 minutos para performance

#### Cambio 2: Crear StateCache Eficiente
```python
# Nuevo archivo: state_cache.py
class ConversationStateCache:
    def __init__(self, max_ttl_sec=300):
        self._cache: dict[str, tuple[ConversationState, float]] = {}
        self._max_ttl = max_ttl_sec
    
    def get(self, db: Session, phone_number: str) -> ConversationState:
        # Si está en caché y no expiró (< 5 min)
        if phone_number in self._cache:
            conv, ts = self._cache[phone_number]
            if time.time() - ts < self._max_ttl:
                return conv
        
        # Traer de BD y cachear
        conv = ConversationManager.get_conversation(db, phone_number)
        self._cache[phone_number] = (conv, time.time())
        return conv
    
    def invalidate(self, phone_number: str):
        # Limpiar caché cuando hay cambios
        if phone_number in self._cache:
            del self._cache[phone_number]
    
    def cleanup_expired(self):
        # Limpiar caché cada 5 minutos
        now = time.time()
        keys_to_delete = [
            k for k, (_, ts) in self._cache.items()
            if now - ts > self._max_ttl
        ]
        for k in keys_to_delete:
            del self._cache[k]
```

#### Cambio 3: Control de sendSeen en HUMAN_MODE
```python
# En send_whatsapp_text():
async def send_whatsapp_text(
    chat_id: str, 
    text: str, 
    skip_seen: bool = False  # Nuevo parámetro
):
    # ... código existente ...
    
    # Marcar como leído SOLO si no estamos en HUMAN_MODE
    if not skip_seen:
        await send_seen(chat_id)
```

#### Cambio 4: Refactorizar Webhook
```python
# Pseudocódigo del nuevo flujo:
@app.post('/webhook')
async def webhook(req: Request, db: Session = Depends(get_db)):
    # 1. Traer estado ACTUAL (SEMPRE desde BD, si es reciente)
    conv = state_cache.get(db, chat_id)
    
    # 2. Chequear HUMAN_MODE y REALMENTE IGNOR
    if conv.human_mode and conv.human_mode_expire > now:
        # ✅ ACTUALIZAR timestamp
        conv.last_message_at = now
        db.commit()
        
        # ✅ NO RESPONDER, NO MARCAR COMO LEÍDO
        return {"ok": True, "status": "human_mode_active"}
    
    # 3. Si expiró HUMAN_MODE, cambiar estado
    if conv.human_mode and conv.human_mode_expire <= now:
        conv.human_mode = False
        conv.human_mode_expire = None
        db.commit()
        state_cache.invalidate(chat_id)
    
    # 4. Procesar como bot normal (con sendSeen)
    # ...
```

---

## 📊 Tabla de Cambios

| Problema | Solución | Línea(s) | Prioridad |
|----------|----------|---------|-----------|
| Duplicidad estados | StateCache + BD única | app.py:89,1400+ | CRÍTICO |
| sendSeen en HUMAN_MODE | Parámetro skip_seen | send_whatsapp_text() | CRÍTICO |
| Memory leak _chat_state | Usar StateCache TTL | app.py:89 | ALTO |
| Sync last_message_time | Actualizar en cada check | webhook | ALTO |
| exit_human_mode no sincroniza | Llamar state_cache.invalidate() | app.py:453 | MEDIO |
| Falta logging | Agregar logs detallados | todo el webhook | MEDIO |

---

## 🚀 Plan de Implementación

### Fase 1: Crear StateCache (5 min)
- [ ] Crear archivo `state_cache.py`
- [ ] Implementar clase`ConversationStateCache`
- [ ] Agregar método de cleanup

### Fase 2: Refactorizar send_whatsapp_text() (3 min)
- [ ] Agregar parámetro `skip_seen=False`
- [ ] Validar que no llame a sendSeen cuando skip_seen=True

### Fase 3: Refactorizar Webhook (15 min)
- [ ] Reemplazar `_chat_state` por StateCache
- [ ] Agregar validación de HUMAN_MODE ANTES de responder
- [ ] Agregar logging detallado
- [ ] Agregar updatede last_message_time en HUMAN_MODE

### Fase 4: Testing (10 min)
- [ ] Test: Iniciar HUMAN_MODE
- [ ] Test: Enviar mensaje, verificar no se marca como leído
- [ ] Test: Esperar a que expire, verificar vuelve a responder
- [ ] Test: Exit manual (opción 98), verificar funciona

### Fase 5: Documentación (5 min)
- [ ] Actualizar WAHA-DOC.md con nuevo flujo
- [ ] Agregar sección de troubleshooting

---

## ⚠️ Riesgos Identificados

1. **BC (Breaking Change)**: El cambio a StateCache puede afectar código qu
e use `_chat_state`
   - **Mitigación**: Buscar todos los usos de `_chat_state` en app.py
   
2. **Performance**: Si hay mucho I/O a BD
   - **Mitigación**: Usar caché de 5 minutos para estados
   
3. **Sincronización de BD**: Si hay varias instancias del bot
   - **Mitigación**: ConversationManager ya usa session fresca de BD

---

## 📝 Checklist de Validación

- [ ] No hay más de 1000 entradas en memoria
- [ ] HUMAN_MODE ignora 100% de mensajes
- [ ] sendSeen NO se envía en HUMAN_MODE
- [ ] Opción 98 funciona correctamente
- [ ] Después de 12h, bot responde automáticamente
- [ ] Logs detallados muestran lo que está pasando
