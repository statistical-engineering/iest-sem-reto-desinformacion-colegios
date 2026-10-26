<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-25T22:34:49Z — «no pasa por contrato» para Apps Script se aplica saltando U7 a U10 con aprobación del humano al entrar en Construcción; el plan no borra las unidades, para que U17 las anote como «no pasa».

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-25T22:34:49Z — el comando de verificación de Construcción se deja para el punto de control de B1, porque la prueba común que lo hace real todavía no existe.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-25T22:34:49Z — orden por riesgo y no por puntaje WSJF; con una sola meta (elegir la opción que pasa todo), el riesgo de cada opción es lo que decide.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
