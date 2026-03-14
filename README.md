# 🤖 WA-BOT - Sistema Integral de WhatsApp

```
  ╔════════════════════════════════════════════════════════════════╗
  ║           🤖 WA-BOT - V1.0.3                                  ║
  ║    Sistema Integral de Chat + Administración con Seguridad    ║
  ╚════════════════════════════════════════════════════════════════╝
```

## 🎯 ¿Qué es?

Sistema completo y profesional para gestionar un bot de WhatsApp en una clínica, consultorio, farmacia o negocio de salud. Incluye:

✅ Chatbot inteligente con menú dinámico  
✅ **Opción rápida: "99 - Chatear con Operador" para transferencia inmediata**  
✅ Gestión completa de usuarios y administradores  
✅ Control de horarios y feriados  
✅ Sistema antispam  
✅ Panel web moderno y fácil de usar  
✅ API REST completa  
✅ Base de datos relacional segura  
✅ Autenticación con JWT  

---

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar/entrar al proyecto
cd /opt/wa-bot

# Configurar variables de entorno
cp .env.example .env
nano .env  # Completar con tus datos

# Iniciar
docker-compose up -d

# Acceder
🌐 http://localhost:8088/
```

### Opción 2: Desarrollo Local

```bash
cd services/clinic-bot-api
pip install -r requirements.txt
cp ../../.env.example .env
python app.py
```

**Admin por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 📚 Documentación

| Documento | Contenido |
|-----------|----------|
| [GUIA_RAPIDA.md](GUIA_RAPIDA.md) | ⚡ Inicio en 10 minutos |
| [DOCUMENTACION.md](DOCUMENTACION.md) | 📖 Documentación completa |
| [CAMBIOS_IMPLEMENTADOS.md](CAMBIOS_IMPLEMENTADOS.md) | ✨ Detalle técnico con los nuevos cambios |

---

## 🆕 Novedades Marzo 2026

- Se corrigió la resolución de rutas para `MenuP.MD` y `MenuF.MD` en Docker y en ejecución local.
- Se agregaron endpoints explícitos de lectura:
  - `GET /api/config/menu`
  - `GET /api/config/offhours`
- La actualización de menú ahora acepta ambos métodos:
  - `POST /api/config/menu`
  - `PUT /api/config/menu`
- Compatibilidad de payload para menú:
  - `{"content": "..."}`
  - `{"menu": "..."}`

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                     USUARIOS / ADMIN                         │
│              http://localhost:8088                           │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP/REST/WebSocket
         ┌───────────┴──────────────┐
         ▼                          ▼
    ┌─────────┐              ┌──────────────┐
    │  LOGIN  │              │   DASHBOARD  │
    │ /login  │              │ /dashboard   │
    └────┬────┘              └──────┬───────┘
         │                          │
         └──────────────┬───────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │   FASTAPI (app.py)       │
         │  - Autenticación (JWT)   │
         │  - API REST              │
         │  - Webhooks              │
         └──────────────┬───────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
     ┌────────┐   ┌──────────┐   ┌──────────┐
     │ SQLite │   │  WAHA    │   │  Ollama  │
     │ (BD)   │   │(WhatsApp)│   │   (IA)   │
     └────────┘   └──────────┘   └──────────┘
```

---

## ✨ Características Principales

### 🔐 Seguridad
- Autenticación con JWT tokens
- Contraseñas hasheadas con bcrypt
- Validación con Pydantic
- CORS configurado
- Sesiones de usuario

### 👥 Usuarios & Admin
- **Admin:** Control total del sistema
- **Usuario:** Pausar/reanudar bot, cambiar contraseña

### ⚙️ Configuración
- Nombre flexible de solución
- Horarios de atención configurable
- Menúe especial fuera de horarios
- Feriados automáticos
- Antispam por número

### 📊 Dashboard
- Estado en tiempo real del bot
- Gestión de usuarios
- Editor de menú
- Calendario de feriados
- Lista negra de números

### 🤖 Chatbot
- Respuestas inteligentes con Ollama
- Menú jerárquico personalizable
- Detección automática de horarios
- Control de inactividad
- Integración con WhatsApp

---

## 📋 Stack Tecnológico

```
Backend:
  🐍 Python 3.11
  ⚡ FastAPI
  🗄️ SQLAlchemy + SQLite/PostgreSQL
  🔐 JWT + bcrypt

Frontend:
  🌐 HTML5
  🎨 CSS3
  💻 JavaScript Vanilla
  📱 Responsive Design

Integraciones:
  📱 WAHA (WhatsApp Web)
  🧠 Ollama (LLM)
  📧 Gmail API
  🔄 N8N Webhooks

DevOps:
  🐳 Docker
  🐳 Docker Compose
  🔧 Linux
```

