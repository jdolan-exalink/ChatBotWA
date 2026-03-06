# Testing Guide: HUMAN MODE Refactoring

## 📋 Cambios Implementados

### 1. **Nuevo módulo: state_cache.py**
- Proporciona caché eficiente con TTL de 5 minutos
- Evita memory leaks al limpiar entradas expiradas
- Mantiene sincronización con BD como fuente de verdad

### 2. **app.py Modificado**
- ✅ Importa `state_cache` 
- ✅ Inicializa caché al startup
- ✅ Crea loop de limpieza de caché cada 5 minutos
- ✅ **Chequeo HUMAN_MODE MOVIDO ANTES de filtros** (es ahora PRIORITARIO)
- ✅ Chequeo HUMAN_MODE usa state_cache para mejor performance
- ✅ Elimina duplicidad de lógica de HUMAN_MODE

### 3. **conversation_manager.py** (Sin cambios)
- Mantiene métodos:
  - `is_in_human_mode()`: Verifica estado + expiration
  - `start_handoff()`: Inicia modo humano por 12h
  - `exit_human_mode()`: Termina manualmente
  - `update_last_message()`: Actualiza timestamp

---

## 🧪 Plan de Testing

### Test 1: Verificar que StateCache funciona

**Objetivo**: Confirmar que el caché se inicializa correctamente

```bash
# Terminal 1: Iniciar el bot
cd /opt/clinic-whatsapp-bot/services/clinic-bot-api
python app.py

# Buscar en los logs:
# ✅ "[STATE_CACHE] Inicializado con TTL=300s"
# ✅ "[CACHE_CLEANUP] Limpez completada: X entradas..."
```

**Esperado**:
- Al iniciar, debe mostrar mensaje de inicialización de caché
- Cada 5 minutos, debe hacer limpieza automática

---

### Test 2: Iniciar HUMAN_MODE y verificar que ignora mensajes

**Objetivo**: Confirmar que mensajes en HUMAN_MODE se ignoran completamente

**Procedimiento**:
1. Un usuario envía un mensaje al bot (cualquier opción, ej: "1")
   - Bot responde ✅

2. Bot envía opción 99 (Hablar con operador)
   - Bot inicia HUMAN_MODE
   - Debería mostrar: `convmachine.start_handoff()`

3. El usuario envía otro mensaje (ej: "Hola")
   - Bot **DEBE IGNORAR** el mensaje
   - **NO responde**
   - Buscar en logs:
     ```
     [WEBHOOK] Chequeo HUMAN_MODE para <chat_id>...
     [WEBHOOK] ✅ <chat_id> EN HUMAN_MODE ACTIVO - Ignorando completamente el mensaje
     [WEBHOOK]    - No se responde
     [WEBHOOK]    - No se marca como leído
     [WEBHOOK]    - Se actualiza último mensaje para tracking
     [STATE_CACHE] Invalidado: <chat_id>
     ```

4. Esperar 12 horas (o modificar BD para que human_mode_expire = now)
   - Usuario envía mensaje
   - Bot **DEBE RESPONDER** con el menú
   - Buscar en logs:
     ```
     [HUMAN_MODE] Expire para <chat_id> - volviendo a BOT_MODE
     [WEBHOOK] off_hours=False
     [WEBHOOK] Buscando opción...
     [WEBHOOK] Enviando respuesta...
     ```

---

### Test 3: Opción 98 (Exit Manual de HUMAN_MODE)

**Objetivo**: Confirmar que opción 98 termina HUMAN_MODE manualmente

**Procedimiento**:
1. Usuario en HUMAN_MODE envía mensaje "98"
   - Bot ignora (sigue en HUMAN_MODE)
   
2. Administrador ejecuta manual exit:
   ```python
   from conversation_manager import ConversationManager
   from database import SessionLocal
   
   db = SessionLocal()
   ConversationManager.exit_human_mode(db, "+5493424123456@c.us")
   ```

3. Usuario envía mensaje
   - Bot **DEBE RESPONDER**
   - Estado debe cambiar a BOT_MODE

---

### Test 4: StateCache Performance

**Objetivo**: Verificar que el caché reduce carga en BD

**Procedimiento**:
1. Habilitar debug logging
2. Enviar 5 mensajes consecutivos rápidamente
   - Primero debe ser MISS (traer de BD)
   - Los siguientes 4 deben ser HIT (del caché)
   - Buscar en logs:
     ```
     [STATE_CACHE] MISS <chat_id> - Traído de BD
     [STATE_CACHE] HIT <chat_id> (edad: 123ms)
     [STATE_CACHE] HIT <chat_id> (edad: 234ms)
     ...
     ```

