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
                        Ver: 1.0.0
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
                    const response = await fetch(`${API_URL}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Credenciales inválidas');
                    }
                    
                    const data = await response.json();
                    localStorage.setItem('token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    // Redirigir según rol
                    setTimeout(() => {
                        if (data.user.is_admin) {
                            window.location.href = '/dashboard';
                        } else {
                            window.location.href = '/user-panel';
                        }
                    }, 500);
                    
                } catch (error) {
                    errorMsg.textContent = error.message;
                    errorMsg.classList.add('show');
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                }
            });
            
            // Focus en username al cargar
            document.getElementById('username').focus();
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
            
            .btn-connect:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(6, 182, 212, 0.3);
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💬 Mi Panel</h1>
                <div class="nav-buttons">
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
        </div>
        
        <!-- Modal QR -->
        <div class="modal" id="qrModal">
            <div class="modal-content">
                <h3>Escanea el QR</h3>
                <p style="color: #cbd5e1; margin-bottom: 20px;">Escanea este código QR desde tu teléfono para conectar WhatsApp</p>
                <img id="qrImage" class="qr-image" src="" alt="QR Code">
                <button class="modal-close" onclick="closeQrModal()">Cerrar</button>
            </div>
        </div>
        
        <script>
            // Validar autenticación al cargar la página
            window.addEventListener('DOMContentLoaded', function() {
                const token = localStorage.getItem('token');
                if (!token) {
                    window.location.href = '/login';
                    return;
                }
                loadStatus();
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
                    
                    // Estado WhatsApp
                    const connected = status.connected;
                    document.getElementById('waIcon').textContent = connected ? '🟢' : '🔴';
                    document.getElementById('waStatus').textContent = connected ? 'Conectado' : 'Desconectado';
                    
                    // Estado Bot
                    const isPaused = status.paused;
                    document.getElementById('botIcon').textContent = isPaused ? '⏸️' : '▶️';
                    document.getElementById('botStatus').textContent = isPaused ? 'Pausado' : 'Activo';
                    
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
                    const hasQr = status.has_qr;
                    if (connected && !hasQr) {
                        waBtn.textContent = '🟢 Reconectar WhatsApp';
                    } else {
                        waBtn.textContent = '🔴 Conectar WhatsApp';
                    }
                } catch (error) {
                    console.error('Error al cargar estado:', error);
                }
            }
            
            async function toggleBot() {
                try {
                    const token = localStorage.getItem('token');
                    const res = await fetch('/status', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const status = await res.json();
                    const isPaused = status.paused;
                    
                    const endpoint = isPaused ? '/bot/resume' : '/bot/pause';
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    
                    if (response.ok) {
                        loadStatus();
                    } else {
                        alert('Error al cambiar estado del bot');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error al cambiar estado del bot');
                }
            }
            
            async function toggleWhatsApp() {
                try {
                    const token = localStorage.getItem('token');
                    const res = await fetch('/status', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const status = await res.json();
                    const connected = status.connected;
                    
                    if (!connected) {
                        // Primero iniciar la conexión
                        try {
                            const connectRes = await fetch('/bot/connect', {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                            });
                            
                            if (!connectRes.ok) {
                                alert('Error al iniciar la conexión. Intenta de nuevo.');
                                return;
                            }
                        } catch (e) {
                            console.error('Error conectando:', e);
                            alert('Error al conectar. Intenta de nuevo.');
                            return;
                        }
                        
                        // Esperar a que WAHA genere el QR
                        await new Promise(r => setTimeout(r, 5000));
                        
                        // Intentar cargar el QR con reintentos
                        let qrLoaded = false;
                        for (let i = 0; i < 10; i++) {
                            try {
                                const qrRes = await fetch('/qr?ts=' + Date.now());
                                if (qrRes.ok) {
                                    const blob = await qrRes.blob();
                                    const url = URL.createObjectURL(blob);
                                    document.getElementById('qrImage').src = url;
                                    document.getElementById('qrModal').classList.add('show');
                                    qrLoaded = true;
                                    return;
                                }
                            } catch (e) {
                                console.error('Intento ' + (i+1) + ' - Error loading QR:', e);
                            }
                            if (i < 9) await new Promise(r => setTimeout(r, 1500));
                        }
                        
                        // Si el QR no está disponible, simplemente actualizar estado
                        if (!qrLoaded) {
                            loadStatus();
                        }
                    } else {
                        // Intenta reconectar
                        try {
                            const response = await fetch('/bot/connect', {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
                            });
                            if (response.ok) {
                                alert('Reconexión iniciada');
                                loadStatus();
                            }
                        } catch (e) {
                            console.error('Error reconectando:', e);
                        }
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            function closeQrModal() {
                document.getElementById('qrModal').classList.remove('show');
            }
            
            function logout() {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
            
            loadStatus();
            setInterval(loadStatus, 5000);
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
                padding: 24px 0;
                overflow-y: auto;
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
            <div class="nav-item" onclick="switchSection('menu')">📋 Editor Menú</div>
            <div class="nav-item" onclick="switchSection('offhours')">🕐 Fuera de Hora</div>
            <div class="nav-item" onclick="switchSection('holidays')">📅 Feriados</div>
            <div class="nav-item" onclick="switchSection('blocklist')">🚫 Bloqueados</div>
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
                    </div>
                    <button class="btn btn-primary" onclick="refresh()">🔄 Actualizar Estado</button>
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
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.95em;">
                            <thead>
                                <tr style="background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid rgba(226, 232, 240, 0.1);">
                                    <th style="padding: 12px; text-align: left; color: #cbd5e1;">Usuario</th>
                                    <th style="padding: 12px; text-align: left; color: #cbd5e1;">Email</th>
                                    <th style="padding: 12px; text-align: left; color: #cbd5e1;">Rol</th>
                                    <th style="padding: 12px; text-align: left; color: #cbd5e1;">Estado</th>
                                </tr>
                            </thead>
                            <tbody id="usersTable">
                                <tr><td colspan="4" style="text-align: center; padding: 20px; color: #94a3b8;">Cargando...</td></tr>
                            </tbody>
                        </table>
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
                            <h3 style="color: #f1f5f9; margin-bottom: 16px;">📅 Horarios Sábado</h3>
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
                        
                        <button type="submit" class="btn btn-primary">💾 Guardar Configuración</button>
                    </form>
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
                                <input type="text" id="blockNumber" placeholder="+5491234567890">
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
                                </tr>
                            </thead>
                            <tbody id="blocklistTable">
                                <tr><td colspan="2" style="text-align: center; padding: 20px; color: #94a3b8;">Cargando...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Modal QR -->
        <div class="modal" id="qrModal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: rgba(18, 24, 40, 0.95); border: 1px solid rgba(226, 232, 240, 0.1); border-radius: 20px; padding: 40px; max-width: 400px; width: 90%; text-align: center;">
                <h3 style="color: #f1f5f9; margin-bottom: 20px;">Escanea el QR</h3>
                <p style="color: #cbd5e1; margin-bottom: 20px;">Escanea este código QR desde tu teléfono para conectar WhatsApp</p>
                <img id="qrImage" style="margin: 20px 0; max-width: 100%; border-radius: 12px; border: 2px solid rgba(226, 232, 240, 0.1);" src="" alt="QR Code">
                <button class="btn btn-secondary" onclick="closeQrModal()" style="margin-top: 20px;">Cerrar</button>
            </div>
        </div>
        
        <script>
            const API_URL = '/api';
            const token = localStorage.getItem('token');
            
            // Validar autenticación y permisos al cargar la página
            window.addEventListener('DOMContentLoaded', function() {
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
                    
                    document.getElementById('waIcon').textContent = status.connected ? '🟢' : '🔴';
                    document.getElementById('waStatus').textContent = status.connected ? 'Conectado' : 'Desconectado';
                    document.getElementById('botIcon').textContent = status.paused ? '⏸️' : '▶️';
                    document.getElementById('botStatus').textContent = status.paused ? 'Pausado' : 'Activo';
                    document.getElementById('chatsToday').textContent = status.chats_today || '0';
                    document.getElementById('hoursIcon').textContent = status.off_hours ? '🕐' : '✅';
                    document.getElementById('hoursStatus').textContent = status.off_hours ? 'Fuera' : 'Normal';
                    document.getElementById('waStatusText').textContent = status.connected ? 'Conectado' : 'Desconectado';
                    
                    const waBtn = document.getElementById('waBtn');
                    const hasQr = status.has_qr;
                    if (status.connected && !hasQr) {
                        waBtn.textContent = '🟢 Reconectar WhatsApp';
                    } else {
                        waBtn.textContent = '🔴 Conectar WhatsApp';
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function toggleWhatsApp() {
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
                    const connected = status.connected;
                    
                    if (!connected) {
                        try {
                            const connectRes = await fetch('/bot/connect', {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${token}` }
                            });
                            
                            if (!connectRes.ok) {
                                alert('Error al iniciar la conexión. Intenta de nuevo.');
                                return;
                            }
                        } catch (e) {
                            console.error('Error conectando:', e);
                            alert('Error al conectar. Intenta de nuevo.');
                            return;
                        }
                        
                        await new Promise(r => setTimeout(r, 5000));
                        
                        let qrLoaded = false;
                        for (let i = 0; i < 10; i++) {
                            try {
                                const qrRes = await fetch('/qr?ts=' + Date.now());
                                if (qrRes.ok) {
                                    const blob = await qrRes.blob();
                                    const url = URL.createObjectURL(blob);
                                    document.getElementById('qrImage').src = url;
                                    document.getElementById('qrModal').style.display = 'flex';
                                    qrLoaded = true;
                                    return;
                                }
                            } catch (e) {
                                console.error('Intento ' + (i+1) + ' - Error loading QR:', e);
                            }
                            if (i < 9) await new Promise(r => setTimeout(r, 1500));
                        }
                        
                        // Si el QR no está disponible, simplemente actualizar estado
                        if (!qrLoaded) {
                            refresh();
                        }
                    } else {
                        try {
                            const response = await fetch('/bot/connect', {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${token}` }
                            });
                            if (response.ok) {
                                alert('Reconexión iniciada');
                                refresh();
                            }
                        } catch (e) {
                            console.error('Error:', e);
                        }
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            function closeQrModal() {
                document.getElementById('qrModal').style.display = 'none';
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
                            <td style="padding: 12px; color: #cbd5e1;">${u.email}</td>
                            <td style="padding: 12px; color: #cbd5e1;">${u.is_admin ? '👑 Admin' : '👤 Usuario'}</td>
                            <td style="padding: 12px; color: #cbd5e1;">${u.is_active ? '✅ Activo' : '❌ Inactivo'}</td>
                        </tr>
                    `).join('');
                } catch (error) {
                    console.error('Error loading users:', error);
                }
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
                            closing_time: document.getElementById('closingTime').value
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
                    document.getElementById('offhoursContent').value = originalOffhoursContent;
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function saveOffhours(e) {
                e.preventDefault();
                try {
                    const res = await fetch(`${API_URL}/config/offhours`, {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            content: document.getElementById('offhoursContent').value
                        })
                    });
                    
                    const msg = document.getElementById('offhoursMessage');
                    const data = await res.json();
                    
                    if (res.ok) {
                        originalOffhoursContent = document.getElementById('offhoursContent').value;
                        msg.textContent = '✅ Menú fuera de hora guardado correctamente (' + data.bytes + ' bytes)';
                        msg.className = 'message show success';
                    } else {
                        msg.textContent = '❌ Error: ' + (data.error || 'Error al guardar');
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
                    const blocked = await res.json();
                    
                    const tbody = document.querySelector('#blocklistTable');
                    tbody.innerHTML = blocked.map(b => `
                        <tr style="border-bottom: 1px solid rgba(226, 232, 240, 0.05);">
                            <td style="padding: 12px; color: #cbd5e1;">${b.phone_number}</td>
                            <td style="padding: 12px; color: #cbd5e1;">${b.reason}</td>
                        </tr>
                    `).join('');
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function blockNumber(e) {
                e.preventDefault();
                try {
                    const res = await fetch(`${API_URL}/blocklist`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            phone_number: document.getElementById('blockNumber').value,
                            reason: document.getElementById('blockReason').value
                        })
                    });
                    
                    if (res.ok) {
                        document.getElementById('blockNumber').value = '';
                        document.getElementById('blockReason').value = '';
                        loadBlocklist();
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            function logout() {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
            
            refresh();
            setInterval(refresh, 5000);
        </script>
    </body>
    </html>
    """

# Ahora reemplazar la función get_dashboard_page() en pages.py
