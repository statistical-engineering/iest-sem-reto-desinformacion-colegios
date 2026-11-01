# Confiabilidad — diseño U5

> **Revisión 2026-10-27 (una sola sala).** La migración 2 aparta las tablas del corte en `v1_*`
> (ADR-W19); el cierre es del reto entero; se agrega el arranque de los relojes (U5-R7) y el 503 de
> ADR-W20.

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20); los requisitos en `../nfr-requirements/`.

- Migraciones (U5-R1, U5-R6): en el constructor, dentro de `blockConcurrencyWhile`, se lee `PRAGMA
  user_version` y se corren las versiones mayores de `MIGRACIONES`, cada una en `transactionSync` que
  termina con `PRAGMA user_version = n`. La versión 2 hace los tres pasos de ADR-W19: renombrar las seis
  tablas a `v1_*`, borrar `participante_unico` y `participantes_estado` (quedaron en `v1_participantes`)
  y crear el esquema nuevo con la fila única de `reto`. Un fallo deja `error_arranque` con el motivo, como
  U1, y todas las rutas responden 500.
- Cierre atómico (U5-R2): `cambiar_estado` a `cerrado` corre en una `transactionSync`: fija `cerrado_en`,
  cierra cada `en_curso` con `cerrar(p, ahora, "cierre")` y pasa los `registrado` a `no_inicio`; después
  escribe la línea de cambio de estado en el registro.
- Abrir y arrancar (U5-R3, U5-R7): en la misma transacción que pasa el reto a «abierto» se fija
  `arranque = ahora` en cada colegio que devuelve `colegios_al_abrir`. `arrancar` solo escribe si
  `puede_arrancar_colegio` lo permite y con `WHERE arranque IS NULL`, así dos clics no lo mueven.
- Transacciones por acción (U5-R3): `config`, `participante` y `colegios` envuelven sus escrituras en
  `transactionSync`; `agregar` valida todos los nombres con `preparar_colegios` antes de insertar.
- Reinicio (U5-R4): nada nuevo en memoria; la caché de exámenes por semilla se rehace sola.
- Sin regresión (U5-R5): la parte base de la prueba común corre contra Workers con un colegio y pasa igual
  que con la versión local.
- Objeto que no responde (ADR-W20): `worker.js` responde 503 con el mensaje del contrato cuando
  `stub.fetch` lanza un error.
