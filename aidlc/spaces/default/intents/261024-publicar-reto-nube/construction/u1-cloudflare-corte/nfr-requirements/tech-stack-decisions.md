# Tecnología — U1

Requisitos no funcionales de U1, el corte delgado de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial, consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano («te dejo potestad absoluta para decidir», 2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | JavaScript (módulos ES), sin TypeScript ni build | Menos piezas; mismo lenguaje que `web/js/` (`team.md`, «Code Style») |
| Plataforma | Cloudflare Workers con recursos estáticos y Durable Objects con SQLite | Plan gratuito: «Workers Free plan can only create and access SQLite-backed Durable Objects» (https://developers.cloudflare.com/durable-objects/platform/pricing/) |
| Pruebas | `node:test` y `node:assert` de Node 24, sin paquetes | Sin dependencias nuevas |
| Cobertura | `node --test --experimental-test-coverage` | Viene con Node |
| Despliegue | `npx wrangler@4.148.0 deploy`, versión exacta | Herramienta oficial; se baja al usarla y no queda como dependencia |
| Prueba común | Python 3 con la biblioteca estándar | Delivery Planning, Q6-A |
