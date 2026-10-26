# Confiabilidad — U12

Requisitos no funcionales de U12, las reglas de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U12 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U12-R1 | Mismos puntos, bono, orden y vencimientos que `servidor.py` para las mismas entradas: todos los casos de `casos_reglas.json` pasan, y la prueba común de U2 (NFR11) da la misma clasificación que la versión local | NFR11, FR5.5 |
| U12-R2 | Toda regla es determinista: la misma entrada da la misma salida, también entre reinicios (no hay estado en memoria ni aleatoriedad fuera de `rng_para(semilla)`) | NFR4, ADR-006 |
| U12-R3 | `ordenar` nunca devuelve dos puestos iguales, incluso con totales, puntos y tiempos idénticos (el `id` desempata) | NFR11 |
| U12-R4 | Una entrada mal formada devuelve un error o `None`, nunca una excepción sin capturar que llegue como 500 | `phases/construction.md` («Error Handling») |
