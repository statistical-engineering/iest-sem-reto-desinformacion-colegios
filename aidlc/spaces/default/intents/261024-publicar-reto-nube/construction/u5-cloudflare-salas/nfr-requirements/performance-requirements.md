# Rapidez — U5

> **Revisión 2026-10-27 (una sola sala).** Una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`) y un reloj por colegio (ADR-009 a ADR-011, `../functional-design/`, D1 a D10 de
> `contract-design-questions.md`). Se quitan la clave del semillero, las claves de sala, crear o borrar
> salas y el catálogo. Los ids retirados no se reutilizan.

Requisitos no funcionales de U5, reto, colegios y relojes en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U5-P1 | `POST /api/responder` de cualquiera de los 10 tipos + `GET /api/estado`: p95 ≤ 1 s con 40 equipos de 3 colegios arrancados a distinta hora | Prueba común (U2) contra la URL | NFR1, NFR2 |
| U5-P2 | `GET /api/admin/resumen` con 40 equipos responde en ≤ 300 ms de ida y vuelta, porque el panel lo pide cada 3 s | Prueba común; con un panel son ≈ 0,33 peticiones/s | NFR3 (por analogía con el tablero), U1-E2 |
| U5-P3 | La entrega de lo vencido (BR6.3) recorre solo los participantes `en_curso` (índice `participantes_estado`) con el arranque de su colegio, no todas las filas; cerrar el reto con 40 equipos es una sola transacción | Revisión del código; `EXPLAIN QUERY PLAN` en una prueba manual | NFR2, NFR11 |
| U5-P4 | Cada petición del Durable Object usa menos de 10 ms de CPU en promedio: el objeto atiende de a una (ADR-W1), así que un `resumen` lento retrasa a todos los equipos | `wrangler tail` con `--format json` muestra `cpuTime` por petición; se revisa en el ensayo de U2 | Límite de CPU del Worker («CPU time per HTTP request 10 ms», https://developers.cloudflare.com/workers/platform/limits/) y del objeto («CPU per request 30 seconds», https://developers.cloudflare.com/durable-objects/platform/limits/) |
