# 📊 Resumen de Implementación: Menús Multinivel y N8N Integration

## ✅ Completado

### 1. Sistema de Menús Multinivel (5+ Niveles)

El sistema ahora soporta navegación en **5 o más niveles de profundidad**:

```
Nivel 1 (main)           
    └─── Nivel 2 (##)     ← Opciones principales 1-7
         └─── Nivel 3 (###)   ← Subopciones 1.1, 1.2, etc.
              └─── Nivel 4 (####)  ← Detalles 1.1.1, 1.1.2, etc.
                   └─── Nivel 5 (#####) ← Acciones 1.1.1.1, 1.1.1.2, etc.
```

**Ejemplo de Flujo Real:**
```
Usuario "1" (main)                        → Level 2: ## 1️⃣ Turnos
Usuario "1" (menu_1)                      → Level 3: ### 1.1 Clínica Médica
Usuario "1" (menu_1_1)                    → Level 4: #### 1.1.1 Dra. Gómez
Usuario "1" (menu_1_1_1)                  → Level 5: ##### 1.1.1.1 Agendar turno
Usuario "1" (menu_1_1_1_1) - opcional     → Level 6: ###### 1.1.1.1.1 (si existe)
```

### 2. Estructura de Archivo MenuP.MD

El archivo ahora sigue esta estructura:

```markdown
# Encabezado (NO se usa)

Introducción y menú principal

---

## 1️⃣ Opción Principal
Contenido nivel 2...

### 1.1 Sub-opción
Contenido nivel 3...

#### 1.1.1 Detalle
Contenido nivel 4...

##### 1.1.1.1 Acción/Información Final
Contenido nivel 5...

---

## 2️⃣ Otra Opción
...
```

### 3. Lógica de Navegación Mejorada

La función `get_menu_section()` ahora:

✅ **Acepta caminos dinámicos**: menu_X_Y_Z_W
✅ **Calcula profundidad automáticamente**: len(path) + 2 = número de #
✅ **Busca encabezados correctos**: Busca `#### 1.1.1` cuando está en menu_1_1
✅ **Evita sub-subsecciones**: No muestra ##### cuando estás en nivel 4
✅ **Manejo de errores**: Devuelve "Opción no disponible" si no existe

### 4. Endpoint N8N Integration

**Nuevo endpoint creado:** `POST /api/menu-action`

```json
Body esperado:
{
  "action_id": "create_appointment",
  "chat_id": "5491234567890",
  "user_data": {...},
  "context": {...}
}

Response:
{
  "ok": true,
  "action_id": "create_appointment",
  "status": "pending"
}
```

### 5. Metadatos N8N en MenuP.MD

El sistema reconoce metadatos especiales:

```markdown
##### 1.1.1.1 📅 Agendar Turno

[N8N] create_appointment
WEBHOOK: https://webhook.tudominio.n8n.io/turno

Contenido...
```

Cuando el usuario selecciona una opción con metadatos [N8N], el sistema:
1. Detecta la etiqueta [N8N]
2. Obtiene el action_id
3. Hace POST a `/api/menu-action`
4. N8N procesa la acción

---

## 🧪 Pruebas Realizadas

