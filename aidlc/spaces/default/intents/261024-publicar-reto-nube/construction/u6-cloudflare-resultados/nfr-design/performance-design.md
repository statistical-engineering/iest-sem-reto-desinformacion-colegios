# Rapidez — diseño U6

> **Revisión 2026-10-27 (una sola sala).** Las consultas ya no filtran por `id_sala` ni reciben `?sala=`:
> leen la única fila de `reto` y todas las filas de las tablas del reto.

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21); los requisitos en `../nfr-requirements/`.

- `publico` (sin parámetros) hace lo de U5 (reto, conteo por estado, colegios) más, solo cuando
  corresponde, una consulta de los finalizados con el nombre de su colegio para `ranking` y `por_grado`
  y, solo en `cerrado` o `resultados`, una con las respuestas del Exp. 01; `ordenar` y `calcular` son las
  de U4 (U4-P1). Sin caché: 10 tableros cada 2 s son 5 peticiones/s de microsegundos cada una (U6-P1).
- `estado` en resultados agrega `revision_publica`, que reutiliza la caché de HMAC por semilla de
  `reto.js` (los ids opacos de la revisión son los mismos del examen), y `puesto_de` sobre los
  finalizados del reto (U6-P2).
- El paquete se arma en memoria con `Uint8Array` y una sola concatenación final; los cuatro CSV salen de
  cuatro consultas (una por tabla, con `JOIN` a `colegios` para el nombre) y la copia usa las mismas
  filas ya leídas, sin volver a consultar (U6-P3, U6-P5). Corre dentro de `blockConcurrencyWhile`; con
  40 participantes son ≈ 1.700 filas de respuestas, unos 50 ms de CPU estimados.
- Reiniciar reutiliza `armar_copia` y hace cuatro `DELETE` (eventos, respuestas, participantes,
  colegios), el de `sqlite_sequence` y un `UPDATE reto` (U6-P4).
- El CRC-32 del zip usa una tabla precalculada una vez por instancia del módulo.
