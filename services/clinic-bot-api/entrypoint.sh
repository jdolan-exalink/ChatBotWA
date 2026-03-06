#!/bin/bash
# Script de inicialización para WA-BOT
# Se ejecuta antes de iniciar el servidor

echo "=========================================="
echo "🔧 WA-BOT - Inicialización"
echo "=========================================="

cd /app

# Esperar a que la BD esté disponible
echo "[1] Esperando a que la BD esté lista..."
sleep 5

# Asegurar que la BD existe
echo "[2] Inicializando base de datos..."
python3 -c "
from database import init_db
from models import User, BotConfig
from security import hash_password
from database import SessionLocal

# Crear tablas
print('   - Creando tablas...')
init_db()

# Verificar usuarios
db = SessionLocal()
admin_count = db.query(User).filter(User.is_admin == True).count()
user_count = db.query(User).count()

if admin_count == 0:
    print('   - Admin no encontrado, creando...')
    admin = User(
        username='admin',
        email='admin@clinic.local',
        hashed_password=hash_password('admin123'),
        full_name='Administrador',
        is_admin=True,
        is_active=True
    )
    db.add(admin)
    print('   ✅ Admin creado: usuario=admin, contraseña=admin123')

regular_user = db.query(User).filter(User.username == 'usuario').first()
if not regular_user:
    print('   - Usuario regular no encontrado, creando...')
    user = User(
        username='usuario',
        email='usuario@clinic.local',
        hashed_password=hash_password('usuario123'),
        full_name='Usuario Regular',
        is_admin=False,
        is_active=True
    )
    db.add(user)
    print('   ✅ Usuario creado: usuario=usuario, contraseña=usuario123')

# Crear config
cfg = db.query(BotConfig).first()
if not cfg:
    print('   - Config no encontrada, creando...')
    from app import SOLUTION_NAME, OLLAMA_URL, OLLAMA_MODEL
    config = BotConfig(
        solution_name=SOLUTION_NAME,
        menu_title=SOLUTION_NAME,
        opening_time='09:00',
        closing_time='18:00',
        sat_opening_time='10:00',
        sat_closing_time='14:00',
        off_hours_enabled=True,
        off_hours_message='🕐 Estamos fuera de horario. Nos vemos pronto!',
        ollama_url=OLLAMA_URL,
        ollama_model=OLLAMA_MODEL,
        admin_idle_timeout_sec=900
    )
    db.add(config)
    print('   ✅ Configuración creada')

db.commit()
print(f'   - Total usuarios en BD: {user_count + (1 if admin_count == 0 else 0) + (1 if not regular_user else 0)}')
db.close()
print('========================================')
print('✅ Inicialización completada')
print('========================================')
"

# Migraciones automáticas: agregar columnas que puedan faltar en DBs existentes
echo "[3] Ejecutando migraciones de schema..."
python3 -c "
from database import engine
from sqlalchemy import text, inspect

inspector = inspect(engine)
existing_cols = {c['name'] for c in inspector.get_columns('bot_config')}

migrations = [
    (\"timezone\",              \"ALTER TABLE bot_config ADD COLUMN timezone VARCHAR(50) DEFAULT 'America/Argentina/Buenos_Aires'\"),
    (\"handoff_enabled\",       \"ALTER TABLE bot_config ADD COLUMN handoff_enabled BOOLEAN DEFAULT 1\"),
    (\"handoff_message\",       \"ALTER TABLE bot_config ADD COLUMN handoff_message TEXT DEFAULT 'Listo, recibimos tu solicitud. Un operador te contacta a la brevedad.'\"),
    (\"handoff_inactivity_minutes\", \"ALTER TABLE bot_config ADD COLUMN handoff_inactivity_minutes INTEGER DEFAULT 120\"),
    (\"waiting_agent_message\", \"ALTER TABLE bot_config ADD COLUMN waiting_agent_message TEXT DEFAULT 'Estamos buscando un operador disponible. Por favor aguarda...'\"),
    (\"in_agent_message\",      \"ALTER TABLE bot_config ADD COLUMN in_agent_message TEXT DEFAULT 'Un operador esta atendiendo tu solicitud.'\"),
    (\"closed_message\",        \"ALTER TABLE bot_config ADD COLUMN closed_message TEXT DEFAULT 'Gracias por contactarte. Tu caso esta cerrado.'\"),
    (\"debug_mode\",             \"ALTER TABLE bot_config ADD COLUMN debug_mode BOOLEAN DEFAULT 0\"),
]

with engine.connect() as conn:
    for col, sql in migrations:
        if col not in existing_cols:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f'   ✅ Columna agregada: {col}')
            except Exception as e:
                print(f'   ⚠️  {col}: {e}')
        else:
            print(f'   - OK (ya existe): {col}')
print('   Schema actualizado.')
"

# Ejecutar servidor
echo ""
echo "🚀 Iniciando WA-BOT..."
python3 /app/app.py
