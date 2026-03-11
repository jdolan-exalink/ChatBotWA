"""
Funciones para renderizar las HTML pages del sistema
Diseño moderno, minimalista y tecnológico
"""

def get_login_page() -> str:
    """Login minimalista y moderno"""
    return """
    <!DOCTYPE html>
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
            
            .submit-btn:active {
                transform: translateY(0);
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
                text-align: center;
                color: #3b82f6;
                margin-top: 20px;
                font-size: 0.95em;
            }
            
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(59, 130, 246, 0.2);
                border-top-color: #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 8px;
                vertical-align: middle;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
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
                        Ver: <span id="versionDisplay">2.2.1</span>
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
                    
                    // Intentar parsear JSON
                    let data = null;
                    let errorDetail = 'Error desconocido';
                    
                    try {
                        data = await response.json();
                        errorDetail = data.detail || data.message || 'Error en el servidor';
                    } catch (parseError) {
                        console.error('[LOGIN] No se puede parsear JSON:', parseError);
                        // Si no es JSON válido, es un error del servidor
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
                    
                    // Redirigir según rol
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
            
            // Obtener versión del servidor
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
            
            // Focus en username al cargar
            document.getElementById('username').focus();
            loadVersion();
        </script>
    </body>
    </html>
    """

def get_user_panel_page() -> str:
    """Panel simplificado para usuarios regulares"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mi Panel - ChatBot WA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                min-height: 100vh;
                padding: 20px;
                color: #e2e8f0;
            }
            
            .container {
                max-width: 700px;
                margin: 0 auto;
            }
            
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
            }
            
            .header h1 {
                font-size: 2em;
                font-weight: 700;
                background: linear-gradient(135deg, #3b82f6, #06b6d4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .nav-buttons {
                display: flex;
                gap: 10px;
            }
            
            .nav-btn {
                padding: 8px 16px;
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                color: #93c5fd;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.3s ease;
            }
            
            .nav-btn:hover {
                background: rgba(59, 130, 246, 0.2);
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
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 16px;
                margin-bottom: 30px;
            }
            
            .status-card {
                background: rgba(18, 24, 40, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 16px;
                padding: 20px;
                text-align: center;
            }
            
            .status-icon {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .status-label {
                font-size: 0.85em;
                color: #94a3b8;
                margin-bottom: 8px;
            }
            
            .status-value {
                font-size: 1em;
                color: #f1f5f9;
                font-weight: 600;
            }
            
            .card {
                background: rgba(18, 24, 40, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 16px;
                padding: 32px;
                margin-bottom: 24px;
            }
            
            .card h2 {
                font-size: 1.3em;
                margin-bottom: 24px;
                color: #f1f5f9;
            }
            
            .toggle-btn {
                width: 100%;
                padding: 16px;
                border: none;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 16px;
            }
            
            .toggle-btn.active {
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }
            
            .toggle-btn.paused {
                background: linear-gradient(135deg, #f59e0b, #d97706);
                color: white;
            }
            
            .toggle-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
            }
            
            .btn-connect {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-connect:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(6, 182, 212, 0.3);
            }
            .btn-connect:disabled {
                cursor: default;
                opacity: 0.85;
            }
            .btn-connect.connected {
                background: linear-gradient(135deg, #16a34a, #15803d);
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
            
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            
            .modal.show {
                display: flex;
            }
            
            .modal-content {
                background: rgba(18, 24, 40, 0.95);
                border: 1px solid rgba(226, 232, 240, 0.1);
                border-radius: 20px;
                padding: 40px;
                max-width: 400px;
                width: 90%;
                text-align: center;
            }
            
            .modal-content h3 {
                color: #f1f5f9;
                margin-bottom: 20px;
            }
            
            .qr-image {
                margin: 20px 0;
                max-width: 100%;
                border-radius: 12px;
                border: 2px solid rgba(226, 232, 240, 0.1);
            }
            
            .modal-close {
                display: inline-block;
                padding: 8px 16px;
                background: rgba(239, 68, 68, 0.1);
                color: #fca5a5;
                border: 1px solid rgba(244, 63, 94, 0.5);
                border-radius: 8px;
                cursor: pointer;
                margin-top: 20px;
            }
            
            .panel-footer {
                text-align: center;
                padding: 32px 20px;
                margin-top: 40px;
                border-top: 1px solid rgba(226, 232, 240, 0.1);
            }
            
            .panel-footer .company {
                color: #cbd5e1;
                font-weight: 600;
                margin-bottom: 4px;
            }
            
            .panel-footer .version {
                color: #64748b;
                font-size: 0.85em;
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
            .btn-disabled { opacity: 0.6; cursor: not-allowed !important; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💬 Mi Panel</h1>
                <div class="nav-buttons">
                    <button class="nav-btn" onclick="window.location.href='/user-config'">⚙️ Configuración</button>
                    <button class="logout-btn" onclick="logout()">Desconectar</button>
                </div>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-icon" id="waIcon">🔴</div>
                    <div class="status-label">WhatsApp</div>
                    <div class="status-value" id="waStatus">Desconect.</div>
                </div>
                <div class="status-card">
                    <div class="status-icon" id="botIcon">⏸️</div>
                    <div class="status-label">Bot</div>
                    <div class="status-value" id="botStatus">Pausado</div>
                </div>
                <div class="status-card">
                    <div class="status-icon" id="hoursIcon">✅</div>
                    <div class="status-label">Horarios</div>
                    <div class="status-value" id="hoursStatus">Normal</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">🤖</div>
                    <div class="status-label">Solución</div>
                    <div class="status-value" id="solutionName">—</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Control del Bot</h2>
                <button class="toggle-btn" id="toggleBtn" onclick="toggleBot()">▶️ Activar Bot</button>
            </div>

            <div class="card">
                <h2>WhatsApp</h2>
                <button class="btn-connect" id="waBtn" onclick="toggleWhatsApp()">🔴 Conectar WhatsApp</button>
            </div>
            
            <div class="panel-footer">
                <div class="company">DOLAN SS - 2026</div>
                <div class="version" id="userPanelVersion">v2.2.1</div>
            </div>
        </div>
        
        <!-- Modal QR -->
        <div class="modal" id="qrModal">
            <div class="modal-content">
                <h3>📱 Conectar WhatsApp</h3>
                <p style="color: #cbd5e1; margin-bottom: 8px;">Escanea el código QR desde tu WhatsApp</p>
                <div class="qr-loading" id="qrLoading">
                    <div class="spinner"></div>
                    <p class="spinner-text" id="qrStatus">Iniciando sesión...<br><small>Por favor espera unos segundos</small></p>
                </div>
                <img id="qrImage" class="qr-image" src="" alt="QR Code" style="display:none;">
                <p id="qrExpireMsg" style="display:none; color:#94a3b8; font-size:0.8em; margin-top:6px;">⏱️ El QR se renueva automáticamente</p>
                <div id="qrError" style="display:none; color:#ef4444; padding:16px 0;">
                    ❌ No se pudo obtener el QR.<br>
                    <button onclick="_retryQr()" style="margin-top:12px; padding:8px 20px; background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.4); color:#93c5fd; border-radius:8px; cursor:pointer; font-size:0.9em;">🔄 Reintentar</button>
                </div>
                <button class="modal-close" onclick="closeQrModal()">✖ Cerrar</button>
            </div>
        </div>
        
        <script>
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
            
            // Validar autenticación al cargar la página
            window.addEventListener('DOMContentLoaded', function() {
                const token = localStorage.getItem('token');
                if (!token) {
                    window.location.href = '/login';
                    return;
                }
                requestNotificationPermission();
                loadStatus();
                
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
            });
            
            async function loadStatus() {
                try {
                    const token = localStorage.getItem('token');
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
                    
                    // Estado WhatsApp
                    const connected = status.connected;
                    document.getElementById('waIcon').textContent = connected ? '🟢' : '🔴';
                    document.getElementById('waStatus').textContent = connected ? 'Conectado' : 'Desconectado';
                    
                    // Estado Bot
                    const isPaused = status.paused;
                    if (!connected) {
                        document.getElementById('botIcon').textContent = '🔴';
                        document.getElementById('botStatus').textContent = 'Desconectado';
                    } else if (isPaused) {
                        document.getElementById('botIcon').textContent = '⏸️';
                        document.getElementById('botStatus').textContent = 'Pausado';
                    } else {
                        document.getElementById('botIcon').textContent = '▶️';
                        document.getElementById('botStatus').textContent = 'Activo';
                    }
                    
                    // Horarios
                    document.getElementById('hoursIcon').textContent = status.off_hours ? '🕐' : '✅';
                    document.getElementById('hoursStatus').textContent = status.off_hours ? 'Fuera' : 'Normal';
                    
                    // Solución
                    document.getElementById('solutionName').textContent = status.solution_name || '—';
                    
                    // Botón toggle del bot
                    const toggleBtn = document.getElementById('toggleBtn');
                    if (isPaused) {
                        toggleBtn.textContent = '▶️ Activar Bot';
                        toggleBtn.classList.remove('active');
                        toggleBtn.classList.add('paused');
                    } else {
                        toggleBtn.textContent = '⏸️ Pausar Bot';
                        toggleBtn.classList.add('active');
                        toggleBtn.classList.remove('paused');
                    }
                    
                    // Botón WhatsApp
                    const waBtn = document.getElementById('waBtn');
                    if (connected) {
                        waBtn.textContent = '✅ WhatsApp Conectado';
                        waBtn.disabled = true;
                        waBtn.classList.add('connected');
                    } else {
                        waBtn.textContent = '🔴 Conectar WhatsApp';
                        waBtn.disabled = false;
                        waBtn.classList.remove('connected');
                    }
                } catch (error) {
                    console.error('Error al cargar estado:', error);
                }
            }
            
            async function toggleBot() {
                const btn = document.getElementById('toggleBtn');
                if (!btn || btn.disabled) return;
                btn.disabled = true;
                btn.classList.add('btn-disabled');
                const origText = btn.textContent;
                btn.textContent = '⏳ Cambiando...';
                try {
                    const token = localStorage.getItem('token');
                    const res = await fetch('/status', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const status = await res.json();
                    const endpoint = status.paused ? '/bot/resume' : '/bot/pause';
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (response.ok) {
                        await loadStatus();
                    } else {
                        btn.textContent = origText;
                    }
                } catch (error) {
                    console.error('toggleBot error:', error);
                    btn.textContent = origText;
                } finally {
                    btn.disabled = false;
                    btn.classList.remove('btn-disabled');
                }
            }
            
            async function changePassword() {
                try {
                    const oldPassword = document.getElementById('oldPassword').value;
                    const newPassword = document.getElementById('newPassword').value;
                    const confirmPassword = document.getElementById('confirmPassword').value;
                    const statusDiv = document.getElementById('passwordStatus');
                    
                    if (!oldPassword || !newPassword || !confirmPassword) {
                        statusDiv.textContent = '❌ Por favor completa todos los campos';
                        statusDiv.style.color = '#ef4444';
                        return;
                    }
                    
                    if (newPassword !== confirmPassword) {
                        statusDiv.textContent = '❌ Las contraseñas no coinciden';
                        statusDiv.style.color = '#ef4444';
                        return;
                    }
                    
                    if (newPassword.length < 6) {
                        statusDiv.textContent = '❌ La contraseña debe tener al menos 6 caracteres';
                        statusDiv.style.color = '#ef4444';
                        return;
                    }
                    
                    const token = localStorage.getItem('token');
                    const response = await fetch('/api/auth/change-password', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            old_password: oldPassword,
                            new_password: newPassword
                        })
                    });
                    
                    if (response.ok) {
                        statusDiv.textContent = '✅ Contraseña actualizada correctamente';
                        statusDiv.style.color = '#10b981';
                        document.getElementById('oldPassword').value = '';
                        document.getElementById('newPassword').value = '';
                        document.getElementById('confirmPassword').value = '';
                        setTimeout(() => { statusDiv.textContent = ''; }, 3000);
                    } else {
                        const error = await response.json();
                        statusDiv.textContent = '❌ ' + (error.detail || 'Error al cambiar contraseña');
                        statusDiv.style.color = '#ef4444';
                    }
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('passwordStatus').textContent = '❌ Error al cambiar contraseña';
                    document.getElementById('passwordStatus').style.color = '#ef4444';
                }
            }
            
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
                        const token = localStorage.getItem('token');
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
                const token = localStorage.getItem('token');
                document.getElementById('qrError').style.display = 'none';
                document.getElementById('qrLoading').style.display = 'flex';
                const st = document.getElementById('qrStatus');
                if (st) st.innerHTML = 'Solicitando nuevo QR...<br><small>Por favor espera</small>';
                // Asegurar sesión en segundo plano — sin bloquear
                fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                    .catch(e => console.warn('[WA] retry connect:', e));
                _startQrPhase1(token);
            }

            function _startQrPhase1(token) {
                if (_qrPollTimer) { clearInterval(_qrPollTimer); _qrPollTimer = null; }
                if (_qrRefreshTimer) { clearInterval(_qrRefreshTimer); _qrRefreshTimer = null; }
                let attempts = 0;
                _qrPollTimer = setInterval(async () => {
                    attempts++;
                    // Update status text so user sees progress
                    const secs = Math.round(attempts * 0.8);
                    const st = document.getElementById('qrStatus');
                    if (st) st.innerHTML = `Esperando QR... (${secs}s)<br><small>Conectando con WhatsApp</small>`;

                    if (attempts > 450) { // ~6 min max
                        clearInterval(_qrPollTimer); _qrPollTimer = null;
                        document.getElementById('qrLoading').style.display = 'none';
                        document.getElementById('qrError').style.display = 'block';
                        return;
                    }
                    const ok = await _fetchAndShowQr();
                    if (ok) {
                        clearInterval(_qrPollTimer); _qrPollTimer = null;
                        console.log('[QR] Mostrado en intento ' + attempts);
                        // Fase 2: esperar scan + auto-refresh QR cada 50s
                        _startConnectPoll(token);
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
                }, 800);
            }

            function toggleWhatsApp() {
                const btn = document.getElementById('waBtn');
                const token = localStorage.getItem('token');
                if (btn && btn.disabled) return;
                if (btn) { btn.disabled = true; btn.textContent = '⏳ Conectando...'; }

                if (lastConnectedStatus === true) {
                    // Ya conectado → solo reconectar, sin mostrar QR
                    if (btn) btn.textContent = '⏳ Reconectando...';
                    fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                        .catch(e => console.warn('[WA] reconnect:', e));
                    setTimeout(() => {
                        if (btn) { btn.disabled = false; btn.textContent = '🟢 Reconectar WhatsApp'; }
                        loadStatus();
                    }, 5000);
                    return;
                }

                // No conectado: abrir modal YA, sin esperar nada
                _openQrModal();

                // Lanzar /bot/connect en segundo plano (sin await = sin bloquear)
                fetch('/bot/connect', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } })
                    .catch(e => console.warn('[WA] connect:', e));

                // Empezar polling de QR inmediatamente
                _startQrPhase1(token);
                if (btn) btn.disabled = false;
            }

            // Fase 2: polling de /status hasta detectar conexión exitosa
            function _startConnectPoll(token) {
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
                    btn.classList.add('connected');
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
                // Refrescar estado del panel
                if (typeof loadStatus === 'function') loadStatus();
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
                if (_qrPollTimer)   { clearInterval(_qrPollTimer);   _qrPollTimer   = null; }
                if (_connPollTimer) { clearInterval(_connPollTimer); _connPollTimer = null; }
                if (_qrRefreshTimer){ clearInterval(_qrRefreshTimer); _qrRefreshTimer = null; }
                document.getElementById('qrModal').classList.remove('show');
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
                setTimeout(() => loadStatus(), 500);
            }

            function logout() {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
            
            // Cargar versión del servidor
            async function loadVersion() {
                try {
                    const res = await fetch('/version');
                    if (res.ok) {
                        const data = await res.json();
                        const versionEl = document.getElementById('userPanelVersion');
                        if (versionEl) {
                            versionEl.textContent = data.version;
                        }
                    }
                } catch (e) {
                    console.log('Version not available:', e);
                }
            }
            
            loadVersion();
            loadStatus();
            setInterval(loadStatus, 5000);
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
            document.getElementById('calTitle').textContent = MONTHS[mo] + ' ' + yr;

            const todayStr = fmtDate(new Date());
            const grid = document.getElementById('calGrid');
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
                padding: 20px;
                border-top: 1px solid rgba(226, 232, 240, 0.1);
                background: rgba(15, 23, 42, 0.95);
                text-align: center;
                font-size: 0.85em;
            }
            
            .sidebar-footer .company {
                color: #cbd5e1;
                font-weight: 600;
                margin-bottom: 4px;
            }
            
            .sidebar-footer .version {
                color: #64748b;
                font-size: 0.75em;
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
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🤖 WA-BOT</h2>
                <p>Admin</p>
            </div>
            
            <div class="nav-item active" onclick="switchSection('status')">📊 Estado</div>
            <div class="nav-item" onclick="switchSection('users')">👥 Usuarios</div>
            <div class="nav-item" onclick="switchSection('config')">⚙️ Configuración</div>
            <div class="nav-item" onclick="switchSection('waha')">📡 WAHA</div>
            <div class="nav-item" onclick="switchSection('menu')">📋 Editor Menú</div>
            <div class="nav-item" onclick="switchSection('offhours')">🕐 Fuera de Hora</div>
            <div class="nav-item" onclick="switchSection('holidays')">📅 Feriados</div>
            <div class="nav-item" onclick="switchSection('blocklist')">🚫 Bloqueados</div>
            
            <div class="sidebar-footer">
                <div class="company">DOLAN SS - 2026</div>
                <div class="version" id="dashboardVersion">v2.2.1</div>
            </div>
        </div>
        
        <div class="main">
            <div class="header">
                <h1>Dashboard Administrativo</h1>
                <button class="logout-btn" onclick="logout()">Desconectar</button>
            </div>
            
            <!-- ESTADO -->
            <div id="status" class="section active">
                <div class="card">
                    <h2>🎯 Estado del Sistema</h2>
                    <div class="status-grid">
                        <div class="status-item">
                            <div class="status-item-icon" id="waIcon">🔴</div>
                            <div class="status-item-label">WhatsApp</div>
                            <div class="status-item-value" id="waStatus">Desconectado</div>
                        </div>
                        <div class="status-item">
                            <div class="status-item-icon" id="botIcon">▶️</div>
                            <div class="status-item-label">Bot</div>
                            <div class="status-item-value" id="botStatus">Activo</div>
                        </div>
                        <div class="status-item">
                            <div class="status-item-icon">📞</div>
                            <div class="status-item-label">Chats Hoy</div>
                            <div class="status-item-value" id="chatsToday">0</div>
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
                    <button class="btn btn-primary" onclick="refresh()">🔄 Actualizar Estado</button>
                    <button class="btn" id="pauseBtn" onclick="toggleBot()" style="margin-left:10px;">⏸️ Pausar Bot</button>
                </div>
                
                <div class="card">
                    <h2>🔌 Gestión de WhatsApp</h2>
                    <p style="color: #cbd5e1; margin-bottom: 16px;">Estado: <strong id="waStatusText">Desconectado</strong></p>
                    <button class="btn btn-primary" id="waBtn" onclick="toggleWhatsApp()">🔴 Conectar WhatsApp</button>
                </div>
            </div>
            
            <!-- USUARIOS -->
            <div id="users" class="section">
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
            
            <!-- CONFIGURACIÓN -->
            <div id="config" class="section">
                <div class="card">
                    <h2>⚙️ Configuración del Bot</h2>
                    <div class="message" id="configMessage"></div>
                    <form onsubmit="saveConfig(event)">
                        <div class="form-group">
                            <label>Nombre de la Solución</label>
                            <input type="text" id="solutionName" placeholder="Clínica">
                        </div>
                        
                        <div class="form-group">
                            <label>Título del Menú</label>
                            <input type="text" id="menuTitle" placeholder="Menú Principal">
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
                        
                        <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                            <h3 style="color: #f1f5f9; margin-bottom: 12px;">🔧 Modo de Operación</h3>
                            <label style="display: flex; align-items: flex-start; gap: 10px; cursor: pointer;">
                                <input type="checkbox" id="debugMode" style="margin-top: 3px; width: 16px; height: 16px; flex-shrink: 0;">
                                <div>
                                    <span style="color: #f1f5f9; font-weight: 500;">Modo Debug</span>
                                    <p style="color: #94a3b8; font-size: 0.85em; margin: 4px 0 0;">
                                        Activado: logs detallados (horarios, webhooks, conexión).<br>
                                        Desactivado <em>(recomendado)</em>: solo chats entrantes y errores.
                                    </p>
                                </div>
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">💾 Guardar Configuración</button>
                    </form>
                </div>
            </div>

            <!-- ESTADO DE WAHA -->
            <div id="waha" class="section">
                <div class="card">
                    <h2>📡 Estado de WAHA</h2>
                    <div id="wahaContent">
                        <div style="text-align: center; padding: 40px;">
                            <div class="spinner"></div>
                            <p style="margin-top: 16px; color: #94a3b8;">Cargando información de WAHA...</p>
                        </div>
                    </div>
                    <div style="margin-top: 24px; display: flex; gap: 12px;">
                        <button onclick="refreshWahaStatus()" class="btn btn-primary">🔄 Actualizar</button>
                        <button onclick="connectWaha()" class="btn btn-secondary" id="btnConnectWaha">🔌 Conectar/Reiniciar</button>
                        <button onclick="logoutWaha()" class="btn btn-danger" id="btnLogoutWaha">🚪 Logout (Borrar QR)</button>
                    </div>
                </div>

                <div class="card" style="margin-top: 24px;">
                    <h3>📊 Información de la Sesión</h3>
                    <pre id="wahaRawInfo" style="background: rgba(0,0,0,0.3); padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 0.85em; color: #94a3b8;"></pre>
                </div>
            </div>

            <!-- EDITOR DE MENÚ -->
            <div id="menu" class="section">
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
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- MENÚ FUERA DE HORA -->
            <div id="offhours" class="section">
                <div class="card">
                    <h2>🕐 Menú Fuera de Hora</h2>
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
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- FERIADOS -->
            <div id="holidays" class="section">
                <div class="card">
                    <h2>📅 Calendario de Feriados</h2>
                    <div class="message" id="holidaysMessage"></div>
                    
                    <div class="calendar">
                        <div class="calendar-header">
                            <button class="btn btn-secondary" style="padding: 4px 12px;" onclick="prevMonth()">◀</button>
                            <h3 id="calendarMonth">Marzo 2026</h3>
                            <button class="btn btn-secondary" style="padding: 4px 12px;" onclick="nextMonth()">▶</button>
                        </div>
                        <div class="calendar-grid" id="calendarGrid"></div>
                    </div>
                    
                    <button class="btn btn-primary" onclick="saveHolidays()" style="width: 100%; margin-bottom: 16px;">💾 Guardar Feriados</button>
                    
                    <form onsubmit="addHolidayManual(event)" style="margin-top: 20px;">
                        <h3 style="color: #f1f5f9; margin-bottom: 12px;">Agregar Manual</h3>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Fecha (YYYY-MM-DD)</label>
                                <input type="date" id="holidayDate">
                            </div>
                            <div class="form-group">
                                <label>Nombre</label>
                                <input type="text" id="holidayName" placeholder="Ej: Navidad">
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">➕ Agregar Feriado</button>
                    </form>
                </div>
            </div>
            
            <!-- BLOQUEADOS -->
            <div id="blocklist" class="section">
                <div class="card">
                    <h2>🚫 Números Bloqueados y Filtros</h2>
                    <div class="message" id="blocklistMessage"></div>
                    
                    <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #f1f5f9; margin-bottom: 12px;">🌍 Filtro por País</h3>
                        <div class="form-group">
                            <label>Códigos de País (separados por coma, ej: +54, +55)</label>
                            <input type="text" id="countryFilter" placeholder="+54, +55, +56">
                        </div>
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" id="countryFilterEnabled" style="width: auto; margin-right: 8px;">
                            <span>Aplicar filtro: rechazar solo números con estos países</span>
                        </label>
                    </div>
                    
                    <div style="background: rgba(30, 41, 59, 0.3); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: #f1f5f9; margin-bottom: 12px;">📍 Filtro por Localidad</h3>
                        <div class="form-group">
                            <label>Patrones de Localidad (separados por coma)</label>
                            <input type="text" id="areaFilter" placeholder="(XXX), [XXX]">
                        </div>
                        <label style="display: flex; align-items: center; cursor: pointer;">
                            <input type="checkbox" id="areaFilterEnabled" style="width: auto; margin-right: 8px;">
                            <span>Aplicar filtro: rechazar solo números con estas áreas</span>
                        </label>
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
                const userStr = localStorage.getItem('user');
                
                if (!token) {
                    window.location.href = '/login';
                    return;
                }
                
                try {
                    const user = JSON.parse(userStr);
                    if (!user.is_admin) {
                        // Usuario sin permisos - redirigir a user-panel
                        window.location.href = '/user-panel';
                        return;
                    }
                } catch (e) {
                    // Error parsing user data
                    window.location.href = '/login';
                    return;
                }
                
                refresh();
            });
            
            let currentMonth = new Date();
            let selectedDates = new Set();
            let originalMenuContent = '';
            let originalOffhoursContent = '';
            let originalOffhoursEnabled = false;
            
            function switchSection(section) {
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                document.getElementById(section).classList.add('active');
                event.target.classList.add('active');
                loadSectionData(section);
            }
            
            async function loadSectionData(section) {
                switch(section) {
                    case 'status': refresh(); break;
                    case 'users': loadUsers(); break;
                    case 'config': loadConfig(); break;
                    case 'waha': refreshWahaStatus(); break;
                    case 'menu': loadMenu(); break;
                    case 'offhours': loadOffhours(); break;
                    case 'holidays': loadHolidays(); break;
                    case 'blocklist': loadBlocklist(); break;
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
                    
                    document.getElementById('waIcon').textContent = status.connected ? '🟢' : '🔴';
                    document.getElementById('waStatus').textContent = status.connected ? 'Conectado' : 'Desconectado';
                    document.getElementById('botIcon').textContent = status.paused ? '⏸️' : '▶️';
                    document.getElementById('botStatus').textContent = status.paused ? 'Pausado' : 'Activo';
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
                try {
                    const res = await fetch(`${API_URL}/admin/users`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const users = await res.json();
                    
                    const tbody = document.querySelector('#usersTable');
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
                    document.getElementById('menuTitle').value = config.menu_title || '';
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
                    document.getElementById('debugMode').checked = !!config.debug_mode;
                } catch (error) {
                    console.error('Error loading config:', error);
                }
            }
            
            async function saveConfig(e) {
                e.preventDefault();
                try {
                    const res = await fetch(`${API_URL}/config`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            solution_name: document.getElementById('solutionName').value,
                            menu_title: document.getElementById('menuTitle').value,
                            opening_time: document.getElementById('openingTime').value,
                            closing_time: document.getElementById('closingTime').value,
                            sat_opening_time: document.getElementById('satOpeningTime').value,
                            sat_closing_time: document.getElementById('satClosingTime').value,
                            sat_enabled: document.getElementById('satEnabled').checked,
                            sun_enabled: document.getElementById('sunEnabled').checked,
                            debug_mode: document.getElementById('debugMode').checked
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
            
            async function loadMenu() {
                try {
                    const res = await fetch(`${API_URL}/config`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const config = await res.json();
                    originalMenuContent = config.menu_content || '# Menú Principal\\n\\nBienvenido a nuestro menú.';
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
            
            function resetMenuEditor() {
                document.getElementById('menuContent').value = originalMenuContent;
                const msg = document.getElementById('menuMessage');
                msg.textContent = '↺ Cambios deshechados';
                msg.className = 'message show success';
                setTimeout(() => msg.classList.remove('show'), 2000);
            }
            
            async function loadOffhours() {
                try {
                    const res = await fetch(`${API_URL}/config`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const config = await res.json();
                    originalOffhoursContent = config.off_hours_message || 'Lo sentimos, estamos fuera de horario.';
                    originalOffhoursEnabled = config.off_hours_enabled || false;
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
            
            function resetOffhoursEditor() {
                document.getElementById('offhoursContent').value = originalOffhoursContent;
                document.getElementById('offhoursEnabled').checked = originalOffhoursEnabled;
                toggleOffhoursState();
                const msg = document.getElementById('offhoursMessage');
                msg.textContent = '↺ Cambios deshechados';
                msg.className = 'message show success';
                setTimeout(() => msg.classList.remove('show'), 2000);
            }
            
            function renderCalendar() {
                const year = currentMonth.getFullYear();
                const month = currentMonth.getMonth();
                
                document.getElementById('calendarMonth').textContent = currentMonth.toLocaleDateString('es-ES', { year: 'numeric', month: 'long' });
                
                const firstDay = new Date(year, month, 1);
                const lastDay = new Date(year, month + 1, 0);
                const daysInMonth = lastDay.getDate();
                const startingDayOfWeek = firstDay.getDay();
                
                let calendarHTML = '';
                const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sab'];
                days.forEach(day => {
                    calendarHTML += `<div class="calendar-day-header">${day}</div>`;
                });
                
                for (let i = 0; i < startingDayOfWeek; i++) {
                    calendarHTML += '<div class="calendar-day other-month"></div>';
                }
                
                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    const isMarked = selectedDates.has(dateStr);
                    calendarHTML += `
                        <div class="calendar-day ${isMarked ? 'marked' : ''}" onclick="toggleHolidayDate('${dateStr}')" style="color: ${isMarked ? 'white' : '#f1f5f9'};">
                            ${day}
                        </div>
                    `;
                }
                
                document.getElementById('calendarGrid').innerHTML = calendarHTML;
            }
            
            function prevMonth() {
                currentMonth.setMonth(currentMonth.getMonth() - 1);
                renderCalendar();
            }
            
            function nextMonth() {
                currentMonth.setMonth(currentMonth.getMonth() + 1);
                renderCalendar();
            }
            
            function toggleHolidayDate(dateStr) {
                if (selectedDates.has(dateStr)) {
                    selectedDates.delete(dateStr);
                } else {
                    selectedDates.add(dateStr);
                }
                renderCalendar();
            }
            
            async function loadHolidays() {
                try {
                    const res = await fetch(`${API_URL}/holidays`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const holidays = await res.json();
                    
                    selectedDates.clear();
                    holidays.forEach(h => {
                        selectedDates.add(h.date);
                    });
                    
                    currentMonth = new Date();
                    renderCalendar();
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function saveHolidays() {
                try {
                    const holidaysArray = Array.from(selectedDates).map(date => ({
                        date: date,
                        name: 'Feriado'
                    }));
                    
                    // Aquí idealmente llamarías a un endpoint para guardar todos los feriados de una vez
                    // Por ahora, guardo cada uno individualmente
                    for (const h of holidaysArray) {
                        await fetch(`${API_URL}/holidays`, {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                date: h.date,
                                name: h.name
                            })
                        });
                    }
                    
                    const msg = document.getElementById('holidaysMessage');
                    msg.textContent = '✅ Feriados guardados correctamente';
                    msg.className = 'message show success';
                    setTimeout(() => msg.classList.remove('show'), 3000);
                } catch (error) {
                    console.error('Error:', error);
                }
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

                    const res = await fetch(`${API_URL}/bot/connect`, {
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

                    const res = await fetch(`${API_URL}/bot/logout`, {
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
                        document.getElementById('dashboardVersion').textContent = data.version;
                        document.getElementById('userPanelVersion').textContent = data.version;
                    }
                } catch (e) {
                    console.log('Version not available:', e);
                }
            }
            
            loadVersion();
            refresh();
            setInterval(refresh, 5000);
        </script>
    </body>
    </html>
    """

# Ahora reemplazar la función get_dashboard_page() en pages.py
