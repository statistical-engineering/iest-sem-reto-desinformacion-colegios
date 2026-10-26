# Rapidez — U12

Requisitos no funcionales de U12, las reglas de la opción GitHub Pages (`reglas.py` dentro de la API de PythonAnywhere). Salen de `requirements.md`, del diseño funcional de U12 y del ADR de U11 (`../../u11-github-pages-corte/decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U12-P1 | `examen_publico` para un participante (42 preguntas, HMAC por opción) tarda menos de 20 ms en esta máquina, para que el único worker siga por debajo de los 50 ms por petición de U11-P3 | Prueba `unittest` con `time.perf_counter` sobre 50 llamadas | NFR2, U11-P3 |
| U12-P2 | `ordenar` con 40 participantes tarda menos de 1 ms; `calcular` del experimento con 40 × 42 respuestas, menos de 10 ms | Idem | NFR3 |
| U12-P3 | Ninguna regla hace E/S: no abre archivos, no lee el reloj, no importa `sqlite3` | `grep` en la revisión y una prueba que importa `reglas` con `sys.modules` vigilado | FR7.1 |
