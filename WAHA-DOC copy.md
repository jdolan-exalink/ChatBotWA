Documento Técnico
Sistema de Chatbot con Handoff a Operador (WAHA)
1. Objetivo

Desarrollar un sistema de chatbot para WhatsApp que:

Presente un menú automático

Permita derivar a un operador humano

Suspenda completamente el bot durante 12 horas

Durante ese período:

No responder mensajes

No marcar mensajes como leídos

No ejecutar lógica automática

Luego de 12 horas el sistema vuelve automáticamente al modo bot.

2. Arquitectura del sistema
WhatsApp
   │
WAHA (WhatsApp HTTP API)
   │
Webhook Events
   │
Backend Chatbot Engine
   │
State Manager
   ├─ BOT MODE
   └─ HUMAN MODE (12h)
   │
Database
Componentes
Componente	Función
WAHA	Gateway WhatsApp
Backend	Lógica del chatbot
Database	Guardar estado del chat
Webhook	Recepción de mensajes

WAHA expone una API REST para enviar mensajes y usa webhooks o websockets para notificar eventos de mensajes entrantes.

3. Flujo general del sistema
Flujo normal
Usuario escribe
      ↓
WAHA recibe mensaje
      ↓
Webhook → Backend
      ↓
Motor del Bot
      ↓
Respuesta automática
Flujo con operador
Usuario escribe 99
      ↓
Backend guarda estado HUMAN
      ↓
Bot envía mensaje de transferencia
      ↓
Bot queda suspendido 12h
      ↓
Operador atiende manualmente
4. Menú inicial del chatbot

Ejemplo de menú:

🏥 Bienvenido a la Clínica

1️⃣ Turnos
2️⃣ Farmacia
3️⃣ Afiliaciones
4️⃣ Discapacidad
5️⃣ Bocas de expendio

👨‍💼 99 Hablar con un operador
5. Handoff a operador

Cuando el usuario envía:

99

El sistema debe:

Registrar el chat como HUMAN MODE

Guardar timestamp de expiración (12h)

Enviar mensaje informativo

Suspender la automatización

Mensaje sugerido:

👨‍💼 Perfecto.

Un operador humano continuará la conversación.
Por favor aguardá unos minutos.

El sistema automático quedará pausado.
6. Gestión de estados

Se debe mantener un state manager para cada número.

Tabla sugerida
chat_state
campo	tipo
id	uuid
chat_id	varchar
mode	enum(bot,human)
expire_at	timestamp
updated_at	timestamp
7. Lógica del webhook

Cada mensaje recibido desde WAHA genera un evento webhook.

Ejemplo de evento recibido:

POST /webhook/message

Payload ejemplo:

{
  "from": "5493424123456@c.us",
  "body": "Hola",
  "chatId": "5493424123456@c.us"
}

WAHA envía eventos de mensajes a una URL configurada para que el backend procese el contenido.

8. Lógica del motor del bot

Pseudo-código:

const HUMAN_TIMEOUT = 12 * 60 * 60 * 1000;

function handleMessage(msg){

   const chat = msg.from;
   const text = msg.body;

   const state = db.getChatState(chat);

   // modo operador activo
   if(state.mode === "human" && state.expire_at > now()){
        return; // ignorar mensaje
   }

   // expiró operador
   if(state.mode === "human" && state.expire_at <= now()){
        db.setMode(chat,"bot");
   }

   if(text === "99"){
        db.setMode(chat,"human");
        db.setExpire(chat, now()+HUMAN_TIMEOUT);

        sendMessage(chat,"Un operador continuará la conversación.");
        return;
   }

   processMenu(chat,text);
}
9. Control de lectura de mensajes

WAHA marca mensajes como leídos cuando el backend envía el endpoint de lectura (sendSeen).

Por lo tanto:

En modo operador

NO ejecutar:

POST /api/sendSeen

Resultado:

el mensaje queda recibido

no se envía confirmación de lectura.

10. API utilizadas de WAHA
Enviar mensaje
POST /api/sendText

Ejemplo:

{
 "session": "default",
 "chatId": "5493424123456@c.us",
 "text": "Hola"
}

WAHA permite enviar mensajes mediante esta API REST.

Marcar como leído (opcional)
POST /api/sendSeen

Solo usar si el bot responde.

11. Expiración del modo operador

Se implementará con:

Método 1 (recomendado)

Verificación en cada mensaje:

if expire < now → volver BOT_MODE
Método 2

Cron job cada 5 minutos:

UPDATE chats
SET mode='bot'
WHERE expire_at < now()
12. Seguridad
API key WAHA

Se debe proteger la API con:

WAHA_API_KEY

Esto obliga a que cada request tenga autenticación.

13. Logs

Registrar:

timestamp
chat_id
message
state
action

Ejemplo:

[10:30] chat:5493424123456 state:BOT → HUMAN
14. Mejoras futuras

Opcionales:

Panel de operadores

lista de chats activos

botón volver al bot

Comando operador
98 volver al bot
Timeout configurable
operator_timeout = 12h
15. Escalabilidad

El sistema debe soportar:

múltiples sesiones WAHA

múltiples operadores

múltiples bots

Arquitectura recomendada:

WAHA
   │
Load Balancer
   │
Chatbot Backend
   │
Redis (states)
   │
PostgreSQL (history)
16. Requisitos técnicos

Backend sugerido:

Node.js

Python FastAPI

Go

Base de datos:

PostgreSQL

Redis (cache)

Infraestructura:

Docker

Reverse proxy (Traefik / Nginx)

17. Entregables esperados

El desarrollador debe entregar:

Webhook server

Motor de bot

Sistema de estados

Integración WAHA

Documentación API

Docker deployment