# Integracion con Sistemas Externos

Esta guia permite conectar ERPs, CRMs, sistemas de turnos o facturacion para enviar notificaciones por WhatsApp usando la API del bot.

## 1) Crear Access Token en Admin

Ruta en panel:

`Dashboard -> Configuracion -> Sistema -> Access Token (Sistemas Externos)`

Pasos:

1. Completar `Nombre del acceso`.
2. Opcional: completar `Eventos permitidos` (CSV) o dejar `*` para permitir todos.
3. Presionar `Crear acceso (auto genera API key)`.
4. Guardar la API key generada (solo se muestra completa una vez).

Tambien podras:

- Regenerar API key.
- Activar/Desactivar el acceso.
- Eliminar el acceso.

## 2) Endpoint para enviar notificaciones

- Metodo: `POST`
- URL: `/api/external/notifications`
- Auth: header `X-API-Key` con la API key generada en Admin

Headers:

```http
Content-Type: application/json
X-API-Key: wabot_ext_xxxxxxxxxxxxxxxxx
```

Body base:

```json
{
  "event_type": "custom",
  "phone_number": "+5491122334455",
  "message": "Hola, este es un mensaje de prueba",
  "recipient_name": "Juan Perez",
  "source_system": "ERP Central",
  "metadata": {}
}
```

## 3) Eventos sugeridos

### 3.1 Turnos

`event_type` recomendados:

- `appointment_reminder`
- `appointment`
- `turno`

Si no envias `message`, el bot arma automaticamente un texto de recordatorio usando `metadata`.

Ejemplo:

```json
{
  "event_type": "appointment_reminder",
  "phone_number": "+5491122334455",
  "recipient_name": "Maria Lopez",
  "source_system": "Agenda Clinica",
  "metadata": {
    "date": "2026-03-20",
    "time": "09:30",
    "professional": "Dra. Gomez",
    "location": "Sede Centro"
  }
}
```

### 3.2 Facturas

`event_type` recomendados:

- `invoice_ready`
- `invoice`
- `factura`

Si no envias `message`, el bot arma automaticamente un texto de factura usando `metadata`.

Ejemplo:

```json
{
  "event_type": "invoice_ready",
  "phone_number": "+5491166677788",
  "recipient_name": "Carlos Diaz",
  "source_system": "ERP Facturacion",
  "metadata": {
    "invoice_number": "FAC-000234",
    "amount": "$ 18.500",
    "due_date": "2026-03-25",
    "payment_url": "https://miempresa.com/pagar/FAC-000234"
  }
}
```

## 4) Ejemplos cURL

### 4.1 Mensaje de turno

```bash
curl -X POST http://localhost:8088/api/external/notifications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wabot_ext_TU_API_KEY" \
  -d '{
    "event_type": "appointment_reminder",
    "phone_number": "+5491122334455",
    "recipient_name": "Maria Lopez",
    "source_system": "Agenda Clinica",
    "metadata": {
      "date": "2026-03-20",
      "time": "09:30",
      "professional": "Dra. Gomez",
      "location": "Sede Centro"
    }
  }'
```

### 4.2 Mensaje de factura

```bash
curl -X POST http://localhost:8088/api/external/notifications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wabot_ext_TU_API_KEY" \
  -d '{
    "event_type": "invoice_ready",
    "phone_number": "+5491166677788",
    "recipient_name": "Carlos Diaz",
    "source_system": "ERP Facturacion",
    "metadata": {
      "invoice_number": "FAC-000234",
      "amount": "$ 18.500",
      "due_date": "2026-03-25"
    }
  }'
```

### 4.3 Mensaje custom directo

```bash
curl -X POST http://localhost:8088/api/external/notifications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wabot_ext_TU_API_KEY" \
  -d '{
    "event_type": "custom",
    "phone_number": "+5491177788899",
    "message": "Tu pedido #A-5543 ya esta listo para retiro.",
    "source_system": "ERP Logistica"
  }'
```

## 5) Respuestas de la API

Exito:

```json
{
  "ok": true,
  "provider": "waha",
  "event_type": "appointment_reminder",
  "phone_number": "5491122334455",
  "access_token": "ERP Facturacion"
}
```

Errores comunes:

- `401`: API key faltante o invalida.
- `403`: `event_type` no permitido para ese Access Token.
- `400`: payload invalido (por ejemplo `phone_number` incorrecto o `event_type` vacio).

## 6) Seguridad recomendada

- Crear un token por sistema externo (no compartir entre apps).
- Definir `event_type` restringidos por token cuando sea posible.
- Rotar API keys periodicamente usando `Regenerar`.
- Desactivar inmediatamente tokens sospechosos.
