#!/usr/bin/env python3
"""
Script de prueba para verificar que el login funciona correctamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import User
from security import hash_password, verify_password

def test_login():
    """Prueba de login"""
    print("=" * 60)
    print("🧪 PRUEBA DE LOGIN - WA-BOT")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Verificar que la BD está inicializada
        print("\n[1] Verificando base de datos...")
        users_count = db.query(User).count()
        print(f"✅ Usuarios en BD: {users_count}")
        
        # 2. Listar usuarios
        print("\n[2] Usuarios disponibles:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} | Email: {user.email} | Admin: {user.is_admin} | Activo: {user.is_active}")
        
        # 3. Probar admin
        print("\n[3] Probando usuario admin...")
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print(f"✅ Admin encontrado: {admin.username}")
            
            # Verificar hash
            test_pwd = "admin123"
            is_valid = verify_password(test_pwd, admin.hashed_password)
            print(f"   - Contraseña 'admin123': {'✅ Válida' if is_valid else '❌ Inválida'}")
            print(f"   - Hash: {admin.hashed_password[:30]}...")
            print(f"   - Activo: {admin.is_active}")
        else:
            print("❌ Admin no encontrado! Necesita ser creado.")
        
        # 4. Probar usuario regular
        print("\n[4] Probando usuario regular...")
        user = db.query(User).filter(User.username == "usuario").first()
        if user:
            print(f"✅ Usuario encontrado: {user.username}")
            
            test_pwd = "usuario123"
            is_valid = verify_password(test_pwd, user.hashed_password)
            print(f"   - Contraseña 'usuario123': {'✅ Válida' if is_valid else '❌ Inválida'}")
            print(f"   - Activo: {user.is_active}")
        else:
            print("❌ Usuario no encontrado! Necesita ser creado.")
        
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA")
        print("=" * 60)
        print("\n💡 Para iniciar el servidor:")
        print("   python3 app.py")
        print("\n📚 Credenciales por defecto:")
        print("   Admin - usuario: admin, contraseña: admin123")
        print("   User  - usuario: usuario, contraseña: usuario123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login()
