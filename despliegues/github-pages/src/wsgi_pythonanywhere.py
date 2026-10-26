# Archivo WSGI para publicar el reto en PythonAnywhere (cuenta gratuita).
#
# En PythonAnywhere: pestaña «Web» → enlace «WSGI configuration file» → borrar TODO lo que trae
# y pegar este contenido. Luego cambiar las dos líneas marcadas con  <<<  y pulsar «Reload».
# Guía completa: carpeta «PUBLICAR EN INTERNET» → GUIA_PUBLICAR_GRATIS.md
import os
import sys

USUARIO = "TU_USUARIO"  # <<< tu nombre de usuario de PythonAnywhere
CLAVE = "CAMBIA-ESTA-CLAVE-2026"  # <<< clave del panel docente (mínimo 10 caracteres, no la compartas)

CARPETA = f"/home/{USUARIO}/reto/2_Aplicacion_Reto"
sys.path.insert(0, CARPETA)
os.environ["CLAVE_ADMIN"] = CLAVE
os.environ["RETO_DB"] = f"/home/{USUARIO}/reto_datos/reto.db"  # fuera de la carpeta del código
os.environ["RETO_JOURNAL"] = "DELETE"  # el disco de PythonAnywhere es de red: modo clásico de SQLite
os.environ["RETO_URL_PUBLICA"] = f"https://{USUARIO.lower()}.pythonanywhere.com"  # el dominio va en minúsculas

from servidor import crear_app  # noqa: E402

application = crear_app()
