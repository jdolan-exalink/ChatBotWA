# 🎯 Guía de Uso Práctico: Menús Multinivel + N8N

## 1️⃣ Ejemplo Básico: Agregar un Nuevo Menú

### Paso 1: Editar MenuP.MD

```markdown
## 8️⃣ Soporte Técnico

Necesitas ayuda con tu cuenta:

1. 🐛 Reportar un error
2. 📱 Problema con app
3. 🔐 Acceso/Contraseña
4. ↩️ Volver al menú principal

---

### 8.1 🐛 Reportar un Error

Cuéntanos el problema:

1. 📧 Reportar por email
2. 📞 Llamar a soporte
3. 💬 Chat en vivo
4. ↩️ Volver atrás

---

#### 8.1.1 📧 Reportar por Email

[N8N] report_bug_email
WEBHOOK: https://webhook.n8n.io/report-bug

Tu reporte será enviado al equipo de tecnología.

Contacto: soporte@clinica.com.ar

1. ↩️ Volver al menú principal
```

### Paso 2: Desplegar

```bash
# Editac en el editor web del dashboard
# O actualizar archivo directamente:
docker exec wa-bot python3 -c "
with open('data/MenuP.MD', 'a') as f:
    f.write('\n## 8️⃣ Soporte Técnico\n...')
"

# Reconstruir (no es necesario, lee dinamicamente)
docker compose restart wa-bot
```

### Paso 3: Probar

```bash
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "5491234567890", "body": "8"}'
  
# Respuesta:
# ## 8️⃣ Soporte Técnico
# Necesitas ayuda...
```

---

## 2️⃣ Ejemplo: Conectar Acción a N8N

### Caso: Agendar turno online

#### Paso 1: Crear Workflow en N8N

```
[Webhook Trigger]
    ↓ (recibe POST con action_id="appointment_book")
[Extraer datos from/specialty/doctor]
    ↓
[Database - Query: CHECK disponibilidad]
    ↓
[Crear en Google Calendar]
    ↓
[HTTP Request POST] → Bot WhatsApp
    ↓
[Email - Enviar confirmación]
```

**Webhook N8N URL:** `https://tudominio.n8n.io/webhook/booking`

#### Paso 2: Actualizar MenuP.MD

```markdown
##### 1.1.1.1 📅 Agendar Turno Ahora

[N8N] appointment_book
WEBHOOK: https://tudominio.n8n.io/webhook/booking

¿Confirmas que deseas agendar turno con Dra. Gómez?

Próximas disponibilidades:
• Martes 08/03 - 09:00 H.
• Martes 08/03 - 10:00 H.
• Jueves 10/03 - 14:00 H.

1. ✅ Confirmar 09:00
2. ✅ Confirmar 10:00
3. ✅ Confirmar 14:00
4. X Cancelar
```

#### Paso 3: N8N Recibe y Procesa

**Webhook recibe:**
```json
{
  "from": "+5491234567890",
  "action": "appointment_book",
  "specialty": "Clínica Médica",
  "doctor": "Dra. Gómez Vanesa",
  "timestamp": "2026-03-04T10:30:00Z"
}
```

**N8N hace:**
```javascript
// 1. Validar disponibilidad
const available = await db.query(
  "SELECT * FROM slots WHERE doctor_id=1 AND date='2026-03-08' AND time='09:00'"
);

if (!available) {
  return { error: "No disponible" };
}

// 2. Crear en Google Calendar
const event = {
  summary: "Turno Clínica Médica - Dra. Gómez",
  start: { dateTime: "2026-03-08T09:00:00" },
  attendees: [{ email: "paciente@gmail.com" }]
};
const calEvent = await googleCalendar.createEvent(event);

// 3. Notificar usuario
await fetch("http://localhost:8088/webhook", {
  method: "POST",
  body: {
    from: "+5491234567890",
    body: `✅ Turno confirmado!\n📅 Martes 08/03 - 09:00 H.\n👨‍⚕️ Dra. Gómez\n📍 Planta 2 - Consultorio 201`
  }
});

// 4. Guardar en DB
await db.insert("appointments", {
  patient_phone: "+5491234567890",
  doctor: "Dra. Gómez",
  date: "2026-03-08",
  time: "09:00:00",
  google_event_id: calEvent.id
});
```

