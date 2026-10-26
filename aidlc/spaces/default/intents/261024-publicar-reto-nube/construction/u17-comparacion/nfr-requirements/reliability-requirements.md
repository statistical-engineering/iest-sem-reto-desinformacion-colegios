# Confiabilidad — U17

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U17-R1 | La fila NFR4 de cada opción medida se da por cumplida solo con `nfr.sobrevive_reinicio: true` en el JSON; `null` cuenta como «sin evidencia» y la opción no pasa | NFR4 |
| U17-R2 | La fila NFR11 se da por cumplida con la comprobación de «mismos puntos y misma clasificación que la versión local» en `pasa: true` | NFR11 |
| U17-R3 | La tabla se cierra una sola vez, con todas las opciones gratuitas terminadas o saltadas; una medición posterior que cambie un veredicto obliga a reabrir el ADR (nuevo estado «Proposed») | BR17.8, FR12.6 |
| U17-R4 | Si ninguna opción pasa todo, U17 no elige: aplica OQ2 y pregunta al humano qué se relaja | FR12.6, OQ2 |
| U17-R5 | La guía incluye volver a la versión anterior con el comando de la ganadora y la afirmación, con URL, de que los datos no se pierden al volver atrás | FR8.2, NFR4 |
