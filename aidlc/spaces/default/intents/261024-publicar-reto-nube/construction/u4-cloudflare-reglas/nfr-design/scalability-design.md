# Escala — diseño U4

> **Revisión 2026-10-27 (una sola sala).** Ya no hay `id_sala`: `reto.js` pasa a las reglas todas las filas del único reto, de todos los colegios.

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

- Cada función recibe las filas del único reto, de todos los colegios, ya armadas por quien consulta
  (`reto.js`, desde U5); con 40 participantes como máximo (NFR1), `ordenar`, `por_grado` y `calcular`
  hacen una pasada y un `sort` (U4-E1).
- Los módulos de `src/reglas/` solo exportan funciones y constantes congeladas; no hay `let` ni `Map` a
  nivel de módulo (U4-E2). La caché de exámenes sigue en `reto.js`.
- `generar_casos.py` produce los mínimos de `functional-spec.md` («Forma de la tabla de casos»): unas
  120 filas, muy por debajo de 500 KB (U4-E3). Si un día crece, se parte por regla en varios archivos
  sin cambiar el formato de cada fila.
