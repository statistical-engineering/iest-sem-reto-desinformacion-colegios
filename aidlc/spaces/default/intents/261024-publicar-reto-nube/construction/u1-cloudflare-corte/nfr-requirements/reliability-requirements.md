# Confiabilidad — U1

Requisitos no funcionales de U1, el corte delgado de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial, consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano («te dejo potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U1-R1 | Toda escritura que respondió 200 queda en el almacenamiento SQLite del Durable Object, que persiste entre reinicios y despliegues | NFR4 |
| U1-R2 | El reloj se calcula con horas guardadas, no con temporizadores en memoria: un reinicio no cambia ningún tiempo | NFR4, NFR11 |
| U1-R3 | Arranque en frío ≤ 30 s | NFR5 |
| U1-R4 | Si se agota la cuota, la plataforma responde con su propio error (Error 1027); el navegador lo trata como un 5xx sin JSON (C-15) | NFR6 |
