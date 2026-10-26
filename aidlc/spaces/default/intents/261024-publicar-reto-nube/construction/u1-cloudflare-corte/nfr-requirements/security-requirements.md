# Seguridad — U1

Requisitos no funcionales de U1, el corte delgado de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial, consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano («te dejo potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U1-S1 | Ninguna respuesta correcta, explicación, tolerancia ni veredicto sale al navegador antes de «resultados» | NFR8, BR6.2 |
| U1-S2 | Ids de opciones opacos con HMAC-SHA256 de la semilla del participante | FR6.2, BR6.1, ADR-006 |
| U1-S3 | El banco va dentro del código del Worker, nunca como archivo estático | NFR8, BR6.3 |
| U1-S4 | La clave del semillero es un secreto del hosting (`CLAVE_SEMILLERO`), de 12 caracteres o más; el servicio no arranca sin ella | NFR9 |
| U1-S5 | Claves solo por `X-Clave-Admin`, comparadas en tiempo constante y en mayúsculas; se guarda solo la huella SHA-256 del secreto de sala | NFR9, BR1.2, ADR-003 |
| U1-S6 | Ningún registro lleva claves, tokens, nombres, colegios ni respuestas | NFR9, NFR10, `.claude/rules/python-code.md` («Logs», aplicado igual a JS) |
| U1-S7 | El cuerpo de un POST se rechaza con 413 si pasa de 65.536 bytes y con 400 si no es JSON | FR4.1 (`api-documentation.md`) |
| U1-S8 | Toda respuesta lleva `Cache-Control: no-store` y `X-Content-Type-Options: nosniff` | FR4.1 |
| U1-S9 | Un error inesperado responde 500 sin detalles | FR4.1 |
