# Rapidez — U4

Requisitos no funcionales de U4, las reglas puras de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C4. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U4-P1 | `ordenar` sobre 40 finalizados de una sala y `calcular` sobre sus respuestas del Exp. 01 tardan juntos < 5 ms de CPU, porque `/api/publico` los corre cada 2 s por tablero | Prueba unitaria con 40 filas fabricadas y `performance.now()`; el umbral solo se informa, no falla la prueba | NFR3, límite de CPU del Durable Object («CPU per request 30 seconds», https://developers.cloudflare.com/durable-objects/platform/limits/) |
| U4-P2 | `armar_misiones` (todos los HMAC de un examen, unos 200 ids) tarda < 50 ms y se ejecuta una sola vez por semilla, como en U1 (caché por semilla en `reto.js`) | Prueba unitaria con el banco real; revisión de que `reto.js` conserva la caché | NFR2, U1-P4 |
| U4-P3 | `traducir_respuesta` y `respuesta_opaca` recalculan solo los HMAC de una pregunta (≤ 20 ids), no del examen entero | Revisión del código | NFR2 |
| U4-P4 | La suite completa de U4 (`node --test` de los 7 archivos) termina en < 30 s en una máquina de desarrollo | Tiempo de `verificar.sh` | NFR12 |
