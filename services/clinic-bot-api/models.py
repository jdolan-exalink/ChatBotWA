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
    off_hours_enabled = Column(Boolean, default=False)
    off_hours_message = Column(Text)
    
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
