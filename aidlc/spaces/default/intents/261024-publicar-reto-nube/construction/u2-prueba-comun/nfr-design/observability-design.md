# Observación — diseño U2

> **Revisión 2026-10-27 (una sola sala).** `nfr.salas` pasa a `nfr.colegios` y las partes son `base`,
> `fugas`, `relojes`, `claves` y `nfr` (D8); entran las claves agregadas `vencimiento`, `no_aplica`,
> `p95_resumen_ms` y `encabezados_csv`; la cuenta regresiva es por colegio.

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

- **Salida impresa** (U2-O1, U2-O4). `prueba.comprobar` imprime «  ✔ » o «  ✘ » con el mensaje, como en
  U1; cada paso imprime su título y, al terminar, los segundos que tardó. Durante la espera del
  vencimiento, cada 60 s imprime «faltan N s para el vencimiento del colegio A» (y de C en la nube).
  `print` solo en `prueba.py`; los módulos no imprimen. Al final, «No aplican: N» con los ids.
- **JSON de C3** (U2-O2, U2-O3). `mediciones.armar(corrida)` produce el objeto con `version_esquema: 1`,
  `opcion` (`local` o `cloudflare`), `url` (sin consulta), `inicio` y `fin` en ISO 8601 con zona horaria,
  `todo_bien`, `comprobaciones` (lista de `{id, parte, pasa, detalle}`, sin las que no aplican) y `nfr`
  con `p95_responder_ms`, `p95_tablero_ms`, `sobrevive_reinicio`, `arranque_frio_ms`, `colegios` (3 en la
  nube, 1 en local), `participantes`, `peticiones`, más las claves agregadas `duracion_min`,
  `vencimiento`, `no_aplica`, `p95_resumen_ms`, `fracciones` y `encabezados_csv`.
  `mediciones.escribir(medicion, ruta)` lo escribe con `indent=2` y `ensure_ascii=False`.
- **Muestras de los p95**. El `detalle` de `nfr_p95_responder` y `nfr_p95_tablero` dice «n = <muestras>,
  p95 = <ms> ms, p50 = <ms> ms».
- **Sin secretos** (U2-O5). `validar_medicion` rechaza secretos en `detalle` (ver `security-design.md`,
  U2-S4) antes de escribir.
- **Registro del servicio**. No se toca: Cloudflare tiene `wrangler tail` y la versión local su consola.
  La prueba no lo lee.
