"""Pruebas del estándar de mensajes de commit.

Uso::

    python -m unittest discover -s .github/scripts
"""

from __future__ import annotations

import unittest

from revisar_mensaje_commit import revisar_mensaje


class PruebasMensajeCommit(unittest.TestCase):
    """Casos del estándar «tipo: descripción»."""

    def test_mensaje_correcto_con_cuerpo(self) -> None:
        texto = "fix: corregir fuga del veredicto\n\n- Oculta «verdad» antes de resultados.\n"
        self.assertEqual(revisar_mensaje(texto), [])

    def test_alcance_y_comentarios_de_git(self) -> None:
        texto = "feat(servidor): agregar tabla de rutas\n# Comentario de git\n"
        self.assertEqual(revisar_mensaje(texto), [])

    def test_sin_tipo(self) -> None:
        self.assertEqual(len(revisar_mensaje("Normalizar fin de línea")), 1)

    def test_tipo_no_permitido(self) -> None:
        self.assertIn("Tipo «update» no permitido", revisar_mensaje("update: agregar algo")[0])

    def test_descripcion_sin_infinitivo(self) -> None:
        self.assertIn("infinitivo", revisar_mensaje("fix: Corrige la fuga")[0])

    def test_punto_final(self) -> None:
        self.assertEqual(revisar_mensaje("docs: actualizar la guía."), ["La primera línea no termina en punto."])

    def test_segunda_linea_no_vacia(self) -> None:
        self.assertIn("segunda línea", revisar_mensaje("chore: ordenar\ncuerpo pegado")[0])

    def test_linea_larga(self) -> None:
        self.assertIn("máximo es 72", revisar_mensaje("chore: ordenar\n\n" + "x" * 73)[0])

    def test_merge_exento(self) -> None:
        self.assertEqual(revisar_mensaje("Merge branch 'main' into develop"), [])

    def test_vacio(self) -> None:
        self.assertEqual(revisar_mensaje("# solo comentarios\n"), ["El mensaje está vacío."])


if __name__ == "__main__":
    unittest.main()
