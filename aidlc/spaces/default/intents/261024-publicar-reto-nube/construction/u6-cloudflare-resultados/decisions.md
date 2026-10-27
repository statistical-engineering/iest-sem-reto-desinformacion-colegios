# ADR de la opción Cloudflare Workers (U6, resultados y exportación)

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** La copia, el paquete y las fechas pasan a ser
> del único reto (ADR-009 a ADR-011, contrato revisado, D7). ADR-W14 cambia las tablas del guion y agrega
> la copia de la migración; ADR-W15 y ADR-W16 no cambian; ADR-W17 cambia el ciclo de vida de las copias
> (ya no se borran con una sala: se borran una a una, D7); ADR-W18 cambia la fecha del nombre. Nuevo:
> ADR-W21, cómo se comprueba el criterio del humano del 2026-10-26, «que ya todos los paneles funcionen,
> el dash, el de admin y el de los estudiantes». **Sin paquetes nuevos:** el `.zip` se arma con código
> propio (ADR-W15).

**Estado:** aprobado por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). Continúa ADR-W1 a ADR-W13 y ADR-W19 a ADR-W20 (`../u1-cloudflare-corte/decisions.md`,
`../u4-cloudflare-reglas/decisions.md`, `../u5-cloudflare-salas/decisions.md`). Límites consultados el
2026-10-25 en https://developers.cloudflare.com/durable-objects/platform/limits/ («Maximum string, BLOB
or table row size 2 MB»; «Storage per account 5GB (Free)») y en
https://developers.cloudflare.com/workers/runtime-apis/web-standards/ (`CompressionStream` «support the
deflate, deflate-raw and gzip compression methods»).

## ADR-W14: La copia completa del reto es un guion SQL (`.sql`) que se vuelve a abrir con `sqlite3`

- **Context** — FR4.3 pide una copia completa que se pueda volver a abrir: «`reto.db` en las opciones
  con SQLite, y en las demás el formato que fije su ADR». Workers usa SQLite, pero el Durable Object no
  tiene sistema de archivos ni `VACUUM INTO`, y producir el formato binario de SQLite exige una
  biblioteca (sin paquetes nuevos, FR7.6). La copia no lleva `token`, `semilla` ni `codigo` personal (R-11,
  C-06, C5). Era la pregunta abierta de C5 en el contrato.

| | A. Guion SQL (`CREATE TABLE` + `INSERT`) de las filas del reto | B. Archivo `.db` binario escrito a mano | C. JSON con las filas del reto |
|---|---|---|---|
| Se vuelve a abrir como base | Sí: `sqlite3 copia.db < copia.sql`, o «Ejecutar SQL» en DB Browser for SQLite | Sí | No sin un programa propio |
| Paquetes nuevos | Ninguno | Habría que escribir el formato de página de SQLite: inviable | Ninguno |
| Tamaño (40 equipos, 42 preguntas) | ≈ 400 KB | ≈ 300 KB | ≈ 350 KB |
| Legible sin herramientas | Sí (texto) | No | Sí |

- **Decision** — A. Un guion `copia_<sala>_<AAAA-MM-DD_HHMM>.sql` en UTF-8 con: un comentario de
  cabecera (código de sala, evento, fecha, versión y huella del banco, versión de la app), las sentencias
  `CREATE TABLE` de `reto`, `colegios`, `participantes`, `respuestas` y `eventos` **sin las columnas
  secretas**, y los `INSERT` de todas sus filas. Los valores se escapan con comillas simples dobladas; los
  números van con punto; las horas quedan en segundos desde 1970 como en la base, y `metadatos.json`
  del paquete las da también en ISO 8601. Es el mismo archivo para «Reiniciar» y para la copia dentro del
  paquete `.zip`. **Revisión 2026-10-25:** la versión 3 del esquema guarda con la misma función las tablas
  `v1_*` que apartó la migración de U5 (ADR-W19) como `migracion_v1.sql`, sin `clave_huella`, `token`,
  `semilla` ni `codigo`, y solo si alguna tiene filas.
- **Consequences** — A favor: se abre con la herramienta que ya usa el semillero para `reto.db` y se
  lee a simple vista. En contra: no es byte a byte un `reto.db`; la guía dice el comando de un paso para
  convertirlo.
- **Alternatives Rejected** — B: imposible sin biblioteca. C: no cumple «volver a abrir».

## ADR-W15: El `.zip` se arma a mano, con entradas sin comprimir («stored») y CRC-32 propio

- **Context** — FR9.1 exige un `.zip`. No hay paquetes (FR7.6). El contenido son unos cientos de KB de
  texto.

