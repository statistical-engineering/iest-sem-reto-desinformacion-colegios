# Rapidez — diseño U5

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W13); los requisitos en `../nfr-requirements/`.

- `responder` hace lo mismo que U1 más la traducción de ids de una sola pregunta (U4-P3); con los
  tipos nuevos no hay consultas adicionales (U5-P1).
- `resumen` arma todo con cuatro consultas: participantes de la sala con su colegio definitivo (vista),
  conteo de respuestas por participante (`GROUP BY`), respuestas del Exp. 01 de la sala para
  `calcular`, y nada más; `ordenar` corre una vez por petición sobre los finalizados (U5-P2).
- `vencer_tiempos` usa el índice `participantes_estado` de U1 y el `JOIN` con `salas` trae `cerrada`
  (U5-P3). Cerrar la sala actualiza con un `UPDATE ... WHERE id_sala = ? AND estado = 'registrado'` para
  `no_inicio` y un bucle solo sobre los `en_curso` de esa sala.
- La espera de 600 ms de una clave incorrecta se devuelve como `esperar_ms` y se cumple fuera de
  `blockConcurrencyWhile`, como U1 hace con `entrar`, así no detiene a nadie más (U5-P4, U5-S4).
- No se agrega caché de resumen: con 40 filas y un panel cada 3 s por sala el costo es de
  microsegundos; si el ensayo de U2 mostrara `cpuTime` alto, la primera medida es una caché por sala
  invalidada en cada escritura, sin cambiar la API.
