# API Interaction Guide — Clinic WhatsApp Bot

**Base URL:** `http://localhost:8088`  
**Versión API:** 2.2.20

---

## Diagnóstico del error 401

### Causa raíz

El error se produjo por **dos causas combinadas**:

1. **Formato de autenticación incorrecto** — El formato `Authorization: ApiKey <token>` **no está soportado**. Solo funcionan:
   - `X-Api-Key: wabot_ext_...` ← **recomendado**
   - `Authorization: Bearer wabot_ext_...`

2. **Token inválido/vencido** — El `api_key` completo solo se muestra una vez (al crear o regenerar el token). La BD guarda solo el hash. Si el token se perdió, hay que regenerarlo desde `/api/admin/access-tokens/{id}/regenerate`.

### ❌ No funciona
```
Authorization: ApiKey wabot_ext_M9V-Web7mCYTK83aGc-4MAFQGtX0kBSy
```

### ✅ Funciona
```
X-Api-Key: wabot_ext_M9V-Web7mCYTK83aGc-4MAFQGtX0kBSy
Authorization: Bearer wabot_ext_M9V-Web7mCYTK83aGc-4MAFQGtX0kBSy
```

---

## Autenticación general

Hay **dos sistemas de autenticación** separados:

| Sistema | Usado para | Cómo obtener |
|---------|-----------|--------------|
| **JWT Bearer** | Endpoints admin/operador (panel web) | `POST /api/auth/login` |
| **API Key** | Integraciones externas (`/api/external/*`) | Generar desde panel admin |

---

## 1. Autenticación JWT (operadores y admins)

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "is_admin": true,
    "is_active": true,
    "full_name": "Administrador"
  }
}
```

El token dura **8 horas**. Luego hay que volver a hacer login.

**Usar el token:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

### Verificar usuario actual

```http
GET /api/auth/me
Authorization: Bearer <jwt_token>
```

---

### Cambiar contraseña

```http
POST /api/auth/change-password
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "old_password": "admin123",
  "new_password": "nueva_clave_segura"
}
```

---

## 2. API Keys para integraciones externas

### Flujo de vida de una API Key

```
Admin genera token  →  api_key visible UNA SOLA VEZ
        ↓
Guardar en sistema externo
        ↓
Usar en header X-Api-Key o Authorization: Bearer
        ↓
Si se pierde → regenerar (invalida la anterior)
```

### Listar tokens existentes

```http
GET /api/admin/access-tokens
Authorization: Bearer <jwt_admin_token>
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "turnero",
    "token_prefix": "wabot_ext_M9V-Web7",
    "description": "turnos",
    "allowed_event_types": "*",
    "is_active": true,
    "created_by": "admin",
    "last_used_at": null,
    "created_at": "2026-03-14T23:28:24"
  }
]
```

> El `token_prefix` sirve para identificar el token pero **no** es el token completo.

---

### Crear nuevo token

```http
POST /api/admin/access-tokens
Authorization: Bearer <jwt_admin_token>
Content-Type: application/json

