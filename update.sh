#!/usr/bin/env bash
# update.sh — descarga los últimos cambios y reconstruye el contenedor
# USO: ./update.sh
# IMPORTANTE: siempre usar este script en vez de 'git pull' solo.
set -e

# ── Preservar archivos de menú personalizados ────────────────────────────────
# Estos archivos se editan por cada instalación y NO deben pisarse con git pull.
echo "💾 Preservando archivos de configuración de menú..."
for f in data/MenuP.MD data/MenuF.MD; do
    if [ -f "$f" ]; then
        cp "$f" "/tmp/$(basename $f).bak"
        echo "   ✅ $f guardado"
    fi
done

echo "⬇️  Actualizando repositorio..."
git pull

# ── Restaurar menús personalizados (si existían antes del pull) ─────────────
echo "🔁 Restaurando archivos de menú personalizados..."
for f in data/MenuP.MD data/MenuF.MD; do
    bak="/tmp/$(basename $f).bak"
    if [ -f "$bak" ]; then
        cp "$bak" "$f"
        rm "$bak"
        echo "   ✅ $f restaurado"
    else
        echo "   ℹ️  $f es nuevo (instalación nueva) — usando versión del repositorio"
    fi
done

echo "🛑 Deteniendo contenedor wa-bot..."
docker compose stop wa-bot

echo "🔨 Reconstruyendo imagen (sin caché)..."
docker compose build --no-cache wa-bot

echo "🚀 Iniciando servicios..."
docker compose up -d

echo "✅ Actualización completada. Versión activa:"
sleep 6
curl -s http://localhost:8088/version || echo "(el servicio aún está arrancando)"
