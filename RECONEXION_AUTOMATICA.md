# Reconexión Automática WAHA - Documentación

## Problema Resuelto

El bot mostraba "desconectado" mientras que en el teléfono la última conexión era reciente. Esto ocurría cuando WAHA perdía la conexión pero el bot no la recuperaba automáticamente.

## Cambios Implementados

### 1. Timeouts Más Generosos

**Antes:**
- Connect: 3s, Read: 6s, Write: 6s, Pool: 3s

**Ahora:**
- Connect: 10s, Read: 15s, Write: 15s, Pool: 10s

Esto evita falsos negativos cuando WAHA responde lentamente.

### 2. Monitor de Conexión Mejorado

**Frecuencia de chequeo:**
- Antes: cada 30 segundos
- Ahora: cada 10 segundos

**Estrategia de reconexión escalonada:**

| Intentos | Acción | Descripción |
|----------|--------|-------------|
| 1-2 | `restart` | Reinicio suave (mantiene autenticación) |
| 3-4 | `stop` + `start` | Reinicio completo de sesión |
| 5+ | `delete` + `create` | Recreación total (requiere reescanear QR) |

**Backoff exponencial entre intentos:**
```
1s → 2s → 4s → 8s → 16s → 30s (máximo)
```

### 3. Heartbeat Antes de Enviar

Antes de cada mensaje por WhatsApp:
1. Verifica que WAHA responde (`/health`)
2. Si no responde, reconecta automáticamente
3. Reintenta el envío

### 4. Logging Mejorado

Nuevos mensajes de log:
```
[MONITOR] ✓ Sesión reconectada OK (status=WORKING)
[MONITOR] Resetear contador de reconexión (era 3)
[SEND] WAHA no disponible, intentando reconectar...
[HTTP] Recreando cliente HTTP WAHA
[MONITOR] WAHA no disponible (ConnectError): ...
```

### 5. Alertas Automáticas

Después de 5 intentos fallidos de reconexión:
- Envía email de alerta (si está configurado)
- Incluye recomendaciones de troubleshooting
- Solo una alerta cada 5 minutos para no saturar

## Configuración Requerida

### Email de Alertas (Opcional)

Para recibir alertas cuando la reconexión automática falla:

```env
GOOGLE_CLIENT_ID=tu-client-id
GOOGLE_CLIENT_SECRET=tu-client-secret
GOOGLE_REFRESH_TOKEN=tu-refresh-token
ALERT_EMAIL_TO=tu-email@ejemplo.com
ALERT_EMAIL_FROM=bot@ejemplo.com
```

### Variables Existentes (No cambian)

```env
WAHA_URL=http://waha:3000
WAHA_API_KEY=tu-api-key
WAHA_SESSION=default
```

## Comandos de Control

### Ver Estado de Conexión

```bash
curl http://localhost:8088/status -H "Authorization: Bearer TU_TOKEN"
```

Respuesta:
```json
{
  "connected": true,
  "provider": "waha",
  "instance": "default",
  "paused": false,
  "solution_name": "Clínica"
}
```

### Forzar Reconexión Manual

Desde el panel web o API:

```bash
curl -X POST http://localhost:8088/bot/connect -H "Authorization: Bearer TU_TOKEN"
```

Esto intenta:
1. Restart si está `WORKING`
2. Recreación completa si está `FAILED` o desconectado

## Troubleshooting

### El bot sigue mostrando "Desconectado"

1. **Verificar WAHA:**
   ```bash
   curl http://waha:3000/health
   ```

2. **Ver logs del bot:**
   ```bash
   docker logs clinic-whatsapp-bot --tail 100
   ```

3. **Ver logs de WAHA:**
   ```bash
   docker logs waha --tail 100
   ```

### WhatsApp cerró la sesión (requiere QR)

El bot automáticamente:
1. Detecta que necesita QR
2. Recrea la sesión
3. El QR está disponible en `/qr` o desde el panel web

**Acción requerida:** Escanear QR desde WhatsApp

### WAHA no responde

Si ves `[MONITOR] WAHA no disponible (ConnectError)`:

1. Verificar que el contenedor WAHA esté corriendo:
   ```bash
   docker ps | grep waha
   ```

2. Reiniciar WAHA:
   ```bash
   docker restart waha
   ```

3. Verificar red entre contenedores:
   ```bash
   docker network inspect clinic-whatsapp-bot_default
   ```

## Métricas de Reconexión

El bot mantiene estas variables globales (visibles en logs):

- `_waha_reconnect_attempts`: Intentos actuales de reconexión
- `_waha_last_reconnect_time`: Timestamp del último intento
- `_last_status["connected"]`: Estado actual de conexión

## Flujo Normal de Reconexión

```
[MONITOR] Sesión caída (status=FAILED), intento #1
[MONITOR] Restart exitoso, esperando reconexión...
[MONITOR] ✓ Sesión reconectada OK (status=WORKING)
[MONITOR] Resetear contador de reconexión (era 1)
```

## Flujo con Reconexión Completa

```
[MONITOR] Sesión caída (status=FAILED), intento #1
[MONITOR] Restart exitoso, esperando reconexión...
[MONITOR] Sesión caída (status=FAILED), intento #2
[MONITOR] Error en restart: ...
[MONITOR] Sesión caída (status=FAILED), intento #3
[MONITOR] Stop+Start exitoso, esperando reconexión...
[MONITOR] ✓ Sesión reconectada OK (status=WORKING)
[MONITOR] Resetear contador de reconexión (era 3)
```

## Flujo con QR Requerido

```
[MONITOR] Sesión caída (status=FAILED), intento #5
[MONITOR] Intentando recreación completa de sesión (requerirá QR)
[CONNECT] DELETE session: 200
[CONNECT] create session: 200
[MONITOR] Recreación completada, esperando QR...
```

**Acción requerida:** Escanear nuevo QR desde el panel web.

## Recomendaciones

1. **No reiniciar manualmente** - El bot lo hace automáticamente
2. **Monitorear logs** - Los primeros 30 segundos son críticos
3. **Configurar alertas por email** - Para saber cuándo intervenir
4. **Mantener WAHA actualizado** - Versiones viejas pueden tener bugs de conexión

## Cambios Técnicos (para desarrolladores)

### Funciones Nuevas

- `_waha_healthcheck()`: Verifica conectividad con WAHA
- `_reset_waha_client()`: Cierra y fuerza recreación del cliente HTTP

### Funciones Modificadas

- `_get_waha_client()`: Timeouts aumentados, logging agregado
- `_monitor_loop()`: Lógica de reconexión escalonada con backoff
- `_send_wha()`: Heartbeat antes de enviar, reconexión automática

### Variables Globales Nuevas

```python
_waha_reconnect_attempts: int      # Contador de intentos
_waha_last_reconnect_time: int     # Timestamp último intento
_waha_force_reconnect: bool        # Flag para forzar reconexión
```

## Resumen

| Característica | Antes | Ahora |
|----------------|-------|-------|
| Detección de caída | 30s | 10s |
| Reintentos | 3 | Ilimitados (con backoff) |
| Estrategia | restart/start | Escalonada (3 niveles) |
| Heartbeat | ❌ | ✅ Antes de cada envío |
| Alertas | Genéricas | Con troubleshooting |
| Logging | Básico | Detallado con diagnóstico |

---

**Versión:** 2.2.2  
**Fecha:** 2026-03-10  
**Autor:** Auto-generado por mejora de reconexión
