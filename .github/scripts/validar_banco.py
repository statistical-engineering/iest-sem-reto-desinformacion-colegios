"""Comprueba, sin modificarlo, que el banco de preguntas sea JSON válido y sume 1.000 puntos.

Solo lee identificadores y puntos: nunca imprime enunciados ni respuestas.

Uso::

    python .github/scripts/validar_banco.py [RUTA_DEL_BANCO]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PUNTOS_TOTALES = 1000
BANCO = Path("2_Aplicacion_Reto/banco_preguntas.json")


def revisar_banco(banco: dict[str, Any]) -> list[str]:
    """Revisa los puntos y los identificadores del banco.

    Args:
        banco: contenido de ``banco_preguntas.json``.

    Returns:
        Los errores encontrados; vacío si el banco cumple.
    """
    preguntas = [p for mision in banco.get("misiones", []) for p in mision.get("preguntas", [])]
    ids = [p.get("id") for p in preguntas]
    total = sum(p.get("puntos", 0) for p in preguntas)
    errores = []
    if total != PUNTOS_TOTALES:
        errores.append(f"El banco suma {total} puntos, no {PUNTOS_TOTALES}.")
    if banco.get("puntos_totales") != PUNTOS_TOTALES:
        errores.append(f"«puntos_totales» vale {banco.get('puntos_totales')}, no {PUNTOS_TOTALES}.")
    repetidos = sorted({i for i in ids if ids.count(i) > 1}, key=str)
    if repetidos:
        errores.append(f"Identificadores de pregunta repetidos: {repetidos}.")
    return errores


def main(ruta: Path) -> int:
    """Lee el banco e imprime los errores.

    Args:
        ruta: ruta de ``banco_preguntas.json``.

    Returns:
        0 si el banco cumple, 1 si no.
    """
    try:
        banco = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"{ruta}: no se pudo leer como JSON: {error}", file=sys.stderr)
        return 1
    errores = revisar_banco(banco)
    for error in errores:
        print(f"{ruta}: {error}", file=sys.stderr)
    return int(bool(errores))


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else BANCO))
