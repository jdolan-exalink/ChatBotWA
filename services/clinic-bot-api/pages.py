"""
Funciones para renderizar las HTML pages del sistema
Diseño moderno, minimalista y tecnológico
"""
import subprocess
try:
    _GIT_VERSION = subprocess.check_output(
        ["git", "--git-dir=/app/.git", "describe", "--tags", "--always"],
        stderr=subprocess.DEVNULL
    ).decode("utf-8").strip()
except Exception:
    _GIT_VERSION = "v2.3.5"


def _scheduled_messages_shared_js() -> str:
    return """
            function _scheduledMessagesNextAt(sm) {
                const now = new Date();
                const timeParts = String(sm.send_time || '').split(':');
                const hh = Number(timeParts[0]);
                const mm = Number(timeParts[1]);
                if (Number.isNaN(hh) || Number.isNaN(mm)) return null;

                if (sm.send_date) {
                    const exact = new Date(`${sm.send_date}T${sm.send_time}`);
                    return Number.isNaN(exact.getTime()) ? null : exact;
                }

                const allowedDays = String(sm.days_of_week || '1,2,3,4,5,6,7')
                    .split(',')
                    .map(d => Number(d.trim()))
                    .filter(Boolean);

                for (let offset = 0; offset < 8; offset++) {
                    const candidate = new Date(now);
                    candidate.setSeconds(0, 0);
                    candidate.setHours(hh, mm, 0, 0);
                    candidate.setDate(now.getDate() + offset);
                    const dayNumber = candidate.getDay() === 0 ? 7 : candidate.getDay();
                    if (!allowedDays.includes(dayNumber)) continue;
                    if (offset === 0 && candidate < now) continue;
                    return candidate;
                }

                return null;
            }

            function _scheduledMessagesGroupKey(date) {
                if (!date) return 'sin-fecha';
                const y = date.getFullYear();
                const m = String(date.getMonth() + 1).padStart(2, '0');
                const d = String(date.getDate()).padStart(2, '0');
                return `${y}-${m}-${d}`;
            }

            function _scheduledMessagesGroupTitle(date) {
                if (!date) return 'Sin fecha';
                const label = date.toLocaleDateString('es-AR', {
                    weekday: 'long',
                    day: '2-digit',
                    month: 'long'
                });
                return label.charAt(0).toUpperCase() + label.slice(1);
            }

            function _formatScheduledDateTimeInput(sm) {
                if (sm && sm.send_date && sm.send_time) {
                    return `${sm.send_date}T${sm.send_time}`;
                }
                if (sm && sm.send_time) {
                    const today = new Date().toISOString().split('T')[0];
                    return `${today}T${sm.send_time}`;
                }
                return '';
            }

            function _renderScheduledMessagesHTML(list, actions) {
                if (!list.length) {
                    return '<div style="color:#94a3b8;font-size:0.88em;">Sin mensajes programados. Usá ➕ Nuevo para crear uno.</div>';
                }

                const enriched = list.map(sm => ({ ...sm, _nextAt: _scheduledMessagesNextAt(sm) }))
                    .sort((a, b) => {
                        const at = a._nextAt ? a._nextAt.getTime() : Number.MAX_SAFE_INTEGER;
                        const bt = b._nextAt ? b._nextAt.getTime() : Number.MAX_SAFE_INTEGER;
                        return at - bt;
                    });

                const groups = new Map();
                enriched.forEach(sm => {
                    const key = _scheduledMessagesGroupKey(sm._nextAt);
                    if (!groups.has(key)) groups.set(key, []);
                    groups.get(key).push(sm);
                });

                let html = '<div style="display:flex;flex-direction:column;gap:14px;">';
                groups.forEach(items => {
                    const groupDate = items[0]._nextAt;
                    html += `<div style="background:rgba(15,23,42,0.55);border:1px solid rgba(148,163,184,0.14);border-radius:16px;padding:14px;">
                        <div style="position:sticky;top:0;background:rgba(15,23,42,0.96);backdrop-filter:blur(10px);padding-bottom:10px;margin-bottom:12px;z-index:1;">
                            <div style="color:#f8fafc;font-weight:700;font-size:0.96em;">${_scheduledMessagesGroupTitle(groupDate)}</div>
                            <div style="color:#64748b;font-size:0.78em;margin-top:3px;">${items.length} mensaje(s)</div>
                        </div>
                        <div style="display:flex;flex-direction:column;gap:10px;">`;
                    items.forEach(sm => {
                        const active = sm.is_active;
                        const nextAtLabel = sm._nextAt
                            ? sm._nextAt.toLocaleString('es-AR', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' })
                            : 'Sin próxima fecha';
                        html += `<div style="background:rgba(30,41,59,0.58);border:1px solid rgba(226,232,240,0.08);border-radius:14px;padding:14px;display:flex;align-items:flex-start;gap:12px;justify-content:space-between;">
                            <div style="flex:1;min-width:0;">
                                <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                                    <div style="color:#f1f5f9;font-weight:600;font-size:0.92em;">${sm.name}</div>
                                    <span style="padding:3px 8px;border-radius:999px;font-size:0.74em;font-weight:700;background:${active?'rgba(16,185,129,0.15)':'rgba(239,68,68,0.14)'};color:${active?'#86efac':'#fca5a5'};">${active?'Activo':'Pausado'}</span>
                                </div>
                                <div style="color:#8696a0;font-size:0.8em;margin-top:4px;">📞 ${sm.phone_number}</div>
                                <div style="color:#cbd5e1;font-size:0.82em;margin-top:6px;">🕐 Próximo envío: ${nextAtLabel}</div>
                                <div style="color:#64748b;font-size:0.78em;margin-top:4px;">📅 Programado para ${sm.send_date || 'fecha no definida'}</div>
                                <div style="color:#94a3b8;font-size:0.82em;margin-top:8px;line-height:1.45;">${sm.message}</div>
                            </div>
                            <div style="display:flex;flex-direction:column;gap:8px;flex-shrink:0;">
                                <button onclick="${actions.editFn}(${sm.id})" style="padding:7px 10px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:8px;color:#93c5fd;cursor:pointer;font-size:0.82em;">✏️ Editar</button>
                                <button onclick="${actions.deleteFn}(${sm.id})" style="padding:7px 10px;background:rgba(220,38,38,0.12);border:1px solid rgba(220,38,38,0.3);border-radius:8px;color:#fca5a5;cursor:pointer;font-size:0.82em;">✖ Cancelar</button>
                            </div>
                        </div>`;
                    });
                    html += '</div></div>';
                });
                html += '</div>';
                return html;
            }

            async function _loadScheduledMessagesList(config) {
                const box = document.getElementById(config.listId);
                if (!box) return;
                try {
                    const res = await fetch(config.url, { headers: { 'Authorization': `Bearer ${token}` } });
                    if (config.checkUnauth && config.checkUnauth(res)) return;
                    const list = await res.json();
                    box.innerHTML = _renderScheduledMessagesHTML(list, config.actions);
                } catch (e) {
                    box.innerHTML = `<div style="color:#ef4444;font-size:0.88em;">${config.errorText}</div>`;
                }
            }

            function _openScheduledMessagesModal(config, sm, editIdSetter) {
                editIdSetter(sm ? sm.id : null);
                document.getElementById(config.titleId).textContent = sm ? '✏️ Editar Mensaje Programado' : '🕐 Nuevo Mensaje Programado';
                document.getElementById(config.nameId).value = sm ? sm.name : '';
                document.getElementById(config.phoneId).value = sm ? sm.phone_number : '';
                document.getElementById(config.timeId).value = sm ? _formatScheduledDateTimeInput(sm) : '';
                document.getElementById(config.messageId).value = sm ? sm.message : '';
                document.getElementById(config.feedbackId).textContent = '';
                document.getElementById(config.modalId).style.display = 'flex';
            }

            function _closeScheduledMessagesModal(config, editIdSetter) {
                document.getElementById(config.modalId).style.display = 'none';
                editIdSetter(null);
            }

            async function _saveScheduledMessage(config, editId, onSuccess) {
                const msgEl = document.getElementById(config.feedbackId);
                const dateTimeVal = document.getElementById(config.timeId).value.trim();
                let send_date = null;
                let send_time = '';
                if (dateTimeVal) {
                    const parts = dateTimeVal.split('T');
                    send_date = parts[0] || null;
                    send_time = parts[1] || '';
                }

                const payload = {
                    name: document.getElementById(config.nameId).value.trim(),
                    phone_number: document.getElementById(config.phoneId).value.trim(),
                    message: document.getElementById(config.messageId).value.trim(),
                    send_time: send_time,
                    send_date: send_date,
                    days_of_week: '',
                };

                if (!payload.name || !payload.phone_number || !payload.message || !payload.send_time) {
                    msgEl.style.color = '#f87171';
                    msgEl.textContent = 'Completá todos los campos obligatorios.';
                    return;
                }

                try {
                    const url = editId ? `${config.url}/${editId}` : config.url;
                    const method = editId ? 'PUT' : 'POST';
                    const res = await fetch(url, {
                        method,
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (config.checkUnauth && config.checkUnauth(res)) return;
                    if (res.ok) {
                        onSuccess();
                    } else {
                        const d = await res.json();
                        msgEl.style.color = '#f87171';
                        msgEl.textContent = '❌ ' + (d.detail || 'Error');
                    }
                } catch (e) {
                    msgEl.style.color = '#f87171';
                    msgEl.textContent = '❌ Error de red';
                }
            }

            async function _editScheduledMessage(config, id, openModal) {
                const res = await fetch(config.url, { headers: { 'Authorization': `Bearer ${token}` } });
                if (config.checkUnauth && config.checkUnauth(res)) return;
                const list = await res.json();
                const sm = list.find(x => x.id === id);
                if (sm) openModal(sm);
            }

            async function _deleteScheduledMessage(config, id, reloadFn) {
                if (!confirm('¿Eliminar este mensaje programado?')) return;
                const res = await fetch(`${config.url}/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
                if (config.checkUnauth && config.checkUnauth(res)) return;
                reloadFn();
            }

            async function _toggleScheduledMessage(config, id, reloadFn) {
                const res = await fetch(`${config.url}/${id}/toggle`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
                if (config.checkUnauth && config.checkUnauth(res)) return;
                reloadFn();
            }
"""

def get_login_page() -> str:
    """Login minimalista y moderno"""
    return """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Iniciar Sesión - ChatBot WA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                color: #f1f5f9;
            }
            
            .login-wrapper {
                display: flex;
                gap: 40px;
                width: 100%;
                max-width: 900px;
                align-items: center;
            }
            
            .login-branding {
                flex: 1;
                color: white;
                display: none;
            }
            
            @media (min-width: 768px) {
                .login-branding { display: block; }
            }
            
            .login-branding h1 {
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .login-branding p {
                font-size: 1.1em;
                color: #cbd5e1;
                line-height: 1.6;
            }
            
            .login-container {
                background: rgba(18, 24, 40, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 24px;
                padding: 40px;
                width: 100%;
                max-width: 420px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }
            
            .login-header {
                margin-bottom: 40px;
                text-align: center;
            }
            
            .logo { 
                font-size: 3em;
                margin-bottom: 16px;
            }
            
            .login-header h2 {
                color: #f1f5f9;
                font-size: 1.8em;
                margin-bottom: 8px;
                font-weight: 700;
            }
            
            .login-header p {
                color: #94a3b8;
                font-size: 0.95em;
            }
            
            .form-group {
                margin-bottom: 24px;
            }
            
            label {
                display: block;
                color: #e2e8f0;
                font-weight: 500;
                margin-bottom: 8px;
                font-size: 0.95em;
            }
            
            input {
                width: 100%;
                padding: 12px 16px;
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.15);
                border-radius: 10px;
                font-size: 1em;
                color: #f1f5f9;
                transition: all 0.3s ease;
            }
            
            input::placeholder {
                color: #64748b;
            }
            
            input:focus {
                outline: none;
                border-color: #3b82f6;
                background: rgba(30, 41, 59, 0.8);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .submit-btn {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 10px;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4);
            }
            
            .submit-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }
            
            .error {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(244, 63, 94, 0.5);
                color: #fca5a5;
                padding: 12px 16px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: none;
                font-size: 0.95em;
            }
            
            .error.show { display: block; }
            
            .loading {
                display: none;
                margin-top: 20px;
                text-align: center;
                color: #94a3b8;
                font-size: 0.9em;
            }
            
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
                vertical-align: middle;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="login-wrapper">
            <div class="login-branding">
                <h1>ChatBot WA</h1>
                <p>Sistema integral de gestión para WhatsApp. Automatiza, controla y gestiona tu WhatsApp desde un único panel.</p>
            </div>
            
            <div class="login-container">
                <div class="login-header">
                    <div class="logo">🤖</div>
                    <h2>Iniciar Sesión</h2>
                    <p>Accede a tu panel de control</p>
                </div>
                
                <form id="loginForm">
                    <div class="error" id="errorMsg"></div>
                    
                    <div class="form-group">
                        <label for="username">Usuario</label>
                        <input type="text" id="username" name="username" required placeholder="Tu usuario" autocomplete="username">
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input type="password" id="password" name="password" required placeholder="Tu contraseña" autocomplete="current-password">
                    </div>
                    
                    <button type="submit" class="submit-btn" id="submitBtn">Iniciar Sesión</button>
                    <div class="loading" id="loading">
                        <span class="spinner"></span>
                        <span>Autenticando...</span>
                    </div>
                </form>
                
                <div style="margin-top: 30px; padding-top: 24px; border-top: 1px solid rgba(226, 232, 240, 0.1);">
                    <p style="color: #475569; font-size: 0.75em; text-align: center;">
                        DOLAN SS - 2026
                    </p>
                    <p style="color: #64748b; font-size: 0.7em; text-align: center; margin-top: 4px;">
                        Ver: <span id="versionDisplay">""" + _GIT_VERSION + """</span>
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            const API_URL = '/api';
            
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value;
                const errorMsg = document.getElementById('errorMsg');
                const loading = document.getElementById('loading');
                const submitBtn = document.getElementById('submitBtn');
                
                if (!username || !password) {
                    errorMsg.textContent = 'Por favor completa todos los campos';
                    errorMsg.classList.add('show');
                    return;
                }
                
                errorMsg.classList.remove('show');
                loading.style.display = 'block';
                submitBtn.disabled = true;
                
                try {
                    console.log('[LOGIN] Enviando credenciales...');
                    
                    const response = await fetch(`${API_URL}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    console.log('[LOGIN] Status:', response.status);
                    
                    let data = null;
                    let errorDetail = 'Error desconocido';
                    
                    try {
                        data = await response.json();
                        errorDetail = data.detail || data.message || 'Error en el servidor';
                    } catch (parseError) {
                        console.error('[LOGIN] No se puede parsear JSON:', parseError);
                        errorDetail = 'Error de servidor. Intenta de nuevo.';
                    }
                    
                    if (!response.ok) {
                        console.error('[LOGIN] Error:', errorDetail);
                        throw new Error(errorDetail);
                    }
                    
                    console.log('[LOGIN] Login exitoso, guardando token...');
                    
                    localStorage.setItem('token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    console.log('[LOGIN] Token guardado, redirigiendo...');
                    
                    setTimeout(() => {
                        if (data.user.is_admin) {
                            window.location.href = '/dashboard';
                        } else {
                            window.location.href = '/user-panel';
                        }
                    }, 500);
                    
                } catch (error) {
                    console.error('[LOGIN] Error capturado:', error);
                    errorMsg.textContent = error.message;
                    errorMsg.classList.add('show');
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                }
            });
            
            async function loadVersion() {
                try {
                    const res = await fetch('/version');
                    if (res.ok) {
                        const data = await res.json();
                        document.getElementById('versionDisplay').textContent = data.version;
                    }
                } catch (e) {
                    console.log('Version not available:', e);
                }
            }
            
            document.getElementById('username').focus();
            loadVersion();
        </script>
    </body>
    </html>
    """

