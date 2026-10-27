# Confiabilidad — U5

> **Revisión 2026-10-27 (una sola sala).** Una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`) y un reloj por colegio (ADR-009 a ADR-011, `../functional-design/`, D1 a D10 de
> `contract-design-questions.md`). Se quitan la clave del semillero, las claves de sala, crear o borrar
> salas y el catálogo. Los ids retirados no se reutilizan.

Requisitos no funcionales de U5, reto, colegios y relojes en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U5-R1 | Desplegar U5 sobre el objeto del corte (U1) no pierde datos: la versión 2 del esquema renombra las seis tablas del corte a `v1_*` con sus filas y crea el esquema de una sala vacío; corre una sola vez | NFR4, ADR-W10, ADR-W19 |
| U5-R2 | Cerrar el reto es atómico: o todos los `en_curso` de todos los colegios quedan entregados con la misma hora de cierre y los `registrado` en `no_inicio`, o nada cambia | FR3.1, BR2.3, ADR-004, NFR11 |
| U5-R3 | Cada acción del docente es una transacción: `config`, `estado`, `participante` y `colegios` (`agregar` es todo o nada: si un nombre no sirve no se agrega ninguno) | `phases/construction.md` («Error Handling»), BR4.2, R-10 |
| U5-R4 | Un reinicio del objeto a mitad del reto no cambia ningún tiempo ni pierde respuestas con 200: el arranque de cada colegio y el `inicio` de cada equipo son horas guardadas en SQLite (U1-R2) | NFR4, FR12.5 (fila NFR4) |
| U5-R5 | Con un solo colegio arrancado al abrir, el reto se comporta como hoy para el estudiante y el tablero, salvo el aviso de espera: la parte base de la prueba común da «TODO BIEN» | FR11.7, FR11.3 |
| U5-R6 | Una migración que falla deja al objeto sin atender (500 con registro del motivo) en vez de atender con un esquema a medias | ADR-W10, `phases/construction.md` (fallar rápido) |
| U5-R7 | El reloj de un colegio arranca una sola vez y no se deshace; el `inicio` de cada equipo es el arranque de su colegio aunque pulse «Comenzar» después | BR4.4, BR6.4, FR3.1 |
