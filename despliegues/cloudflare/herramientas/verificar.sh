#!/usr/bin/env bash
# Verifica la opción Cloudflare Workers de punta a punta, en local y sin publicar nada.
#
# Uso, desde cualquier carpeta:   bash despliegues/cloudflare/herramientas/verificar.sh
# Requiere: bash, node 24, python3 y red para bajar wrangler la primera vez.
#
# Qué hace, en orden, y se detiene al primer fallo:
#   1. Pruebas de las reglas (node:test).
#   2. Levanta el Worker con `npx wrangler@4.148.0 dev` en el puerto 8787, espera la salud y corre la
#      prueba común en modo nube con la clave de prueba de .dev.vars (si no existe, crea una al azar).
#   3. Simulacro de la versión local (2_Aplicacion_Reto/), que debe decir «TODO BIEN».
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPCION="$(dirname "$AQUI")"
RAIZ="$(cd "$OPCION/../.." && pwd)"
PUERTO=8787

node --test "$OPCION/pruebas/reglas.test.js"

if [ ! -f "$OPCION/.dev.vars" ]; then
  CLAVE_NUEVA="$(python3 -c 'import secrets; print(secrets.token_hex(12))')"
  printf 'CLAVE_SEMILLERO=%s\n' "$CLAVE_NUEVA" > "$OPCION/.dev.vars"
fi
CLAVE="$(sed -n 's/^CLAVE_SEMILLERO=//p' "$OPCION/.dev.vars")"

mkdir -p "$OPCION/.wrangler"
(cd "$OPCION" && exec npx --yes wrangler@4.148.0 dev --port "$PUERTO" > "$OPCION/.wrangler/verificar.log" 2>&1) &
PID=$!
trap 'kill "$PID" 2>/dev/null || true; pkill -f "wrangler.*--port $PUERTO" 2>/dev/null || true' EXIT

for _ in $(seq 1 90); do
  if curl -fs "http://localhost:$PUERTO/api/publico" > /dev/null 2>&1; then break; fi
  sleep 1
done

python3 "$RAIZ/despliegues/prueba_comun/src/prueba.py" --url "http://localhost:$PUERTO" --clave "$CLAVE" --modo nube

(cd "$RAIZ/2_Aplicacion_Reto" && python3 pruebas/simulacro.py 40)

echo "VERIFICACION COMPLETA: reglas, prueba común en Workers y simulacro local."
