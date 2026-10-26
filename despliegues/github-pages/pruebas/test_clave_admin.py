"""Clave del panel: solo por cabecera y bloqueo por navegador, no por la IP de todo el colegio.

Desde la raíz del repositorio::

    python -m unittest discover -s despliegues/github-pages/pruebas -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
os.environ.setdefault("RETO_BANCO", str(RAIZ / "2_Aplicacion_Reto" / "banco_preguntas.json"))
os.environ.setdefault("RETO_WEB", str(RAIZ / "despliegues" / "github-pages" / "web"))
sys.path.insert(0, str(RAIZ / "despliegues" / "github-pages" / "src"))

import servidor  # noqa: E402

CLAVE = "UNACLAVEDEPRUEBA"
IP_COLEGIO = "200.1.2.3"
NAV_DOCENTE = "d" * 22
NAV_ESTUDIANTE = "e" * 22


def pedir(ruta: str, *, clave: str = "", nav: str = "", ip: str = IP_COLEGIO) -> tuple[int, dict, dict]:
    """POST a la API como lo haría el navegador; devuelve código, cuerpo y cabeceras extra."""
    cabeceras = {"Content-Length": "2", "X-Clave-Admin": clave, "Cookie": f"reto_nav={nav}" if nav else ""}
    codigo, _, datos, extra = servidor.atender("POST", ruta, cabeceras.get, lambda _n: b"{}", ip)
    return codigo, json.loads(datos), extra


class ClaveAdmin(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.carpeta = tempfile.TemporaryDirectory()
        servidor.preparar(Path(cls.carpeta.name) / "reto.db", CLAVE)

    @classmethod
    def tearDownClass(cls) -> None:
        servidor.DB.close()
        cls.carpeta.cleanup()

    def setUp(self) -> None:
        for freno in (servidor.FRENO_ADMIN, servidor.FRENO_ADMIN_RED):
            freno.fallos.clear()
        servidor.NAVEGADORES_DOCENTES.clear()

    def test_la_clave_en_la_url_no_sirve(self) -> None:
        codigo, _, _ = pedir(f"/api/admin/login?clave={CLAVE}", nav=NAV_DOCENTE)
        self.assertEqual(codigo, 403)
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav=NAV_DOCENTE)[0], 200)

    def test_entrega_la_cookie_solo_si_falta(self) -> None:
        _, _, sin_cookie = pedir("/api/admin/login", clave=CLAVE)
        self.assertRegex(sin_cookie["Set-Cookie"], r"^reto_nav=[A-Za-z0-9_-]{22}; .*HttpOnly")
        self.assertNotIn("Set-Cookie", pedir("/api/admin/login", clave=CLAVE, nav=NAV_DOCENTE)[2])

    def test_un_estudiante_que_falla_no_bloquea_al_docente(self) -> None:
        for _ in range(8):
            self.assertEqual(pedir("/api/admin/login", clave="MALA", nav=NAV_ESTUDIANTE)[0], 403)
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav=NAV_ESTUDIANTE)[0], 429)
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav=NAV_DOCENTE)[0], 200)

    def test_el_freno_de_la_red_no_detiene_al_navegador_del_docente(self) -> None:
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav=NAV_DOCENTE)[0], 200)
        for i in range(40):  # alguien que cambia de navegador para seguir probando
            pedir("/api/admin/login", clave="MALA", nav=f"{i:022d}")
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav="n" * 22)[0], 429)
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav=NAV_DOCENTE)[0], 200)
        self.assertEqual(pedir("/api/admin/login", clave=CLAVE, nav="n" * 22, ip="190.9.9.9")[0], 200)


if __name__ == "__main__":
    unittest.main()
