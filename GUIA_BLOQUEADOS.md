# 🚫 GUÍA DE BLOQUEADOS - Sistema ChatBot WhatsApp

## 📋 Descripción
La funcionalidad de **Bloqueados** permite agregar números de teléfono a una lista negra (blocklist) para que el bot no envíe el menú a esos números. Esto es útil para:

- **Spam/Harasser**: Bloquear números que envían spam
- **Facturación**: Evitar que se envíe el menú a números administrativos
- **Desarrollo/Testing**: Bloquear números de prueba en producción
- **Privado**: Bloquear números específicos por razones de privacidad

---

## ✅ Funcionalidad Corregida

### Problemas Solucionados:
1. ✅ **Validación de entrada**: El formulario ahora valida que haya datos
2. ✅ **Manejo de errores**: Muestra errores claros al usuario
3. ✅ **Botones de eliminar**: La tabla ahora tiene botones para desbloquear números
4. ✅ **Mensajes de feedback**: Muestra mensajes de éxito/error después de cada acción
5. ✅ **Confirmación de eliminación**: Pide confirmación antes de desbloquear

---

## 🎯 Cómo Usar

### 1. Acceder al Panel de Bloqueados
- Ve al dashboard de administrador
- Haz clic en el menú **"🚫 Bloqueados"** en la barra lateral

### 2. Agregar un Número Bloqueado

#### Información Necesaria:
- **Número de WhatsApp**: Debe comenzar con `+` (ej: `+543424438150`)
- **Razón**: Por qué se bloquea (ej: `Facturación`, `Spam`, etc.)

#### Pasos:
1. Completa el campo "Número de WhatsApp" con el formato correcto
2. Escribe la razón del bloqueo
3. Haz clic en el botón "🚫 Bloquear"
4. Verás un mensaje de confirmación

#### Ejemplo Proporcionado:
```
Número: +543424438150
Razón: Facturación
```

### 3. Ver Números Bloqueados

La sección "📋 Lista de Bloqueados" muestra:
- **Número**: El número de teléfono bloqueado
- **Razón**: Por qué fue bloqueado
- **Acción**: Botón para desbloquear (si es necesario)

### 4. Desbloquear un Número

1. Localiza el número en la tabla de "📋 Lista de Bloqueados"
2. Haz clic en el botón rojo "Desbloquear"
3. Confirma la acción en el cuadro de diálogo
4. Se mostrará un mensaje de confirmación

---

## 📊 Estados de Mensajes

El sistema muestra diferentes tipos de mensajes con colores distintos:

### ✅ Éxito (Verde)
```
✅ Número bloqueado exitosamente
✅ Número desbloqueado exitosamente
```

### ⚠️ Advertencia (Naranja)
```
⚠️ Ingresa un número de teléfono
⚠️ El número debe comenzar con +
⚠️ Ingresa una razón para el bloqueo
```

### ❌ Error (Rojo)
```
❌ Error: Número ya está bloqueado
❌ Error al agregar a blocklist: [detalles]
❌ Error al cargar lista de bloqueados
```

### ⏳ Procesando (Azul)
```
⏳ Agregando número a blocklist...
⏳ Desbloqueando número...
```

---

## 🔌 Integración con el Bot

Cuando un número está en la blocklist, el bot:

1. **Detecta el número** en los mensajes entrantes
2. **No responde** con el menú automático
3. **No inicia conversación**
4. **No registra estadísticas** del chat

### Validación en Tiempo Real
El sistema verifica la blocklist en:
- Cuando recibe un mensaje de WhatsApp
- Antes de enviar el menú automático
- Antes de registrar la conversación

---

## 🧪 Prueba Manual (Script Python)

Para probar desde línea de comandos:

```bash
cd /opt/clinic-whatsapp-bot
python3 test_blocklist.py
```

### Qué Hace la Prueba:
1. ✅ Obtiene token de autenticación
2. ✅ Lista números bloqueados actuales
3. ✅ Agrega `+543424438150` (Facturación) como prueba
4. ✅ Verifica que se agregó correctamente
5. ✅ Elimina el número de prueba
6. ✅ Verifica que se eliminó correctamente

---

## 🔍 Validaciones Implementadas

### Número de Teléfono:
- ✅ Requerido (no vacío)
- ✅ Debe comenzar con `+`
- ✅ Máximo 20 caracteres
- ✅ Único (no permite duplicados)

### Razón:
- ✅ Requerido (no vacío)
- ✅ Máximo 255 caracteres

### Autenticación:
- ✅ Solo administradores pueden agregar/eliminar bloqueados
- ✅ Requiere token válido
- ✅ Verifica permisos en cada operación

---

## 🎨 Interfaz Mejorada

La tabla de bloqueados ahora:
- ✅ Muestra 3 columnas: Número, Razón, Acción
- ✅ Botones rojo para desbloquear
- ✅ Confirmación antes de eliminar
- ✅ Mensaje cuando no hay números bloqueados
- ✅ Estilos consistentes con el resto del dashboard

---

## 📱 Ejemplo Práctico Completo

### Agregar a Facturación:
```
Campo: Número de WhatsApp
Valor: +543424438150

Campo: Razón
Valor: Facturación

Acción: Clic en "🚫 Bloquear"
Resultado: ✅ Número bloqueado exitosamente
```

### Resultado en Lista:
```
┌─────────────────────┬───────────────┬──────────────┐
│ Número              │ Razón         │ Acción       │
├─────────────────────┼───────────────┼──────────────┤
│ +543424438150       │ Facturación   │ Desbloquear  │
└─────────────────────┴───────────────┴──────────────┘
```

---

## ⚙️ Configuración en Backend

El modelo de base de datos:

```python
class WhatsAppBlockList(Base):
    __tablename__ = "whatsapp_blocklist"
    
    id                  # ID único
    phone_number        # Número de teléfono (único)
    reason              # Razón del bloqueo
    blocked_at          # Fecha/hora de bloqueo (automática)
```

---

## 🆘 Solución de Problemas

### Problema: No aparecer botones de desbloquear
**Solución**: Recarga la página (F5) o espera que cargue la lista

### Problema: "Número ya está bloqueado"
**Solución**: El número ya existe en la blocklist, intenta desbloquear y volveré a bloquear

### Problema: No puedes ver la sección de bloqueados
**Solución**: Verifica que seas administrador, cierra sesión y vuelve a iniciar

### Problema: Error de autenticación
**Solución**: Los tokens expiran, cierra sesión y vuelve a iniciar

---

## 📞 Contacto

Para reportar problemas con la funcionalidad de bloqueados, incluye:
- Número exacto que quisiste bloquear
- Mensaje de error mostrado
- La razón que ingresaste

---

**Versión**: 1.0.4  
**Última actualización**: Marzo 2026  
**Estado**: ✅ Funcionalidad completa y probada
