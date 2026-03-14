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

# Verificar archivos de menú — instalar si es instalación nueva
echo "[2] Verificando archivos de menú..."
mkdir -p /app/data
for base in MenuP MenuF; do
    if [ -f "/app/data/${base}.MD" ] || [ -f "/app/data/${base}.md" ]; then
        echo "   - OK (ya existe): ${base}.MD/.md"
        continue
    fi
    echo "   ℹ️  /app/data/${base}.MD no encontrado — copiando template inicial..."
    cp "/app/templates/${base}.MD" "/app/data/${base}.MD" && echo "   ✅ ${base}.MD creado desde template"
done

# Asegurar que la BD existe
echo "[3] Inicializando base de datos..."
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

# Migraciones automáticas con versionado de schema
echo "[4] Verificando version de schema y aplicando migraciones..."
python3 -c "
from database import init_db
init_db()
"

# Ejecutar servidor
echo ""
echo "🚀 Iniciando WA-BOT..."
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8088} --loop uvloop --workers 4 --log-level warning
