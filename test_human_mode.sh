#!/bin/bash
# Test HUMAN_MODE: 99 -> mensajes -> 98

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
WEBHOOK_URL="http://localhost:8088/webhook"
PHONE="+5493424999999@c.us"
TS=$(date +%s)

# Headers
echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  TEST: HUMAN_MODE (99 -> msgs -> 98)  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "Teléfono: ${YELLOW}${PHONE}${NC}"
echo -e "Webhook: ${YELLOW}${WEBHOOK_URL}${NC}\n"

# Función para enviar mensaje
send_msg() {
    local step=$1
    local text=$2
    local desc=$3
    
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} ${CYAN}PASO ${step}:${NC} ${desc}"
    echo -e "  Enviando: '${text}'"
    
    local msg_id="${TS}$(date +%N)"
    local payload="{
      \"payload\": {
        \"from\": \"${PHONE}\",
        \"chatId\": \"${PHONE}\",
        \"body\": \"${text}\",
        \"timestamp\": $(date +%s),
        \"fromMe\": false,
        \"messageId\": \"msg-${msg_id}\",
        \"type\": \"text\",
        \"hasMedia\": false
      }
    }"
    
    local response=$(curl -s -X POST "${WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "${payload}")
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "${payload}")
    
    echo -e "  ${GREEN}✓${NC} HTTP ${http_code}"
    
    if echo "${response}" | grep -q "human_mode_active"; then
        echo -e "  ${GREEN}✓✓ Usuario EN HUMAN_MODE (ignorado)${NC}"
    fi
    
    sleep 1
}

# =====PASO 1: Mensaje normal=====
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${CYAN}PASO 1: Mensaje Normal (ANTES)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"
send_msg "1.1" "Hola bot" "Mensaje normal"

# ===== PASO 2: Opción 99 =====
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${CYAN}PASO 2: Enviar 99 (INICIAR HUMAN_MODE)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"
send_msg "2.1" "99" "Opción 99 - Iniciar HUMAN_MODE"

# ===== PASO 3: Mensajes en HUMAN_MODE =====
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${CYAN}PASO 3: 3 MENSAJES EN HUMAN_MODE${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

send_msg "3.1" "Hola operador" "Mensaje 1 en HUMAN_MODE"
send_msg "3.2" "¿Estás ahí?" "Mensaje 2 en HUMAN_MODE"
send_msg "3.3" "Necesito ayuda" "Mensaje 3 en HUMAN_MODE"

# ===== PASO 4: Opción 98 =====
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${CYAN}PASO 4: Enviar 98 (SALIR DE HUMAN_MODE)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"
send_msg "4.1" "98" "Opción 98 - Salir de HUMAN_MODE"

# ===== PASO 5: Mensajes Normales =====
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${CYAN}PASO 5: Mensaje Normal (DESPUÉS)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"
send_msg "5.1" "Hola" "Mensaje normal después"

# ===== RESUMEN =====
echo -e "\n${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ TEST COMPLETADO${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

echo -e "${CYAN}Revisar los LOGS del bot:${NC}"
echo -e "  ${GREEN}✓${NC} Paso 1: Bot responde"
echo -e "  ${GREEN}✓${NC} Paso 2: '[WEBHOOK] 🔴 Usuario solicita opción 99'"
echo -e "  ${GREEN}✓${NC} Paso 3: '[WEBHOOK] ✅ ... EN HUMAN_MODE ACTIVO' (3 veces)"
echo -e "  ${GREEN}✓${NC} Paso 4: '[WEBHOOK] 🟢 Usuario solicita opción 98'"
echo -e "  ${GREEN}✓${NC} Paso 5: Bot responde normalmente\n"

echo -e "${YELLOW}Para ver logs en tiempo real:${NC}"
echo -e "  docker logs -f clinic-bot-api | grep WEBHOOK\n"
