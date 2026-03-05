from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ===================== AUTH =====================
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    full_name: Optional[str] = None
    is_admin: bool = False

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    is_admin: bool
    is_active: bool
    is_paused: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    new_password: str

# ===================== BOT CONFIG =====================
class BotConfigUpdate(BaseModel):
    solution_name: Optional[str] = None
    menu_title: Optional[str] = None
    opening_time: Optional[str] = None  # HH:MM (Lunes-Viernes)
    closing_time: Optional[str] = None  # HH:MM (Lunes-Viernes)
    sat_opening_time: Optional[str] = None  # HH:MM Sábado
    sat_closing_time: Optional[str] = None  # HH:MM Sábado
    off_hours_enabled: Optional[bool] = None
    off_hours_message: Optional[str] = None
    country_filter_enabled: Optional[bool] = None
    country_codes: Optional[str] = None  # CSV
    area_filter_enabled: Optional[bool] = None
    area_codes: Optional[str] = None  # CSV
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    admin_idle_timeout_sec: Optional[int] = None

class BotConfigResponse(BaseModel):
    id: int
    solution_name: str
    menu_title: str
    is_paused: bool
    opening_time: Optional[str]
    closing_time: Optional[str]
    sat_opening_time: Optional[str]
    sat_closing_time: Optional[str]
    off_hours_enabled: bool
    country_filter_enabled: bool
    country_codes: Optional[str]
    area_filter_enabled: bool
    area_codes: Optional[str]
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ===================== COUNTRY FILTERS =====================
class CountryFilterCreate(BaseModel):
    country_code: str
    country_name: str
    allowed_provinces: Optional[str] = None  # JSON

class CountryFilterResponse(BaseModel):
    id: int
    country_code: str
    country_name: str
    is_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===================== HOLIDAYS =====================
class HolidayCreate(BaseModel):
    date: str  # YYYY-MM-DD
    name: str
    description: Optional[str] = None

class HolidayResponse(BaseModel):
    id: int
    date: str
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===================== HOLIDAY MENUS =====================
class HolidayMenuCreate(BaseModel):
    name: str
    content: str  # Markdown del menú

class HolidayMenuUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class HolidayMenuResponse(BaseModel):
    id: int
    name: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===================== WHATSAPP BLOCKLIST =====================
class WhatsAppBlockCreate(BaseModel):
    phone_number: str
    reason: Optional[str] = None

class WhatsAppBlockResponse(BaseModel):
    id: int
    phone_number: str
    reason: Optional[str]
    blocked_at: datetime
    
    class Config:
        from_attributes = True

# ===================== STATUS =====================
class BotStatusResponse(BaseModel):
    provider: str
    instance: str
    connected: bool
    paused: bool
    has_qr: bool
    solution_name: str
    info: dict
