# ⚡ Guía Rápida de Inicio

## 1️⃣ Primeros Pasos (5 minutos)

### Paso 1: Configuración Inicial

```bash
cd /opt/clinic-whatsapp-bot

# Copiar configuración de ejemplo
cp .env.example .env

# Editar .env con tus valores
nano .env
```

### Paso 2: Iniciar Sistema

```bash
# Iniciar con Docker Compose
docker-compose up -d

# Esperar a que esté listo (10-20 segundos)
docker-compose logs -f clinic-bot-api
```

### Paso 3: Acceder al Sistema

```
🌐 http://localhost:8088/
🔐 Login: http://localhost:8088/login

Admin por defecto:
  Usuario: admin
  Contraseña: admin123
```

---

## 2️⃣ Cambiar Contraseña de Admin (Recomendado)

Una vez logueado como admin:

```
Dashboard → Configuración → "Cambiar Contraseña"
```

O por API:

```bash
curl -X POST http://localhost:8088/api/auth/change-password \
  -H "Authorization: Bearer {YOUR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin123",
    "new_password": "tu_nueva_contraseña"
  }'
```

---

## 3️⃣ Configurar Nombre de Solución

### Vía Web:
**Dashboard → Configuración → "Nombre de la Solución"**

Ejemplo opciones:
- "Clínica San José"
- "Centro Médico Integral"
- "Farmacia Don Pedro"
- "Consultorio Dental"

### Vía API:
```bash
curl -X PUT http://localhost:8088/api/config \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "solution_name": "Clínica San José",
    "menu_title": "Bienvenido a Clínica San José"
  }'
```

---

## 4️⃣ Crear Usuarios Adicionales

### Vía Web Dashboard:

1. **Dashboard → Usuarios**
2. **Botón "➕ Nuevo Usuario"**
3. Ingresar:
   - Usuario: `usuario1`
   - Email: `usuario1@example.com`
   - Contraseña: `contraseña_segura`
   - Nombre: `Juan Pérez`
   - ✓ Es Administrador (si quieres que sea admin)
4. **Crear Usuario**

### Vía API:
```bash
curl -X POST http://localhost:8088/api/admin/users \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario1",
    "email": "usuario1@example.com",
    "password": "contraseña_segura",
    "full_name": "Juan Pérez",
    "is_admin": false
  }'
```

---

## 5️⃣ Configurar Horarios

### Via Web:

**Dashboard → Configuración**
- Hora de Apertura: `08:00`
- Hora de Cierre: `17:00`
- ✓ Habilitar menú fuera de horarios
- Mensaje: Crear menú especial primero

### Flujo Completo:

1. **Dashboard → Fuera de Horario → Nuevo Menú**
2. Nombre: `Menú Nocturno`
3. Contenido:
   ```markdown
   🌙 Centro Médico - Horario Nocturno

   Disculpa, nuestro horario es:
   🕘 Lunes a Viernes: 08:00 - 17:00
   🕘 Sábado: 09:00 - 13:00
   
   Línea de emergencias: 911
   
   Vuelve mañana durante horario de atención.
   ```
4. **Crear Menú**
5. **Configuración → Habilitar "menú fuera de horarios"**

---

## 6️⃣ Agregar Feriados

### Via Web Dashboard:

1. **Dashboard → Feriados**
2. **Botón "➕ Nuevo Feriado"**
3. Ingresar:
   - Fecha: `2024-12-25`
   - Nombre: `Navidad`
   - Descripción: `Día de Navidad`
4. **Crear Feriado**

### Ejemplo de Feriados por País:

**Argentina:**
```
2024-01-01: Año Nuevo
2024-02-12: Carnaval (lunes)
2024-02-13: Carnaval (martes)
2024-03-24: Día de la Memoria
2024-04-02: Malvinas
2024-04-25: Día del Veterano
2024-05-01: Día del Trabajador
2024-06-17: Guemes
2024-06-20: Día de la Bandera
2024-07-09: Independencia
2024-08-17: Muerte del Libertador
2024-10-12: Respeto a la Diversidad
2024-11-18: Día Nacional de la Soberanía
2024-12-08: Inmaculada Concepción
2024-12-25: Navidad
```

---

## 7️⃣ Bloquear Números de WhatsApp

### Via Web:

1. **Dashboard → Lista Negra**
2. **Botón "➕ Bloquear Número"**
3. Número: `+5493421234567`
4. Razón: `Spam` / `Abuso` / `Solicitud Usuario`

