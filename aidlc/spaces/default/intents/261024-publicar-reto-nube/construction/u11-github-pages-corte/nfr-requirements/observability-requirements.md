# Observación — U11

Requisitos no funcionales de U11, el corte delgado de GitHub Pages con la API en PythonAnywhere. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial consultada el 2026-10-25 (URL en `../decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U11-O1 | Se registran el arranque (huella del banco y número de preguntas), los cambios de estado de la sala, cada 503 y los errores 500 con su traza, con `logging` a `stderr` | `.claude/rules/python-code.md` («Logs») |
| U11-O2 | Los registros se leen en los archivos `error.log` y `server.log` de la pestaña Web de PythonAnywhere; no se guardan aparte ni se mandan a otro servicio | NFR6 |
| U11-O3 | Salud: `GET /api/publico` responde `{"ok": true}`; es la primera comprobación de la prueba común y de la prueba de humo | BR7.1, FR5.1 |
| U11-O4 | Las publicaciones de Pages quedan en el historial de Actions y en el entorno `github-pages` del repositorio, con la referencia publicada; sirve para saber qué versión de pantallas está en línea | ADR-G2, FR5.2 |
