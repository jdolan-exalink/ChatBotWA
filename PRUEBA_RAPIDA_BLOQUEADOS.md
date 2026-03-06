# ⚡ GUÍA RÁPIDA DE PRUEBA - Bloqueados

## 🎯 Objetivo
Verificar que la funcionalidad de bloqueados funciona correctamente agregando el número `+543424438150` con razón "Facturación".

---

## ✅ Paso 1: Acceder al Sistema

### Opción A: Navegador (Interfaz Gráfica)
```
1. Abre HTTP en tu navegador:
   http://localhost:8088/dashboard

2. Inicia sesión:
   Usuario: admin
   Contraseña: admin123

3. Deberías ver el dashboard
```

### Opción B: Terminal (Script de Prueba)
```bash
cd /opt/clinic-whatsapp-bot
python3 test_blocklist.py
```

---

## 🔧 Prueba Opción A: Interfaz Web

### Paso 1: Navegar a Bloqueados
```
1. En el dashboard, espera a que cargue
2. En el menú lateral izquierdo, busca: 🚫 Bloqueados
3. Haz click en esa opción
4. Deberías ver un formulario y una tabla vacía
```

### Paso 2: Rellenar Formulario
```
Campo 1 - "Número de WhatsApp":
  Ingresa: +543424438150

Campo 2 - "Razón":
  Ingresa: Facturación

(Deja desmarcados los filtros de país/localidad)
```

### Paso 3: Enviar Formulario
```
1. Haz click en el botón azul: "🚫 Bloquear"
2. Observa lo que pasa:
```

#### Resultado Esperado ✅
```
Mensaje mostrado:
┌─────────────────────────────────────┐
│ ⏳ Agregando número a blocklist...  │ (unos segundos)
│                                     │
│ ✅ Número bloqueado exitosamente    │ (después)
└─────────────────────────────────────┘

Los campos se limpian (vacíos)

La tabla actualiza con una nueva fila:
┌──────────────────┬────────────┬──────────────┐
│ Número           │ Razón      │ Acción       │
├──────────────────┼────────────┼──────────────┤
│ +543424438150    │ Facturación│ [Desbloquear]│
└──────────────────┴────────────┴──────────────┘
```

#### Si Hay Error ❌
```
Si ves un mensaje rojo:
❌ Error: [detalle]

Posibles causas:
• No estás logueado como admin
• El API no está funcionando
• Ya existe ese número (ejecuta antes)
• Error de validación

Abre la consola (F12) para ver detalles
```

### Paso 4: Verificar Eliminación (opcional)
```
1. Localiza la fila con +543424438150
2. Haz click en el botón rojo: "Desbloquear"
3. Se abrirá un diálogo de confirmación
4. Haz click en "Aceptar"
5. Verás: "⏳ Desbloqueando número..."
6. Después: "✅ Número desbloqueado exitosamente"
7. La fila desaparece de la tabla
```

---

## 🧪 Prueba Opción B: Script Python

### Requisitos
```
Python 3.7+
requests library instalado

Para instalar:
pip3 install requests
```

### Ejecutar Prueba
```bash
cd /opt/clinic-whatsapp-bot
python3 test_blocklist.py
```

### Salida Esperada
```
============================================================
PRUEBA DE FUNCIONALIDAD DE BLOQUEADOS
============================================================

1️⃣ Obteniendo token de autenticación...
✅ Token obtenido: eyJhbGc...

2️⃣ Listando bloqueados actuales...
✅ Total de números bloqueados: 0

3️⃣ Agregando nuevo bloqueo...
   Número: +543424438150
   Razón: Facturación
   Status Code: 200
   Response: {...}
✅ Número bloqueado exitosamente
   ID: 1
   Teléfono: +543424438150
   Razón: Facturación

4️⃣ Listando bloqueados después de agregar...
✅ Total de números bloqueados: 1
   - +543424438150: Facturación

5️⃣ Removiendo número bloqueado...
   Status Code: 200
   Response: {"ok": true, "message": "..."}
✅ Número desbloqueado exitosamente

6️⃣ Listando bloqueados finales...
✅ Total de números bloqueados: 0

============================================================
PRUEBA COMPLETADA
============================================================
```

---

## 🔍 Checklist de Verificación

Marca ✓ conforme avances:

### Funcionalidad
- [ ] Puedo acceder a la sección "Bloqueados"
- [ ] El formulario se ve correctamente
- [ ] Puedo llenar el número: +543424438150
- [ ] Puedo llenar la razón: Facturación
- [ ] Al hacer click en "Bloquear" aparece el mensaje de procesando
- [ ] El mensaje cambia a éxito ✅
- [ ] Los campos se limpian automáticamente
- [ ] La tabla muestra el nuevo número
- [ ] La tabla tiene un botón "Desbloquear"
- [ ] Puedo eliminar el número
- [ ] Al eliminar aparece confirmación
- [ ] Desaparece de la tabla

