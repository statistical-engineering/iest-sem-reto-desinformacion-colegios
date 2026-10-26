# Confiabilidad — diseño U5

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W13); los requisitos en `../nfr-requirements/`.

- Migraciones (U5-R1, U5-R6): en el constructor, dentro de `blockConcurrencyWhile`, se corre `ESQUEMA`
  (versión 1, idempotente) y luego `MIGRACIONES` con versión mayor que `PRAGMA user_version`, cada una
  en `transactionSync` que termina con `PRAGMA user_version = n`. Un fallo deja `error_arranque` con el
  motivo, como U1, y todas las rutas responden 500.
- Cierre atómico (U5-R2): `cambiar_estado` a `cerrado` corre en una `transactionSync`: fija `cerrada`,
  cierra cada `en_curso` con `cerrar(p, ahora, "cierre")` y pasa los `registrado` a `no_inicio`; después
  registra la línea de cambio de estado.
- Transacciones por acción (U5-R3): `config`, `participante`, `catalogo`, `colegios`, `salas/clave` y
  `salas/borrar` envuelven sus escrituras en `transactionSync`; una lectura sola no la necesita.
- Reinicio (U5-R4): nada nuevo en memoria; la caché de exámenes por semilla se rehace sola.
- Una sola sala (U5-R5): la parte base de la prueba común corre contra Workers con una sala y pasa igual
  que con la versión local.
