"""Varias salas a la vez (FR11.7): relojes, clasificaciones y claves no se mezclan.

Desde la raíz del repositorio::

    python -m unittest discover -s despliegues/github-pages/pruebas -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[3]
os.environ.setdefault("RETO_BANCO", str(RAIZ / "2_Aplicacion_Reto" / "banco_preguntas.json"))
os.environ.setdefault("RETO_WEB", str(RAIZ / "despliegues" / "github-pages" / "web"))
sys.path.insert(0, str(RAIZ / "despliegues" / "github-pages" / "src"))

import servidor  # noqa: E402

SEMILLERO = "CLAVEDELSEMILLERO"


def pedir(ruta: str, cuerpo: dict | None = None, *, clave: str = "", token: str = "") -> tuple[int, Any]:
    """GET (sin cuerpo) o POST (con cuerpo) a la API, como lo haría el navegador."""
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else b""
    cabeceras = {
        "Content-Length": str(len(datos)),
        "X-Clave-Admin": clave,
        "Authorization": f"Bearer {token}" if token else "",
        "Cookie": "reto_nav=" + "p" * 22,
    }
    metodo = "POST" if cuerpo is not None else "GET"
    codigo, _, respuesta, _ = servidor.atender(metodo, ruta, cabeceras.get, lambda _n: datos, "10.0.0.1")
    return codigo, json.loads(respuesta)


class Salas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.carpeta = tempfile.TemporaryDirectory()
        servidor.preparar(Path(cls.carpeta.name) / "reto.db", SEMILLERO)

    @classmethod
    def tearDownClass(cls) -> None:
        servidor.DB.close()
        cls.carpeta.cleanup()

    def nueva_sala(self, colegio: str) -> tuple[str, str, str]:
        """Crea una sala con un colegio; devuelve código, clave e id del colegio."""
        _, r = pedir("/api/admin/salas/crear", {"evento": colegio}, clave=SEMILLERO)
        _, c = pedir("/api/admin/colegios", {"accion": "provisional", "nombre": colegio}, clave=r["clave"])
        return r["sala"], r["clave"], c["id_colegio"]

    def inscribir(self, sala: str, colegio: str, nombre: str) -> str:
        ficha = {"nombre": nombre, "colegio": colegio, "grado": "10", "sala": sala}
        codigo, r = pedir("/api/registro", ficha)
        self.assertEqual(codigo, 200, r)
        return r["token"]

    def test_dos_salas_con_reloj_clasificacion_y_clave_propios(self) -> None:
        sala_a, clave_a, colegio_a = self.nueva_sala("Colegio Alfa")
        sala_b, clave_b, colegio_b = self.nueva_sala("Colegio Beta")
        token_a = self.inscribir(sala_a, colegio_a, "Ana Pérez")
        self.inscribir(sala_b, colegio_b, "Bruno Díaz")

        self.assertEqual(pedir("/api/admin/estado", {"estado": "abierto"}, clave=clave_a)[0], 200)
        self.assertEqual(pedir(f"/api/publico?sala={sala_b}")[1]["estado"], "inscripcion")
        pedir("/api/admin/reloj", {"accion": "pausar"}, clave=clave_a)
        self.assertTrue(pedir(f"/api/publico?sala={sala_a}")[1]["reloj"]["pausado"])
        pedir("/api/admin/estado", {"estado": "abierto"}, clave=clave_b)
        self.assertFalse(pedir(f"/api/publico?sala={sala_b}")[1]["reloj"]["pausado"])

        pedir("/api/comenzar", {}, token=token_a)
        pedir("/api/finalizar", {}, token=token_a)
        pedir("/api/admin/estado", {"estado": "resultados"}, clave=clave_a)
        self.assertEqual(pedir(f"/api/publico?sala={sala_b}")[1]["estado"], "abierto")
        nombres_b = [f["nombre"] for f in pedir(f"/api/publico?sala={sala_b}")[1].get("ranking", [])]
        self.assertNotIn("Ana Pérez", nombres_b)
        resumen_b = pedir(f"/api/admin/resumen?sala={sala_b}", clave=SEMILLERO)[1]
        self.assertEqual([p["nombre"] for p in resumen_b["participantes"]], ["Bruno Díaz"])

        self.assertEqual(pedir(f"/api/admin/resumen?sala={sala_b}", clave=clave_a)[0], 403)
        self.assertEqual(pedir(f"/api/admin/estado?sala={sala_b}", {"estado": "cerrado"}, clave=clave_a)[0], 403)
        self.assertEqual(pedir("/api/admin/salas", clave=clave_a)[0], 403)
        self.assertNotIn("clave", json.dumps(pedir("/api/admin/salas", clave=SEMILLERO)[1]))

    def test_regenerar_clave_y_borrar_sala(self) -> None:
        sala, clave, _ = self.nueva_sala("Colegio Gamma")
        _, nueva = pedir(f"/api/admin/salas/clave?sala={sala}", {}, clave=SEMILLERO)
        self.assertEqual(pedir("/api/admin/login", {}, clave=clave)[0], 403)
        self.assertEqual(pedir("/api/admin/login", {}, clave=nueva["clave"])[1]["rol"], "sala")
        borrar = {"confirmar": "BORRAR"}
        self.assertEqual(pedir(f"/api/admin/salas/borrar?sala={sala}", borrar, clave=SEMILLERO)[0], 400)
        pedir("/api/admin/estado", {"estado": "cerrado"}, clave=nueva["clave"])
        self.assertEqual(pedir(f"/api/admin/salas/borrar?sala={sala}", borrar, clave=SEMILLERO)[0], 200)
        self.assertEqual(pedir(f"/api/publico?sala={sala}")[0], 404)


if __name__ == "__main__":
    unittest.main()
