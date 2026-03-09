#!/usr/bin/env python3
"""
Importa números desde bloqueados.txt a la lista de bloqueados del bot.

Formato aceptado en el archivo (una entrada por línea):
  Nombre: +5493424343638
  +5493424343638
  5493424343638
  5493424343638  # comentario opcional tras el número
  # líneas que empiezan con # son ignoradas

Uso:
  python3 import_blocklist.py [--file bloqueados.txt] [--url http://localhost:8088] [--user admin] [--password admin123] [--reason "Importación masiva"]
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error

def parse_args():
    p = argparse.ArgumentParser(description="Importar blocklist desde archivo de texto")
    p.add_argument("--file",     default="bloqueados.txt",      help="Archivo de entrada (default: bloqueados.txt)")
    p.add_argument("--url",      default="http://localhost:8088", help="URL base del bot (default: http://localhost:8088)")
    p.add_argument("--user",     default="admin",               help="Usuario admin (default: admin)")
    p.add_argument("--password", default="admin123",            help="Contraseña admin (default: admin123)")
    p.add_argument("--reason",   default="Importación masiva",  help="Motivo por defecto para entradas sin nombre")
    p.add_argument("--dry-run",  action="store_true",           help="Mostrar qué se importaría sin hacer cambios")
    return p.parse_args()


def api_post(url, data, token=None):
    body = json.dumps(data).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def login(base_url, username, password):
    status, data = api_post(f"{base_url}/api/auth/login", {"username": username, "password": password})
    if status != 200:
        print(f"❌ Login fallido ({status}): {data}")
        sys.exit(1)
    return data["access_token"]


def parse_file(path):
    """
    Devuelve lista de (phone_str, reason_str).
    Acepta: 'Nombre: +numero', '+numero', 'numero', líneas con # al final.
    """
    entries = []
    with open(path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            # Quitar comentarios al final de la línea
            line = re.sub(r"\s*#.*$", "", line).strip()

            # Formato "Nombre: +numero" o "Nombre: numero"
            if ":" in line:
                parts = line.split(":", 1)
                name = parts[0].strip()
                phone = parts[1].strip()
                reason = name if name else "Importación masiva"
            else:
                phone = line.strip()
                reason = "Importación masiva"

            # Extraer solo dígitos y '+' del número (eliminar texto sobrante)
            phone = re.sub(r"[^\d+@.]", "", phone)
            if not phone:
                print(f"  ⚠️  Línea {lineno}: no se encontró número en '{raw.strip()}' — omitida")
                continue

            entries.append((phone, reason))
    return entries


def main():
    args = parse_args()

    print(f"📂 Leyendo {args.file}...")
    entries = parse_file(args.file)
    print(f"   {len(entries)} entradas encontradas\n")

    if not entries:
        print("✅ Nada para importar.")
        return

    if args.dry_run:
        print("🔍 Modo dry-run — no se realizarán cambios:\n")
        for phone, reason in entries:
            print(f"   {phone}  →  motivo: {reason}")
        return

    print(f"🔐 Autenticando como '{args.user}'...")
    token = login(args.url, args.user, args.password)
    print("   Token obtenido ✓\n")

    ok = 0; skipped = 0; errors = 0

    for phone, reason in entries:
        status, resp = api_post(
            f"{args.url}/api/blocklist",
            {"phone_number": phone, "reason": reason},
            token=token
        )
        if status in (200, 201):
            print(f"   ✅ Bloqueado: {phone}  ({reason})")
            ok += 1
        elif status == 400 and "ya bloqueado" in str(resp).lower():
            print(f"   ⚠️  Ya existía: {phone}")
            skipped += 1
        else:
            print(f"   ❌ Error {status} para {phone}: {resp}")
            errors += 1

    print(f"\n{'─'*50}")
    print(f"✅ Importados: {ok}  |  ⚠️  Ya existían: {skipped}  |  ❌ Errores: {errors}")


if __name__ == "__main__":
    main()
