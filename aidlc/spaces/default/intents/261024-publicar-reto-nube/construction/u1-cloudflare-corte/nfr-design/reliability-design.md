# Confiabilidad — diseño U1

Diseño no funcional de U1. Las decisiones están en `../decisions.md` (ADR-W1 a ADR-W5); los requisitos en `../nfr-requirements/`.

- Todo dato vive en el SQLite del Durable Object (ADR-W1), que persiste entre reinicios y despliegues (U1-R1).
- Los tiempos se guardan como horas en segundos desde 1970 y la entrega por tiempo se calcula en cada petición (U1-R2), igual que `vencer_tiempos()` de hoy.
- Un Worker no se «duerme» como Render: el arranque en frío es de milisegundos (U1-R3).
