# Monitoreo — U3

- La versión local no tiene monitoreo aparte, y U3 no lo agrega: la consola del docente (U3-O1) y
  `stderr` para errores (U3-O2) siguen igual.
- Salud: `GET /api/publico` responde 200, como hoy; es lo que `simulacro.py` espera al arrancar y lo que
  la prueba común revisa primero.
- Que la corrección está activa se ve con la prueba común en modo local (U3-O3): las cinco
  comprobaciones de la parte de fugas en ✔. Antes de U3 fallan; después pasan.
- Rendimiento: si un docente nota lentitud en `/api/estado`, el `timeit` de U3-P1 anotado en el PR es la
  referencia; no hay métrica en vivo porque la versión local nunca la tuvo (FR12.1).
