# ADR de la opción Cloudflare Workers (U6, resultados y exportación)

**Estado:** aprobado por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). Continúa ADR-W1 a ADR-W13 (`../u1-cloudflare-corte/decisions.md`,
`../u4-cloudflare-reglas/decisions.md`, `../u5-cloudflare-salas/decisions.md`). Límites consultados el
2026-10-25 en https://developers.cloudflare.com/durable-objects/platform/limits/ («Maximum string, BLOB
or table row size 2 MB»; «Storage per account 5GB (Free)») y en
https://developers.cloudflare.com/workers/runtime-apis/web-standards/ (`CompressionStream` «support the
deflate, deflate-raw and gzip compression methods»).

## ADR-W14: La copia completa de una sala es un guion SQL (`.sql`) que se vuelve a abrir con `sqlite3`

- **Context** — FR4.3 pide una copia completa que se pueda volver a abrir: «`reto.db` en las opciones
  con SQLite, y en las demás el formato que fije su ADR». Workers usa SQLite, pero el Durable Object no
  tiene sistema de archivos ni `VACUUM INTO`, y producir el formato binario de SQLite exige una
  biblioteca (sin paquetes nuevos, FR7.6). La copia lleva solo las filas de la sala (R-05) y sin
  `token`, `semilla`, `codigo` personal ni `clave_huella` (R-11, C-06).

| | A. Guion SQL (`CREATE TABLE` + `INSERT`) de las filas de la sala | B. Archivo `.db` binario escrito a mano | C. JSON con las filas de la sala |
|---|---|---|---|
| Se vuelve a abrir como base | Sí: `sqlite3 copia.db < copia.sql`, o «Ejecutar SQL» en DB Browser for SQLite | Sí | No sin un programa propio |
| Paquetes nuevos | Ninguno | Habría que escribir el formato de página de SQLite: inviable | Ninguno |
| Tamaño (40 personas, 42 preguntas) | ≈ 400 KB | ≈ 300 KB | ≈ 350 KB |
| Legible sin herramientas | Sí (texto) | No | Sí |

- **Decision** — A. Un guion `copia_<sala>_<AAAA-MM-DD_HHMM>.sql` en UTF-8 con: un comentario de
  cabecera (sala, evento, fecha, huella del banco, versión de la app), las sentencias `CREATE TABLE` de
  `salas`, `colegios`, `sala_colegios`, `participantes`, `respuestas` y `eventos` **sin las columnas
  secretas**, y los `INSERT` de esa sala. Los valores se escapan con comillas simples dobladas; los
  números van con punto; las horas quedan en segundos desde 1970 como en la base, y `metadatos.json`
  del paquete las da también en ISO 8601. Es el mismo archivo para «Reiniciar» (CopiaDeSala) y para la
  copia dentro del paquete `.zip`.
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
| Tamaño del paquete | ≈ 1 MB para 40 personas | ≈ 200 KB | Según el paquete |
| Aprobación | No hace falta | No hace falta | Sí (FR7.6) |
| Riesgo | Bajo: formato fijo y probado con `unzip -t` en la prueba | Medio: hay que manejar el flujo asíncrono dentro del objeto | Dependencia externa |

- **Decision** — A. Un módulo `src/servicios/zip.js` con `armar_zip([{nombre, bytes}])` que devuelve
  `Uint8Array`; CRC-32 con tabla de 256 entradas; fechas DOS a partir de la hora del servidor. Se prueba
  en `node:test` abriendo el resultado con `unzip -l` y `unzip -t` cuando el binario existe, y siempre
  comprobando la firma y el CRC con una implementación de referencia en la prueba.
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
  decimales y flotantes con `String(v)` (punto, sin ceros de relleno).
- **Consequences** — A favor: el docente no nota el cambio de hosting en sus CSV y el semillero une
  paquetes sin opciones. En contra: dos escritores pequeños en vez de uno.
- **Alternatives Rejected** — B: incómodo para unir. C: cambia la conducta visible.

## ADR-W17: Las copias viven en la misma base, en trozos de 512 KiB, y la versión de la app la escribe `copiar.sh`

- **Context** — Una copia de sala pesa ≈ 400 KB y el límite de fila o valor en SQLite del objeto es
  2 MB. `metadatos.json` pide la versión de la app (FR9.1); el Worker no tiene acceso a git.

| | A. Tabla `copias` + `copia_trozos` de 512 KiB; `src/version.json` generado por `copiar.sh` | B. Una sola fila por copia | C. Guardar las copias en otro almacén (R2, KV) |
|---|---|---|---|
| Límite de 2 MB | Nunca se alcanza, cualquiera sea el tamaño | Una sala grande con textos largos podría pasarlo | No aplica |
| Piezas | 0 nuevas | 0 | 1 servicio más (contra la parsimonia de `project.md`) |
| Borrar la sala borra las copias | Un `DELETE` más en la misma transacción | Igual | Dos sistemas que coordinar (NFR10.1) |
| Versión de la app | `copiar.sh` escribe `{"commit", "fecha"}` con `git rev-parse --short HEAD`; el archivo se ignora en git y el `import` falla si no existe (el despliegue siempre corre `copiar.sh` antes) | Igual | Igual |

- **Decision** — A. Estimación de almacenamiento: 10 salas × 5 copias × 0,5 MB ≈ 25 MB, frente a 5 GB
  del plan gratuito; y las copias se borran con la sala al cerrar el reto (NFR10.1).
- **Consequences** — A favor: una sola base, un solo borrado. En contra: leer una copia concatena
  trozos; es una consulta `ORDER BY n`.
- **Alternatives Rejected** — B: depende del tamaño. C: una pieza más.

## ADR-W18: Fechas en la zona de Colombia y nombre del paquete con la fecha de apertura

- **Context** — FR9.1 nombra el paquete `AAAA-MM-DD_<sala>_reto.zip` y FR9.2 pide ISO 8601 con zona
  (`2026-11-03T08:15:00-05:00`). Colombia usa UTC−5 todo el año, sin horario de verano.

| | A. Desplazamiento fijo −05:00 calculado a mano | B. `Intl.DateTimeFormat` con `America/Bogota` | C. UTC |
|---|---|---|---|
| Correcto para Colombia | Sí | Sí | La fecha del nombre cambia a las 19:00 hora local |
| Depende de datos de zonas del runtime | No | Sí (Workers los trae, pero es una dependencia más) | No |

- **Decision** — A. `fecha_iso_bogota(segundos)` resta 5 horas y escribe `-05:00`. La fecha del nombre
  del paquete y de la copia es la de apertura de la sala (`abierta`); si nunca se abrió, la de creación.
- **Consequences** — Si el semillero jugara desde otra zona, la hora impresa seguiría siendo la de
  Colombia; se anota en el diccionario de datos.
- **Alternatives Rejected** — B: dependencia innecesaria. C: nombres confusos.
