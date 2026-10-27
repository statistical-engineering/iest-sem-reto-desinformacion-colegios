# Escala — U17

> **Revisión 2026-10-27 (una sola sala).** U17-E1 cambia de 10 salas a 3 colegios con relojes (NFR1 revisado); U17-E2 usa la estimación de BR17.12; U17-E4 nombra la página 1027.

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U17-E1 | La fila NFR1 se da por cumplida solo con las comprobaciones de la parte `relojes` en `pasa: true` y, en la corrida de `wrangler dev`, `nfr.colegios` = 3 y `nfr.participantes` = 40 (BR17.2); los dos números van en la casilla | NFR1 |
| U17-E2 | La fila «Consumo frente a la cuota» de Cloudflare trae la estimación de un reto real de 90 minutos (BR17.12, `EstimacionDeConsumo`) dividida por las 100.000 peticiones diarias, con la fórmula, la URL y la fecha de consulta; al lado, `nfr.peticiones` de la corrida pública; cumple si la estimación es ≤ 50 % | NFR6 |
| U17-E3 | Las columnas documentadas (Render, Cloudflare Containers) traen la estimación de sus unidades (U15-E2, U16-E2) sin recalcular | NFR6, FR12.2a |
| U17-E4 | La guía dice qué pasa si la cuota se agota a mitad del reto: página de error 1027 de Cloudflare hasta la medianoche UTC (las 19:00 en Colombia), con la frase oficial y su URL, y que el reto sigue en red local o con el túnel temporal | NFR6, BR17.12 |
