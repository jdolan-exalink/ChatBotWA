# Clínica WhatsApp Bot - Guía Completa del Sistema

## Descripción General

Sistema integral de chatbot para WhatsApp con gestión de usuarios, administración avanzada, control de horarios y antispam.

## Actualización Marzo 2026

Se aplicaron mejoras para evitar menús vacíos en configuración y alinear la API de configuración:

- Corrección de resolución de rutas de archivos `MenuP.MD` y `MenuF.MD`.
- Compatibilidad completa en Docker (`/app/data`) y entorno local (`data/` en raíz del proyecto).
- Nuevos endpoints de lectura:
  - `GET /api/config/menu`
  - `GET /api/config/offhours`
- Endpoint de actualización de menú con doble método:
  - `POST /api/config/menu`
  - `PUT /api/config/menu`
- Soporte de payload en dos formatos para actualización de menú:
  - `{"content": "..."}`
  - `{"menu": "..."}`

### Características Principales

✅ **Autenticación y Gestión de Usuarios**
- Login con usuario y contraseña
- Dos roles: Usuario y Administrador
- Gestión de contraseñas hashidas con bcrypt
- Tokens JWT para sesiones seguras

✅ **Control del Bot por Usuarios**
- Los usuarios pueden pausar y reanudar el bot
- Panel personal simple y funcional
- No interferencia con funciones de admin

✅ **Panel de Administrador Completo**
- Gestión de usuarios (crear, editar, eliminar, resetear contraseña)
- Configuración flexible del nombre de la solución
- Editor de menú en tiempo real
- Sistema de horarios de atención
- Gestión de feriados con calendario

✅ **Menú Dinámico por Horarios**
- Menú diferente fuera de horarios
- Menú especial para fines de semana
- Detección automática de feriados
- Mensajes personalizados fuera de horario

✅ **Sistema Antispam**
- Lista negra de números de WhatsApp
- Sistema de filtros por país/provincia
- Bloqueo automático de números  

✅ **Integración con WhatsApp**
- Usa WAHA (WhatsApp Web API)
- Escaneo de QR automático
- Conexión segura y confiable
- Soporte para Evolution API

✅ **IA con Ollama**
- Respuestas automáticas inteligentes
- Integración con modelos LLM
- Base de conocimiento personalizable

---

## Instalación y Configuración

### 1. Requisitos Previos

```bash
# Instalar dependencias del sistema
apt-get update
apt-get install -y python3.11 python3-pip docker.io
```

### 2. Configuración de Archivo .env

Crear archivo `.env` en la raíz del proyecto:

```env
# WhatsApp / WAHA
WAHA_API_KEY=your-api-key-here
WAHA_SESSION=default
WAHA_URL=http://waha:3000

# Base de Datos
DATABASE_URL=sqlite:///./clinic_bot.db
# O para PostgreSQL:
# DATABASE_URL=postgresql://usuario:contraseña@localhost/clinic_bot

# Seguridad
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
SOLUTION_NAME=Clínica San José

# IA Ollama
OLLAMA_URL=http://10.1.1.39:11434
OLLAMA_MODEL=lfm2:latest

# Email (opcional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
ALERT_EMAIL_TO=
ALERT_EMAIL_FROM=

# N8N (opcional)
N8N_EVENT_WEBHOOK=
```

### 3. Iniciar con Docker Compose

```bash
cd /opt/clinic-whatsapp-bot
docker-compose up -d
```

El sistema creará automáticamente:
- Admin por defecto: `admin` / `admin123`
- Configuración inicial en la BD
- Tablas necesarias

---

## Uso del Sistema

### Acceso Principal

**URL Base:** `http://localhost:8088`

### Flujo de Usuario Regular

1. **Acceder al panel:** `/login`
2. **Introducir credenciales**
3. **Panel de usuario:** `/user-panel`
   - Pausar el bot
   - Reanudar el bot
   - Cerrar sesión

### Flujo de Administrador

1. **Acceder al panel:** `/login`
2. **Introducir credenciales admin**
3. **Dashboard completo:** `/dashboard`

#### Opciones en Dashboard

**📊 Estado**
- Ver estado de conexión WhatsApp
- Ver QR para escanear
- Pausar/Reanudar bot
- Desconectar WhatsApp

**👥 Usuarios**
- Listar todos los usuarios
- Crear nuevos usuarios
- Editar usuarios existentes
- Resetear contraseñas
- Cambiar roles (Usuario/Admin)
- Eliminar usuarios

**⚙️ Configuración**
- Cambiar nombre de la solución
- Configurar título del menú
- Establecer horarios (apertura/cierre)
- Habilitar menú fuera de horarios
- Configurar URL y modelo de Ollama

