# Escala — U17

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U17-E1 | La fila NFR1 se da por cumplida solo con las comprobaciones de la parte `salas` del JSON (10 salas de tamaños desiguales, 40 participantes) en `pasa: true`; `nfr.salas` y `nfr.participantes` van en la casilla | NFR1 |
| U17-E2 | La fila «Consumo frente a la cuota» de cada opción medida sale de `nfr.peticiones` dividido por la cuota diaria o mensual que cite su ADR con URL; cumple si es ≤ 50 % | NFR6 |
| U17-E3 | Las columnas documentadas (Render, Cloudflare Containers) traen la estimación de sus unidades (U15-E2, U16-E2) sin recalcular | NFR6, FR12.2a |
| U17-E4 | La guía dice qué pasa si la cuota se agota a mitad del reto en la ganadora, con la frase oficial y su URL | NFR6 |