| | A. Escribir el formato ZIP «stored» (sin compresión) con CRC-32 propio | B. ZIP con `deflate-raw` por `CompressionStream` | C. Un paquete npm de ZIP |
|---|---|---|---|
| Código propio | ≈ 90 líneas: cabecera local, directorio central, fin de directorio, tabla CRC-32 | Lo mismo más el flujo de compresión y el tamaño comprimido por entrada | 0 |
| Tamaño del paquete | ≈ 1 MB para 40 equipos | ≈ 200 KB | Según el paquete |
| Aprobación | No hace falta | No hace falta | Sí (FR7.6) |
| Riesgo | Bajo: formato fijo y probado con `unzip -t` en la prueba | Medio: hay que manejar el flujo asíncrono dentro del objeto | Dependencia externa |

- **Decision** — A. Un módulo `src/servicios/zip.js` con `armar_zip([{nombre, bytes}])` que devuelve
  `Uint8Array`; CRC-32 con tabla de 256 entradas; nombres de entrada en UTF-8 (bit 11 de la cabecera);
  fechas DOS a partir de la hora del servidor en Colombia. Se prueba en `node:test` abriendo el resultado
  con `unzip -l` y `unzip -t` cuando el binario existe, y siempre comprobando la firma y el CRC con una
  implementación de referencia en la prueba.
- **Consequences** — A favor: ninguna dependencia y un archivo que cualquier sistema abre. En contra: el
  paquete pesa unas cinco veces más de lo que pesaría comprimido; con 1 MB por reto y pocos retos al
  año no importa. Si un día hiciera falta, `deflate-raw` existe en Workers y se agrega sin cambiar la
  API.
- **Alternatives Rejected** — B: más complejidad sin necesidad. C: paquete nuevo sin motivo.

## ADR-W16: Dos formatos de CSV, cada uno igual a su referencia

- **Context** — Los dos CSV de hoy (`resultados.csv`, `respuestas.csv` de `/api/admin/*.csv`) no cambian
  de columnas ni de formato (FR4.3): `;`, BOM, decimales con coma a 4 cifras, `\r\n` (el `csv.writer`
  de Python) y `respuesta` como `json.dumps(ensure_ascii=False)` (separadores `", "` y `": "`). Los CSV
  del paquete (FR9.2) son para unir retos y años con pandas: UTF-8 con encabezado, ISO 8601, decimales
  con punto. C-13 pide fijar separador y BOM del paquete.

| | A. Hoy igual que Python; paquete con coma, sin BOM, `\n` y RFC 4180 | B. Todo con `;` y BOM | C. Todo con coma |
|---|---|---|---|
| CSV de hoy idénticos a la versión local | Sí (byte a byte, lo comprueba la prueba común) | Sí | No: cambia lo que el docente ya usa |
| Paquete fácil de unir en pandas | Sí (`read_csv` sin opciones) | Exige `sep=";"`, `decimal=","` | Sí |

- **Decision** — A. `src/servicios/csv.js` tiene dos escritores: `csv_python(filas)` (el de hoy) y
  `csv_paquete(filas)`. El de hoy formatea cada número como `f"{v:.4f}".replace(".", ",")` solo cuando
  el valor es un flotante en Python (puntos, bono, total, nota, tiempos, fracción, puntos por
  pregunta) y deja enteros tal cual (`salidas`, `variante`, `max_puntos` cuando es entero, segundos
  redondeados); `respuesta` se serializa con `json_como_python`. El del paquete escribe enteros sin
  decimales y flotantes con `String(v)` (punto, sin ceros de relleno). La columna `colegio` de los CSV de
  hoy lleva el nombre de la lista del docente.
- **Consequences** — A favor: el docente no nota el cambio de hosting en sus CSV y el semillero une
  paquetes sin opciones. En contra: dos escritores pequeños en vez de uno.
- **Alternatives Rejected** — B: incómodo para unir. C: cambia la conducta visible.

## ADR-W17: Las copias viven en la misma base, en trozos de 512 KiB, y la versión de la app la escribe `copiar.sh`

- **Context** — Una copia del reto pesa ≈ 400 KB y el límite de fila o valor en SQLite del objeto es
  2 MB. `metadatos.json` pide la versión de la app (FR9.1); el Worker no tiene acceso a git. **Revisión
  2026-10-25:** ya no hay «Borrar la sala»; «Reiniciar» conserva las copias (`components.md`, «Copias y
  "Reiniciar"») y el docente borra cada una con `POST /api/admin/copia/borrar` (D7, NFR10.1).

| | A. Tabla `copias` + `copia_trozos` de 512 KiB; `src/version.json` generado por `copiar.sh` | B. Una sola fila por copia | C. Guardar las copias en otro almacén (R2, KV) |
|---|---|---|---|
| Límite de 2 MB | Nunca se alcanza, cualquiera sea el tamaño | Un reto grande con textos largos podría pasarlo | No aplica |
| Piezas | 0 nuevas | 0 | 1 servicio más (contra la parsimonia de `project.md`) |
| Borrar una copia | Un `DELETE` de la copia y sus trozos en una transacción | Igual | Dos sistemas que coordinar (NFR10.1) |
| Versión de la app | `copiar.sh` escribe `{"commit", "fecha"}` con `git rev-parse --short HEAD`; el archivo se ignora en git y el `import` falla si no existe (el despliegue siempre corre `copiar.sh` antes) | Igual | Igual |

