#!/usr/bin/env python3
"""
Script para probar la funcionalidad de bloqueados
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8088"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def get_token():
    """Obtener token de autenticación"""
    response = requests.post(
        f"{BASE_URL}/api/token",
        data={"username": ADMIN_USER, "password": ADMIN_PASS}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Error al obtener token: {response.text}")
        return None

def list_blocklist(token):
    """Listar números bloqueados"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/blocklist", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error al listar bloqueados: {response.text}")
        return []

def add_to_blocklist(token, phone_number, reason):
    """Agregar número a blocklist"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "phone_number": phone_number,
        "reason": reason
    }
    response = requests.post(
        f"{BASE_URL}/api/blocklist",
        headers=headers,
        json=data
    )
    return response

def remove_from_blocklist(token, block_id):
    """Remover número de blocklist"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/api/blocklist/{block_id}",
        headers=headers
    )
    return response

def main():
    print("=" * 60)
    print("PRUEBA DE FUNCIONALIDAD DE BLOQUEADOS")
    print("=" * 60)
    
    # Paso 1: Obtener token
    print("\n1️⃣ Obteniendo token de autenticación...")
    token = get_token()
    if not token:
        return
    print(f"✅ Token obtenido: {token[:20]}...")
    
    # Paso 2: Listar bloqueados actuales
    print("\n2️⃣ Listando bloqueados actuales...")
    blocked = list_blocklist(token)
    print(f"✅ Total de números bloqueados: {len(blocked)}")
    for b in blocked:
        print(f"   - {b['phone_number']}: {b['reason']}")
    
    # Paso 3: Agregar nuevo bloqueo
    test_number = "+543424438150"
    test_reason = "Facturación"
    print(f"\n3️⃣ Agregando nuevo bloqueo...")
    print(f"   Número: {test_number}")
    print(f"   Razón: {test_reason}")
    
    response = add_to_blocklist(token, test_number, test_reason)
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Número bloqueado exitosamente")
        print(f"   ID: {result.get('id')}")
        print(f"   Teléfono: {result.get('phone_number')}")
        print(f"   Razón: {result.get('reason')}")
        new_block_id = result.get('id')
    else:
        print(f"❌ Error al bloquear número")
        new_block_id = None
    
    # Paso 4: Listar bloqueados de nuevo
    print(f"\n4️⃣ Listando bloqueados después de agregar...")
    blocked = list_blocklist(token)
    print(f"✅ Total de números bloqueados: {len(blocked)}")
    for b in blocked:
        print(f"   - {b['phone_number']}: {b['reason']}")
    
    # Paso 5: Remover el número bloqueado (si se agregó exitosamente)
    if new_block_id:
        print(f"\n5️⃣ Removiendo número bloqueado...")
        response = remove_from_blocklist(token, new_block_id)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Número desbloqueado exitosamente")
        else:
            print(f"❌ Error al desbloquear número")
        
        # Listar bloqueados finales
        print(f"\n6️⃣ Listando bloqueados finales...")
        blocked = list_blocklist(token)
        print(f"✅ Total de números bloqueados: {len(blocked)}")
        for b in blocked:
            print(f"   - {b['phone_number']}: {b['reason']}")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
