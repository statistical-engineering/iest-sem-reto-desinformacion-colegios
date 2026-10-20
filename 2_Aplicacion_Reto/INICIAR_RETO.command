#!/bin/bash
# Inicia el reto en Mac (equivalente a INICIAR_RETO.bat). Doble clic para abrir.
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "  No se encontro Python 3 en este Mac."
  echo "  Instalalo desde https://www.python.org/downloads/ y vuelve a abrir este archivo."
  echo
  read -n 1 -s -r -p "  Pulsa una tecla para cerrar..."
  exit 1
fi
python3 servidor.py "$@"
echo
read -n 1 -s -r -p "Pulsa una tecla para cerrar..."
