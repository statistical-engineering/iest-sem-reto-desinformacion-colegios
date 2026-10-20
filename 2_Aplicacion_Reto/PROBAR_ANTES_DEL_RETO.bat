@echo off
chcp 65001 >nul
title Simulacro del reto (no toca los datos reales)
cd /d "%~dp0"
echo.
echo   Simulacro con 40 estudiantes ficticios en una base de datos temporal.
echo   No borra ni modifica las inscripciones reales.
echo.
where py >nul 2>nul
if not errorlevel 1 goto conpy
where python >nul 2>nul
if not errorlevel 1 goto conpython
echo   No se encontro Python. Instalalo desde https://www.python.org/downloads/
pause
exit /b 1
:conpy
py -3 pruebas\simulacro.py 40
goto fin
:conpython
python pruebas\simulacro.py 40
:fin
echo.
pause
