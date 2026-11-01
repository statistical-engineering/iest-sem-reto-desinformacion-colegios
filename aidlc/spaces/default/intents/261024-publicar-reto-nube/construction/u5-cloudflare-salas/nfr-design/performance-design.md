# Rapidez — diseño U5

> **Revisión 2026-10-27 (una sola sala).** Sin vista `colegios_definitivos` ni filtros por sala: el
> colegio sale con un `JOIN` y la entrega de lo vencido usa el arranque de cada colegio.

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20); los requisitos en `../nfr-requirements/`.

- `responder` hace lo mismo que U1 más la traducción de ids de una sola pregunta (U4-P3); con los
  tipos nuevos no hay consultas adicionales (U5-P1).
- `resumen` arma todo con cuatro consultas: participantes con el nombre de su colegio (`JOIN`), conteo
  de respuestas por participante (`GROUP BY`), respuestas del Exp. 01 para `calcular` y la lista de
  colegios con su número de equipos; `ordenar` y `por_grado` corren una vez por petición (U5-P2).
- La entrega de lo vencido usa el índice `participantes_estado` y un `JOIN` con `colegios` para traer el
  `arranque` (U5-P3). Cerrar el reto pasa los `registrado` a `no_inicio` con un solo `UPDATE` y recorre
  solo los `en_curso`.
- La espera de 600 ms de una clave incorrecta se devuelve como `esperar_ms` y se cumple fuera de
  `blockConcurrencyWhile`, como U1 hace con `entrar`, así no detiene a nadie más (U5-P4, U5-S4).
- No se agrega caché de resumen: con 40 filas y un panel cada 3 s el costo es de microsegundos; si el
  ensayo de U2 mostrara `cpuTime` alto, la primera medida es una caché invalidada en cada escritura, sin
  cambiar la API.
