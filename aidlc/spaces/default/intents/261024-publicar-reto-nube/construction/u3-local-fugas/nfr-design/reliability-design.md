# Confiabilidad — diseño U3

Diseño no funcional de U3. Las decisiones están en `../decisions.md`; los requisitos en
`../nfr-requirements/`.

- **Determinismo** (U3-R1). `opaco_de` depende solo de la semilla, el ámbito y el id; no lee reloj, base
  ni estado global. Un reinicio del servidor deja los mismos ids, y una pestaña abierta antes del
  reinicio sigue respondiendo con ids válidos.
- **Sin migración** (U3-R2). No hay cambio de esquema; `conectar` sigue con sus `CREATE TABLE IF NOT
  EXISTS`. Una respuesta guardada antes de U3 ya tiene ids del banco, así que `opacar_respuesta` la
  muestra igual que una nueva.
- **Simulacro y prueba común** (U3-R3). La entrada tolerante de `traducir_entrada` (ADR-L1) es lo que
  mantiene `simulacro.py` en «TODO BIEN» sin tocarlo; la prueba común en modo local es la que demuestra
  que las fugas se cerraron.
- **Errores** (U3-R4). `traducir_entrada` y `opacar_respuesta` recorren la respuesta según su tipo con
  `isinstance`: un valor de otra forma se devuelve igual, sin `try`. Un error de programación (por
  ejemplo, una pregunta del banco sin `opciones`) sube al `except Exception` del manejador y responde
  500 con `[error]` en `stderr`, como hoy; no se agregan `except` nuevos.
- **Volver atrás** (U3-R5). Como la base no cambia, volver al commit anterior de `2_Aplicacion_Reto/` y
  reiniciar el servidor basta; una respuesta guardada con U3 se lee igual con el código anterior.
