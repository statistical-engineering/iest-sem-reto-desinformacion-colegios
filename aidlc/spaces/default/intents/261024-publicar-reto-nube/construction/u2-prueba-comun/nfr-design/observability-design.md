# Observación — diseño U2

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

- **Salida impresa** (U2-O1, U2-O4). `prueba.comprobar` imprime «  ✔ » o «  ✘ » con el mensaje, como en
  U1; cada paso imprime su título y, al terminar, los segundos que tardó. Durante la espera del
  vencimiento, cada 60 s imprime «faltan N s para el vencimiento». `print` solo en `prueba.py`; los
  módulos no imprimen.
- **JSON de C3** (U2-O2, U2-O3). `mediciones.armar(corrida)` produce el objeto con `version_esquema: 1`,
  `opcion`, `url`, `inicio` y `fin` en ISO 8601 con zona horaria, `todo_bien`, `comprobaciones` (lista de
  `{id, parte, pasa, detalle}`) y `nfr` con `p95_responder_ms`, `p95_tablero_ms`, `sobrevive_reinicio`,
  `arranque_frio_ms`, `salas`, `participantes`, `peticiones`, más las claves agregadas `duracion_min` y
  `fracciones`. `mediciones.escribir(medicion, ruta)` lo escribe con `indent=2` y `ensure_ascii=False`.
- **Muestras de los p95**. El `detalle` de `nfr_p95_responder` y `nfr_p95_tablero` dice «n = <muestras>,
  p95 = <ms> ms, p50 = <ms> ms».
- **Sin secretos** (U2-O5). `validar_medicion` rechaza secretos en `detalle` (ver `security-design.md`,
  U2-S4) antes de escribir.
- **Registro del servicio**. No se toca: cada opción tiene su propio registro (`wrangler tail` en
  Workers, la consola en local). La prueba no lo lee.
