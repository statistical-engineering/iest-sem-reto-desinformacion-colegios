# Rapidez — diseño U4

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

- `ordenar` hace una sola pasada para armar las claves y un `sort` con comparador de cinco niveles; con
  40 filas son unas 200 comparaciones (U4-P1).
- `calcular` recorre las filas una vez para agrupar por participante y después solo los «completos»;
  nada cuadrático (U4-P1).
- `armar_misiones` sigue haciendo todos los HMAC de un examen con `Promise.all` por pregunta y queda en
  la caché por semilla de `reto.js` (U4-P2). `traducir_respuesta` y `respuesta_opaca` llaman a
  `opacos_de` solo con los ids de esa pregunta o de esa parte (U4-P3).
- `a_numero` y `normalizar_texto` usan expresiones regulares lineales sobre cadenas ya acotadas
  (U4-S4), así que su costo es despreciable.
- La suite carga `banco.json`, `banco_prueba.json` y `casos_reglas.json` una vez por archivo de prueba
  (U4-P4).
