# Rapidez — diseño U13

Diseño no funcional de U13. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- El resumen del panel es una consulta `SELECT … FROM participantes p JOIN colegios c … WHERE p.sala = ?`
  más la fila de la sala; el nombre definitivo se resuelve en SQL con `COALESCE(d.nombre, c.nombre)`
  sobre un `LEFT JOIN` a `colegios d ON d.id_colegio = c.unido_a` (U13-P1).
- Cerrar una sala: una lectura de los `en_curso`, el cálculo de `hora_de_entrega` y `bono` en Python y un
  `executemany` con los `UPDATE`, todo dentro de un `BEGIN IMMEDIATE` (U13-P2).
- Índices: `UNIQUE(nombre_normalizado)`, `sala_colegios(sala)`, `participantes(sala, estado)` (U13-P3).
- La hora de entrega se aplica una vez por petición de sala, al entrar, como en U11.
