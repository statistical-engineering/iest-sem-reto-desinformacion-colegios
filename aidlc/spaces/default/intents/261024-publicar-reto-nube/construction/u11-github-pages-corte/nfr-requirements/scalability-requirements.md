# Escala — U11

Requisitos no funcionales de U11, el corte delgado de GitHub Pages con la API en PythonAnywhere. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial consultada el 2026-10-25 (URL en `../decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U11-E1 | Hasta 40 participantes a la vez en todas las salas, con un solo worker | NFR1, ADR-G1 |
| U11-E2 | Peticiones de una sesión de 90 minutos (estimación de U1: ≈ 60.600 con 10 salas, tableros y paneles) sin cuota de peticiones en PythonAnywhere: los CPU-segundos «does not currently apply to your web apps» (https://help.pythonanywhere.com/pages/WhatAreCPUSeconds); el ancho de banda del plan gratuito es «Low» sin cifra (https://www.pythonanywhere.com/pricing/), así que NFR6 se cierra con el consumo medido por U2 y anotado por U17 | NFR6 |
| U11-E3 | Tráfico de Pages por sesión: 40 cargas × menos de 300 KB más 10 tableros ≈ 15 MB, frente al límite blando de «100 GB per month» (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits): menos del 1 % | NFR6 |
| U11-E4 | Disco: una sala de 40 personas con 42 preguntas ocupa menos de 1 MB en SQLite; 100 salas con sus copias caben holgadas en los «512 MiB of disk space» (https://help.pythonanywhere.com/pages/FreeAccountsFeatures/); el máximo de salas a la vez queda en 10, como en U1 (OQ8) | NFR6, NFR1 |
| U11-E5 | Publicaciones de Pages: cada corrida del flujo manual gasta alrededor de un minuto de los «2,000 minutes per month» de GitHub Free (https://docs.github.com/en/get-started/learning-about-github/githubs-plans); con menos de 20 publicaciones al mes se usa menos del 2 % | NFR6, ADR-G2 |
