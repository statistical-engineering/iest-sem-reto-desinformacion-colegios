"""
Modo revisión del reto: abre la actividad como docente y como estudiante en el navegador.

Se abre con «ABRIR PARA HACER PRUEBA/ABRIR LA PRUEBA.bat». Usa una base de datos aparte
(2_Aplicacion_Reto/datos_prueba/), así que nunca toca
los datos del reto real. Cada vez que se abre empieza de cero.

    python modo_prueba.py            # empieza de cero
    python modo_prueba.py --seguir   # conserva lo que se hizo en la revisión anterior
"""
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SERVIDOR = AQUI / "servidor.py"
DATOS = AQUI / "datos_prueba"
PUERTO = 8010
CLAVE = "REVISAR"
SALA = "DEMO"
BASE = f"http://localhost:{PUERTO}"


def puerto_ocupado():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PUERTO)) == 0


def admin(ruta, datos):
    req = urllib.request.Request(BASE + ruta, data=json.dumps(datos).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "X-Clave-Admin": CLAVE})
    urllib.request.urlopen(req, timeout=5).read()


def main():
    if puerto_ocupado():
        print(f"\n  Ya hay una prueba abierta (puerto {PUERTO}). Ciérrala primero o usa esas pestañas.")
        webbrowser.open(BASE + "/admin")
        return
    if "--seguir" not in sys.argv and DATOS.exists():
        shutil.rmtree(DATOS, ignore_errors=True)
    DATOS.mkdir(exist_ok=True)

    proc = subprocess.Popen([sys.executable, str(SERVIDOR), "--puerto", str(PUERTO), "--clave", CLAVE,
                             "--db", str(DATOS / "reto.db")],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    for _ in range(60):
        if puerto_ocupado():
            break
        if proc.poll() is not None:
            print("\n  El servidor no pudo arrancar:\n", proc.stderr.read())
            return
        time.sleep(0.25)

    admin("/api/admin/config", {"sala": SALA, "evento": "Prueba de la actividad"})
    estado = json.loads(urllib.request.urlopen(BASE + "/api/publico", timeout=5).read())["estado"]
    if estado == "inscripcion":
        admin("/api/admin/estado", {"estado": "abierto"})

    linea = "=" * 66
    print(linea)
    print("  MODO PRUEBA — Detectives de la desinformación")
    print(linea)
    print(f"  Vista ESTUDIANTE:  {BASE}/          código de sala:  {SALA}")
    print(f"  Panel DOCENTE:     {BASE}/admin     clave docente:   {CLAVE}")
    print(f"  TABLERO (proyector): {BASE}/tablero")
    print(linea)
    print("  El reto ya está ABIERTO: inscríbete como estudiante y responde.")
    print("  Al terminar: en el panel docente pulsa «Cerrar el reto» y luego")
    print("  «Publicar resultados» para ver puntajes, podio y respuestas correctas.")
    print("  Para probar varios estudiantes a la vez, abre la vista estudiante en una")
    print("  ventana de incógnito (Ctrl+Shift+N) o en otro navegador.")
    print(linea)
    print("  Deja esta ventana abierta mientras revisas. Ciérrala para terminar.")
    print(linea)

    webbrowser.open(BASE + "/admin")
    time.sleep(0.6)
    webbrowser.open(BASE + "/tablero")
    time.sleep(0.6)
    webbrowser.open(BASE + "/")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    main()
