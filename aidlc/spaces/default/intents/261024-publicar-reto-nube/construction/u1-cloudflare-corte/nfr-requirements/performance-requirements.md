# Rapidez — U1

Requisitos no funcionales de U1, el corte delgado de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial, consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano («te dejo potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U1-P1 | `POST /api/responder` + `GET /api/estado`: p95 ≤ 1 s | Prueba común contra la URL (U2 lo mide con 40 participantes) | NFR2 |
| U1-P2 | `GET /api/publico?sala=`: p95 ≤ 1,5 s | Prueba común | NFR3 |
| U1-P3 | Cada petición usa menos de 10 ms de CPU en el Worker | El Worker solo enruta; la lógica corre en el Durable Object | Límite del plan gratuito: «CPU time per HTTP request 10 ms» (https://developers.cloudflare.com/workers/platform/limits/) |
| U1-P4 | El banco se lee una vez al arrancar el Durable Object, no en cada petición | Revisión del código | NFR2 |