---

## 3️⃣ Ejemplo: Menú Dinámico Basado en Datos

### Caso: Mostrar especialistas disponibles

**Idea:** En lugar de agregar manualmente cada especialista,  N8N genera el menú dinámicamente.

#### Paso 1: Endpoint de N8N que retorna menú

```javascript
// En N8N:
GET https://tudominio.n8n.io/api/menu/specialists

Response:
{
  "specialists": [
    {
      "id": 1,
      "name": "Dra. Gómez Vanesa",
      "specialty": "Medicina General",
      "available_slots": 3,
      "next_appointment": "2026-03-08 09:00"
    },
    {
      "id": 2,
      "name": "Dr. Aramayo Alejandro",
      "specialty": "Medicina General",
      "available_slots": 0,
      "next_appointment": "2026-03-15 10:00"
    }
  ]
}
```

#### Paso 2: Bot Fetch del Menú

```python
# En app.py - ejemplo

async def get_dynamic_menu_section(...):
    # Obtener datos de N8N
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://tudominio.n8n.io/api/menu/specialists"
        )
        specialists = response.json()["specialists"]
    
    # Construir menú dinámico
    menu = "### 1.1 🩺 Clínica Médica\n\n"
    menu += "Especialistas disponibles:\n\n"
    
    for i, spec in enumerate(specialists, 1):
        status = "✅" if spec["available_slots"] > 0 else "❌"
        menu += f"{i}. {status} {spec['name']}\n"
        menu += f"   Próximo: {spec['next_appointment']}\n\n"
    
    return menu
```

---

## 4️⃣ Ejemplo: Integración con Sistema Existente

### Caso: Consultar estado de afiliación

#### Paso 1: N8N conecta a tu API existente

```javascript
// N8N Workflow:

[Webhook Trigger] - Recibe request de bot
    ↓
[Extract] - obtener patient_phone
    ↓
[HTTP Request] - GET https://tuapi.clinica.com/api/patient/status?phone=...
    ↓
[Set Variables] - nombre, estado, plan
    ↓
[Text Template] - Construir respuesta
    ↓
[HTTP Request POST] - Enviar a Bot
```

#### Paso 2: MenuP.MD con acción

```markdown
### 5.1 📋 Consultar Mi Afiliación

[N8N] check_affiliation_status
WEBHOOK: https://webhook.n8n.io/affiliation-status

Consultando tu información...

Status: Activo ✅
Plan: Premium
Cobertura: 100%
Vencimiento: 15/12/2026

¿Necesitas algo más?

1. 📞 Contactar soporte
2. 🔄 Renovar plan
3. ↩️ Volver atrás
```

---

## 5️⃣ Monitoreo y Debugging

### Ver qué acciones se activan

```bash
# Terminal 1: Ver logs en tiempo real
docker compose logs wa-bot -f | grep -E "\[N8N\]|\[WEBHOOK\]"

# Output esperado:
# [WEBHOOK] Buscando opción: 1.1.1.1 (sección: menu_1_1_1)
# [N8N] Acción create_appointment detectada
# [N8N] POST a webhook...
```

### Testear un flujo completo

