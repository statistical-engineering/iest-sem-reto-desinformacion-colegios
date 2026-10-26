# Rapidez — U5

Requisitos no funcionales de U5, salas y examen completos en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U5-P1 | `POST /api/responder` de cualquiera de los 10 tipos + `GET /api/estado`: p95 ≤ 1 s con 40 participantes repartidos en 10 salas | Prueba común (U2) contra la URL | NFR2 |
| U5-P2 | `GET /api/admin/resumen` de una sala de 40 personas responde en ≤ 300 ms de ida y vuelta, porque el panel lo pide cada 3 s y cada sala tiene su panel | Prueba común; con 10 paneles son ≈ 3,3 peticiones/s en total | NFR3 (por analogía con el tablero), U1-E2 |
| U5-P3 | `vencer_tiempos` recorre solo los participantes `en_curso` (índice de U1) y no todas las filas del servicio; cerrar una sala de 40 personas es una sola transacción | Revisión del código; `EXPLAIN QUERY PLAN` en una prueba manual | NFR2, NFR11 |
| U5-P4 | Cada petición del Durable Object usa menos de 10 ms de CPU en promedio: el objeto atiende de a una (ADR-W1), así que un `resumen` lento retrasa a todas las salas | `wrangler tail` con `--format json` muestra `cpuTime` por petición; se revisa en el ensayo de U2 | Límite de CPU del Worker («CPU time per HTTP request 10 ms», https://developers.cloudflare.com/workers/platform/limits/) y del objeto («CPU per request 30 seconds», https://developers.cloudflare.com/durable-objects/platform/limits/) |
