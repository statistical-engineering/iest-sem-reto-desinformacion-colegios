"""Revisa que la columna de una opción en despliegues/COMPARACION.md diga de dónde sale cada cifra.

Una casilla sin medir empieza por «pendiente» o «Sin medir» y no necesita fuente. Cualquier otra casilla debe
traer una URL ``https://`` o un comando entre comillas invertidas (FR12.4). Solo usa la biblioteca estándar.

Uso, desde la raíz del repositorio:

    python3 despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion render

Termina con código 0 y «TODO BIEN», o con código 1 y la lista de filas sin fuente.
"""

import argparse
import pathlib
import sys

TABLA = pathlib.Path(__file__).resolve().parents[2] / "COMPARACION.md"
SIN_MEDIR = ("pendiente", "Sin medir")


def filas_sin_fuente(texto: str, opcion: str) -> list[str]:
    """Devuelve los criterios cuya casilla de ``opcion`` tiene una cifra sin URL ni comando.

    Args:
        texto: contenido de COMPARACION.md.
        opcion: nombre de la columna, sin importar mayúsculas (por ejemplo «render»).

    Returns:
        Los criterios que fallan, en el orden de la tabla.

    Raises:
        ValueError: si la tabla no tiene esa columna.

    Justificación: paso aislado, probado en test_revisar_comparacion.TestFilasSinFuente.test_detecta_cifra_sin_url.
    """
    lineas = [linea.strip() for linea in texto.splitlines() if linea.startswith("|")]
    filas = [[c.strip() for c in linea.strip("|").split("|")] for linea in lineas]
    encabezado = next((f for f in filas if f[0] == "Criterio"), [])
    nombres = [n.lower() for n in encabezado]
    if opcion.lower() not in nombres:
        raise ValueError(f"COMPARACION.md no tiene la columna «{opcion}»")
    columna = nombres.index(opcion.lower())
    cuerpo = [f for f in filas if f[0] not in ("Criterio", "") and not set(f[0]) <= set("-")]
    return [
        f[0]
        for f in cuerpo
        if not f[columna].startswith(SIN_MEDIR) and "https://" not in f[columna] and "`" not in f[columna]
    ]


def main() -> int:
    """Lee la tabla, revisa la columna pedida e imprime el resultado.

    Returns:
        0 si todas las casillas tienen fuente; 1 si alguna no la tiene.
    """
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--opcion", required=True, help="columna de COMPARACION.md, por ejemplo render")
    opcion = argumentos.parse_args().opcion
    fallas = filas_sin_fuente(TABLA.read_text(encoding="utf-8"), opcion)
    for criterio in fallas:
        print(f"FALTA FUENTE: {opcion} / {criterio}")
    if fallas:
        return 1
    print(f"TODO BIEN: cada cifra de la columna {opcion} tiene URL o comando.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
