# Escala — U3

Requisitos no funcionales de U3. La versión local sigue siendo de una sola sala, un solo proceso y un
candado global (`LOCK`), y U3 no cambia eso (FR12.1). Decisiones tomadas por el asistente con la potestad
que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U3-E1 | Con 40 participantes a la vez (el máximo de hoy, NFR1 para la versión local), el costo extra de los HMAC dentro del `LOCK` se mantiene bajo: 40 estados cada 20 s × 250 HMAC ≈ 500 HMAC por segundo, menos de 1 % de un núcleo | NFR1, U3-P1 |
| U3-E2 | No se agregan tablas, columnas ni archivos: el tamaño de `reto.db` y de las copias de «Reiniciar» no cambia | ADR-006 (alternativa A: nada nuevo que guardar), FR4.3 |
| U3-E3 | La única instancia sigue siendo la regla: no hay estado nuevo en memoria que haga falta compartir | `project.md` («Deployment»: una sola instancia) |
