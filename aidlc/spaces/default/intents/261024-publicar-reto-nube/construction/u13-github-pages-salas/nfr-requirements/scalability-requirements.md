# Escala — U13

Requisitos no funcionales de U13, salas y catálogo de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U13 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U13-E1 | 10 salas abiertas a la vez con hasta 40 participantes en total (prueba común de U2 con tamaños desiguales); el máximo de salas no se limita en el código, lo limita la guía (OQ8) | NFR1 |
| U13-E2 | El catálogo crece sin límite práctico: 1.000 colegios ocupan menos de 200 KB en SQLite frente a los 512 MiB del plan | NFR6 |
| U13-E3 | Las rutas del panel del semillero se usan pocas veces por reto; no cambian la estimación de ≈ 61.100 peticiones por sesión de U11 | NFR6 |
