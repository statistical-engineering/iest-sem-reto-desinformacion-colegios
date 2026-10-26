"""Ids opacos (ADR-006): el navegador no ve ningún id del banco y la calificación no cambia.

Desde la raíz del repositorio::

    python -m unittest discover -s despliegues/github-pages/pruebas -v
"""

import os
import re
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

FORMA_OPACA = re.compile(r"^o[a-z2-7]{11}$")
PARTICIPANTES = ({"semilla": "a1b2c3d4", "grupo": "A"}, {"semilla": "e5f6a7b8", "grupo": "B"})


def respuesta_cualquiera(c: dict) -> Any:
    """Una respuesta válida (con ids reales) para una pregunta sin respuesta correcta: hipótesis, informe, fases."""
    if c["tipo"] == "texto":
        return "Informe de prueba"
    if c["tipo"] == "opcion":
        return c["opciones"][0]["id"]
    if c["tipo"] == "estimar":
        return (c["min"] + c["max"]) / 2
    lista = c.get("items") or c["publicaciones"]
    return {i["id"]: c["categorias"][0]["id"] for i in lista}


def ids_publicos(pub: dict) -> list[str]:
    ids = [o["id"] for campo in ("opciones", "items", "publicaciones", "partes") for o in pub.get(campo, [])]
    return ids + [o["id"] for parte in pub.get("partes", []) for o in parte["opciones"]]


class IdsOpacos(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.carpeta = tempfile.TemporaryDirectory()
        servidor.preparar(Path(cls.carpeta.name) / "reto.db", "CLAVEDEPRUEBAS")

    @classmethod
    def tearDownClass(cls) -> None:
        servidor.DB.close()
        cls.carpeta.cleanup()

    def test_el_navegador_solo_ve_ids_opacos(self) -> None:
        for p in PARTICIPANTES:
            for _, q in servidor.PREGUNTAS.values():
                if servidor.visible_para(p, q):
                    ids = ids_publicos(servidor.version_publica(p, q))
                    self.assertTrue(all(FORMA_OPACA.match(i) for i in ids), (q["id"], ids))

    def test_dos_participantes_ven_ids_distintos(self) -> None:
        _, q = servidor.PREGUNTAS["m5_azar"]
        uno, otro = (set(ids_publicos(servidor.version_publica(p, q))) for p in PARTICIPANTES)
        self.assertFalse(uno & otro)

    def test_la_respuesta_correcta_en_ids_opacos_vale_todo_el_puntaje(self) -> None:
        tipos = set()
        for p in PARTICIPANTES:
            for _, q in servidor.PREGUNTAS.values():
                if not servidor.visible_para(p, q):
                    continue
                _, c = servidor.resolver(p, q)
                real = c["respuesta"] if "respuesta" in c else respuesta_cualquiera(c)
                opaca = servidor.traducir(p, c, real, a_real=False)
                validada = servidor.validar_respuesta(c, servidor.traducir(p, c, opaca, a_real=True))
                if "respuesta" in c and q["puntos"]:
                    self.assertEqual(servidor.fraccion(c, validada), 1.0, q["id"])
                    tipos.add(c["tipo"])
        self.assertTrue({"opcion", "multiple", "clasificar", "ordenar", "construir", "numero"} <= tipos, tipos)

    def test_un_id_inventado_no_pasa_la_validacion(self) -> None:
        p = PARTICIPANTES[0]
        _, c = servidor.resolver(p, servidor.PREGUNTAS["m5_azar"][1])
        with self.assertRaises(AssertionError):
            servidor.validar_respuesta(c, servidor.traducir(p, c, "o" + "a" * 11, a_real=True))


if __name__ == "__main__":
    unittest.main()
