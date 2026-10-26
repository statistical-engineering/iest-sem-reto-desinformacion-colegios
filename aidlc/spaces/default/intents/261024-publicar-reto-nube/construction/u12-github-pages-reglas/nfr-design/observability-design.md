# Observación — diseño U12

Diseño no funcional de U12. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- `test_reglas.py` usa `subTest(regla=..., funcion=..., indice=...)`: el fallo nombra la fila sin
  imprimir su `salida_esperada` (U12-O1).
- `herramientas/verificar.sh` corre `trace` y resume «reglas.py: <n> % de líneas» leyendo el `.cover`
  generado; falla si baja de 80 (U12-O2).
