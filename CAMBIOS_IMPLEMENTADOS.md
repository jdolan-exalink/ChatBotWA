# 🚀 Sistema Integral de Clínica WhatsApp Bot - Resumen de Cambios

## 🆕 Nuevos Cambios Técnicos (Marzo 2026)

### ✅ Corrección de carga de menús en Configuración

Se resolvió el problema donde `MenuP.MD` y `MenuF.MD` aparecían en blanco en pantalla de configuración.

Implementación realizada:

- Mejora en resolución de rutas de datos (`_data_path`) para soportar:
  - `DATA_DIR` (si está definido)
  - `/app/data` (Docker)
  - `services/clinic-bot-api/data` (legacy)
  - `data/` en raíz del proyecto (local)
- Fallback estable para creación inicial de archivos en local.

### ✅ Endpoints de configuración alineados

- Nuevo `GET /api/config/menu` para leer `MenuP.MD`.
- Nuevo `GET /api/config/offhours` para leer estado y mensaje fuera de horario.
- `POST /api/config/menu` agregado como alias de `PUT /api/config/menu`.
- Update de menú acepta payload con `content` o `menu`.

### ✅ Documentación actualizada

- `API_REFERENCE.md` alineado con métodos y payload reales.
- Se reflejan los nuevos endpoints y compatibilidad de payload.

## ✨ Cambios Principales Implementados

### 1. **Sistema Completo de Autenticación y Usuarios**
- ✅ Login seguro con usuario y contraseña
- ✅ Hashing de contraseñas con bcrypt
- ✅ Tokens JWT para sesiones seguras
- ✅ Dos roles: Usuario y Administrador
- ✅ Gestión completa de usuarios por admin

### 2. **Panel de Administrador Avanzado**
**Ubicación:** `/dashboard`
- 📊 **Estado:** Ver conexión WhatsApp, QR, pausar/reanudar
- 👥 **Usuarios:** Crear, editar, eliminar, resetear contraseña, cambiar roles
- ⚙️ **Configuración:** Nombre solución, horarios, Ollama
- 📝 **Menú:** Editor visual del menú principal
- 🗓️ **Feriados:** Agregar/eliminar días feriados
- ⏱️ **Fuera de Horario:** Menús especiales para fuera de horarios
- 🚫 **Lista Negra:** Bloquear números de WhatsApp

### 3. **Panel de Usuario Simplificado**
**Ubicación:** `/user-panel`
- ▶️ Pausar el bot
- ⏸️ Reanudar el bot
- 🚪 Cerrar sesión

### 4. **Base de Datos Relacional**
**Tecnología:** SQLAlchemy + SQLite (con opción PostgreSQL)
- `users` - Gestión de usuarios
- `bot_config` - Configuración global
- `holidays` - Feriados
- `holiday_menus` - Menús fuera de horarios
- `whatsapp_blocklist` - Números bloqueados
- `country_filters` - Filtros geográficos

### 5. **Sistema de Horarios Inteligente**
- ⏰ Configurar horas de apertura/cierre
- 📅 Detectar automáticamente feriados
- 🌙 Menú especial fuera de horarios
- 📊 Diferente respuesta fin de semana

### 6. **Nombre Configurable de la Solución**
- ✅ Variable `SOLUTION_NAME` en .env
- ✅ Guardado en base de datos
- ✅ Actualizable por admin
- ✅ Aparece en toda la interfaz

### 7. **Sistema Antispam Base**
- 🚫 Lista negra de números
- 🔍 Validación antes de responder
- 📝 Razón de bloqueo

### 8. **Menú Dinámico por Horarios**
- 🎯 Menú inteligente fuera de horarios
- 📝 Editable y personalizable
- 🔄 Cambio automático según horario
- 📆 Soporte para feriados

### 9. **API REST Completa**
- 📡 Endpoints para autenticación
- 👤 Endpoints de gestión de usuarios
- ⚙️ Endpoints de configuración
- 📅 Endpoints de feriados
- 📞 Endpoints de control del bot

### 10. **Interfaz Moderna**
- 🎨 HTML5 + CSS3 + JavaScript vanilla
- 📱 Responsive design
- 🌈 Gradientes y animaciones
- ⚡ Carga rápida

---

## 📁 Archivos Nuevos Creados

```
/opt/clinic-whatsapp-bot/
├── services/clinic-bot-api/
│   ├── app.py                 # ✨ NUEVO - Refactorizado con todos los cambios
│   ├── database.py            # ✨ NUEVO - Configuración SQLAlchemy
│   ├── models.py              # ✨ NUEVO - Modelos de BD
│   ├── schemas.py             # ✨ NUEVO - Esquemas Pydantic
│   ├── security.py            # ✨ NUEVO - Funciones de seguridad
│   ├── pages.py               # ✨ NUEVO - Generador de páginas HTML
│   ├── app_old.py             # Respaldo del app.py original
│   ├── requirements.txt        # ✨ ACTUALIZADO - Nuevas dependencias
│   └── clinic_bot.db          # ✨ CREADA AUTOMÁTICAMENTE - Base de datos
├── DOCUMENTACION.md           # ✨ NUEVO - Documentación completa
├── CAMBIOS_IMPLEMENTADOS.md   # ✨ NUEVO - Este archivo
└── .env.example               # ✨ ACTUALIZADO - Con todas las variables
```