---

## 🎯 Casos de Uso

✅ **Clínicas y Consultórios**
- Toma de turnos automática
- Información de especialidades
- Horarios y disponibilidad

✅ **Farmacias**
- Información de medicamentos
- Precios y disponibilidad
- Horarios de atención

✅ **Centros Médicos**
- Derivación a profesionales
- Información de estudios
- Contacto de urgencias

✅ **Negocios de Salud General**
- Atención al cliente
- FAQs automatizadas
- Toma de datos

---

## 📊 URLs Principales

| Función | URL | Acceso |
|---------|-----|--------|
| 🏠 Principal | `/` | Público |
| 🔐 Login | `/login` | Público |
| 📊 Dashboard | `/dashboard` | Admin |
| 👤 Panel Usuario | `/user-panel` | Usuario |
| 🌐 API REST | `/api/*` | Autenticado |
| 🚨 Health | `/health` | Público |

---

## 🔧 Configuración Básica

```env
# .env
SOLUTION_NAME=Mi Clínica
WAHA_API_KEY=tu-api-key
DATABASE_URL=sqlite:///./clinic_bot.db
SECRET_KEY=tu-clave-secreta
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=lfm2:latest
```

---

## 📦 Archivos Nuevos

```
✨ database.py       - Configuración BD
✨ models.py         - Modelos SQLAlchemy
✨ schemas.py        - Validación Pydantic
✨ security.py       - JWT + Hashing
✨ pages.py          - Generador HTML
✨ app.py            - Nueva versión refactorizada
✨ DOCUMENTACION.md  - Documentación completa
✨ GUIA_RAPIDA.md    - Quick start
```

---

## 🚀 Flujo de Uso

### Administrador
```
LOGIN → DASHBOARD → (Usuarios | Config | Menú | Feriados | etc)
```

### Usuario Regular
```
LOGIN → USER PANEL → (Pausar | Reanudar | Logout)
```

### Cliente WhatsApp
```
Enviar Mensaje → Webhook → Verificación → Respuesta IA
```

---

## ⚡ API REST - Ejemplos

### Login
```bash
curl -X POST http://localhost:8088/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Crear Usuario
```bash
curl -X POST http://localhost:8088/api/admin/users \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "username":"nuevo",
    "password":"123456",
    "email":"user@example.com"
  }'
```

### Agregar Feriado
```bash
curl -X POST http://localhost:8088/api/holidays \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "date":"2024-12-25",
    "name":"Navidad"
  }'
```

---

## 🔒 Seguridad Pre-Producción

- [ ] Cambiar admin password
- [ ] Cambiar SECRET_KEY
- [ ] Usar HTTPS (nginx + certbot)
- [ ] Configurar PostgreSQL
- [ ] Habilitar backups
- [ ] Ajustar firewall
- [ ] Configurar alertas email
- [ ] Rate limiting
- [ ] Logs centralizados

---

## ❓ Troubleshooting

```bash
# Ver logs
docker-compose logs -f wa-bot

# Reiniciar
docker-compose restart

# Limpiar y reiniciar
docker-compose down && docker-compose up -d

# Acceder a shell
docker exec -it wa-bot bash
```

---

## 📞 Soporte

Documentación completa disponible en:
- 📖 [DOCUMENTACION.md](DOCUMENTACION.md)
- ⚡ [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
- ✨ [CAMBIOS_IMPLEMENTADOS.md](CAMBIOS_IMPLEMENTADOS.md)

---

## 📝 Licencia & Autoría

Sistema desarrollado para clínicas y negocios de salud.
Contactar a equipo de desarrollo para soporte profesional.

---

## 🎉 ¡Bienvenido!

Gracias por usar **WA-BOT**. Este sistema te permite:

✅ Automatizar atención al cliente  
✅ Gestionar horarios y feriados  
✅ Administrar usuarios seguramente  
✅ Mantener control total de tu chatbot  

**¡Adelante! Comienza con la [GUIA_RAPIDA.md](GUIA_RAPIDA.md)** 🚀

---

```
╔════════════════════════════════════════════════════════════════╗
║                    🤖 WA-BOT - V0.3.0                         ║
║                      Marzo 2026                                ║
╚════════════════════════════════════════════════════════════════╝
```                      ║
║                    ¡Gestforma fácil y segura!                 ║
╚════════════════════════════════════════════════════════════════╝
```
