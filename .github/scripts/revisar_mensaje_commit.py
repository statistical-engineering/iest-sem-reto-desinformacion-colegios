"""Revisa que un mensaje de commit (o el título de un PR) siga el estándar del equipo.

Estándar:
    tipo(alcance opcional): descripción en español

    Cuerpo opcional, separado por una línea vacía.

- ``tipo`` sale de ``TIPOS``.
- La descripción empieza en minúscula con un verbo en infinitivo («agregar», «corregir»)
  y no termina en punto.
- Ninguna línea pasa de ``MAX_LINEA`` caracteres, salvo las que llevan un enlace.

Uso (pre-commit pasa la ruta del archivo del mensaje)::

    python .github/scripts/revisar_mensaje_commit.py RUTA [RUTA ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TIPOS = ("feat", "fix", "refactor", "chore", "docs", "test", "perf", "build", "ci", "style", "revert")
MAX_LINEA = 72
PREFIJOS_EXENTOS = ("Merge ", 'Revert "', "fixup! ", "squash! ", "amend! ")
TIJERAS = "# ------------------------ >8 ------------------------"
ENCABEZADO = re.compile(r"^(?P<tipo>[a-z]+)(\([a-z0-9_./-]+\))?!?: (?P<descripcion>.+)$")
INFINITIVO = re.compile(r"^[a-záéíóúñ]+(ar|er|ir)$")


def limpiar(texto: str) -> list[str]:
    """Quita los comentarios de git y lo que va después de las tijeras.

    Args:
        texto: mensaje tal como lo guarda git.

    Returns:
        Las líneas del mensaje, sin líneas vacías al final.
    """
    lineas = []
    for linea in texto.splitlines():
        if linea.startswith(TIJERAS):
            break
        if not linea.startswith("#"):
            lineas.append(linea.rstrip())
    while lineas and not lineas[-1]:
        lineas.pop()
    return lineas


def revisar_encabezado(encabezado: str) -> list[str]:
    """Revisa la primera línea del mensaje.

    Args:
        encabezado: primera línea del mensaje.

    Returns:
        Los errores encontrados; vacío si cumple.
    """
    coincidencia = ENCABEZADO.match(encabezado)
    if coincidencia is None:
        return [f"La primera línea debe ser «tipo: descripción» (tipos: {', '.join(TIPOS)})."]
    errores = []
    if coincidencia["tipo"] not in TIPOS:
        errores.append(f"Tipo «{coincidencia['tipo']}» no permitido; usa uno de: {', '.join(TIPOS)}.")
    primera_palabra = coincidencia["descripcion"].split()[0]
    if not INFINITIVO.match(primera_palabra):
        errores.append(f"La descripción debe empezar en minúscula con un verbo en infinitivo, no «{primera_palabra}».")
    if encabezado.endswith("."):
        errores.append("La primera línea no termina en punto.")
    return errores


def revisar_mensaje(texto: str) -> list[str]:
    """Revisa un mensaje completo contra el estándar.

    Args:
        texto: mensaje de commit o título de PR.

    Returns:
        Los errores encontrados; vacío si cumple o si es un mensaje que git genera solo.
    """
    lineas = limpiar(texto)
    if not lineas:
        return ["El mensaje está vacío."]
    if lineas[0].startswith(PREFIJOS_EXENTOS):
        return []
    errores = revisar_encabezado(lineas[0])
    if len(lineas) > 1 and lineas[1]:
        errores.append("La segunda línea debe quedar vacía para separar el cuerpo.")
    for numero, linea in enumerate(lineas, start=1):
        if len(linea) > MAX_LINEA and "http" not in linea:
            errores.append(f"La línea {numero} tiene {len(linea)} caracteres; el máximo es {MAX_LINEA}.")
    return errores


def main(rutas: list[str]) -> int:
    """Revisa cada archivo de mensaje e imprime los errores.

    Args:
        rutas: rutas de los archivos con mensajes.

    Returns:
        0 si todos cumplen, 1 si alguno falla.
    """
    codigo = 0
    for ruta in rutas:
        errores = revisar_mensaje(Path(ruta).read_text(encoding="utf-8"))
        for error in errores:
            print(f"{ruta}: {error}", file=sys.stderr)
        codigo = codigo or int(bool(errores))
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
