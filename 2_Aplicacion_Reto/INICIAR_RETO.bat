@echo off
chcp 65001 >nul
title Reto - Detectives de la desinformacion
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 goto conpy
where python >nul 2>nul
if not errorlevel 1 goto conpython
echo.
echo   No se encontro Python en este computador.
echo   Instalalo gratis desde https://www.python.org/downloads/
echo   Durante la instalacion marca la casilla "Add python.exe to PATH".
echo.
pause
exit /b 1
:conpy
py -3 servidor.py %*
goto fin
:conpython
python servidor.py %*
:fin
echo.
pause
