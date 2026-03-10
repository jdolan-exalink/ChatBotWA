# Resumen de Cambios - Reconexión Automática WAHA

## Problema
El bot mostraba "desconectado" pero en el teléfono la última conexión era reciente. WhatsApp cerraba la conexión y el bot no la recuperaba automáticamente.

## Solución Implementada

### 1. Mejoras en el Código (`app.py`)

#### Timeouts Aumentados
```python
# ANTES: connect=3s, read=6s, write=6s
# AHORA: connect=10s, read=15s, write=15s, pool=10s
```

#### Monitor de Conexión Mejorado
- **Frecuencia:** 30s → 10s
- **Estrategia escalonada:**
  - Intentos 1-2: `restart` (mantiene auth)
  - Intentos 3-4: `stop` + `start` (más agresivo)
  - Intentos 5+: `delete` + `create` (requiere QR)
- **Backoff exponencial:** 1s → 2s → 4s → 8s → 16s → 30s

#### Heartbeat Antes de Enviar
```python
# Verifica WAHA antes de cada mensaje
if not await _waha_healthcheck():
    _reset_waha_client()  # Reconecta automáticamente
```

#### Logging Mejorado
```
[MONITOR] ✓ Sesión reconectada OK (status=WORKING)
[SEND] WAHA no disponible, intentando reconectar...
[HTTP] Recreando cliente HTTP WAHA
```

### 2. Mejoras en Docker

#### `docker-compose.yml`
Agregado health check:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8088/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

#### `Dockerfile`
Agregado curl para health checks:
```dockerfile
RUN apt-get update && apt-get install -y curl
```

### 3. Documentación Nueva

- `RECONEXION_AUTOMATICA.md` - Guía completa con troubleshooting

## Cómo Aplicar los Cambios

### Opción A: Rebuild Completo (Recomendado)
```bash
cd /opt/clinic-whatsapp-bot
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Opción B: Rebuild Rápido
```bash
cd /opt/clinic-whatsapp-bot
docker-compose build wa-bot
docker-compose up -d wa-bot
```

### Verificar que está corriendo
```bash
docker-compose ps
docker logs wa-bot --tail 50
```

## Comportamiento Esperado

### Escenario 1: Caída Temporal de WAHA
```
[MONITOR] Sesión caída (status=FAILED), intento #1
[MONITOR] Restart exitoso, esperando reconexión...
[MONITOR] ✓ Sesión reconectada OK (status=WORKING)
```
**Resultado:** Reconexión automática en < 20 segundos

### Escenario 2: WhatsApp Cierra Sesión
```
[MONITOR] Sesión caída (status=FAILED), intento #5
[MONITOR] Intentando recreación completa de sesión (requerirá QR)
[MONITOR] Recreación completada, esperando QR...
```
**Acción requerida:** Escanear QR desde panel web

### Escenario 3: WAHA No Responde
```
[MONITOR] WAHA no disponible (ConnectError): Connection refused
[SEND] WAHA no disponible, intentando reconectar...
```
**Acción requerida:** Verificar contenedor WAHA

## Métricas de Éxito

| Métrica | Antes | Ahora |
|---------|-------|-------|
| Detección de caída | 30s | 10s |
| Reconexión típica | Manual | < 20s automático |
| Reintentos | 3 | Ilimitados |
| Alertas | Genéricas | Con troubleshooting |

## Configuración Opcional: Alertas por Email

Para recibir alertas cuando falla la reconexión automática:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...
ALERT_EMAIL_TO=tu-email@ejemplo.com
```

## Troubleshooting Rápido

### Ver estado de conexión
```bash
curl http://localhost:8088/status -H "Authorization: Bearer TU_TOKEN"
```

### Ver logs en tiempo real
```bash
docker logs wa-bot -f
```

### Forzar reconexión manual
```bash
curl -X POST http://localhost:8088/bot/connect -H "Authorization: Bearer TU_TOKEN"
```

### Reiniciar WAHA
```bash
docker restart clinic-waha wa-bot
```

## Archivos Modificados

1. `services/clinic-bot-api/app.py` - Lógica de reconexión
2. `services/clinic-bot-api/Dockerfile` - Curl para health check
3. `docker-compose.yml` - Health check configuration
4. `RECONEXION_AUTOMATICA.md` - Documentación nueva (archivo nuevo)

## Próximos Pasos

1. **Aplicar cambios:** Seguir instrucciones en "Cómo Aplicar los Cambios"
2. **Monitorear logs:** `docker logs wa-bot -f`
3. **Probar desconexión:** Opcional, reiniciar WAHA para verificar reconexión
4. **Configurar alertas:** Si se desea email ante fallos

---

**Fecha:** 2026-03-10  
**Versión:** 2.2.2  
**Estado:** Listo para producción
