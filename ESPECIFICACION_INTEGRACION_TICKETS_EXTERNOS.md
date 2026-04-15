# Especificacion de Integracion Externa por Access Token y Tickets

## 1. Objetivo

Este documento define como debe integrarse un sistema externo con WA-BOT para:

- autenticarse mediante Access Token;
- consultar tickets abiertos y su estado;
- leer el numero de telefono del cliente;
- leer mensajes recientes del chat;
- responder al cliente por API;
- cerrar tickets y devolver la conversacion al bot;
- manejar errores de autenticacion, validacion y negocio.

El objetivo es que el equipo externo desarrolle contra un contrato claro y estable, usando `ticket_id` como identificador funcional y no los IDs internos de base de datos.

## 2. Estado actual del backend

### 2.1 Ya implementado hoy

Con Access Token externo hoy existe:

- `POST /api/external/notifications`

Con JWT de usuario del panel hoy existen:

- `GET /api/tickets/list`
- `GET /api/human-mode/messages/{phone}`
- `POST /api/human-mode/reply`
- `POST /api/human-mode/close`

### 2.2 Conclusion tecnica

Hoy el backend ya tiene toda la logica de tickets, lectura de mensajes, respuesta y cierre, pero esa operacion esta expuesta al panel por JWT de usuario, no por Access Token externo.

Para una integracion externa completa se recomienda exponer una capa dedicada:

- `/api/external/tickets`
- `/api/external/tickets/{ticket_id}`
- `/api/external/tickets/{ticket_id}/messages`
- `/api/external/tickets/{ticket_id}/reply`
- `/api/external/tickets/{ticket_id}/close`

Este documento toma la logica ya existente y la convierte en un contrato de integracion para sistemas externos.

## 3. Autenticacion y conexion

## 3.1 Tipo de credencial

El sistema externo debe autenticarse con un Access Token generado desde el panel administrador.

Headers soportados:

```http
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
```

o bien:

```http
Authorization: Bearer wabot_ext_xxxxxxxxxxxxxxxxx
```

No usar:

```http
Authorization: ApiKey wabot_ext_xxxxxxxxxxxxxxxxx
```

Ese formato no esta soportado.

## 3.2 Ciclo de vida del Access Token

1. Un admin genera el token desde el panel.
2. El `api_key` completo se muestra una sola vez.
3. El sistema externo lo guarda en su vault o configuracion segura.
4. Si el token se pierde, se debe regenerar.
5. Al regenerarlo, el token anterior queda invalido.

## 3.3 Endpoints administrativos para tokens

Estos endpoints siguen usando JWT de admin:

- `GET /api/admin/access-tokens`
- `POST /api/admin/access-tokens`
- `POST /api/admin/access-tokens/{id}/regenerate`
- `POST /api/admin/access-tokens/{id}/toggle`
- `DELETE /api/admin/access-tokens/{id}`

## 3.4 Chequeos de conexion recomendados

Para diagnostico basico:

- `GET /health` para disponibilidad del servicio.
- `GET /version` para version desplegada.

Para estado operativo de WhatsApp, hoy existe:

- `GET /status`

pero requiere JWT de usuario. Si se quiere monitoreo externo por Access Token, se recomienda agregar:

- `GET /api/external/status`

Respuesta recomendada:

```json
{
  "ok": true,
  "provider": "waha",
  "instance": "default",
  "connected": true,
  "has_qr": false,
  "paused": false,
  "version": "2.2.20"
}
```

## 4. Modelo funcional de tickets

## 4.1 Identificadores

- `ticket_id`: identificador funcional y estable. Formato actual: `TKT-XXXXXXXX`.
- `phone_number`: numero normalizado del cliente, sin `+`, sin espacios.
- `chat_id`: formato interno de WhatsApp para transporte: `{phone_number}@c.us`.
- `id`: IDs como `act_123` o `hist_123` son internos del panel y no deben formar parte del contrato externo.

## 4.2 Campos relevantes del ticket