def get_user_panel_page() -> str:
    """Panel de usuario rediseñado - misma estética que admin con sidebar"""
    return """<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel Usuario - ChatBot WA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
                color: #e2e8f0;
            }
            
            /* ── SIDEBAR ── */
            .sidebar {
                position: fixed;
                left: 0; top: 0;
                width: 250px; height: 100vh;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(226, 232, 240, 0.1);
                padding: 24px 0 0 0;
                display: flex;
                flex-direction: column;
                z-index: 100;
            }

            .sidebar-header {
                padding: 0 20px 24px;
                border-bottom: 1px solid rgba(226, 232, 240, 0.1);
                margin-bottom: 12px;
            }

            .sidebar-header h2 {
                font-size: 1.3em;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 4px;
            }

            .sidebar-header p { color: #94a3b8; font-size: 0.82em; }

            .sidebar-nav { flex: 1; }

            .nav-item {
                padding: 12px 20px;
                color: #cbd5e1;
                cursor: pointer;
                transition: all 0.3s ease;
                border-left: 3px solid transparent;
                margin: 2px 0;
                font-size: 0.95em;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .nav-item:hover { background: rgba(59, 130, 246, 0.1); color: #93c5fd; }
            .nav-item.active { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border-left-color: #3b82f6; }

            /* ── SIDEBAR FOOTER ── */
            .sidebar-footer {
                border-top: 1px solid rgba(226, 232, 240, 0.1);
                padding: 14px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                background: rgba(15, 23, 42, 0.97);
            }

            .sidebar-user {
                display: flex;
                align-items: center;
                gap: 9px;
                padding: 9px 10px;
                background: rgba(30, 41, 59, 0.5);
                border-radius: 10px;
                border: 1px solid rgba(226, 232, 240, 0.07);
                cursor: pointer;
                transition: background 0.2s;
                user-select: none;
            }
            .sidebar-user:hover { background: rgba(30, 41, 59, 0.8); }

            .sidebar-user-avatar {
                width: 32px; height: 32px;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                border-radius: 8px;
                display: flex; align-items: center; justify-content: center;
                font-weight: 700; color: white; font-size: 0.88em;
                flex-shrink: 0;
            }
            .sidebar-user-info { flex: 1; overflow: hidden; }
            .sidebar-user-name {
                color: #f1f5f9; font-weight: 600; font-size: 0.88em;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            }
            .sidebar-user-role { color: #64748b; font-size: 0.75em; }

            .user-chevron {
                color: #64748b; font-size: 0.75em;
                transition: transform 0.25s;
                flex-shrink: 0;
            }
            .user-chevron.open { transform: rotate(180deg); }

            .user-menu {
                background: rgba(15, 23, 42, 0.98);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 10px;
                overflow: hidden;
            }
            .user-menu-item {
                padding: 10px 14px;
                color: #93c5fd;
                cursor: pointer;
                font-size: 0.88em;
                font-weight: 500;
                transition: background 0.2s;
                display: flex; align-items: center; gap: 8px;
            }
            .user-menu-item:hover { background: rgba(59, 130, 246, 0.15); }

            .sidebar-logout-btn {
                width: 100%;
                padding: 9px;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.85em;
                font-weight: 600;
                display: flex; align-items: center; justify-content: center; gap: 6px;
                transition: all 0.3s ease;
            }
            .sidebar-logout-btn:hover { background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.4); }

            .sidebar-footer-info { text-align: center; }
            .sidebar-footer-info .company { color: #475569; font-weight: 600; font-size: 0.78em; }
            .sidebar-footer-info .version { color: #334155; font-size: 0.75em; }

            /* ── MAIN ── */
            .main { margin-left: 250px; padding: 30px; min-height: 100vh; }

            .section { display: none; }
            .section.active { display: block; animation: fadeIn 0.3s ease; }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(8px); }
                to   { opacity: 1; transform: translateY(0); }
            }

            .page-header { margin-bottom: 28px; }
            .page-header h1 {
                font-size: 2em; font-weight: 700;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            /* ── CARDS ── */
            .card {
                background: rgba(18, 24, 40, 0.85);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.08);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
            }
            .card h2 { font-size: 1.2em; margin-bottom: 18px; color: #f1f5f9; font-weight: 600; }
            .card-footer {
                display: flex; gap: 12px; justify-content: flex-end;
                margin-top: 20px; padding-top: 20px;
                border-top: 1px solid rgba(226, 232, 240, 0.06);
            }

            /* ── BUTTONS ── */
            .btn {
                padding: 10px 20px; border: none; border-radius: 8px;
                font-size: 0.9em; font-weight: 600; cursor: pointer;
                transition: all 0.2s;
            }
            .btn-primary { background: linear-gradient(135deg, #3b82f6, #06b6d4); color: white; }
            .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(59,130,246,0.3); }
            .btn-primary:disabled { opacity: 0.55; cursor: not-allowed; transform: none; box-shadow: none; }
            .btn-secondary {
                background: rgba(226,232,240,0.08);
                border: 1px solid rgba(226,232,240,0.12);
                color: #94a3b8;
            }
            .btn-secondary:hover { background: rgba(226,232,240,0.13); }
            .btn-danger {
                background: rgba(239,68,68,0.12);
                border: 1px solid rgba(244,63,94,0.35);
                color: #f87171;
            }
            .btn-danger:hover { background: rgba(239,68,68,0.22); }
            .btn-sm { padding: 5px 12px; font-size: 0.82em; }
            .btn-icon { padding: 5px 10px; font-size: 0.85em; }

            /* ── STATUS GRID ── */
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 16px; margin-bottom: 24px;
            }
            .status-item {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.08);
                border-radius: 12px; padding: 18px; text-align: center;
            }
            .status-item-icon { font-size: 2em; margin-bottom: 8px; }
            .status-item-label { font-size: 0.82em; color: #94a3b8; margin-bottom: 6px; }
            .status-item-value { font-size: 1.5em; color: #f1f5f9; font-weight: 700; }

            /* ── TOGGLE / CONNECT BUTTONS ── */
            .toggle-btn {
                width: 100%; padding: 14px;
                border: none; border-radius: 10px;
                font-size: 1em; font-weight: 600; cursor: pointer;
                transition: all 0.3s ease;
            }
            .toggle-btn.active { background: linear-gradient(135deg, #10b981, #059669); color: white; }
            .toggle-btn.paused { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
            .toggle-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(59,130,246,0.25); }

            .btn-connect {
                width: 100%; padding: 12px;
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                color: white; border: none; border-radius: 10px;
                font-size: 1em; font-weight: 600; cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-connect:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(6,182,212,0.3); }
            .btn-connect:disabled { cursor: default; opacity: 0.85; }
            .btn-connect.connected { background: linear-gradient(135deg, #16a34a, #15803d); }

            /* ── FORM ── */
            .form-group { margin-bottom: 14px; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
            @media (max-width: 640px) { .form-row { grid-template-columns: 1fr; } }
            label { display: block; color: #cbd5e1; font-size: 0.88em; font-weight: 500; margin-bottom: 5px; }
            input[type="text"],
            input[type="email"],
            input[type="password"],
            input[type="date"],
            input[type="time"],
            select, textarea {
                width: 100%; padding: 9px 12px;
                background: rgba(30,41,59,0.6);
                border: 1px solid rgba(226,232,240,0.12);
                border-radius: 8px; color: #f1f5f9; font-size: 0.92em;
                font-family: inherit; transition: border-color 0.2s;
            }
            input:focus, select:focus, textarea:focus {
                outline: none; border-color: rgba(59,130,246,0.5);
                background: rgba(30,41,59,0.8);
            }
            textarea { resize: vertical; }

            /* ── CALENDAR ── */
            .hol-layout {
                display: grid;
                grid-template-columns: 1.15fr 0.85fr;
                gap: 24px; align-items: start;
            }
            @media (max-width: 900px) { .hol-layout { grid-template-columns: 1fr; } }

            .cal-wrap {
                background: rgba(30,41,59,0.5);
                border: 1px solid rgba(226,232,240,0.1);
                border-radius: 12px; padding: 18px;
                user-select: none;
            }
            .cal-header {
                display: flex; align-items: center; justify-content: space-between;
                margin-bottom: 16px;
            }
            .cal-title { font-size: 1.1em; font-weight: 600; color: #f1f5f9; }
            .cal-nav { display: flex; gap: 6px; }
            .cal-btn {
                padding: 5px 12px;
                background: rgba(59,130,246,0.12);
                border: 1px solid rgba(59,130,246,0.25);
                color: #93c5fd; border-radius: 7px; cursor: pointer;
                font-size: 0.85em; font-weight: 600; transition: background 0.2s;
            }
            .cal-btn:hover { background: rgba(59,130,246,0.25); }
            .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
            .cal-hdr { text-align: center; font-size: 0.76em; font-weight: 700; color: #64748b; padding: 5px 0; }
            .cal-hdr.wknd { color: #f472b6; }
            .cal-cell {
                aspect-ratio: 1; display: flex; align-items: center;
                justify-content: center; border-radius: 8px;
                background: rgba(15,23,42,0.4);
                border: 1px solid rgba(226,232,240,0.08);
                font-size: 0.88em; font-weight: 600; color: #cbd5e1;
                cursor: pointer; transition: all 0.18s;
            }
            .cal-cell.empty { background: transparent; border-color: transparent; cursor: default; }
            .cal-cell:not(.empty):not(.selected):not(.pending):not(.removing):hover {
                background: rgba(59,130,246,0.2); border-color: rgba(59,130,246,0.35); color: #93c5fd;
            }
            .cal-cell.wknd { color: #f472b6; }
            .cal-cell.selected {
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                border-color: rgba(59,130,246,0.6); color: #fff; font-weight: 700;
            }
            .cal-cell.pending {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                border-color: rgba(245,158,11,0.6); color: #fff; font-weight: 700;
            }
            .cal-cell.removing {
                background: rgba(239,68,68,0.18);
                border-color: rgba(244,63,94,0.45); color: #f87171; text-decoration: line-through;
            }
            .cal-cell.today { outline: 2px solid rgba(99,102,241,0.8); outline-offset: 2px; }
            .cal-legend {
                display: flex; flex-wrap: wrap; gap: 12px; margin-top: 14px;
                padding-top: 14px; border-top: 1px solid rgba(226,232,240,0.07);
                font-size: 0.78em; color: #64748b;
            }
            .cal-legend span { display: flex; align-items: center; gap: 5px; }
            .leg-dot { width: 12px; height: 12px; border-radius: 4px; display: inline-block; }

            .pending-badge {
                display: inline-flex; align-items: center; gap: 6px;
                padding: 7px 12px; background: rgba(245,158,11,0.12);
                border: 1px solid rgba(245,158,11,0.35);
                border-radius: 8px; font-size: 0.85em; color: #fcd34d;
                margin-bottom: 14px;
            }
            .pending-badge.hidden { display: none; }

            .holiday-row {
                display: flex; align-items: center; justify-content: space-between;
                padding: 9px 12px; background: rgba(59,130,246,0.06);
                border: 1px solid rgba(59,130,246,0.12);
                border-radius: 9px; margin-bottom: 7px;
            }
            .holiday-info { display: flex; flex-direction: column; gap: 2px; }
            .holiday-date { font-size: 0.82em; color: #60a5fa; font-weight: 600; }
            .holiday-name { font-size: 0.9em; color: #f1f5f9; }
            .empty-state { text-align: center; padding: 28px; color: #475569; font-size: 0.9em; font-style: italic; }

            /* ── BLOCKLIST ── */
            .block-row {
                display: flex; align-items: center; justify-content: space-between;
                padding: 11px 14px; background: rgba(30,41,59,0.4);
                border: 1px solid rgba(226,232,240,0.07);
                border-radius: 9px; margin-bottom: 8px;
            }
            .block-info { display: flex; flex-direction: column; gap: 2px; }
            .block-phone { font-size: 0.92em; color: #f1f5f9; font-weight: 600; }
            .block-reason { font-size: 0.8em; color: #64748b; }

            /* ── TOAST ── */
            .toast {
                position: fixed; bottom: 24px; right: 24px;
                padding: 13px 20px; border-radius: 10px;
                font-size: 0.88em; font-weight: 500;
                transform: translateY(80px); opacity: 0;
                transition: all 0.3s; z-index: 9000;
                max-width: 320px; pointer-events: none;
            }
            .toast.show { transform: translateY(0); opacity: 1; }
            .toast.success { background: rgba(16,185,129,0.18); border: 1px solid rgba(16,185,129,0.4); color: #6ee7b7; }
            .toast.error   { background: rgba(239,68,68,0.18); border: 1px solid rgba(244,63,94,0.4); color: #fca5a5; }
            .toast.info    { background: rgba(59,130,246,0.18); border: 1px solid rgba(59,130,246,0.4); color: #93c5fd; }

            /* ── WA TOAST ── */
            .wa-toast {
                position: fixed; bottom: 30px; left: 50%;
                transform: translateX(-50%) translateY(80px);
                background: #16a34a; color: white;
                padding: 14px 28px; border-radius: 12px;
                font-weight: 600; font-size: 0.95em;
                z-index: 9999; opacity: 0;
                transition: transform 0.35s ease, opacity 0.35s ease;
                pointer-events: none;
            }
            .wa-toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }

            /* ── MODALS ── */
            .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.75); align-items: center; justify-content: center; z-index: 1000; }
            .modal.show { display: flex; }
            .modal-content {
                background: rgba(18,24,40,0.96); border: 1px solid rgba(226,232,240,0.1);
                border-radius: 20px; padding: 36px; max-width: 400px; width: 90%; text-align: center;
            }
            .modal-content h3 { color: #f1f5f9; margin-bottom: 16px; }
            .qr-image { margin: 18px 0; max-width: 100%; border-radius: 12px; border: 2px solid rgba(226,232,240,0.1); }
            .modal-close {
                display: inline-block; padding: 8px 18px;
                background: rgba(239,68,68,0.1); color: #fca5a5;
                border: 1px solid rgba(244,63,94,0.4);
                border-radius: 8px; cursor: pointer; margin-top: 18px;
            }

            /* ── SPINNER ── */
            .qr-loading { display: flex; flex-direction: column; align-items: center; padding: 28px 0; }
            .spinner {
                width: 50px; height: 50px;
                border: 5px solid rgba(59,130,246,0.2);
                border-top-color: #3b82f6;
                border-radius: 50%; animation: spin 0.9s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
            .spinner-text { color: #94a3b8; margin-top: 14px; font-size: 0.88em; text-align: center; line-height: 1.5; }

            /* ── CHANGE PASSWORD MODAL ── */
            .pw-modal {
                display: none; position: fixed; inset: 0;
                background: rgba(0,0,0,0.78); align-items: center; justify-content: center; z-index: 3000;
            }
            .pw-modal.show { display: flex; }
            .pw-modal-content {
                background: rgba(15,23,42,0.99);
                border: 1px solid rgba(226,232,240,0.12);
                border-radius: 18px; padding: 28px; width: 94%; max-width: 380px;
                display: flex; flex-direction: column; gap: 14px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            }
            .pw-modal-header { display: flex; justify-content: space-between; align-items: center; }
            .pw-modal-title { color: #f1f5f9; font-size: 1.05em; font-weight: 700; }
            .pw-modal-close { background: none; border: none; color: #94a3b8; font-size: 1.3em; cursor: pointer; }

            @media (max-width: 768px) {
                .sidebar { width: 100%; height: auto; position: relative; border-right: none; border-bottom: 1px solid rgba(226,232,240,0.1); }
                .main { margin-left: 0; padding: 20px; }
            }
        </style>
    </head>
    <body>

        <!-- ══════════ SIDEBAR ══════════ -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🤖 WA-BOT</h2>
                <p>Panel Usuario</p>
            </div>

            <div class="sidebar-nav">
                <div class="nav-item active" id="navEstado" onclick="switchSection('estado')">📊 Estado</div>
                <div class="nav-item" id="navTickets" onclick="switchSection('tickets')">🎫 Tickets</div>
                <div class="nav-item" id="navProgramados" onclick="switchSection('programados')">🕐 Programados</div>
                <div class="nav-item" id="navFeriados" onclick="switchSection('feriados')">📅 Feriados</div>
                <div class="nav-item" id="navBloqueados" onclick="switchSection('bloqueados')">🚫 Bloqueados</div>
            </div>

            <div class="sidebar-footer">
                <!-- User box with dropdown -->
                <div class="sidebar-user" id="sidebarUserBox" onclick="toggleUserMenu()">
                    <div class="sidebar-user-avatar" id="userAvatar">U</div>
                    <div class="sidebar-user-info">
                        <div class="sidebar-user-name" id="sidebarUserName">Usuario</div>
                        <div class="sidebar-user-role">Operador</div>
                    </div>
                    <span class="user-chevron" id="userChevron">▾</span>
                </div>

                <!-- Dropdown menu -->
                <div class="user-menu" id="userMenu" style="display:none;">
                    <div class="user-menu-item" onclick="openChangePwModal()">🔑 Cambiar Contraseña</div>
                </div>

                <button class="sidebar-logout-btn" onclick="logout()">
                    <span>🚪</span> Logout
                </button>

                <div class="sidebar-footer-info">
                    <div class="company">DOLAN SS · 2026</div>
                    <div class="version" id="userPanelVersion">""" + _GIT_VERSION + """</div>
                </div>
            </div>
        </div>

        <!-- ══════════ MAIN CONTENT ══════════ -->
        <div class="main">

            <!-- ═══  ESTADO  ═══ -->
            <div id="estado" class="section active">
                <div class="page-header">
                    <h1>📊 Estado del Sistema</h1>
                </div>

                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-item-icon" id="waIcon">🔴</div>
                        <div class="status-item-label">WhatsApp</div>
                        <div class="status-item-value" id="waStatus">Desconectado</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-icon" id="botIcon">⏸️</div>
                        <div class="status-item-label">Bot</div>
                        <div class="status-item-value" id="botStatus">Pausado</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-icon" id="hoursIcon">✅</div>
                        <div class="status-item-label">Horarios</div>
                        <div class="status-item-value" id="hoursStatus">Normal</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-icon">🤖</div>
                        <div class="status-item-label">Solución</div>
                        <div class="status-item-value" id="solutionName">—</div>
                    </div>
                </div>

                <div class="card">
                    <h2>🎛️ Control del Bot</h2>
                    <button class="toggle-btn" id="toggleBtn" onclick="toggleBot()">▶️ Activar Bot</button>
                </div>

                <div class="card">
                    <h2>📱 WhatsApp</h2>
                    <button class="btn-connect" id="waBtn" onclick="toggleWhatsApp()">🔴 Conectar WhatsApp</button>
                </div>

                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                        <h2 style="margin-bottom:0;">⏸️ Números en Espera (Parking)</h2>
                        <button class="btn btn-secondary" style="padding:7px 13px;font-size:0.85em;" onclick="loadParkedList()">🔄 Actualizar</button>
                    </div>
                    <div id="parkedListUser"><div style="color:#94a3b8;font-size:0.88em;">Cargando...</div></div>
                </div>

            </div>

            <!-- ═══  TICKETS  ═══ -->
            <div id="tickets" class="section">
                <div class="page-header">
                    <h1>🎫 Tickets (Chats)</h1>
                    <p style="color: #94a3b8;">Gestiona las conversaciones de los usuarios con el bot o el operador.</p>
                </div>
                
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>Listado de Tickets</h2>
                        <button class="btn btn-primary btn-sm" onclick="loadTickets()"><i class="fas fa-sync"></i> Refrescar</button>
                    </div>
                    
                    <div id="ticketsGrid" style="display: flex; flex-direction: column; gap: 12px; max-height: 60vh; overflow-y: auto; padding-right: 10px;">
                        <div class="empty-state">Cargando tickets...</div>
                    </div>
                </div>

            </div>

            <div id="programados" class="section">
                <div class="page-header">
                    <h1>🕐 Mensajes Programados</h1>
                    <p style="color:#94a3b8;">Ordenados de más cerca a más lejos y agrupados por día.</p>
                </div>

                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;gap:12px;flex-wrap:wrap;">
                        <div>
                            <h2 style="margin:0;">Listado Programado</h2>
                            <p style="color:#94a3b8;margin-top:6px;font-size:0.88em;">Editá o cancelá cualquier envío desde esta vista.</p>
                        </div>
                        <div style="display:flex;gap:8px;">
                            <button class="btn btn-secondary btn-sm" onclick="loadSchedList()">🔄 Refrescar</button>
                            <button class="btn btn-primary btn-sm" onclick="openSchedModal()">➕ Nuevo</button>
                        </div>
                    </div>
                    <div id="schedList" style="max-height:62vh;overflow-y:auto;padding-right:8px;">
                        <div style="color:#94a3b8;font-size:0.88em;">Cargando...</div>
                    </div>
                </div>
            </div>

            <!-- Modales Tickets -->
            <div id="ticketChatModal" class="modal">
                <div style="background:#111b21; border-radius:16px; width:96%; max-width:560px; height:82vh; max-height:680px; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 80px rgba(0,0,0,0.7);">
                    <div style="background:#1f2c34; padding:10px 16px; display:flex; align-items:center; gap:12px; border-bottom:1px solid rgba(255,255,255,0.06); flex-shrink:0;">
                        <div style="width:40px; height:40px; border-radius:50%; background:#2a3942; display:flex; align-items:center; justify-content:center; font-size:1.1em; flex-shrink:0;">👤</div>
                        <div style="flex:1; min-width:0;">
                            <div id="ticketChatModalTitle" style="color:#e9edef; font-size:0.97em; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></div>
                            <div style="color:#8696a0; font-size:0.75em;">Ticket: <span id="ticketChatModalTicket" style="color:#53bdeb; font-family:monospace;"></span></div>
                        </div>
                        <button onclick="closeTicketChatModal()" style="background:none; border:none; color:#8696a0; font-size:1.3em; cursor:pointer; padding:6px; flex-shrink:0;">&times;</button>
                    </div>
                    <div id="ticketChatMessages" style="flex:1; overflow-y:auto; padding:12px 10px; display:flex; flex-direction:column; gap:2px; background:#0b141a;"></div>
                    <div style="background:#1f2c34; padding:12px; display:flex; justify-content:space-between; align-items:center; gap:10px; border-top:1px solid rgba(255,255,255,0.06); flex-shrink:0;">
                        <div style="display:flex; flex-direction:column; gap:6px; align-items:flex-start;">
                            <div style="display:flex; gap:8px; flex-wrap:wrap;" id="ticketChatModalActions"></div>
                            <div style="font-size:0.78em; color:#94a3b8;">Seleccioná uno o más mensajes del chat para llevarlos al programado.</div>
                        </div>
                        <button class="btn btn-primary btn-sm" id="ticketBtnSched" onclick="openTicketScheduleModal()">Agendar Mensaje</button>
                    </div>
                </div>
            </div>
            
            <div id="ticketScheduleModal" class="modal">
                <div class="modal-content">
                    <h3 style="margin-top:0;">Agendar Mensaje</h3>
                    <div class="form-group" style="text-align: left;">
                        <label>Teléfono</label>
                        <input type="text" id="ticketSchedPhone" readonly style="opacity: 0.7;">
                    </div>
                    <div class="form-group" style="text-align: left;">
                        <label>Nombre del Recordatorio</label>
                        <input type="text" id="ticketSchedName" placeholder="Ej: Recordatorio Turno">
                    </div>
                    <div class="form-group" style="text-align: left;">
                        <label>Fecha y Hora</label>
                        <input type="datetime-local" id="ticketSchedTime">
                    </div>
                    <div class="form-group" style="text-align: left;">
                        <label>Mensaje</label>
                        <textarea id="ticketSchedMessage" rows="4" placeholder="Contenido del mensaje..."></textarea>
                    </div>
                    <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                        <button class="btn btn-secondary" onclick="closeTicketScheduleModal()">Cancelar</button>
                        <button class="btn btn-primary" onclick="saveTicketScheduledMessage()">Guardar</button>
                    </div>
                </div>
            </div>

            <!-- ═══  FERIADOS  ═══ -->
            <div id="feriados" class="section">
                <div class="page-header">
                    <h1>📅 Feriados</h1>
                </div>

                <div class="hol-layout">
                    <div class="card" style="margin-bottom:0;">
                        <h2>📅 Calendario de Feriados</h2>
                        <p style="color:#64748b;font-size:0.85em;margin-bottom:14px;">
                            Clic en un día para marcar/desmarcar como feriado.
                            <strong style="color:#60a5fa;">Azul</strong> = guardado &nbsp;·&nbsp;
                            <strong style="color:#fcd34d;">Amarillo</strong> = pendiente &nbsp;·&nbsp;
                            <strong style="color:#f87171;">Tachado</strong> = por eliminar.
                        </p>
                        <div id="pendingBadge" class="pending-badge hidden">
                            ⚠️ <span id="pendingText">0 cambios pendientes</span>
                        </div>
                        <div class="cal-wrap">
                            <div class="cal-header">
                                <div class="cal-nav">
                                    <button class="cal-btn" onclick="calPrev()">◀ Ant</button>
                                    <button class="cal-btn" onclick="calToday()">Hoy</button>
                                    <button class="cal-btn" onclick="calNext()">Sig ▶</button>
                                </div>
                                <div class="cal-title" id="calTitle">—</div>
                            </div>
                            <div class="cal-grid" id="calGrid"></div>
                            <div class="cal-legend">
                                <span><div class="leg-dot" style="background:linear-gradient(135deg,#3b82f6,#06b6d4);"></div> Guardado</span>
                                <span><div class="leg-dot" style="background:linear-gradient(135deg,#f59e0b,#d97706);"></div> Por guardar</span>
                                <span><div class="leg-dot" style="background:rgba(239,68,68,0.3);border:1px solid #f87171;"></div> Por eliminar</span>
                                <span><div class="leg-dot" style="background:transparent;outline:2px solid rgba(99,102,241,0.8);outline-offset:1px;"></div> Hoy</span>
                                <span><div class="leg-dot" style="background:rgba(244,114,182,0.15);"></div> <span style="color:#f472b6">Fin de semana</span></span>
                            </div>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-secondary" onclick="cancelHolidays()">✖ Cancelar</button>
                            <button class="btn btn-primary" id="saveHBtn" onclick="saveHolidays()">💾 Guardar Feriados</button>
                        </div>
                    </div>

                    <div class="card" style="margin-bottom:0;">
                        <h2>📋 Feriados Guardados</h2>
                        <div id="holidaysList" style="max-height:480px;overflow-y:auto;">
                            <div class="empty-state">Cargando...</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ═══  BLOQUEADOS  ═══ -->
            <div id="bloqueados" class="section">
                <div class="page-header">
                    <h1>🚫 Lista de Bloqueados</h1>
                </div>

                <div class="card">
                    <h2>🔒 Bloquear Número</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Número (ej: 5491112345678)</label>
                            <input type="text" id="blPhone" placeholder="5491112345678">
                        </div>
                        <div class="form-group">
                            <label>Motivo (opcional)</label>
                            <input type="text" id="blReason" placeholder="Spam, molestia, etc.">
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-secondary" onclick="clearBlockForm()">✖ Cancelar</button>
                        <button class="btn btn-primary" id="saveBlBtn" onclick="saveBlock()">🚫 Bloquear</button>
                    </div>
                </div>

                <div class="card">
                    <h2>📋 Números Bloqueados</h2>
                    <div id="blocklistItems"><div class="empty-state">Cargando...</div></div>
                </div>
            </div>
        </div>

        <!-- ══════════ MODALS ══════════ -->

        <!-- Modal: Cambiar Contraseña -->
        <div class="pw-modal" id="changePwModal">
            <div class="pw-modal-content">
                <div class="pw-modal-header">
                    <span class="pw-modal-title">🔑 Cambiar Contraseña</span>
                    <button class="pw-modal-close" onclick="closeChangePwModal()">&times;</button>
                </div>
                <form onsubmit="return false;" autocomplete="on">
                <input type="text" name="username" autocomplete="username" style="display:none;" aria-hidden="true">
                <div class="form-group">
                    <label>Contraseña Actual</label>
                    <input type="password" id="oldPw" placeholder="Tu contraseña actual" autocomplete="current-password">
                </div>
                <div class="form-group">
                    <label>Contraseña Nueva</label>
                    <input type="password" id="newPw" placeholder="Mínimo 6 caracteres" autocomplete="new-password">
                </div>
                <div class="form-group">
                    <label>Confirmar Contraseña</label>
                    <input type="password" id="confirmPw" placeholder="Repetí la nueva contraseña" autocomplete="new-password">
                </div>
                </form>
                <div id="pwMsg" style="font-size:0.85em;min-height:18px;text-align:center;"></div>
                <div style="display:flex;gap:10px;margin-top:4px;">
                    <button onclick="savePassword()" class="btn btn-primary" style="flex:1;">💾 Guardar</button>
                    <button onclick="closeChangePwModal()" class="btn btn-secondary" style="padding:10px 16px;">Cancelar</button>
                </div>
            </div>
        </div>

        <!-- Modal: Mensajes Programados -->
        <div id="schedModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.82);align-items:center;justify-content:center;z-index:2000;">
            <div style="background:rgba(15,23,42,0.99);border:1px solid rgba(226,232,240,0.12);border-radius:18px;padding:28px;width:94%;max-width:480px;display:flex;flex-direction:column;gap:14px;box-shadow:0 20px 60px rgba(0,0,0,0.6);">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="color:#f1f5f9;font-size:1.05em;font-weight:700;" id="schedModalTitle">🕐 Nuevo Mensaje Programado</div>
                    <button onclick="closeSchedModal()" style="background:none;border:none;color:#94a3b8;font-size:1.3em;cursor:pointer;">&times;</button>
                </div>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <div><label style="color:#94a3b8;font-size:0.82em;display:block;margin-bottom:4px;">Nombre / Descripción</label>
                        <input id="schedName" type="text" placeholder="Ej: Recordatorio turno mañana" style="width:100%;padding:9px 12px;background:rgba(30,41,59,0.7);border:1px solid rgba(226,232,240,0.15);border-radius:8px;color:#f1f5f9;font-size:0.9em;box-sizing:border-box;"></div>
                    <div><label style="color:#94a3b8;font-size:0.82em;display:block;margin-bottom:4px;">Número(s) destino</label>
                        <input id="schedPhone" type="text" placeholder="5491112345678" style="width:100%;padding:9px 12px;background:rgba(30,41,59,0.7);border:1px solid rgba(226,232,240,0.15);border-radius:8px;color:#f1f5f9;font-size:0.9em;box-sizing:border-box;"></div>
                    <div><label style="color:#94a3b8;font-size:0.82em;display:block;margin-bottom:4px;">Fecha y Hora</label>
                        <input id="schedTime" type="datetime-local" style="width:100%;padding:9px 12px;background:rgba(30,41,59,0.7);border:1px solid rgba(226,232,240,0.15);border-radius:8px;color:#f1f5f9;font-size:0.9em;box-sizing:border-box;"></div>
                    <div><label style="color:#94a3b8;font-size:0.82em;display:block;margin-bottom:4px;">Mensaje</label>
                        <textarea id="schedMsg" rows="4" placeholder="Texto del mensaje a enviar..." style="width:100%;padding:9px 12px;background:rgba(30,41,59,0.7);border:1px solid rgba(226,232,240,0.15);border-radius:8px;color:#f1f5f9;font-size:0.9em;resize:vertical;box-sizing:border-box;"></textarea></div>
                </div>
                <div style="display:flex;gap:10px;margin-top:4px;">
                    <button onclick="saveSchedMsg()" style="flex:1;padding:11px;background:linear-gradient(135deg,#3b82f6,#06b6d4);border:none;border-radius:8px;color:white;font-weight:600;cursor:pointer;">💾 Guardar</button>
                    <button onclick="closeSchedModal()" style="padding:11px 18px;background:rgba(30,41,59,0.5);border:1px solid rgba(226,232,240,0.1);border-radius:8px;color:#94a3b8;cursor:pointer;">Cancelar</button>
                </div>
                <div id="schedModalMsg" style="font-size:0.85em;min-height:18px;text-align:center;"></div>
            </div>
        </div>

        <!-- Modal: Chat Ticket -->
        <div id="chatModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);align-items:center;justify-content:center;z-index:2000;">
            <div style="background:#111b21;border-radius:16px;width:96%;max-width:560px;height:82vh;max-height:680px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.7);">
                <div style="background:#1f2c34;padding:10px 16px;display:flex;align-items:center;gap:12px;border-bottom:1px solid rgba(255,255,255,0.06);flex-shrink:0;">
                    <div style="width:40px;height:40px;border-radius:50%;background:#2a3942;display:flex;align-items:center;justify-content:center;font-size:1.1em;flex-shrink:0;">👤</div>
                    <div style="flex:1;min-width:0;">
                        <div id="chatModalTitle" style="color:#e9edef;font-size:0.97em;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"></div>
                        <div style="color:#8696a0;font-size:0.75em;">Ticket: <span id="chatModalTicket" style="color:#53bdeb;font-family:monospace;"></span></div>
                    </div>
                    <button onclick="closeChatModal()" style="background:none;border:none;color:#8696a0;font-size:1.3em;cursor:pointer;padding:6px;flex-shrink:0;">&times;</button>
                </div>
                <div id="chatMessages" style="flex:1;overflow-y:auto;padding:12px 10px;display:flex;flex-direction:column;gap:2px;background:#0b141a;"></div>
                <div style="background:#1f2c34;padding:8px 12px;display:flex;align-items:flex-end;gap:8px;border-top:1px solid rgba(255,255,255,0.06);flex-shrink:0;">
                    <div style="flex:1;background:#2a3942;border-radius:24px;padding:9px 16px;display:flex;align-items:flex-end;min-height:44px;">
                        <textarea id="chatReplyInput" placeholder="Escribe un mensaje" rows="1"
                            style="flex:1;background:transparent;border:none;outline:none;color:#d1d7db;font-size:0.95em;resize:none;overflow-y:hidden;max-height:110px;height:22px;font-family:inherit;line-height:22px;padding:0;display:block;width:100%;"
                            onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendChatReply();}"
                            oninput="_resizeChatTA(this)"></textarea>
                    </div>
                    <button id="chatCloseBtn" onclick="closeTicketFromModal()" title="Cerrar ticket"
                        style="width:44px;height:44px;flex-shrink:0;background:rgba(220,38,38,0.22);border:1px solid rgba(220,38,38,0.45);border-radius:50%;color:#fca5a5;font-size:0.95em;cursor:pointer;">🔒</button>
                    <button onclick="sendChatReply()" title="Enviar"
                        style="width:44px;height:44px;flex-shrink:0;background:#00a884;border:none;border-radius:50%;color:white;font-size:1.1em;cursor:pointer;">➤</button>
                </div>
                <div id="chatReplyMsg" style="font-size:0.8em;min-height:20px;text-align:center;padding:2px 12px 5px;background:#1f2c34;color:#8696a0;"></div>
            </div>
        </div>

        <!-- Modal: QR -->
        <div class="modal" id="qrModal">
            <div class="modal-content">
                <h3>📱 Conectar WhatsApp</h3>
                <p style="color:#cbd5e1;margin-bottom:8px;">Escanea el código QR desde tu WhatsApp</p>
                <div class="qr-loading" id="qrLoading">
                    <div class="spinner"></div>
                    <p class="spinner-text" id="qrStatus">Iniciando sesión...<br><small>Por favor espera unos segundos</small></p>
                </div>
                <img id="qrImage" class="qr-image" src="" alt="QR Code" style="display:none;">
                <p id="qrExpireMsg" style="display:none;color:#94a3b8;font-size:0.8em;margin-top:6px;">⏱️ El QR se renueva automáticamente</p>
                <div id="qrError" style="display:none;color:#ef4444;padding:16px 0;">
                    ❌ No se pudo obtener el QR.<br>
                    <button onclick="_retryQr()" style="margin-top:12px;padding:8px 20px;background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);color:#93c5fd;border-radius:8px;cursor:pointer;font-size:0.9em;">🔄 Reintentar</button>
                </div>
                <button class="modal-close" onclick="closeQrModal()">✖ Cerrar</button>
            </div>
        </div>

        <div class="toast" id="toast"></div>

        <script>
            const token = localStorage.getItem('token');
            const userStr = localStorage.getItem('user');

            // ── Auth helper: 401 → redirigir a login ─────────────
            function _checkUnauth(res) {
                if (res.status === 401) {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                    return true;
                }
                return false;
            }

            // ── Auth & init ──────────────────────────────────────
            window.addEventListener('DOMContentLoaded', () => {
                if (!token) { window.location.href = '/login'; return; }
                _loadSidebarUser();
                switchSection('estado');
                requestNotificationPermission();
                loadStatus();
                loadParkedList();
                loadSchedList();
                loadVersion();
                setInterval(loadStatus, 5000);
                setInterval(loadParkedList, 15000);
                setInterval(_pollDisconnect, 8000);
            });

            function _loadSidebarUser() {
                if (userStr) {
                    try {
                        const u = JSON.parse(userStr);
                        const nameEl   = document.getElementById('sidebarUserName');
                        const avatarEl = document.getElementById('userAvatar');
                        if (nameEl) nameEl.textContent = u.full_name || u.username || 'Usuario';
                        if (avatarEl) avatarEl.textContent = (u.full_name || u.username || 'U').charAt(0).toUpperCase();
                        return;
                    } catch(e) {}
                }
                fetch('/api/auth/me', { headers: { 'Authorization': `Bearer ${token}` } })
                    .then(r => r.json()).then(u => {
                        const nameEl   = document.getElementById('sidebarUserName');
                        const avatarEl = document.getElementById('userAvatar');
                        if (nameEl) nameEl.textContent = u.full_name || u.username || 'Usuario';
                        if (avatarEl) avatarEl.textContent = (u.full_name || u.username || 'U').charAt(0).toUpperCase();
                    }).catch(() => {});
            }

            // ── User dropdown ────────────────────────────────────
            let _userMenuOpen = false;
            function toggleUserMenu() {
                _userMenuOpen = !_userMenuOpen;
                const menu    = document.getElementById('userMenu');
                const chevron = document.getElementById('userChevron');
                menu.style.display = _userMenuOpen ? 'block' : 'none';
                if (chevron) chevron.classList.toggle('open', _userMenuOpen);
            }

            // ── Section switch ───────────────────────────────────
            function switchSection(id) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                const section = document.getElementById(id);
                if (section) section.classList.add('active');
                const cap = id.charAt(0).toUpperCase() + id.slice(1);
                const navEl = document.getElementById('nav' + cap);
                if (navEl) navEl.classList.add('active');
                if (id === 'feriados')  { loadHolidays(); }
                if (id === 'bloqueados') { loadBlocklist(); }
            }

            // ── Toast ────────────────────────────────────────────
            let _toastTimer;
            function showToast(msg, type = 'success') {
                const t = document.getElementById('toast');
                clearTimeout(_toastTimer);
                t.textContent = msg;
                t.className = 'toast ' + type + ' show';
                _toastTimer = setTimeout(() => t.classList.remove('show'), 3500);
            }

            // ── Status / notifications ───────────────────────────
            let lastConnectedStatus = null;

            function requestNotificationPermission() {
                if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
            }

            async function _pollDisconnect() {
                try {
                    const res = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                    const s = await res.json();
                    if (lastConnectedStatus === true && s.connected === false) {
                        if ('Notification' in window && Notification.permission === 'granted') {
                            new Notification('🤖 WA-BOT', { body: '⚠️ El bot se ha desconectado de WhatsApp', tag: 'bot-disconnect' });
                        }
                    }
                    lastConnectedStatus = s.connected;
                } catch(e) {}
            }

            window.loadStatus = async function loadStatus() {
                try {
                    const res = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                    if (!res.ok) { if (res.status === 403) { window.location.href = '/login'; } return; }
                    const s = await res.json();
                    lastConnectedStatus = s.connected;

                    document.getElementById('waIcon').textContent   = s.connected ? '🟢' : '🔴';
                    document.getElementById('waStatus').textContent  = s.connected ? 'Conectado' : 'Desconectado';

                    if (!s.connected) {
                        document.getElementById('botIcon').textContent  = '🔴';
                        document.getElementById('botStatus').textContent = 'Desconectado';
                    } else if (s.paused) {
                        document.getElementById('botIcon').textContent  = '⏸️';
                        document.getElementById('botStatus').textContent = 'Pausado';
                    } else {
                        document.getElementById('botIcon').textContent  = '▶️';
                        document.getElementById('botStatus').textContent = 'Activo';
                    }

                    document.getElementById('hoursIcon').textContent   = s.off_hours ? '🕐' : '✅';
                    document.getElementById('hoursStatus').textContent  = s.off_hours ? 'Fuera' : 'Normal';
                    document.getElementById('solutionName').textContent = s.solution_name || '—';

                    const toggleBtn = document.getElementById('toggleBtn');
                    if (s.paused) {
                        toggleBtn.textContent = '▶️ Activar Bot';
                        toggleBtn.classList.remove('active'); toggleBtn.classList.add('paused');
                    } else {
                        toggleBtn.textContent = '⏸️ Pausar Bot';
                        toggleBtn.classList.add('active'); toggleBtn.classList.remove('paused');
                    }

                    const waBtn = document.getElementById('waBtn');
                    if (s.connected) {
                        waBtn.textContent = '✅ WhatsApp Conectado';
                        waBtn.disabled = true; waBtn.classList.add('connected');
                    } else {
                        waBtn.textContent = '🔴 Conectar WhatsApp';
                        waBtn.disabled = false; waBtn.classList.remove('connected');
                    }
                } catch(e) { console.error('[STATUS]', e); }
            }

            async function toggleBot() {
                const btn = document.getElementById('toggleBtn');
                if (!btn || btn.disabled) return;
                btn.disabled = true;
                const origText = btn.textContent;
                btn.textContent = '⏳ Cambiando...';
                try {
                    const res = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                    const s   = await res.json();
                    const ep  = s.paused ? '/bot/resume' : '/bot/pause';
                    const r   = await fetch(ep, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
                    if (r.ok) await loadStatus();
                    else btn.textContent = origText;
                } catch(e) { btn.textContent = origText; }
                finally { btn.disabled = false; }
            }

            async function closeHumanModeFromUserPanel() {
                const input = document.getElementById('humanModePhoneUser');
                const msg   = document.getElementById('humanModeMsgUser');
                const phone = (input?.value || '').trim();
                if (!phone) { msg.textContent = '❌ Ingresá un número/chat'; msg.style.color = '#ef4444'; return; }
                try {
                    const res = await fetch('/api/human-mode/close', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: phone })
                    });
                    const data = await res.json();
                    if (!res.ok) { msg.textContent = '❌ ' + (data.detail || 'Error'); msg.style.color = '#ef4444'; return; }
                    if (data.closed) {
                        msg.textContent = `✅ Chat ${data.phone_number} volvió a modo bot`;
                        msg.style.color = '#86efac';
                        loadParkedList();
                    } else {
                        msg.textContent = 'ℹ️ ' + (data.detail || 'Sin cambios');
                        msg.style.color = '#93c5fd';
                    }
                } catch(e) { msg.textContent = '❌ Error de conexión'; msg.style.color = '#ef4444'; }
            }

            async function loadParkedList() {
                const container = document.getElementById('parkedListUser');
                if (!container) return;
                try {
                    const res  = await fetch('/api/human-mode/list', { headers: { 'Authorization': `Bearer ${token}` } });
                    const data = await res.json();
                    if (!Array.isArray(data) || data.length === 0) {
                        container.innerHTML = '<div style="color:#86efac;font-size:0.88em;">✅ No hay números en espera</div>'; return;
                    }
                    const rows = data.map(item => {
                        const started = item.handoff_started_at ? new Date(item.handoff_started_at + 'Z').toLocaleString('es-AR') : '—';
                        const state   = item.current_state === 'WAITING_AGENT' ? '⏳ Esperando operador' : '👤 Con operador';
                        const ticket  = item.ticket_id || '—';
                        return `<tr style="border-bottom:1px solid rgba(226,232,240,0.07);">
                            <td style="padding:9px 8px;"><button onclick="openChatModal('${item.phone_number}','${ticket}','user')" style="background:none;border:none;color:#93c5fd;font-family:monospace;font-size:0.88em;cursor:pointer;text-decoration:underline;padding:0;">${item.phone_number}</button></td>
                            <td style="padding:9px 8px;color:#94a3b8;font-size:0.82em;">${ticket}</td>
                            <td style="padding:9px 8px;color:#94a3b8;font-size:0.82em;">${state}</td>
                            <td style="padding:9px 8px;color:#94a3b8;font-size:0.78em;">${started}</td>
                            <td style="padding:9px 8px;">
                                <button onclick="openChatModal('${item.phone_number}','${ticket}','user')" style="padding:5px 9px;background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);color:#93c5fd;border-radius:6px;cursor:pointer;font-size:0.78em;margin-right:4px;">💬 Chat</button>
                                <button onclick="releaseParkedUser('${item.phone_number}',this)" style="padding:5px 9px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);color:#86efac;border-radius:6px;cursor:pointer;font-size:0.78em;">🔓 Liberar</button>
                            </td>
                        </tr>`;
                    }).join('');
                    container.innerHTML = `<table style="width:100%;border-collapse:collapse;">
                        <thead><tr style="background:rgba(30,41,59,0.5);">
                            <th style="padding:9px 8px;text-align:left;color:#cbd5e1;font-size:0.82em;">Número</th>
                            <th style="padding:9px 8px;text-align:left;color:#cbd5e1;font-size:0.82em;">Ticket</th>
                            <th style="padding:9px 8px;text-align:left;color:#cbd5e1;font-size:0.82em;">Estado</th>
                            <th style="padding:9px 8px;text-align:left;color:#cbd5e1;font-size:0.82em;">Inicio</th>
                            <th style="padding:9px 8px;text-align:left;color:#cbd5e1;font-size:0.82em;">Acciones</th>
                        </tr></thead>
                        <tbody>${rows}</tbody>
                    </table>`;
                } catch(e) {
                    container.innerHTML = '<div style="color:#ef4444;font-size:0.88em;">❌ Error al cargar lista</div>';
                }
            }

            async function releaseParkedUser(phone, btn) {
                btn.disabled = true; btn.textContent = '⏳';
                try {
                    const res  = await fetch('/api/human-mode/close', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: phone })
                    });
                    const data = await res.json();
                    if (data.closed) loadParkedList();
                    else { btn.disabled = false; btn.textContent = '🔓 Liberar'; }
                } catch(e) { btn.disabled = false; btn.textContent = '🔓 Liberar'; }
            }

            // ── Scheduled messages ───────────────────────────────
""" + _scheduled_messages_shared_js() + """
            let _schedEditId = null;

            const _userSchedConfig = {
                url: '/api/scheduled-messages',
                listId: 'schedList',
                errorText: 'Error al cargar mensajes programados',
                checkUnauth: _checkUnauth,
                actions: {
                    editFn: 'editSched',
                    deleteFn: 'deleteSched'
                },
                modalId: 'schedModal',
                titleId: 'schedModalTitle',
                nameId: 'schedName',
                phoneId: 'schedPhone',
                timeId: 'schedTime',
                messageId: 'schedMsg',
                feedbackId: 'schedModalMsg'
            };

            function _setUserSchedEditId(value) { _schedEditId = value; }
            async function loadSchedList() { return _loadScheduledMessagesList(_userSchedConfig); }
            function openSchedModal(sm) { _openScheduledMessagesModal(_userSchedConfig, sm, _setUserSchedEditId); }
            function closeSchedModal() { _closeScheduledMessagesModal(_userSchedConfig, _setUserSchedEditId); }
            async function saveSchedMsg() { return _saveScheduledMessage(_userSchedConfig, _schedEditId, () => { closeSchedModal(); loadSchedList(); }); }
            async function toggleSched(id) { return _toggleScheduledMessage(_userSchedConfig, id, loadSchedList); }
            async function editSched(id) { return _editScheduledMessage(_userSchedConfig, id, openSchedModal); }
            async function deleteSched(id) { return _deleteScheduledMessage(_userSchedConfig, id, loadSchedList); }

            // ── Chat Modal ───────────────────────────────────────
            let _chatModalPhone  = '';
            let _chatMsgPollTimer = null;

            function _resizeChatTA(el) {
                el.style.height = '22px';
                const maxH = 22 * 4;
                el.style.height    = Math.min(maxH, el.scrollHeight) + 'px';
                el.style.overflowY = el.scrollHeight > maxH ? 'auto' : 'hidden';
            }

            function openChatModal(phone, ticket, panel) {
                _chatModalPhone = phone;
                document.getElementById('chatModalTitle').textContent  = phone;
                document.getElementById('chatModalTicket').textContent = ticket;
                document.getElementById('chatMessages').innerHTML = '<div style="color:#8696a0;text-align:center;padding:30px;">Cargando mensajes...</div>';
                const ta = document.getElementById('chatReplyInput');
                ta.value = ''; ta.style.height = '22px'; ta.style.overflowY = 'hidden';
                document.getElementById('chatReplyMsg').textContent = '';
                document.getElementById('chatModal').style.display = 'flex';
                loadChatMessages();
                _chatMsgPollTimer = setInterval(loadChatMessages, 8000);
            }
            function closeChatModal() {
                if (_chatMsgPollTimer) { clearInterval(_chatMsgPollTimer); _chatMsgPollTimer = null; }
                document.getElementById('chatModal').style.display = 'none';
                _chatModalPhone = '';
            }

            async function loadChatMessages() {
                if (!_chatModalPhone) return;
                try {
                    const res  = await fetch(`/api/human-mode/messages/${encodeURIComponent(_chatModalPhone)}`, { headers: { 'Authorization': `Bearer ${token}` } });
                        const data = await res.json();
                        const box  = document.getElementById('chatMessages');
                        const msgs = Array.isArray(data) ? data : (data.messages || []);
                        if (!msgs || !msgs.length) {
                            box.innerHTML = '<div style="color:#8696a0;text-align:center;padding:30px;font-size:0.9em;">Sin mensajes disponibles</div>'; return;
                        }
                        const sorted     = [...msgs].sort((a,b) => a.timestamp - b.timestamp);
                    const wasAtBottom = box.scrollHeight - box.scrollTop <= box.clientHeight + 60;
                    box.innerHTML = sorted.map(m => {
                        const t = m.timestamp ? new Date(m.timestamp*1000).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}) : '';
                        if (m.from_me) return `<div style="display:flex;justify-content:flex-end;margin:2px 0;"><div style="background:#005c4b;border-radius:8px 2px 8px 8px;padding:7px 12px 5px;max-width:78%;color:#e9edef;font-size:0.9em;word-break:break-word;">${m.body||'<i style="color:#8696a0">[sin texto]</i>'}<div style="font-size:0.68em;color:#8adfcc;text-align:right;margin-top:3px;">${t}</div></div></div>`;
                        return `<div style="display:flex;justify-content:flex-start;margin:2px 0;"><div style="background:#202c33;border-radius:2px 8px 8px 8px;padding:7px 12px 5px;max-width:78%;color:#e9edef;font-size:0.9em;word-break:break-word;">${m.body||'<i style="color:#8696a0">[sin texto]</i>'}<div style="font-size:0.68em;color:#8696a0;text-align:right;margin-top:3px;">${t}</div></div></div>`;
                    }).join('');
                    if (wasAtBottom) box.scrollTop = box.scrollHeight;
                } catch(e) { document.getElementById('chatMessages').innerHTML = '<div style="color:#ef4444;text-align:center;padding:20px;">Error al cargar mensajes</div>'; }
            }

            async function sendChatReply() {
                const input = document.getElementById('chatReplyInput');
                const msg   = document.getElementById('chatReplyMsg');
                const text  = (input.value || '').trim();
                if (!text || !_chatModalPhone) return;
                input.disabled = true;
                try {
                    const res = await fetch('/api/human-mode/reply', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: _chatModalPhone, text })
                    });
                    if (res.ok) {
                        input.value = ''; input.style.height = '22px'; input.style.overflowY = 'hidden';
                        msg.textContent = '✅ Enviado'; msg.style.color = '#8adfcc';
                        setTimeout(() => { msg.textContent = ''; }, 2000);
                        setTimeout(loadChatMessages, 800);
                    } else { msg.textContent = '❌ Error al enviar'; msg.style.color = '#ef4444'; }
                } catch(e) { msg.textContent = '❌ Error de conexión'; msg.style.color = '#ef4444'; }
                finally { input.disabled = false; input.focus(); }
            }

            async function closeTicketFromModal() {
                if (!_chatModalPhone) return;
                const reply = document.getElementById('chatReplyInput').value.trim();
                const btn   = document.getElementById('chatCloseBtn');
                btn.disabled = true; btn.textContent = '⏳';
                try {
                    const res  = await fetch('/api/human-mode/close', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: _chatModalPhone, operator_reply: reply })
                    });
                    const data = await res.json();
                    if (data.closed) { closeChatModal(); loadParkedList(); }
                } finally { btn.disabled = false; btn.textContent = '🔒'; }
            }

            // ── WA Connect / QR ──────────────────────────────────
            let _qrPollTimer    = null;
            let _connPollTimer  = null;
            let _qrRefreshTimer = null;
            let _qrLastUpdateAt  = 0;
            let _lastConnectKickAt = 0;

            async function _fetchAndShowQr() {
                try {
                    const qrRes = await fetch('/qr?ts=' + Date.now());
                    if (qrRes.ok) {
                        const blob = await qrRes.blob();
                        const url  = URL.createObjectURL(blob);
                        document.getElementById('qrImage').src = url;
                        document.getElementById('qrImage').style.display = 'block';
                        document.getElementById('qrExpireMsg').style.display = 'block';
                        document.getElementById('qrLoading').style.display = 'none';
                        _qrLastUpdateAt = Date.now();
                        const st = document.getElementById('qrStatus');
                        if (st) st.innerHTML = 'QR listo para escanear<br><small>Se renueva automáticamente</small>';
                        return true;
                    }
                    if (qrRes.status === 404 || qrRes.status === 503) {
                        const st = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                        if (st.ok) { const s = await st.json(); if (s.connected) { _closeQrSuccess(); return true; } }
                    }
                } catch(e) {}
                return false;
            }

            function _retryQr() {
                document.getElementById('qrError').style.display = 'none';
                document.getElementById('qrLoading').style.display = 'flex';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Solicitando nuevo QR...<br><small>Por favor espera</small>';
                fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } }).catch(() => {});
                _startQrPhase1(token);
            }

            function _startQrPhase1(tok) {
                if (_qrPollTimer)    { clearInterval(_qrPollTimer);    _qrPollTimer    = null; }
                if (_qrRefreshTimer) { clearInterval(_qrRefreshTimer); _qrRefreshTimer = null; }
                let attempts = 0;
                _qrPollTimer = setInterval(async () => {
                    attempts++;
                    const st = document.getElementById('qrStatus');
                    if (st) st.innerHTML = `Esperando QR... (${Math.round(attempts*0.8)}s)<br><small>Conectando con WhatsApp</small>`;
                    if (attempts > 450) {
                        clearInterval(_qrPollTimer); _qrPollTimer = null;
                        document.getElementById('qrLoading').style.display = 'none';
                        document.getElementById('qrError').style.display = 'block';
                        return;
                    }
                    const ok = await _fetchAndShowQr();
                    if (ok) {
                        clearInterval(_qrPollTimer); _qrPollTimer = null;
                        _startConnectPoll(tok);
                        _qrRefreshTimer = setInterval(async () => {
                            const img = document.getElementById('qrImage');
                            if (!img || img.style.display === 'none') return;
                            const ok2 = await _fetchAndShowQr();
                            if (!ok2 || (Date.now() - _qrLastUpdateAt) > 45000) {
                                if ((Date.now() - _lastConnectKickAt) > 90000) {
                                    _lastConnectKickAt = Date.now();
                                    fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${tok}` } }).catch(() => {});
                                }
                            }
                        }, 30000);
                    }
                }, 800);
            }

            function toggleWhatsApp() {
                const btn = document.getElementById('waBtn');
                if (btn && btn.disabled) return;
                if (btn) { btn.disabled = true; btn.textContent = '⏳ Conectando...'; }
                if (lastConnectedStatus === true) {
                    fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } }).catch(() => {});
                    setTimeout(() => { if (btn) { btn.disabled = false; btn.textContent = '🟢 Reconectar WhatsApp'; } loadStatus(); }, 5000);
                    return;
                }
                _openQrModal();
                fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } }).catch(() => {});
                _startQrPhase1(token);
                if (btn) btn.disabled = false;
            }

            function _startConnectPoll(tok) {
                if (_connPollTimer) { clearInterval(_connPollTimer); _connPollTimer = null; }
                let connAttempts = 0;
                _connPollTimer = setInterval(async () => {
                    connAttempts++;
                    if (connAttempts > 300) { clearInterval(_connPollTimer); _connPollTimer = null; return; }
                    try {
                        const r = await fetch('/status', { headers: { 'Authorization': `Bearer ${tok}` } });
                        if (!r.ok) return;
                        const s = await r.json();
                        if (s.connected) { clearInterval(_connPollTimer); _connPollTimer = null; _closeQrSuccess(); }
                    } catch(e) {}
                }, 2000);
            }

            function _closeQrSuccess() {
                closeQrModal();
                const btn = document.getElementById('waBtn');
                if (btn) { btn.textContent = '✅ WhatsApp Conectado'; btn.disabled = true; btn.classList.add('connected'); }
                let toast = document.getElementById('waToast');
                if (!toast) { toast = document.createElement('div'); toast.id = 'waToast'; toast.className = 'wa-toast'; document.body.appendChild(toast); }
                toast.textContent = '✅ WhatsApp conectado exitosamente';
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 4000);
                loadStatus();
            }

            function _openQrModal() {
                document.getElementById('qrLoading').style.display = 'flex';
                document.getElementById('qrImage').style.display = 'none';
                document.getElementById('qrImage').src = '';
                document.getElementById('qrExpireMsg').style.display = 'none';
                document.getElementById('qrError').style.display = 'none';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Iniciando sesión...<br><small>Por favor espera unos segundos</small>';
                document.getElementById('qrModal').classList.add('show');
            }

            function closeQrModal() {
                if (_qrPollTimer)    { clearInterval(_qrPollTimer);    _qrPollTimer    = null; }
                if (_connPollTimer)  { clearInterval(_connPollTimer);  _connPollTimer  = null; }
                if (_qrRefreshTimer) { clearInterval(_qrRefreshTimer); _qrRefreshTimer = null; }
                document.getElementById('qrModal').classList.remove('show');
                document.getElementById('qrLoading').style.display = 'flex';
                document.getElementById('qrImage').style.display = 'none';
                document.getElementById('qrImage').src = '';
                document.getElementById('qrExpireMsg').style.display = 'none';
                document.getElementById('qrError').style.display = 'none';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Iniciando sesión...<br><small>Por favor espera unos segundos</small>';
                const waBtn = document.getElementById('waBtn');
                if (waBtn) waBtn.disabled = false;
                setTimeout(() => loadStatus(), 500);
            }

            // ── Calendar / Feriados ──────────────────────────────
            let calDate    = new Date();
            let _savedHols = [];
            let _savedSet  = new Set();
            let _selSet    = new Set();

            const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
            const WDAYS  = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];

            function calPrev()  { calDate.setMonth(calDate.getMonth()-1); renderCalendar(); }
            function calNext()  { calDate.setMonth(calDate.getMonth()+1); renderCalendar(); }
            function calToday() { calDate = new Date(); renderCalendar(); }

            function fmtDate(d)      { return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); }
            function fmtParts(y,m,d) { return y+'-'+String(m).padStart(2,'0')+'-'+String(d).padStart(2,'0'); }
            function fmtHuman(s)     { if(!s) return ''; const [y,m,d]=s.split('-'); return d+'/'+m+'/'+y; }

            function renderCalendar() {
                const yr      = calDate.getFullYear();
                const mo      = calDate.getMonth();
                const titleEl = document.getElementById('calTitle');
                if (titleEl) titleEl.textContent = MONTHS[mo] + ' ' + yr;
                const todayStr = fmtDate(new Date());
                const grid = document.getElementById('calGrid');
                if (!grid) return;
                grid.innerHTML = '';
                WDAYS.forEach((d,i) => { const h = document.createElement('div'); h.className = 'cal-hdr'+(i===0||i===6?' wknd':''); h.textContent = d; grid.appendChild(h); });
                const firstDow = new Date(yr,mo,1).getDay();
                const daysInMo = new Date(yr,mo+1,0).getDate();
                for(let i=0;i<firstDow;i++) { const e=document.createElement('div'); e.className='cal-cell empty'; grid.appendChild(e); }
                for(let d=1;d<=daysInMo;d++) {
                    const ds     = fmtParts(yr,mo+1,d);
                    const dow    = new Date(yr,mo,d).getDay();
                    const isWkd  = dow===0||dow===6;
                    const inDB   = _savedSet.has(ds);
                    const inSel  = _selSet.has(ds);
                    const cell   = document.createElement('div');
                    let cls = 'cal-cell'+(isWkd?' wknd':'')+(ds===todayStr?' today':'');
                    if(inDB&&inSel)       cls+=' selected';
                    else if(!inDB&&inSel) cls+=' pending';
                    else if(inDB&&!inSel) cls+=' removing';
                    cell.className = cls;
                    cell.textContent = d;
                    if(inDB&&inSel)        cell.title = (_savedHols.find(h=>h.date===ds)?.name||'Feriado guardado');
                    else if(!inDB&&inSel)  cell.title = 'Nuevo feriado — pendiente de guardar';
                    else if(inDB&&!inSel)  cell.title = 'Se eliminará al guardar';
                    cell.onclick = () => { if(_selSet.has(ds)) _selSet.delete(ds); else _selSet.add(ds); renderCalendar(); updatePendingBadge(); };
                    grid.appendChild(cell);
                }
            }

            function updatePendingBadge() {
                const toAdd = [..._selSet].filter(d=>!_savedSet.has(d)).length;
                const toDel = [..._savedSet].filter(d=>!_selSet.has(d)).length;
                const total = toAdd + toDel;
                const badge = document.getElementById('pendingBadge');
                const text  = document.getElementById('pendingText');
                if (total > 0) {
                    badge?.classList.remove('hidden');
                    const parts = [];
                    if(toAdd>0) parts.push(`+${toAdd} por agregar`);
                    if(toDel>0) parts.push(`-${toDel} por eliminar`);
                    if(text) text.textContent = parts.join('  ·  ');
                } else { badge?.classList.add('hidden'); }
            }

            async function loadHolidays() {
                try {
                    const res = await fetch('/api/holidays', { headers: { 'Authorization': `Bearer ${token}` } });
                    if (!res.ok) throw new Error();
                    _savedHols = await res.json();
                    _savedHols.sort((a,b) => a.date.localeCompare(b.date));
                    _savedSet  = new Set(_savedHols.map(h=>h.date));
                    _selSet    = new Set(_savedSet);
                    updatePendingBadge(); renderCalendar(); renderHolidayList();
                } catch(e) {
                    const el = document.getElementById('holidaysList');
                    if(el) el.innerHTML = '<div class="empty-state">❌ Error al cargar feriados</div>';
                }
            }

            function renderHolidayList() {
                const el = document.getElementById('holidaysList');
                if (!el) return;
                if (!_savedHols.length) { el.innerHTML = '<div class="empty-state">📭 No hay feriados guardados</div>'; return; }
                el.innerHTML = _savedHols.map(h => `
                    <div class="holiday-row">
                        <div class="holiday-info">
                            <span class="holiday-date">📅 ${fmtHuman(h.date)}</span>
                            <span class="holiday-name">${h.name||'Feriado'}</span>
                        </div>
                        <button class="btn btn-danger btn-sm" onclick="quickDelete(${h.id},'${h.date}')">🗑️</button>
                    </div>`).join('');
            }

            function cancelHolidays() {
                _selSet = new Set(_savedSet);
                renderCalendar(); updatePendingBadge();
                showToast('↺ Cambios descartados', 'info');
            }

            async function saveHolidays() {
                const toAdd = [..._selSet].filter(d=>!_savedSet.has(d));
                const toDel = [..._savedSet].filter(d=>!_selSet.has(d));
                if (toAdd.length===0 && toDel.length===0) { showToast('Sin cambios pendientes','info'); return; }
                const btn = document.getElementById('saveHBtn');
                btn.disabled = true; btn.textContent = '⏳ Guardando...';
                let errors = 0;
                try {
                    for(const date of toDel) {
                        const h = _savedHols.find(h=>h.date===date);
                        if (!h) continue;
                        const r = await fetch('/api/holidays/'+h.id, { method:'DELETE', headers:{'Authorization':`Bearer ${token}`} });
                        if (!r.ok) errors++;
                    }
                    for(const date of toAdd) {
                        const r = await fetch('/api/holidays', { method:'POST', headers:{'Authorization':`Bearer ${token}`,'Content-Type':'application/json'}, body:JSON.stringify({date,name:'Feriado'}) });
                        if (!r.ok) errors++;
                    }
                    await loadHolidays();
                    if (errors > 0) showToast(`⚠️ Guardado con ${errors} error(es)`, 'error');
                    else showToast('✅ Feriados actualizados correctamente');
                } catch(e) { showToast('❌ Error de conexión', 'error'); }
                finally { btn.disabled = false; btn.textContent = '💾 Guardar Feriados'; }
            }

            async function quickDelete(id, date) {
                _selSet.delete(date);
                const r = await fetch('/api/holidays/'+id, { method:'DELETE', headers:{'Authorization':`Bearer ${token}`} });
                if (r.ok) { showToast('🗑️ Feriado eliminado'); await loadHolidays(); }
                else showToast('❌ Error al eliminar', 'error');
            }

            // ── Blocklist ────────────────────────────────────────
            let _blocklist = [];

            async function loadBlocklist() {
                try {
                    const res = await fetch('/api/blocklist', { headers: { 'Authorization': `Bearer ${token}` } });
                    if (!res.ok) throw new Error();
                    _blocklist = await res.json();
                    renderBlocklist();
                } catch(e) {
                    const el = document.getElementById('blocklistItems');
                    if(el) el.innerHTML = '<div class="empty-state">❌ Error al cargar la lista</div>';
                }
            }

            function renderBlocklist() {
                const el = document.getElementById('blocklistItems');
                if (!el) return;
                if (!_blocklist.length) { el.innerHTML = '<div class="empty-state">✅ No hay números bloqueados</div>'; return; }
                el.innerHTML = _blocklist.map(b => `
                    <div class="block-row">
                        <div class="block-info">
                            <span class="block-phone">📵 ${b.phone_number}</span>
                            ${b.reason ? `<span class="block-reason">${b.reason}</span>` : ''}
                        </div>
                        <button class="btn btn-danger btn-icon" onclick="unblock(${b.id},'${b.phone_number}')">🗑️ Desbloquear</button>
                    </div>`).join('');
            }

            async function saveBlock() {
                const phone  = document.getElementById('blPhone').value.trim();
                const reason = document.getElementById('blReason').value.trim();
                if (!phone) { showToast('Ingresá un número de teléfono','error'); return; }
                const btn = document.getElementById('saveBlBtn');
                btn.disabled = true; btn.textContent = '⏳ Bloqueando...';
                try {
                    const res = await fetch('/api/blocklist', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: phone, reason })
                    });
                    if (res.ok) { showToast('🚫 Número bloqueado'); clearBlockForm(); await loadBlocklist(); }
                    else { const err = await res.json(); showToast('❌ '+(err.detail||'Error al bloquear'),'error'); }
                } catch(e) { showToast('❌ Error de conexión','error'); }
                finally { btn.disabled = false; btn.textContent = '🚫 Bloquear'; }
            }

            async function unblock(id, phone) {
                if (!confirm('¿Desbloquear '+phone+'?')) return;
                try {
                    const res = await fetch('/api/blocklist/'+id, { method:'DELETE', headers:{'Authorization':`Bearer ${token}`} });
                    if (res.ok) { showToast('✅ Número desbloqueado'); await loadBlocklist(); }
                    else showToast('❌ Error al desbloquear','error');
                } catch(e) { showToast('❌ Error de conexión','error'); }
            }
            function clearBlockForm() { document.getElementById('blPhone').value = ''; document.getElementById('blReason').value = ''; }

            // ── Change Password Modal ────────────────────────────
            function openChangePwModal() {
                _userMenuOpen = false;
                document.getElementById('userMenu').style.display = 'none';
                document.getElementById('userChevron')?.classList.remove('open');
                document.getElementById('oldPw').value     = '';
                document.getElementById('newPw').value     = '';
                document.getElementById('confirmPw').value = '';
                document.getElementById('pwMsg').textContent = '';
                document.getElementById('changePwModal').classList.add('show');
            }
            function closeChangePwModal() { document.getElementById('changePwModal').classList.remove('show'); }

            async function savePassword() {
                const oldPw     = document.getElementById('oldPw').value;
                const newPw     = document.getElementById('newPw').value;
                const confirmPw = document.getElementById('confirmPw').value;
                const msgEl     = document.getElementById('pwMsg');
                if (!oldPw||!newPw||!confirmPw) { msgEl.style.color='#f87171'; msgEl.textContent='Completá todos los campos'; return; }
                if (newPw !== confirmPw)          { msgEl.style.color='#f87171'; msgEl.textContent='Las contraseñas no coinciden'; return; }
                if (newPw.length < 6)             { msgEl.style.color='#f87171'; msgEl.textContent='Mínimo 6 caracteres'; return; }
                const saveBtns = document.querySelectorAll('.pw-modal-content .btn-primary');
                saveBtns.forEach(b => { b.disabled = true; b.textContent = '⏳ Guardando...'; });
                try {
                    const res = await fetch('/api/auth/change-password', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ old_password: oldPw, new_password: newPw })
                    });
                    if (res.ok) {
                        msgEl.style.color = '#6ee7b7'; msgEl.textContent = '✅ Contraseña actualizada';
                        showToast('✅ Contraseña actualizada exitosamente');
                        setTimeout(() => closeChangePwModal(), 1500);
                    } else {
                        const err = await res.json();
                        msgEl.style.color = '#f87171'; msgEl.textContent = '❌ ' + (err.detail || 'Contraseña actual incorrecta');
                    }
                } catch(e) { msgEl.style.color='#f87171'; msgEl.textContent='❌ Error de conexión'; }
                finally { saveBtns.forEach(b => { b.disabled=false; b.textContent='💾 Guardar'; }); }
            }

            function logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.href = '/login'; }
            async function loadVersion() {
                try {
                    const res = await fetch('/version');
                    if (!res.ok) return;
                    const data = await res.json();
                    const el = document.getElementById('userPanelVersion');
                    if (el) el.textContent = data.version || '—';
                } catch(e) {}
            }

            let currentTickets = [];
            let currentChatPhone = "";
            let currentChatTicketId = "";

            async function loadTickets() {
                try {
                    const res = await fetch('/api/tickets/list', {
                        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token')}
                    });
                    if(res.ok) {
                        currentTickets = await res.json();
                        renderTickets();
                    }
                } catch(e) { console.error(e); }
            }

            function renderTickets() {
                const grid = document.getElementById('ticketsGrid');
                if(!grid) return;
                if(!currentTickets.length) {
                    grid.innerHTML = '<div class="empty-state">No hay tickets</div>';
                    return;
                }

                let html = '';
                currentTickets.forEach(t => {
                    let badgeColor = '#64748b';
                    if (t.status === 'pendiente') badgeColor = '#f59e0b';
                    if (t.status === 'confirmado') badgeColor = '#10b981';
                    if (t.status === 'cancelado') badgeColor = '#ef4444';
                    if (t.status === 'timeout')   badgeColor = '#ef4444';
                    if (t.status === 'cerrado')    badgeColor = '#3b82f6';

                    let statusLabel = t.status.toUpperCase();
                    if(t.is_deleted) statusLabel += ' (BORRADO por ' + (t.deleted_by || 'Unknown') + ')';

                    const schedBadge = t.has_scheduled_message ? '<span style="background: rgba(139,92,246,0.2); color: #c4b5fd; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-left: 8px;">⏳ Programado</span>' : '';

                    html += `
                        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(226,232,240,0.08);border-radius:12px;padding:16px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
                            <div style="flex:1;min-width:0;">
                                <div style="font-weight:600;color:#f1f5f9;font-size:0.95em;">${t.ticket_id || '-'} | Tel: ${t.phone_number} ${schedBadge}</div>
                                <div style="color:${badgeColor};font-weight:500;font-size:0.88em;margin-top:4px;">${statusLabel} | Origen: ${t.menu_breadcrumb || t.menu_section || '-'}</div>
                                <div style="font-size:0.75em;color:#64748b;margin-top:3px;">Abierto: ${t.opened_at ? new Date(t.opened_at).toLocaleString() : '-'}</div>
                            </div>
                            <div style="display:flex;gap:8px;flex-shrink:0;">
                                <button class="btn btn-secondary btn-sm" onclick="viewTicket('${t.id}')">Ver Chat</button>
                            </div>
                        </div>
                    `;
                });
                grid.innerHTML = html;
            }

            async function viewTicket(tid) {
                const t = currentTickets.find(x => x.id === tid);
                if(!t) return;

                currentChatPhone = t.phone_number;
                currentChatTicketId = tid;

                document.getElementById('ticketChatModalTitle').textContent = `Chat: ${t.phone_number} (${t.status})`;
                document.getElementById('ticketChatModalTicket').textContent = t.ticket_id || '-';
                document.getElementById('ticketChatMessages').innerHTML = '<div style="color:#94a3b8;text-align:center;padding:20px;">Cargando mensajes...</div>';
                document.getElementById('ticketChatModal').classList.add('show');

                let actionsHtml = '';
                if (!t.is_deleted) {
                    if (t.status === 'pendiente') {
                        actionsHtml += `<button class="btn btn-primary btn-sm" onclick="actionTicket('fin')">Fin</button>`;
                    }
                    if (t.status === 'timeout') {
                        actionsHtml += `<button class="btn btn-primary btn-sm" onclick="actionTicket('resume')">Retomar</button>`;
                    }
                }
                document.getElementById('ticketChatModalActions').innerHTML = actionsHtml;

                try {
                    const res = await fetch(`/api/human-mode/messages/${encodeURIComponent(t.phone_number)}`, {
                        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token')}
                    });
                    if(res.ok) {
                        const data = await res.json();
                        const msgs = Array.isArray(data) ? data : (data.messages || []);
                        let chtml = '';
                        if(!msgs || msgs.length === 0) {
                            chtml = '<div style="color:#94a3b8;text-align:center;padding:20px;">No hay mensajes recientes</div>';
                        } else {
                            msgs.forEach(m => {
                                const isBot = m.from_me || m.fromMe;
                                const align = isBot ? 'right' : 'left';
                                const bg = isBot ? 'rgba(59,130,246,0.2)' : 'rgba(30,41,59,0.8)';
                                const text = m.body || m.text || (typeof m === "string" ? m : JSON.stringify(m));
                                const escapedText = _escapeSchedMsgAttr(text);
                                chtml += `<div style="text-align:${align};margin-bottom:8px;display:flex;align-items:flex-start;justify-content:${isBot ? 'flex-end' : 'flex-start'};gap:8px;">
                                    ${!isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-top:8px;cursor:pointer;" title="Seleccionar mensaje para agendar">` : ''}
                                    <div style="display:inline-block;background:${bg};padding:8px 12px;border-radius:8px;max-width:80%;word-break:break-word;text-align:left;">
                                        ${text}
                                    </div>
                                    ${isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-top:8px;cursor:pointer;" title="Seleccionar mensaje para agendar">` : ''}
                                </div>`;
                            });
                        }
                        document.getElementById('ticketChatMessages').innerHTML = chtml;
                        const box = document.getElementById('ticketChatMessages');
                        box.scrollTop = box.scrollHeight;
                    } else {
                        document.getElementById('ticketChatMessages').innerHTML = '<div style="color:#94a3b8;text-align:center;">No se pudieron cargar los mensajes.</div>';
                    }
                } catch(e) {
                    document.getElementById('ticketChatMessages').innerHTML = '<div style="color:#94a3b8;text-align:center;">Error cargando mensajes.</div>';
                }
            }

            function closeTicketChatModal() { document.getElementById('ticketChatModal').classList.remove('show'); }

            function _escapeSchedMsgAttr(text) {
                const tempDiv = document.createElement('div');
                tempDiv.textContent = text || '';
                return tempDiv.innerHTML.replace(/"/g, '&quot;');
            }

            function _getSelectedSchedChatText(containerSelector) {
                const checkboxes = document.querySelectorAll(`${containerSelector} .msg-cb:checked`);
                if (!checkboxes.length) return '';
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = Array.from(checkboxes).map(cb => cb.value).join('\\n\\n');
                return tempDiv.textContent.trim();
            }

            async function actionTicket(action) {
                if(action === 'delete' && !confirm("¿Seguro que quieres borrar este ticket?")) return;
                try {
                    const res = await fetch('/api/tickets/action', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: JSON.stringify({ action: action, id: currentChatTicketId })
                    });
                    if(res.ok) {
                        closeTicketChatModal();
                        loadTickets();
                    } else {
                        alert("Error ejecutando accion");
                    }
                } catch(e){ console.error(e); }
            }

            function openTicketScheduleModal() {
                document.getElementById('ticketSchedPhone').value = currentChatPhone;
                document.getElementById('ticketSchedName').value = '';
                document.getElementById('ticketSchedTime').value = '';
                document.getElementById('ticketSchedMessage').value = _getSelectedSchedChatText('#ticketChatMessages');
                document.getElementById('ticketScheduleModal').classList.add('show');
            }

            function closeTicketScheduleModal() { document.getElementById('ticketScheduleModal').classList.remove('show'); }

            async function saveTicketScheduledMessage() {
                const phone = document.getElementById('ticketSchedPhone').value;
                const name = document.getElementById('ticketSchedName').value;
                const time = document.getElementById('ticketSchedTime').value;
                const msg = document.getElementById('ticketSchedMessage').value;
                let send_time = '';
                let send_date = null;
                if (time) {
                    const parts = time.split('T');
                    send_date = parts[0] || null;
                    send_time = parts[1] || '';
                }
                
                if(!name || !send_time || !msg) { alert("Completar todos los campos"); return; }
                
                try {
                    const res = await fetch('/api/scheduled-messages', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: JSON.stringify({
                            name: name,
                            phone_number: phone,
                            send_time: send_time,
                            send_date: send_date,
                            message: msg,
                            days_of_week: "1,2,3,4,5,6,7",
                            is_active: true
                        })
                    });
                    if(res.ok) {
                        closeTicketScheduleModal();
                        loadTickets(); // refresh to show scheduled message badge
                        loadSchedList();
                        showToast("Mensaje agendado");
                    }
                } catch(e) { console.error(e); }
            }

            // Hook loadTickets into switchSection if section is tickets
            const originalSwitchSection = window.switchSection || function(){};
            window.switchSection = function(sectionId, el) {
                // update navigation UI if using elements
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                if(el) el.classList.add('active');
                else {
                    const selector = document.querySelector(`.nav-item[onclick*="'${sectionId}'"]`);
                    if(selector) selector.classList.add('active');
                }
                // hide all sections
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                
                // show target
                const target = document.getElementById(sectionId + 'Section') || document.getElementById(sectionId);
                if(target) target.classList.add('active');
                
                if(sectionId === 'tickets') { loadTickets(); }
                else if (sectionId === 'programados') { loadSchedList(); }
                else originalSwitchSection(sectionId, el);
            };

            </script>
    </body>
    </html>
    """
