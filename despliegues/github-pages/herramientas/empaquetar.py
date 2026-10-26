"""Arma el paquete que se sube a PythonAnywhere: ``despliegues/github-pages/dist/reto_para_internet.zip``.

Junta el servidor y el WSGI de ``src/``, las pantallas de ``web/`` y el banco de ``2_Aplicacion_Reto/`` con la
misma estructura que espera ``wsgi_pythonanywhere.py`` (todo dentro de ``2_Aplicacion_Reto/``). Solo usa la
biblioteca estándar.

Uso, desde la raíz del repositorio::

    python despliegues/github-pages/herramientas/empaquetar.py

El ``.zip`` lleva el banco con las respuestas: no se versiona (``dist/`` está en ``.gitignore``) y solo se sube a
PythonAnywhere.
"""

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
OPCION = RAIZ / "despliegues" / "github-pages"
DESTINO = OPCION / "dist" / "reto_para_internet.zip"
CARPETA = "2_Aplicacion_Reto"


def archivos() -> list[tuple[Path, str]]:
    """Lista lo que va en el paquete.

    Returns:
        Pares (archivo en el repositorio, ruta dentro del ``.zip``).
    """
    pares = [
        (OPCION / "src" / "servidor.py", f"{CARPETA}/servidor.py"),
        (OPCION / "src" / "wsgi_pythonanywhere.py", f"{CARPETA}/wsgi_pythonanywhere.py"),
        (RAIZ / CARPETA / "banco_preguntas.json", f"{CARPETA}/banco_preguntas.json"),
    ]
    web = OPCION / "web"
    pares += [(f, f"{CARPETA}/web/{f.relative_to(web).as_posix()}") for f in sorted(web.rglob("*")) if f.is_file()]
    return pares


def main() -> int:
    """Escribe el ``.zip`` y lista su contenido.

    Returns:
        0 si quedó listo; 1 si falta algún archivo.
    """
    pares = archivos()
    faltan = [str(origen) for origen, _ in pares if not origen.is_file()]
    if faltan:
        print("Faltan archivos:", *faltan, sep="\n  ", file=sys.stderr)
        return 1
    DESTINO.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as paquete:
        for origen, nombre in pares:
            paquete.write(origen, nombre)
    print(f"Listo: {DESTINO.relative_to(RAIZ)} ({DESTINO.stat().st_size // 1024} KB)")
    for _, nombre in pares:
        print("  " + nombre)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
