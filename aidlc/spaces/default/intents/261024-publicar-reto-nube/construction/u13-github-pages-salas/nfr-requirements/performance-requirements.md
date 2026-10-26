# Rapidez — U13

Requisitos no funcionales de U13, salas y catálogo de la opción GitHub Pages (API en PythonAnywhere). Salen de `requirements.md`, del diseño funcional de U13 y del ADR de U11 (`../../u11-github-pages-corte/decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U13-P1 | `GET /api/admin/resumen` con 40 participantes responde en menos de 50 ms dentro del candado (una consulta con `JOIN` a colegios, sin consultas por fila) | Prueba `unittest` con 40 inscritos y `perf_counter` | NFR2, U11-P3 |
| U13-P2 | Cerrar una sala con 40 personas en curso entrega a todos en una sola transacción de menos de 100 ms | Idem | NFR2, ADR-004 |
| U13-P3 | Las consultas de catálogo y de colegios de la sala usan índices (`UNIQUE` en `nombre_normalizado`, índice en `sala_colegios.sala`) | `EXPLAIN QUERY PLAN` en la revisión | NFR2 |