{
  "name": "mi-sistema-crm",
  "description": "Notificaciones desde CRM",
  "allowed_event_types": "*"
}
```

> `allowed_event_types`: `"*"` para todos, o CSV como `"turno,factura"`.

**Respuesta — el `api_key` solo aparece aquí, guardarlo:**
```json
{
  "id": 2,
  "name": "mi-sistema-crm",
  "token_prefix": "wabot_ext_AbCd1234",
  "allowed_event_types": "*",
  "is_active": true,
  "api_key": "wabot_ext_AbCd1234xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

### Regenerar token (cuando se pierde o hay que rotar)

```http
POST /api/admin/access-tokens/{id}/regenerate
Authorization: Bearer <jwt_admin_token>
```

Invalida el token anterior. El nuevo `api_key` se devuelve en la respuesta.

---

### Activar/Desactivar token

```http
POST /api/admin/access-tokens/{id}/toggle
Authorization: Bearer <jwt_admin_token>
```

---

### Eliminar token

```http
DELETE /api/admin/access-tokens/{id}
Authorization: Bearer <jwt_admin_token>
```

---

## 3. Envío de notificaciones WhatsApp (integración externa)

**Endpoint:** `POST /api/external/notifications`  
**Auth:** API Key (X-Api-Key o Bearer)

### Formatos de número de teléfono (todos válidos)

| Formato | Interpretado como |
|---------|------------------|
| `+5491112345678` | `5491112345678` |
| `5491112345678` | `5491112345678` |
| `+54 911 1234 5678` | `5491112345678` |

> El `+` se elimina automáticamente. Los espacios se eliminan. El formato correcto es el código de país sin `+` seguido del número completo.

---

### Ejemplo 1 — Mensaje libre

```http
POST /api/external/notifications
X-Api-Key: wabot_ext_M9V-Web7mCYTK83aGc-4MAFQGtX0kBSy
Content-Type: application/json

{
  "event_type": "custom",
  "phone_number": "5491112345678",
  "message": "Hola! Tu turno fue confirmado para mañana a las 10:30hs."
}
```

**Respuesta (200):**
```json
{
  "ok": true,
  "provider": "waha",
  "event_type": "custom",
  "phone_number": "5491112345678",
  "access_token": "turnero"
}
```

---

### Ejemplo 2 — Recordatorio de turno (mensaje auto-generado)

```http
POST /api/external/notifications
X-Api-Key: wabot_ext_M9V-Web7mCYTK83aGc-4MAFQGtX0kBSy
Content-Type: application/json

{
  "event_type": "turno",
  "phone_number": "+5491112345678",
  "recipient_name": "Juan Pérez",
  "metadata": {
    "date": "2026-03-20",
    "time": "10:30",
    "professional": "Dr. García",
    "location": "Consultorio 3"
  }
}
```

Mensaje generado automáticamente:
```
Hola Juan Pérez.
Te enviamos un recordatorio de turno.
Fecha/Hora: 2026-03-20 10:30
Profesional: Dr. García
Lugar: Consultorio 3
Si necesitas reprogramar, responde a este mensaje.
```

---

### Ejemplo 3 — Notificación de factura

```http
POST /api/external/notifications
X-Api-Key: wabot_ext_M9V-Web7mCYTK83aGc-4MAFQGtX0kBSy
Content-Type: application/json

{
  "event_type": "factura",
  "phone_number": "5491112345678",
  "recipient_name": "Ana López",
  "metadata": {
    "invoice_number": "FC-00123",
    "amount": "$15.000",
    "due_date": "2026-03-31",
    "payment_url": "https://pago.clinicauom.com/FC-00123"
  }
}
```

---

### Campos del payload

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `event_type` | string | ✅ | Tipo de evento. Ver tabla abajo. |
| `phone_number` | string | ✅ | Número WhatsApp destino |
| `message` | string | ❌ | Texto libre. Si se envía, **ignora** el mensaje auto-generado |
| `recipient_name` | string | ❌ | Nombre del destinatario (usado en plantillas) |
| `source_system` | string | ❌ | Nombre del sistema que origina el evento |
| `metadata` | object | ❌ | Datos adicionales para las plantillas |

### Tipos de evento soportados

| `event_type` | Plantilla automática | Metadata relevante |
|-------------|---------------------|-------------------|
| `turno` / `appointment` / `appointment_reminder` | Recordatorio de turno | `date`, `time`, `professional`, `location` |
| `factura` / `invoice` / `invoice_ready` | Notificación de factura | `invoice_number`, `amount`, `due_date`, `payment_url` |
| `custom` o cualquier otro | Texto genérico con metadata | cualquier clave:valor |

> **Tip:** Si se especifica `message`, siempre se usa ese texto sin importar el `event_type`.

---

### Errores posibles

| Código | Mensaje | Causa |
|--------|---------|-------|
| `401` | `API key requerida` | No se envió header de autenticación |
| `401` | `API key inválida o inactiva` | Token incorrecto, expirado o desactivado |
| `403` | `event_type no permitido` | El token tiene restricción de event_types |
| `400` | `phone_number inválido` | Número vacío o formato no reconocido |
| `400` | `message vacío` | El mensaje resultante está vacío |
| `400` | `event_type requerido` | Campo `event_type` faltante o vacío |

---

## 4. Modo humano / Operador

### Listar conversaciones activas en modo humano

```http
GET /api/human-mode/list
Authorization: Bearer <jwt_token>
```

**Respuesta:**
```json
[
  {
    "phone": "5491112345678",
    "state": "waiting_agent",
    "human_mode_since": "2026-03-15T22:00:00",
    "last_message_at": "2026-03-15T22:05:00"
  }
]
```

**Estados posibles:**
- `waiting_agent` — esperando que un operador tome el caso
- `in_agent` — operador asignado y atendiendo
- `closed` — cerrado

---

### Ver mensajes de un chat

```http
GET /api/human-mode/messages/{phone}
Authorization: Bearer <jwt_token>
```

Ejemplo: `GET /api/human-mode/messages/5491112345678`

---

### Responder como operador

```http
POST /api/human-mode/reply
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "phone": "5491112345678",
  "message": "Hola, soy el operador. ¿En qué puedo ayudarte?"
}
```

---

### Cerrar ticket / devolver al bot

```http
POST /api/human-mode/close
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "phone": "5491112345678"
}
```

---

## 5. Configuración del bot

### Leer configuración actual

```http
GET /api/config
Authorization: Bearer <jwt_token>
```

### Actualizar configuración

```http
PUT /api/config
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "opening_time": "08:00",
  "closing_time": "19:00",
  "off_hours_enabled": true,
  "off_hours_message": "Estamos fuera de horario. Reabrimos el próximo día hábil.",
  "handoff_enabled": true
}
```

### Ver/Editar menú

```http
GET /api/config/menu
POST /api/config/menu
Authorization: Bearer <jwt_token>
```

---

## 6. Control del bot

```http
POST /bot/pause       # Pausar respuestas automáticas
POST /bot/resume      # Reanudar
POST /bot/connect     # Reconectar WhatsApp
POST /bot/logout      # Desconectar sesión WhatsApp
```

Todos requieren `Authorization: Bearer <jwt_admin_token>`.

---

## 7. Estado general

```http
GET /health                     # Sin auth — liveness check
GET /api/waha/status            # Estado WAHA (con JWT)
GET /api/debug/status           # Estado interno (con JWT)
```

**Health check:**
```json
{"ok": true, "provider": "waha", "instance": "default"}
```

---

## Tabla de referencia rápida

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | ninguna | Login, obtener JWT |
| `/api/auth/me` | GET | JWT | Usuario actual |
| `/api/auth/change-password` | POST | JWT | Cambiar contraseña |
| `/api/external/notifications` | POST | API Key | **Enviar mensaje WhatsApp** |
| `/api/admin/access-tokens` | GET/POST | JWT Admin | Listar/Crear API Keys |
| `/api/admin/access-tokens/{id}/regenerate` | POST | JWT Admin | Regenerar API Key |
| `/api/admin/access-tokens/{id}/toggle` | POST | JWT Admin | Activar/desactivar |
| `/api/admin/access-tokens/{id}` | DELETE | JWT Admin | Eliminar |
| `/api/human-mode/list` | GET | JWT | Conversaciones en modo humano |
| `/api/human-mode/reply` | POST | JWT | Responder como operador |
| `/api/human-mode/close` | POST | JWT | Cerrar ticket |
| `/api/config` | GET/PUT | JWT | Leer/actualizar config |
| `/bot/pause` \| `/bot/resume` | POST | JWT Admin | Control del bot |
| `/health` | GET | ninguna | Estado del servicio |

---

## Ejemplo completo: test de integración desde cero

```bash
BASE="http://localhost:8088"

# 1. Login admin
RESPONSE=$(curl -s -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')
JWT=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Crear API key para sistema externo
TOKEN_RESP=$(curl -s -X POST "$BASE/api/admin/access-tokens" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"name":"mi-crm","description":"Notificaciones CRM","allowed_event_types":"*"}')
API_KEY=$(echo $TOKEN_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['api_key'])")
echo "API Key: $API_KEY"   # ← Guardar este valor

# 3. Enviar notificación WhatsApp
curl -s -X POST "$BASE/api/external/notifications" \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "turno",
    "phone_number": "5491112345678",
    "recipient_name": "Juan Pérez",
    "metadata": {
      "date": "2026-03-20",
      "time": "10:30",
      "professional": "Dr. García"
    }
  }'
```

---

*Generado: 2026-03-15 | API versión 2.2.20*
