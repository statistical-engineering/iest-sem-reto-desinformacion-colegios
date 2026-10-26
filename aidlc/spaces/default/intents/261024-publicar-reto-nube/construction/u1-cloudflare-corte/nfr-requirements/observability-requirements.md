# Observación — U1

Requisitos no funcionales de U1, el corte delgado de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial, consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano («te dejo potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U1-O1 | Se registran el arranque, los cambios de estado de la sala y los errores 500 con su traza | `.claude/rules/python-code.md` («Logs») |
| U1-O2 | Los registros se ven con `wrangler tail` o en el panel de Cloudflare; no se guardan aparte | NFR6 |
| U1-O3 | Salud: `GET /api/publico` responde `{"ok": true}` | BR7.1, FR5.1 |
