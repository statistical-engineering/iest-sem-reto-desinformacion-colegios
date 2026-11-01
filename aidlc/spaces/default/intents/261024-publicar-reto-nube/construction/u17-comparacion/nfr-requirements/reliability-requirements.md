# Confiabilidad — U17

> **Revisión 2026-10-27 (una sola sala).** U17-R1 a U17-R5 quedan para una sola candidata construida (Cloudflare, FR12.2c), con dos corridas (ADR-C5) y sin volver atrás a la versión de varias salas.

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U17-R1 | La fila NFR4 de Cloudflare se da por cumplida solo con `nfr.sobrevive_reinicio: true` en las dos corridas (ADR-C5); `null` cuenta como «sin evidencia» y la opción no pasa | NFR4 |
| U17-R2 | La fila NFR11 se da por cumplida con `mismas_fracciones_que_local` y `mismos_csv_que_local` en `pasa: true` | NFR11 |
| U17-R3 | La tabla se cierra una sola vez, con U6 terminada y las dos mediciones de Cloudflare escritas (BR17.8); una medición posterior que cambie un veredicto obliga a reabrir el ADR (nuevo estado «Proposed») | BR17.8, FR12.6 |
| U17-R4 | Si Cloudflare no pasa todo, U17 no elige: aplica OQ2 y pregunta al humano qué se relaja | FR12.6, OQ2 |
| U17-R5 | La guía incluye volver a la versión anterior con `wrangler rollback`, la afirmación de que los datos no se pierden y la advertencia de no volver a una versión anterior a la de una sala (ADR-W19 de U5) | FR8.2, NFR4 |
