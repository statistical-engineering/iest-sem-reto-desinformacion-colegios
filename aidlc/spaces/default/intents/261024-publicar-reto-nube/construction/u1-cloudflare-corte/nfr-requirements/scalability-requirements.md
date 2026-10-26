# Escala — U1

Requisitos no funcionales de U1, el corte delgado de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial, consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano («te dejo potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U1-E1 | Hasta 40 participantes a la vez en todas las salas | NFR1 |
| U1-E2 | Consumo de una sesión de 90 minutos ≤ 50 % de la cuota diaria. Estimación: 40 estudiantes con sondeo de `/api/estado` cada 4 s ≈ 54.000 peticiones; 10 tableros cada 2 s ≈ 27.000. Eso pasa el 50 % de 100.000 peticiones al día de Workers Free («Requests 100,000 per day», https://developers.cloudflare.com/workers/platform/limits/). Se decide en NFR Design | NFR6 |
| U1-E3 | Escrituras SQLite ≤ 50 % de 100.000 filas al día («SQLite rows written 100,000 per day», https://developers.cloudflare.com/durable-objects/platform/pricing/); una sesión escribe unas 40 × 60 respuestas ≈ 2.400 filas | NFR6 |
