"""Pruebas de revisar_comparacion.py con tablas pequeñas escritas aquí."""

import unittest

from revisar_comparacion import TABLA, filas_sin_fuente

TABLA_EJEMPLO = """| Criterio | Render | Otra |
|---|---|---|
| Costo en US$ | US$ 7 al mes (https://render.com/pricing) | pendiente |
| Arranque en frío | despierta en un minuto | pendiente |
| Pasos | Sin medir (FR12.2a) | 3 |
| Líneas | 120, según `wc -l` | pendiente |
"""


class TestFilasSinFuente(unittest.TestCase):
    def test_detecta_cifra_sin_url(self) -> None:
        self.assertEqual(filas_sin_fuente(TABLA_EJEMPLO, "render"), ["Arranque en frío"])

    def test_columna_sin_medir_no_falla_salvo_cifras(self) -> None:
        self.assertEqual(filas_sin_fuente(TABLA_EJEMPLO, "Otra"), ["Pasos"])

    def test_columna_inexistente_es_error(self) -> None:
        with self.assertRaises(ValueError):
            filas_sin_fuente(TABLA_EJEMPLO, "Heroku")

    def test_columna_render_real_tiene_fuentes(self) -> None:
        self.assertEqual(filas_sin_fuente(TABLA.read_text(encoding="utf-8"), "render"), [])


if __name__ == "__main__":
    unittest.main()