**📝 Menú**
- Editor de menú principal en Markdown
- Visualización en tiempo real
- Guardar cambios

**🗓️ Feriados**
- Agregar días feriados
- Eliminar feriados
- Los feriados se tratan como fuera de horarios

**⏱️ Fuera de Horario**
- Crear menús especiales para fuera de horarios
- Habilitar/deshabilitar menús
- Mensajes personalizados

**🚫 Lista Negra**
- Bloquear números de WhatsApp
- Agregar razones de bloqueo
- Desbloquear números

---

## API REST - Endpoints Principales

### Autenticación

```bash
# Login
POST /api/auth/login
{
  "username": "usuario",
  "password": "contraseña"
}

# Obtener info del usuario actual
GET /api/auth/me
Headers: Authorization: Bearer {token}

# Cambiar contraseña
POST /api/auth/change-password
{
  "old_password": "antigua",
  "new_password": "nueva"
}
```

### Gestión de Usuarios (Solo Admin)

```bash
# Listar usuarios
GET /api/admin/users

# Crear usuario
POST /api/admin/users
{
  "username": "nuevo_usuario",
  "email": "user@example.com",
  "password": "contraseña",
  "full_name": "Nombre Completo",
  "is_admin": false
}

# Actualizar usuario
PUT /api/admin/users/{user_id}

# Eliminar usuario
DELETE /api/admin/users/{user_id}

# Resetear contraseña
POST /api/admin/users/{user_id}/reset-password
{
  "new_password": "nueva_contraseña"
}

# Pausar/Reanudar usuario
POST /api/admin/users/{user_id}/toggle-pause
```

### Configuración del Bot

```bash
# Obtener configuración
GET /api/config

# Actualizar configuración
PUT /api/config
{
  "solution_name": "Nueva Clínica",
  "menu_title": "Bienvenido",
  "opening_time": "08:00",
  "closing_time": "17:00",
  "off_hours_enabled": true,
  "off_hours_message": "Fuera de horarios"
}

# Obtener menú principal (archivo MenuP.MD)
GET /api/config/menu

# Actualizar menú principal
POST /api/config/menu
{
  "content": "# Menú\n1) Turnos"
}

# También válido por compatibilidad
PUT /api/config/menu
{
  "menu": "# Menú\n1) Turnos"
}

# Obtener configuración fuera de horario (MenuF.MD)
GET /api/config/offhours
```

### Feriados

```bash
# Listar feriados
GET /api/holidays

# Crear feriado
POST /api/holidays
{
  "date": "2024-12-25",
  "name": "Navidad",
  "description": "Día de Navidad"
}

# Eliminar feriado
DELETE /api/holidays/{holiday_id}
```

### Menús Fuera de Horario

```bash
# Listar menús
GET /api/holiday-menus

# Crear menú
POST /api/holiday-menus
{
  "name": "Menú Nocturno",
  "content": "Contenido en Markdown"
}

# Actualizar menú
PUT /api/holiday-menus/{menu_id}

# Eliminar menú
DELETE /api/holiday-menus/{menu_id}
```

### Control del Bot

```bash
# Pausar bot
POST /bot/pause
Headers: Authorization: Bearer {token}

# Reanudar bot
POST /bot/resume
Headers: Authorization: Bearer {token}

# Desconectar WhatsApp
POST /bot/logout
Headers: Authorization: Bearer {token}

# Estado del bot
GET /status

# Obtener QR
GET /qr

# Healthcheck
GET /health
```

---

## Base de Datos - Modelos

### Tabla: users
```sql
id: INTEGER (primary key)
username: VARCHAR(255) - Único
email: VARCHAR(255) - Único
hashed_password: VARCHAR(255)
full_name: VARCHAR(255)
is_admin: BOOLEAN (default: False)
is_active: BOOLEAN (default: True)
is_paused: BOOLEAN (default: False)
created_at: DATETIME
updated_at: DATETIME
last_login: DATETIME
```

### Tabla: bot_config
```sql
id: INTEGER (primary key)
solution_name: VARCHAR(255)
menu_title: VARCHAR(255)
is_paused: BOOLEAN
opening_time: VARCHAR(5) - HH:MM
closing_time: VARCHAR(5) - HH:MM
off_hours_enabled: BOOLEAN
off_hours_message: TEXT
ollama_url: VARCHAR(255)
ollama_model: VARCHAR(255)
admin_idle_timeout_sec: INTEGER (default: 900)
updated_at: DATETIME
```

### Tabla: holidays
```sql
id: INTEGER (primary key)
date: VARCHAR(10) - YYYY-MM-DD (Único)
name: VARCHAR(255)
description: TEXT
created_at: DATETIME
```

