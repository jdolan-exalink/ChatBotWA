# Changelog - WA-BOT

Todos los cambios notables de este proyecto serán documentados en este archivo.

---

## [2.1.0] - 2026-03-06

### ✨ Nuevas Funcionalidades
- **Modo Operador (Human Mode) completamente reescrito**
  - ✅ Tecla `99` activa modo operador correctamente
  - ✅ Tecla `98` desactiva modo operador y regresa al menú
  - ✅ Lógica de horario con `calendar.timegm()` para timezone-safe comparison
  - ✅ Silenciamiento correcto de mensajes en modo humano
- **Nueva página `/user-config` (Configuración de Usuario)**
  - ✅ Calendario de feriados interactivo (click-to-toggle)
  - ✅ Gestión de lista de bloqueados
  - ✅ Cambio de contraseña movido a esta página
- **Calendario de Feriados — rediseño completo**
  - ✅ Click en día = marcar/desmarcar como feriado
  - ✅ Estados visuales: azul (guardado), amarillo (pendiente add), rojo tachado (pendiente delete)
  - ✅ Sábados/domingos en rosa, día de hoy con contorno
  - ✅ Badge dinámico de cambios pendientes
  - ✅ Guardado por diff: solo hace POST de nuevos + DELETE de eliminados
  - ✅ Botón Cancelar restaura la selección original desde el servidor
- **Mejoras de UX en panel de usuario y admin**
  - ✅ Modal QR con apertura instantánea + spinner de carga
  - ✅ Polling cada 1.5s (hasta 45s) sin bloquear la UI
  - ✅ Botón Pausar Bot en panel admin y usuario con feedback visual

### 🔧 Endpoints API
- `/api/holidays` GET/POST/DELETE: abierto a usuarios regulares (antes solo admin)
- `/api/blocklist` GET/POST/DELETE: abierto a usuarios regulares
- `/user-config` GET: nueva ruta para la página de configuración de usuario

### 🐛 Correcciones
- Modo operador: opción `99` y `98` funcionan correctamente en todos los flujos
- QR: eliminado delay hardcodeado de 8s
- Panel admin: botón Pausar Bot no existía, ahora agregado

### 📦 Infraestructura
- Dockerfile + docker-compose sin cambios de estructura
- `conversation_manager.py` y `state_cache.py` agregados al repo

---

## [1.0.4] - 2026-03-04 (Hotfix)

### 🐛 Correcciones de Bugs
- **Arreglado error de login "Unexpected token 'I', "Internal S"... is not valid JSON"**
  - ✅ Mejorado manejo de errores en endpoint `/api/auth/login`
  - ✅ Mejor logging en backend para debugging
  - ✅ Validación individual de credenciales
  - ✅ Mejorado manejo de respuestas JSON en frontend
  - ✅ Try-catch para parseo de JSON en JavaScript

### 🔧 Mejoras Internas
- **Inicialización de usuarios mejorada**
  - ✅ Agregado `db.flush()` para asegurar inserciones
  - ✅ `db.rollback()` en caso de errores
  - ✅ Logging detallado en cada paso
  - ✅ Mejor detección de problemas

### 📚 Documentación
- Agregado [LOGIN_FIX.md](LOGIN_FIX.md) con guía completa de solución
- Agregado script [test_login.py](services/clinic-bot-api/test_login.py) para diagnóstico

### 🧪 Testing
- Script de prueba para verificar usuarios en BD
- Detección automática de problemas de login
- Debugging mejorado en logs

---

## [1.0.3] - 2026-03-04

### ✨ Nuevas Características
- **Gestión completa de usuarios mejorada**
  - ✅ Crear nuevos usuarios con modal intuitivo
  - ✅ Editar contraseña de usuarios existentes
  - ✅ Eliminar usuarios con confirmación
  - ✅ Activar/Desactivar usuarios (bloquea login)
  - ✅ Pausar/Reanudar usuarios (sin enviar menú principal)

### 🐛 Correcciones de Bugs
- **Horarios "Fuera de hora" ahora funciona correctamente**
  - ✅ Verifica feriados automáticamente
  - ✅ Horarios diferenciados para lunes-viernes vs fin de semana
  - ✅ Menú fuera de horarios se envía incluso a usuarios nuevos
  - ✅ Respeta horarios de sábado configurados

### 🔧 Mejoras Internacionales
- **Filtro por País mejorado (🌍)**
  - ✅ Validación correcta de códigos de país (+54, +55, +56, etc.)
  - ✅ Si está ACTIVO: solo responde a números con esos códigos
  - ✅ Si está INACTIVO: responde a cualquier número
  - ✅ Logging detallado para debugging

### 📊 Cambios de API
- `UserUpdate` schema mejorado con campo `is_active`
- Endpoint `PUT /api/admin/users/{id}` ahora soporta cambios de estado
- Mejores mensajes de error en todos los endpoints

### 💾 Cambios en Base de Datos
- Modelo `User` con campos:
  - `is_active` - Permite/bloquea login
  - `is_paused` - Pausar usuario sin borrarlo
  - Índices mejorados para queries más rápidas

### 📖 Documentación
- Actualizado README.md a versión 1.0.3
- Agregado CHANGELOG.md con historial completo

### 🧪 Testing & Validación
- Todas las sintaxis validadas con `python3 -m py_compile`
- Endpoints testeados con casos de uso
- UI responsive en desktop y mobile

---

## [1.0.2] - 2026-03-03

### ✨ Nuevas Características
- Panel de administración mejorado
- Soporte para menús de fuera de horarios
- Sistema de bloqueados avanzado

### 🐛 Correcciones
- Arreglada autenticación de JWT
- Mejorada detección de desconexión de WhatsApp

---

## [1.0.1] - 2026-03-02

### ✨ Lanzamiento Inicial
- ✅ Bot de WhatsApp con IA integrada
- ✅ Gestión de usuarios y admin
- ✅ Control de horarios y feriados
- ✅ API REST completa
- ✅ Dashboard web responsivo
- ✅ Sistema antispam con blocklist
- ✅ Autenticación con JWT

---

## Versión Anterior

### [0.3.0]
- Versión beta inicial del sistema
- Funcionalidades básicas de bot y admin
