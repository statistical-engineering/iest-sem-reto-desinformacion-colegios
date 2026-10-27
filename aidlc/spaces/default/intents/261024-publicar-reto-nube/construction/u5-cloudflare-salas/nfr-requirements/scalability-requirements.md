# Escala — U5

> **Revisión 2026-10-27 (una sola sala).** Una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`) y un reloj por colegio (ADR-009 a ADR-011, `../functional-design/`, D1 a D10 de
> `contract-design-questions.md`). Se quitan la clave del semillero, las claves de sala, crear o borrar
> salas y el catálogo. Los ids retirados no se reutilizan.

Requisitos no funcionales de U5, reto, colegios y relojes en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U5-E1 | Un reto con 40 equipos de 3 colegios arrancados a distinta hora, durante 90 minutos, sin que el objeto único se vuelva el cuello de botella: la cola de `blockConcurrencyWhile` no supera 1 s de espera en el p95 | NFR1, ADR-W1 |
| U5-E2 | Consumo de la sesión: U5 no agrega rutas periódicas. La estimación de U1 (≈ 60.600 peticiones) contaba 10 paneles (10 × 5.400 s / 3 s = 18.000); con un panel (1.800) baja a ≈ 44.400, ≤ 50 % de 100.000 por día («Requests 100,000 per day», https://developers.cloudflare.com/workers/platform/limits/). Es una estimación: la cifra medida la da U2 | NFR6, ADR-W20 |
| U5-E3 | Escrituras SQLite por sesión: 40 × 42 respuestas + 40 × 2 actualizaciones de puntos ≈ 3.400 filas, más cierres, eventos y colegios; ≤ 50 % de las 100.000 filas escritas por día del plan gratuito («SQLite rows written 100,000 per day», https://developers.cloudflare.com/durable-objects/platform/pricing/) | NFR6 |
| U5-E4 | La lista de colegios de un reto tiene decenas de filas; `agregar` con varios nombres usa una sentencia por nombre dentro de una transacción, así nunca pasa de 100 parámetros por sentencia («Maximum bound parameters per query 100», https://developers.cloudflare.com/durable-objects/platform/limits/) | FR10.3, BR4.2, ADR-009 |
| U5-E5 | Sin tope de colegios en el código; la guía recomienda la carga de NFR1 | ADR-W12 |
