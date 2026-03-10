# Fix QR No Disponible

## Problema
El QR no se mostraba en el panel web aunque WAHA estuviera disponible.

## Causas Identificadas

1. **Timeouts muy cortos en `_waha_qr()`:** 2-3 segundos no eran suficientes
2. **Endpoint `/status` muy restrictivo:** Solo pedía QR cuando `status == "SCAN_QR_CODE"`
3. **Endpoint `/qr` pasivo:** No intentaba generar QR si no existía
4. **Falta de logging:** No se sabía por qué fallaba la obtención del QR

## Solución Implementada

### 1. Timeouts Aumentados en `_waha_qr()`

```python
# ANTES
timeout=httpx.Timeout(connect=2.0, read=3.0, write=3.0, pool=2.0)

# AHORA
timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
```

### 2. Logging Detallado de QR

```python
_logc(f"[QR] Obtenido desde {p} (image, {len(r.content)} bytes)")
_logc(f"[QR] Obtenido desde {p} (base64, {len(decoded)} bytes)")
```

### 3. Endpoint `/status` Mejorado

Ahora solicita QR en múltiples estados:

```python
# ANTES: Solo en SCAN_QR_CODE
qr = await _waha_qr() if (not connected and session_status == "SCAN_QR_CODE") else None

# AHORA: En STARTING, SCAN_QR_CODE, y FAILED
needs_qr = not connected and session_status in ("SCAN_QR_CODE", "STARTING", "FAILED")
qr = await _waha_qr() if needs_qr else None
```

### 4. Endpoint `/qr` Activo

Ahora genera QR automáticamente si no existe:

```
1. Intenta obtener QR existente
2. Si no hay → hace restart de sesión
3. Espera 3 segundos
4. Intenta obtener QR nuevamente
5. Si no hay → hace recreate completo (borra auth)
6. Espera 5 segundos
7. Intenta obtener QR por última vez
```

### 5. Logging de Estado

```python
if not connected:
    _logc(f"[STATUS] Desconectado (status={session_status}, eng_state={eng_state}), QR disponible={qr is not None}")
```

## Flujo de Obtención de QR

### Escenario Normal (QR ya disponible)
```
[QR] Obtenido desde /api/sessions/default/auth/qr?format=image (image, 2048 bytes)
→ QR mostrado inmediatamente
```

### Escenario con Restart
```
[QR] No hay QR disponible, intentando generar nuevo...
[QR] restart → 200
[QR] QR generado exitosamente después de restart
→ QR mostrado después de 3-5 segundos
```

### Escenario con Recreate (QR expirado)
```
[QR] No hay QR disponible, intentando generar nuevo...
[QR] restart → 500
[QR] Restart no generó QR, intentando recreación completa...
[CONNECT] DELETE session: 200
[CONNECT] create session: 200
[QR] QR generado exitosamente después de recreate
→ QR mostrado después de 8-10 segundos
```

## Cómo Aplicar

```bash
cd /opt/clinic-whatsapp-bot
docker-compose down
docker-compose build wa-bot
docker-compose up -d
```

## Verificar Funcionamiento

### 1. Ver logs en tiempo real
```bash
docker logs wa-bot -f
```

### 2. Ver estado de conexión
```bash
curl http://localhost:8088/status -H "Authorization: Bearer TU_TOKEN"
```

Respuesta esperada cuando necesita QR:
```json
{
  "connected": false,
  "has_qr": true,
  "info": {
    "name": "default",
    "status": "SCAN_QR_CODE"
  }
}
```

### 3. Ver QR directamente
```bash
curl http://localhost:8088/qr -H "Authorization: Bearer TU_TOKEN" -o qr.png
```

## Troubleshooting

### QR sigue sin mostrarse

1. **Verificar WAHA:**
   ```bash
   curl http://localhost:3100/health
   ```

2. **Ver logs de WAHA:**
   ```bash
   docker logs clinic-waha --tail 50
   ```

3. **Reiniciar WAHA:**
   ```bash
   docker restart clinic-waha wa-bot
   ```

4. **Forzar QR desde API:**
   ```bash
   curl -X POST http://localhost:8088/bot/connect -H "Authorization: Bearer TU_TOKEN"
   ```

### QR expira rápidamente

El QR de WhatsApp expira ~60 segundos. El panel web debería:
- Hacer polling cada 50 segundos
- El endpoint `/qr` ahora genera QR nuevo automáticamente

## Cambios en Archivos

| Archivo | Cambios |
|---------|---------|
| `services/clinic-bot-api/app.py` | `_waha_qr()`, `/status`, `/qr` mejorados |
| `services/clinic-bot-api/Dockerfile` | curl instalado |
| `docker-compose.yml` | health check agregado |

## Resumen de Mejoras

| Característica | Antes | Ahora |
|----------------|-------|-------|
| Timeout QR | 2-3s | 5-10s |
| Rutas probadas | 4 (secuencial) | 4 (paralelo) |
| Logging QR | ❌ | ✅ Detallado |
| Generación auto | ❌ | ✅ 3 niveles |
| Estados para QR | 1 (SCAN_QR_CODE) | 3 (STARTING, SCAN_QR_CODE, FAILED) |

---

**Fecha:** 2026-03-10  
**Versión:** 2.2.2  
**Estado:** Listo para producción
