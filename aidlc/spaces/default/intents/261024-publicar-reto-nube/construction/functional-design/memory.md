<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->
- 2026-10-25T22:42:48Z — [unit u1-cloudflare-corte] la prueba común mínima vive en despliegues/prueba_comun/src/ y no en prueba_comun/prueba.py, porque el LEEME de esa carpeta ya fija src/ y pruebas/.

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->
- 2026-10-25T22:42:48Z — [unit u1-cloudflare-corte] contra la versión local, la salud solo exige 200 y el colegio va como texto, porque la versión local no tiene /api/colegios ni responde {"ok": true}.

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->
- 2026-10-25T22:42:48Z — [unit u1-cloudflare-corte] el corte califica solo opcion y rechaza otros tipos con 400; mantiene el corte pequeño y U4 trae los otros 9 tipos con sus pruebas.

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
