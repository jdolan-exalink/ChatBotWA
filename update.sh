#!/usr/bin/env bash
# update.sh — descarga los últimos cambios y reconstruye el contenedor
# USO: ./update.sh
# IMPORTANTE: siempre usar este script en vez de 'git pull' solo.
# El 'git pull' solo NO actualiza el contenedor Docker.
set -e

echo "🔄 Guardando cambios locales (stash)..."
git stash

echo "⬇️  Actualizando repositorio..."
git pull

echo "🔁 Restaurando cambios locales..."
git stash pop 2>/dev/null || echo "   (sin cambios locales que restaurar)"

echo "🛑 Deteniendo contenedor wa-bot..."
docker compose stop wa-bot

echo "🔨 Reconstruyendo imagen (sin caché)..."
docker compose build --no-cache wa-bot

echo "🚀 Iniciando servicios..."
docker compose up -d

echo "✅ Actualización completada. Versión activa:"
sleep 6
curl -s http://localhost:8088/version || echo "(el servicio aún está arrancando)"
