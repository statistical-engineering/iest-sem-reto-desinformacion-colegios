# Plan de código — U6 `u6-cloudflare-resultados`

> Escrito el 2026-10-27 para una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo por
> `X-Clave-Admin`, nunca `?clave=`) y reloj por colegio (ADR-009 a ADR-011). Criterio de cierre del
> humano (2026-10-26): «que ya todos los paneles funcionen, el dash, el de admin y el de los estudiantes»
> (ADR-W21, BR10.1 a BR10.3).

## Summary

- Builds: lo que sale después del reto en Cloudflare Workers: resultados del estudiante, tablero con
  podio general y por grado con nota, los dos CSV de hoy, el paquete `.zip` armado en JS sin
  dependencias, «Reiniciar» con BORRAR y copia previa, las rutas de copias (D7), la migración 3 y la
  comprobación de que `/`, `/admin` y `/tablero` funcionan completas.
- Touches: `despliegues/cloudflare/` (`src/reto.js`, `src/servicios/*.js`, `pruebas/*.test.js`,
  `herramientas/copiar.sh`, `herramientas/verificar.sh`, `herramientas/cambios_web.patch`, `.gitignore`,
  `LEEME.md`), `despliegues/prueba_comun/src/prueba.py` (solo si U2 aún no tiene las comprobaciones de
  U6) y `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`. Nunca `2_Aplicacion_Reto/` (FR12.1).
- Tests: unas 30 pruebas `node:test` en tres archivos (`exportacion.test.js`, `resultados.test.js`,
  `pantallas.test.js`), la prueba común completa contra `wrangler dev` y contra la versión local, y el
  recorrido manual de las tres pantallas.

Fuentes: `../functional-design/` (F1 a F9, BR1.1 a BR10.3, tablas «Pantallas completas» y «Recorrido de
las pantallas»), `../nfr-design/`, `../infrastructure-design/`, `../decisions.md` (ADR-W14 a ADR-W18 y
ADR-W21) y el contrato (`contract-summary.md`, C1 y C5; `contract-design-questions.md`, D1 a D10). Este
alcance no tiene historias de usuario: cada paso se traza a FR, BR y requisitos U6-*.