### Errores
- [ ] Si dejo el número vacío, muestra error
- [ ] Si no pongo el "+", muestra error
- [ ] Si no pongo razón, muestra error
- [ ] Si intento agregar el mismo número dos veces, muestra error
- [ ] Los errores tienen color rojo ❌

### Seguridad
- [ ] Sin loguearse, no puedes ver bloqueados
- [ ] Con usuario no-admin, no puedes agregar
- [ ] El token se envía correctamente
- [ ] No hay información sensible en el navegador

### Performance
- [ ] La página carga rápido
- [ ] Al hacer click en "Bloquear", responde en < 3 segundos
- [ ] Los mensajes desaparecen automáticamente
- [ ] No se congela el navegador

---

## 🆘 Solución de Problemas

### Problema: "No puedo ver la sección Bloqueados"
```
Soluciones:
1. Recarga la página (F5)
2. Cierra sesión y vuelve a iniciar
3. Verifica estar logueado como admin
4. Abre consola (F12) y busca errores
```

### Problema: "Error: Número ya está bloqueado"
```
Significa: El número ya existe en la lista

Soluciones:
1. Elimina el número primero (click Desbloquear)
2. Luego intenta agregar de nuevo
3. O usa otro número para prueba (+5491234567890)
```

### Problema: "Error al cargar lista de bloqueados"
```
Significa: Problema al conectar con el API

Soluciones:
1. Verifica que el servidor FastAPI está corriendo
   docker-compose ps | grep wa-bot
2. Verifica que el puerto 8088 es accesible
3. Cierra y abre el dashboard nuevamente
4. Busca errores en la consola (F12)
```

### Problema: "Error: HTTP error! status: 401"
```
Significa: Tu token de autenticación expiró

Soluciones:
1. Cierra sesión (logout)
2. Vuelve a iniciar sesión
3. Intenta la operación nuevamente
```

### Problema: "La tabla no se actualiza"
```
Soluciones:
1. Espera 1-2 segundos más
2. Refrescar recargando la página
3. Abre consola (F12) y busca warnings
4. Intenta con un número diferente
```

---

## 📊 Información de Debug

### Para ver errores en detalle:
```
1. Abre el navegador: F12
2. Ve a la pestaña "Console"
3. Intenta agregar el número
4. Busca mensajes rojos o amarillos
5. Copia el error completo for reportar
```

### Ver peticiones HTTP:
```
1. Abre el navegador: F12
2. Ve a la pestaña "Network"
3. Intenta agregar el número
4. Verifica que aparezca:
   POST /api/blocklist
   Status: 200 ✓
5. Haz click para ver detalles
```

### Ver logs del servidor:
```bash
# Si corre en Docker:
docker logs wa-bot | tail -20

# Si corre localmente:
# Los logs aparecen en tu terminal
```

---

## 🎯 Casos de Prueba Detallados

### Test 1: Agregar número válido
```
Input:
  Número: +543424438150
  Razón: Facturación

Expected:
  ✅ Mensaje de éxito
  📋 Aparece en tabla
  [Desbloquear] visible

Result: PASS / FAIL ___
```

### Test 2: Número vacío
```
Input:
  Número: [dejar en blanco]
  Razón: Test

Expected:
  ⚠️ "Ingresa un número de teléfono"

Result: PASS / FAIL ___
```

### Test 3: Número sin "+"
```
Input:
  Número: 543424438150
  Razón: Test

Expected:
  ⚠️ "El número debe comenzar con +"

Result: PASS / FAIL ___
```

### Test 4: Razón vacía
```
Input:
  Número: +543424438150
  Razón: [dejar en blanco]

Expected:
  ⚠️ "Ingresa una razón para el bloqueo"

Result: PASS / FAIL ___
```

### Test 5: Número duplicado
```
Input:
  Número: +543424438150 (que ya existe)
  Razón: Otro motivo

Expected:
  ❌ "Error: Número ya está bloqueado"

Result: PASS / FAIL ___
```

### Test 6: Desbloquear número
```
Input:
  Click en botón [Desbloquear]
  Confirmar: SÍ

Expected:
  ✅ Mensaje de desbloqueo exitoso
  Número desaparece de tabla

Result: PASS / FAIL ___
```

---

## ⏱️ Estimado de Tiempo

| Tarea | Tiempo |
|-------|--------|
| Acceder al dashboard | 30 segundos |
| Navegar a Bloqueados | 10 segundos |
| Rellenar formulario | 15 segundos |
| Enviar y ver resultado | 3 segundos |
| Verificar tabla | 10 segundos |
| Desbloquear número | 5 segundos |
| **Total** | **~1 minuto** |

---

## ✅ Confirmación Final

Una vez completada toda la prueba, deberías poder decir:

> "✅ La funcionalidad de bloqueados está funcionando perfectamente:
> - Puedo agregar números
> - Veo mensajes de éxito
> - Puedo ver la lista actualizada
> - Puedo eliminar números
> - No hay errores"

Si todo eso es verdad: **¡ÉXITO! ✅**

---

**Versión**: 1.0.4  
**Última actualización**: Marzo 5, 2026  
**Duración estimada**: 1-2 minutos
