# Tecnología — U5

> **Revisión 2026-10-27 (una sola sala).** Una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`) y un reloj por colegio (ADR-009 a ADR-011, `../functional-design/`, D1 a D10 de
> `contract-design-questions.md`). Se quitan la clave del semillero, las claves de sala, crear o borrar
> salas y el catálogo. Los ids retirados no se reutilizan.

Requisitos no funcionales de U5, reto, colegios y relojes en Cloudflare Workers. Lo de U1 y U4 sigue igual; aquí solo lo que U5 agrega. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Tema | Decisión | Por qué |
|---|---|---|
| Esquema | `PRAGMA user_version` y lista `MIGRACIONES[]` en `src/reto.js` (ADR-W10); la versión 2 renombra las tablas del corte a `v1_*` y crea `reto`, `colegios`, `participantes`, `respuestas` y `eventos` (ADR-W19) | Primer cambio de esquema sobre datos existentes; sin paquetes |
| Colegio del participante | `JOIN` con `colegios` (`nombre_de_colegio`); sin vista ni `unido_a` | ADR-W13 reemplazado por ADR-009 |
| Transacciones | `ctx.storage.transactionSync` en toda escritura de más de una sentencia, como U1 | R-10, atomicidad |
| Tamaño de `reto.js` | Se parte en `src/reto.js` (clase, rutas, acceso, migraciones) y `src/servicios/{ciclo,colegios,inscripcion,examen}.js`, funciones que reciben el objeto como primer argumento | `reto.js` ya tiene 754 líneas; cada archivo cabe en un PR de 400 (`team.md`) |
| Clave | Secreto `CLAVE_DOCENTE` (reemplaza a `CLAVE_SEMILLERO`); en local en `.dev.vars` | ADR-010, NFR9 |
| Pruebas | Las reglas siguen en `node:test` (U4). Las rutas se prueban por HTTP con la prueba común (U2) contra `wrangler dev`; no se agrega un simulador del Durable Object | Sin paquetes nuevos (Vitest con el pool de Workers se rechazó en ADR-W2) |
| Pantallas | `cambios_web.patch` se rehace con los cambios de `functional-spec.md` («Pantallas»); `copiar.sh` sigue aplicándolo | Delivery Planning Q7-A: la copia va sin cambios y los cambios aparte |
| Paquetes nuevos | Ninguno; `npx wrangler@4.148.0` como en U1 | FR7.6 |
