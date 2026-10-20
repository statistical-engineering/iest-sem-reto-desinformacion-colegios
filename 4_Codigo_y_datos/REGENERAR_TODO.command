#!/bin/bash
# Repite todo el proceso en Mac (equivalente a REGENERAR_TODO.bat): análisis, banco de preguntas, clave y simulacro.
cd "$(dirname "$0")/scripts" || exit 1
fallo() { echo; echo "  Algo falló: lee el mensaje de arriba."; read -n 1 -s -r -p "  Pulsa una tecla para cerrar..."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "  Falta Python 3: https://www.python.org/downloads/"; fallo; }
echo; echo " 1/4  Análisis de los datos (tablas, gráficas y ANALISIS.md)..."; python3 generar_analisis.py || fallo
echo " 2/4  Banco de preguntas (con comprobación de cada clave)..."; python3 construir_banco.py || fallo
echo " 3/4  Clave de respuestas para el docente..."; python3 generar_clave_respuestas.py || fallo
echo " 4/4  Simulacro de la aplicación..."; python3 ../../2_Aplicacion_Reto/pruebas/simulacro.py 30 || fallo
echo; echo " Listo. Reinicia el servidor del reto para que tome los cambios."
read -n 1 -s -r -p " Pulsa una tecla para cerrar..."
