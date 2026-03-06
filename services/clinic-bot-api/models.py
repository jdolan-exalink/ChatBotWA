from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class User(Base):
    """Modelo de usuario del sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_paused = Column(Boolean, default=False)  # Para pausar/reanudar el bot
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User {self.username} (admin={self.is_admin})>"

class BotConfig(Base):
    """Configuración general del bot"""
    __tablename__ = "bot_config"
    
    id = Column(Integer, primary_key=True, index=True)
    solution_name = Column(String(255), default="Clínica")  # Nombre de la solución (configurable)
    menu_title = Column(String(255), default="Clínica")
    is_paused = Column(Boolean, default=False)
    
    # Horarios
    opening_time = Column(String(5))  # HH:MM (Lunes-Viernes)
    closing_time = Column(String(5))  # HH:MM (Lunes-Viernes)
    sat_opening_time = Column(String(5), default="10:00")  # HH:MM Sábado
    sat_closing_time = Column(String(5), default="14:00")  # HH:MM Sábado
    off_hours_enabled = Column(Boolean, default=True)
    off_hours_message = Column(Text, default="🕐 Estamos fuera de horario. Nos vemos pronto!")
    timezone = Column(String(50), default="America/Argentina/Buenos_Aires")  # Timezone para horarios
    
    # Filtros
    country_filter_enabled = Column(Boolean, default=False)
    country_codes = Column(Text)  # CSV: "+54,+55,+56"
    area_filter_enabled = Column(Boolean, default=False)
    area_codes = Column(Text)  # CSV: "(011),(012)"
    
    # Configuración de IA
    ollama_url = Column(String(255))
    ollama_model = Column(String(255))
    
    # Admin timeout
    admin_idle_timeout_sec = Column(Integer, default=900)
    
    # ============ HANDOFF / ATENCIÓN HUMANA ============
    # Estado machine para bot → operario
    handoff_enabled = Column(Boolean, default=True)  # ¿Activar handoff?
    handoff_message = Column(Text, default="✅ Listo, recibimos tu solicitud. Un operador te contacta a la brevedad.")
    
    # Inactividad: tiempo para cerrar conversa automáticamente
    handoff_inactivity_minutes = Column(Integer, default=120)  # 2 horas por defecto
    
    # Mensaje mientras espera operario
    waiting_agent_message = Column(Text, default="Estamos buscando un operador disponible. Por favor aguarda...")
    
    # Mensaje cuando operario está atendiendo
    in_agent_message = Column(Text, default="Un operador está atendiendo tu solicitud.")
    
    # Mensaje cuando se cierra el ticket
    closed_message = Column(Text, default="Gracias por contactarte. Tu caso está cerrado. Si necesitas ayuda, escribe nuevamente.")
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BotConfig {self.solution_name}>"

class CountryFilter(Base):
    """Filtros de país/provincia para antispam"""
    __tablename__ = "country_filters"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(2), index=True)  # Ej: 'AR' para Argentina
    country_name = Column(String(255))
    allowed_provinces = Column(Text)  # JSON con provincias permitidas
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CountryFilter {self.country_code}>"

class Holiday(Base):
    """Días feriados para tratarlos como fuera de horario"""
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True)  # YYYY-MM-DD
    name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Holiday {self.date} - {self.name}>"

class HolidayMenu(Base):
    """Menú específico para horas no laborales y feriados"""
    __tablename__ = "holiday_menus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    content = Column(Text)  # Menú markdown
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HolidayMenu {self.name}>"

class WhatsAppBlockList(Base):
    """Lista negra de números de WhatsApp"""
    __tablename__ = "whatsapp_blocklist"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True)
    reason = Column(String(255))
    blocked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<WhatsAppBlockList {self.phone_number}>"


class ConversationState(Base):
    """Estado de conversación por usuario (state machine para handoff)"""
    __tablename__ = "conversation_states"
    
    # Estados posibles:
    # BOT_MENU: El bot guía con menús
    # COLLECTING_DATA: El bot recopila datos
    # WAITING_AGENT: Esperando asignación a operador
    # IN_AGENT: En conversación con operador
    # CLOSED: Ticket cerrado, vuelve a bot
    # BLACKLISTED: Número en lista negra, respuestas mínimas
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    current_state = Column(String(50), default="BOT_MENU")  # Estado actual
    
    # Handoff (atención humana)
    handoff_active = Column(Boolean, default=False)  # ¿Hay handoff activo?
    human_mode = Column(Boolean, default=False)  # ¿Está en modo humano? (12h timeout)
    human_mode_expire = Column(DateTime(timezone=True))  # Cuándo expira el modo humano
    assigned_agent_id = Column(Integer)  # ID del operario asignado
    assigned_agent_name = Column(String(255))  # Nombre del operario
    ticket_id = Column(String(100), unique=True, index=True)  # ID del ticket
    
    # Datos recolectados (JSON o texto)
    collected_data = Column(Text)  # JSON con datos del usuario
    last_bot_menu = Column(String(100))  # Último menú que vio
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), onupdate=func.now())
    handoff_started_at = Column(DateTime(timezone=True))  # Cuándo empezó el handoff
    closed_at = Column(DateTime(timezone=True))  # Cuándo se cerró
    
    # Metadata
    is_blocked = Column(Boolean, default=False)  # ¿Está bloqueado?
    block_reason = Column(String(255))
    extra_data = Column(Text)  # JSON para datos extra
    
    def __repr__(self):
        return f"<ConversationState {self.phone_number} ({self.current_state})>"


class AgentAssignment(Base):
    """Asignación de conversaciones a operarios"""
    __tablename__ = "agent_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)  # Foreign key logico a ConversationState
    agent_id = Column(Integer, index=True)  # ID del operario (User)
    phone_number = Column(String(20), index=True)  # Teléfono del usuario
    ticket_id = Column(String(100), index=True)  # ID del ticket
    
    # Estado de la asignación
    status = Column(String(50), default="ASSIGNED")  # ASSIGNED, IN_PROGRESS, CLOSED
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))  # Cuándo el operario empezó a responder
    closed_at = Column(DateTime(timezone=True))  # Cuándo se cerró
    
    # Notas del operario
    notes = Column(Text)
    resolution = Column(Text)  # Cómo se resolvió
    
    def __repr__(self):
        return f"<AgentAssignment ticket={self.ticket_id} agent={self.agent_id}>"