### Prueba 1: Navegación Multinivel
✅ Level 1 → Level 2 (## turnos)
✅ Level 2 → Level 3 (### clínica médica)
✅ Level 3 → Level 4 (#### dra gómez)
✅ Level 4 → Level 5 (##### agendar turno)
✅ Opción "0" regresa a main desde cualquier nivel

### Prueba 2: Manejo de Errores
✅ Usuario escribe letra → "Debes escribir un número"
✅ Usuario escribe opción inexistente → "Opción no disponible"
✅ Navigation hacia arriba funciona (puede cambiar de rama)

### Prueba 3: Formato de Respuesta
✅ Muestra encabezado correcto
✅ Muestra opciones sin subsecciones más profundas
✅ Formatea con emojis y bullets
✅ Incluye separador --- cuando correponde

---

## 📋 Estructura de MenuP.MD Actual

**Capas implementadas:**

### Turno (menu_1)
- 1.1 Clínica Médica (menu_1_1)
  - 1.1.1 Dra. Gómez Vanesa (menu_1_1_1)
    - 1.1.1.1 ✅ Agendar turno [N8N]
    - 1.1.1.2 ✅ Contactar teléfono
  - 1.1.2 Dr. Aramayo (menu_1_1_2)
    - 1.1.2.1 ✅ Agendar turno [N8N]
    - 1.1.2.2 ✅ Contactar teléfono
  - 1.1.3 Dra. Sánchez (menu_1_1_3)
    - 1.1.3.1 ✅ Llamar para agendar
- 1.2 Traumatología (menu_1_2)
  - 1.2.1 Dr. Meoli (menu_1_2_1)
    - 1.2.1.1 ✅ Agendar turno [N8N]
    - 1.2.1.2 ✅ Contactar teléfono

### Asuntos Laborales (menu_2)
- 2.1 WhatsApp Línea 1 (menu_2_1)
- 2.2 WhatsApp Línea 2 (menu_2_2)
- 2.3 WhatsApp Línea 3 (menu_2_3)
- 2.4 Consultas Generales (menu_2_4)
  - 2.4.1 ✅ Enviar email RRHH [N8N]
  - 2.4.2 ✅ Preguntas frecuentes

### Otros (3, 4, 5, 6, 7)
✅ Farmacia
✅ Afiliaciones
✅ Discapacidad
✅ Bocas de expendio
✅ Compra de orden

---

## 🔗 Cómo Conectar con N8N

### Paso 1: Crear Webhook en N8N

1. Abre tu instancia de N8N
2. Crea un nuevo workflow
3. Agrega un nodo "Webhook Trigger"
4. Copia la URL:  `https://tudominio.n8n.io/webhook/xxx`

### Paso 2: Actualizar MenuP.MD

```markdown
##### 1.1.1.1 📅 Agendar Turno

[N8N] create_appointment
WEBHOOK: https://tudominio.n8n.io/webhook/agendar-turno

Contenido...
```

### Paso 3: Configurar N8N Workflow

El webhook recibe:
```json
{
  "from": "5491234567890",
  "action": "create_appointment",
  "specialty": "Clínica Médica",
  "doctor": "Dra. Gómez",
  "timestamp": "2026-03-04T10:30:00Z"
}
```

N8N puede:
1. **Guardar en base de datos**
2. **Enviar confirmación por email**
3. **Crear evento en calendario**
4. **Notificar al usuario por WhatsApp**

### Paso 4: Respuesta a Usuario

Desde N8N, haz un HTTP REQUEST POST a:
```
POST http://localhost:8088/webhook

{
  "from": "5491234567890",
  "body": "✅ Turno confirmado para el 08/03/2026 09:00"
}
```

---

## 📚 Archivos Relacionados

| Archivo | Descripción |
|---------|-------------|
| `/MENU_SETUP_GUIDE.md` | Guía completa de configuración (este directorio) |
| `/data/MenuP.MD` | Menú principal actual (498 líneas, 5 niveles) |
| `/data/MenuP.MD.backup` | Backup de versión anterior |
| `/data/MenuP_example.md` | Ejemplo original (para referencia) |
| `/services/clinic-bot-api/app.py` | Código Python con nueva lógica |

---

## 🚀 Próximos Pasos (Opcionales)

1. **Persistencia de N8N URLs**
   - Crear tabla DB: `menu_actions` (action_id, webhook_url, description)
   - Consultar desde app.py cuando se detecta [N8N]

2. **Análisis de Uso**
   - Loguear ruta de navegación completa
   -  Reportes de qué opciones son más usadas

3. **Actualización Dinámica**
   - Permitir editar MenuP.MD desde dashboard
   - Validar estructura automáticamente
   - Preview en tiempo real

4. **Multi-idioma**
   - Crear MenuP_EN.MD,MenuP_PT.MD
   - Detectar idioma del usuario
   - Servir menú según preferencia

5. **Estadísticas**
   - Dashboard con usuarios activos, opciones más usadas
   - Integración con Google Sheets vía N8N

---

## 💡 Casos de Uso Avanzados

### Caso 1: Turno Inteligente
```
Usuario -> Turnos -> Clínica Médica -> Dra. Gómez -> Agendar Turno
           ↓
        [N8N Webhook]
           ↓
        Valida disponibilidad
        Reserva en Google Calendar
        Envía confirmación por SMS/WhatsApp
        Guarda en base de datos
```

### Caso 2: Soporte Técnico
```
Usuario -> Soporte -> Problema técnico -> Contactar -> Enviar ticket
            ↓
         [N8N Webhook]
            ↓
         Crea ticket en Jira
         Asigna equipo correspondiente
         Envía confirmación al usuario
         Agenda follow-up automático
```

### Caso 3: Compras Online
```
Usuario -> Tienda -> Productos -> Producto X -> Comprar
            ↓
         [N8N Webhook]
            ↓
         Valida stock
         Procesa pago (Stripe/PayPal)
         Genera orden
         Avisa almacén
         Envía link de seguimiento
```

---

## 📞 Soporte

Para configur problemas:

1. **Verificar estructura MenuP.MD**:
   ```bash
   grep "^#" /opt/clinic-whatsapp-bot/data/MenuP.MD | head -20
   ```

2. **Ver logs en tiempo real**:
   ```bash
   docker compose logs clinic-bot-api -f | grep WEBHOOK
   ```

3. **Validar JSON de acciones**:
   ```bash
   curl -X POST http://localhost:8088/api/menu-action \
     -H "Authorization: Bearer TOKEN" \
     -d '{"action_id": "test", "chat_id": "123"}'
   ```

---

**Creado:** Marzo 4, 2026
**Versión:** 2.0 - Menús Multinivel + N8N Integration
**Estado:** ✅ Completado y Testeado
