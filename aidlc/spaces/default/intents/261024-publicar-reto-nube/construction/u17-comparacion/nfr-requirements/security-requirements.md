# Seguridad — U17

> **Revisión 2026-10-27 (una sola sala).** U17-S3 y U17-S4 quedan con una sola clave, `CLAVE_DOCENTE` (ADR-010): ya no hay clave del semillero ni clave de sala. U17-S1 cubre también el `LEEME.md` de Cloudflare; U17-S5 nombra las rutas de comprobación.

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U17-S1 | La tabla, el ADR, la guía y el `LEEME.md` de Cloudflare no llevan claves, tokens, URL con clave, respuestas del banco ni datos de participantes; el JSON de C3 tampoco | NFR8, NFR9, BR17.11 |
| U17-S2 | La fila NFR8 de cada opción medida se da por cumplida solo con las comprobaciones de la parte `fugas` del JSON en `pasa: true` | NFR8, FR6.3 |
| U17-S3 | La fila NFR9 se da por cumplida con las comprobaciones de la parte `claves` (403 con clave ausente, incorrecta o en la URL) en `pasa: true` y la revisión del código anotada en la casilla (quién y cuándo) | NFR9 |
| U17-S4 | La guía dice que hay una sola clave, la clave docente: tiene 12 caracteres o más, se guarda con `wrangler secret put CLAVE_DOCENTE`, se entrega al docente por un canal privado y nunca va en el enlace ni en el repositorio | NFR9, ADR-010, `project.md` («Corrections», X-Clave-Admin) |
| U17-S5 | La fila NFR10 y NFR10.1 se da por cumplida solo si alguien siguió la guía de cierre una vez (paquete guardado, «Reiniciar», copias borradas) y comprobó con `/api/admin/resumen` y `/api/admin/copias` que no quedan filas ni copias (fecha y quién en la casilla) | NFR10, NFR10.1 |
| U17-S6 | La guía explica que el repositorio es público y que por eso los CSV y el paquete van al lugar privado del semillero, nunca al repositorio | FR8.2, FR9.4, NFR10 |
