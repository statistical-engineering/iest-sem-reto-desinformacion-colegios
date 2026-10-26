# Rapidez — U14

Requisitos no funcionales de U14, resultados y exportación de la opción GitHub Pages (API en PythonAnywhere). Salen de `requirements.md`, del diseño funcional de U14 y del ADR de U11 (`../../u11-github-pages-corte/decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U14-P1 | `GET /api/publico?sala=`: p95 ≤ 1,5 s con 10 tableros cada 2 s y 40 personas; dentro del candado, menos de 30 ms (ranking y experimento de una sala) | Prueba común (U2) y `unittest` con `perf_counter` | NFR3 |
| U14-P2 | El paquete de una sala de 40 personas se arma en menos de 2 s y pesa menos de 2 MB; no se arma dentro del candado del proceso (se lee la sala en una transacción corta y se comprime fuera) | `unittest` con 40 inscritos | NFR2, U11-P3 |
| U14-P3 | La copia de «Reiniciar» (SQLite temporal con `ATTACH`) tarda menos de 1 s para 40 personas, dentro de la transacción de reinicio | Idem | NFR2 |
| U14-P4 | El tablero no se encola detrás de descargas: una descarga de paquete no retiene el candado más de 50 ms | Revisión del código y prueba con un tablero sondeando durante una descarga | NFR3 |
