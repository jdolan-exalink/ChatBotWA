from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, UniqueConstraint
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
    solution_name = Column(String(255), default="Clínica")  # Nombre de la solución / título del menú
    is_paused = Column(Boolean, default=False)
    
    # Horarios
    opening_time = Column(String(5))  # HH:MM (Lunes-Viernes)
    closing_time = Column(String(5))  # HH:MM (Lunes-Viernes)
    sat_opening_time = Column(String(5), default="10:00")  # HH:MM Sábado
    sat_closing_time = Column(String(5), default="14:00")  # HH:MM Sábado
    sat_enabled = Column(Boolean, default=True)   # False = sábado siempre cerrado
    sun_enabled = Column(Boolean, default=False)  # False = domingo siempre cerrado
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

    # Plantillas para recordatorios programados desde tickets
    scheduled_confirmation_template = Column(
        Text,
        default="✅ *Recordatorio programado*\n\n*{RECORDATORIO}*\n📅 Turno: *{FECHA}* a las *{HORA}*\n🔔 Avisos automáticos: *1 día antes* y *1 hora antes*.\n{NOTA_BLOQUE}\n{CALENDAR_LINK_BLOQUE}\nSi necesitás cambios, respondé a este mensaje.",
    )
    scheduled_reminder_template = Column(
        Text,
        default="✨ *{RECORDATORIO}*\n\nTe recordamos tu turno para el *{FECHA}* a las *{HORA}*.\n⏰ Aviso: *{AVISO}*.\n{NOTA_BLOQUE}\n{CALENDAR_LINK_BLOQUE}\nSi necesitás reprogramar, respondé a este mensaje.",
    )
    scheduled_calendar_link_enabled = Column(Boolean, default=False)
    scheduled_calendar_link_base_url = Column(String(255))

    # ============ LOGGING ============
    debug_mode = Column(Boolean, default=False)  # True=logs detallados, False=solo chats y errores

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
    menu_breadcrumb = Column(Text)  # Ruta con descripciones para el ticket
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), onupdate=func.now())
    handoff_started_at = Column(DateTime(timezone=True))  # Cuándo empezó el handoff
    closed_at = Column(DateTime(timezone=True))  # Cuándo se cerró
    
    # Metadata
    is_blocked = Column(Boolean, default=False)  # ¿Está bloqueado?
    block_reason = Column(String(255))
    extra_data = Column(Text)  # JSON para datos extra
    
    ticket_status = Column(String(50), default="pendiente") # pendiente, confirmado, etc.
    
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


class DailyChatContact(Base):
    """Contacto unico por dia para metrica 'chats de hoy'."""
    __tablename__ = "daily_chat_contacts"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD en timezone local configurada
    phone_number = Column(String(20), index=True, nullable=False)
    first_message_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("day", "phone_number", name="uq_daily_chat_contacts_day_phone"),
    )

    def __repr__(self):
        return f"<DailyChatContact day={self.day} phone={self.phone_number}>"


class WahaRuntimeState(Base):
    """Estado runtime persistente para métricas de conexión WAHA."""
    __tablename__ = "waha_runtime_state"

    id = Column(Integer, primary_key=True, index=True)
    connected_since_epoch = Column(Integer, nullable=True)
    disconnected_since_epoch = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<WahaRuntimeState connected_since={self.connected_since_epoch}>"


class TicketHistory(Base):
    """Historial de tickets cerrados o vencidos para estadísticas."""
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(100), index=True, nullable=False)
    phone_number = Column(String(20), index=True, nullable=False)

    # Estado al cierre
    close_reason = Column(String(50), default="manual")  # manual | expired | bot_return
    closed_by = Column(String(255))   # username del operador o "system"
    operator_reply = Column(Text)     # Último mensaje enviado por el operador (si hubo)

    # Tiempos
    opened_at = Column(DateTime(timezone=True))   # handoff_started_at original
    closed_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer)            # segundos desde apertura a cierre

    # Nuevos estados unificados
    ticket_status = Column(String(50), default="cerrado") # cerrado, cancelado, timeout
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(String(255))
    
    # Sección del menú que originó el ticket
    menu_section = Column(String(100))
    menu_breadcrumb = Column(Text)

    def __repr__(self):
        return f"<TicketHistory {self.ticket_id} reason={self.close_reason}>"


class ScheduledMessage(Base):
    """Mensajes programados para envío automático a una hora configurada."""
    __tablename__ = "scheduled_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)          # etiqueta descriptiva
    phone_number = Column(String(30), nullable=False)   # destinatario (puede ser múltiples, CSV)
    message = Column(Text, nullable=False)              # texto del mensaje
    send_time = Column(String(5), nullable=False)       # "HH:MM" hora local configurada
    send_date = Column(String(10), nullable=True)        # "YYYY-MM-DD" fecha específica (None = recurrente)
    days_of_week = Column(String(20), default="1,2,3,4,5,6,7")  # 1=Lun … 7=Dom (CSV)
    is_active = Column(Boolean, default=True)
    last_sent_date = Column(String(10), nullable=True)  # "YYYY-MM-DD" evita doble envío
    ticket_id = Column(String(100), index=True)
    event_at = Column(String(40), nullable=True)        # ISO datetime del turno original
    schedule_note = Column(Text, nullable=True)
    schedule_kind = Column(String(30), default="general")
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ScheduledMessage '{self.name}' at {self.send_time}>"


class ExternalAccessToken(Base):
    """Access tokens para integraciones de sistemas externos."""
    __tablename__ = "external_access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    token_prefix = Column(String(32), nullable=False)
    token_hash = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(Text)
    allowed_event_types = Column(String(255), default="*")  # CSV: appointment,invoice,custom
    is_active = Column(Boolean, default=True)
    created_by = Column(String(255))
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ExternalAccessToken {self.name} active={self.is_active}>"
