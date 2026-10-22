#!/usr/bin/env python3
"""
Inicia el reto y lo publica en internet con un enlace https temporal y gratis (tunel de Cloudflare).
Funciona en Windows, Mac y Linux. Los estudiantes entran desde CUALQUIER red con el enlace que aparece.

    python iniciar_internet.py                 # (en Windows: py iniciar_internet.py)
    python iniciar_internet.py --clave MICLAVE # el resto de opciones pasan al servidor

El computador debe quedar encendido, con internet y esta ventana abierta durante todo el reto.
El enlace cambia cada vez que se inicia. La primera vez descarga la herramienta `cloudflared` (una sola vez).
"""
import argparse
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
HERR = AQUI / ".herramientas"
BASE = "https://github.com/cloudflare/cloudflared/releases/latest/download/"


def puerto_ocupado(puerto):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def descargar(url, destino):
    parcial = destino.with_name(destino.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "reto-desinformacion"})
    with urllib.request.urlopen(req, timeout=60) as r, open(parcial, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        hecho, ultimo = 0, 0
        while True:
            bloque = r.read(1 << 20)
            if not bloque:
                break
            f.write(bloque)
            hecho += len(bloque)
            if total and hecho - ultimo >= (4 << 20):
                print(f"    {hecho * 100 // total}%", end="\r", flush=True)
                ultimo = hecho
    parcial.replace(destino)
    print("    100%      ")


def buscar_cloudflared():
    ya = shutil.which("cloudflared")
    if ya:
        return ya
    nombre = "cloudflared.exe" if os.name == "nt" else "cloudflared"
    local = HERR / nombre
    if local.exists():
        return str(local)
    HERR.mkdir(exist_ok=True)
    sistema, arq = platform.system(), platform.machine().lower()
    print("\n  Descargando (una sola vez) la herramienta que crea el enlace publico...")
    if sistema == "Windows":
        descargar(BASE + "cloudflared-windows-amd64.exe", local)
    elif sistema == "Darwin":
        a = "arm64" if arq in ("arm64", "aarch64") else "amd64"
        tgz = HERR / "cf.tgz"
        descargar(BASE + f"cloudflared-darwin-{a}.tgz", tgz)
        with tarfile.open(tgz) as t, open(local, "wb") as f:
            f.write(t.extractfile("cloudflared").read())
        tgz.unlink()
    else:
        a = "arm64" if arq in ("arm64", "aarch64") else "amd64"
        descargar(BASE + f"cloudflared-linux-{a}", local)
    if os.name != "nt":
        os.chmod(local, 0o755)
    return str(local)


def esperar_url(ruta_log, proceso, segundos=40):
    patron = re.compile(r"https://[-a-z0-9]+\.trycloudflare\.com")
    fin = time.time() + segundos
    while time.time() < fin:
        try:
            m = patron.search(Path(ruta_log).read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            m = None
        if m:
            return m.group(0)
        if proceso.poll() is not None:
            break
        time.sleep(0.5)
    return None


def mantener_despierto():
    """Evita que el computador se duerma mientras el reto esta abierto."""
    try:
        if os.name == "nt":
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)
        elif platform.system() == "Darwin" and shutil.which("caffeinate"):
            subprocess.Popen(["caffeinate", "-dis", "-w", str(os.getpid())])
    except Exception:  # noqa: BLE001
        pass


def main():
    if os.name == "nt":
        os.system("chcp 65001 >nul")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--puerto", type=int, default=int(os.environ.get("PORT", 8000)))
    a, extra = ap.parse_known_args()

    if puerto_ocupado(a.puerto):
        print(f"\n  Ya hay algo abierto en el puerto {a.puerto} (¿otra ventana del reto?). Cierrala y vuelve a intentar.")
        return 1
    try:
        cf = buscar_cloudflared()
    except Exception as e:  # noqa: BLE001
        print(f"\n  No se pudo descargar la herramienta del enlace publico ({e}). Revisa que haya internet.")
        return 1

    log = tempfile.NamedTemporaryFile(prefix="tunel_", suffix=".log", delete=False)
    log.close()
    with open(log.name, "wb") as f:
        tunel = subprocess.Popen([cf, "tunnel", "--no-autoupdate", "--url", f"http://localhost:{a.puerto}"],
                                 stdout=f, stderr=subprocess.STDOUT)
    try:
        print("\n  Creando el enlace publico (unos segundos)...")
        url = esperar_url(log.name, tunel)
        if not url:
            print("  No se pudo crear el enlace. Revisa que haya internet. Detalle:")
            print("  " + "\n  ".join(Path(log.name).read_text(encoding="utf-8", errors="ignore").splitlines()[-5:]))
            return 1
        mantener_despierto()
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        subprocess.run([sys.executable, str(AQUI / "servidor.py"), "--puerto", str(a.puerto),
                        "--url-publica", url, *extra], env=env)
    except KeyboardInterrupt:
        pass
    finally:
        tunel.terminate()
        try:
            tunel.wait(timeout=5)
        except subprocess.TimeoutExpired:
            tunel.kill()
        try:
            os.unlink(log.name)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    codigo = main()
    try:
        input("\n  Pulsa Enter para cerrar...")
    except (EOFError, KeyboardInterrupt):
        pass
    sys.exit(codigo)
