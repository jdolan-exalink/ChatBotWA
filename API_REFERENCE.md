# 🔌 Referencia de API Endpoints

## Base URL
```
http://localhost:8088
```

## Integracion Externa (Nuevo)

Para integrar sistemas externos (turnos, facturas, etc.) usando `Access Token` autogenerado desde Admin, ver:

- `INTEGRACION_SISTEMAS_EXTERNOS.md`

---

## 📲 Webhooks WhatsApp

### `POST /webhook` - Recibir mensaje de usuario
Punto de entrada principal para mensajes entrantes.

**Request:**
```json
{
  "from": "+5491234567890",
  "body": "1"
}
```

**Headers:**
```
Content-Type: application/json
```

**Response:**
```json
{
  "ok": true
}
```

**Ejemplos:**
```bash
# Menú principal
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+5491234567890", "body": "hola"}'

# Navegar opción 1
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+5491234567890", "body": "1"}'

# Volver al menú (opción 0)
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+5491234567890", "body": "0"}'
```

---

## 🤖 N8N Integration

### `POST /api/menu-action` - Ejecutar acción N8N
Endpoint para disparar acciones en N8N desde el menú.

**Authentication:** Bearer Token (required)

**Request:**
```json
{
  "action_id": "unique_action_identifier",
  "chat_id": "+5491234567890",
  "user_data": {
    "name": "Juan Pérez",
    "email": "juan@example.com"
  },
  "context": {
    "specialty": "Clínica Médica",
    "doctor": "Dra. Gómez"
  }
}
```

**Headers:**
```
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json
```

**Response:**
```json
{
  "ok": true,
  "action_id": "unique_action_identifier",
  "message": "Acción unique_action_identifier procesada",
  "status": "pending"
}
```

**Ejemplos:**
```bash
# Agendar turno
curl -X POST http://localhost:8088/api/menu-action \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "action_id": "appointment_book",
    "chat_id": "+5491234567890",
    "user_data": {
      "name": "María García"
    },
    "context": {
      "specialty": "Clínica Médica",
      "doctor": "Dra. Gómez",
      "date": "2026-03-08",
      "time": "09:00"
    }
  }'

# Consultar afiliación
curl -X POST http://localhost:8088/api/menu-action \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "action_id": "check_affiliation",
    "chat_id": "+5491234567890",
    "user_data": {}
  }'
```

---

## 📧 Email

### `POST /api/send-email` - Enviar email
Envía emails desde el sistema.

**Authentication:** Bearer Token (required)

**Request:**
```json
{
  "to": "usuario@example.com",
  "subject": "Asunto",
  "body": "Contenido del email"
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Email enviado"
}
```

**Ejemplos:**
```bash
curl -X POST http://localhost:8088/api/send-email \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "paciente@gmail.com",
    "subject": "Confirmación de turno",
    "body": "Tu turno ha sido confirmado para el 08/03/2026..."
  }'
```

---

## 📋 Configuración de Menú

### `GET /api/config/menu` - Obtener menú actual
Retorna el contenido completo del menú.

**Authentication:** Bearer Token (optional)

**Response:**
```json
{
  "ok": true,
  "menu": "## 1️⃣ Turnos\n### 1.1 🩺 Clínica Médica\n..."
}
```

**Ejemplo:**
```bash
curl -X GET http://localhost:8088/api/config/menu \
  -H "Authorization: Bearer your-token-here"
```

---

### `POST /api/config/menu` - Actualizar menú
Reemplaza el menú con nuevo contenido.

**Authentication:** Bearer Token (required)

**Request:**
```json
{
  "menu": "## 1️⃣ Turnos\n### 1.1 Opción\n..."
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Menú actualizado"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8088/api/config/menu \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "menu": "## 1️⃣ Turnos\n### 1.1 Nueva opción\n..."
  }'
```

---

## 👤 Autenticación y Admin

### `POST /api/login` - Login de admin
Obtiene token de autenticación.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8088/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

---

### `GET /api/me` - Obtener info del usuario actual
Retorna información del usuario autenticado.

**Authentication:** Bearer Token (required)

**Response:**
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin"
}
```

**Ejemplo:**
```bash
curl -X GET http://localhost:8088/api/me \
  -H "Authorization: Bearer your-token-here"
