#!/usr/bin/env python3
"""
Test automatizado del flujo HUMAN_MODE:
1. Enter 99 (HUMAN_MODE)
2. Send messages (should be ignored)
3. Exit 98 (BOT_MODE)
"""
import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Configuración
WEBHOOK_URL = "http://localhost:8088/webhook"
PHONE_NUMBER = "+5493424999999@c.us"  # Número de prueba único
SESSION_ID = "test-session-001"

# Colores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_test(step, message):
    """Log con formato bonito"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.BLUE}[{timestamp}]{Colors.ENDC} {Colors.BOLD}STEP {step}:{Colors.ENDC} {message}")

def log_result(status, message):
    """Log de resultado"""
    if status == "✓":
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    elif status == "✗":
        print(f"{Colors.RED}✗ {message}{Colors.ENDC}")
    elif status == "→":
        print(f"{Colors.CYAN}→ {message}{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def create_webhook_payload(text: str, from_me: bool = False):
    """Crea un payload similar a lo que WAHA envía"""
    return {
        "payload": {
            "from": PHONE_NUMBER,
            "chatId": PHONE_NUMBER,
            "body": text,
            "timestamp": int(datetime.now().timestamp()),
            "fromMe": from_me,
            "messageId": f"{SESSION_ID}-{int(datetime.now().timestamp() * 1000)}",
            "type": "text",
            "hasMedia": False
        }
    }

async def send_webhook_message(session: aiohttp.ClientSession, text: str, step: str, from_me: bool = False):
    """Envía un mensaje al webhook"""
    payload = create_webhook_payload(text, from_me)
    
    log_test(step, f"Enviando: '{text}'")
    print(f"{Colors.CYAN}  Payload: {json.dumps(payload)}{Colors.ENDC}")
    
    try:
        async with session.post(WEBHOOK_URL, json=payload, timeout=10) as resp:
            response_text = await resp.text()
            response_data = json.loads(response_text) if response_text else {}
            
            log_result("→", f"HTTP {resp.status}")
            if resp.status == 200:
                log_result("✓", f"Webhook procesó OK")
                if "human_mode_active" in response_text:
                    log_result("✓", f">>> Usuario EN HUMAN_MODE (ignorado)")
                else:
                    log_result("→", f"Respuesta: {response_data}")
            else:
                log_result("✗", f"Error HTTP {resp.status}")
            
            return response_data
    except asyncio.TimeoutError:
        log_result("✗", "Timeout al conectar")
        return None
    except Exception as e:
        log_result("✗", f"Error: {e}")
        return None

async def run_test_flow():
    """Ejecuta el flujo completo de testing"""
    print(f"\n{Colors.BOLD}╔════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}║  TEST AUTOMATIZADO: HUMAN_MODE FLOW   ║{Colors.ENDC}")
    print(f"{Colors.BOLD}╚════════════════════════════════════════╝{Colors.ENDC}\n")
    
    print(f"Teléfono: {Colors.YELLOW}{PHONE_NUMBER}{Colors.ENDC}")
    print(f"Webhook: {Colors.YELLOW}{WEBHOOK_URL}{Colors.ENDC}\n")
    
    async with aiohttp.ClientSession() as session:
        # ===== PASO 1: Mensaje normal =====
        print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BOLD}PASO 1: Mensaje Normal ANTES de HUMAN_MODE{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
        
        await send_webhook_message(session, "Hola bot", "1.1")
        await asyncio.sleep(1)
        
        # ===== PASO 2: Opción 99 =====
        print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BOLD}PASO 2: Enviar 99 - INICIAR HUMAN_MODE{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
        
        await send_webhook_message(session, "99", "2.1")
        await asyncio.sleep(1)
        
        # ===== PASO 3: Mensajes en HUMAN_MODE =====
        print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BOLD}PASO 3: MENSAJES EN HUMAN_MODE (deben ignorarse){Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
        
        messages = ["Hola operador", "¿Estás?", "Ayuda pls"]
        
        for i, msg in enumerate(messages, 1):
            await send_webhook_message(session, msg, f"3.{i}")
            await asyncio.sleep(0.5)
        
        # ===== PASO 4: Opción 98 =====
        print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BOLD}PASO 4: Enviar 98 - SALIR DE HUMAN_MODE{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
        
        await send_webhook_message(session, "98", "4.1")
        await asyncio.sleep(1)
        
        # ===== PASO 5: Mensajes normales nuevamente =====
        print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BOLD}PASO 5: MENSAJES NORMALES (Bot activo){Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
        
        await send_webhook_message(session, "Hola", "5.1")
        await asyncio.sleep(0.5)
    
    # ===== RESUMEN =====
    print(f"\n{Colors.HEADER}{'='*50}{Colors.ENDC}")
    print(f"{Colors.BOLD}✓ TEST COMPLETADO{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*50}{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}Revisar los logs del bot (docker logs -f clinic-bot-api):{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Paso 1: Bot responde normalmente")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Paso 2: '[WEBHOOK] 🔴 Usuario solicita opción 99'")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Paso 3: '[WEBHOOK] ✅ {PHONE_NUMBER} EN HUMAN_MODE ACTIVO'")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Paso 4: '[WEBHOOK] 🟢 Usuario solicita opción 98'")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Paso 5: Bot responde nuevamente\n")

if __name__ == "__main__":
    print(f"{Colors.YELLOW}Requerimientos:{Colors.ENDC}")
    print(f"  1. Bot corriendo en http://localhost:8088")
    print(f"  2. Instalar: pip install aiohttp\n")
    
    try:
        asyncio.run(run_test_flow())
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Test cancelado{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        sys.exit(1)

