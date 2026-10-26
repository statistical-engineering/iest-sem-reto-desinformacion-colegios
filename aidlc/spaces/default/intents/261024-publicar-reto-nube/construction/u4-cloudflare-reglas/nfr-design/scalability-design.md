# Escala — diseño U4

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

- Cada función recibe las filas de una sala ya filtradas por quien consulta (`reto.js` filtra por
  `id_sala`); ninguna regla recibe el servicio entero (U4-E1).
- Los módulos de `src/reglas/` solo exportan funciones y constantes congeladas; no hay `let` ni `Map` a
  nivel de módulo (U4-E2). La caché de exámenes sigue en `reto.js`.
- `generar_casos.py` produce los mínimos de `functional-spec.md` («Forma de la tabla de casos»): unas
  120 filas, muy por debajo de 500 KB (U4-E3). Si un día crece, se parte por regla en varios archivos
  sin cambiar el formato de cada fila.
