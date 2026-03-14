#!/usr/bin/env bash
# update.sh — descarga los últimos cambios y reconstruye el contenedor
set -e

echo "🔄 Actualizando repositorio..."
git pull

echo "🔨 Reconstruyendo y reiniciando contenedores..."
docker compose up -d --build

echo "✅ Actualización completada. Versión activa:"
sleep 5
curl -s http://localhost:8088/version || echo "(el servicio aún está arrancando)"
