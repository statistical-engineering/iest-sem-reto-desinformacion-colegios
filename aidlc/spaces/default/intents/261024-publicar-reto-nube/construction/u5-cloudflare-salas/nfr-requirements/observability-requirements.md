# Observación — U5

Requisitos no funcionales de U5, salas y examen completos en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U5-O1 | Se registran, sin datos personales ni claves: el arranque con la versión del esquema, cada migración aplicada, cada cambio de estado de sala con su código de sala, cada sala creada o borrada (código) y los errores 500 con traza | U1-O1, `.claude/rules/python-code.md` («Logs») |
| U5-O2 | No se registran inscripciones, respuestas, acciones del docente ni intentos de clave fallidos (serían 40 × 42 líneas por sesión y podrían llevar nombres) | NFR10, U1-S6 |
| U5-O3 | `GET /api/admin/salas` sirve al semillero como vista de operación: cuántas salas hay, en qué estado y con cuántos inscritos | OQ8, NFR7 |
| U5-O4 | Salud: `GET /api/publico` sin `?sala=` sigue respondiendo `{"ok": true}` aunque haya cero salas o una migración pendiente de datos | FR11.4, U1-O3 |
