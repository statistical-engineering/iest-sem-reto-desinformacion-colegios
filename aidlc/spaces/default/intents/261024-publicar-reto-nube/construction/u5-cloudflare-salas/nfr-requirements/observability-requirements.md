# Observación — U5

> **Revisión 2026-10-27 (una sola sala).** Una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`) y un reloj por colegio (ADR-009 a ADR-011, `../functional-design/`, D1 a D10 de
> `contract-design-questions.md`). Se quitan la clave del semillero, las claves de sala, crear o borrar
> salas y el catálogo. Los ids retirados no se reutilizan.

Requisitos no funcionales de U5, reto, colegios y relojes en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U5-O1 | Se registran, sin datos personales ni claves: el arranque con la versión del esquema, cada migración aplicada, cada cambio de estado del reto, cada reloj de colegio arrancado (nombre del colegio, que no es dato personal, D10) y los errores 500 con traza | U1-O1, `.claude/rules/python-code.md` («Logs») |
| U5-O2 | No se registran inscripciones, respuestas, acciones del docente sobre participantes ni intentos de clave fallidos (serían 40 × 42 líneas por sesión y podrían llevar nombres) | NFR10, U1-S6 |
| U5-O3 | La tarjeta «Colegios» del panel (`GET /api/admin/resumen` y `GET /api/admin/colegios`) es la vista de operación: estado del reloj y número de equipos por colegio | FR11.5, BR4.5, NFR7 |
| U5-O4 | Salud: `GET /api/publico` sin parámetros es el tablero y el chequeo de salud; responde 200 aunque la lista de colegios esté vacía, y 500 si falta `CLAVE_DOCENTE` o una migración falló, para que la prueba de humo lo note | BR7.2, BR1.6, `project.md` («Corrections», ADR-011) |
