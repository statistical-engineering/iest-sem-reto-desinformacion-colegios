#!/bin/bash
# Inicia el reto y lo publica en internet con un enlace https (tunel gratuito de Cloudflare).
# Sirve cuando los estudiantes NO estan en tu misma red wifi (casa, otro colegio, wifi con aislamiento).
# El enlace cambia cada vez que se inicia. Deja esta ventana abierta durante todo el reto.
cd "$(dirname "$0")" || exit 1
PUERTO=8000

parar() {
  echo; read -n 1 -s -r -p "  Pulsa una tecla para cerrar..."; exit 1
}

if ! command -v python3 >/dev/null 2>&1; then
  echo; echo "  No se encontro Python 3. Instalalo desde https://www.python.org/downloads/"; parar
fi

if ! command -v cloudflared >/dev/null 2>&1; then
  echo
  echo "  Falta 'cloudflared' (la herramienta gratuita que crea el enlace publico)."
  if command -v brew >/dev/null 2>&1; then
    echo "  Instalandolo con Homebrew..."
    brew install cloudflared || { echo "  No se pudo instalar. Prueba en Terminal: brew install cloudflared"; parar; }
  else
    echo "  Instala Homebrew (https://brew.sh) y luego en Terminal escribe:  brew install cloudflared"
    echo "  Despues vuelve a abrir este archivo."
    parar
  fi
fi

LOG=$(mktemp)
cloudflared tunnel --no-autoupdate --url "http://localhost:$PUERTO" >"$LOG" 2>&1 &
TPID=$!
trap 'kill $TPID 2>/dev/null; rm -f "$LOG"' EXIT
trap 'exit 0' INT TERM

echo; echo "  Creando el enlace publico (unos segundos)..."
URL=""
for _ in $(seq 1 60); do
  URL=$(grep -o 'https://[-a-z0-9]*\.trycloudflare\.com' "$LOG" | head -1)
  [ -n "$URL" ] && break
  kill -0 $TPID 2>/dev/null || break
  sleep 0.5
done
if [ -z "$URL" ]; then
  echo "  No se pudo crear el enlace. Revisa que haya internet. Detalle:"; tail -5 "$LOG"; parar
fi

python3 servidor.py --puerto "$PUERTO" --url-publica "$URL" "$@"
echo; read -n 1 -s -r -p "Pulsa una tecla para cerrar..."
