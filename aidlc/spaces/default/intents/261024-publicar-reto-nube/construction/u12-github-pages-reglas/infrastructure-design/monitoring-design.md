# Monitoreo — U12

- Igual que U11 (`../../u11-github-pages-corte/infrastructure-design/monitoring-design.md`): salud por
  `GET /api/publico`, registros en la pestaña Web de PythonAnywhere.
- Lo propio de U12 se vigila antes de desplegar, no en producción: `verificar.sh` imprime la cobertura de
  `reglas.py` (U12-O2) y `unittest` nombra la fila de `casos_reglas.json` que falló (U12-O1).
- Después de desplegar, la prueba común de U2 (NFR11) confirma que los puntos y la clasificación son los
  de la versión local.
