# Observación — diseño U3

Diseño no funcional de U3. Las decisiones están en `../decisions.md`; los requisitos en
`../nfr-requirements/`.

- **Consola igual** (U3-O1). `main()` no cambia: las mismas líneas de arranque y el mismo silencio de
  `log_message`.
- **Errores** (U3-O2). Las funciones nuevas no capturan nada; el manejador imprime `[error] <repr>` y
  responde 500 sin detalles, como hoy. `repr(e)` de un `KeyError` o `TypeError` dentro de las funciones
  nuevas no lleva la semilla ni la respuesta del participante, porque esas funciones no las ponen en
  mensajes de excepción.
- **Verificación externa** (U3-O3). El estado de la corrección se observa con la prueba común en modo
  local: `fuga_ids_opacos`, `fuga_orden_banco`, `fuga_verdad_cerrado`, `experimento_completo_resultados` y
  `csv_ids_del_banco` en ✔.
