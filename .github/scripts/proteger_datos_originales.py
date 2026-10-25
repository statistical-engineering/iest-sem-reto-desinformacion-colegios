"""Rechaza cualquier cambio en ``4_Codigo_y_datos/datos_originales/``, la fuente única de verdad.

Revisa los archivos del commit en preparación o, en un PR, los del rango que pre-commit recibe
con ``--from-ref`` y ``--to-ref``. Así ``pre-commit run --all-files`` no falla por archivos que
ya existen y no cambiaron.
"""

from __future__ import annotations

import os
import subprocess
import sys

CARPETA = "4_Codigo_y_datos/datos_originales/"


def archivos_cambiados() -> list[str]:
    """Lista los archivos cambiados en el commit en preparación o en el rango del PR.

    Returns:
        Rutas relativas a la raíz del repositorio.

    Raises:
        subprocess.CalledProcessError: si git falla.
    """
    desde, hasta = os.environ.get("PRE_COMMIT_FROM_REF"), os.environ.get("PRE_COMMIT_TO_REF")
    rango = [f"{desde}...{hasta}"] if desde and hasta else ["--cached"]
    salida = subprocess.run(["git", "diff", "--name-only", *rango], check=True, capture_output=True, text=True)
    return salida.stdout.splitlines()


def main() -> int:
    """Imprime los archivos protegidos que cambiaron.

    Returns:
        0 si no cambió ninguno, 1 si cambió alguno.
    """
    tocados = [ruta for ruta in archivos_cambiados() if ruta.startswith(CARPETA)]
    for ruta in tocados:
        print(f"{ruta}: {CARPETA} es de solo lectura (fuente única de verdad).", file=sys.stderr)
    return int(bool(tocados))


if __name__ == "__main__":
    sys.exit(main())
