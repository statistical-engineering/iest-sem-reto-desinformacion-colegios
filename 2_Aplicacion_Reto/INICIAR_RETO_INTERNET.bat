@echo off
chcp 65001 >nul
title Reto - Detectives de la desinformacion (por internet)
cd /d "%~dp0"
set "PY="
if exist "python\python.exe" "python\python.exe" -c "import sys; sys.exit(0 if sys.version_info[:2]>=(3,9) else 1)" >nul 2>nul && set PY="%CD%\python\python.exe"
if not defined PY py -3 -c "import sys; sys.exit(0 if sys.version_info[:2]>=(3,9) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info[:2]>=(3,9) else 1)" >nul 2>nul && set "PY=python"
if not defined PY goto sinpython
%PY% iniciar_internet.py %*
goto fin
:sinpython
echo.
echo   No se encontro un Python 3.9 o mas nuevo que funcione en este computador.
echo.
echo   OPCION A (sin permisos de administrador): descarga en https://www.python.org/downloads/windows/
echo      el "Windows embeddable package (64-bit)" (un .zip pequeno), haz clic derecho - Propiedades - Desbloquear,
echo      y extraelo dentro de esta carpeta en una subcarpeta llamada  python  (python.exe debe quedar ahi dentro).
echo   OPCION B: instala Python desde https://www.python.org/downloads/ marcando "Add python.exe to PATH".
echo   Si al escribir "python" se abre la Microsoft Store, cierrala: es un atajo falso de Windows.
echo.
pause
exit /b 1
:fin
echo.
pause
