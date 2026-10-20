#!/bin/bash
# Simulacro con 40 estudiantes ficticios (no toca los datos reales). Doble clic en Mac.
cd "$(dirname "$0")" || exit 1
echo
echo "  Simulacro con 40 estudiantes ficticios en una base de datos temporal."
echo "  No borra ni modifica las inscripciones reales."
echo
if ! command -v python3 >/dev/null 2>&1; then
  echo "  No se encontro Python 3. Instalalo desde https://www.python.org/downloads/"
  read -n 1 -s -r -p "  Pulsa una tecla para cerrar..."
  exit 1
fi
python3 pruebas/simulacro.py 40
echo
read -n 1 -s -r -p "Pulsa una tecla para cerrar..."