```

---

## 📊 Estadísticas y Datos

### `GET /api/stats` - Estadísticas del sistema
Retorna estadísticas de uso.

**Authentication:** Bearer Token (optional)

**Response:**
```json
{
  "ok": true,
  "total_users": 150,
  "total_messages": 2543,
  "active_users_today": 25,
  "most_used_menu": "1️⃣ Turnos"
}
```

---

### `GET /api/chats` - Listar conversaciones
Obtiene lista de conversaciones.

**Authentication:** Bearer Token (required)

**Query Parameters:**
```
?page=1&limit=20&search=5491234567890
```

**Response:**
```json
{
  "ok": true,
  "data": [
    {
      "chat_id": "+5491234567890",
      "last_message": "Agendar turno",
      "current_section": "menu_1_1_1",
      "updated_at": "2026-03-04T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1
}
```

---

### `GET /api/chats/{chat_id}` - Obtener conversación específica
Retorna detalles de una conversación.

**Authentication:** Bearer Token (required)

**Response:**
```json
{
  "ok": true,
  "chat_id": "+5491234567890",
  "state": {
    "section": "menu_1_1_1",
    "created_at": "2026-02-28T14:30:00Z",
    "updated_at": "2026-03-04T10:30:00Z"
  }
}
```

**Ejemplo:**
```bash
curl -X GET http://localhost:8088/api/chats/5491234567890 \
  -H "Authorization: Bearer your-token-here"
```

---

## 🔍 Búsqueda y Consultas

### `GET /api/search/menu` - Buscar en menú
Busca opciones en el menú.

**Query Parameters:**
```
?q=turno&level=1
```

**Response:**
```json
{
  "ok": true,
  "results": [
    {
      "section": "menu_1",
      "title": "1️⃣ Turnos",
      "description": "Agendar turnos..."
    }
  ]
}
```

---

## 🚀 Salud del Sistema

### `GET /api/health` - Estado del sistema
Verifica que todo esté funcionando.

**Authentication:** None (public)

**Response:**
```json
{
  "status": "ok",
  "api_version": "1.0",
  "database": "connected",
  "waha": "connected",
  "uptime_seconds": 86400
}
```

**Ejemplo:**
```bash
curl -X GET http://localhost:8088/api/health
```

---

### `GET /api/health/detailed` - Estado detallado
Información completa del sistema.

**Response:**
```json
{
  "ok": true,
  "api": "ok",
  "database": {
    "status": "connected",
    "tables": 15
  },
  "waha": {
    "status": "connected",
    "port": 3100,
    "sessions": 1
  },
  "cache": {
    "items": 245
  }
}
```

---

## 📝 Logs

### `GET /api/logs` - Obtener logs
Retorna logs del sistema.

**Authentication:** Bearer Token (required)

**Query Parameters:**
```
?level=info&limit=100&chat_id=5491234567890
```

**Response:**
```json
{
  "ok": true,
  "logs": [
    {
      "timestamp": "2026-03-04T10:30:00Z",
      "level": "info",
      "message": "Navegación: menu_1 → menu_1_1",
      "chat_id": "+5491234567890"
    }
  ]
}
```

---

## 🔐 Seguridad y Rate Limiting

### Headers recomendados en todas las requests:
```
Content-Type: application/json
Authorization: Bearer YOUR_API_TOKEN
User-Agent: MyApp/1.0
```

### Rate Limiting:
- **Límite general:** 100 requests/minuto por IP
- **Limite de /webhook:** 1000 requests/minuto
- **Limite de /api/menu-action:** 100 requests/minuto

### Códigos de Error:
```
200 - OK
400 - Bad Request
401 - Unauthorized
403 - Forbidden
404 - Not Found
429 - Too Many Requests
500 - Internal Server Error
```

---

## 📖 Ejemplos de Flujos Completos

### Flujo 1: Usuario navega menú → N8N

```bash
# 1. Usuario envía "1"
curl -X POST http://localhost:8088/webhook \
  -d '{"from": "+5491234567890", "body": "1"}'

# 2. Bot retorna menú nivel 2
# Respuesta: "### 1.1 🩺 Clínica Médica..."

# 3. Usuario envía "1" nuevamente
curl -X POST http://localhost:8088/webhook \
  -d '{"from": "+5491234567890", "body": "1"}'

# 4. Bot retorna menú nivel 3
# Respuesta: "#### 1.1.1 👩‍⚕️ Dra. Gómez..."

# 5. Usuario envía "1" una vez más
curl -X POST http://localhost:8088/webhook \
  -d '{"from": "+5491234567890", "body": "1"}'

# 6. Bot detecta [N8N] action_id
# Bot hace POST /api/menu-action automáticamente
# Respuesta al usuario: "✅ Turno confirmado..."
```

### Flujo 2: Admin actualiza menú programáticamente

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8088/api/login \
  -d '{"username":"admin","password":"pass"}' | jq -r '.access_token')

# 2. Obtener menú actual
curl -X GET http://localhost:8088/api/config/menu \
  -H "Authorization: Bearer $TOKEN"

# 3. Actualizar menú
curl -X POST http://localhost:8088/api/config/menu \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"menu": "## Nueva estructura..."}'

# 4. Verificar
curl -X GET http://localhost:8088/api/config/menu \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 Testing con Postman

### Variables de entorno Postman:
```json
{
  "base_url": "http://localhost:8088",
  "token": "your-bearer-token",
  "test_phone": "+5491234567890"
}
```

### Collection de requests:
```json
{
  "info": {
    "name": "Clinic Bot API",
    "version": "1.0"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/health"
      }
    },
    {
      "name": "Send Message",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/webhook",
        "body": {
          "from": "{{test_phone}}",
          "body": "1"
        }
      }
    },
    {
      "name": "Menu Action",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/menu-action",
        "header": {
          "Authorization": "Bearer {{token}}"
        },
        "body": {
          "action_id": "appointment_book",
          "chat_id": "{{test_phone}}"
        }
      }
    }
  ]
}
```

---

**Última actualización:** Marzo 4, 2026
**Versión:** 1.0
**Endpoint base:** `http://localhost:8088`
**Documentación:** Ver `MENU_SETUP_GUIDE.md` para conceptos
