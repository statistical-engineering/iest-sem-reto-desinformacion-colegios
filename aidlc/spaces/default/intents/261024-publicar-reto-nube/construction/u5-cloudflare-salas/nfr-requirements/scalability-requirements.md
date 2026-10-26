# Escala — U5

Requisitos no funcionales de U5, salas y examen completos en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U5-E1 | 10 salas abiertas a la vez con 40 participantes en total, de tamaños desiguales (1 a 10), durante 90 minutos, sin que el objeto único se vuelva el cuello de botella: la cola de `blockConcurrencyWhile` no supera 1 s de espera en el p95 | NFR1, ADR-W1 |
| U5-E2 | Consumo de la sesión con paneles: a la estimación de U1 (≈ 60.600 peticiones) U5 no agrega rutas periódicas; el panel ya estaba contado (10 × 5.400 s / 3 s = 18.000). Sigue ≤ 50 % de 100.000 por día («Requests 100,000 per day», https://developers.cloudflare.com/workers/platform/limits/) con 10 salas | NFR6 |
| U5-E3 | Escrituras SQLite por sesión: 40 × 42 respuestas + 40 × 2 actualizaciones de puntos ≈ 3.400 filas, más cierres y eventos; ≤ 50 % de las 100.000 filas escritas por día del plan gratuito («SQLite rows written 100,000 per day», https://developers.cloudflare.com/durable-objects/platform/pricing/) | NFR6 |
| U5-E4 | El catálogo de colegios puede tener cientos de filas (años de retos) y la lista de la inscripción sigue siendo solo los elegidos de la sala | FR10.3, ADR-002 |
| U5-E5 | Sin tope de salas en el código; la guía recomienda 10 a la vez (ADR-W12) | OQ8 |