```json
{
  "ticket_id": "TKT-A1B2C3D4",
  "phone_number": "5491122334455",
  "current_state": "WAITING_AGENT",
  "ticket_status": "pendiente",
  "human_mode": true,
  "human_mode_expire": "2026-03-23T18:40:00Z",
  "menu_section": "menu_1_1",
  "menu_breadcrumb": "1.1 -> Turnos -> Clinica Medica",
  "opened_at": "2026-03-23T16:40:00Z",
  "closed_at": null
}
```

## 4.3 `current_state` vs `ticket_status`

Son dos conceptos distintos y ambos deben exponerse.

### `current_state`

Representa el estado conversacional:

- `BOT_MENU`: el cliente esta nuevamente en el flujo automatico.
- `COLLECTING_DATA`: el bot esta recopilando datos.
- `WAITING_AGENT`: el ticket fue creado y espera atencion humana.
- `IN_AGENT`: un operador o sistema externo esta atendiendo.
- `CLOSED`: estado logico de cierre.
- `BLACKLISTED`: numero bloqueado.

### `ticket_status`

Representa el estado operativo del ticket:

- `pendiente`: ticket abierto y en curso.
- `confirmado`: ticket atendido o aceptado por el sistema externo.
- `cancelado`: ticket cancelado.
- `timeout`: ticket cerrado por expiracion.
- `cerrado`: ticket finalizado manualmente.

## 4.4 Reglas de transicion

Flujo base:

1. El cliente envia `99` o entra a una opcion de menu con `{{TICKET}}`.
2. El sistema crea `ticket_id`.
3. El ticket queda en `current_state=WAITING_AGENT` y `ticket_status=pendiente`.
4. El sistema externo toma el ticket y responde al cliente.
5. El ticket pasa a `current_state=IN_AGENT`.
6. Cuando el caso termina, el sistema externo lo cierra.
7. La conversacion vuelve a `current_state=BOT_MENU` y el ticket pasa a historial.

Cierres posibles:

- cierre manual: `ticket_status=cerrado`
- cierre por timeout: `ticket_status=timeout`
- cancelacion: `ticket_status=cancelado`
- cierre por mensaje final del operador: `close_reason=escrito_saludos`

## 5. Contrato recomendado para integracion externa de tickets

## 5.1 Listar tickets

```http
GET /api/external/tickets
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
```

Filtros recomendados:

- `status=pendiente,confirmado`
- `state=WAITING_AGENT,IN_AGENT`
- `type=active|history|all`
- `limit=100`
- `offset=0`
- `updated_since=2026-03-23T00:00:00Z`

Respuesta recomendada:

```json
{
  "ok": true,
  "items": [
    {
      "ticket_id": "TKT-A1B2C3D4",
      "phone_number": "5491122334455",
      "current_state": "WAITING_AGENT",
      "ticket_status": "pendiente",
      "menu_section": "menu_1_1",
      "menu_breadcrumb": "1.1 -> Turnos -> Clinica Medica",
      "opened_at": "2026-03-23T16:40:00Z",
      "closed_at": null,
      "human_mode_expire": "2026-03-23T18:40:00Z",
      "type": "active"
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 1
  }
}
```

## 5.2 Obtener un ticket por `ticket_id`

```http
GET /api/external/tickets/TKT-A1B2C3D4
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
```

Respuesta recomendada:

```json
{
  "ok": true,
  "item": {
    "ticket_id": "TKT-A1B2C3D4",
    "phone_number": "5491122334455",
    "chat_id": "5491122334455@c.us",
    "current_state": "WAITING_AGENT",
    "ticket_status": "pendiente",
    "menu_section": "menu_1_1",
    "menu_breadcrumb": "1.1 -> Turnos -> Clinica Medica",
    "opened_at": "2026-03-23T16:40:00Z",
    "closed_at": null,
    "human_mode": true,
    "human_mode_expire": "2026-03-23T18:40:00Z",
    "source": "active"
  }
}
```

## 5.3 Leer mensajes del ticket

```http
GET /api/external/tickets/TKT-A1B2C3D4/messages?limit=40
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
```

Respuesta recomendada:

```json
{
  "ok": true,
  "ticket_id": "TKT-A1B2C3D4",
  "phone_number": "5491122334455",
  "messages": [
    {
      "id": "ABCD1234",
      "from_me": false,
      "body": "Hola, necesito ayuda con un turno",
      "timestamp": 1774284010,
      "type": "chat"
    },
    {
      "id": "EFGH5678",
      "from_me": true,
      "body": "Hola, te ayudo con eso.",
      "timestamp": 1774284070,
      "type": "chat"
    }
  ]
}
```

## 5.4 Responder al cliente por API

```http
POST /api/external/tickets/TKT-A1B2C3D4/reply
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
Content-Type: application/json

{
  "text": "Hola, ya revisamos tu caso. Te contacto para confirmarte el turno.",
  "agent_name": "CRM Operador 1",
  "mark_as_in_agent": true
}
```

Comportamiento esperado:

- busca el ticket por `ticket_id`;
- obtiene `phone_number`;
- convierte a `chat_id={phone_number}@c.us`;
- envia el mensaje por WhatsApp;
- si el ticket estaba en `WAITING_AGENT`, lo mueve a `IN_AGENT`;
- renueva timeout de modo humano.

Respuesta recomendada:

```json
{
  "ok": true,
  "ticket_id": "TKT-A1B2C3D4",
  "phone_number": "5491122334455",
  "current_state": "IN_AGENT",
  "ticket_status": "pendiente",
  "message_sent": true
}
```

## 5.5 Confirmar toma del ticket

Este endpoint es opcional pero recomendable cuando el sistema externo quiera marcar que ya asumio el caso aunque todavia no haya respondido.

```http
POST /api/external/tickets/TKT-A1B2C3D4/confirm
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
Content-Type: application/json

{
  "agent_name": "CRM Operador 1"
}
```

Respuesta recomendada:

```json
{
  "ok": true,
  "ticket_id": "TKT-A1B2C3D4",
  "current_state": "IN_AGENT",
  "ticket_status": "confirmado"
}
```

## 5.6 Cerrar ticket

```http
POST /api/external/tickets/TKT-A1B2C3D4/close
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
Content-Type: application/json

{
  "resolution": "Turno confirmado para el jueves",
  "operator_reply": "Gracias por contactarte. Tu consulta quedo resuelta.",
  "close_reason": "manual",
  "send_farewell_message": true
}
```

Comportamiento esperado:

- si `send_farewell_message=true`, enviar mensaje final al cliente;
- archivar ticket en historial;
- salir de `human_mode`;
- volver a `current_state=BOT_MENU`;
- dejar el ticket como `cerrado` en historial.

Respuesta recomendada:

```json
{
  "ok": true,
  "ticket_id": "TKT-A1B2C3D4",
  "closed": true,
  "ticket_status": "cerrado",
  "returned_to_bot": true
}
```

## 6. Ejemplo de flujo extremo a extremo

## 6.1 Paso 1 - El cliente abre ticket

Evento real dentro del bot:

- cliente envia `99`;
- el bot crea `ticket_id`;
- el ticket queda en `WAITING_AGENT`.

## 6.2 Paso 2 - El sistema externo lista pendientes

```bash
curl -X GET "http://localhost:8088/api/external/tickets?state=WAITING_AGENT&type=active" \
  -H "X-API-Key: wabot_ext_TU_API_KEY"
```

## 6.3 Paso 3 - El sistema externo lee el telefono y los mensajes

```bash
curl -X GET "http://localhost:8088/api/external/tickets/TKT-A1B2C3D4" \
  -H "X-API-Key: wabot_ext_TU_API_KEY"
```

```bash
curl -X GET "http://localhost:8088/api/external/tickets/TKT-A1B2C3D4/messages" \
  -H "X-API-Key: wabot_ext_TU_API_KEY"
```

## 6.4 Paso 4 - El sistema externo responde

```bash
curl -X POST "http://localhost:8088/api/external/tickets/TKT-A1B2C3D4/reply" \
  -H "X-API-Key: wabot_ext_TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hola, soy del area de turnos. Ya revise tu caso.",
    "agent_name": "Area Turnos",
    "mark_as_in_agent": true
  }'
```

## 6.5 Paso 5 - El sistema externo cierra

