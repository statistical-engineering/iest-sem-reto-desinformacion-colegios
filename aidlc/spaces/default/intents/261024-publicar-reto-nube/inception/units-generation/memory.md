<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-25T20:55:03Z — Cada opción gratuita se parte en 4 unidades por capa (corte, reglas, salas, resultados) y las de pago quedan como unidades de solo documentación (Q1-A, Q2-A).

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-25T20:55:03Z — El humano y el asistente hacen push directo a develop, sin PR; las ramas y los PR de máximo 400 líneas son para el resto del equipo (nota del humano en Units Generation). Antes de cada push se corren a mano el simulacro y la prueba común, porque la revisión de PR (revisar-pr.yml) no corre.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
