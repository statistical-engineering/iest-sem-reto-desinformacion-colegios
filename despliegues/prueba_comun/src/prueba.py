"""Prueba común mínima del corte delgado (U1): la misma prueba contra cualquier versión del reto.

Recorre por HTTP los 8 pasos de «Prueba común mínima» (functional-spec.md de U1) y revisa que las pantallas
respondan. Solo usa la biblioteca estándar de Python.

Uso, desde la raíz del repositorio:

    python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8787 --clave CLAVE --modo nube
    python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8000 --clave CLAVE --modo local

Con ``--modo nube`` la clave es la del semillero y la prueba crea su propia sala. Con ``--modo local`` la clave
es la docente de servidor.py, la sala sale de /api/publico, el colegio va como texto y no se crean colegios.
La URL y la clave también se pueden dar con las variables PRUEBA_URL y PRUEBA_CLAVE.

Termina en «TODO BIEN» (código 0) o con la lista de lo que falló (código 1); si no hay conexión, código 2.
Nunca imprime claves, tokens ni respuestas correctas, y nunca pone una clave en la URL.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

SECRETAS = frozenset({"respuesta", "explicacion", "tolerancia", "verdad", "multitud_acierta", "veredicto"})
FORMA_OPACA = re.compile(r"^o[a-z2-7]{11}([a-z2-7]{5})?$")
OPACO_FALSO = "o" + "a" * 11
PANTALLAS = ("/", "/admin", "/tablero", "/static/css/reto.css", "/static/js/estudiante.js")
BANCO_POR_URL = ("/static/banco_preguntas.json", "/banco.json", "/src/banco.json")


@dataclass
class Prueba:
    """Una corrida: a qué URL se le pide, con qué clave y modo, lo que se va guardando y lo que falló."""

    url: str
    clave: str
    modo: str
    fallas: list[str] = field(default_factory=list)
    datos: dict[str, Any] = field(default_factory=dict)

    @property
    def nube(self) -> bool:
        """Si la versión probada es una de la nube (con salas y colegios)."""
        return self.modo == "nube"

    def pedir(
        self, ruta: str, cuerpo: dict[str, Any] | None = None, *, token: str = "", clave: str = "", crudo: bool = False
    ) -> tuple[int, Any]:
        """Hace una petición GET (sin cuerpo) o POST (con cuerpo JSON).

        Args:
            ruta: ruta con su consulta, por ejemplo ``/api/publico?sala=KQMT``.
            cuerpo: cuerpo JSON; si falta, la petición es GET.
            token: token del participante para la cabecera Authorization.
            clave: clave para la cabecera X-Clave-Admin.
            crudo: devuelve el texto en vez de leer JSON.

        Returns:
            El código HTTP y el cuerpo de la respuesta.
        """
        cabeceras = {"Content-Type": "application/json"}
        if token:
            cabeceras["Authorization"] = f"Bearer {token}"
        if clave:
            cabeceras["X-Clave-Admin"] = clave
        datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
        metodo = "GET" if cuerpo is None else "POST"
        peticion = urllib.request.Request(self.url + ruta, data=datos, headers=cabeceras, method=metodo)
        try:
            with urllib.request.urlopen(peticion, timeout=20) as respuesta:
                return respuesta.status, leer(respuesta.read(), crudo)
        except urllib.error.HTTPError as error:
            return error.code, leer(error.read(), crudo)

    def comprobar(self, condicion: bool, mensaje: str) -> bool:
        """Imprime una comprobación y guarda el mensaje si falló.

        Returns:
            La misma condición, para poder detener la prueba si algo esencial falló.
        """
        print(("  ✔ " if condicion else "  ✘ ") + mensaje)
        if not condicion:
            self.fallas.append(mensaje)
        return condicion


def leer(bytes_cuerpo: bytes, crudo: bool) -> Any:
    """Lee el cuerpo de una respuesta.

    Returns:
        El texto si ``crudo``; si no, el JSON, o ``{"error": ...}`` si la respuesta no era JSON (por ejemplo, la
        página de error de la plataforma).
    """
    texto = bytes_cuerpo.decode("utf-8", "replace")
    if crudo:
        return texto
    try:
        return json.loads(texto) if texto.strip() else {}
    except json.JSONDecodeError:
        return {"error": "la respuesta no es JSON"}


def claves_de(valor: Any) -> set[str]:
    """Todas las claves de los objetos dentro de ``valor``, a cualquier profundidad.

    Justificación: paso aislado, usado por los pasos 5 y 7 de la prueba.
    """
    if isinstance(valor, dict):
        return set(valor) | {k for v in valor.values() for k in claves_de(v)}
    if isinstance(valor, list):
        return {k for v in valor for k in claves_de(v)}
    return set()


def ids_publicos(misiones: list[dict[str, Any]]) -> list[str]:
    """Ids de opciones, ítems, publicaciones y partes que ve el navegador."""
    ids = []
    for pregunta in (q for m in misiones for q in m.get("preguntas", [])):
        for clave in ("opciones", "items", "publicaciones", "partes"):
            ids += [o["id"] for o in pregunta.get(clave, [])]
        ids += [o["id"] for parte in pregunta.get("partes", []) for o in parte["opciones"]]
    return ids


def sufijo() -> str:
    """Texto único por corrida, para que una segunda corrida no choque con nombres repetidos."""
    return time.strftime("%Y-%m-%d %H:%M:%S") + f".{time.time_ns() % 1_000_000:06d}"


def paso_1_salud(p: Prueba) -> bool:
    """Paso 1: el chequeo de salud."""
    estado, cuerpo = p.pedir("/api/publico")
    if p.nube:
        return p.comprobar(estado == 200 and cuerpo == {"ok": True}, 'GET /api/publico sin ?sala= da solo {"ok": true}')
    return p.comprobar(estado == 200, "GET /api/publico responde 200")


def paso_2_nube(p: Prueba) -> bool:
    """Paso 2 en la nube: con la clave del semillero se crea una sala; con una clave mala, 403."""
    estado, _ = p.pedir("/api/admin/salas/crear", {}, clave="ESTANOESLACLAVE")
    p.comprobar(estado == 403, "crear una sala con una clave mala da 403")
    estado, _ = p.pedir("/api/admin/login", {}, clave="ZZZZ-NOEXISTE")
    p.comprobar(estado == 403, "una clave de sala que no existe da 403")
    estado, r = p.pedir("/api/admin/salas/crear", {"evento": "Prueba común"}, clave=p.clave)
    creada = estado == 200 and str(r.get("clave", "")).startswith(f"{r.get('sala')}-")
    if not p.comprobar(creada, "con la clave del semillero se crea una sala con su clave"):
        return False
    p.datos.update(sala=r["sala"], clave_sala=r["clave"])
    estado, _ = p.pedir(f"/api/admin/login?sala={r['sala']}&clave={r['clave']}", {})
    p.comprobar(estado == 403, "la clave en la URL (?clave=) no sirve: 403")
    _, r = p.pedir("/api/admin/login", {}, clave=r["clave"].lower())
    p.comprobar(r.get("rol") == "sala" and r.get("sala") == p.datos["sala"], "la clave de la sala entra con rol «sala»")
    _, r = p.pedir("/api/admin/login", {}, clave=p.clave)
    return p.comprobar(r.get("rol") == "semillero", "la clave del semillero entra con rol «semillero»")


def paso_2_local(p: Prueba) -> bool:
    """Paso 2 en local: la clave docente entra y una mala da 403; la sala sale de /api/publico."""
    estado, _ = p.pedir("/api/admin/login", {}, clave="ESTANOESLACLAVE")
    p.comprobar(estado == 403, "una clave mala da 403")
    estado, _ = p.pedir("/api/admin/login", {}, clave=p.clave)
    _, publico = p.pedir("/api/publico")
    p.datos.update(sala=publico.get("sala", ""), clave_sala=p.clave, colegio="Colegio de prueba")
    return p.comprobar(estado == 200 and bool(p.datos["sala"]), "la clave docente entra y /api/publico da la sala")


def paso_3_nube(p: Prueba) -> bool:
    """Paso 3 en la nube: colegio provisional con nombre único, colegio repetido, acceso por sala y apertura."""
    sala, clave = p.datos["sala"], p.datos["clave_sala"]
    nombre = f"Colegio de prueba {sufijo()}"
    estado, r = p.pedir(f"/api/admin/colegios?sala={sala}", {"accion": "provisional", "nombre": nombre}, clave=clave)
    if not p.comprobar(estado == 200 and bool(r.get("id_colegio")), "se agrega un colegio provisional a la sala"):
        return False
    p.datos["colegio"] = r["id_colegio"]
    otro = {"accion": "provisional", "nombre": "  " + nombre.upper()}
    estado, r = p.pedir(f"/api/admin/colegios?sala={sala}", otro, clave=clave)
    p.comprobar(estado == 400 and "existente" in r, "el mismo colegio en mayúsculas da 400 con «existente»")
    estado, _ = p.pedir("/api/admin/estado", {"estado": "abierto"}, clave=p.clave)
    p.comprobar(estado == 400, "con la clave del semillero y sin ?sala= da 400")
    estado, _ = p.pedir("/api/admin/estado?sala=ZZZZ", {"estado": "abierto"}, clave=clave)
    p.comprobar(estado == 403, "con la clave de la sala no se actúa sobre otra sala (403)")
    estado, _ = p.pedir("/api/admin/estado", {"estado": "abierto"}, clave=clave)
    _, publico = p.pedir(f"/api/publico?sala={sala}")
    _, lista = p.pedir(f"/api/colegios?sala={sala}")
    ids = [c.get("id_colegio") for c in lista.get("colegios", [])]
    p.comprobar(p.datos["colegio"] in ids, "/api/colegios?sala= ofrece el colegio agregado")
    return p.comprobar(estado == 200 and publico.get("estado") == "abierto", "la sala queda abierta")


def paso_3_local(p: Prueba) -> bool:
    """Paso 3 en local: sin colegios; solo se abre la sala."""
    estado, _ = p.pedir(f"/api/admin/estado?sala={p.datos['sala']}", {"estado": "abierto"}, clave=p.clave)
    _, publico = p.pedir("/api/publico")
    return p.comprobar(estado == 200 and publico.get("estado") == "abierto", "la sala queda abierta")


def paso_4_inscripcion(p: Prueba) -> bool:
    """Paso 4: inscripción, inscripción repetida y volver a entrar con el código."""
    ficha = {
        "nombre": f"Detective de prueba {sufijo()}",
        "colegio": p.datos["colegio"],
        "grado": "10",
        "integrantes": "",
        "sala": p.datos["sala"].lower(),
    }
    if p.nube:
        estado, _ = p.pedir("/api/registro", {**ficha, "colegio": "cNOEXISTE"})
        p.comprobar(estado == 400, "un colegio que no está en la lista de la sala da 400")
    estado, r = p.pedir("/api/registro", ficha)
    if not p.comprobar(estado == 200 and len(str(r.get("codigo", ""))) == 5, "se inscribe un participante"):
        return False
    p.datos.update(token=r["token"], codigo=r["codigo"])
    estado, _ = p.pedir("/api/registro", {**ficha, "nombre": ficha["nombre"].upper()})
    p.comprobar(estado == 400, "no deja inscribir dos veces el mismo nombre, colegio y grado")
    _, r = p.pedir("/api/entrar", {"codigo": p.datos["codigo"].lower()})
    p.comprobar(r.get("token") == p.datos["token"], "entrar con el código recupera la sesión")
    estado, _ = p.pedir("/api/entrar", {"codigo": "00000"})
    return p.comprobar(estado == 404, "un código que no existe da 404")


def paso_5_comenzar(p: Prueba) -> bool:
    """Paso 5: comienza; /api/estado no trae respuesta, explicación, tolerancia ni veredicto."""
    estado, _ = p.pedir("/api/comenzar", {}, token=p.datos["token"])
    p.comprobar(estado == 200, "comenzar responde 200")
    _, r = p.pedir("/api/estado", token=p.datos["token"])
    misiones = r.get("misiones", [])
    p.datos["misiones"] = misiones
    en_curso = r.get("participante", {}).get("estado") == "en_curso" and bool(misiones)
    if not p.comprobar(en_curso, "el participante queda en curso y recibe las misiones"):
        return False
    fugas = (claves_de(misiones) & SECRETAS) | ({"revision"} & set(r))
    p.comprobar(not fugas, "/api/estado no trae respuesta, explicación, tolerancia ni veredicto")
    if p.nube:
        p.comprobar(
            all(FORMA_OPACA.match(i) for i in ids_publicos(misiones)), "todos los ids que ve el navegador son opacos"
        )
    return True


def paso_6_responder(p: Prueba) -> bool:
    """Paso 6: responde una pregunta «opcion»; responderla otra vez da 400 «ya respondida»."""
    preguntas = [
        q for m in p.datos["misiones"] for q in m["preguntas"] if q["tipo"] == "opcion" and not q.get("requiere")
    ]
    if not p.comprobar(bool(preguntas), "hay una pregunta «opcion» sin requisito para responder"):
        return False
    pregunta = preguntas[0]
    token = p.datos["token"]
    estado, _ = p.pedir("/api/responder", {"pregunta": pregunta["id"], "respuesta": OPACO_FALSO}, token=token)
    p.comprobar(estado == 400, "un id de opción que no corresponde da 400")
    respuesta = pregunta["opciones"][0]["id"]
    estado, r = p.pedir("/api/responder", {"pregunta": pregunta["id"], "respuesta": respuesta}, token=token)
    if not p.comprobar(estado == 200 and r.get("ok") is True, "responder una pregunta «opcion» da ok"):
        return False
    p.datos.update(pregunta=pregunta["id"], respuesta=respuesta)
    estado, r = p.pedir("/api/responder", {"pregunta": pregunta["id"], "respuesta": respuesta}, token=token)
    return p.comprobar(estado == 400 and "ya fue respondida" in r.get("error", ""), "responderla otra vez da 400")


def paso_7_guardada(p: Prueba) -> bool:
    """Paso 7: /api/estado muestra la respuesta guardada, con su id opaco en la nube."""
    _, r = p.pedir("/api/estado", token=p.datos["token"])
    guardada = r.get("respuestas", {}).get(p.datos["pregunta"], {}).get("respuesta")
    p.comprobar(guardada == p.datos["respuesta"], "/api/estado muestra la respuesta guardada tal como se envió")
    if p.nube:
        p.comprobar(bool(FORMA_OPACA.match(str(guardada))), "la respuesta guardada sale con su id opaco")
    return True


def paso_8_entrega(p: Prueba) -> bool:
    """Paso 8: entrega con /api/finalizar y /api/estado muestra «finalizado»."""
    token = p.datos["token"]
    estado, _ = p.pedir("/api/finalizar", {}, token=token)
    _, r = p.pedir("/api/estado", token=token)
    finalizado = estado == 200 and r.get("participante", {}).get("estado") == "finalizado"
    p.comprobar(finalizado, "después de entregar, /api/estado muestra «finalizado»")
    otra = {"pregunta": p.datos["pregunta"], "respuesta": p.datos["respuesta"]}
    estado, r = p.pedir("/api/responder", otra, token=token)
    return p.comprobar(estado == 400 and "terminó" in r.get("error", ""), "después de entregar no se acepta responder")


def paso_9_pantallas(p: Prueba) -> bool:
    """Pantallas: las páginas y sus estáticos dan 200; el banco nunca se sirve por URL (404)."""
    for ruta in PANTALLAS:
        estado, _ = p.pedir(ruta, crudo=True)
        p.comprobar(estado == 200, f"GET {ruta} responde 200")
    for ruta in BANCO_POR_URL:
        estado, _ = p.pedir(ruta, crudo=True)
        p.comprobar(estado == 404, f"GET {ruta} da 404: el banco no se sirve")
    return True


PASOS: dict[str, list[tuple[str, Callable[[Prueba], bool]]]] = {
    "nube": [
        ("1) Salud", paso_1_salud),
        ("2) Salas y claves", paso_2_nube),
        ("3) Colegio provisional y apertura", paso_3_nube),
        ("4) Inscripción", paso_4_inscripcion),
        ("5) Comenzar y examen sin fugas", paso_5_comenzar),
        ("6) Responder una vez", paso_6_responder),
        ("7) Respuesta guardada", paso_7_guardada),
        ("8) Entrega", paso_8_entrega),
        ("9) Pantallas", paso_9_pantallas),
    ],
    "local": [
        ("1) Salud", paso_1_salud),
        ("2) Clave docente", paso_2_local),
        ("3) Apertura", paso_3_local),
        ("4) Inscripción", paso_4_inscripcion),
        ("5) Comenzar y examen sin fugas", paso_5_comenzar),
        ("6) Responder una vez", paso_6_responder),
        ("7) Respuesta guardada", paso_7_guardada),
        ("8) Entrega", paso_8_entrega),
        ("9) Pantallas", paso_9_pantallas),
    ],
}


def correr(p: Prueba) -> int:
    """Corre los pasos en orden; si uno esencial falla, se detiene porque los demás dependen de él.

    Returns:
        0 si todo pasó, 1 si algo falló.
    """
    print(f"Prueba común · modo {p.modo} · {p.url}")
    for titulo, paso in PASOS[p.modo]:
        print(f"\n{titulo}")
        if not paso(p):
            p.fallas.append(f"la prueba se detuvo en «{titulo}»")
            break
    print("\n" + ("TODO BIEN: el corte cumple la prueba común." if not p.fallas else f"{len(p.fallas)} fallas:"))
    for falla in p.fallas:
        print("  -", falla)
    return 1 if p.fallas else 0


def main() -> int:
    """Lee los argumentos y corre la prueba.

    Returns:
        El código de salida: 0 todo bien, 1 con fallas, 2 sin conexión o sin datos.
    """
    lector = argparse.ArgumentParser(description="Prueba común mínima del reto (U1)")
    lector.add_argument("--url", default=os.environ.get("PRUEBA_URL", ""), help="URL de la versión a probar")
    lector.add_argument("--clave", default=os.environ.get("PRUEBA_CLAVE", ""), help="clave del semillero o docente")
    lector.add_argument("--modo", choices=sorted(PASOS), default="nube", help="nube (con salas) o local")
    argumentos = lector.parse_args()
    if not argumentos.url or not argumentos.clave:
        print("Falta la URL o la clave (--url y --clave, o PRUEBA_URL y PRUEBA_CLAVE).", file=sys.stderr)
        return 2
    prueba = Prueba(argumentos.url.rstrip("/"), argumentos.clave.strip(), argumentos.modo)
    try:
        return correr(prueba)
    except urllib.error.URLError as error:
        print(f"No hay conexión con {prueba.url}: {error.reason}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