```bash
curl -X POST "http://localhost:8088/api/external/tickets/TKT-A1B2C3D4/close" \
  -H "X-API-Key: wabot_ext_TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": "Caso resuelto",
    "operator_reply": "Gracias por contactarte. Quedamos a disposicion.",
    "close_reason": "manual",
    "send_farewell_message": true
  }'
```

## 7. Manejo de errores

## 7.1 Errores reales ya presentes en el backend

Autenticacion externa:

- `401 API key requerida`
- `401 API key invalida o inactiva`
- `403 event_type no permitido para este Access Token`

Validacion ya existente:

- `400 event_type requerido`
- `400 phone_number requerido`
- `400 phone_number invalido`
- `400 phone_number y text requeridos`
- `400 message vacio`
- `404 No encontrado`
- `409 No se pudo crear token (duplicado)`

## 7.2 Errores recomendados para la API externa de tickets

El contrato de tickets deberia usar este formato:

```json
{
  "ok": false,
  "error": {
    "code": "ticket_not_found",
    "message": "No existe un ticket activo o historico con ese ticket_id"
  }
}
```

Codigos recomendados:

- `400 bad_request`: faltan datos o formato invalido.
- `401 unauthorized`: falta Access Token o es invalido.
- `403 forbidden`: token sin permisos para la operacion.
- `404 ticket_not_found`: no existe el ticket consultado.
- `409 invalid_transition`: la transicion no corresponde al estado actual.
- `409 already_closed`: el ticket ya estaba cerrado.
- `422 validation_error`: payload correcto a nivel JSON pero semantica invalida.
- `503 whatsapp_unavailable`: WAHA no disponible o sesion desconectada.

## 7.3 Casos concretos a contemplar

### Ticket inexistente

```json
{
  "ok": false,
  "error": {
    "code": "ticket_not_found",
    "message": "No existe un ticket con id TKT-XXXXXXX"
  }
}
```

### Ticket ya cerrado

```json
{
  "ok": false,
  "error": {
    "code": "already_closed",
    "message": "El ticket ya se encuentra cerrado"
  }
}
```

### Numero sin formato valido

```json
{
  "ok": false,
  "error": {
    "code": "invalid_phone_number",
    "message": "phone_number invalido"
  }
}
```

### WhatsApp no disponible

```json
{
  "ok": false,
  "error": {
    "code": "whatsapp_unavailable",
    "message": "No se pudo entregar el mensaje en WAHA"
  }
}
```

## 8. Reglas tecnicas para el sistema externo

- Guardar el Access Token en forma segura. Nunca hardcodearlo en frontend.
- Usar `ticket_id` como clave funcional.
- No depender de IDs internos tipo `act_123` o `hist_123`.
- Tratar `phone_number` como dato sensible.
- Si el sistema externo responde por API, debe registrar sus propios logs con `ticket_id`, `phone_number`, fecha y resultado.
- El sistema externo debe tolerar reintentos idempotentes en lectura y cierres duplicados.
- Si hace polling, se recomienda cada 10 a 30 segundos para tickets activos.
- Si el ticket pasa a `timeout`, el sistema externo debe dejar de responder sobre ese ticket y refrescar el listado.

## 9. Recomendacion de implementacion en backend

Para no duplicar logica ya existente, la nueva API externa de tickets deberia reutilizar internamente:

- `_get_external_access()` para autenticar;
- `ConversationState` y `TicketHistory` para lectura;
- `/api/human-mode/messages/{phone}` para obtener mensajes;
- `_send_wha()` para replies;
- `_close_ticket_with_fin()` o `_exit_human_mode()` para cierre;
- `_resume_ticket_from_history()` para reapertura futura, si se decide exponerla.

## 10. Resumen ejecutivo

La integracion externa por Access Token debe considerar dos capas:

1. Lo ya implementado hoy: notificaciones salientes por `POST /api/external/notifications`.
2. La capa recomendada para operacion de tickets: lectura, mensajes, reply, confirmacion y cierre por `ticket_id`.

Con este contrato, un sistema externo puede:

- detectar tickets nuevos;
- identificar al cliente por telefono;
- leer el chat;
- responder por API;
- mover el caso a atencion humana activa;
- cerrar el ticket y devolver al cliente al bot.