---

## 🔐 Credenciales por Defecto

**Usuario Admin:**
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANTE:** Cambiar la contraseña después del primer login

---

## 🚀 Iniciar el Sistema

### Opción 1: Con Docker Compose (Recomendado)

```bash
cd /opt/clinic-whatsapp-bot

# Asegurar que .env existe con configuración correcta
cp .env.example .env
# Editar .env con tus valores

# Iniciar servicios
docker-compose up -d

# Verificar logs
docker-compose logs -f wa-bot
```

**URLs Disponibles:**
- 🏠 **Principal:** http://localhost:8088/
- 🔐 **Login:** http://localhost:8088/login
- 📊 **Dashboard:** http://localhost:8088/dashboard
- 👤 **User Panel:** http://localhost:8088/user-panel

### Opción 2: Manual (Desarrollo)

```bash
cd /opt/clinic-whatsapp-bot/services/clinic-bot-api

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp ../../.env.example .env

# Ejecutar aplicación
python app.py
```

---

## 📊 Flujo de Uso Principal

### Para Usuarios Regulares:

```
1. Ir a http://localhost:8088/login
2. Introducir credenciales (usuario regular)
3. Acceder a /user-panel
4. Pueden pausar/reanudar el bot
```

### Para Administradores:

```
1. Ir a http://localhost:8088/login
2. Introducir credenciales de admin
3. Acceder a /dashboard
4. Gestionar todo el sistema
```

### Para Desarrolladores:

```
# Acceder a API REST
curl -X POST http://localhost:8088/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Obtendrás:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {...}
}

# Usar token en próximas peticiones:
curl -X GET http://localhost:8088/api/admin/users \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 🔧 Configuración Rápida

### Cambiar Nombre de la Solución

1. Login como admin
2. Dashboard → Configuración
3. Cambiar "Nombre de la Solución"
4. Guardar cambios

O via API:
```bash
curl -X PUT http://localhost:8088/api/config \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"solution_name":"Mi Clínica"}'
```

### Agregar Horarios

Dashboard → Configuración:
- Hora de Apertura: 08:00
- Hora de Cierre: 17:00
- Habilitar menú fuera de horarios: ✓

### Crear Feriado

Dashboard → Feriados → Nuevo Feriado:
- Fecha: 2024-12-25
- Nombre: Navidad
- Descripción: (opcional)

---

## 📚 Características por Hacer (Próximas Versiones)

- [ ] Sistema de filtros por país/provincia (antispam avanzado)
- [ ] Dashboard con estadísticas de mensajes
- [ ] Integración con CRM
- [ ] Webhooks personalizados
- [ ] Rate limiting por usuario
- [ ] Encriptación de datos sensibles
- [ ] Backup automático de BD
- [ ] Notificaciones por email/Telegram
- [ ] Multi-idioma
- [ ] Búsqueda y filtrado de usuarios

---

## ⚙️ Arquitectura Técnica

```
┌─────────────────┐
│   Cliente Web   │
│  (Login/Admin)  │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐       ┌──────────────┐
│    FastAPI      │◄─────►│  SQLAlchemy  │
│    (app.py)     │       │  SQLite/PG   │
└────────┬────────┘       └──────────────┘
         │ 
    ┌────┼────┐
    ▼    ▼    ▼
┌──────────────────────┐
│  - Auth (JWT)        │
│  - Users (CRUD)      │
│  - Config            │
│  - Holidays          │
│  - WhatsApp Webhook  │
└──────────────────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌──────────────────────┐
│  - WAHA API          │
│  - Ollama AI         │
│  - Email (Gmail)     │
│  - N8N Webhooks      │
└──────────────────────┘
```

---

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT tokens con expiración
- ✅ CORS configurado
- ✅ Validación con Pydantic
- ⚠️ TODO: HTTPS en producción
- ⚠️ TODO: Rate limiting
- ⚠️ TODO: Logs de auditoría

---

## 📞 Soporte

Para reportar problemas o solicitar features:

1. Revisar DOCUMENTACION.md
2. Verificar logs: `docker-compose logs clinic-bot-api`
3. Contactar al equipo de desarrollo

---

## 📝 Historial de Cambios

**v0.3.0 (Marzo 2026):**
- ✅ Sistema completo de usuarios y autenticación
- ✅ Panel de administrador avanzado
- ✅ Base de datos relacional (SQLAlchemy)
- ✅ Nombre configurable de solución
- ✅ Sistema de horarios e inteligente
- ✅ Menú dinámico fuera de horarios
- ✅ Lista negra de números
- ✅ API REST completa con JWT

**v0.2.0 (Anterior):**
- Sistema básico del bot
- Admin con contraseña simpl
- Editor de menú

---

*Actualizado: Marzo 2026*
*Sistema: Clínica WhatsApp Bot v0.3.0*
