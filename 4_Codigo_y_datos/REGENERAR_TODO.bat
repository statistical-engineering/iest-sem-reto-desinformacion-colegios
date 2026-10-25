@echo off
chcp 65001 >nul
title Regenerar analisis, banco de preguntas y clave de respuestas
cd /d "%~dp0scripts"
where uv >nul 2>nul
if errorlevel 1 (
  echo  Falta uv: https://docs.astral.sh/uv/getting-started/installation/
  goto error
)
rem uv usa las versiones exactas de uv.lock (pandas, numpy, matplotlib).
set PY=uv run --group datos python
echo.
echo  1/4  Analisis de los datos (tablas, graficas y ANALISIS.md)...
%PY% generar_analisis.py || goto error
echo  2/4  Banco de preguntas (con comprobacion de cada clave)...
%PY% construir_banco.py || goto error
echo  3/4  Clave de respuestas para el docente...
%PY% generar_clave_respuestas.py || goto error
echo  4/4  Simulacro de la aplicacion...
%PY% ..\..\2_Aplicacion_Reto\pruebas\simulacro.py 30 || goto error
echo.
echo  Listo. Reinicia el servidor del reto para que tome los cambios.
pause
exit /b 0
:error
echo.
echo  Algo fallo: lee el mensaje de arriba.
pause
exit /b 1