3. Esperar > 5 minutos
4. Enviar mensaje
   - Debe ser MISS de nuevo (caché expiró)

---

### Test 5: Memory Leak Prevention

**Objetivo**: Verificar que el caché no crece sin límite

**Procedimiento**:
1. Simular 1000 chats diferentes
   ```python
   # En el webhook, log muestra tamaño de caché:
   # [CACHE_CLEANUP] Limpieza completada: 100 entradas
   # Cache: StateCache(size=900, hits=5000, misses=1000, ...)
   ```

2. Después de 5 minutos, debe limpiar
   - Mostrar: `Limpieza completada: 100 entradas eliminadas`

3. Verificar que **nunca crece más allá de ~320 entradas** (con 5 min TTL)
   - Máximo = TTL / intervalo_cleanup * fluj_por_segundo

---

## 📊 Checklist de Validación

### Logs esperados después de refactoring:

- [ ] Al iniciar app.py:
  - `[STATE_CACHE] Inicializado con TTL=300s`
  
- [ ] Cada 5 minutos:
  - `[CACHE_CLEANUP] Limpieza completada: X entradas`
  
- [ ] Cuando usuario en HUMAN_MODE envía mensaje:
  - `[WEBHOOK] ✅ <chat_id> EN HUMAN_MODE ACTIVO`
  - `[WEBHOOK] Ignorando completamente el mensaje`
  - `[WEBHOOK] - No se responde`
  
- [ ] Cache statistics:
  - Hit rate > 80% (si hay chats activos)
  - Invalidations se hacen correctamente
  - Memory size nunca excede ~500 entradas

---

## 🔍 Debugging

### Si HUMAN_MODE no funciona:

1. **Verificar BD**
   ```sql
   SELECT phone_number, human_mode, human_mode_expire, current_state 
   FROM conversation_state 
   WHERE phone_number = '+5493424123456@c.us';
   ```
   - human_mode debe ser TRUE
   - human_mode_expire debe ser > NOW()

2. **Verificar ConversationManager**
   ```python
   from conversation_manager import ConversationManager
   from database import SessionLocal
   
   db = SessionLocal()
   result = ConversationManager.is_in_human_mode(db, "+5493424123456@c.us")
   print(f"is_in_human_mode: {result}")
   ```

3. **Verificar caché**
   ```python
   from state_cache import get_state_cache
   
   cache = get_state_cache()
   print(cache.stats())  # Ver hits/misses
   print(cache)  # Ver tamaño
   ```

4. **Logs detallados**
   - Buscar línea `[WEBHOOK] Chequeo HUMAN_MODE para`
   - Buscar función que retorna (debe ser línea con `human_mode_active`)

### Si memory leak persiste:

1. Verificar que `cleanup_state_cache_loop()` está corriendo:
   ```bash
   ps aux | grep python | grep app.py
   # Debe haber al menos 2 procesos
   ```

2. Verificar frecuencia de cleanup:
   ```bash
   grep "CACHE_CLEANUP" logs.txt | tail -10
   # Debe aparecer cada ~5 minutos
   ```

3. Si no aparece, revisar:
   - `asyncio.create_task(cleanup_state_cache_loop())` en startup
   - Que el loop no tiene excepciones

---

## 📈 Métricas a Monitorear

### Antes vs Después

| Métrica | Antes | Después | Esperado |
|---------|-------|---------|----------|
| Memory usage | Crece indefinidamente | Estable | < 100MB para 1000 chats |
| Cache hit rate | N/A | ~85% | > 80% |
| HUMAN_MODE false negatives | Desconocido | 0% | 0% (100% confiabilidad) |
| Respuesta a mensajes HUMAN_MODE | Variable | < 100ms | < 100ms |
| BD queries por mensaje | 2-3 | 0-1 (caché) | Reducción 50-75% |

---

## 🚀 Pasos Finales

1. [ ] Ejecutar todos los tests
2. [ ] Validar logs esperados
3. [ ] Verificar memory usage se mantiene estable
4. [ ] Confirmar HUMAN_MODE funciona al 100%
5. [ ] Deploydeploy a producción

---

## ⚠️ Rollback Plan

Si hay problemas:

```bash
# Revertir cambios
git checkout HEAD -- services/clinic-bot-api/app.py
rm services/clinic-bot-api/state_cache.py

# Reiniciar
docker-compose restart clinic-bot-api
```

**Nota**: Los cambios en conversation_manager.py NO se modificaron, así que la BD seguirá teniendo datos válidos.
