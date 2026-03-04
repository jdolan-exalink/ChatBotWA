# ⚡ Cheat Sheet: Menús Multinivel + N8N

## 🚀 Inicio Rápido (30 segundos)

### 1. Agregar opción al menú
```markdown
## 1️⃣ Mi Opción
Descripción breve
1. Subopciones
2. Más opciones
```

### 2. Agregar subopciones (nivel 2)
```markdown
### 1.1 Subopciones
Descripción
1. Acción
```

### 3. Conectar a N8N
```markdown
#### 1.1.1 Acción N8N

[N8N] action_id
WEBHOOK: https://webhook.n8n.io/myaction

Descripción que ve el usuario
```

### 4. Desplegar
```bash
# Editar /data/MenuP.MD directamente
# Reiniciar (opcional, se recarga automáticamente)

# Probar
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+5491234567890", "body": "1"}'
```

---

## 📐 Estructura de Headers

```
##      = Nivel 1 (Opciones principales)
###     = Nivel 2 (Subopciones)
####    = Nivel 3 (Sub-subopciones)
#####   = Nivel 4 (Acciones finales)
```

**Regla:** Cada nivel agregado = 1 `#` más

---

## 🔗 Integración N8N: 3 pasos

### Paso 1: Detectar acción en MenuP.MD
```markdown
[N8N] unique_action_name
WEBHOOK: https://your-webhook.url

Usuario ve esto...
```

### Paso 2: Bot extrae y envía
```json
POST /api/menu-action
{
  "action_id": "unique_action_name",
  "from": "+5491234567890",
  "context": {...request context...}
}
```

### Paso 3: N8N responde
```json
{
  "ok": true,
  "message": "Acción procesada",
  "status": "pending"
}
```

---

## 🗂️ Rutas de Estado

```
Usuario envía "1" → Bot busca "menu_1"
Usuario envía "1" → Bot busca "menu_1_1"
Usuario envía "0" → Bot retorna a "main"
```

**Archivo:** Estado guardado en DB (chat_id → section)

---

## 🐛 Debug Rápido

```bash
# Ver menú compilado
grep "^##" data/MenuP.MD

# Ver acciones N8N definidas
grep "\[N8N\]" data/MenuP.MD

# Ver estructura completa
cat data/MenuP.MD | less

# Probar navegación específica
curl -X POST http://localhost:8088/webhook \
  -H "Content-Type: application/json" \
  -d '{"from": "+549123", "body": "1"}'

# Ver logs
docker compose logs wa-bot -f

# Verificar que archivo se recarga
# (Edita MenuP.MD y envía mensaje - cambios inmediatos)
```

---

## ✅ Checklist antes de push

