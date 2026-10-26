# Seguridad — diseño U3

Diseño no funcional de U3. Las decisiones están en `../decisions.md`; los requisitos en
`../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U3-S1 | `opaco_de`: `hmac.new(semilla, f"{ambito}\|{id}", sha256)` → base32 minúsculas → 11 caracteres con prefijo «o»; sin la semilla no se puede ir del opaco al id del banco ni comparar opacos de dos participantes (ADR-L1) |
| U3-S2 | La semilla se lee de la fila del participante dentro de `version_publica`, `estado_participante` y `responder`; no se agrega a ningún diccionario de salida; `test_servidor` revisa que `opacar_salida` no agregue claves |
| U3-S3 | `sin_veredicto(exp)` devuelve `{"n": exp["n"], "listo": exp["listo"]}`; `publico()` lo aplica solo en «cerrado» (ADR-L2) |
| U3-S4 | `opacar_respuesta` usa la misma tabla por tipo que `traducir_entrada` (`BR2.3`), con los mismos ámbitos de `opacar_salida`; `estado_participante` la aplica a `respuestas` y a `revision` |
| U3-S5 | `traducir_entrada` devuelve el mismo objeto cuando ningún id coincide; el 400 lo da `validar_respuesta` con el mensaje de hoy, sin decir si el id era opaco o del banco |
| U3-S6 | No se agregan `print` ni `logging`; el manejador sigue imprimiendo solo `repr(e)` en un 500 |
| U3-S7 | Las preguntas de `test_servidor.py` son inventadas (ids `x1`, `x2`, textos «Opción uno», «Opción dos») y sus claves de respuesta son de esas preguntas inventadas |
