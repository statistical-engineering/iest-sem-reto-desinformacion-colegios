#!/bin/bash
# Repite todo el proceso en Mac (equivalente a REGENERAR_TODO.bat): análisis, banco de preguntas, clave y simulacro.
cd "$(dirname "$0")/scripts" || exit 1
fallo() { echo; echo "  Algo falló: lee el mensaje de arriba."; read -n 1 -s -r -p "  Pulsa una tecla para cerrar..."; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "  Falta uv: https://docs.astral.sh/uv/getting-started/installation/"; fallo; }
# uv usa las versiones exactas de uv.lock (pandas, numpy, matplotlib).
PY="uv run --group datos python"
echo; echo " 1/4  Análisis de los datos (tablas, gráficas y ANALISIS.md)..."; $PY generar_analisis.py || fallo
echo " 2/4  Banco de preguntas (con comprobación de cada clave)..."; $PY construir_banco.py || fallo
echo " 3/4  Clave de respuestas para el docente..."; $PY generar_clave_respuestas.py || fallo
echo " 4/4  Simulacro de la aplicación..."; $PY ../../2_Aplicacion_Reto/pruebas/simulacro.py 30 || fallo
echo; echo " Listo. Reinicia el servidor del reto para que tome los cambios."
read -n 1 -s -r -p " Pulsa una tecla para cerrar..."