def get_user_config_page() -> str:
    """Página de configuración para usuarios (feriados, bloqueados, contraseña)"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configuración - ChatBot WA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
                color: #e2e8f0;
            }
            .layout { display: flex; min-height: 100vh; }

            /* SIDEBAR */
            .sidebar {
                width: 220px;
                background: rgba(15, 23, 42, 0.97);
                border-right: 1px solid rgba(226,232,240,0.1);
                padding: 28px 0;
                position: fixed; top:0; left:0; height:100vh;
                display: flex; flex-direction: column; gap: 4px;
                z-index: 10;
            }
            .sidebar-brand {
                padding: 0 20px 24px;
                border-bottom: 1px solid rgba(226,232,240,0.08);
                margin-bottom: 12px;
            }
            .sidebar-brand h2 {
                font-size: 1.15em;
                font-weight: 700;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .sidebar-brand p { color: #64748b; font-size: 0.8em; margin-top: 2px; }
            .nav-item {
                display: flex; align-items: center; gap: 10px;
                padding: 11px 20px;
                color: #94a3b8; cursor: pointer;
                font-size: 0.95em; font-weight: 500;
                border-left: 3px solid transparent;
                transition: all 0.2s;
            }
            .nav-item:hover { color: #e2e8f0; background: rgba(59,130,246,0.07); }
            .nav-item.active { color: #60a5fa; border-left-color: #3b82f6; background: rgba(59,130,246,0.12); }
            .nav-back {
                margin-top: auto; padding: 20px;
                border-top: 1px solid rgba(226,232,240,0.08);
            }
            .btn-back {
                width: 100%; padding: 10px;
                background: rgba(239,68,68,0.1);
                border: 1px solid rgba(244,63,94,0.4);
                color: #fca5a5; border-radius: 8px;
                cursor: pointer; font-size: 0.9em; font-weight: 500;
                transition: background 0.2s;
            }
            .btn-back:hover { background: rgba(239,68,68,0.2); }

            /* MAIN */
            .main { margin-left: 220px; padding: 36px 32px; flex: 1; }
            .page-header { margin-bottom: 28px; }
            .page-header h1 {
                font-size: 1.7em; font-weight: 700;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .page-header p { color: #64748b; font-size: 0.9em; margin-top: 4px; }

            /* SECTIONS */
            .section { display: none; }
            .section.active { display: block; }

            /* CARD */
            .card {
                background: rgba(18,24,40,0.85);
                border: 1px solid rgba(226,232,240,0.08);
                border-radius: 16px; padding: 28px;
                margin-bottom: 24px;
            }
            .card h2 { font-size: 1.1em; color: #f1f5f9; margin-bottom: 20px; font-weight: 600; }
            .card-footer {
                display: flex; gap: 12px; justify-content: flex-end;
                margin-top: 20px; padding-top: 20px;
                border-top: 1px solid rgba(226,232,240,0.08);
            }

            /* BUTTONS */
            .btn {
                padding: 10px 22px; border: none; border-radius: 8px;
                font-size: 0.9em; font-weight: 600; cursor: pointer;
                transition: all 0.2s;
            }
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                color: white;
            }
            .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(59,130,246,0.35); }
            .btn-primary:disabled { opacity: 0.55; cursor: not-allowed; transform: none; }
            .btn-secondary {
                background: rgba(226,232,240,0.08);
                border: 1px solid rgba(226,232,240,0.15);
                color: #94a3b8;
            }
            .btn-secondary:hover { background: rgba(226,232,240,0.13); }
            .btn-danger {
                background: rgba(239,68,68,0.12);
                border: 1px solid rgba(244,63,94,0.4);
                color: #f87171;
            }
            .btn-danger:hover { background: rgba(239,68,68,0.22); }
            .btn-sm { padding: 5px 12px; font-size: 0.82em; }
            .btn-icon { padding: 5px 9px; font-size: 0.85em; }

            /* FORM */
            .form-group { margin-bottom: 16px; }
            label { display: block; color: #cbd5e1; font-size: 0.88em; font-weight: 500; margin-bottom: 6px; }
            input[type="text"], input[type="email"], input[type="password"], input[type="date"], select, textarea {
                width: 100%; padding: 10px 13px;
                background: rgba(30,41,59,0.6);
                border: 1px solid rgba(226,232,240,0.12);
                border-radius: 8px; color: #f1f5f9; font-size: 0.93em;
                transition: border-color 0.2s;
            }
            input:focus, select:focus, textarea:focus {
                outline: none; border-color: rgba(59,130,246,0.5);
            }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
            @media (max-width: 640px) { .form-row { grid-template-columns: 1fr; } }

            /* TOAST */
            .toast {
                position: fixed; bottom: 28px; right: 28px;
                padding: 14px 20px; border-radius: 10px;
                font-size: 0.9em; font-weight: 500;
                transform: translateY(80px); opacity: 0;
                transition: all 0.3s; z-index: 999;
                max-width: 340px;
            }
            .toast.show { transform: translateY(0); opacity: 1; }
            .toast.success { background: rgba(16,185,129,0.18); border: 1px solid rgba(16,185,129,0.4); color: #6ee7b7; }
            .toast.error   { background: rgba(239,68,68,0.18); border: 1px solid rgba(244,63,94,0.4); color: #fca5a5; }
            .toast.info    { background: rgba(59,130,246,0.18); border: 1px solid rgba(59,130,246,0.4); color: #93c5fd; }

            /* HOLIDAYS TWO-COLUMN LAYOUT */
            .hol-layout {
                display: flex; gap: 24px; align-items: flex-start;
            }
            .hol-cal-col { flex: 0 0 auto; width: 440px; max-width: 100%; }
            .hol-list-col { flex: 1 1 0; min-width: 240px; }
            .hol-list-col #holidaysList { max-height: 480px; overflow-y: auto; }
            @media (max-width: 900px) {
                .hol-layout { flex-direction: column; }
                .hol-cal-col { width: 100%; }
            }

            /* CALENDAR */
            .cal-wrap {
                background: rgba(30,41,59,0.5);
                border: 1px solid rgba(226,232,240,0.1);
                border-radius: 12px; padding: 20px; margin-bottom: 4px;
            }
            .cal-header {
                display: flex; align-items: center; justify-content: space-between;
                margin-bottom: 18px;
            }
            .cal-title { font-size: 1.1em; font-weight: 600; color: #f1f5f9; }
            .cal-nav { display: flex; gap: 6px; }
            .cal-btn {
                padding: 5px 13px; background: rgba(59,130,246,0.12);
                border: 1px solid rgba(59,130,246,0.25);
                color: #93c5fd; border-radius: 7px; cursor: pointer;
                font-size: 0.88em; font-weight: 600; transition: background 0.2s;
            }
            .cal-btn:hover { background: rgba(59,130,246,0.25); }
            .cal-grid {
                display: grid; grid-template-columns: repeat(7, 1fr);
                gap: 7px;
            }
            .cal-hdr {
                text-align: center; font-size: 0.78em; font-weight: 700;
                color: #64748b; padding: 5px 0;
            }
            .cal-hdr.wknd { color: #f472b6; }
            .cal-cell {
                aspect-ratio: 1; display: flex; align-items: center;
                justify-content: center; border-radius: 8px;
                background: rgba(15,23,42,0.5);
                border: 1px solid rgba(226,232,240,0.1);
                font-size: 0.88em; font-weight: 600; color: #cbd5e1;
                cursor: pointer; transition: all 0.18s;
            }
            .cal-cell.empty { background: transparent; border-color: transparent; cursor: default; }
            .cal-cell:not(.empty):not(.selected):not(.pending):hover {
                background: rgba(59,130,246,0.2);
                border-color: rgba(59,130,246,0.35);
                color: #93c5fd;
            }
            .cal-cell.wknd { color: #f472b6; }
            .cal-cell.wknd:not(.selected):not(.pending):hover { background: rgba(244,114,182,0.15); border-color: rgba(244,114,182,0.3); }
            /* Saved holiday (in DB) = blue gradient */
            .cal-cell.selected {
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                border-color: rgba(59,130,246,0.6);
                color: #fff; font-weight: 700;
            }
            /* Pending new (not yet saved) = amber */
            .cal-cell.pending {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                border-color: rgba(245,158,11,0.6);
                color: #fff; font-weight: 700;
            }
            /* To be removed (in DB but deselected) = red strikethrough */
            .cal-cell.removing {
                background: rgba(239,68,68,0.18);
                border-color: rgba(244,63,94,0.45);
                color: #f87171; text-decoration: line-through;
            }
            .cal-cell.today {
                outline: 2px solid rgba(99,102,241,0.8);
                outline-offset: 2px;
            }
            .cal-legend {
                display: flex; flex-wrap: wrap; gap: 12px;
                margin-top: 14px; padding-top: 14px;
                border-top: 1px solid rgba(226,232,240,0.08);
                font-size: 0.8em; color: #64748b;
            }
            .cal-legend span { display: flex; align-items: center; gap: 5px; }
            .leg-dot {
                width: 13px; height: 13px; border-radius: 4px; display: inline-block;
            }
            .pending-badge {
                display: inline-flex; align-items: center; gap: 6px;
                padding: 7px 14px;
                background: rgba(245,158,11,0.15);
                border: 1px solid rgba(245,158,11,0.4);
                border-radius: 8px; font-size: 0.87em; color: #fcd34d;
                margin-bottom: 16px;
            }
            .pending-badge.hidden { display: none; }
            .holiday-row {
                display: flex; align-items: center; justify-content: space-between;
                padding: 10px 14px; background: rgba(59,130,246,0.06);
                border: 1px solid rgba(59,130,246,0.15);
                border-radius: 9px; margin-bottom: 8px;
            }
            .holiday-info { display: flex; flex-direction: column; gap: 2px; }
            .holiday-date { font-size: 0.85em; color: #60a5fa; font-weight: 600; }
            .holiday-name { font-size: 0.93em; color: #f1f5f9; }
            .empty-state { text-align: center; padding: 32px; color: #475569; font-size: 0.9em; }

            /* BLOCKLIST */
            .block-row {
                display: flex; align-items: center; justify-content: space-between;
                padding: 11px 14px; background: rgba(30,41,59,0.4);
                border: 1px solid rgba(226,232,240,0.08);
                border-radius: 9px; margin-bottom: 8px;
            }
            .block-info { display: flex; flex-direction: column; gap: 2px; }
            .block-phone { font-size: 0.93em; color: #f1f5f9; font-weight: 600; }
            .block-reason { font-size: 0.82em; color: #64748b; }
            .block-actions { display: flex; gap: 6px; }
            .add-form {
                background: rgba(30,41,59,0.5); border: 1px solid rgba(226,232,240,0.1);
                border-radius: 12px; padding: 20px; margin-bottom: 20px;
            }
            .add-form h3 { font-size: 0.95em; color: #cbd5e1; margin-bottom: 14px; }

            /* TICKETS */
            .ticket-row {
                display: flex; align-items: center; justify-content: space-between;
                padding: 11px 14px; background: rgba(30,41,59,0.4);
                border: 1px solid rgba(226,232,240,0.08);
                border-radius: 9px; margin-bottom: 8px;
            }
            .ticket-info { display: flex; flex-direction: column; gap: 2px; }
            .ticket-id { font-size: 0.93em; color: #f1f5f9; font-weight: 600; }
            .ticket-status { font-size: 0.82em; color: #64748b; }
            .ticket-actions { display: flex; gap: 6px; }

            @media (max-width: 768px) {
                .sidebar { width: 100%; height: auto; position: relative; flex-direction: row; flex-wrap: wrap; padding: 12px; }
                .sidebar-brand { padding-bottom: 0; border-bottom: none; margin-bottom: 0; }
                .nav-back { margin-top: 0; padding: 0; border: none; }
                .main { margin-left: 0; padding: 20px 16px; }
                .nav-item { padding: 8px 12px; border-left: none; border-bottom: 3px solid transparent; }
                .nav-item.active { border-bottom-color: #3b82f6; border-left-color: transparent; }
            }
        </style>
    </head>
    <body>
    <div class="layout">
        <aside class="sidebar">
            <div class="sidebar-brand">
                <h2>⚙️ Configuración</h2>
                <p>Panel de Usuario</p>
            </div>
            <div class="nav-item active" onclick="switchSection('holidays', this)">📅 Feriados</div>
            <div class="nav-item" onclick="switchSection('blocklist', this)">🚫 Bloqueados</div>
            <div class="nav-item" onclick="switchSection('password', this)">🔐 Contraseña</div>
            <div class="nav-back">
                <button class="btn-back" onclick="window.location.href='/user-panel'">← Volver al Panel</button>
            </div>
        </aside>

        <main class="main">
            <div class="page-header">
                <h1>⚙️ Configuración</h1>
                <p>Administrá feriados, lista de bloqueados y tu contraseña</p>
            </div>

            <!-- ═══════════════  FERIADOS  ═══════════════ -->
            <div id="holidays" class="section active">
                <div class="hol-layout">
                    <!-- Columna izquierda: Calendario -->
                    <div class="card hol-cal-col">
                        <h2>📅 Calendario de Feriados</h2>
                        <p style="color:#64748b;font-size:0.88em;margin-bottom:16px;">
                            Hacé clic en un día para marcarlo como feriado. Los días marcados en
                            <strong style="color:#60a5fa;">azul</strong> ya están guardados;
                            en <strong style="color:#fcd34d;">amarillo</strong> están pendientes de guardar;
                            en <strong style="color:#f87171;">rojo tachado</strong> serán eliminados.
                            Sábados y domingos se muestran en <strong style="color:#f472b6;">rosa</strong>.
                        </p>

                        <div id="pendingBadge" class="pending-badge hidden">
                            ⚠️ <span id="pendingText">0 cambios pendientes</span>
                        </div>

                        <div class="cal-wrap">
                            <div class="cal-header">
                                <div class="cal-nav">
                                    <button class="cal-btn" onclick="calPrev()">◀ Ant</button>
                                    <button class="cal-btn" onclick="calToday()">Hoy</button>
                                    <button class="cal-btn" onclick="calNext()">Sig ▶</button>
                                </div>
                                <div class="cal-title" id="calTitle">—</div>
                            </div>
                            <div class="cal-grid" id="calGrid"></div>
                            <div class="cal-legend">
                                <span><div class="leg-dot" style="background:linear-gradient(135deg,#3b82f6,#06b6d4);"></div> Feriado guardado</span>
                                <span><div class="leg-dot" style="background:linear-gradient(135deg,#f59e0b,#d97706);"></div> Por guardar</span>
                                <span><div class="leg-dot" style="background:rgba(239,68,68,0.3);border:1px solid #f87171;"></div> Por eliminar</span>
                                <span><div class="leg-dot" style="background:transparent;outline:2px solid rgba(99,102,241,0.8);outline-offset:1px;"></div> Hoy</span>
                                <span><div class="leg-dot" style="background:rgba(15,23,42,0.5);border:1px solid rgba(226,232,240,0.1);"></div> <span style="color:#f472b6">Fin de semana</span></span>
                            </div>
                        </div>

                        <!-- Guardar / Cancelar -->
                        <div class="card-footer">
                            <button class="btn btn-secondary" onclick="cancelHolidays()">✖ Cancelar cambios</button>
                            <button class="btn btn-primary" id="saveHBtn" onclick="saveHolidays()">💾 Guardar Feriados</button>
                        </div>
                    </div>

                    <!-- Columna derecha: Lista resumen -->
                    <div class="card hol-list-col">
                        <h2>📋 Feriados Guardados</h2>
                        <div id="holidaysList"><div class="empty-state">Cargando...</div></div>
                    </div>
                </div>
            </div>

            <!-- ═══════════════  BLOQUEADOS  ═══════════════ -->
            <div id="blocklist" class="section">
                <!-- Agregar -->
                <div class="card">
                    <h2>🚫 Agregar a Lista de Bloqueados</h2>
                    <div class="add-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Número de teléfono (ej: 5491112345678)</label>
                                <input type="text" id="blPhone" placeholder="5491112345678">
                            </div>
                            <div class="form-group">
                                <label>Motivo (opcional)</label>
                                <input type="text" id="blReason" placeholder="Spam, molestia, etc.">
                            </div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-secondary" onclick="clearBlockForm()">✖ Cancelar</button>
                        <button class="btn btn-primary" id="saveBlBtn" onclick="saveBlock()">🚫 Bloquear Número</button>
                    </div>
                </div>

                <!-- Lista -->
                <div class="card">
                    <h2>📋 Números Bloqueados</h2>
                    <div id="blocklistItems"><div class="empty-state">Cargando...</div></div>
                </div>
            </div>

            <!-- ═══════════════  CONTRASEÑA  ═══════════════ -->
            <div id="password" class="section">
                <div class="card">
                    <h2>🔐 Cambiar Contraseña</h2>
                    <div class="form-group">
                        <label>Contraseña Actual</label>
                        <input type="password" id="oldPw" placeholder="Tu contraseña actual">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Contraseña Nueva</label>
                            <input type="password" id="newPw" placeholder="Mínimo 6 caracteres">
                        </div>
                        <div class="form-group">
                            <label>Confirmar Contraseña</label>
                            <input type="password" id="confirmPw" placeholder="Repetí la nueva contraseña">
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-secondary" onclick="clearPwForm()">✖ Cancelar</button>
                        <button class="btn btn-primary" id="savePwBtn" onclick="savePassword()">💾 Guardar Contraseña</button>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        const token = localStorage.getItem('token');

        // ── Auth check ──────────────────────────────────────────
        window.addEventListener('DOMContentLoaded', () => {
            if (!token) { window.location.href = '/login'; return; }
            switchSection('holidays', document.querySelector('.nav-item.active'));
        });

        // ── Secciones ───────────────────────────────────────────
        function switchSection(id, el) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            if (el) el.classList.add('active');
            if (id === 'holidays') { loadHolidays(); renderCalendar(); }
            if (id === 'blocklist') loadBlocklist();
        }

        // ── Toast ───────────────────────────────────────────────
        let _toastTimer;
        function showToast(msg, type = 'success') {
            const t = document.getElementById('toast');
            clearTimeout(_toastTimer);
            t.textContent = msg;
            t.className = 'toast ' + type + ' show';
            _toastTimer = setTimeout(() => t.classList.remove('show'), 3500);
        }

        // ══════════════════════════════════════════════════════
        //  CALENDARIO  —  click-to-toggle con diff-save
        // ══════════════════════════════════════════════════════
        let calDate      = new Date();
        let _savedHols   = [];        // [{id, date, name}] — cargado del servidor
        let _savedSet    = new Set(); // fechas actualmente en BD
        let _selSet      = new Set(); // fechas actualmente seleccionadas en UI

        const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                        'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
        const WDAYS  = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];

        function calPrev()  { calDate.setMonth(calDate.getMonth()-1); renderCalendar(); }
        function calNext()  { calDate.setMonth(calDate.getMonth()+1); renderCalendar(); }
        function calToday() { calDate = new Date(); renderCalendar(); }

        function fmtDate(d) {
            return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
        }
        function fmtParts(y,m,d) {
            return y+'-'+String(m).padStart(2,'0')+'-'+String(d).padStart(2,'0');
        }
        function fmtHuman(s) {
            if(!s) return '';
            const [y,m,d]=s.split('-'); return d+'/'+m+'/'+y;
        }

        function renderCalendar() {
            const yr = calDate.getFullYear();
            const mo = calDate.getMonth();
            const titleEl = document.getElementById('calTitle');
            if (titleEl) titleEl.textContent = MONTHS[mo] + ' ' + yr;

            const todayStr = fmtDate(new Date());
            const grid = document.getElementById('calGrid');
            if (!grid) return;
            grid.innerHTML = '';

            // Headers
            WDAYS.forEach((d,i) => {
                const h = document.createElement('div');
                h.className = 'cal-hdr' + (i===0||i===6?' wknd':'');
                h.textContent = d;
                grid.appendChild(h);
            });

            const firstDow = new Date(yr, mo, 1).getDay();
            const daysInMo = new Date(yr, mo+1, 0).getDate();

            for(let i=0; i<firstDow; i++) {
                const e=document.createElement('div'); e.className='cal-cell empty'; grid.appendChild(e);
            }

            for(let d=1; d<=daysInMo; d++) {
                const ds    = fmtParts(yr, mo+1, d);
                const dow   = new Date(yr,mo,d).getDay();
                const isWkd = dow===0||dow===6;
                const inDB  = _savedSet.has(ds);
                const inSel = _selSet.has(ds);
                const isToday = ds === todayStr;

                const cell = document.createElement('div');
                let cls = 'cal-cell';
                if(isWkd) cls += ' wknd';
                if(isToday) cls += ' today';

                // State classes
                if(inDB && inSel)      cls += ' selected';  // saved & still selected
                else if(!inDB && inSel) cls += ' pending';   // new, not yet saved
                else if(inDB && !inSel) cls += ' removing';  // was saved, now deselected
                // else: normal (neither saved nor selected)

                cell.className = cls;
                cell.textContent = d;

                // Tooltips
                if(inDB && inSel) cell.title = (_savedHols.find(h=>h.date===ds)?.name||'Feriado guardado');
                else if(!inDB && inSel) cell.title = 'Nuevo feriado — pendiente de guardar';
                else if(inDB && !inSel) cell.title = 'Se eliminará al guardar';
                else if(isWkd) cell.title = dow===6?'Sábado':'Domingo';

                // All days (including weekends) are clickable to toggle
                cell.onclick = () => {
                    if(_selSet.has(ds)) _selSet.delete(ds);
                    else _selSet.add(ds);
                    renderCalendar();
                    updatePendingBadge();
                };
                grid.appendChild(cell);
            }
        }

        function updatePendingBadge() {
            const toAdd = [..._selSet].filter(d=>!_savedSet.has(d)).length;
            const toDel = [..._savedSet].filter(d=>!_selSet.has(d)).length;
            const total = toAdd + toDel;
            const badge = document.getElementById('pendingBadge');
            const text  = document.getElementById('pendingText');
            if (total > 0) {
                if (badge) badge.classList.remove('hidden');
                const parts = [];
                if (toAdd > 0) parts.push(`+${toAdd} por agregar`);
                if (toDel > 0) parts.push(`-${toDel} por eliminar`);
                if (text) text.textContent = parts.join('  ·  ');
            } else {
                if (badge) badge.classList.add('hidden');
            }
        }

        // ── FERIADOS CRUD ───────────────────────────────────────
        async function loadHolidays() {
            try {
                const res = await fetch('/api/holidays', {headers:{'Authorization':`Bearer ${token}`}});
                if(!res.ok) throw new Error('HTTP '+res.status);
                _savedHols = await res.json();
                _savedHols.sort((a,b)=>a.date.localeCompare(b.date));
                _savedSet = new Set(_savedHols.map(h=>h.date));
                _selSet   = new Set(_savedSet); // start with same selection as saved
                updatePendingBadge();
                renderCalendar();
                renderHolidayList();
            } catch(e) {
                document.getElementById('holidaysList').innerHTML='<div class="empty-state">❌ Error al cargar feriados</div>';
            }
        }

        function renderHolidayList() {
            const el = document.getElementById('holidaysList');
            if(!_savedHols.length) {
                el.innerHTML='<div class="empty-state">📭 No hay feriados guardados</div>'; return;
            }
            el.innerHTML = _savedHols.map(h => `
                <div class="holiday-row">
                    <div class="holiday-info">
                        <span class="holiday-date">📅 ${fmtHuman(h.date)}</span>
                        <span class="holiday-name">${h.name||'Feriado'}</span>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="quickDelete(${h.id},'${h.date}')">🗑️</button>
                </div>
            `).join('');
        }

        function cancelHolidays() {
            _selSet = new Set(_savedSet);
            renderCalendar();
            updatePendingBadge();
            showToast('↺ Cambios descartados', 'info');
        }

        async function saveHolidays() {
            const toAdd = [..._selSet].filter(d=>!_savedSet.has(d));
            const toDel = [..._savedSet].filter(d=>!_selSet.has(d));

            if(toAdd.length===0 && toDel.length===0) {
                showToast('Sin cambios pendientes', 'info'); return;
            }

            const btn = document.getElementById('saveHBtn');
            btn.disabled=true; btn.textContent='⏳ Guardando...';
            let errors=0;
            try {
                // DELETE removed holidays
                for(const date of toDel) {
                    const h = _savedHols.find(h=>h.date===date);
                    if(!h) continue;
                    const r = await fetch('/api/holidays/'+h.id, {
                        method:'DELETE', headers:{'Authorization':`Bearer ${token}`}
                    });
                    if(!r.ok) errors++;
                }
                // POST new holidays
                for(const date of toAdd) {
                    const r = await fetch('/api/holidays', {
                        method:'POST',
                        headers:{'Authorization':`Bearer ${token}`,'Content-Type':'application/json'},
                        body: JSON.stringify({date, name:'Feriado'})
                    });
                    if(!r.ok) errors++;
                }
                await loadHolidays();
                if(errors>0) showToast(`⚠️ Guardado con ${errors} error(es)`, 'error');
                else showToast('✅ Feriados actualizados correctamente');
            } catch(e) {
                showToast('❌ Error de conexión', 'error');
            } finally {
                btn.disabled=false; btn.textContent='💾 Guardar Feriados';
            }
        }

        async function quickDelete(id, date) {
            // Remove from selSet and savedSet immediately (visual + API)
            _selSet.delete(date);
            const r = await fetch('/api/holidays/'+id, {
                method:'DELETE', headers:{'Authorization':`Bearer ${token}`}
            });
            if(r.ok) {
                showToast('🗑️ Feriado eliminado');
                await loadHolidays();
            } else {
                showToast('❌ Error al eliminar', 'error');
            }
        }

        // ══════════════════════════════════════════════════════
        //  BLOCKLIST — CRUD
        // ══════════════════════════════════════════════════════
        let _blocklist = [];

        async function loadBlocklist() {
            try {
                const res = await fetch('/api/blocklist', { headers: { 'Authorization': `Bearer ${token}` } });
                if (!res.ok) throw new Error('HTTP ' + res.status);
                _blocklist = await res.json();
                renderBlocklist();
            } catch(e) {
                document.getElementById('blocklistItems').innerHTML = '<div class="empty-state">❌ Error al cargar la lista</div>';
            }
        }

        function renderBlocklist() {
            const el = document.getElementById('blocklistItems');
            if (!_blocklist.length) {
                el.innerHTML = '<div class="empty-state">✅ No hay números bloqueados</div>';
                return;
            }
            el.innerHTML = _blocklist.map(b => `
                <div class="block-row">
                    <div class="block-info">
                        <span class="block-phone">📵 ${b.phone_number}</span>
                        ${b.reason ? `<span class="block-reason">${b.reason}</span>` : ''}
                    </div>
                    <div class="block-actions">
                        <button class="btn btn-danger btn-icon" onclick="unblock(${b.id}, '${b.phone_number}')">🗑️ Desbloquear</button>
                    </div>
                </div>
            `).join('');
        }

        async function saveBlock() {
            const phone = document.getElementById('blPhone').value.trim();
            const reason = document.getElementById('blReason').value.trim();
            if (!phone) { showToast('Ingresá un número de teléfono', 'error'); return; }

            const btn = document.getElementById('saveBlBtn');
            btn.disabled = true; btn.textContent = '⏳ Bloqueando...';
            try {
                const res = await fetch('/api/blocklist', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone_number: phone, reason })
                });
                if (res.ok) {
                    showToast('🚫 Número bloqueado');
                    clearBlockForm();
                    await loadBlocklist();
                } else {
                    const err = await res.json();
                    showToast('❌ ' + (err.detail || 'Error al bloquear'), 'error');
                }
            } catch(e) {
                showToast('❌ Error de conexión', 'error');
            } finally {
                btn.disabled = false; btn.textContent = '🚫 Bloquear Número';
            }
        }

        async function unblock(id, phone) {
            if (!confirm('¿Desbloquear ' + phone + '?')) return;
            try {
                const res = await fetch('/api/blocklist/' + id, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    showToast('✅ Número desbloqueado');
                    await loadBlocklist();
                } else {
                    showToast('❌ Error al desbloquear', 'error');
                }
            } catch(e) {
                showToast('❌ Error de conexión', 'error');
            }
        }

        function clearBlockForm() {
            document.getElementById('blPhone').value = '';
            document.getElementById('blReason').value = '';
        }

        // ══════════════════════════════════════════════════════
        //  CONTRASEÑA
        // ══════════════════════════════════════════════════════
        async function savePassword() {
            const oldPw    = document.getElementById('oldPw').value;
            const newPw    = document.getElementById('newPw').value;
            const confirmPw = document.getElementById('confirmPw').value;

            if (!oldPw || !newPw || !confirmPw) { showToast('Completá todos los campos', 'error'); return; }
            if (newPw !== confirmPw) { showToast('Las contraseñas no coinciden', 'error'); return; }
            if (newPw.length < 6) { showToast('Mínimo 6 caracteres', 'error'); return; }

            const btn = document.getElementById('savePwBtn');
            btn.disabled = true; btn.textContent = '⏳ Guardando...';
            try {
                const res = await fetch('/api/auth/change-password', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ old_password: oldPw, new_password: newPw })
                });
                if (res.ok) {
                    showToast('✅ Contraseña actualizada correctamente');
                    clearPwForm();
                } else {
                    const err = await res.json();
                    showToast('❌ ' + (err.detail || 'Contraseña actual incorrecta'), 'error');
                }
            } catch(e) {
                showToast('❌ Error de conexión', 'error');
            } finally {
                btn.disabled = false; btn.textContent = '💾 Guardar Contraseña';
            }
        }

        function clearPwForm() {
            document.getElementById('oldPw').value = '';
            document.getElementById('newPw').value = '';
            document.getElementById('confirmPw').value = '';
        }
    
            // TICKETS LOGIC
            let currentTickets = [];
            let currentChatPhone = "";
            let currentChatTicketId = "";

            async function loadTickets() {
                try {
                    const res = await fetch('/api/tickets/list', {
                        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token')}
                    });
                    if(res.ok) {
                        currentTickets = await res.json();
                        renderTickets();
                    }
                } catch(e) { console.error(e); }
            }

            function renderTickets() {
                const grid = document.getElementById('ticketsGrid');
                if(!currentTickets.length) {
                    grid.innerHTML = '<div class="empty-state">No hay tickets</div>';
                    return;
                }
                
                let html = '';
                currentTickets.forEach(t => {
                    let badgeColor = '#64748b';
                    if (t.status === 'pendiente') badgeColor = '#f59e0b';
                    if (t.status === 'confirmado') badgeColor = '#10b981';
                    if (t.status === 'cancelado') badgeColor = '#ef4444';
                    if (t.status === 'timeout')   badgeColor = '#ef4444';
                    
                    let statusLabel = t.status.toUpperCase();
                    if(t.is_deleted) statusLabel += ' (BORRADO por ' + (t.deleted_by || 'Unknown') + ')';
                    
                    let schedBadge = t.has_scheduled_message ? '<span style="background: rgba(139,92,246,0.2); color: #c4b5fd; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-left: 8px;">⏳ Programado</span>' : '';

                    html += `
                        <div class="ticket-row">
                            <div class="ticket-info">
                                <div class="ticket-id">${t.ticket_id || '-'} | Tel: ${t.phone_number} ${schedBadge}</div>
                                <div class="ticket-status" style="color: ${badgeColor}; font-weight: 500;">
                                    ${statusLabel} | Origen: ${t.menu_section || '-'}
                                </div>
                                <div style="font-size: 0.75em; color: #64748b; margin-top: 4px;">
                                    Abierto: ${t.opened_at ? new Date(t.opened_at).toLocaleString() : '-'}
                                </div>
                            </div>
                            <div class="ticket-actions">
                                <button class="btn btn-secondary btn-sm" onclick="viewTicket('${t.id}')">Ver Chat</button>
                            </div>
                        </div>
                    `;
                });
                grid.innerHTML = html;
            }

            async function viewTicket(tid) {
                const t = currentTickets.find(x => x.id === tid);
                if(!t) return;
                
                currentChatPhone = t.phone_number;
                currentChatTicketId = tid;
                
                document.getElementById('chatModalTitle').textContent = `Chat: ${t.phone_number} (${t.status})`;
                document.getElementById('chatContent').innerHTML = '<div class="spinner-text">Cargando mensajes desde WAHA...</div>';
                document.getElementById('chatModal').classList.add('show');
                
                // Actions
                let actionsHtml = '';
                if (!t.is_deleted) {
                    if (t.status === 'pendiente') {
                        actionsHtml += `<button class="btn btn-primary btn-sm" onclick="actionTicket('fin')">Fin</button>`;
                    }
                    if (t.status === 'timeout') {
                        actionsHtml += `<button class="btn btn-primary btn-sm" onclick="actionTicket('resume')">Retomar</button>`;
                    }
                    actionsHtml += `<button class="btn btn-danger btn-sm" onclick="actionTicket('delete')">Borrar (Cancelar)</button>`;
                }
                document.getElementById('chatModalActions').innerHTML = actionsHtml;
                
                // fetch messages
                try {
                    const res = await fetch(`/api/human-mode/messages/${encodeURIComponent(t.phone_number)}`, {
                        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token')}
                    });
                    if(res.ok) {
                        const data = await res.json();
                        const msgs = Array.isArray(data) ? data : (data.messages || []);
                        let chtml = '';
                        if(!msgs || msgs.length === 0) {
                            chtml = '<div class="empty-state">No hay mensajes recientes en WAHA</div>';
                        } else {
                            // msgs is an array of Waha message objects
                            msgs.forEach(m => {
                                const isBot = m.from_me || m.fromMe;
                                const align = isBot ? 'right' : 'left';
                                const bg = isBot ? 'rgba(59,130,246,0.2)' : 'rgba(30,41,59,0.8)';
                                const text = m.body || m.text || (typeof m === "string" ? m : JSON.stringify(m));
                                const tempDiv = document.createElement('div');
                                tempDiv.textContent = text;
                                const escapedText = tempDiv.innerHTML.replace(/"/g, '&quot;');
                                chtml += `<div style="text-align: ${align}; margin-bottom: 8px; display: flex; align-items: center; justify-content: ${isBot ? 'flex-end' : 'flex-start'};">
                                    ${!isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-right:8px; cursor:pointer;" title="Seleccionar para recordatorio">` : ''}
                                    <div style="display: inline-block; background: ${bg}; padding: 8px 12px; border-radius: 8px; max-width: 80%; word-break: break-word; text-align: left;">
                                        ${text}
                                    </div>
                                    ${isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-left:8px; cursor:pointer;" title="Seleccionar para recordatorio">` : ''}
                                </div>`;
                            });
                        }
                        document.getElementById('chatContent').innerHTML = chtml;
                        document.getElementById('chatContent').scrollTop = document.getElementById('chatContent').scrollHeight;
                    } else {
                        document.getElementById('chatContent').innerHTML = '<div class="empty-state">No se pudieron cargar los mensajes.</div>';
                    }
                } catch(e) {
                    document.getElementById('chatContent').innerHTML = '<div class="empty-state">Error cargando mensajes.</div>';
                }
            }

            function closeChatModal() { document.getElementById('chatModal').classList.remove('show'); }

            async function actionTicket(action) {
                if(action === 'delete') {
                    if(!confirm("¿Seguro que quieres borrar este ticket?")) return;
                }
                try {
                    const res = await fetch('/api/tickets/action', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: JSON.stringify({ action: action, id: currentChatTicketId })
                    });
                    if(res.ok) {
                        closeChatModal();
                        loadTickets();
                    } else {
                        alert("Error ejecutando accion");
                    }
                } catch(e){ console.error(e); }
            }

            function openScheduleModal() {
                document.getElementById('schedPhone').value = currentChatPhone;
                document.getElementById('schedName').value = '';
                document.getElementById('schedTime').value = '';
                
                const checkboxes = document.querySelectorAll('#chatContent .msg-cb:checked');
                const selectedText = Array.from(checkboxes).map(cb => cb.value).join('\\n\\n');
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = selectedText;
                
                document.getElementById('schedMessage').value = tempDiv.textContent;
                document.getElementById('scheduleModal').classList.add('show');
            }

            function closeScheduleModal() { document.getElementById('scheduleModal').classList.remove('show'); }

            async function saveScheduledMessage() {
                const phone = document.getElementById('schedPhone').value;
                const name = document.getElementById('schedName').value;
                const time = document.getElementById('schedTime').value;
                const msg = document.getElementById('schedMessage').value;
                
                if(!name || !time || !msg) { alert("Completar todos los campos"); return; }
                
                try {
                    const res = await fetch('/api/scheduled-messages', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: JSON.stringify({
                            name: name,
                            phone_number: phone,
                            send_time: time,
                            message: msg,
                            days_of_week: "1,2,3,4,5,6,7",
                            is_active: true
                        })
                    });
                    if(res.ok) {
                        closeScheduleModal();
                        loadTickets(); // refresh to show scheduled message badge
                        showToast("Mensaje agendado");
                    }
                } catch(e) { console.error(e); }
            }

            // Hook loadTickets into switchSection if section is tickets
            const originalSwitchSection = window.switchSection || function(){};
            window.switchSection = function(sectionId, el) {
                // update navigation UI if using elements
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                if(el) el.classList.add('active');
                else {
                    const selector = document.querySelector(`.nav-item[onclick*="'${sectionId}'"]`);
                    if(selector) selector.classList.add('active');
                }
                // hide all sections
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                
                // show target
                const target = document.getElementById(sectionId + 'Section') || document.getElementById(sectionId);
                if(target) target.classList.add('active');
                
                if(sectionId === 'tickets') loadTickets();
                else originalSwitchSection(sectionId, el);
            };

            </script>
    </body>
    </html>
    """