**Depende de U5.** U6 no empieza hasta que U5 (B9) esté cerrada: reto de una fila, `CLAVE_DOCENTE`,
esquema versión 2 con `MIGRACIONES[]`, `GET /api/admin/resumen` completo (ADR-W11 de U5: el resumen es
de U5, aunque `unit-of-work.md` lo ponga en U6) y las filas U5 de «Pantallas completas» pasando. U6 no
reescribe nada de eso: lo usa.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "implementamos cada capa que se pueda probar, luego escribimos y corremos sus pruebas `unittest`, y tras cada cambio en el servidor o en el banco corremos `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` hasta ver «TODO BIEN».",
  "scope": "classic",
  "test_strategy": "standard",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Methodology evidence**: el humano eligió escribir las pruebas después del código (Q4-A); la única\n  prueba existente, `2_Aplicacion_Reto/pruebas/simulacro.py` (29 comprobaciones de extremo a extremo\n  por HTTP, según `code-quality-assessment.md`), se escribió sobre un servidor ya construido; no hay\n  rastro de pruebas escritas antes del código.\n- **Ordering**: implementamos cada capa que se pueda probar, luego escribimos y corremos sus pruebas\n  `unittest`, y tras cada cambio en el servidor o en el banco corremos\n  `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` hasta ver «TODO BIEN».\n- Cobertura (Q5-D, Q7-A): mantenemos el piso de 80 % de cobertura de líneas del alcance `classic` y\n  lo medimos en local con el módulo `trace` de la biblioteca estándar, sin paquetes nuevos. No hay\n  CI: las pruebas corren en local antes de abrir el pull request. La falta de CI es una excepción\n  explícita decidida por el humano; el 80 % no se baja para que una etapa pase.\n- Prueba de aceptación y marco de pruebas: ya fijados en `project.md` («Testing Posture»:\n  `simulacro.py` nunca se debilita; `unittest` sí, `pytest` no).\n- Las pruebas nuevas verifican una conducta, sin `if` ni `try` dentro, entran por la interfaz pública\n  y no usan *mocks* en la lógica pura (`.claude/rules/python-code.md`, «Pruebas»).\n- Antes de cada reto en vivo, la persona que lo dirige corre `PROBAR_ANTES_DEL_RETO` (`.bat` o\n  `.command`), que ejecuta el mismo simulacro (`2_Aplicacion_Reto/LEEME.md`, «Uso rápido»)."
    },
    {
      "layer": "project",
      "text": "- Prueba de aceptación: `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` debe terminar en «TODO BIEN»; nunca se debilita para que pase (fuente: `CLAUDE.md`, «Invariantes que no se rompen»).\n- Pruebas nuevas con `unittest` de la biblioteca estándar; `pytest` no está aprobado (fuente: `.claude/rules/python-code.md`)."
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  }
}
```

Nota: el contrato reproduce el de U1 (mismo equipo, alcance `classic`, estrategia `standard`). Las
huellas `input_sha256` y `contract_sha256` las calcula el motor al emitir la directiva de Code
Generation de U6; no se copian de U1. El marco de la opción es `node:test` (ADR-W2), no `unittest`: el
«Ordering» del equipo se aplica capa por capa con ese marco, y el simulacro sigue siendo el cierre.

## Pasos

- [ ] Paso 1. Precondición: confirmar que U5 está cerrada. `node --test despliegues/cloudflare/pruebas/reglas.test.js` pasa, `bash despliegues/cloudflare/herramientas/verificar.sh` termina con código 0 contra la versión de U5, `RUTAS` de `src/reto.js` ya tiene las 16 rutas de U5 con nivel `publico`, `token` o `clave` (sin `semillero` ni `sala`) y `GET /api/admin/resumen` responde 200 con la clave. Si algo falta, se detiene y se avisa: no se rehace U5 aquí. ADR-W11 de U5, BR10.2 (filas 1 a 14 y 22).
- [ ] Paso 2. Estructura: `herramientas/copiar.sh` escribe `src/version.json` con `{"commit": <git rev-parse --short HEAD>, "fecha": <ISO 8601 con -05:00>}`; `despliegues/cloudflare/.gitignore` agrega `src/version.json`; carpeta `src/servicios/`. BR7.1, U6-R7, ADR-W17.
- [ ] Paso 3. Runner: comprobar que `node --test` corre cada archivo nombrado (Node 24; con una carpeta falla, `project.md`, «Corrections») y anotar los comandos exactos en `unit-test-instructions.md`.
- [ ] Paso 4. Datos: migración 3 en `MIGRACIONES[]` de `src/reto.js`, en una transacción: `CREATE TABLE IF NOT EXISTS copias (id_copia, creada, nombre_archivo, bytes, sha256)` y `copia_trozos (id_copia, n, contenido BLOB, PRIMARY KEY (id_copia, n))`; si alguna tabla `v1_*` tiene filas, guardarlas con `armar_copia` (Paso 5) como `migracion_v1.sql` sin `clave_huella`, `token`, `semilla` ni `codigo`; `DROP` de las seis `v1_*`; `user_version = 3`; registro «Migración v3 aplicada.». No se crea índice por sala. BR9.1, U6-R6, ADR-W10, ADR-W14, ADR-W17.
- [ ] Paso 5. Lógica pura de formatos (sin SQL, sin `env`, importable desde Node):
  - `src/servicios/csv.js`: `csv_python(cabecera, filas)` (`;`, BOM, `\r\n`, comillas como `csv.writer`), `decimal_coma(v)` (`f"{v:.4f}"` con coma solo para flotantes), `json_como_python(valor)` (separadores `", "` y `": "`, `.0` en flotantes enteros), `csv_paquete(cabecera, filas)` (coma, sin BOM, `\n`, RFC 4180, `null` vacío) y `fecha_iso_bogota(segundos)` (−05:00 fijo). BR3.1, BR3.2, BR4.2, ADR-W16, ADR-W18.
  - `src/servicios/zip.js`: `crc32(bytes)` con tabla de 256 entradas y `armar_zip([{nombre, bytes}], ahora)` «stored», nombres UTF-8 (bit 11), fecha DOS en hora de Colombia, devuelve `Uint8Array`. BR4.1, ADR-W15, U6-R5.
  - `src/servicios/copia.js`: `armar_copia({cabecera, tablas})` (comentario de cabecera, `CREATE TABLE` sin columnas secretas ni `AUTOINCREMENT`/`REFERENCES`, `INSERT` con comillas simples dobladas, números con punto, comentario final con filas por tabla), `partir_en_trozos(texto)` (524.288 bytes UTF-8) y `unir_trozos(trozos)`. BR5.1, BR5.3, ADR-W14, U6-E2.
- [ ] Paso 6. Pruebas de formatos `despliegues/cloudflare/pruebas/exportacion.test.js` (5 a 8 por módulo, sin `if` ni `try` dentro, datos inventados en la prueba, nunca respuestas del banco): `csv_python` con `;`, comilla y salto de línea dentro de un valor, decimales `0,5000`, enteros tal cual; `json_como_python` contra salidas fijas de `json.dumps` (listas, objetos, `1.0`, tildes); `csv_paquete` con coma y comilla doblada; `armar_zip` con dos entradas: firmas, tamaños y CRC contra una segunda implementación de CRC-32 escrita en la prueba, y `unzip -t` cuando el binario existe; `armar_copia` sin `token`, `semilla`, `codigo` ni `clave_huella` en los `CREATE TABLE`; trozos de un texto de 1,2 MB con tildes que vuelven a unirse igual y ninguno pasa de 524.288 bytes; `fecha_iso_bogota` en 23:30 de Colombia que no cambia de día; una clave de prueba conocida no aparece en los bytes de un `.zip` armado con filas de prueba. U6-S4, U6-S6, U6-R5, BR4.4.
- [ ] Paso 7. Lógica pura de resultados `src/servicios/resultados.js`, sobre las calculadoras de U4 (`ordenar`, `puesto_de`, `experimento_publico`, `calcular`, `revision_publica`): `vista_resultados(reto, participante, finalizados, banco)` devuelve `{puesto, puesto_grado, nota, revision}` solo con `reto.estado === "resultados"` y el participante `finalizado`, y `{}` en otro caso; `vista_tablero(reto, finalizados, experimento)` devuelve `ranking` (top 10 con `puesto`, `puesto_grado`, `nombre`, `colegio`, `grado`, `total`, `puntos`, `nota`) y `por_grado` (`"9"`, `"10"`, `"11"`, top 10 cada uno) juntos solo en `resultados` o con modo sorpresa apagado, y `experimento` reducido a `{n, listo}` en `cerrado` y completo en `resultados`. BR1.1, BR2.1, BR2.2, FR2.5, FR6.1, FR11.4, U6-S1, U6-S2.
- [ ] Paso 8. Pruebas `despliegues/cloudflare/pruebas/resultados.test.js` (5 a 8): sin `revision` ni `puesto` en `abierto` y `cerrado`; con ellas en `resultados` y finalizado; `ranking` y `por_grado` ausentes juntos con modo sorpresa antes de `resultados`; presentes juntos con modo sorpresa apagado; `por_grado` con las tres claves y a lo sumo 10 filas; `nota` y `puesto_grado` en cada fila; experimento en `cerrado` solo con `n` y `listo` (sin `verdad`, `multitud_acierta`, `clase`, `por_publicacion`, `multitud`). U6-S1, U6-S2.
- [ ] Paso 9. Acceso a datos y rutas:
  - `src/servicios/exportacion.js` con `COLUMNAS_EXPORTABLES` por tabla (todas las consultas se arman de ahí; nunca `SELECT *`): `csv_resultados` y `csv_respuestas` con las cabeceras y el orden de `csv_resultados()` y `csv_respuestas()` de `servidor.py` (colegio por nombre, `respuesta` con ids del banco); `paquete(reto, ahora)` con los cuatro CSV de `entities.md` en el orden de C5, `copia_<código>_<fecha>.sql` y `metadatos.json` (campos de BR4.3, `version_app` de `version.json`, `huella_banco` de `banco_huella.json`), nombre `AAAA-MM-DD_<código>_reto.zip` con la fecha de `abierto_en` o de ahora; `reiniciar` en una `transactionSync` (copia, `DELETE` de eventos, respuestas, participantes y colegios, `sqlite_sequence`, reto a `inscripcion` con `abierto_en` y `cerrado_en` en `NULL`, configuración intacta); `guardar_copia`, `listar_copias` (por `creada` desc), `leer_copia` (une trozos y comprueba `sha256`; si no coincide, 500 y «copia dañada <id_copia>») y `borrar_copia` (copia y trozos en una transacción). BR3.1, BR3.2, BR4.1, BR4.3, BR4.5, BR5.1, BR5.2, BR5.3, BR6.1, BR6.2, U6-R1, U6-R3, U6-P5.
  - `src/reto.js`: las 7 rutas de U6 en `RUTAS` con nivel `clave` (`GET /api/admin/resultados.csv`, `GET /api/admin/respuestas.csv`, `GET /api/admin/paquete.zip`, `POST /api/admin/reiniciar`, `GET /api/admin/copias`, `GET /api/admin/copia`, `POST /api/admin/copia/borrar`); `confirmar !== "BORRAR"` → 400 «Escribe BORRAR para confirmar.»; id ausente → 404 «No existe esa copia.»; respuesta de archivo con `Content-Type` (`text/csv; charset=utf-8`, `application/zip`, `application/sql; charset=utf-8`), `Content-Disposition: attachment` y las cabeceras comunes (`Cache-Control: no-store`, `X-Content-Type-Options: nosniff`); `estado` y `publico` agregan lo de `resultados.js`; la entrega de lo vencido corre antes, como en toda petición; registros de U6-O1 y nada más. BR3.3, U6-S3, U6-S7, U6-S8, U6-S9, U6-O1, U6-O2.
- [ ] Paso 10. Pruebas de rutas: la prueba común (`despliegues/prueba_comun/src/prueba.py`, de U2) contra `npx wrangler@4.148.0 dev` en modo nube y contra la versión local en modo local, con las comprobaciones de U6 que lista su `functional-spec.md` («Prueba común»): `fuga_verdad_cerrado`, `fuga_revision_antes`, `resultados_por_grado`, `resultados_nota`, los dos CSV iguales byte a byte a los de la versión local con el mismo guion, `paquete_completo` (se abre con `zipfile`, seis archivos, una fila por participante, sin columnas secretas, la copia reabierta con `sqlite3` en memoria con las filas del resumen), `base_reiniciar_copia`, 403 con `?clave=` aunque la cabecera sea correcta. Si U2 aún no las tiene, se agregan en `prueba.py` con los ids de `../../u2-prueba-comun/functional-design/functional-spec.md` y se anota en `code-summary.md`. U6-R2, U6-R4, U6-S3, U6-S7, FR12.3.
- [ ] Paso 11. Pantallas: rehacer `herramientas/cambios_web.patch` sobre la copia de U5 y volver a correr `copiar.sh`. FR4.1, FR2.5, FR9.1, FR11.4, C-08.
  - `web/static/js/admin.js`: botón «⬇ Paquete del semillero (.zip)» junto a los dos CSV, descargado con `fetch` y la cabecera como los CSV; tarjeta «Copias» con la lista de `GET /api/admin/copias` y, por fila, «Descargar» (`GET /api/admin/copia?id=`, `fetch` + `Blob`) y «Borrar» (`POST /api/admin/copia/borrar`, con confirmación); tras reiniciar, «Reto reiniciado. Copia de seguridad: <id_copia>. Está en la lista de copias.»; la nota de la zona de peligro ya no habla de la «carpeta datos/».
  - `web/tablero.html`: después del podio general, una diapositiva por grado con su top y la nota de cada fila; con modo sorpresa encendido antes de `resultados` sigue «La clasificación se revela al final».
  - `web/static/js/estudiante.js`: la pantalla final muestra «Puesto en tu grado» con `puesto_grado`.
- [ ] Paso 12. Prueba de pantallas `despliegues/cloudflare/pruebas/pantallas.test.js` (`node:test`, sin servidor): lee como texto `web/static/js/*.js`, `web/tablero.html` y `src/reto.js` (no lo importa: depende de `cloudflare:workers`), saca cada literal que empieza con `/api/` y cada clave `"MÉTODO /api/..."` de `RUTAS`; falla si una pantalla llama una ruta ausente, si escribe `?sala=` o `?clave=`, o si `RUTAS` no tiene las 23 rutas del contrato C1; cuando exista `despliegues/prueba_comun/contrato_api.yaml`, también exige cada ruta ahí. BR10.1, U6-R8, ADR-W21.
- [ ] Paso 13. Comprobar las tres pantallas, por la prueba común y a mano (BR10.2, BR10.3, U6-R9, U6-O5):
  - Prueba común: las 27 comprobaciones `pantalla_*` de la tabla «Pantallas completas» (filas 1 a 22) dan bien en modo nube; las de U6 son `pantalla_estado_final` (fila 4), `pantalla_csv_resultados`, `pantalla_csv_respuestas`, `pantalla_paquete`, `pantalla_reiniciar`, `pantalla_copias`, `pantalla_copia`, `pantalla_copia_borrar` (filas 15 a 21) y `pantalla_publico_cerrado` y `pantalla_publico_resultados` (fila 22).
  - Estudiante (`/`): en `npx wrangler@4.148.0 dev`, con dos colegios y tres equipos, cada vista y acción de la fila «Estudiante» del «Recorrido de las pantallas», hasta la pantalla final con puesto, puesto en el grado, nota y revisión en «resultados».
  - Panel (`/admin`): cada vista y acción de la fila «Panel», incluidos los dos CSV, el paquete (se abre en el equipo), la tarjeta «Copias» con Descargar y Borrar y «Reiniciar» con BORRAR.
  - Tablero (`/tablero`): inscripción, en curso con el reloj de cada colegio, cerrado y resultados con podio general, una diapositiva por grado con nota, clasificación completa y las diapositivas del experimento.
  - Con la consola del navegador abierta y sin errores; cada línea se anota «sí» o «no» con fecha y persona en `code-summary.md` de U6. Una línea en «no» deja la unidad abierta.
- [ ] Paso 14. Configuración: `herramientas/verificar.sh` lee la clave de `CLAVE_DOCENTE` en `.dev.vars` (como la dejó U5), falla si falta `src/version.json` y corre, en este orden y nombrando cada archivo, `reglas.test.js`, `exportacion.test.js`, `resultados.test.js` y `pantallas.test.js`, luego la prueba común en modo nube y el simulacro local. Sin paquetes nuevos; `npx wrangler@4.148.0`. U6-R7, FR7.6.
- [ ] Paso 15. Documentación: `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md` con una tabla por archivo del paquete (columna, tipo, unidad, valores, de dónde sale), `metadatos.json` y la copia, el aviso de que `id_colegio` no se conserva entre retos y los años se unen por el nombre normalizado, y la hora de Colombia (ADR-W18); una prueba en `exportacion.test.js` compara los encabezados de `csv.js` con los nombres del diccionario. `despliegues/cloudflare/LEEME.md`: descargas, copias y «Cierre de un reto» de `../infrastructure-design/infrastructure-specification.md` en palabras simples. BR8.1, FR9.3, U6-O4.
- [ ] Paso 16. Cobertura: `node --test --experimental-test-coverage` sobre los tres archivos nuevos; ≥ 80 % de líneas en `src/servicios/csv.js`, `zip.js`, `copia.js` y `resultados.js` (piso del alcance `classic`, `team.md`, «Testing Posture»); `exportacion.js` y las rutas quedan cubiertas por la prueba común. Se anota la cifra en `code-summary.md`.
- [ ] Paso 17. Cierre: `bash despliegues/cloudflare/herramientas/verificar.sh` termina con código 0 (pruebas `node:test`, prueba común en «TODO BIEN» y simulacro); `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` termina en «TODO BIEN»; `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` sale vacío (FR12.1). `bolt-plan.md`, B11.