### Tabla: holiday_menus
```sql
id: INTEGER (primary key)
name: VARCHAR(255) (Único)
content: TEXT
is_active: BOOLEAN (default: True)
created_at: DATETIME
updated_at: DATETIME
```

### Tabla: whatsapp_blocklist
```sql
id: INTEGER (primary key)
phone_number: VARCHAR(20) (Único)
reason: VARCHAR(255)
blocked_at: DATETIME
```

### Tabla: country_filters
```sql
id: INTEGER (primary key)
country_code: VARCHAR(2) - Ej: 'AR'
country_name: VARCHAR(255)
allowed_provinces: TEXT - JSON
is_enabled: BOOLEAN
created_at: DATETIME
```

---

## Detalles Técnicos

### Stack Tecnológico

- **Framework:** FastAPI (Python 3.11+)
- **BD:** SQLAlchemy con SQLite/PostgreSQL
- **Autenticación:** JWT + bcrypt
- **WhatsApp:** WAHA API
- **IA:** Ollama
- **Frontend:** HTML5 + Vanilla JavaScript
- **Containers:** Docker Compose

### Estructura de Archivos

```
clinic-bot-api/
├── app.py                 # Applicación principal con todos los endpoints
├── database.py           # Configuración de SQLAlchemy
├── models.py            # Modelos de Base de Datos (SQLAlchemy)
├── schemas.py           # Esquemas Pydantic (validación)
├── security.py          # Funciones de seguridad (JWT, hash)
├── pages.py             # Funciones para renderizar pages HTML
├── requirements.txt    # Dependencias Python
├── Dockerfile         # Imagen Docker
└── clinic_bot.db      # Base de datos SQLite (creada automáticamente)
```

### Flujo de Autenticación

1. Usuario entra credenciales en `/login`
2. Se valida contra BCrypt en tabla `users`
3. Se genera token JWT válido por 60 minutos
4. Token se almacena en localStorage del navegador
5. Cada request incluye `Authorization: Bearer {token}`
6. Servidor valida JWT y extrae info del usuario

### Flujo de Mensajes WhatsApp

1. WAHA recibe mensaje en WhatsApp
2. Webhook POST a `/webhook` con payload
3. Sistema verifica:
   - ¿Está el bot pausado?
   - ¿Está el número bloqueado?
   - ¿Es fuera de horario?
4. Si es horario normal → usa menú inteligente
5. Si es fuera de horario → usa menú especial
6. Respuesta se envía vía WAHA API

---

## Configuración Avanzada

### Usar PostgreSQL en Lugar de SQLite

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/clinic_bot
```

### Habilitar CORS

Ya está configurado para permitir todos los orígenes. En producción, modificar:

```python
# En app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tudominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Aumentar Timeout de Admin

```env
ADMIN_IDLE_TIMEOUT_SEC=1800  # 30 minutos
```

### Usuarios Paused vs Bot Paused

- **Usuario Paused:** Ese usuario específico no puede usar el bot
- **Bot Paused:** Nadie puede usar el bot (solo admin)

---

## Troubleshooting

### "Base de datos locked"

**Solución:** SQLite tiene limitaciones de concurrencia.
```bash
# Cambiar a PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/clinic
```

### "Token inválido"

```bash
# Verificar SECRET_KEY en .env
# Generar una nueva:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### "No conecta a WhatsApp"

1. Verificar que WAHA está corriendo: `docker ps`
2. Verificar WAHA_API_KEY en .env
3. Revisitar QR: http://localhost:8088/qr
4. Resetear WAHA: `docker-compose restart waha`

### "Ollama no responde"

```bash
# Verificar que Ollama está corriendo
curl http://10.1.1.39:11434/api/tags

# Descargar un modelo
ollama pull lfm2:latest
```

---

## Mejoras Futuras Sugeridas

1. **Sistemas de logs avanzados** con ELK Stack
2. **Análisis de mensajes** (sentimiento, clasificación)
3. **Dashboard de estadísticas** (mensajes, usuarios activos)
4. **Integración con CRM** (Salesforce, Hubspot)
5. **Webhooks personalizados** para eventos
6. **Rate limiting** por usuario
7. **Encriptación de datos sensibles** en BD
8. **Backup automático** de BD
9. **Notificaciones email/Telegram** para eventos
10. **Multi-idioma** en interfaz

---

## Soporte y Contribuciones

Para reportar bugs o solicitar features, contactar al equipo de desarrollo.

**Última actualización:** Marzo 2026
**Versión:** 0.3.0

---

*Documentación completa del Sistema de Clínica WhatsApp Bot*
