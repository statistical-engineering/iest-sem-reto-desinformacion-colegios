# Escala — U12

Requisitos no funcionales de U12, las reglas de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U12 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U12-E1 | Las reglas trabajan sobre las filas de una sola sala (≤ 40 personas por el tope de NFR1); no hay estructuras globales ni memoria compartida entre llamadas, salvo la caché por semilla del examen que vive en `servicio.py` (U11-P4) | NFR1, FR11.2 |
| U12-E2 | `reglas.py` no suma consumo de cuota: corre dentro de la misma petición del único worker (U11-E2) | NFR6 |
