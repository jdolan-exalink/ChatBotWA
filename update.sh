#!/usr/bin/env bash
# update.sh — descarga los últimos cambios y reconstruye el contenedor
set -e

echo "🔄 Actualizando repositorio..."
git pull

echo "🔨 Reconstruyendo contenedor (sin caché)..."
docker compose build --no-cache wa-bot

echo "🚀 Reiniciando servicios..."
docker compose up -d

echo "✅ Actualización completada. Versión activa:"
sleep 5
curl -s http://localhost:8088/version || echo "(el servicio aún está arrancando)"