- [ ] Headers tienen `#` correcto (##, ###, ####, #####)
- [ ] Numeración es continua (1, 2, 3... no 1, 3, 5)
- [ ] `### 1.1` tiene `## 1` arriba
- [ ] `#### 1.1.1` tiene `### 1.1` arriba
- [ ] Sin espacios en blanco entre números
- [ ] [N8N] solo en líneas de acción final
- [ ] WEBHOOK: URLs válidas y activas
- [ ] Emojis representan la acción
- [ ] "0" siempre retorna a menú principal
- [ ] Probé navegación hasta nivel 4-5

---

## 🎯 Casos de Uso Rápidos

### Turnos/Citas
```markdown
## 1️⃣ Turnos
### 1.1 🩺 Especialidad
#### 1.1.1 👨‍⚕️ Doctor
##### 1.1.1.1 📅 Agendar → [N8N] book_appointment
```

### Consultas
```markdown
## 2️⃣ Consultas
### 2.1 📋 Mi Estado
#### 2.1.1 💊 Prescripciones → [N8N] list_prescriptions
```

### Pagos
```markdown
## 3️⃣ Pagos
### 3.1 💳 Métodos
#### 3.1.1 🏦 Transferencia → [N8N] payment_transfer
```

---

## 📊 Límites

| Parámetro | Límite |
|-----------|--------|
| Profundidad | 5+ niveles posibles |
| Opciones por nivel | Sin límite |
| Usuarios simultáneos | Depende de WAHA |
| Webhooks N8N | Sin límite |
| Tamaño MenuP.MD | Hasta varios MB |
| Respuesta menú | <100ms (sin N8N) |
| Respuesta con N8N | 1-10 segundos |

---

## 🔧 Variables en Webhooks N8N

El bot envía:
```json
{
  "from": "+5491234567890",          // Teléfono usuario
  "action_id": "action_name",        // De [N8N] metadata
  "current_section": "menu_1_1_1",  // Dónde está usuario
  "timestamp": "2026-03-04T...",    // Cuándo
  "context": {                       // Datos opcionales
    "name": "Usuario",
    "custom_field": "valor"
  }
}
```

---

## 🚨 Errores Comunes

### ❌ "Opción no disponible"
- Verificar `##`, `###`, `####` son correctos
- Asegurar numeración continua

### ❌ Bot no responde
- Ver Docker logs: `docker compose logs`
- Verificar WAHA conectado: `docker compose ps`

### ❌ N8N no se dispara
- Verificar [N8N] en MenuP.MD
- Verificar WEBHOOK: URL correcta
- Ver logs: `grep N8N docker logs`

### ❌ Usuario se queda en menú antiguo
- Datos en DB no se actualizaron
- Resetear estado: `DELETE FROM chats WHERE...`

---

## 📱 Comandos del Usuario

```
"0"      → Ir a menú principal (desde cualquier nivel)
"1"      → Seleccionar opción 1
"2"      → Seleccionar opción 2
"hola"   → Mostrar menú principal
"Menu"   → Mostrar menú principal
"salir"  → Salir (retorna a main)
```

---

## 🔐 Autenticación N8N

### Headers requeridos en `/api/menu-action`:
```bash
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json
```

### Token está en:
- Variables de entorno: `API_TOKEN`
- Base de datos: tabla `admin_users`
- FastAPI bearers: `Depends(get_current_admin)`

---

## 📈 Performance Tips

1. **Menú<2KB**: Carga en <50ms
2. **N8N respuesta<2s**: Usuario no abandona
3. **Emojis pequeños**: Carga más rápido en WhatsApp
4. **Limitar a 8 opciones**: UX más clara

---

## 🎓 Relación: Número de # vs Ruta

```
MARKDOWN          RUTA DE ESTADO
========          ==============
## 1             main → "1" → menu_1
### 1.1          menu_1 → "1" → menu_1_1  
#### 1.1.1       menu_1_1 → "1" → menu_1_1_1
##### 1.1.1.1    menu_1_1_1 → "1" → menu_1_1_1_1
```

**Fórmula:** `num_hashes = len(path_parts) + 2`

---

## 🔄 Ciclo Completo (Diagrama ASCII)

```
Usuario escribe "1"
    ↓
Bot recibe en /webhook
    ↓
Extrae current_section del DB (ej: "menu_1")
    ↓
Carga MenuP.MD y busca "### 1.1"
    ↓
Si tiene [N8N] → POST /api/menu-action
    ↓
Bot espera respuesta (opcional)
    ↓
Actualiza DB: section = "menu_1_1"
    ↓
Responde al usuario con contenido
    ↓
Usuario lee respuesta en WhatsApp
```

---

## 📚 Referencias Rápidas

| Archivo | Para Qué |
|---------|----------|
| `MENU_SETUP_GUIDE.md` | Conceptos y teoría completa |
| `IMPLEMENTATION_SUMMARY.md` | Cómo está hecho el sistema |
| `PRACTICAL_EXAMPLES.md` | Ejemplos reales listos para copiar |
| `CHEAT_SHEET.md` | Este archivo (referencia rápida) |
| `MenuP.MD` | Menú actual en vivo |
| `MenuP_example.md` | Ejemplo de estructura 5 niveles |

---

## ⏱️ Tiempo de Implementación

| Tarea | Tiempo |
|-------|--------|
| Agregar menú simple | 2 min |
| Agregar 2 niveles | 5 min |
| Conectar N8N | 10 min (si N8N existe) |
| Testear completo | 5 min |
| **Total para caso nuevo** | **~20 min** |

---

**Última actualización:** Marzo 4, 2026
**Versión:** 1.0
**Comandos más usados al principio:** `cat MenuP.MD | grep "^##"` y `docker compose logs -f`
