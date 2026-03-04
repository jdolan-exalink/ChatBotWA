# 📋 Guía de Configuración de Menús Multinivel y Conexión con N8N

## 📖 Tabla de Contenidos
1. [Estructura de Menús](#estructura-de-menús)
2. [Sistema de Navegación](#sistema-de-navegación)
3. [Conectar con N8N](#conectar-con-n8n)
4. [Ejemplos Prácticos](#ejemplos-prácticos)
5. [API Reference](#api-reference)

---

## 🏗️ Estructura de Menús

### Niveles de Profundidad

El sistema soporta **menús multinivel ilimitados** usando markdown headers:

```
# Encabezado Principal (NO se usa - reservado)
## Nivel 1: Menú Principal (opciones 1, 2, 3...)
### Nivel 2: Submenú (opciones 1.1, 1.2, 1.3...)
#### Nivel 3: Sub-submenú (opciones 1.1.1, 1.1.2...)
##### Nivel 4: Sub-sub-submenú (opciones 1.1.1.1...)
```

### Reglas de Formato

1. **Separadores de sección**: Usa `---` para separar visualmente bloques
2. **Numeración automática**: Solo números, sin emojis en los títulos (los emojis van al inicio)
3. **Detalles no editables**: Las líneas de detalle (no numeradas) se muestran solo en subsecciones

### Ejemplo Básico

```markdown
# 🏥 Sistema de Atención

Bienvenido. Selecciona una opción:

1️⃣ Turnos
2️⃣ Asuntos Laborales
3️⃣ Farmacia

↩️ Escribe 0 para volver al menú principal.

---

## 1️⃣ Turnos

Seleccionaste Turnos. Elige especialidad:

1. 🩺 Clínica Médica
2. 🦴 Traumatología
3. 🫀 Cardiología

13. ↩️ Volver al menú principal

---

### 1.1 🩺 Clínica Médica

Profesionales disponibles:

1. 👩‍⚕️ **Dra. Gómez Vanesa**
   • Martes 09:00-11:00 H.
   • Tel: 5802184

2. 👨‍⚕️ **Dr. Aramayo Alejandro**
   • Miércoles 09:30-12:30 H.

---

### 1.2 🦴 Traumatología

Profesional:
👨‍⚕️ **Dr. Daniel Meoli**
• Lunes 10:00 H.
```

---

## 🧭 Sistema de Navegación

### Estados de Navegación

El sistema mantiene el estado del usuario usando identificadores de sección:

```
main                    # Menú principal
↓
menu_1                  # Nivel 1: Opción 1 seleccionada
↓
menu_1_1                # Nivel 2: Opción 1.1 seleccionada
↓
menu_1_1_1              # Nivel 3: Opción 1.1.1 seleccionada
```

### Flujo de Navegación

```
Usuario enviá "1" en menu_1_2_3 
    ↓
Sistema busca encabezado #### 1.2.3.1
    ↓
Si existe → Muestra contenido de 1.2.3.1 (sin sub-encabezados #####)
Si no existe → Retorna error "Opción no disponible"
```

### Reglas Especiales

- **Opción "0"**: Siempre regresa al menú principal (main)
- **Números válidos**: Solo se aceptan dígitos
- **Sin saltos**: Debes navegar secuencialmente (no puedes ir de 1 → 1.2 directamente)

---

## 🔗 Conectar con N8N

### Configuración Básica

1. **Crear webhook en N8N**
   ```
   Tu URL de N8N: https://tudominio.n8n.io/webhook/clinic-bot
   ```

2. **Almacenar URL en base de datos**
   ```sql
   INSERT INTO menu_actions (action_id, n8n_webhook_url, description)
   VALUES ('create_appointment', 'https://tudominio.n8n.io/webhook/crear-turno', 'Crear turno');
   ```

3. **Marcar en menú con metadatos**
   ```markdown
   #### 1.1.1 📅 Agendar Turno
   [N8N] create_appointment
   URL: https://tudominio.n8n.io/webhook/crear-turno
   
   Presiona 1 para agendar con Dra. Gómez
   ```

### Estructura de Datos Enviados a N8N

Cuando el usuario interactúa con una opción conectada a N8N, se envían:

```json
{
  "action_id": "create_appointment",
  "chat_id": "5491234567890",
  "user_name": "Usuario",
  "menu_path": ["1", "1", "1"],
  "timestamp": "2026-03-04T10:30:00Z",
  "context": {
    "specialist": "Clínica Médica",
    "doctor": "Dra. Gómez Vanesa"
  }
}
```

### Webhook en N8N

Crea un flujo en N8N que:

1. **Recibe** el webhook desde el bot
2. **Procesa** la información (validar, guardar, etc.)
3. **Responde** con confirmación
4. **Notifica** al usuario via WhatsApp

Ejemplo de flujo N8N:
```
Webhook Trigger
    ↓
Extract Data (chat_id, action_id)
    ↓
Database Insert (guardar turno)
    ↓
HTTP Request to Bot API
    POST /api/send_message
    {
      "chat_id": "5491234567890",
      "message": "✅ Turno confirmado para el 08/03/2026 a las 09:00"
    }
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Turnos con Especialidades (2 Niveles)

```markdown
## 1️⃣ Turnos

Elige una especialidad:

1. 🩺 Clínica Médica
2. 🦴 Traumatología
3. 🫀 Cardiología

---

### 1.1 🩺 Clínica Médica

Médicos disponibles:

1. Dra. Gómez (Mar/Jue)
2. Dr. Aramayo (Mié)

---

### 1.2 🦴 Traumatología

Médicos disponibles:

1. Dr. Meoli (Lun)
```

**Navegación:**
- Usuario: "1" (desde main) → Muestra ## 1️⃣ Turnos
- Usuario: "1" (desde menu_1) → Muestra ### 1.1 Clínica Médica
- Usuario: "1" (desde menu_1_1) → Muestra detalle del doctor

### Ejemplo 2: Turnos con Sub-especialidades (3 Niveles)

```markdown
## 1️⃣ Turnos

Elige área:

1. 👨‍⚕️ Clínica General
2. 👩‍⚕️ Ginecología

---

### 1.1 👨‍⚕️ Clínica General

Elige especialista:

1. Medicina Interna
2. Cardiología

---

#### 1.1.1 Medicina Interna

Médicos disponibles:

1. Dr. López
2. Dra. García

---

#### 1.1.2 Cardiología

Médicos disponibles:

1. Dr. Pérez
```

**Navegación:**
- "1" (main) → Clínica General
- "1" (menu_1) → Medicina Interna  
- "1" (menu_1_1) → Dr. López

### Ejemplo 3: Conectar a N8N

```markdown
#### 1.1.1 📅 Agendar Turno

[N8N] create_appointment
WEBHOOK: https://n8n.tudominio.io/webhook/turno

¿Confirmás el turno con Dra. Gómez el 08/03/2026 09:00?

1. ✅ Confirmar turno
2. ❌ Volver atrás

---

#### 1.1.1.1 ✅ Turno Confirmado

Tu turno ha sido reservado.

📅 Fecha: 08/03/2026
⏰ Hora: 09:00
👨‍⚕️ Médico: Dra. Gómez
```

Cuando el usuario selecciona "1", el bot:
1. Detecta el metadato `[N8N]`
2. Hace POST a `/api/menu-action` con `action_id: create_appointment`
3. N8N procesa y confirma
4. Bot envía respuesta al usuario

---

## 🔌 API Reference

### Endpoint: Menu Action Handler

**Ruta:** `POST /api/menu-action`

**Autenticación:** Bearer token (admin)

**Body:**
```json
{
  "action_id": "create_appointment",
  "chat_id": "5491234567890",
  "user_data": {
    "name": "Juan",
    "specialty": "Clínica Médica",
    "doctor": "Dra. Gómez"
  },
  "context": {
    "menu_path": ["1", "1"],
    "timestamp": "2026-03-04T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "ok": true,
  "action_id": "create_appointment",
  "message": "Acción create_appointment procesada",
  "status": "pending"
}
```

### Endpoint: Enviar Mensaje WhatsApp

**Ruta:** `POST /webhook` (internamente desde N8N)

**Body (desde N8N):**
```json
{
  "chat_id": "5491234567890",
  "body": "✅ Turno confirmado para el 08/03/2026"
}
```

---

## 🧪 Testing y Pruebas

### Prueba 1: Navegación Básica

```bash
# Primer mensaje (menú principal)
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "5491234567890", "body": "hola"}'

# Seleccionar opción 1
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "5491234567890", "body": "1"}'

# Seleccionar opción 1 dentro de 1
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "5491234567890", "body": "1"}'

# Volver al menú
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "5491234567890", "body": "0"}'
```

### Prueba 2: Acción N8N

```bash
# Enviar acción a N8N
curl -X POST http://localhost:8088/api/menu-action \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu_token_admin" \
  -d '{
    "action_id": "create_appointment",
    "chat_id": "5491234567890",
    "user_data": {"specialty": "Clínica Médica"}
  }'
```

---

## 📝 Checklist de Implementación

- [ ] Crear estructura de menú en MenuP.MD con múltiples niveles
- [ ] Probar navegación en cada nivel
- [ ] Crear cuenta en N8N (si no la tienes)
- [ ] Crear webhook en N8N para acciones
- [ ] Agregar metadatos `[N8N]` en MenuP.MD para acciones
- [ ] Probar endpoint `/api/menu-action`
- [ ] Configurar flujo N8N completo
- [ ] Hacer prueba end-to-end

---

## 🎯 Mejores Prácticas

1. **Estructura clara**: Usa máximo 4 niveles de profundidad
2. **Numeración consistente**: Siempre secuencial (1, 2, 3...)
3. **Descripciones breves**: El usuario ve en WhatsApp (caracteres limitados)
4. **Contextualización**: Indica en qué nivel está el usuario ("Especialidad:", "Médico:", etc.)
5. **Volver atrás**: Incluye siempre opción "0" o final con número para regresar
6. **N8N tardío**: Conecta acciones en niveles profundos (no en nivel 1)
7. **Validación**: N8N debe validar datos antes de confirmar

---

## 🛠️ Debugging

**Problema:** Usuario escribe número pero aparece "Opción no disponible"
- Verifica que el header tiene la profundidad correcta (## para nivel 1, ### para nivel 2, etc.)
- Verifica que no hay espacios extra en el formato

**Problema:** Se muestra sub-subsección cuando debería mostrar solo subsección
- El sistema detecta `####` (sub-subsección) automáticamente
- Si se muestra, es que la numeración es incorrecta (ej: 1.1.1 en vez de 1.1)

**Problema:** N8N no recibe el webhook
- Verifica URL en BD: `SELECT * FROM menu_actions WHERE action_id='create_appointment'`
- Verifica logs: `docker compose logs clinic-bot-api | grep "[N8N]"`

---

## ✅ Conclusión

You now have:
- ✅ Menús multinivel escalables
- ✅ Navegación fluida sin confusiones
- ✅ Integración lista con N8N
- ✅ API abierta para acciones personalizadas

¡Listo para implementar tantos niveles como necesites! 🚀