### Vía API:
```bash
curl -X POST http://localhost:8088/api/blocklist \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+5493421234567",
    "reason": "Spam"
  }'
```

---

## 8️⃣ Pausar/Reanudar Bot

### Solo Admin:

**Dashboard → Estado**
- **⏸️ Pausar Bot** - Detiene respuestas a todos
- **▶️ Reanudar Bot** - Vuelve a responder

### Usuario Regular:

**User Panel** (`http://localhost:8088/user-panel`)
- **⏸️ Pausar** - Pausa solo su acceso
- **▶️ Reanudar** - Reanuda su acceso

---

## 9️⃣ Editar Menú Principal

### Via Web:

1. **Dashboard → Menú**
2. Editar Markdown del menú
3. Ver formato:
   ```markdown
   # 🏥 Clínica San José
   Bienvenido/a 👋
   
   Elegí una opción:
   1️⃣ Turnos
   2️⃣ Consultas
   3️⃣ Farmacia
   0️⃣ Volver
   ```
4. **Guardar Menú**

### Guía Markdown:
- `# Título`
- `##Sus Subtítulo`
- `**Negrita**`
- `- Bullet point`
- `1. Número`
- `[Link](url)`
- `✅❌🟢`

---

## 🔟 Resetear Contraseña de Usuario

### Como Admin:

1. **Dashboard → Usuarios**
2. Encontrar usuario
3. Botón **"Resetear Contraseña"**
4. Ingresar nueva contraseña
5. Compartir contraseña temporal con usuario

### Vía API:
```bash
curl -X POST http://localhost:8088/admin/users/2/reset-password \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "nueva_temporal_123"
  }'
```

---

## ❓ Problemas Comunes

### "No puedo conectarme a WhatsApp"

```bash
# Verificar que WAHA está corriendo
docker ps | grep waha

# Reiniciar WAHA
docker-compose restart waha

# Verificar logs
docker-compose logs waha
```

### "Base de datos locked"

```bash
# Solución 1: Reiniciar
docker-compose restart clinic-bot-api

# Solución 2: Cambiar a PostgreSQL (mejor opción)
# Editar .env:
# DATABASE_URL=postgresql://user:pass@localhost/clinic
```

### "Olvide contraseña de admin"

```bash
# Solución: Resetear por archivo de config
# 1. Entrar a container
docker exec -it clinic-bot-api bash

# 2. Editar con python:
python
>>> from security import hash_password
>>> new_hash = hash_password("nueva_contraseña")
>>> print(new_hash)

# 3. Ver DOCUMENTACION.md para más detalles
```

---

## 📊 Comandos Útiles

```bash
# Ver estado de todos los servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Detener todo
docker-compose down

# Eliminar volúmenes (⚠️ Borra BD)
docker-compose down -v

# Reconstruir después de cambios
docker-compose up -d --build

# Acceder a shell del container
docker exec -it clinic-bot-api bash

# Ejecutar comando en container
docker exec clinic-bot-api python -c "print('hello')"
```

---

## 🔐 Checklist de Seguridad

Antes de ir a producción:

- [ ] Cambiar contraseña de admin
- [ ] Cambiar SECRET_KEY en .env
- [ ] Usar HTTPS (nginx + Let's Encrypt)
- [ ] Cambiar DATABASE_URL a PostgreSQL
- [ ] Configurar backups automáticos
- [ ] Activar email de alertas
- [ ] Revisar firewall
- [ ] Cambiar puertos por defecto
- [ ] Implementar rate limiting
- [ ] Configurar logs centralizados

---

## 📞 URLs Importantes

| Función | URL |
|---------|-----|
| Panel Principal | http://localhost:8088 |
| Login | http://localhost:8088/login |
| Dashboard Admin | http://localhost:8088/dashboard |
| Panel Usuario | http://localhost:8088/user-panel |
| API Health | http://localhost:8088/health |
| Estado Bot | http://localhost:8088/status |
| QR WhatsApp | http://localhost:8088/qr |

---

## 🎓 Documentación Completa

Para más información:
- Ver `DOCUMENTACION.md` - Guía completa
- Ver `CAMBIOS_IMPLEMENTADOS.md` - Detalle técnico
- Ver código en `app.py`, `models.py`, `security.py`

---

**¡Listo! Tu sistema está en marcha 🚀**

Para soporte: Contacta al equipo de desarrollo