def get_dashboard_page() -> str:
    """Dashboard admin completamente rediseñado"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Admin - ChatBot WA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
                color: #e2e8f0;
            }
            
            .sidebar {
                position: fixed;
                left: 0;
                top: 0;
                width: 250px;
                height: 100vh;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(226, 232, 240, 0.1);
                padding: 24px 0 120px 0;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            
            .sidebar-header {
                padding: 0 20px 30px;
                border-bottom: 1px solid rgba(226, 232, 240, 0.1);
                margin-bottom: 20px;
            }
            
            .sidebar-header h2 {
                font-size: 1.3em;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
            }
            
            .sidebar-header p {
                color: #94a3b8;
                font-size: 0.85em;
            }
            
            .nav-item {
                padding: 12px 20px;
                color: #cbd5e1;
                cursor: pointer;
                transition: all 0.3s ease;
                border-left: 3px solid transparent;
                margin: 4px 0;
            }
            
            .nav-item:hover {
                background: rgba(59, 130, 246, 0.1);
                color: #3b82f6;
            }
            
            .nav-item.active {
                background: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
                border-left-color: #3b82f6;
            }
            
            .sidebar-footer {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 16px;
                border-top: 1px solid rgba(226, 232, 240, 0.1);
                background: rgba(15, 23, 42, 0.95);
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .sidebar-user {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px;
                background: rgba(30, 41, 59, 0.4);
                border-radius: 10px;
                border: 1px solid rgba(226, 232, 240, 0.05);
            }

            .sidebar-user-avatar {
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                color: white;
                font-size: 0.85em;
            }

            .sidebar-user-info {
                flex: 1;
                text-align: left;
                overflow: hidden;
            }

            .sidebar-user-name {
                color: #f1f5f9;
                font-weight: 600;
                font-size: 0.9em;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .sidebar-user-role {
                color: #64748b;
                font-size: 0.75em;
            }

            .sidebar-logout-btn {
                width: 100%;
                padding: 8px;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.85em;
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                transition: all 0.3s ease;
            }

            .sidebar-logout-btn:hover {
                background: rgba(239, 68, 68, 0.2);
                border-color: rgba(239, 68, 68, 0.4);
            }
            
            .sidebar-footer-info {
                text-align: center;
                font-size: 0.8em;
            }
            
            .sidebar-footer .company {
                color: #475569;
                font-weight: 600;
                margin-bottom: 2px;
            }
            
            .sidebar-footer .version {
                color: #334155;
                font-size: 0.85em;
            }
            
            .main {
                margin-left: 250px;
                padding: 30px;
            }
            
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2em;
                font-weight: 700;
            }
            
            .logout-btn {
                padding: 8px 16px;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(244, 63, 94, 0.5);
                color: #fca5a5;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s ease;
            }
            
            .logout-btn:hover {
                background: rgba(239, 68, 68, 0.2);
            }
            
            .section {
                display: none;
            }
            
            .section.active {
                display: block;
                animation: fadeIn 0.3s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .card {
                background: rgba(18, 24, 40, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
            }
            
            .card h2 {
                font-size: 1.4em;
                margin-bottom: 20px;
                color: #f1f5f9;
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }
            
            .status-item {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            }
            
            .status-item-icon {
                font-size: 2.5em;
                margin-bottom: 8px;
            }
            
            .status-item-label {
                font-size: 0.85em;
                color: #94a3b8;
                margin-bottom: 8px;
            }
            
            .status-item-value {
                font-size: 1.8em;
                color: #f1f5f9;
                font-weight: 700;
            }

            .status-item-combo-title {
                font-size: 1.8em;
                color: #f1f5f9;
                font-weight: 700;
                margin-bottom: 12px;
            }

            .status-combo-indicators {
                display: flex;
                flex-direction: column;
                gap: 8px;
                align-items: center;
            }

            .status-combo-pill {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                min-width: 130px;
                padding: 8px 12px;
                border-radius: 999px;
                font-size: 0.95em;
                font-weight: 700;
                border: 1px solid transparent;
            }

            .status-combo-pill.on {
                color: #86efac;
                background: rgba(34, 197, 94, 0.12);
                border-color: rgba(34, 197, 94, 0.35);
            }

            .status-combo-pill.off {
                color: #fca5a5;
                background: rgba(239, 68, 68, 0.12);
                border-color: rgba(239, 68, 68, 0.35);
            }
            
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-size: 0.95em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
            }
            
            .btn-secondary {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                color: #93c5fd;
            }
            
            .btn-secondary:hover {
                background: rgba(59, 130, 246, 0.2);
            }
            
            .form-group {
                margin-bottom: 16px;
            }
            
            .form-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            label {
                display: block;
                color: #e2e8f0;
                font-weight: 500;
                margin-bottom: 6px;
                font-size: 0.95em;
            }
            
            input[type="text"],
            input[type="email"],
            input[type="time"],
            input[type="date"],
            select, textarea {
                width: 100%;
                padding: 10px 12px;
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.15);
                border-radius: 8px;
                color: #f1f5f9;
                font-size: 0.95em;
                font-family: inherit;
                transition: all 0.3s ease;
            }
            
            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: #3b82f6;
                background: rgba(30, 41, 59, 0.8);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            textarea {
                min-height: 300px;
                resize: vertical;
                font-family: monospace;
            }
            
            .buttons-group {
                display: flex;
                gap: 10px;
                margin-top: 16px;
                flex-wrap: wrap;
            }
            
            .message {
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 16px;
                display: none;
            }
            
            .message.show { display: block; }
            
            .message.success {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                color: #a7f3d0;
            }
            
            .message.error {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(244, 63, 94, 0.3);
                color: #fca5a5;
            }
            
            .calendar {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
            
            .calendar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .calendar-header h3 {
                color: #f1f5f9;
                font-size: 1.2em;
            }
            
            .calendar-grid {
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 8px;
            }
            
            .calendar-day-header {
                text-align: center;
                color: #94a3b8;
                font-weight: 600;
                padding: 8px;
                font-size: 0.85em;
            }
            
            .calendar-day {
                aspect-ratio: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.2s ease;
            }
            
            .calendar-day:hover {
                background: rgba(59, 130, 246, 0.2);
                border-color: rgba(59, 130, 246, 0.3);
            }
            
            .calendar-day.marked {
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                color: white;
                border-color: rgba(59, 130, 246, 0.5);
            }
            
            .calendar-day.other-month {
                color: #475569;
            }
            
            @media (max-width: 768px) {
                .sidebar {
                    width: 100%;
                    height: auto;
                    position: relative;
                    border-bottom: 1px solid rgba(226, 232, 240, 0.1);
                    border-right: none;
                }
                
                .main {
                    margin-left: 0;
                }
                
                .nav-item {
                    display: inline-block;
                    margin-right: 16px;
                }
            }

            /* Spinner QR */
            .qr-loading {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 30px 0;
            }
            .spinner {
                width: 56px;
                height: 56px;
                border: 5px solid rgba(59, 130, 246, 0.2);
                border-top-color: #3b82f6;
                border-radius: 50%;
                animation: spin 0.9s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
            .spinner-text {
                color: #94a3b8;
                margin-top: 16px;
                font-size: 0.9em;
                text-align: center;
                line-height: 1.5;
            }
            .btn-pause {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                color: white;
            }
            .btn-pause:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(245, 158, 11, 0.3);
            }
            .btn-connected {
                background: linear-gradient(135deg, #16a34a, #15803d) !important;
                opacity: 0.85;
                cursor: default !important;
            }
            .btn-connected:hover {
                transform: none !important;
                box-shadow: none !important;
            }
            .wa-toast {
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%) translateY(80px);
                background: #16a34a;
                color: white;
                padding: 14px 28px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 0.95em;
                z-index: 9999;
                opacity: 0;
                transition: transform 0.35s ease, opacity 0.35s ease;
                pointer-events: none;
            }
            .wa-toast.show {
                transform: translateX(-50%) translateY(0);
                opacity: 1;
            }

            /* ── Config Tabs ── */
            .config-tab-bar {
                display: flex;
                gap: 6px;
                margin-bottom: 24px;
                background: rgba(15, 23, 42, 0.7);
                padding: 5px;
                border-radius: 12px;
                border: 1px solid rgba(226, 232, 240, 0.08);
            }
            .config-tab {
                flex: 1;
                padding: 10px 16px;
                background: transparent;
                border: none;
                border-radius: 8px;
                color: #94a3b8;
                font-size: 0.92em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .config-tab:hover {
                color: #e2e8f0;
                background: rgba(59, 130, 246, 0.1);
            }
            .config-tab.active {
                background: rgba(59, 130, 246, 0.22);
                color: #60a5fa;
            }
            .config-tab-panel {
                display: none;
            }
            .config-tab-panel.active {
                display: block;
                animation: fadeIn 0.3s ease;
            }
            .btn-danger {
                background: rgba(239, 68, 68, 0.15);
                border: 1px solid rgba(239, 68, 68, 0.4);
                color: #fca5a5;
            }
            .btn-danger:hover {
                background: rgba(239, 68, 68, 0.25);
            }

            /* ── ESTILOS CALENDARIO AVANZADO ── */
            .hol-layout {
                display: grid;
                grid-template-columns: 1.2fr 0.8fr;
                gap: 24px;
                align-items: start;
            }
            @media (max-width: 992px) { .hol-layout { grid-template-columns: 1fr; } }
            
            .hol-cal-col { min-width: 0; }
            .hol-list-col { min-width: 0; position: sticky; top: 20px; max-height: calc(100vh - 40px); display: flex; flex-direction: column; overflow: hidden; }
            #holidaysList { overflow-y: auto; flex: 1; padding-right: 8px; margin-top: 10px; }

            .cal-wrap {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 16px;
                padding: 20px;
                user-select: none;
            }
            .cal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            .cal-title { font-size: 1.25em; font-weight: 700; color: #f1f5f9; text-transform: capitalize; }
            .cal-nav { display: flex; gap: 8px; }
            .cal-btn {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                color: #93c5fd;
                padding: 6px 12px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.85em;
                font-weight: 600;
                transition: all 0.2s;
            }
            .cal-btn:hover { background: rgba(59, 130, 246, 0.2); }
            
            .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
            .cal-hdr { text-align: center; color: #64748b; font-size: 0.75em; font-weight: 700; text-transform: uppercase; padding: 8px 0; }
            .cal-hdr.wknd { color: #f472b6; }
            
            .cal-cell {
                aspect-ratio: 1;
                background: rgba(15, 23, 42, 0.3);
                border: 1px solid rgba(226, 232, 240, 0.05);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 0.95em;
                color: #f1f5f9;
                cursor: pointer;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
            }
            .cal-cell:not(.empty):hover {
                transform: scale(1.08);
                z-index: 2;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                border-color: rgba(59, 130, 246, 0.4);
            }
            .cal-cell.empty { background: transparent; border: none; cursor: default; }
            .cal-cell.wknd { color: #f472b6; background: rgba(244, 114, 182, 0.05); }
            .cal-cell.today { outline: 2px solid rgba(99,102,241,0.8); outline-offset: 1px; }

            /* Estados del calendario */
            .cal-cell.selected {
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                border-color: #60a5fa;
                color: white;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            }
            .cal-cell.pending {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                border-color: #fbbf24;
                color: white;
                animation: pulse 2s infinite;
            }
            .cal-cell.removing {
                background: rgba(239, 68, 68, 0.15);
                border: 1px dashed #ef4444;
                color: #fca5a5;
                text-decoration: line-through;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.8; }
                100% { opacity: 1; }
            }

            .cal-legend { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 20px; font-size: 0.8em; color: #94a3b8; }
            .cal-legend span { display: flex; align-items: center; gap: 6px; }
            .leg-dot { width: 10px; height: 10px; border-radius: 3px; }

            .pending-badge {
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.3);
                color: #fbbf24;
                padding: 10px 16px;
                border-radius: 10px;
                margin-bottom: 16px;
                font-size: 0.88em;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .pending-badge.hidden { display: none; }

            /* Lista de feriados (derecha) */
            .holiday-row {
                background: rgba(30, 41, 59, 0.4);
                border: 1px solid rgba(226, 232, 240, 0.05);
                border-radius: 12px;
                padding: 12px 16px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.2s;
            }
            .holiday-row:hover { background: rgba(30, 41, 59, 0.6); border-color: rgba(226, 232, 240, 0.15); }
            .holiday-info { display: flex; flex-direction: column; gap: 2px; }
            .holiday-date { color: #f1f5f9; font-weight: 600; font-size: 0.95em; }
            .holiday-name { color: #94a3b8; font-size: 0.85em; }
            
            .btn-danger.btn-sm { padding: 4px 8px; font-size: 0.85em; }
            
            .card-footer { border-top: 1px solid rgba(226, 232, 240, 0.05); padding-top: 20px; margin-top: 20px; display: flex; gap: 12px; }
            .empty-state { text-align: center; color: #64748b; padding: 40px 20px; font-style: italic; font-size: 0.9em; }
            .btn-sm { padding: 6px 12px; font-size: 0.85em; }
            .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.75); align-items: center; justify-content: center; z-index: 1000; }
            .modal.show { display: flex; }
            .modal-content { background: rgba(18,24,40,0.97); border: 1px solid rgba(226,232,240,0.12); border-radius: 16px; padding: 32px; max-width: 640px; width: 95%; max-height: 90vh; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🤖 WA-BOT</h2>
                <p>Admin</p>
            </div>
            
            <div class="nav-item active" onclick="switchSection('status')">📊 Estado</div>
            <div class="nav-item" onclick="switchSection('ticketsAdmin')">🎫 Tickets</div>
            <div class="nav-item" onclick="switchSection('programadosAdmin')">🕐 Programados</div>
            <div class="nav-item" onclick="switchSection('holidays')">📅 Feriados</div>
            <div class="nav-item" onclick="switchSection('config')">⚙️ Configuración</div>
            
            <div class="sidebar-footer">
                <div class="sidebar-user" id="sidebarUserBox" style="display: none;">
                    <div class="sidebar-user-avatar" id="userAvatar">A</div>
                    <div class="sidebar-user-info">
                        <div class="sidebar-user-name" id="sidebarUserName">Admin</div>
                        <div class="sidebar-user-role">Administrador</div>
                    </div>
                </div>
                
                <button class="sidebar-logout-btn" onclick="logout()">
                    <span>🚪</span> Logout
                </button>
                
                <div class="sidebar-footer-info">
                    <div class="company" style="color: #64748b;">DOLAN SS</div>
                    <div class="version" id="dashboardVersion" style="color: #475569;">""" + _GIT_VERSION + """</div>
                </div>
            </div>
        </div>
        
        <div class="main">
            <div class="header">
                <h1>Dashboard Administrativo</h1>
            </div>
            
            <!-- ESTADO -->
            <div id="status" class="section active">
                <div class="card">
                    <h2>🎯 Estado del Sistema</h2>
                    <div class="status-grid">
                        <div class="status-item">
                            <div class="status-item-value status-item-combo-title">💬 / 🤖</div>
                            <div class="status-combo-indicators">
                                <div class="status-combo-pill off" id="waStatusPill">🔴 WA OFF</div>
                                <div class="status-combo-pill off" id="botStatusPill">🔴 Bot OFF</div>
                            </div>
                        </div>
                        <div class="status-item">
                            <div class="status-item-icon">📞</div>
                            <div class="status-item-label">Chats Hoy</div>
                            <div class="status-item-value" id="chatsToday">0</div>
                        </div>
                        <div class="status-item">
                            <div class="status-item-icon">🎫</div>
                            <div class="status-item-label">Tickets Abiertos</div>
                            <div class="status-item-value" id="openTicketsCount">0</div>
                        </div>
                        <div class="status-item">
                            <div class="status-item-icon" id="hoursIcon">✅</div>
                            <div class="status-item-label">Horarios</div>
                            <div class="status-item-value" id="hoursStatus">Normal</div>
                        </div>
                        <div class="status-item">
                            <div class="status-item-icon">⏱️</div>
                            <div class="status-item-label">Uptime WA</div>
                            <div class="status-item-value" id="waUptime">0s</div>
                        </div>
                    </div>
                    <span id="waStatusText" style="display:none;">Desconectado</span>
                    <button class="btn btn-primary" id="waBtn" onclick="toggleWhatsApp()">🔴 Conectar WhatsApp</button>
                    <button class="btn" id="pauseBtn" onclick="toggleBot()" style="margin-left:10px;">⏸️ Pausar Bot</button>
                </div>

                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <h2 style="margin-bottom:0;">⏸️ Números en Espera (Parking)</h2>
                        <button class="btn btn-secondary" onclick="loadAdminParkedList()" style="padding:8px 14px; font-size:0.9em;">🔄 Actualizar</button>
                    </div>
                    <div id="parkedListAdmin">
                        <div style="color:#94a3b8; font-size:0.9em;">Cargando...</div>
                    </div>
                </div>

            </div>

            <!-- ────── SECCIÓN TICKETS ADMIN ────── -->
            <div id="ticketsAdmin" class="section">
                <div style="margin-bottom: 20px;">
                    <h2 style="color: #f1f5f9; margin: 0;">🎫 Tickets</h2>
                    <p style="color: #94a3b8; margin-top: 6px; font-size: 0.9em;">Gestión de conversaciones y turnos derivados a operadores.</p>
                </div>
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="margin:0;">Listado de Tickets</h2>
                        <button class="btn btn-primary btn-sm" onclick="loadAdminTickets()">🔄 Refrescar</button>
                    </div>
                    <div id="adminTicketsGrid" style="display: flex; flex-direction: column; gap: 12px; max-height: 60vh; overflow-y: auto; padding-right: 10px;">
                        <div class="empty-state">Cargando tickets...</div>
                    </div>
                </div>
            </div>

            <div id="programadosAdmin" class="section">
                <div style="margin-bottom: 20px;">
                    <h2 style="color: #f1f5f9; margin: 0;">🕐 Mensajes Programados</h2>
                    <p style="color: #94a3b8; margin-top: 6px; font-size: 0.9em;">Listado general de envíos agendados, ordenado por próxima ejecución.</p>
                </div>
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; gap:12px; flex-wrap:wrap;">
                        <div>
                            <h2 style="margin:0;">Agenda de Mensajes</h2>
                            <p style="color:#94a3b8; margin-top:6px; font-size:0.88em;">Podés crear, editar, pausar o cancelar mensajes desde esta vista.</p>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button class="btn btn-secondary btn-sm" onclick="loadAdminSchedList()">🔄 Refrescar</button>
                            <button class="btn btn-primary btn-sm" onclick="openAdminSchedModal()">➕ Nuevo</button>
                        </div>
                    </div>
                    <div id="adminSchedList" style="max-height:62vh; overflow-y:auto; padding-right:8px;">
                        <div style="color:#94a3b8; font-size:0.88em;">Cargando...</div>
                    </div>
                </div>
            </div>

            <!-- Modal Chat Admin -->
            <div id="adminChatModal" class="modal">
                <div class="modal-content" style="max-width: 600px; width: 95%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(226,232,240,0.1); padding-bottom: 15px; margin-bottom: 15px;">
                        <h3 id="adminChatModalTitle" style="margin: 0;">Conversación</h3>
                        <button class="btn btn-secondary btn-sm" onclick="closeAdminChatModal()" style="margin: 0;">X</button>
                    </div>
                    <div id="adminChatContent" style="height: 350px; overflow-y: auto; text-align: left; background: rgba(15,23,42,0.5); padding: 15px; border-radius: 8px; font-size: 0.9em;"></div>
                    <div style="margin-top: 15px; display: flex; gap: 10px; justify-content: space-between; align-items: center;">
                        <div style="display:flex; flex-direction:column; gap:6px; align-items:flex-start;">
                            <div style="display: flex; gap: 10px;" id="adminChatModalActions"></div>
                            <div style="font-size:0.78em; color:#94a3b8;">Seleccioná mensajes del chat para copiarlos al agendado.</div>
                        </div>
                        <button class="btn btn-primary btn-sm" id="btnAdminSched" onclick="openAdminTicketScheduleModal()">Agendar Mensaje</button>
                    </div>
                </div>
            </div>

            <!-- Modal Agendar Admin Ticket -->
            <div id="adminTicketSchedModal" class="modal">
                <div class="modal-content">
                    <h3 style="margin-top:0;">Agendar Mensaje</h3>
                    <div class="form-group" style="text-align: left;">
                        <label>Teléfono</label>
                        <input type="text" id="adminSchedTicketPhone" readonly style="opacity: 0.7;">
                    </div>
                    <div class="form-group" style="text-align: left;">
                        <label>Nombre del Recordatorio</label>
                        <input type="text" id="adminSchedTicketName" placeholder="Ej: Recordatorio Turno">
                    </div>
                    <div class="form-group" style="text-align: left;">
                        <label>Fecha y Hora</label>
                        <input type="datetime-local" id="adminSchedTicketTime">
                    </div>
                    <div class="form-group" style="text-align: left;">
                        <label>Mensaje</label>
                        <textarea id="adminSchedTicketMessage" rows="4" placeholder="Contenido del mensaje..."></textarea>
                    </div>
                    <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                        <button class="btn btn-secondary" onclick="closeAdminTicketScheduleModal()">Cancelar</button>
                        <button class="btn btn-primary" onclick="saveAdminTicketScheduledMessage()">Guardar</button>
                    </div>
                </div>
            </div>
            
            <!-- USUARIOS (modales globales, el contenido está en config/sistema) -->
            
            <!-- MODAL CREAR USUARIO -->
            <div class="modal" id="createUserModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); align-items: center; justify-content: center; z-index: 1000;">
                <div style="background: rgba(18, 24, 40, 0.95); border: 1px solid rgba(226, 232, 240, 0.1); border-radius: 20px; padding: 40px; max-width: 500px; width: 90%;">
                    <h2 style="color: #f1f5f9; margin-bottom: 24px;">Crear Nuevo Usuario</h2>
                    <form onsubmit="createNewUser(event)">
                        <div class="form-group">
                            <label>Usuario</label>
                            <input type="text" id="newUsername" required placeholder="nombre_usuario">
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="newEmail" placeholder="usuario@example.com">
                        </div>
                        <div class="form-group">
                            <label>Contraseña</label>
                            <input type="password" id="newPassword" required placeholder="Contraseña segura">
                        </div>
                        <div class="form-group">
                            <label>Nombre Completo</label>
                            <input type="text" id="newFullName" placeholder="Nombre Completo">
                        </div>
                        <label style="display: flex; align-items: center; cursor: pointer; margin-bottom: 20px;">
                            <input type="checkbox" id="newIsAdmin" style="width: auto; margin-right: 8px;">
                            <span style="color: #cbd5e1;">Es administrador</span>
                        </label>
                        <div style="display: flex; gap: 12px;">
                            <button type="submit" class="btn btn-primary" style="flex: 1;">✅ Crear Usuario</button>
                            <button type="button" class="btn btn-secondary" onclick="closeCreateUserModal()" style="flex: 1;">❌ Cancelar</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- MODAL CAMBIAR CONTRASEÑA -->
            <div class="modal" id="changePasswordModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); align-items: center; justify-content: center; z-index: 1000;">
                <div style="background: rgba(18, 24, 40, 0.95); border: 1px solid rgba(226, 232, 240, 0.1); border-radius: 20px; padding: 40px; max-width: 500px; width: 90%;">
                    <h2 style="color: #f1f5f9; margin-bottom: 24px;" id="changePasswordTitle">Cambiar Contraseña</h2>
                    <form onsubmit="saveNewPassword(event)" id="changePasswordForm">
                        <input type="hidden" id="changePasswordUserId">
                        <div class="form-group">
                            <label>Nueva Contraseña</label>
                            <input type="password" id="newPasswordValue" required placeholder="Nueva contraseña" autocomplete="new-password">
                        </div>
                        <div class="form-group">
                            <label>Confirmar Contraseña</label>
                            <input type="password" id="confirmPasswordValue" required placeholder="Confirmar contraseña" autocomplete="new-password">
                        </div>
                        <div style="display: flex; gap: 12px;">
                            <button type="submit" class="btn btn-primary" style="flex: 1;">✅ Cambiar Contraseña</button>
                            <button type="button" class="btn btn-secondary" onclick="closeChangePasswordModal()" style="flex: 1;">❌ Cancelar</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- MODAL CONFIRMAR ELIMINACIÓN -->
            <div class="modal" id="deleteUserModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); align-items: center; justify-content: center; z-index: 1000;">
                <div style="background: rgba(18, 24, 40, 0.95); border: 1px solid rgba(226, 232, 240, 0.1); border-radius: 20px; padding: 40px; max-width: 500px; width: 90%; text-align: center;">
                    <h2 style="color: #f1f5f9; margin-bottom: 16px;">⚠️ Eliminar Usuario</h2>
                    <p style="color: #cbd5e1; margin-bottom: 24px;">¿Estás seguro de que deseas eliminar a <strong id="deleteUsernamePlaceholder"></strong>? Esta acción no se puede deshacer.</p>
                    <div style="display: flex; gap: 12px;">
                        <button onclick="confirmDeleteUser()" class="btn btn-primary" style="flex: 1; background: rgba(239, 68, 68, 0.1); border-color: rgba(244, 63, 94, 0.5); color: #fca5a5;">🗑️ Eliminar</button>
                        <button onclick="closeDeleteUserModal()" class="btn btn-secondary" style="flex: 1;">❌ Cancelar</button>
                    </div>
                </div>
            </div>
            
            <!-- CONFIGURACIÓN (panel con tabs) -->
            <div id="config" class="section">
                <div class="config-tab-bar">
                    <button class="config-tab active" onclick="switchConfigTab('chatbot', this)">📋 Chatbot</button>
                    <button class="config-tab" onclick="switchConfigTab('sistema', this)">⚙️ Sistema</button>
                    <button class="config-tab" onclick="switchConfigTab('usuarios', this)">👥 Usuarios</button>
                    <button class="config-tab" onclick="switchConfigTab('bloqueos', this)">🚫 Bloqueos</button>
                </div>

                <!-- ══ TAB: CHATBOT → Editor de Menú + Fuera de Hora ══ -->
                <div id="configTab-chatbot" class="config-tab-panel active">
                    <div class="card">
                        <h2>📋 Editor de Menú Principal</h2>
                        <div class="message" id="menuMessage"></div>
                        <form onsubmit="saveMenu(event)">
                            <div class="form-group">
                                <label>Contenido del Menú (Markdown)</label>
                                <textarea id="menuContent" placeholder="# Menú Principal..." style="min-height: 400px;"></textarea>
                            </div>
                            <div class="buttons-group">
                                <button type="submit" class="btn btn-primary">💾 Guardar Menú</button>
                                <button type="button" class="btn btn-secondary" onclick="resetMenuEditor()">↺ Deshacer Cambios</button>
                                <button type="button" class="btn btn-secondary" onclick="restoreMenuBackup()">⏮ Restaurar Versión Anterior</button>
                            </div>
                        </form>
                    </div>

                    <div class="card">
                        <h2>🕐 Mensaje Fuera de Hora</h2>
                        <div class="message" id="offhoursMessage"></div>
                        <form onsubmit="saveOffhours(event)">
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="offhoursEnabled" onchange="toggleOffhoursState()">
                                    ✓ Habilitar Fuera de Horario
                                </label>
                                <p style="color: #94a3b8; font-size: 0.85em; margin-top: 8px;">
                                    Cuando está habilitado, responde con este mensaje fuera de horarios y feriados.
                                </p>
                            </div>
                            <div class="form-group">
                                <label>Mensaje Fuera de Horario</label>
                                <textarea id="offhoursContent" placeholder="Lo sentimos, estamos fuera de horario..." style="min-height: 300px;"></textarea>
                            </div>
                            <div class="buttons-group">
                                <button type="submit" class="btn btn-primary">💾 Guardar</button>
                                <button type="button" class="btn btn-secondary" onclick="resetOffhoursEditor()">↺ Deshacer Cambios</button>
                                <button type="button" class="btn btn-secondary" onclick="restoreOffhoursBackup()">⏮ Restaurar Versión Anterior</button>
                            </div>
                        </form>
                    </div>

                    <div class="card">
                        <h2>🎟️ Mensajes de Ticket</h2>
                        <div class="message" id="ticketMessagesMessage"></div>
                        <form onsubmit="saveTicketMessages(event)">
                            <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                                <h3 style="color: #f1f5f9; margin-bottom: 12px;">🎟️ Mensaje de Creación de Ticket</h3>
                                <div class="form-group">
                                    <label>Mensaje Base (Usa {TKT} para número de ticket y {HOURS} para tiempo estimado)</label>
                                    <textarea id="handoffMessage" rows="8" placeholder="Ocurrirá al derivar a humano..."></textarea>
                                </div>
                                <div class="buttons-group">
                                    <button type="submit" class="btn btn-primary">💾 Guardar Mensaje</button>
                                </div>
                            </div>

                            <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                                <h3 style="color: #f1f5f9; margin-bottom: 12px;">👋 Mensaje de Cierre de Ticket (/fin)</h3>
                                <p style="color:#94a3b8;font-size:0.85em;margin-bottom:10px;">
                                    Este mensaje se envía automáticamente al cliente cuando el operador escribe <strong>/fin</strong> para cerrar el ticket.
                                </p>
                                <div class="form-group">
                                    <label>Mensaje de Despedida</label>
                                    <textarea id="farewellMessage" rows="5" placeholder="Gracias por contactarte. ¡Que tengas un buen día! 😊"></textarea>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- ══ TAB: SISTEMA → Config Bot + WAHA + Usuarios + Bloqueados ══ -->
                <div id="configTab-sistema" class="config-tab-panel">
                    <!-- Configuración del Bot -->
                    <div class="card">
                        <h2>⚙️ Configuración del Bot</h2>
                        <div class="message" id="configMessage"></div>
                        <form onsubmit="saveConfig(event)">
                            <div class="form-group">
                                <label>Nombre de la Solución / Título del Menú</label>
                                <input type="text" id="solutionName" placeholder="Clínica">
                            </div>
                        
                        <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 16px;">📅 Horarios Lunes - Viernes</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Hora de Apertura</label>
                                    <input type="time" id="openingTime">
                                </div>
                                <div class="form-group">
                                    <label>Hora de Cierre</label>
                                    <input type="time" id="closingTime">
                                </div>
                            </div>
                        </div>
                        
                        <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 12px;">📅 Horarios Sábado</h3>
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin-bottom: 14px;">
                                <input type="checkbox" id="satEnabled" style="width:16px;height:16px;" onchange="toggleSatFields()">
                                <span style="color:#f1f5f9;">Sábado con atención</span>
                            </label>
                            <div id="satFields">
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Hora de Apertura</label>
                                        <input type="time" id="satOpeningTime">
                                    </div>
                                    <div class="form-group">
                                        <label>Hora de Cierre</label>
                                        <input type="time" id="satClosingTime">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 12px;">📅 Horarios Domingo</h3>
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin-bottom: 14px;">
                                <input type="checkbox" id="sunEnabled" style="width:16px;height:16px;" onchange="toggleSunFields()">
                                <span style="color:#f1f5f9;">Domingo con atención</span>
                            </label>
                            <div id="sunFields" style="display:none;">
                                <p style="color:#94a3b8;font-size:0.85em;margin-bottom:8px;">Usa los mismos horarios que el sábado cuando está habilitado.</p>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">💾 Guardar Configuración</button>
                        </form>
                    </div>

                    <!-- Integraciones Externas / Access Token -->
                    <div class="card" style="margin-top: 24px;">
                        <h2>🔐 Access Token (Sistemas Externos)</h2>
                        <div class="message" id="accessTokenMessage"></div>

                        <form onsubmit="createAccessToken(event)" style="margin-bottom: 20px;">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Nombre del acceso</label>
                                    <input type="text" id="extAccessName" placeholder="Ej: ERP Facturacion" required>
                                </div>
                                <div class="form-group">
                                    <label>Eventos permitidos (CSV o *)</label>
                                    <input type="text" id="extAccessEvents" placeholder="appointment_reminder,invoice_ready,custom" value="*">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Descripción</label>
                                <input type="text" id="extAccessDescription" placeholder="Sistema que enviará turnos/facturas">
                            </div>
                            <button type="submit" class="btn btn-primary">➕ Crear acceso (auto genera API key)</button>
                        </form>

                        <div id="newAccessTokenBox" style="display:none; margin-bottom: 18px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 14px;">
                            <div style="font-weight: 600; color: #86efac; margin-bottom: 6px;">API key generada</div>
                            <div style="color: #cbd5e1; font-size: 0.88em; margin-bottom: 8px;">Guardala ahora. Por seguridad no vuelve a mostrarse completa.</div>
                            <code id="newAccessTokenValue" style="display:block; white-space: pre-wrap; word-break: break-all; color: #e2e8f0; background: rgba(15, 23, 42, 0.7); padding: 10px; border-radius: 8px;"></code>
                            <button type="button" class="btn btn-secondary" style="margin-top: 10px;" onclick="copyLatestAccessToken()">📋 Copiar API key</button>
                        </div>

                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 0.92em;">
                                <thead>
                                    <tr style="background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid rgba(226, 232, 240, 0.1);">
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Nombre</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Prefijo</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Eventos</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Estado</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Último uso</th>
                                        <th style="padding: 12px; text-align: right; color: #cbd5e1;">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="accessTokensTable">
                                    <tr><td colspan="6" style="text-align: center; padding: 20px; color: #94a3b8;">Cargando...</td></tr>
                                </tbody>
                            </table>
                        </div>

                        <p style="margin-top: 14px; color: #94a3b8; font-size: 0.84em; line-height: 1.5;">
                            Endpoint para integraciones: <code style="background: rgba(15, 23, 42, 0.7); padding: 2px 6px; border-radius: 6px;">POST /api/external/notifications</code><br>
                            Header requerido: <code style="background: rgba(15, 23, 42, 0.7); padding: 2px 6px; border-radius: 6px;">X-API-Key: &lt;tu_token&gt;</code>
                        </p>
                    </div>

                    <!-- WAHA -->
                    <div class="card" style="margin-top: 24px;">
                        <h2>📡 Estado de WAHA</h2>
                        <div id="wahaContent">
                            <div style="text-align: center; padding: 40px;">
                                <div class="spinner"></div>
                                <p style="margin-top: 16px; color: #94a3b8;">Cargando información de WAHA...</p>
                            </div>
                        </div>
                        <div style="margin-top: 24px; display: flex; gap: 12px; flex-wrap: wrap;">
                            <button onclick="refreshWahaStatus()" class="btn btn-primary">🔄 Actualizar</button>
                            <button onclick="connectWaha()" class="btn btn-secondary" id="btnConnectWaha">🔌 Conectar/Reiniciar</button>
                            <button onclick="logoutWaha()" class="btn btn-danger" id="btnLogoutWaha">🚪 Logout (Borrar QR)</button>
                        </div>
                        <details style="margin-top: 20px; background: rgba(15, 23, 42, 0.35); border: 1px solid rgba(226, 232, 240, 0.08); border-radius: 10px; padding: 0 14px 14px 14px;">
                            <summary style="color: #f1f5f9; font-size: 1em; cursor: pointer; padding: 14px 0; font-weight: 600;">
                                📊 Información de la Sesión
                            </summary>
                            <pre id="wahaRawInfo" style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 0.82em; color: #94a3b8; margin: 0;"></pre>
                        </details>
                    </div>

                </div>
                <!-- fin configTab-sistema -->

                <!-- ══ TAB: USUARIOS ══ -->
                <div id="configTab-usuarios" class="config-tab-panel">
                    <div class="card">
                        <h2>👥 Gestión de Usuarios</h2>
                        <div class="message" id="usersMessage"></div>
                        <button class="btn btn-primary" onclick="openCreateUserModal()" style="margin-bottom: 20px;">➕ Crear Nuevo Usuario</button>
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse; font-size: 0.95em;">
                                <thead>
                                    <tr style="background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid rgba(226, 232, 240, 0.1);">
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Usuario</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Email</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Rol</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Activo</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Pausa</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody id="usersTable">
                                    <tr><td colspan="6" style="text-align: center; padding: 20px; color: #94a3b8;">Cargando...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- ══ TAB: BLOQUEOS ══ -->
                <div id="configTab-bloqueos" class="config-tab-panel">
                    <div class="card">
                        <h2>🚫 Bloqueos</h2>
                        <div class="message" id="blocklistMessage"></div>

                        <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 8px;">🌍 Filtro por País — Lista Blanca</h3>
                            <p style="color: #94a3b8; font-size: 0.85em; margin: 0 0 12px 0; line-height: 1.5;">
                                Cuando está <strong style="color:#22d3ee;">activo</strong>, el bot <strong style="color:#f1f5f9;">SOLO responderá</strong> a
                                números cuyos primeros dígitos coincidan con los códigos indicados. Cualquier número de otro
                                país será ignorado silenciosamente.<br>
                                <em>Ejemplo: <code style="background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px;">+54</code>
                                → solo números de Argentina; <code style="background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px;">+54, +598</code>
                                → Argentina y Uruguay.</em>
                            </p>
                            <div class="form-group">
                                <label>Códigos de País permitidos (separados por coma, ej: +54, +55)</label>
                                <input type="text" id="countryFilter" placeholder="+54, +55, +56">
                            </div>
                            <label style="display: flex; align-items: center; cursor: pointer;">
                                <input type="checkbox" id="countryFilterEnabled" style="width: auto; margin-right: 8px;">
                                <span>✅ Activar filtro: solo responder a números de estos países</span>
                            </label>
                        </div>

                        <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 8px;">📍 Filtro por Localidad — Lista Blanca</h3>
                            <p style="color: #94a3b8; font-size: 0.85em; margin: 0 0 12px 0; line-height: 1.5;">
                                Cuando está <strong style="color:#22d3ee;">activo</strong>, el bot <strong style="color:#f1f5f9;">SOLO responderá</strong> a
                                números que contengan alguno de los patrones indicados en cualquier parte del número.
                                Permite restringir por código de área local dentro de un mismo país.<br>
                                <em>Ejemplo: <code style="background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px;">351</code>
                                → solo responde a números con el código de área 351 (Córdoba, Argentina).</em>
                            </p>
                            <div class="form-group">
                                <label>Patrones de Localidad permitidos (separados por coma)</label>
                                <input type="text" id="areaFilter" placeholder="351, 011, 0351">
                            </div>
                            <label style="display: flex; align-items: center; cursor: pointer;">
                                <input type="checkbox" id="areaFilterEnabled" style="width: auto; margin-right: 8px;">
                                <span>✅ Activar filtro: solo responder a números de estas localidades</span>
                            </label>
                        </div>

                        <div style="margin-bottom: 24px;">
                            <button class="btn btn-primary" onclick="saveFilters()" style="width: 100%;">💾 Guardar Filtros</button>
                        </div>

                        <form onsubmit="blockNumber(event)" style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 12px;">🔒 Bloquear Número Manual</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Número de WhatsApp</label>
                                    <input type="text" id="blockNumber" placeholder="5491234567890 o +5491234567890">
                                </div>
                                <div class="form-group">
                                    <label>Razón</label>
                                    <input type="text" id="blockReason" placeholder="Ej: Spam">
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">🚫 Bloquear</button>
                        </form>

                        <h3 style="color: #f1f5f9; margin-bottom: 12px;">📋 Lista de Bloqueados</h3>
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid rgba(226, 232, 240, 0.1);">
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Número</th>
                                        <th style="padding: 12px; text-align: left; color: #cbd5e1;">Razón</th>
                                        <th style="padding: 12px; text-align: right; color: #cbd5e1;">Acción</th>
                                    </tr>
                                </thead>
                                <tbody id="blocklistTable">
                                    <tr><td colspan="3" style="text-align: center; padding: 20px; color: #94a3b8;">Cargando...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <!-- fin #config -->

            <!-- FERIADOS (sección top-level) -->
            <div id="holidays" class="section">
                <div class="hol-layout">
                    <!-- Columna izquierda: Calendario -->
                    <div class="card hol-cal-col">
                        <h2>📅 Calendario de Feriados</h2>
                        <p style="color:#64748b;font-size:0.88em;margin-bottom:16px;">
                            Hacé clic en un día para marcarlo como feriado. Los días marcados en
                            <strong style="color:#60a5fa;">azul</strong> ya están guardados;
                            en <strong style="color:#fcd34d;">amarillo</strong> están pendientes de guardar;
                            en <strong style="color:#f87171;">rojo tachado</strong> serán eliminados.
                            Sábados y domingos se muestran en <strong style="color:#f472b6;">rosa</strong>.
                        </p>

                        <div id="pendingBadge" class="pending-badge hidden">
                            ⚠️ <span id="pendingText">0 cambios pendientes</span>
                        </div>

                        <div class="cal-wrap">
                            <div class="cal-header">
                                <div class="cal-nav">
                                    <button class="cal-btn" onclick="calPrev()">◀ Ant</button>
                                    <button class="cal-btn" onclick="calToday()">Hoy</button>
                                    <button class="cal-btn" onclick="calNext()">Sig ▶</button>
                                </div>
                                <div class="cal-title" id="calTitle">—</div>
                            </div>
                            <div class="cal-grid" id="calGrid"></div>
                            <div class="cal-legend">
                                <span><div class="leg-dot" style="background:linear-gradient(135deg,#3b82f6,#06b6d4);"></div> Feriado guardado</span>
                                <span><div class="leg-dot" style="background:linear-gradient(135deg,#f59e0b,#d97706);"></div> Por guardar</span>
                                <span><div class="leg-dot" style="background:rgba(239,68,68,0.3);border:1px solid #f87171;"></div> Por eliminar</span>
                                <span><div class="leg-dot" style="background:transparent;outline:2px solid rgba(99,102,241,0.8);outline-offset:1px;"></div> Hoy</span>
                                <span><div class="leg-dot" style="background:rgba(15,23,42,0.5);border:1px solid rgba(226,232,240,0.1);"></div> <span style="color:#f472b6">Fin de semana</span></span>
                            </div>
                        </div>

                        <!-- Guardar / Cancelar -->
                        <div class="card-footer">
                            <button class="btn btn-secondary" onclick="cancelHolidays()">✖ Cancelar cambios</button>
                            <button class="btn btn-primary" id="saveHBtn" onclick="saveHolidays()">💾 Guardar Feriados</button>
                        </div>
                    </div>

                    <!-- Columna derecha: Lista resumen -->
                    <div class="card hol-list-col">
                        <h2>📋 Feriados Guardados</h2>
                        <div id="holidaysList"><div class="empty-state">Cargando...</div></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Admin Modal Mensajes Programados -->
        <div id="adminSchedModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.82); align-items:center; justify-content:center; z-index:2000;">
            <div style="background:rgba(15,23,42,0.99); border:1px solid rgba(226,232,240,0.12); border-radius:18px; padding:28px; width:94%; max-width:480px; display:flex; flex-direction:column; gap:14px; box-shadow:0 20px 60px rgba(0,0,0,0.6);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="color:#f1f5f9; font-size:1.05em; font-weight:700;" id="adminSchedModalTitle">🕐 Nuevo Mensaje Programado</div>
                    <button onclick="closeAdminSchedModal()" style="background:none; border:none; color:#94a3b8; font-size:1.3em; cursor:pointer;">&times;</button>
                </div>
                <div style="display:flex; flex-direction:column; gap:10px;">
                    <div><label style="color:#94a3b8; font-size:0.82em; display:block; margin-bottom:4px;">Nombre / Descripción</label>
                        <input id="adminSchedName" type="text" placeholder="Ej: Recordatorio turno mañana" style="width:100%; padding:9px 12px; background:rgba(30,41,59,0.7); border:1px solid rgba(226,232,240,0.15); border-radius:8px; color:#f1f5f9; font-size:0.9em; box-sizing:border-box;"></div>
                    <div><label style="color:#94a3b8; font-size:0.82em; display:block; margin-bottom:4px;">Número(s) destino <span style="color:#64748b;">(coma si son varios)</span></label>
                        <input id="adminSchedPhone" type="text" placeholder="5491112345678" style="width:100%; padding:9px 12px; background:rgba(30,41,59,0.7); border:1px solid rgba(226,232,240,0.15); border-radius:8px; color:#f1f5f9; font-size:0.9em; box-sizing:border-box;"></div>
                    <div><label style="color:#94a3b8; font-size:0.82em; display:block; margin-bottom:4px;">Fecha y Hora</label>
                        <input id="adminSchedTime" type="datetime-local" style="width:100%; padding:9px 12px; background:rgba(30,41,59,0.7); border:1px solid rgba(226,232,240,0.15); border-radius:8px; color:#f1f5f9; font-size:0.9em; box-sizing:border-box;"></div>
                    <div><label style="color:#94a3b8; font-size:0.82em; display:block; margin-bottom:4px;">Mensaje</label>
                        <textarea id="adminSchedMsg" rows="4" placeholder="Texto del mensaje a enviar..." style="width:100%; padding:9px 12px; background:rgba(30,41,59,0.7); border:1px solid rgba(226,232,240,0.15); border-radius:8px; color:#f1f5f9; font-size:0.9em; resize:vertical; box-sizing:border-box;"></textarea></div>
                </div>
                <div style="display:flex; gap:10px; margin-top:4px;">
                    <button onclick="saveAdminSchedMsg()" style="flex:1; padding:11px; background:linear-gradient(135deg,#3b82f6,#06b6d4); border:none; border-radius:8px; color:white; font-weight:600; cursor:pointer;">💾 Guardar</button>
                    <button onclick="closeAdminSchedModal()" style="padding:11px 18px; background:rgba(30,41,59,0.5); border:1px solid rgba(226,232,240,0.1); border-radius:8px; color:#94a3b8; cursor:pointer;">Cancelar</button>
                </div>
                <div id="adminSchedModalMsg" style="font-size:0.85em; min-height:18px; text-align:center;"></div>
            </div>
        </div>

        <!-- Admin Chat Modal -->
        <div id="adminChatModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.88); align-items:center; justify-content:center; z-index:2000;">
            <div style="background:#111b21; border-radius:16px; width:96%; max-width:560px; height:82vh; max-height:680px; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 80px rgba(0,0,0,0.7);">
                <!-- Header WA style -->
                <div style="background:#1f2c34; padding:10px 16px; display:flex; align-items:center; gap:12px; border-bottom:1px solid rgba(255,255,255,0.06); flex-shrink:0;">
                    <div style="width:40px; height:40px; border-radius:50%; background:#2a3942; display:flex; align-items:center; justify-content:center; font-size:1.1em; flex-shrink:0;">👤</div>
                    <div style="flex:1; min-width:0;">
                        <div id="adminChatModalTitle" style="color:#e9edef; font-size:0.97em; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"></div>
                        <div style="color:#8696a0; font-size:0.75em;">Ticket: <span id="adminChatModalTicket" style="color:#53bdeb; font-family:monospace;"></span></div>
                    </div>
                    <button onclick="adminCloseChatModal()" style="background:none; border:none; color:#8696a0; font-size:1.3em; cursor:pointer; padding:6px; flex-shrink:0;">&times;</button>
                </div>
                <!-- Messages -->
                <div id="adminChatMessages" style="flex:1; overflow-y:auto; padding:12px 10px; display:flex; flex-direction:column; gap:2px; background:#0b141a;"></div>
                <!-- Compose bar -->
                <div style="background:#1f2c34; padding:8px 12px; display:flex; align-items:flex-end; gap:8px; border-top:1px solid rgba(255,255,255,0.06); flex-shrink:0;">
                    <div style="flex:1; background:#2a3942; border-radius:24px; padding:9px 16px; display:flex; align-items:flex-end; min-height:44px;">
                        <textarea id="adminChatReplyInput" placeholder="Escribe un mensaje" rows="1"
                            style="flex:1; background:transparent; border:none; outline:none; color:#d1d7db; font-size:0.95em; resize:none; overflow-y:hidden; max-height:110px; height:22px; font-family:inherit; line-height:22px; padding:0; display:block; width:100%;"
                            onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();adminSendChatReply();}"
                            oninput="_resizeAdminChatTA(this)"></textarea>
                    </div>
                    <button id="adminChatCloseBtn" onclick="adminCloseTicketFromModal()" title="Cerrar ticket"
                        style="width:44px; height:44px; flex-shrink:0; background:rgba(220,38,38,0.22); border:1px solid rgba(220,38,38,0.45); border-radius:50%; color:#fca5a5; font-size:0.95em; cursor:pointer;">🔒</button>
                    <button onclick="adminSendChatReply()" title="Enviar"
                        style="width:44px; height:44px; flex-shrink:0; background:#00a884; border:none; border-radius:50%; color:white; font-size:1.1em; cursor:pointer;">➤</button>
                </div>
                <div id="adminChatReplyMsg" style="font-size:0.8em; min-height:20px; text-align:center; padding:2px 12px 5px; background:#1f2c34; color:#8696a0;"></div>
            </div>
        </div>

        <!-- Modal QR -->
        <div class="modal" id="qrModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: rgba(18, 24, 40, 0.95); border: 1px solid rgba(226, 232, 240, 0.1); border-radius: 20px; padding: 40px; max-width: 400px; width: 90%; text-align: center;">
                <h3 style="color: #f1f5f9; margin-bottom: 16px;">📱 Conectar WhatsApp</h3>
                <p style="color: #cbd5e1; margin-bottom: 8px;">Escanea el código QR desde tu WhatsApp</p>
                <div class="qr-loading" id="qrLoading">
                    <div class="spinner"></div>
                    <p class="spinner-text" id="qrStatus">Iniciando sesión...<br><small>Por favor espera unos segundos</small></p>
                </div>
                <img id="qrImage" style="display:none; margin: 20px 0; max-width: 100%; border-radius: 12px; border: 2px solid rgba(226, 232, 240, 0.1);" src="" alt="QR Code">
                <p id="qrExpireMsg" style="display:none; color:#94a3b8; font-size:0.8em; margin-top:6px;">⏱️ El QR se renueva automáticamente</p>
                <div id="qrError" style="display:none; color:#ef4444; padding:16px 0;">
                    ❌ No se pudo obtener el QR.<br>
                    <button onclick="_retryQr()" style="margin-top:12px; padding:8px 20px; background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.4); color:#93c5fd; border-radius:8px; cursor:pointer; font-size:0.9em;">🔄 Reintentar</button>
                </div>
                <button class="btn btn-secondary" onclick="closeQrModal()" style="margin-top: 20px;">✖ Cerrar</button>
            </div>
        </div>
        
        <script>
            const API_URL = '/api';
            const token = localStorage.getItem('token');
            const userStr = localStorage.getItem('user');

            // Cargar info de usuario en la sidebar
            if (userStr) {
                try {
                    const user = JSON.parse(userStr);
                    const userNameEl = document.getElementById('sidebarUserName');
                    const userAvatarEl = document.getElementById('userAvatar');
                    const userBoxEl = document.getElementById('sidebarUserBox');
                    
                    if (userNameEl) userNameEl.textContent = user.full_name || user.username || 'Usuario';
                    if (userAvatarEl) {
                        const name = user.full_name || user.username || 'U';
                        userAvatarEl.textContent = name.charAt(0).toUpperCase();
                    }
                    if (userBoxEl) userBoxEl.style.display = 'flex';
                } catch (e) {
                    console.error('Error parsing user data', e);
                }
            }
            
            // Variables para rastrear cambios de estado
            let lastConnectedStatus = null;
            let statusPollingInterval = null;
            
            // Solicitar permisos de notificación
            function requestNotificationPermission() {
                if ('Notification' in window && Notification.permission === 'default') {
                    Notification.requestPermission();
                }
            }
            
            // Mostrar notificación de desconexión
            function notifyDisconnection() {
                if ('Notification' in window && Notification.permission === 'granted') {
                    new Notification('🤖 WA-BOT', {
                        body: '⚠️ El bot se ha desconectado de WhatsApp',
                        icon: '🔴',
                        tag: 'bot-disconnect'
                    });
                }
            }
            
            // Validar autenticación y permisos al cargar la página
            window.addEventListener('DOMContentLoaded', function() {
                requestNotificationPermission();
                
                // Polling cada 8 segundos para detectar desconexiones
                statusPollingInterval = setInterval(async () => {
                    try {
                        const token = localStorage.getItem('token');
                        const res = await fetch('/status', {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const status = await res.json();
                        
                        // Detectar cambio de conectado a desconectado
                        if (lastConnectedStatus === true && status.connected === false) {
                            console.warn('[STATUS] Desconexión detectada!');
                            notifyDisconnection();
                        }
                        
                        lastConnectedStatus = status.connected;
                    } catch (e) {
                        console.error('[STATUS_POLL] Error:', e);
                    }
                }, 8000);
                
                if (!token) {
                    window.location.href = '/login';
                    return;
                }
                
                try {
                    const user = JSON.parse(userStr);
                    if (!user.is_admin) {
                        window.location.href = '/user-panel';
                        return;
                    }
                } catch (e) {
                    window.location.href = '/login';
                    return;
                }
                
                refresh();
                loadAdminParkedList();
                loadAdminSchedList();
                loadHolidays();
            });
            
            let currentMonth = new Date();
            let selectedDates = new Set();
            let originalMenuContent = '';
            let originalOffhoursContent = '';
            let originalOffhoursEnabled = false;
            
            function switchSection(section) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-item.active').forEach(n => n.classList.remove('active'));
                
                const targetSection = document.getElementById(section);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
                
                // Buscar el nav-item que corresponde a esta sección
                const navItems = document.querySelectorAll('.nav-item');
                navItems.forEach(n => {
                    const oc = n.getAttribute('onclick');
                    if (oc && oc.includes(`'${section}'`)) {
                        n.classList.add('active');
                    }
                });

                if (section === 'holidays') { 
                    loadHolidays(); 
                }
                else if (section === 'status') refresh();
                else if (section === 'config') loadConfigTabData(currentConfigTab);
                else if (section === 'ticketsAdmin') { loadAdminTickets(); loadAdminSchedList(); }
                else if (section === 'programadosAdmin') loadAdminSchedList();
            }

            // ── TICKETS ADMIN JS ────────────────────────────────────────────────────────
            let adminCurrentTickets = [];
            let adminCurrentChatPhone = '';
            let adminCurrentChatTicketId = '';

            async function loadAdminTickets() {
                try {
                    const res = await fetch('/api/tickets/list', {
                        headers: { 'Authorization': 'Bearer ' + token }
                    });
                    if (res.ok) {
                        adminCurrentTickets = await res.json();
                        const openTicketsEl = document.getElementById('openTicketsCount');
                        if (openTicketsEl) {
                            openTicketsEl.textContent = String(
                                adminCurrentTickets.filter(t => t.type === 'active').length
                            );
                        }
                        renderAdminTickets();
                    }
                } catch(e) { console.error(e); }
            }

            function renderAdminTickets() {
                const grid = document.getElementById('adminTicketsGrid');
                if (!adminCurrentTickets.length) {
                    grid.innerHTML = '<div class="empty-state">No hay tickets</div>';
                    return;
                }
                let html = '';
                adminCurrentTickets.forEach(t => {
                    let badgeColor = '#64748b';
                    if (t.status === 'pendiente') badgeColor = '#f59e0b';
                    if (t.status === 'confirmado') badgeColor = '#10b981';
                    if (t.status === 'cancelado') badgeColor = '#ef4444';
                    if (t.status === 'timeout')   badgeColor = '#ef4444';
                    if (t.status === 'cerrado')    badgeColor = '#3b82f6';

                    let statusLabel = t.status.toUpperCase();
                    if (t.is_deleted) statusLabel += ' (BORRADO por ' + (t.deleted_by || 'Unknown') + ')';

                    let schedBadge = t.has_scheduled_message
                        ? '<span style="background:rgba(139,92,246,0.2);color:#c4b5fd;padding:2px 6px;border-radius:4px;font-size:0.8em;margin-left:8px;">\u23F3 Programado</span>'
                        : '';

                    html += `
                        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(226,232,240,0.08);border-radius:12px;padding:16px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
                            <div style="flex:1;min-width:0;">
                                <div style="font-weight:600;color:#f1f5f9;font-size:0.95em;">${t.ticket_id || '-'} | Tel: ${t.phone_number} ${schedBadge}</div>
                                <div style="color:${badgeColor};font-weight:500;font-size:0.88em;margin-top:4px;">${statusLabel} | Origen: ${t.menu_breadcrumb || t.menu_section || '-'}</div>
                                <div style="font-size:0.75em;color:#64748b;margin-top:3px;">Abierto: ${t.opened_at ? new Date(t.opened_at).toLocaleString() : '-'}</div>
                            </div>
                            <div style="display:flex;gap:8px;flex-shrink:0;">
                                <button class="btn btn-secondary btn-sm" onclick="adminViewTicket('${t.id}')">Ver Chat</button>
                            </div>
                        </div>`;
                });
                grid.innerHTML = html;
            }

            async function adminViewTicket(tid) {
                const t = adminCurrentTickets.find(x => x.id === tid);
                if (!t) return;
                adminCurrentChatPhone = t.phone_number;
                adminCurrentChatTicketId = tid;

                document.getElementById('adminChatModalTitle').textContent = `Chat: ${t.phone_number} (${t.status})`;
                document.getElementById('adminChatContent').innerHTML = '<div style="color:#94a3b8;text-align:center;padding:20px;">Cargando mensajes...</div>';
                document.getElementById('adminChatModal').classList.add('show');

                let actionsHtml = '';
                if (!t.is_deleted) {
                    if (t.status === 'pendiente') actionsHtml += `<button class="btn btn-primary btn-sm" onclick="adminActionTicket('fin')">Fin</button>`;
                    if (t.status === 'timeout')   actionsHtml += `<button class="btn btn-primary btn-sm" onclick="adminActionTicket('resume')">Retomar</button>`;
                    actionsHtml += `<button class="btn btn-danger btn-sm" onclick="adminActionTicket('delete')">Borrar</button>`;
                }
                document.getElementById('adminChatModalActions').innerHTML = actionsHtml;

                try {
                    const res = await fetch(`/api/human-mode/messages/${encodeURIComponent(t.phone_number)}`, {
                        headers: { 'Authorization': 'Bearer ' + token }
                    });
                    if (res.ok) {
                        const data = await res.json();
                        const msgs = Array.isArray(data) ? data : (data.messages || []);
                        let chtml = '';
                        if (!msgs || !msgs.length) {
                            chtml = '<div style="color:#94a3b8;text-align:center;padding:20px;">No hay mensajes recientes</div>';
                        } else {
                            msgs.forEach(m => {
                                const isBot = m.from_me || m.fromMe;
                                const align = isBot ? 'right' : 'left';
                                const bg    = isBot ? 'rgba(59,130,246,0.2)' : 'rgba(30,41,59,0.8)';
                                const text  = m.body || m.text || JSON.stringify(m);
                                const escapedText = _escapeSchedMsgAttr(text);
                                chtml += `<div style="text-align:${align};margin-bottom:8px;display:flex;align-items:flex-start;justify-content:${isBot ? 'flex-end' : 'flex-start'};gap:8px;">
                                    ${!isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-top:8px;cursor:pointer;" title="Seleccionar mensaje para agendar">` : ''}
                                    <div style="display:inline-block;background:${bg};padding:8px 12px;border-radius:8px;max-width:80%;word-break:break-word;text-align:left;">${text}</div>
                                    ${isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-top:8px;cursor:pointer;" title="Seleccionar mensaje para agendar">` : ''}
                                </div>`;
                            });
                        }
                        document.getElementById('adminChatContent').innerHTML = chtml;
                        const cc = document.getElementById('adminChatContent');
                        cc.scrollTop = cc.scrollHeight;
                    } else {
                        document.getElementById('adminChatContent').innerHTML = '<div style="color:#94a3b8;text-align:center;">No se pudieron cargar los mensajes.</div>';
                    }
                } catch(e) {
                    document.getElementById('adminChatContent').innerHTML = '<div style="color:#94a3b8;text-align:center;">Error cargando mensajes.</div>';
                }
            }

            function closeAdminChatModal() { document.getElementById('adminChatModal').classList.remove('show'); }

            async function adminActionTicket(action) {
                if (action === 'delete' && !confirm('\u00bfSeguro que quieres borrar este ticket?')) return;
                try {
                    const res = await fetch('/api/tickets/action', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                        body: JSON.stringify({ action: action, id: adminCurrentChatTicketId })
                    });
                    if (res.ok) { closeAdminChatModal(); loadAdminTickets(); }
                    else        alert('Error ejecutando accion');
                } catch(e) { console.error(e); }
            }

            function openAdminTicketScheduleModal() {
                document.getElementById('adminSchedTicketPhone').value   = adminCurrentChatPhone;
                document.getElementById('adminSchedTicketName').value    = '';
                document.getElementById('adminSchedTicketTime').value    = '';
                document.getElementById('adminSchedTicketMessage').value = _getSelectedSchedChatText('#adminChatContent');
                document.getElementById('adminTicketSchedModal').classList.add('show');
            }
            function closeAdminTicketScheduleModal() { document.getElementById('adminTicketSchedModal').classList.remove('show'); }

            async function saveAdminTicketScheduledMessage() {
                const phone = document.getElementById('adminSchedTicketPhone').value;
                const name  = document.getElementById('adminSchedTicketName').value;
                const val   = document.getElementById('adminSchedTicketTime').value;
                const msg   = document.getElementById('adminSchedTicketMessage').value;
                
                let send_time = '';
                let send_date = null;
                if (val) {
                    const parts = val.split('T');
                    send_date = parts[0];
                    send_time = parts[1];
                }
                
                if (!name || !send_time || !msg) { alert('Completar todos los campos'); return; }
                try {
                    const res = await fetch('/api/scheduled-messages', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                        body: JSON.stringify({ name, phone_number: phone, send_time, send_date, message: msg, days_of_week: '1,2,3,4,5,6,7', is_active: true })
                    });
                    if (res.ok) { closeAdminTicketScheduleModal(); loadAdminTickets(); loadAdminSchedList(); showToast('Mensaje agendado'); }
                } catch(e) { console.error(e); }
            }
            // ── FIN TICKETS ADMIN ──────────────────────────────────────────────────────────────

            // ── Toast ───────────────────────────────────────────────
            function showToast(msg, type = 'success') {
                const t = document.getElementById('toast') || document.createElement('div');
                if (!document.getElementById('toast')) {
                    t.id = 'toast';
                    t.className = 'wa-toast';
                    document.body.appendChild(t);
                }
                t.textContent = msg;
                t.style.background = type === 'success' ? '#16a34a' : (type === 'error' ? '#dc2626' : '#3b82f6');
                t.className = 'wa-toast show';
                setTimeout(() => t.classList.remove('show'), 3500);
            }

            // ══════════════════════════════════════════════════════
            //  CALENDARIO AVANZADO
            // ══════════════════════════════════════════════════════
            let calDate      = new Date();
            let _savedHols   = [];        // [{id, date, name}]
            let _savedSet    = new Set(); // fechas en BD
            let _selSet      = new Set(); // fechas seleccionadas UI

            const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                            'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
            const WDAYS  = ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];

            function calPrev()  { calDate.setMonth(calDate.getMonth()-1); renderCalendar(); }
            function calNext()  { calDate.setMonth(calDate.getMonth()+1); renderCalendar(); }
            function calToday() { calDate = new Date(); renderCalendar(); }

            function fmtDate(d) {
                return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
            }
            function fmtParts(y,m,d) {
                return y+'-'+String(m).padStart(2,'0')+'-'+String(d).padStart(2,'0');
            }
            function fmtHuman(s) {
                if(!s) return '';
                const [y,m,d]=s.split('-'); return d+'/'+m+'/'+y;
            }

            function renderCalendar() {
                const yr = calDate.getFullYear();
                const mo = calDate.getMonth();
                const titleEl = document.getElementById('calTitle');
                if(!titleEl) return;
                titleEl.textContent = MONTHS[mo] + ' ' + yr;

                const todayStr = fmtDate(new Date());
                const grid = document.getElementById('calGrid');
                if(!grid) return;
                grid.innerHTML = '';

                WDAYS.forEach((d,i) => {
                    const h = document.createElement('div');
                    h.className = 'cal-hdr' + (i===0||i===6?' wknd':'');
                    h.textContent = d;
                    grid.appendChild(h);
                });

                const firstDow = new Date(yr, mo, 1).getDay();
                const daysInMo = new Date(yr, mo+1, 0).getDate();

                for(let i=0; i<firstDow; i++) {
                    const e=document.createElement('div'); e.className='cal-cell empty'; grid.appendChild(e);
                }

                for(let d=1; d<=daysInMo; d++) {
                    const ds    = fmtParts(yr, mo+1, d);
                    const dow   = new Date(yr,mo,d).getDay();
                    const isWkd = dow===0||dow===6;
                    const inDB  = _savedSet.has(ds);
                    const inSel = _selSet.has(ds);
                    const isToday = ds === todayStr;

                    const cell = document.createElement('div');
                    let cls = 'cal-cell';
                    if(isWkd) cls += ' wknd';
                    if(isToday) cls += ' today';

                    if(inDB && inSel)      cls += ' selected';
                    else if(!inDB && inSel) cls += ' pending';
                    else if(inDB && !inSel) cls += ' removing';

                    cell.className = cls;
                    cell.textContent = d;

                    if(inDB && inSel) cell.title = (_savedHols.find(h=>h.date===ds)?.name||'Feriado guardado');
                    else if(!inDB && inSel) cell.title = 'Nuevo feriado — pendiente de guardar';
                    else if(inDB && !inSel) cell.title = 'Se eliminará al guardar';
                    else if(isWkd) cell.title = dow===6?'Sábado':'Domingo';

                    cell.onclick = () => {
                        if(_selSet.has(ds)) _selSet.delete(ds);
                        else _selSet.add(ds);
                        renderCalendar();
                        updatePendingBadge();
                    };
                    grid.appendChild(cell);
                }
            }

            function updatePendingBadge() {
                const toAdd = [..._selSet].filter(d=>!_savedSet.has(d)).length;
                const toDel = [..._savedSet].filter(d=>!_selSet.has(d)).length;
                const total = toAdd + toDel;
                const badge = document.getElementById('pendingBadge');
                const text  = document.getElementById('pendingText');
                if(!badge || !text) return;
                if(total>0) {
                    badge.classList.remove('hidden');
                    const parts=[];
                    if(toAdd>0) parts.push(`+${toAdd} por agregar`);
                    if(toDel>0) parts.push(`-${toDel} por eliminar`);
                    text.textContent = parts.join('  ·  ');
                } else {
                    badge.classList.add('hidden');
                }
            }

            async function loadHolidays() {
                try {
                    const res = await fetch('/api/holidays', {headers:{'Authorization':`Bearer ${token}`}});
                    if(!res.ok) throw new Error('HTTP '+res.status);
                    _savedHols = await res.json();
                    _savedHols.sort((a,b)=>a.date.localeCompare(b.date));
                    _savedSet = new Set(_savedHols.map(h=>h.date));
                    _selSet   = new Set(_savedSet);
                    updatePendingBadge();
                    renderCalendar();
                    renderHolidayList();
                } catch(e) {
                    const listEl = document.getElementById('holidaysList');
                    if(listEl) listEl.innerHTML='<div class="empty-state">❌ Error al cargar feriados</div>';
                }
            }

            function renderHolidayList() {
                const el = document.getElementById('holidaysList');
                if(!el) return;
                if(!_savedHols.length) {
                    el.innerHTML='<div class="empty-state">📭 No hay feriados guardados</div>'; return;
                }
                el.innerHTML = _savedHols.map(h => `
                    <div class="holiday-row">
                        <div class="holiday-info">
                            <span class="holiday-date">📅 ${fmtHuman(h.date)}</span>
                            <span class="holiday-name">${h.name||'Feriado'}</span>
                        </div>
                        <button class="btn btn-danger btn-sm" onclick="quickDelete(${h.id},'${h.date}')">🗑️</button>
                    </div>
                `).join('');
            }

            function cancelHolidays() {
                _selSet = new Set(_savedSet);
                renderCalendar();
                updatePendingBadge();
                showToast('↺ Cambios descartados', 'info');
            }

            async function saveHolidays() {
                const toAdd = [..._selSet].filter(d=>!_savedSet.has(d));
                const toDel = [..._savedSet].filter(d=>!_selSet.has(d));

                if(toAdd.length===0 && toDel.length===0) {
                    showToast('Sin cambios pendientes', 'info'); return;
                }

                const btn = document.getElementById('saveHBtn');
                if(btn) { btn.disabled=true; btn.textContent='⏳ Guardando...'; }
                let errors=0;
                try {
                    for(const date of toDel) {
                        const h = _savedHols.find(h=>h.date===date);
                        if(!h) continue;
                        const r = await fetch('/api/holidays/'+h.id, {
                            method:'DELETE', headers:{'Authorization':`Bearer ${token}`}
                        });
                        if(!r.ok) errors++;
                    }
                    for(const date of toAdd) {
                        const r = await fetch('/api/holidays', {
                            method:'POST',
                            headers:{'Authorization':`Bearer ${token}`,'Content-Type':'application/json'},
                            body: JSON.stringify({date, name:'Feriado'})
                        });
                        if(!r.ok) errors++;
                    }
                    await loadHolidays();
                    if(errors>0) showToast(`⚠️ Guardado con ${errors} error(es)`, 'error');
                    else showToast('✅ Feriados actualizados correctamente');
                } catch(e) {
                    showToast('❌ Error de conexión', 'error');
                } finally {
                    if(btn) { btn.disabled=false; btn.textContent='💾 Guardar Feriados'; }
                }
            }

            async function quickDelete(id, date) {
                if(!confirm('¿Eliminar feriado?')) return;
                const r = await fetch('/api/holidays/'+id, {
                    method:'DELETE', headers:{'Authorization':`Bearer ${token}`}
                });
                if(r.ok) {
                    showToast('🗑️ Feriado eliminado');
                    await loadHolidays();
                } else {
                    showToast('❌ Error al eliminar', 'error');
                }
            }
            
            let currentConfigTab = 'chatbot';
            let latestAccessTokenValue = '';

            function switchConfigTab(tab, btn) {
                currentConfigTab = tab;
                document.querySelectorAll('.config-tab-panel').forEach(p => p.classList.remove('active'));
                document.querySelectorAll('.config-tab').forEach(b => b.classList.remove('active'));
                document.getElementById('configTab-' + tab).classList.add('active');
                btn.classList.add('active');
                loadConfigTabData(tab);
            }

            function loadConfigTabData(tab) {
                if (tab === 'chatbot') {
                    loadMenu();
                    loadOffhours();
                    loadTicketMessages();
                } else if (tab === 'sistema') {
                    loadConfig();
                    loadAccessTokens();
                    refreshWahaStatus();
                } else if (tab === 'usuarios') {
                    loadUsers();
                } else if (tab === 'bloqueos') {
                    loadBlocklist();
                }
            }

            function _setAccessTokenMessage(text, ok = true) {
                const msg = document.getElementById('accessTokenMessage');
                if (!msg) return;
                msg.textContent = text;
                msg.className = ok ? 'message show success' : 'message show error';
                setTimeout(() => msg.classList.remove('show'), 3500);
            }

            function _formatDateSafe(iso) {
                if (!iso) return 'Nunca';
                try { return new Date(iso).toLocaleString('es-AR'); }
                catch(e) { return iso; }
            }

            async function loadAccessTokens() {
                const tbody = document.getElementById('accessTokensTable');
                if (!tbody) return;
                try {
                    const res = await fetch(`${API_URL}/admin/access-tokens`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    const rows = await res.json();
                    if (!rows.length) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#94a3b8;">Sin accesos creados</td></tr>';
                        return;
                    }
                    tbody.innerHTML = rows.map(r => `
                        <tr style="border-bottom: 1px solid rgba(226, 232, 240, 0.05);">
                            <td style="padding: 12px; color: #e2e8f0;">${r.name}</td>
                            <td style="padding: 12px; color: #93c5fd; font-family: monospace;">${r.token_prefix}...</td>
                            <td style="padding: 12px; color: #cbd5e1;">${r.allowed_event_types || '*'}</td>
                            <td style="padding: 12px; color: ${r.is_active ? '#86efac' : '#fca5a5'};">${r.is_active ? 'Activo' : 'Inactivo'}</td>
                            <td style="padding: 12px; color: #94a3b8;">${_formatDateSafe(r.last_used_at)}</td>
                            <td style="padding: 12px; text-align: right;">
                                <div style="display:flex; justify-content:flex-end; gap:6px; flex-wrap: wrap;">
                                    <button class="btn btn-secondary" style="padding:4px 8px; font-size:0.82em;" onclick="regenerateAccessToken(${r.id})">♻️ Regenerar</button>
                                    <button class="btn btn-secondary" style="padding:4px 8px; font-size:0.82em;" onclick="toggleAccessToken(${r.id})">${r.is_active ? '⏸️ Desactivar' : '▶️ Activar'}</button>
                                    <button class="btn btn-danger" style="padding:4px 8px; font-size:0.82em;" onclick="deleteAccessToken(${r.id})">🗑️ Eliminar</button>
                                </div>
                            </td>
                        </tr>
                    `).join('');
                } catch (error) {
                    console.error('Error loading access tokens:', error);
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:20px;color:#fca5a5;">Error al cargar access tokens</td></tr>';
                }
            }

            function _showNewApiKey(value) {
                latestAccessTokenValue = value || '';
                const box = document.getElementById('newAccessTokenBox');
                const code = document.getElementById('newAccessTokenValue');
                if (!box || !code) return;
                code.textContent = latestAccessTokenValue;
                box.style.display = latestAccessTokenValue ? 'block' : 'none';
            }

            async function copyLatestAccessToken() {
                if (!latestAccessTokenValue) return;
                try {
                    await navigator.clipboard.writeText(latestAccessTokenValue);
                    _setAccessTokenMessage('✅ API key copiada al portapapeles', true);
                } catch(e) {
                    _setAccessTokenMessage('❌ No se pudo copiar. Copiala manualmente.', false);
                }
            }

            async function createAccessToken(e) {
                e.preventDefault();
                try {
                    const payload = {
                        name: document.getElementById('extAccessName').value.trim(),
                        description: document.getElementById('extAccessDescription').value.trim() || null,
                        allowed_event_types: document.getElementById('extAccessEvents').value.trim() || '*'
                    };
                    if (!payload.name) {
                        _setAccessTokenMessage('❌ El nombre es obligatorio', false);
                        return;
                    }

                    const res = await fetch(`${API_URL}/admin/access-tokens`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        _setAccessTokenMessage('❌ ' + (data.detail || 'No se pudo crear el acceso'), false);
                        return;
                    }

                    _showNewApiKey(data.api_key || '');
                    _setAccessTokenMessage('✅ Access Token creado. Guardá la API key generada.', true);
                    document.getElementById('extAccessName').value = '';
                    document.getElementById('extAccessDescription').value = '';
                    document.getElementById('extAccessEvents').value = '*';
                    loadAccessTokens();
                } catch (error) {
                    console.error('Error creating access token:', error);
                    _setAccessTokenMessage('❌ Error de conexión al crear access token', false);
                }
            }

            async function regenerateAccessToken(id) {
                if (!confirm('¿Regenerar API key? La anterior dejará de funcionar inmediatamente.')) return;
                try {
                    const res = await fetch(`${API_URL}/admin/access-tokens/${id}/regenerate`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        _setAccessTokenMessage('❌ ' + (data.detail || 'No se pudo regenerar'), false);
                        return;
                    }
                    _showNewApiKey(data.api_key || '');
                    _setAccessTokenMessage('✅ API key regenerada correctamente', true);
                    loadAccessTokens();
                } catch (error) {
                    _setAccessTokenMessage('❌ Error de conexión al regenerar', false);
                }
            }

            async function toggleAccessToken(id) {
                try {
                    const res = await fetch(`${API_URL}/admin/access-tokens/${id}/toggle`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        _setAccessTokenMessage('❌ ' + (data.detail || 'No se pudo cambiar estado'), false);
                        return;
                    }
                    _setAccessTokenMessage('✅ Estado actualizado', true);
                    loadAccessTokens();
                } catch (error) {
                    _setAccessTokenMessage('❌ Error de conexión al actualizar estado', false);
                }
            }

            async function deleteAccessToken(id) {
                if (!confirm('¿Eliminar este access token? Esta acción no se puede deshacer.')) return;
                try {
                    const res = await fetch(`${API_URL}/admin/access-tokens/${id}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        _setAccessTokenMessage('❌ ' + (data.detail || 'No se pudo eliminar'), false);
                        return;
                    }
                    _setAccessTokenMessage('✅ Access token eliminado', true);
                    loadAccessTokens();
                } catch (error) {
                    _setAccessTokenMessage('❌ Error de conexión al eliminar', false);
                }
            }
            
            async function loadSectionData(section) {
                switch(section) {
                    case 'status': refresh(); break;
                    case 'holidays': loadHolidays(); break;
                    case 'config': loadConfigTabData(currentConfigTab); break;
                }
            }
            
            async function refresh() {
                try {
                    const res = await fetch('/status', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    
                    if (!res.ok) {
                        if (res.status === 403) {
                            window.location.href = '/login';
                            return;
                        }
                        throw new Error(`HTTP ${res.status}`);
                    }
                    
                    const status = await res.json();
                    lastConnectedStatus = status.connected;  // Actualizar estado para notificaciones
                    
                    const waStatusPill = document.getElementById('waStatusPill');
                    if (waStatusPill) {
                        waStatusPill.textContent = status.connected ? '🟢 WA ON' : '🔴 WA OFF';
                        waStatusPill.classList.toggle('on', status.connected);
                        waStatusPill.classList.toggle('off', !status.connected);
                    }

                    const botStatusPill = document.getElementById('botStatusPill');
                    if (botStatusPill) {
                        const botOn = !status.paused;
                        botStatusPill.textContent = botOn ? '🟢 Bot ON' : '🔴 Bot OFF';
                        botStatusPill.classList.toggle('on', botOn);
                        botStatusPill.classList.toggle('off', !botOn);
                    }

                    // Actualizar botón de pausa
                    const pauseBtn = document.getElementById('pauseBtn');
                    if (pauseBtn) {
                        if (status.paused) {
                            pauseBtn.textContent = '▶️ Activar Bot';
                            pauseBtn.className = 'btn btn-primary';
                        } else {
                            pauseBtn.textContent = '⏸️ Pausar Bot';
                            pauseBtn.className = 'btn btn-pause';
                        }
                    }
                    document.getElementById('chatsToday').textContent = status.chats_today || '0';
                    document.getElementById('hoursIcon').textContent = status.off_hours ? '🕐' : '✅';
                    document.getElementById('hoursStatus').textContent = status.off_hours ? 'Fuera' : 'Normal';
                    document.getElementById('waStatusText').textContent = status.connected ? 'Conectado' : 'Desconectado';
                    const waUptimeEl = document.getElementById('waUptime');
                    if (waUptimeEl) {
                        waUptimeEl.textContent = formatDuration(status.connection_uptime_seconds || 0);
                    }

                    await refreshOpenTicketsCount();
                    
                    const waBtn = document.getElementById('waBtn');
                    if (status.connected) {
                        waBtn.textContent = '✅ WhatsApp Conectado';
                        waBtn.disabled = true;
                        waBtn.classList.add('btn-connected');
                    } else {
                        waBtn.textContent = '🔴 Conectar WhatsApp';
                        waBtn.disabled = false;
                        waBtn.classList.remove('btn-connected');
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }

            async function refreshOpenTicketsCount() {
                try {
                    const res = await fetch('/api/tickets/list', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!res.ok) return;

                    const tickets = await res.json();
                    const openCount = Array.isArray(tickets)
                        ? tickets.filter(t => t.type === 'active').length
                        : 0;

                    const openTicketsEl = document.getElementById('openTicketsCount');
                    if (openTicketsEl) {
                        openTicketsEl.textContent = String(openCount);
                    }
                } catch (error) {
                    console.error('Error loading open tickets count:', error);
                }
            }

            function formatDuration(totalSeconds) {
                const sec = Math.max(0, Number(totalSeconds) || 0);
                const d = Math.floor(sec / 86400);
                const h = Math.floor((sec % 86400) / 3600);
                const m = Math.floor((sec % 3600) / 60);
                const s = sec % 60;

                if (d > 0) return `${d}d ${h}h ${m}m`;
                if (h > 0) return `${h}h ${m}m ${s}s`;
                if (m > 0) return `${m}m ${s}s`;
                return `${s}s`;
            }

            async function toggleBot() {
                const btn = document.getElementById('pauseBtn');
                if (!btn || btn.disabled) return;
                btn.disabled = true;
                const orig = btn.textContent;
                btn.textContent = '⏳ Cambiando...';
                try {
                    const res = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                    const status = await res.json();
                    const endpoint = status.paused ? '/bot/resume' : '/bot/pause';
                    await fetch(endpoint, { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } });
                    await refresh();
                } catch(e) {
                    console.error('toggleBot:', e);
                    btn.textContent = orig;
                } finally {
                    btn.disabled = false;
                }
            }

            async function closeHumanModeFromAdmin() {
                const input = document.getElementById('humanModePhoneAdmin');
                const msg = document.getElementById('humanModeMsgAdmin');
                const phone = (input?.value || '').trim();
                if (!phone) {
                    msg.textContent = '❌ Ingresá un número/chat';
                    msg.style.color = '#ef4444';
                    return;
                }
                try {
                    const res = await fetch(`${API_URL}/human-mode/close`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ phone_number: phone })
                    });
                    const data = await res.json();
                    if (!res.ok) {
                        msg.textContent = '❌ ' + (data.detail || 'No se pudo cerrar modo humano');
                        msg.style.color = '#ef4444';
                        return;
                    }
                    if (data.closed) {
                        msg.textContent = `✅ Chat ${data.phone_number} volvió a modo bot`;
                        msg.style.color = '#86efac';
                        loadAdminParkedList();
                    } else {
                        msg.textContent = 'ℹ️ ' + (data.detail || 'Sin cambios');
                        msg.style.color = '#93c5fd';
                    }
                } catch (error) {
                    msg.textContent = '❌ Error de conexión: ' + error.message;
                    msg.style.color = '#ef4444';
                }
            }

            async function loadAdminParkedList() {
                const container = document.getElementById('parkedListAdmin');
                if (!container) return;
                try {
                    const res = await fetch(`${API_URL}/human-mode/list`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    if (!Array.isArray(data) || data.length === 0) {
                        container.innerHTML = '<div style="color:#86efac; font-size:0.9em;">✅ No hay números en espera</div>';
                        return;
                    }
                    const rows = data.map(item => {
                        const started = item.handoff_started_at ? new Date(item.handoff_started_at + 'Z').toLocaleString('es-AR') : '—';
                        const expire = item.human_mode_expire ? new Date(item.human_mode_expire + 'Z').toLocaleString('es-AR') : '—';
                        const state = item.current_state === 'WAITING_AGENT' ? '⏳ Esperando operador' : '👤 Con operador';
                        const ticket = item.ticket_id || '—';
                        const phoneSafe = item.phone_number.replace(/'/g, "\\'");
                        return `<tr style="border-bottom:1px solid rgba(226,232,240,0.08);">
                            <td style="padding:10px 8px; color:#f1f5f9; font-family:monospace; font-size:0.9em;">${item.phone_number}</td>
                            <td style="padding:10px 8px; color:#94a3b8; font-size:0.85em;">${state}</td>
                            <td style="padding:10px 8px; color:#93c5fd; font-size:0.8em; font-family:monospace;">${ticket}</td>
                            <td style="padding:10px 8px; color:#cbd5e1; font-size:0.8em; max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${item.menu_breadcrumb||'—'}">${item.menu_breadcrumb||'—'}</td>
                            <td style="padding:10px 8px; color:#94a3b8; font-size:0.8em;">${started}</td>
                            <td style="padding:10px 8px; color:#94a3b8; font-size:0.8em;">${expire}</td>
                            <td style="padding:10px 8px; display:flex; gap:6px; flex-wrap:wrap;">
                                <button onclick="adminOpenChatModal('${phoneSafe}','${ticket}')" style="padding:6px 10px; background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.4); color:#93c5fd; border-radius:6px; cursor:pointer; font-size:0.82em;">💬 Chat</button>
                                <button onclick="releaseAdminParked('${phoneSafe}', this)" style="padding:6px 10px; background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4); color:#86efac; border-radius:6px; cursor:pointer; font-size:0.82em;">🔓 Liberar</button>
                            </td>
                        </tr>`;
                    }).join('');
                    container.innerHTML = `<div style="overflow-x:auto;"><table style="width:100%; border-collapse:collapse;">
                        <thead><tr style="background:rgba(30,41,59,0.5);">
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Número</th>
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Estado</th>
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Ticket</th>
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Origen</th>
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Inicio</th>
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Vence</th>
                            <th style="padding:10px 8px; text-align:left; color:#cbd5e1; font-size:0.85em;">Acción</th>
                        </tr></thead>
                        <tbody>${rows}</tbody>
                    </table></div>`;
                } catch(e) {
                    container.innerHTML = '<div style="color:#ef4444; font-size:0.9em;">❌ Error al cargar lista</div>';
                }
            }

            async function releaseAdminParked(phone, btn) {
                btn.disabled = true;
                btn.textContent = '⏳';
                try {
                    const res = await fetch(`${API_URL}/human-mode/close`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: phone, operator_reply: '' })
                    });
                    const data = await res.json();
                    if (data.closed) {
                        loadAdminParkedList();
                    } else {
                        btn.disabled = false;
                        btn.textContent = '🔓 Liberar';
                    }
                } catch(e) {
                    btn.disabled = false;
                    btn.textContent = '🔓 Liberar';
                }
            }

            // --- Admin Chat Modal ---
            let _adminChatPhone = null;

            function _resizeAdminChatTA(el) {
                el.style.height = '22px';
                const lineH = 22;
                const maxH = lineH * 4;
                const newH = Math.min(maxH, el.scrollHeight);
                el.style.height = newH + 'px';
                el.style.overflowY = el.scrollHeight > maxH ? 'auto' : 'hidden';
            }

            function adminOpenChatModal(phone, ticket) {
                _adminChatPhone = phone;
                document.getElementById('adminChatModalTitle').textContent = phone;
                document.getElementById('adminChatModalTicket').textContent = ticket || '—';
                document.getElementById('adminChatModal').style.display = 'flex';
                const ta = document.getElementById('adminChatReplyInput');
                ta.value = ''; ta.style.height = '22px'; ta.style.overflowY = 'hidden';
                document.getElementById('adminChatReplyMsg').textContent = '';
                adminLoadChatMessages();
            }

            function adminCloseChatModal() {
                document.getElementById('adminChatModal').style.display = 'none';
                _adminChatPhone = null;
            }

            async function adminLoadChatMessages() {
                if (!_adminChatPhone) return;
                const box = document.getElementById('adminChatMessages');
                try {
                    const res = await fetch(`${API_URL}/human-mode/messages/${encodeURIComponent(_adminChatPhone)}`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    const msgs = (data.messages || []).slice().sort((a, b) => a.timestamp - b.timestamp);
                    if (!msgs.length) {
                        box.innerHTML = '<div style="color:#8696a0; text-align:center; padding:30px; font-size:0.9em;">Sin mensajes recientes</div>';
                        return;
                    }
                    const wasAtBottom = box.scrollHeight - box.scrollTop <= box.clientHeight + 60;
                    box.innerHTML = msgs.map(m => {
                        const t = m.timestamp ? new Date(m.timestamp * 1000).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}) : '';
                        if (m.from_me) {
                            return `<div style="display:flex;justify-content:flex-end;margin:2px 0;">
                                <div style="background:#005c4b;border-radius:8px 2px 8px 8px;padding:7px 12px 5px;max-width:78%;color:#e9edef;font-size:0.9em;word-break:break-word;">
                                    ${m.body || '<i style="color:#8696a0">[sin texto]</i>'}
                                    <div style="font-size:0.68em;color:#8adfcc;text-align:right;margin-top:3px;">${t}</div>
                                </div></div>`;
                        } else {
                            return `<div style="display:flex;justify-content:flex-start;margin:2px 0;">
                                <div style="background:#202c33;border-radius:2px 8px 8px 8px;padding:7px 12px 5px;max-width:78%;color:#e9edef;font-size:0.9em;word-break:break-word;">
                                    ${m.body || '<i style="color:#8696a0">[sin texto]</i>'}
                                    <div style="font-size:0.68em;color:#8696a0;text-align:right;margin-top:3px;">${t}</div>
                                </div></div>`;
                        }
                    }).join('');
                    if (wasAtBottom) box.scrollTop = box.scrollHeight;
                } catch(e) {
                    box.innerHTML = '<div style="color:#ef4444; font-size:0.9em; text-align:center;">Error al cargar mensajes</div>';
                }
            }

            async function adminSendChatReply() {
                if (!_adminChatPhone) return;
                const input = document.getElementById('adminChatReplyInput');
                const msg = document.getElementById('adminChatReplyMsg');
                const text = input.value.trim();
                if (!text) return;
                input.disabled = true;
                try {
                    const res = await fetch(`${API_URL}/human-mode/reply`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: _adminChatPhone, text: text })
                    });
                    const data = await res.json();
                    if (data.ok) {
                        input.value = ''; input.style.height = '22px'; input.style.overflowY = 'hidden';
                        msg.style.color = '#8adfcc';
                        msg.textContent = '✅ Enviado';
                        setTimeout(() => { msg.textContent = ''; }, 2000);
                        setTimeout(() => adminLoadChatMessages(), 800);
                    } else {
                        msg.style.color = '#f87171';
                        msg.textContent = '❌ Error al enviar';
                    }
                } catch(e) {
                    msg.style.color = '#f87171';
                    msg.textContent = '❌ Error de red';
                } finally {
                    input.disabled = false; input.focus();
                }
            }

            async function adminCloseTicketFromModal() {
                if (!_adminChatPhone) return;
                const btn = document.getElementById('adminChatCloseBtn');
                const msg = document.getElementById('adminChatReplyMsg');
                const reply = document.getElementById('adminChatReplyInput').value.trim();
                btn.disabled = true;
                btn.textContent = '⏳';
                msg.style.color = '#94a3b8';
                msg.textContent = 'Cerrando ticket...';
                try {
                    const res = await fetch(`${API_URL}/human-mode/close`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone_number: _adminChatPhone, operator_reply: reply })
                    });
                    const data = await res.json();
                    if (data.closed) {
                        adminCloseChatModal();
                        loadAdminParkedList();
                    } else {
                        btn.disabled = false;
                        btn.textContent = '🔒 Cerrar Ticket';
                        msg.style.color = '#f87171';
                        msg.textContent = '❌ No se pudo cerrar';
                    }
                } catch(e) {
                    btn.disabled = false;
                    btn.textContent = '🔒 Cerrar Ticket';
                    msg.style.color = '#f87171';
                    msg.textContent = '❌ Error de red';
                }
            }

            // ── MENSAJES PROGRAMADOS (admin) ────────────────────────
""" + _scheduled_messages_shared_js() + """
            let _adminSchedEditId = null;

            const _adminSchedConfig = {
                url: `${API_URL}/scheduled-messages`,
                listId: 'adminSchedList',
                errorText: 'Error al cargar mensajes programados',
                checkUnauth: null,
                actions: {
                    editFn: 'editAdminSched',
                    deleteFn: 'deleteAdminSched'
                },
                modalId: 'adminSchedModal',
                titleId: 'adminSchedModalTitle',
                nameId: 'adminSchedName',
                phoneId: 'adminSchedPhone',
                timeId: 'adminSchedTime',
                messageId: 'adminSchedMsg',
                feedbackId: 'adminSchedModalMsg'
            };

            function _setAdminSchedEditId(value) { _adminSchedEditId = value; }
            async function loadAdminSchedList() { return _loadScheduledMessagesList(_adminSchedConfig); }
            function openAdminSchedModal(sm) { _openScheduledMessagesModal(_adminSchedConfig, sm, _setAdminSchedEditId); }
            function closeAdminSchedModal() { _closeScheduledMessagesModal(_adminSchedConfig, _setAdminSchedEditId); }
            async function saveAdminSchedMsg() { return _saveScheduledMessage(_adminSchedConfig, _adminSchedEditId, () => { closeAdminSchedModal(); loadAdminSchedList(); }); }
            async function toggleAdminSched(id) { return _toggleScheduledMessage(_adminSchedConfig, id, loadAdminSchedList); }
            async function editAdminSched(id) { return _editScheduledMessage(_adminSchedConfig, id, openAdminSchedModal); }
            async function deleteAdminSched(id) { return _deleteScheduledMessage(_adminSchedConfig, id, loadAdminSchedList); }

            let _qrPollTimer = null;

            let _connPollTimer = null;
            let _qrRefreshTimer = null;
            let _qrLastUpdateAt = 0;
            let _lastConnectKickAt = 0;

            async function _fetchAndShowQr() {
                try {
                    const qrRes = await fetch('/qr?ts=' + Date.now());
                    if (qrRes.ok) {
                        const blob = await qrRes.blob();
                        const url = URL.createObjectURL(blob);
                        document.getElementById('qrImage').src = url;
                        document.getElementById('qrImage').style.display = 'block';
                        document.getElementById('qrExpireMsg').style.display = 'block';
                        document.getElementById('qrLoading').style.display = 'none';
                        _qrLastUpdateAt = Date.now();
                        const st = document.getElementById('qrStatus');
                        if (st) st.innerHTML = 'QR listo para escanear<br><small>Se renueva automaticamente</small>';
                        return true;
                    }
                    // 404 = sesión ya conectada o QR no disponible — verificar estado
                    if (qrRes.status === 404 || qrRes.status === 503) {
                        const st = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                        if (st.ok) {
                            const s = await st.json();
                            if (s.connected) {
                                console.log('[QR] Sesión ya conectada, cerrando modal');
                                _closeQrSuccess();
                                return true;
                            }
                        }
                    }
                } catch(e) {}
                return false;
            }

            function _retryQr() {
                document.getElementById('qrError').style.display = 'none';
                document.getElementById('qrLoading').style.display = 'flex';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Solicitando nuevo QR...<br><small>Por favor espera</small>';
                fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                    .catch(e => console.warn('[WA] retry connect:', e));
                _startQrPhase1();
            }

            function _startQrPhase1() {
                if (_qrPollTimer)    { clearInterval(_qrPollTimer);    _qrPollTimer    = null; }
                if (_qrRefreshTimer) { clearInterval(_qrRefreshTimer); _qrRefreshTimer = null; }
                let attempts = 0;
                _qrPollTimer = setInterval(async () => {
                    attempts++;
                    const secs = Math.round(attempts * 1.5);
                    const st = document.getElementById('qrStatus');
                    if (st) st.innerHTML = `Esperando QR... (${secs}s)<br><small>Conectando con WhatsApp</small>`;

                    if (attempts > 240) { // ~6 min max
                        clearInterval(_qrPollTimer); _qrPollTimer = null;
                        document.getElementById('qrLoading').style.display = 'none';
                        document.getElementById('qrError').style.display = 'block';
                        return;
                    }
                    const ok = await _fetchAndShowQr();
                    if (ok) {
                        clearInterval(_qrPollTimer); _qrPollTimer = null;
                        console.log('[QR] Mostrado en intento ' + attempts);
                        // Fase 2: esperar a que el usuario escanee
                        _startConnectPoll();
                        // Renovar QR en intervalos cortos para evitar expiracion silenciosa
                        _qrRefreshTimer = setInterval(async () => {
                            const img = document.getElementById('qrImage');
                            if (!img || img.style.display === 'none') return;
                            console.log('[QR] Renovando QR...');
                            const ok = await _fetchAndShowQr();
                            if (!ok || (Date.now() - _qrLastUpdateAt) > 45000) {
                                const st = document.getElementById('qrStatus');
                                if (st) st.innerHTML = 'Renovando QR...<br><small>No cierres esta ventana</small>';
                                if ((Date.now() - _lastConnectKickAt) > 90000) {
                                    _lastConnectKickAt = Date.now();
                                    fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                                        .catch(e => console.warn('[WA] refresh connect:', e));
                                }
                            }
                        }, 30000);
                    }
                }, 1500);
            }

            function toggleWhatsApp() {
                const btn = document.getElementById('waBtn');
                if (btn && btn.disabled) return;
                if (btn) { btn.disabled = true; btn.textContent = '⏳ Conectando...'; }

                if (lastConnectedStatus === true) {
                    // Ya conectado → solo reconectar, sin mostrar QR
                    if (btn) btn.textContent = '⏳ Reconectando...';
                    fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                        .catch(e => console.warn('[WA] reconnect:', e));
                    setTimeout(() => {
                        if (btn) { btn.disabled = false; btn.textContent = '🟢 Reconectar WhatsApp'; }
                        refresh();
                    }, 5000);
                    return;
                }

                // No conectado: abrir modal YA, sin esperar nada
                _openQrModal();

                // Lanzar /bot/connect en segundo plano (sin await = sin bloquear)
                fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                    .catch(e => console.warn('[WA] connect:', e));

                // Empezar polling de QR inmediatamente
                _startQrPhase1();
                if (btn) btn.disabled = false;
            }

            // Fase 2: polling de /status hasta detectar conexión exitosa
            function _startConnectPoll() {
                if (_connPollTimer) { clearInterval(_connPollTimer); _connPollTimer = null; }
                let connAttempts = 0;
                _connPollTimer = setInterval(async () => {
                    connAttempts++;
                    if (connAttempts > 300) { // hasta ~10 minutos
                        clearInterval(_connPollTimer); _connPollTimer = null;
                        return;
                    }
                    try {
                        const r = await fetch('/status', { headers: { 'Authorization': `Bearer ${token}` } });
                        if (!r.ok) return;
                        const s = await r.json();
                        if (s.connected) {
                            clearInterval(_connPollTimer); _connPollTimer = null;
                            console.log('[QR] ¡Conectado! Cerrando modal...');
                            _closeQrSuccess();
                        }
                    } catch(e) {}
                }, 2000);
            }

            function _closeQrSuccess() {
                closeQrModal();
                // Deshabilitar botón y poner estado conectado
                const btn = document.getElementById('waBtn');
                if (btn) {
                    btn.textContent = '✅ WhatsApp Conectado';
                    btn.disabled = true;
                    btn.classList.add('btn-connected');
                }
                // Toast de éxito
                let toast = document.getElementById('waToast');
                if (!toast) {
                    toast = document.createElement('div');
                    toast.id = 'waToast';
                    toast.className = 'wa-toast';
                    document.body.appendChild(toast);
                }
                toast.textContent = '✅ WhatsApp conectado exitosamente';
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 4000);
                if (typeof refresh === 'function') refresh();
            }

            function _openQrModal() {
                document.getElementById('qrLoading').style.display = 'flex';
                document.getElementById('qrImage').style.display = 'none';
                document.getElementById('qrImage').src = '';
                document.getElementById('qrExpireMsg').style.display = 'none';
                document.getElementById('qrError').style.display = 'none';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Iniciando sesión...<br><small>Por favor espera unos segundos</small>';
                document.getElementById('qrModal').style.display = 'flex';
            }

            function closeQrModal() {
                if (_qrPollTimer)    { clearInterval(_qrPollTimer);    _qrPollTimer    = null; }
                if (_connPollTimer)  { clearInterval(_connPollTimer);  _connPollTimer  = null; }
                if (_qrRefreshTimer) { clearInterval(_qrRefreshTimer); _qrRefreshTimer = null; }
                document.getElementById('qrModal').style.display = 'none';
                document.getElementById('qrLoading').style.display = 'flex';
                document.getElementById('qrImage').style.display = 'none';
                document.getElementById('qrImage').src = '';
                document.getElementById('qrExpireMsg').style.display = 'none';
                document.getElementById('qrError').style.display = 'none';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Iniciando sesión...<br><small>Por favor espera unos segundos</small>';
                // Rehabilitar botón y refrescar estado
                const waBtn = document.getElementById('waBtn');
                if (waBtn) waBtn.disabled = false;
                setTimeout(() => refresh(), 500);
            }

            async function loadUsers() {
                const tbody = document.querySelector('#usersTable');
                if (!tbody) return;
                try {
                    const res = await fetch(`${API_URL}/admin/users`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    const users = await res.json();
                    tbody.innerHTML = users.map(u => `
                        <tr style="border-bottom: 1px solid rgba(226, 232, 240, 0.05);">
                            <td style="padding: 12px; color: #cbd5e1;">${u.username}</td>
                            <td style="padding: 12px; color: #cbd5e1;">${u.email || '-'}</td>
                            <td style="padding: 12px; color: #cbd5e1;">${u.is_admin ? '👑 Admin' : '👤 Usuario'}</td>
                            <td style="padding: 12px; color: #cbd5e1;">
                                <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.85em;" onclick="toggleUserActive(${u.id}, ${u.is_active})">
                                    ${u.is_active ? '✅ Activo' : '❌ Inactivo'}
                                </button>
                            </td>
                            <td style="padding: 12px; color: #cbd5e1;">
                                <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.85em;" onclick="toggleUserPause(${u.id}, ${u.is_paused})">
                                    ${u.is_paused ? '⏸️ En Pausa' : '▶️ Activo'}
                                </button>
                            </td>
                            <td style="padding: 12px;">
                                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.85em;" onclick="openChangePasswordModal(${u.id}, '${u.username}')">🔑</button>
                                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.85em;" onclick="openDeleteUserModal(${u.id}, '${u.username}')">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    `).join('');
                } catch (error) {
                    console.error('Error loading users:', error);
                    const msg = document.getElementById('usersMessage');
                    msg.textContent = '❌ Error al cargar usuarios';
                    msg.className = 'message show error';
                }
            }
            
            function toggleSatFields() {
                const enabled = document.getElementById('satEnabled').checked;
                document.getElementById('satFields').style.display = enabled ? '' : 'none';
            }

            function toggleSunFields() {
                const enabled = document.getElementById('sunEnabled').checked;
                document.getElementById('sunFields').style.display = enabled ? '' : 'none';
            }

            async function loadConfig() {
                try {
                    const res = await fetch(`${API_URL}/config`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const config = await res.json();
                    
                    document.getElementById('solutionName').value = config.solution_name || '';
                    document.getElementById('openingTime').value = config.opening_time || '09:00';
                    document.getElementById('closingTime').value = config.closing_time || '18:00';
                    document.getElementById('satOpeningTime').value = config.sat_opening_time || '10:00';
                    document.getElementById('satClosingTime').value = config.sat_closing_time || '14:00';
                    const satEnabled = config.sat_enabled !== false;
                    document.getElementById('satEnabled').checked = satEnabled;
                    document.getElementById('satFields').style.display = satEnabled ? '' : 'none';
                    const sunEnabled = !!config.sun_enabled;
                    document.getElementById('sunEnabled').checked = sunEnabled;
                    document.getElementById('sunFields').style.display = sunEnabled ? '' : 'none';
                    if (document.getElementById('handoffMessage')) {
                        document.getElementById('handoffMessage').value = config.handoff_message || '';
                    }
                    if (document.getElementById('farewellMessage')) {
                        document.getElementById('farewellMessage').value = config.farewell_message || '';
                    }
                    // Bloqueados: filtros
                    const cfEl = document.getElementById('countryFilter');
                    const afEl = document.getElementById('areaFilter');
                    const cfeEl = document.getElementById('countryFilterEnabled');
                    const afeEl = document.getElementById('areaFilterEnabled');
                    if (cfEl) cfEl.value = config.country_codes || '';
                    if (afEl) afEl.value = config.area_codes || '';
                    if (cfeEl) cfeEl.checked = !!config.country_filter_enabled;
                    if (afeEl) afeEl.checked = !!config.area_filter_enabled;
                } catch (error) {
                    console.error('Error loading config:', error);
                }
            }

            async function loadTicketMessages() {
                try {
                    const res = await fetch(`${API_URL}/config`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const config = await res.json();

                    const handoffEl = document.getElementById('handoffMessage');
                    const farewellEl = document.getElementById('farewellMessage');
                    if (handoffEl) handoffEl.value = config.handoff_message || '';
                    if (farewellEl) farewellEl.value = config.farewell_message || '';
                } catch (error) {
                    console.error('Error loading ticket messages:', error);
                }
            }
            
            async function saveConfig(e) {
                e.preventDefault();
                try {
                    const handoffEl = document.getElementById('handoffMessage');
                    const farewellEl = document.getElementById('farewellMessage');
                    const res = await fetch(`${API_URL}/config`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            solution_name: document.getElementById('solutionName').value,
                            opening_time: document.getElementById('openingTime').value,
                            closing_time: document.getElementById('closingTime').value,
                            sat_opening_time: document.getElementById('satOpeningTime').value,
                            sat_closing_time: document.getElementById('satClosingTime').value,
                            sat_enabled: document.getElementById('satEnabled').checked,
                            sun_enabled: document.getElementById('sunEnabled').checked,
                            handoff_message: handoffEl ? handoffEl.value : undefined,
                            farewell_message: farewellEl ? farewellEl.value : undefined
                        })
                    });
                    
                    const msg = document.getElementById('configMessage');
                    if (res.ok) {
                        msg.textContent = '✅ Configuración guardada correctamente';
                        msg.className = 'message show success';
                    } else {
                        msg.textContent = '❌ Error al guardar';
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    console.error('Error:', error);
                }
            }

            async function saveTicketMessages(e) {
                e.preventDefault();
                try {
                    const res = await fetch(`${API_URL}/config`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            handoff_message: document.getElementById('handoffMessage').value,
                            farewell_message: document.getElementById('farewellMessage').value
                        })
                    });

                    const msg = document.getElementById('ticketMessagesMessage');
                    if (res.ok) {
                        msg.textContent = '✅ Mensajes de ticket guardados correctamente';
                        msg.className = 'message show success';
                    } else {
                        msg.textContent = '❌ Error al guardar los mensajes de ticket';
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    const msg = document.getElementById('ticketMessagesMessage');
                    msg.textContent = '❌ Error de conexión: ' + error.message;
                    msg.className = 'message show error';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                    console.error('Error:', error);
                }
            }
            
            async function loadMenu() {
                try {
                    const res = await fetch(`${API_URL}/config/menu`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    originalMenuContent = data.menu || '# Menú Principal\\n\\nBienvenido a nuestro menú.';
                    document.getElementById('menuContent').value = originalMenuContent;
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function saveMenu(e) {
                e.preventDefault();
                try {
                    const res = await fetch(`${API_URL}/config/menu`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            content: document.getElementById('menuContent').value
                        })
                    });
                    
                    const msg = document.getElementById('menuMessage');
                    const data = await res.json();
                    
                    if (res.ok) {
                        originalMenuContent = document.getElementById('menuContent').value;
                        msg.textContent = '✅ Menú guardado correctamente (' + data.bytes + ' bytes)';
                        msg.className = 'message show success';
                    } else {
                        msg.textContent = '❌ Error: ' + (data.error || 'Error al guardar');
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    const msg = document.getElementById('menuMessage');
                    msg.textContent = '❌ Error de conexión: ' + error.message;
                    msg.className = 'message show error';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                    console.error('Error:', error);
                }
            }

            async function restoreMenuBackup() {
                if (!confirm('¿Restaurar la versión anterior del menú?')) return;
                try {
                    const res = await fetch(`${API_URL}/config/menu/restore`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    const msg = document.getElementById('menuMessage');
                    const data = await res.json();
                    if (!res.ok) {
                        msg.textContent = '❌ Error: ' + (data.detail || data.error || 'No se pudo restaurar');
                        msg.className = 'message show error';
                        setTimeout(() => msg.classList.remove('show'), 3000);
                        return;
                    }

                    await loadMenu();
                    msg.textContent = '✅ Menú restaurado a la versión anterior';
                    msg.className = 'message show success';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    const msg = document.getElementById('menuMessage');
                    msg.textContent = '❌ Error de conexión: ' + error.message;
                    msg.className = 'message show error';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                    console.error('Error:', error);
                }
            }
            
            function resetMenuEditor() {
                document.getElementById('menuContent').value = originalMenuContent;
                const msg = document.getElementById('menuMessage');
                msg.textContent = '↺ Cambios deshechados';
                msg.className = 'message show success';
                setTimeout(() => msg.classList.remove('show'), 2000);
            }
            
            async function loadOffhours() {
                try {
                    const res = await fetch(`${API_URL}/config/offhours`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    originalOffhoursContent = data.off_hours_message || 'Lo sentimos, estamos fuera de horario.';
                    originalOffhoursEnabled = data.off_hours_enabled || false;
                    document.getElementById('offhoursContent').value = originalOffhoursContent;
                    document.getElementById('offhoursEnabled').checked = originalOffhoursEnabled;
                    toggleOffhoursState();
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            function toggleOffhoursState() {
                const enabled = document.getElementById('offhoursEnabled').checked;
                document.getElementById('offhoursContent').disabled = !enabled;
                document.getElementById('offhoursContent').style.opacity = enabled ? '1' : '0.5';
            }
            
            async function saveOffhours(e) {
                e.preventDefault();
                try {
                    const enabled = document.getElementById('offhoursEnabled').checked;
                    const res = await fetch(`${API_URL}/config`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            off_hours_enabled: enabled,
                            off_hours_message: document.getElementById('offhoursContent').value
                        })
                    });
                    
                    const msg = document.getElementById('offhoursMessage');
                    const data = await res.json();
                    
                    if (res.ok) {
                        originalOffhoursContent = document.getElementById('offhoursContent').value;
                        msg.textContent = '✅ Configuración de fuera de hora guardada correctamente';
                        msg.className = 'message show success';
                    } else {
                        msg.textContent = '❌ Error: ' + (data.detail || data.error || 'Error al guardar');
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    const msg = document.getElementById('offhoursMessage');
                    msg.textContent = '❌ Error de conexión: ' + error.message;
                    msg.className = 'message show error';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                    console.error('Error:', error);
                }
            }

            async function restoreOffhoursBackup() {
                if (!confirm('¿Restaurar la versión anterior de fuera de hora?')) return;
                try {
                    const res = await fetch(`${API_URL}/config/offhours/restore`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    const msg = document.getElementById('offhoursMessage');
                    const data = await res.json();
                    if (!res.ok) {
                        msg.textContent = '❌ Error: ' + (data.detail || data.error || 'No se pudo restaurar');
                        msg.className = 'message show error';
                        setTimeout(() => msg.classList.remove('show'), 3000);
                        return;
                    }

                    await loadOffhours();
                    msg.textContent = '✅ Fuera de hora restaurado a la versión anterior';
                    msg.className = 'message show success';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    const msg = document.getElementById('offhoursMessage');
                    msg.textContent = '❌ Error de conexión: ' + error.message;
                    msg.className = 'message show error';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                    console.error('Error:', error);
                }
            }
            
            function resetOffhoursEditor() {
                document.getElementById('offhoursContent').value = originalOffhoursContent;
                document.getElementById('offhoursEnabled').checked = originalOffhoursEnabled;
                toggleOffhoursState();
                const msg = document.getElementById('offhoursMessage');
                msg.textContent = '↺ Cambios deshechados';
                msg.className = 'message show success';
                setTimeout(() => msg.classList.remove('show'), 2000);
            }
            
            async function addHolidayManual(e) {
                e.preventDefault();
                try {
                    const res = await fetch(`${API_URL}/holidays`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            date: document.getElementById('holidayDate').value,
                            name: document.getElementById('holidayName').value
                        })
                    });
                    
                    if (res.ok) {
                        document.getElementById('holidayDate').value = '';
                        document.getElementById('holidayName').value = '';
                        loadHolidays();
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function saveFilters() {
                const messageEl = document.getElementById('blocklistMessage');
                try {
                    const country_codes = document.getElementById('countryFilter').value.trim();
                    const area_codes = document.getElementById('areaFilter').value.trim();
                    const country_filter_enabled = document.getElementById('countryFilterEnabled').checked;
                    const area_filter_enabled = document.getElementById('areaFilterEnabled').checked;

                    messageEl.innerHTML = '<div style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6;">⏳ Guardando filtros...</div>';

                    const res = await fetch(`${API_URL}/config`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            country_filter_enabled,
                            country_codes: country_codes || null,
                            area_filter_enabled,
                            area_codes: area_codes || null
                        })
                    });

                    if (res.ok) {
                        messageEl.innerHTML = '<div style="background: rgba(34, 197, 94, 0.2); color: #86efac; padding: 12px; border-radius: 8px; border-left: 4px solid #22c55e;">✅ Filtros guardados correctamente</div>';
                    } else {
                        const err = await res.json().catch(() => ({}));
                        messageEl.innerHTML = `<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">❌ Error al guardar: ${err.detail || res.status}</div>`;
                    }
                    setTimeout(() => { if (messageEl) messageEl.innerHTML = ''; }, 4000);
                } catch (error) {
                    console.error('Error saving filters:', error);
                    messageEl.innerHTML = `<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">❌ Error: ${error.message}</div>`;
                }
            }

            async function loadBlocklist() {
                try {
                    const res = await fetch(`${API_URL}/blocklist`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!res.ok) {
                        throw new Error(`HTTP error! status: ${res.status}`);
                    }
                    const blocked = await res.json();
                    
                    const tbody = document.querySelector('#blocklistTable');
                    if (blocked.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 20px; color: #94a3b8;">No hay números bloqueados</td></tr>';
                    } else {
                        tbody.innerHTML = blocked.map(b => `
                            <tr style="border-bottom: 1px solid rgba(226, 232, 240, 0.05);">
                                <td style="padding: 12px; color: #cbd5e1;">${b.phone_number}</td>
                                <td style="padding: 12px; color: #cbd5e1;">${b.reason}</td>
                                <td style="padding: 12px; text-align: right;">
                                    <button onclick="deleteBlock(${b.id})" style="background: #dc2626; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85em; transition: background 0.3s;">
                                        Desbloquear
                                    </button>
                                </td>
                            </tr>
                        `).join('');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('blocklistMessage').innerHTML = '<div style="background: rgba(220, 38, 38, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #dc2626;">❌ Error al cargar lista de bloqueados</div>';
                }
            }
            
            async function blockNumber(e) {
                e.preventDefault();
                const phoneInput = document.getElementById('blockNumber');
                const reasonInput = document.getElementById('blockReason');
                const messageEl = document.getElementById('blocklistMessage');
                
                // Validación
                const phone = phoneInput.value.trim();
                const reason = reasonInput.value.trim();
                
                if (!phone) {
                    messageEl.innerHTML = '<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">⚠️ Ingresa un número de teléfono</div>';
                    return;
                }
                
                // Solo verificar que sean caracteres numéricos válidos (con o sin +, @c.us, espacios)
                const digits = phone.replace(/[^0-9]/g, '');
                if (digits.length < 7) {
                    messageEl.innerHTML = '<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">⚠️ El número parece inválido</div>';
                    return;
                }
                
                if (!reason) {
                    messageEl.innerHTML = '<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">⚠️ Ingresa una razón para el bloqueo</div>';
                    return;
                }
                
                try {
                    messageEl.innerHTML = '<div style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6;">⏳ Agregando número a blocklist...</div>';
                    
                    const res = await fetch(`${API_URL}/blocklist`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            phone_number: phone,
                            reason: reason
                        })
                    });
                    
                    if (res.ok) {
                        const result = await res.json();
                        phoneInput.value = '';
                        reasonInput.value = '';
                        messageEl.innerHTML = '<div style="background: rgba(34, 197, 94, 0.2); color: #86efac; padding: 12px; border-radius: 8px; border-left: 4px solid #22c55e;">✅ Número bloqueado exitosamente</div>';
                        setTimeout(() => loadBlocklist(), 500);
                    } else {
                        const error = await res.json();
                        messageEl.innerHTML = `<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">❌ Error: ${error.detail || 'No se pudo bloquear el número'}</div>`;
                    }
                } catch (error) {
                    console.error('Error:', error);
                    messageEl.innerHTML = `<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">❌ Error al agregar a blocklist: ${error.message}</div>`;
                }
            }
            
            async function deleteBlock(blockId) {
                if (!confirm('¿Estás seguro de que deseas desbloquear este número?')) {
                    return;
                }
                
                try {
                    const messageEl = document.getElementById('blocklistMessage');
                    messageEl.innerHTML = '<div style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6;">⏳ Desbloqueando número...</div>';
                    
                    const res = await fetch(`${API_URL}/blocklist/${blockId}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    
                    if (res.ok) {
                        messageEl.innerHTML = '<div style="background: rgba(34, 197, 94, 0.2); color: #86efac; padding: 12px; border-radius: 8px; border-left: 4px solid #22c55e;">✅ Número desbloqueado exitosamente</div>';
                        setTimeout(() => loadBlocklist(), 500);
                    } else {
                        const error = await res.json();
                        messageEl.innerHTML = `<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">❌ Error: ${error.detail || 'No se pudo desbloquear'}</div>`;
                    }
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('blocklistMessage').innerHTML = `<div style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444;">❌ Error al desbloquear: ${error.message}</div>`;
                }
            }
            
            function logout() {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }

            // ========== ESTADO DE WAHA ==========

            async function refreshWahaStatus() {
                try {
                    const res = await fetch(`${API_URL}/waha/status`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    renderWahaStatus(data);
                } catch (error) {
                    document.getElementById('wahaContent').innerHTML = `
                        <div style="color: #ef4444; text-align: center; padding: 20px;">
                            ❌ Error al cargar: ${error.message}
                        </div>
                    `;
                }
            }

            function renderWahaStatus(data) {
                const connected = data.connected;
                const session = data.session || {};

                // Estado principal
                const statusHtml = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                        <div style="background: rgba(${connected ? '34,197,94' : '239,68,68'}, 0.15); border: 1px solid rgba(${connected ? '34,197,94' : '239,68,68'}, 0.3); padding: 20px; border-radius: 12px; text-align: center;">
                            <div style="font-size: 2em; margin-bottom: 8px;">${connected ? '🟢' : '🔴'}</div>
                            <div style="color: #94a3b8; font-size: 0.85em;">Conexión</div>
                            <div style="font-size: 1.2em; font-weight: 600; color: ${connected ? '#86efac' : '#fca5a5'};">${connected ? 'CONECTADO' : 'DESCONECTADO'}</div>
                        </div>
                        <div style="background: rgba(59,130,246, 0.15); border: 1px solid rgba(59,130,246, 0.3); padding: 20px; border-radius: 12px; text-align: center;">
                            <div style="font-size: 2em; margin-bottom: 8px;">📡</div>
                            <div style="color: #94a3b8; font-size: 0.85em;">Estado</div>
                            <div style="font-size: 1.2em; font-weight: 600; color: #93c5fd;">${session.status || 'UNKNOWN'}</div>
                        </div>
                        <div style="background: rgba(168,85,247, 0.15); border: 1px solid rgba(168,85,247, 0.3); padding: 20px; border-radius: 12px; text-align: center;">
                            <div style="font-size: 2em; margin-bottom: 8px;">🤖</div>
                            <div style="color: #94a3b8; font-size: 0.85em;">Engine</div>
                            <div style="font-size: 1.2em; font-weight: 600; color: #d8b4fe;">${session.engine || 'N/A'}</div>
                        </div>
                        <div style="background: rgba(234,179,8, 0.15); border: 1px solid rgba(234,179,8, 0.3); padding: 20px; border-radius: 12px; text-align: center;">
                            <div style="font-size: 2em; margin-bottom: 8px;">⏱️</div>
                            <div style="color: #94a3b8; font-size: 0.85em;">Uptime</div>
                            <div style="font-size: 1.2em; font-weight: 600; color: #fde047;">${formatUptime(data.uptime_seconds || 0)}</div>
                        </div>
                    </div>

                    ${connected && session.me ? `
                        <div style="background: rgba(34,197,94, 0.1); border: 1px solid rgba(34,197,94, 0.2); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <div style="width: 48px; height: 48px; background: rgba(34,197,94, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5em;">👤</div>
                                <div>
                                    <div style="font-weight: 600; color: #86efac;">${session.me.pushName || 'Usuario'}</div>
                                    <div style="color: #94a3b8; font-size: 0.85em;">${session.me.id || 'N/A'}</div>
                                </div>
                            </div>
                        </div>
                    ` : ''}

                    ${!connected && data.qr_available ? `
                        <div style="text-align: center; padding: 20px;">
                            <div style="color: #fbbf24; font-size: 1.1em; margin-bottom: 16px;">⚠️ QR Disponible - Escanea para conectar</div>
                            <img src="/qr?ts=${Date.now()}" alt="QR Code" style="max-width: 300px; border: 2px solid rgba(251,191,36, 0.3); border-radius: 12px;" />
                        </div>
                    ` : ''}

                    ${!connected && !data.qr_available ? `
                        <div style="text-align: center; padding: 20px; color: #94a3b8;">
                            ${session.status === 'STARTING' ? '⏳ WAHA está iniciando...' : 'Presiona "Conectar/Reiniciar" para iniciar sesión'}
                        </div>
                    ` : ''}
                `;

                document.getElementById('wahaContent').innerHTML = statusHtml;

                // Información raw
                document.getElementById('wahaRawInfo').textContent = JSON.stringify(data, null, 2);

                // Actualizar botones
                document.getElementById('btnConnectWaha').disabled = connected;
                document.getElementById('btnLogoutWaha').disabled = !connected;
            }

            function formatUptime(seconds) {
                const hrs = Math.floor(seconds / 3600);
                const mins = Math.floor((seconds % 3600) / 60);
                const secs = seconds % 60;
                if (hrs > 0) return `${hrs}h ${mins}m`;
                if (mins > 0) return `${mins}m ${secs}s`;
                return `${secs}s`;
            }

            async function connectWaha() {
                if (!confirm('¿Reiniciar sesión de WAHA? Esto puede requerir escanear QR.')) return;

                try {
                    const btn = document.getElementById('btnConnectWaha');
                    btn.disabled = true;
                    btn.textContent = '⏳ Conectando...';

                    const res = await fetch('/bot/connect', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    const data = await res.json();

                    if (data.ok) {
                        document.getElementById('wahaContent').innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div class="spinner"></div>
                                <p style="margin-top: 16px; color: #94a3b8;">Iniciando sesión...</p>
                            </div>
                        `;
                        setTimeout(refreshWahaStatus, 3000);
                    } else {
                        alert('Error al conectar: ' + JSON.stringify(data));
                        btn.disabled = false;
                        btn.textContent = '🔌 Conectar/Reiniciar';
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                    document.getElementById('btnConnectWaha').disabled = false;
                    document.getElementById('btnConnectWaha').textContent = '🔌 Conectar/Reiniciar';
                }
            }

            async function logoutWaha() {
                if (!confirm('⚠️ ¿Cerrar sesión de WAHA? Tendrás que escanear QR nuevamente.')) return;

                try {
                    const btn = document.getElementById('btnLogoutWaha');
                    btn.disabled = true;
                    btn.textContent = '⏳ Cerrando...';

                    const res = await fetch('/bot/logout', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    const data = await res.json();

                    if (data.ok) {
                        document.getElementById('wahaContent').innerHTML = `
                            <div style="text-align: center; padding: 40px; color: #fbbf24;">
                                <div style="font-size: 3em; margin-bottom: 16px;">🚪</div>
                                <p>Sesión cerrada. Escanea el QR para reconectar.</p>
                            </div>
                        `;
                        setTimeout(refreshWahaStatus, 2000);
                    } else {
                        alert('Error: ' + JSON.stringify(data));
                        btn.disabled = false;
                        btn.textContent = '🚪 Logout (Borrar QR)';
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                    document.getElementById('btnLogoutWaha').disabled = false;
                    document.getElementById('btnLogoutWaha').textContent = '🚪 Logout (Borrar QR)';
                }
            }

            // ========== FUNCIONES DE USUARIOS ==========
            
            function openCreateUserModal() {
                document.getElementById('createUserModal').style.display = 'flex';
                document.getElementById('newUsername').focus();
            }
            
            function closeCreateUserModal() {
                document.getElementById('createUserModal').style.display = 'none';
                document.getElementById('newUsername').value = '';
                document.getElementById('newEmail').value = '';
                document.getElementById('newPassword').value = '';
                document.getElementById('newFullName').value = '';
                document.getElementById('newIsAdmin').checked = false;
            }
            
            async function createNewUser(e) {
                e.preventDefault();
                
                const username = document.getElementById('newUsername').value.trim();
                const email = document.getElementById('newEmail').value.trim();
                const password = document.getElementById('newPassword').value;
                const fullName = document.getElementById('newFullName').value.trim();
                const isAdmin = document.getElementById('newIsAdmin').checked;
                
                if (!username || !password) {
                    alert('Usuario y contraseña son requeridos');
                    return;
                }
                
                try {
                    const res = await fetch(`${API_URL}/admin/users`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username,
                            email: email || null,
                            password,
                            full_name: fullName || null,
                            is_admin: isAdmin
                        })
                    });
                    
                    const msg = document.getElementById('usersMessage');
                    if (res.ok) {
                        msg.textContent = '✅ Usuario creado correctamente';
                        msg.className = 'message show success';
                        closeCreateUserModal();
                        loadUsers();
                    } else {
                        const error = await res.json();
                        msg.textContent = '❌ ' + (error.detail || 'Error al crear usuario');
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    console.error('Error:', error);
                    const msg = document.getElementById('usersMessage');
                    msg.textContent = '❌ Error de conexión';
                    msg.className = 'message show error';
                }
            }
            
            function openChangePasswordModal(userId, username) {
                document.getElementById('changePasswordModal').style.display = 'flex';
                document.getElementById('changePasswordTitle').textContent = `Cambiar Contraseña - ${username}`;
                document.getElementById('changePasswordUserId').value = userId;
                document.getElementById('newPasswordValue').value = '';
                document.getElementById('confirmPasswordValue').value = '';
                document.getElementById('newPasswordValue').focus();
            }
            
            function closeChangePasswordModal() {
                document.getElementById('changePasswordModal').style.display = 'none';
            }
            
            async function saveNewPassword(e) {
                e.preventDefault();
                
                const userId = parseInt(document.getElementById('changePasswordUserId').value);
                const newPassword = document.getElementById('newPasswordValue').value;
                const confirmPassword = document.getElementById('confirmPasswordValue').value;
                
                if (!newPassword || newPassword.length < 4) {
                    alert('La contraseña debe tener al menos 4 caracteres');
                    return;
                }
                
                if (newPassword !== confirmPassword) {
                    alert('Las contraseñas no coinciden');
                    return;
                }
                
                try {
                    const res = await fetch(`${API_URL}/admin/users/${userId}/reset-password`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            new_password: newPassword
                        })
                    });
                    
                    const msg = document.getElementById('usersMessage');
                    if (res.ok) {
                        msg.textContent = '✅ Contraseña actualizada correctamente';
                        msg.className = 'message show success';
                        closeChangePasswordModal();
                        loadUsers();
                    } else {
                        const error = await res.json();
                        msg.textContent = '❌ ' + (error.detail || 'Error al cambiar contraseña');
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    console.error('Error:', error);
                    const msg = document.getElementById('usersMessage');
                    msg.textContent = '❌ Error de conexión';
                    msg.className = 'message show error';
                }
            }
            
            function openDeleteUserModal(userId, username) {
                document.getElementById('deleteUserModal').style.display = 'flex';
                document.getElementById('deleteUsernamePlaceholder').textContent = username;
                document.getElementById('deleteUserModal').dataset.userId = userId;
            }
            
            function closeDeleteUserModal() {
                document.getElementById('deleteUserModal').style.display = 'none';
            }
            
            async function confirmDeleteUser() {
                const userId = parseInt(document.getElementById('deleteUserModal').dataset.userId);
                
                try {
                    const res = await fetch(`${API_URL}/admin/users/${userId}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const msg = document.getElementById('usersMessage');
                    if (res.ok) {
                        msg.textContent = '✅ Usuario eliminado correctamente';
                        msg.className = 'message show success';
                        closeDeleteUserModal();
                        loadUsers();
                    } else {
                        const error = await res.json();
                        msg.textContent = '❌ ' + (error.detail || 'Error al eliminar usuario');
                        msg.className = 'message show error';
                    }
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    console.error('Error:', error);
                    const msg = document.getElementById('usersMessage');
                    msg.textContent = '❌ Error de conexión';
                    msg.className = 'message show error';
                }
            }
            
            async function toggleUserActive(userId, isActive) {
                try {
                    const res = await fetch(`${API_URL}/admin/users/${userId}`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            is_active: !isActive
                        })
                    });
                    
                    if (res.ok) {
                        loadUsers();
                    } else {
                        alert('Error al cambiar estado del usuario');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error de conexión');
                }
            }
            
            async function toggleUserPause(userId, isPaused) {
                try {
                    const res = await fetch(`${API_URL}/admin/users/${userId}/toggle-pause`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (res.ok) {
                        loadUsers();
                    } else {
                        alert('Error al cambiar pausa del usuario');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error de conexión');
                }
            }
            
            // Cargar versión del servidor
            async function loadVersion() {
                try {
                    const res = await fetch('/version');
                    if (res.ok) {
                        const data = await res.json();
                        const dv = document.getElementById('dashboardVersion');
                        if (dv) dv.textContent = data.version;
                        const uv = document.getElementById('userPanelVersion');
                        if (uv) uv.textContent = data.version;
                    }
                } catch (e) {
                    console.log('Version not available:', e);
                }
            }
            loadVersion();
            refresh();
            loadAdminParkedList();
            loadAdminSchedList();
            setInterval(refresh, 5000);
            setInterval(loadAdminParkedList, 15000);

            function _escapeSchedMsgAttr(text) {
                const tempDiv = document.createElement('div');
                tempDiv.textContent = text || '';
                return tempDiv.innerHTML.replace(/"/g, '&quot;');
            }

            function _getSelectedSchedChatText(containerSelector) {
                const checkboxes = document.querySelectorAll(`${containerSelector} .msg-cb:checked`);
                if (!checkboxes.length) return '';
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = Array.from(checkboxes).map(cb => cb.value).join('\\n\\n');
                return tempDiv.textContent.trim();
            }
        
            // TICKETS LOGIC
            let currentTickets = [];
            let currentChatPhone = "";
            let currentChatTicketId = "";

            async function loadTickets() {
                try {
                    const res = await fetch('/api/tickets/list', {
                        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token')}
                    });
                    if(res.ok) {
                        currentTickets = await res.json();
                        renderTickets();
                    }
                } catch(e) { console.error(e); }
            }

            function renderTickets() {
                const grid = document.getElementById('ticketsGrid');
                if(!currentTickets.length) {
                    grid.innerHTML = '<div class="empty-state">No hay tickets</div>';
                    return;
                }
                
                let html = '';
                currentTickets.forEach(t => {
                    let badgeColor = '#64748b';
                    if (t.status === 'pendiente') badgeColor = '#f59e0b';
                    if (t.status === 'confirmado') badgeColor = '#10b981';
                    if (t.status === 'cancelado') badgeColor = '#ef4444';
                    if (t.status === 'timeout')   badgeColor = '#ef4444';
                    
                    let statusLabel = t.status.toUpperCase();
                    if(t.is_deleted) statusLabel += ' (BORRADO por ' + (t.deleted_by || 'Unknown') + ')';
                    
                    let schedBadge = t.has_scheduled_message ? '<span style="background: rgba(139,92,246,0.2); color: #c4b5fd; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-left: 8px;">⏳ Programado</span>' : '';

                    html += `
                        <div class="ticket-row">
                            <div class="ticket-info">
                                <div class="ticket-id">${t.ticket_id || '-'} | Tel: ${t.phone_number} ${schedBadge}</div>
                                <div class="ticket-status" style="color: ${badgeColor}; font-weight: 500;">
                                    ${statusLabel} | Origen: ${t.menu_section || '-'}
                                </div>
                                <div style="font-size: 0.75em; color: #64748b; margin-top: 4px;">
                                    Abierto: ${t.opened_at ? new Date(t.opened_at).toLocaleString() : '-'}
                                </div>
                            </div>
                            <div class="ticket-actions">
                                <button class="btn btn-secondary btn-sm" onclick="viewTicket('${t.id}')">Ver Chat</button>
                            </div>
                        </div>
                    `;
                });
                grid.innerHTML = html;
            }

            async function viewTicket(tid) {
                const t = currentTickets.find(x => x.id === tid);
                if(!t) return;
                
                currentChatPhone = t.phone_number;
                currentChatTicketId = tid;
                
                document.getElementById('chatModalTitle').textContent = `Chat: ${t.phone_number} (${t.status})`;
                document.getElementById('chatContent').innerHTML = '<div class="spinner-text">Cargando mensajes desde WAHA...</div>';
                document.getElementById('chatModal').classList.add('show');
                
                // Actions
                let actionsHtml = '';
                if (!t.is_deleted) {
                    if (t.status === 'pendiente') {
                        actionsHtml += `<button class="btn btn-primary btn-sm" onclick="actionTicket('fin')">Fin</button>`;
                    }
                    if (t.status === 'timeout') {
                        actionsHtml += `<button class="btn btn-primary btn-sm" onclick="actionTicket('resume')">Retomar</button>`;
                    }
                    actionsHtml += `<button class="btn btn-danger btn-sm" onclick="actionTicket('delete')">Borrar (Cancelar)</button>`;
                }
                document.getElementById('chatModalActions').innerHTML = actionsHtml;
                
                // fetch messages
                try {
                    const res = await fetch(`/api/human-mode/messages/${encodeURIComponent(t.phone_number)}`, {
                        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token')}
                    });
                    if(res.ok) {
                        const data = await res.json();
                        const msgs = Array.isArray(data) ? data : (data.messages || []);
                        let chtml = '';
                        if(!msgs || msgs.length === 0) {
                            chtml = '<div class="empty-state">No hay mensajes recientes en WAHA</div>';
                        } else {
                            // msgs might be an array of Waha message objects
                            msgs.forEach(m => {
                                const isBot = m.from_me || m.fromMe;
                                const align = isBot ? 'right' : 'left';
                                const bg = isBot ? 'rgba(59,130,246,0.2)' : 'rgba(30,41,59,0.8)';
                                const text = m.body || m.text || (typeof m === "string" ? m : JSON.stringify(m));
                                const tempDiv = document.createElement('div');
                                tempDiv.textContent = text;
                                const escapedText = tempDiv.innerHTML.replace(/"/g, '&quot;');
                                chtml += `<div style="text-align: ${align}; margin-bottom: 8px; display: flex; align-items: center; justify-content: ${isBot ? 'flex-end' : 'flex-start'};">
                                    ${!isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-right:8px; cursor:pointer;" title="Seleccionar para recordatorio">` : ''}
                                    <div style="display: inline-block; background: ${bg}; padding: 8px 12px; border-radius: 8px; max-width: 80%; word-break: break-word; text-align: left;">
                                        ${text}
                                    </div>
                                    ${isBot ? `<input type="checkbox" class="msg-cb" value="${escapedText}" style="margin-left:8px; cursor:pointer;" title="Seleccionar para recordatorio">` : ''}
                                </div>`;
                            });
                        }
                        document.getElementById('chatContent').innerHTML = chtml;
                        document.getElementById('chatContent').scrollTop = document.getElementById('chatContent').scrollHeight;
                    } else {
                        document.getElementById('chatContent').innerHTML = '<div class="empty-state">No se pudieron cargar los mensajes.</div>';
                    }
                } catch(e) {
                    document.getElementById('chatContent').innerHTML = '<div class="empty-state">Error cargando mensajes.</div>';
                }
            }

            function closeChatModal() { document.getElementById('chatModal').classList.remove('show'); }

            async function actionTicket(action) {
                if(action === 'delete') {
                    if(!confirm("¿Seguro que quieres borrar este ticket?")) return;
                }
                try {
                    const res = await fetch('/api/tickets/action', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: JSON.stringify({ action: action, id: currentChatTicketId })
                    });
                    if(res.ok) {
                        closeChatModal();
                        loadTickets();
                    } else {
                        alert("Error ejecutando accion");
                    }
                } catch(e){ console.error(e); }
            }

            function openScheduleModal() {
                document.getElementById('schedPhone').value = currentChatPhone;
                document.getElementById('schedName').value = '';
                document.getElementById('schedTime').value = '';
                
                const checkboxes = document.querySelectorAll('#chatContent .msg-cb:checked');
                const selectedText = Array.from(checkboxes).map(cb => cb.value).join('\\n\\n');
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = selectedText;
                
                document.getElementById('schedMessage').value = tempDiv.textContent;
                document.getElementById('scheduleModal').classList.add('show');
            }

            function closeScheduleModal() { document.getElementById('scheduleModal').classList.remove('show'); }

            async function saveScheduledMessage() {
                const phone = document.getElementById('schedPhone').value;
                const name = document.getElementById('schedName').value;
                const time = document.getElementById('schedTime').value;
                const msg = document.getElementById('schedMessage').value;
                
                if(!name || !time || !msg) { alert("Completar todos los campos"); return; }
                
                try {
                    const res = await fetch('/api/scheduled-messages', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('token')
                        },
                        body: JSON.stringify({
                            name: name,
                            phone_number: phone,
                            send_time: time,
                            message: msg,
                            days_of_week: "1,2,3,4,5,6,7",
                            is_active: true
                        })
                    });
                    if(res.ok) {
                        closeScheduleModal();
                        loadTickets(); // refresh to show scheduled message badge
                        showToast("Mensaje agendado");
                    }
                } catch(e) { console.error(e); }
            }

            // Hook loadTickets into switchSection if section is tickets
            const originalSwitchSection = window.switchSection || function(){};
            window.switchSection = function(sectionId, el) {
                // update navigation UI if using elements
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                if(el) el.classList.add('active');
                else {
                    const selector = document.querySelector(`.nav-item[onclick*="'${sectionId}'"]`);
                    if(selector) selector.classList.add('active');
                }
                // hide all sections
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                
                // show target
                const target = document.getElementById(sectionId + 'Section') || document.getElementById(sectionId);
                if(target) target.classList.add('active');
                
                if(sectionId === 'tickets') loadTickets();
                else originalSwitchSection(sectionId, el);
            };

            </script>
    </body>
    </html>
    """

# Ahora reemplazar la función get_dashboard_page() en pages.py
