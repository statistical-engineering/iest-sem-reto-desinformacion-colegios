# Rapidez — U6

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U6-P1 | `GET /api/publico?sala=` con ranking y experimento: p95 ≤ 1,5 s con 40 participantes y 10 tableros pidiendo cada 2 s | Prueba común (U2) contra la URL | NFR3 |
| U6-P2 | `GET /api/estado` en resultados (con `revision` de 42 preguntas y sus ids opacos): p95 ≤ 1 s | Prueba común | NFR2 |
| U6-P3 | Armar el paquete de una sala de 40 personas (4 CSV + copia + zip) tarda ≤ 2 s de pared y ≤ 200 ms de CPU dentro del objeto, porque mientras se arma ninguna otra sala es atendida (ADR-W1) | `wrangler tail --format json` (`cpuTime`) en el ensayo de U2 | NFR2, límite de CPU del objeto («CPU per request 30 seconds», https://developers.cloudflare.com/durable-objects/platform/limits/) |
| U6-P4 | Reiniciar (copia + borrado) de una sala de 40 personas termina en ≤ 2 s | Prueba común, reloj del cliente | FR1.1 |
| U6-P5 | Los dos CSV de hoy se generan en una pasada por tabla, sin una consulta por participante | Revisión del código | NFR2 |
