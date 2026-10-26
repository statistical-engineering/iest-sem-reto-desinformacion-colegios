<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-25T21:20:48Z — la nube no acepta ?clave= en la URL, solo X-Clave-Admin; ADR-005 y FR9.5 ya piden solo la cabecera, y la URL con clave quedaría en los registros del hosting.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-25T21:20:48Z — /api/publico sin ?sala= responde solo {"ok": true} en la nube; hoy trae todo el tablero. Sirve de chequeo de salud sin mostrar una sala, y tablero.html pasa a leer sala de su URL.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-25T21:20:48Z — la tabla casos_reglas.json se comparte como datos entre opciones, no como código; así se cumple FR12.2 (sin código compartido) y las tres opciones prueban las mismas reglas.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
- 2026-10-25T21:20:48Z — orden de los push a casos_reglas.json si U4, U8 y U12 corren en paralelo; lo fija Delivery Planning.
