@echo off
chcp 65001 >nul
title PRUEBA DEL RETO - deja esta ventana abierta
cd /d "%~dp0..\2_Aplicacion_Reto"
where py >nul 2>nul
if not errorlevel 1 goto conpy
where python >nul 2>nul
if not errorlevel 1 goto conpython
echo.
echo   No se encontro Python. Instalalo gratis desde https://www.python.org/downloads/
echo   y marca la casilla "Add python.exe to PATH".
pause
exit /b 1
:conpy
py -3 modo_prueba.py
goto fin
:conpython
python modo_prueba.py
:fin
echo.
pause