- **Decision** — A. Estimación de almacenamiento: 10 copias × 0,5 MB ≈ 5 MB, frente a 5 GB del plan
  gratuito; la guía de cierre (U17) pide borrar las copias después de guardar el paquete (NFR10.1).
- **Consequences** — A favor: una sola base, un borrado por copia. En contra: leer una copia concatena
  trozos; es una consulta `ORDER BY n`. Si el docente nunca borra, las copias se acumulan; con pocos retos
  al año no llegan al límite.
- **Alternatives Rejected** — B: depende del tamaño. C: una pieza más.

## ADR-W18: Fechas en la zona de Colombia y nombre del paquete con la fecha de apertura

- **Context** — FR9.1 nombra el paquete `AAAA-MM-DD_<sala>_reto.zip` y FR9.2 pide ISO 8601 con zona
  (`2026-11-03T08:15:00-05:00`). Colombia usa UTC−5 todo el año, sin horario de verano.

| | A. Desplazamiento fijo −05:00 calculado a mano | B. `Intl.DateTimeFormat` con `America/Bogota` | C. UTC |
|---|---|---|---|
| Correcto para Colombia | Sí | Sí | La fecha del nombre cambia a las 19:00 hora local |
| Depende de datos de zonas del runtime | No | Sí (Workers los trae, pero es una dependencia más) | No |

- **Decision** — A. `fecha_iso_bogota(segundos)` resta 5 horas y escribe `-05:00`. La fecha del nombre
  del paquete y de la copia es la de apertura del reto (`abierto_en`); si nunca se abrió, la del momento de
  la descarga o de la copia (revisión 2026-10-25: el reto no tiene fecha de creación). `<sala>` es el código
  de sala del reto.
- **Consequences** — Si el semillero jugara desde otra zona, la hora impresa seguiría siendo la de
  Colombia; se anota en el diccionario de datos.
- **Alternatives Rejected** — B: dependencia innecesaria. C: nombres confusos.

## ADR-W21: Cómo se comprueba que las tres pantallas funcionan completas

- **Context** — El humano fijó el 2026-10-26 como criterio de aceptación de U5 y de cierre de U6: «que ya
  todos los paneles funcionen, el dash, el de admin y el de los estudiantes». Hoy el panel de Cloudflare
  falla justo después del login porque el corte no tiene `GET /api/admin/resumen`: una llamada de la
  pantalla sin ruta rompe la pantalla entera aunque la prueba común pase.

| | A. Tres capas: una prueba automática que cruza las llamadas de `web/` con la tabla de rutas, comprobaciones por HTTP en la prueba común y un recorrido guiado de cada pantalla | B. Solo la prueba común por HTTP | C. Solo un recorrido manual |
|---|---|---|---|
| Detecta una llamada sin ruta | Sí, sin servidor, en cada `node --test` | Solo si la prueba común llama esa ruta | Solo si alguien pulsa ese botón |
| Detecta una pantalla que no se dibuja con datos reales | Sí (recorrido) | No: la prueba no ejecuta el JavaScript del navegador | Sí |
| Costo | Medio: una prueba de unas 60 líneas y una lista de comprobación | Bajo | Bajo, pero sin rastro |
| Paquetes nuevos | Ninguno | Ninguno | Ninguno |

- **Decision** — A.
  1. `pruebas/pantallas.test.js` (`node:test`, sin servidor): lee `web/static/js/*.js` y `web/tablero.html`,
     saca cada ruta literal que empieza con `/api/` y exige que esté en `RUTAS` de `reto.js` y en
     `despliegues/prueba_comun/contrato_api.yaml` (este último en cuanto U2 lo cree, porque U6 y U2 van en
     la misma tanda); falla si alguna pantalla nombra `?sala=` o `?clave=`.
  2. La prueba común (U2) llama cada ruta de la tabla «Pantallas completas» de `functional-spec.md` con
     la forma que usa la pantalla y revisa las claves JSON que la pantalla lee (comprobaciones
     `pantalla_*`, parte `base` de C3).
  3. Antes de cerrar U6, una persona recorre en `wrangler dev` la lista de vistas de cada pantalla
     (`functional-spec.md`, «Recorrido de las pantallas») y anota fecha y resultado en el resumen de Code
     Generation. La consola del navegador no puede mostrar ningún error.
- **Consequences** — A favor: una ruta que falte rompe `node --test` antes del push; lo que la prueba no
  ve lo ve el recorrido. En contra: el recorrido es manual y toma unos 20 minutos.
- **Alternatives Rejected** — B: no habría detectado el panel roto de hoy si la prueba no llamara al
  resumen. C: no deja comprobación repetible.
