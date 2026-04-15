# 🤖 WA-BOT - Sistema Integral de WhatsApp

```text
╔════════════════════════════════════════════════════════════════╗
║               🤖 WA-BOT - Documentación de Uso (2026)           ║
╚════════════════════════════════════════════════════════════════╝
```

## 🎯 Resumen

WA-BOT es una solución completa para gestionar interacción por WhatsApp con soporte a handoff (transferencia a operador), panel web administrativo y API REST. Está diseñada para clínicas, farmacias y negocios de salud que necesiten automatizar atención y mantener control humano cuando sea necesario.

---

## 🚀 Inicio Rápido

### Docker (recomendado)

```bash
# Dentro del repo
cp .env.example .env
# Edita .env con tus credenciales
docker compose up -d --build
# Panel: http://localhost:8088/
```

### Desarrollo local (rápido)

```bash
cd services/clinic-bot-api
pip install -r requirements.txt
cp ../../.env.example .env
python app.py
```

Admin por defecto (cámbialo en producción): usuario `admin` / contraseña `admin123`

---

## 📌 Uso en el Panel (Interfaz web)

**Para Administradores**
- Acceder a `http://<host>:8088/` → `Dashboard`.
- Funcionalidades principales:
  - Gestión de usuarios (crear, editar, borrar).
  - Configuración de menús y contenidos (editor de `MenuP.MD` / `MenuF.MD`).
  - Configurar horarios de atención y feriados.
  - Activar/desactivar handoff (transferencia a operador).
  - Visualizar tickets y chats en curso.

**Para Operadores**
- Ver lista de tickets asignados y su historial.
- Tomar/soltar atención de un cliente (asignar ticket).
- Responder mensajes desde el panel cuando se habilita la interfaz de operador.

**Para Usuarios (panel de cliente)**
- Consultar estado de solicitudes y datos personales.
- Pausar/reanudar notificaciones o interacción con el bot (según configuración).

---

## 💬 Uso por Chat (WhatsApp)

El bot responde mensajes y ofrece un menú interactivo. Además soporta handoff para pasar a un operador humano.

### Comandos y atajos (clientes)

Estos comandos están disponibles por defecto o pueden activarse/configurarse desde el panel:

- `99` — Solicitar transferencia a un operador humano (handoff). El bot confirmará y generará un ticket.
- `menu` — Mostrar el menú principal y opciones disponibles.
- `ayuda` / `help` — Ver instrucciones básicas y formas de contacto.
- `estado` — Consultar el estado de tu solicitud o turno.
- `cancelar` — Cancelar una solicitud/handoff pendiente (si aplica).

Ejemplo sencillo (cliente):
```
Cliente: 99
Bot: "Listo, recibimos tu solicitud. Un operador te contacta a la brevedad."
```

### Comandos y acciones (operadores / administradores)

Las acciones de operador suelen gestionarse desde el panel, pero hay metadatos y mensajes que el sistema utiliza en chat:

- Tomar ticket (desde el panel): marcar como "en atención" y comenzar la conversación.
- `cerrar` (desde la interfaz) — Marcar ticket como cerrado cuando finaliza la atención.
- Responder directamente al cliente (desde panel u interfaz de operador).

Nota: los comandos exactos expuestos vía chat para operadores dependen de la integración y del front-end de operadores; la lógica de tickets y estados (`ticket_status`, `assigned_agent_id`) está presente en la base de datos y en la API.

---

## 🧭 Ciclo de atención (ticket + handoff)

1. Cliente envía `99` o solicita un operador.
2. El bot crea un ticket y responde con un mensaje de confirmación.
3. Si hay operadores disponibles, el ticket se asigna; si no, queda en cola con mensaje de espera.
4. Operador atiende, responde y cierra el ticket cuando termina.

Parámetros configurables:
- `handoff_enabled` (boolean)
- `handoff_inactivity_minutes` (tiempo para cerrar por inactividad)
- Textos personalizados: `handoff_message`, `waiting_agent_message`, `in_agent_message` (ver `database.py` defaults).

---

## ⚙️ Configuración & Variables importantes

Comprueba y edita el archivo `.env` con las claves y endpoints necesarios:

```env
SOLUTION_NAME=Mi Clínica
WAHA_API_KEY=tu-api-key
DATABASE_URL=sqlite:///./chatbot.sql
SECRET_KEY=tu-clave-secreta
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=lfm2:latest
```

---

## 🔎 Endpoints útiles (ejemplos)

- `POST /api/auth/login` — Autenticación (devuelve JWT).
- `GET /api/config/menu` — Obtener menú actual.
- `POST /api/config/menu` — Actualizar menú (admin).
- `POST /api/holidays` — Agregar feriado (admin).

Ver ejemplos en secciones de la API dentro del repositorio.

---

## ✅ Buenas prácticas antes de producción

- Cambiar credenciales por defecto.
- Usar HTTPS y reverse-proxy (nginx).
- Migrar a PostgreSQL para carga concurrente.
- Habilitar backups automáticos y logging centralizado.

---

## 📚 Recursos y documentación adicional

- Guía rápida: [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
- Documentación técnica: [DOCUMENTACION.md](DOCUMENTACION.md)
- Cambios y novedades: [CAMBIOS_IMPLEMENTADOS.md](CAMBIOS_IMPLEMENTADOS.md)

---

## 🙋‍♂️ Soporte y contacto

Para soporte o personalizaciones, contacta al equipo de desarrollo responsable del despliegue.

---

Gracias por usar WA-BOT — si querés, puedo agregar ejemplos concretos de mensajes o capturas del panel para mejorar la sección visual.