```bash
#!/bin/bash
# test_flow.sh

USER="5491234567890"
API="http://localhost:8088/webhook"

echo "1. Menú principal"
curl -s -X POST $API -H "Content-Type: application/json" \
  -d "{\"from\": \"$USER\", \"body\": \"hola\"}" | jq .

echo -e "\n2. Opción 1 (Turnos)"
curl -s -X POST $API -H "Content-Type: application/json" \
  -d "{\"from\": \"$USER\", \"body\": \"1\"}" | jq .

echo -e "\n3. Opción 1 (Clínica Médica)"
curl -s -X POST $API -H "Content-Type: application/json" \
  -d "{\"from\": \"$USER\", \"body\": \"1\"}" | jq .

echo -e "\n4. Opción 1 (Dra. Gómez)"
curl -s -X POST $API -H "Content-Type: application/json" \
  -d "{\"from\": \"$USER\", \"body\": \"1\"}" | jq .

echo -e "\n5. Opción 1 (Agendar turno - activa N8N)"
curl -s -X POST $API -H "Content-Type: application/json" \
  -d "{\"from\": \"$USER\", \"body\": \"1\"}" | jq .

echo -e "\nFlujo completado. Verifica los logs de N8N:"
echo "docker compose logs wa-bot | grep N8N"
```

### Validar estructura MenuP.MD

```bash
# Verificar que las numeraciones son correctas
python3 << 'EOF'
import re

with open('data/MenuP.MD', 'r') as f:
    lines = f.readlines()

current_sections = {}
for i, line in enumerate(lines, 1):
    match = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', line)
    if match:
        level = len(match.group(1))
        number = match.group(2)
        current_sections[level] = number
        print(f"Line {i}: {level}# - {number}")

# Verificar que no hay saltos (ej: 1.1.1 → 1.1.3)
print("\n✅ Estructura validada")
EOF
```

---

## 6️⃣ Troubleshooting

### Problema: Bot dice "Opción no disponible"

**Causas posibles:**

1. **Encabezado incorrecto**
   ```bash
   # Verificar formato
   grep "#### 1.1.1 " data/MenuP.MD
   # Debe ser: #### 1.1.1 (exactamente 4 #)
   ```

2. **Numeración discontinua**
   ```bash
   # Revisar que no hay saltos
   grep "^###" data/MenuP.MD | sort -V
   # 1.1, 1.2, 1.3 OK
   # 1.1, 1.3 ❌ (falta 1.2)
   ```

3. **Usuario en sección incorrecta**
   ```bash
   # Ver logs con sección actual
   docker compose logs -f | grep "sección actual"
   ```

### Problema: N8N No recibe el webhook

1. **Verificar URL**
   ```bash
   curl -X GET https://webhook.tudominio.n8n.io
   # Si da 404, la URL es incorrecta
   ```

2. **Verificar que MenuP.MD tiene [N8N]**
   ```bash
   grep "\[N8N\]" data/MenuP.MD
   # Debe aparecer al menos una línea
   ```

3. **Revisar logs del bot**
   ```bash
   docker compose logs | grep "N8N\|menu-action"
   ```

### Problema: Respuesta lenta desde N8N

- **N8N puede tardar 2-5 segundos** en procesar
- Considera un workflow más simple
- Si es crítico, usa `async` en N8N

---

## 📝 Checklist de Implementación

- [ ] Crear estructura básica en MenuP.MD (niveles ## y ###)
- [ ] Probar navegación en 2-3 niveles
- [ ] Crear cuenta N8N gratuita
- [ ] Crear primer webhook en N8N
- [ ] Agregar [N8N] metadata a MenuP.MD
- [ ] Conectar N8N a tu base de datos
- [ ] Testear flujo completo
- [ ] Agregar más opciones con [N8N]
- [ ] Implementar respuestas dinámicas
- [ ] Monitoreo en producción

---

## 🎓 Conceptos Clave

| Concepto | Definición |
|----------|-----------|
| **menu_1_1_1** | Identificador de sección (camino de navegación) |
| **[N8N]** | Metadato para detectar acciones especiales |
| **Webhook** | URL de N8N que recibe datos del bot |
| **Nivel de profundidad** | Cuántos # tiene el encabezado |
| **Separador ---** | Divide visualmente bloques en Markdown |
| **Emoji** | Funcional (dra👩‍⚕️, número 1️⃣, volver ↩️) |

---

**Última actualización:** Marzo 4, 2026
**Versión:** 1.0
