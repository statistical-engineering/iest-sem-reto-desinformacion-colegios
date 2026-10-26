# Tecnología — U5

Requisitos no funcionales de U5, salas y examen completos en Cloudflare Workers. Lo de U1 y U4 sigue igual; aquí solo lo que U5 agrega. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Tema | Decisión | Por qué |
|---|---|---|
| Esquema | `PRAGMA user_version` y lista `MIGRACIONES[]` en `src/reto.js` (ADR-W10) | Primer cambio de esquema sobre datos existentes; sin paquetes |
| Vista SQL | `CREATE VIEW colegios_definitivos` (`COALESCE(unido_a, id_colegio)` y el nombre del definitivo) en la migración 2 | Un solo lugar para resolver el colegio (ADR-W13) |
| Transacciones | `ctx.storage.transactionSync` en toda escritura de más de una sentencia, como U1 | R-10, atomicidad |
| Tamaño de `reto.js` | Se parte en `src/reto.js` (clase, rutas, acceso) y `src/servicios/{salas,catalogo,inscripcion,examen}.js`, funciones que reciben el objeto (`this`) como primer argumento | `reto.js` ya tiene 754 líneas; cada archivo nuevo cabe en un PR de 400 (`team.md`); `components.md` nombra esos cuatro bloques |
| Pruebas | Las reglas siguen en `node:test` (U4). Las rutas se prueban por HTTP con la prueba común (U2) contra `wrangler dev`; no se agrega un simulador del Durable Object | Sin paquetes nuevos (Vitest con el pool de Workers se rechazó en ADR-W2) |
| Pantallas | `cambios_web.patch` crece con los cambios de `functional-spec.md` («Pantallas»); `copiar.sh` sigue aplicándolo | Delivery Planning Q7-A: la copia va sin cambios y los cambios aparte |
| Paquetes nuevos | Ninguno | FR7.6 |
