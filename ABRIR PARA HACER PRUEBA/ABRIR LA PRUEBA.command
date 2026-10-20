#!/bin/bash
# Abre el reto en modo prueba (estudiante + panel docente + tablero). Doble clic en Mac.
cd "$(dirname "$0")/../2_Aplicacion_Reto" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "  No se encontro Python 3. Instalalo desde https://www.python.org/downloads/"
  read -n 1 -s -r -p "  Pulsa una tecla para cerrar..."
  exit 1
fi
python3 modo_prueba.py "$@"
echo
read -n 1 -s -r -p "Pulsa una tecla para cerrar..."
