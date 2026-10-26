# Observación — U13

Requisitos no funcionales de U13, salas y catálogo de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U13 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U13-O1 | Se registran, además de lo de U11, cada cambio de estado de sala con su código («Sala KQMT: cerrado»), la creación y el borrado de salas y la regeneración de una clave (solo el código de sala, nunca la clave) | `.claude/rules/python-code.md` («Logs»), NFR9 |
| U13-O2 | `GET /api/admin/salas` sirve al semillero como vista de qué salas existen y en qué estado están; no hace falta panel aparte | FR11.5 |
