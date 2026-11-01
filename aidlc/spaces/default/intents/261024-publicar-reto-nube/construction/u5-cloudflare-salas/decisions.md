# ADR de la opción Cloudflare Workers (U5, reto, colegios y relojes)

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** La unidad se llamaba «salas»; ahora es «reto,
> colegios y relojes» (ADR-009 a ADR-011 de `inception/domain-design/decisions.md`, contrato revisado).
> ADR-W10 cambia el contenido de las versiones 2 y 3 del esquema; ADR-W11 se conserva con el reparto
> revisado y el criterio de «paneles completos» del humano (2026-10-26); ADR-W12 queda reducido a lo que
> sigue valiendo; ADR-W13 queda **reemplazado** (ya no hay colegios provisionales ni `unido_a`). Nuevos:
> ADR-W19 (migración desde el corte) y ADR-W20 (el 503 y la cuota).

**Estado:** aprobado por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). Continúa ADR-W1 a ADR-W5 (`../u1-cloudflare-corte/decisions.md`) y ADR-W6 a
ADR-W9 (`../u4-cloudflare-reglas/decisions.md`). Límites consultados el 2026-10-25 en
https://developers.cloudflare.com/durable-objects/platform/limits/ («Maximum SQL statement length
100 KB», «Maximum bound parameters per query 100») y el 2026-10-26 en
https://developers.cloudflare.com/workers/platform/limits/ (Free: «100,000 requests, resetting at
midnight UTC»; al pasarse, «Returns a Cloudflare `1027` error page»).

## ADR-W10: Cambios de esquema con `PRAGMA user_version` y una lista ordenada de migraciones

- **Context** — U1 crea las tablas con `CREATE TABLE IF NOT EXISTS` en el constructor del objeto y no
  escribe `user_version` (queda en 0). U5 es el primer cambio de esquema sobre un objeto que ya tiene
  datos (el corte desplegado): pasar de varias salas a una sola exige quitar columnas con clave foránea
  (`participantes.id_sala`), y `CREATE TABLE IF NOT EXISTS` no cambia una tabla que ya existe. Las
  `migrations` de `wrangler.jsonc` son de clases de objetos, no de SQL.

| | A. `PRAGMA user_version` y lista `MIGRACIONES[]` con una sentencia por versión | B. Mirar `PRAGMA table_info` y agregar lo que falte | C. Borrar y recrear las tablas |
|---|---|---|---|
| Datos existentes | Se conservan | Se conservan | Se pierden (viola NFR4) |
| Repetible | Sí: cada versión corre una vez | Sí, pero cada columna exige su propia comprobación | Sí |
| Volver atrás | Una versión anterior del código no conoce la tabla nueva | Igual | No |
| Costo | Bajo: unas 15 líneas en el arranque | Medio | Bajo |

- **Decision** — A. Al arrancar, dentro de `blockConcurrencyWhile`, se lee `PRAGMA user_version` y se
  corren en orden las versiones mayores, cada una dentro de `transactionSync`, escribiendo el número nuevo
  al final de la misma transacción. Versiones (revisión 2026-10-25):

| Versión | Unidad | Qué hace |
|---|---|---|
| 1 | U1 | El `ESQUEMA` del corte, tal cual (`IF NOT EXISTS`, no daña un objeto que ya lo tiene) |
| 2 | U5 | Una sala: aparta las tablas del corte y crea el esquema nuevo (ADR-W19) |
| 3 | U6 | Tabla `copias` y la copia de lo apartado (ADR-W14 de U6) |

  Las versiones siguientes se agregan a la lista; nunca se edita una ya publicada.
- **Consequences** — A favor: desplegar U5 sobre los datos del corte no pierde nada; una versión que
  falla deja la transacción sin aplicar. En contra: volver a la versión del corte después de migrar no
  sirve (no conoce las tablas nuevas): la vuelta atrás tras U5 es redesplegar U5, no U1 (se anota en el
  `LEEME.md`, U17).
- **Alternatives Rejected** — B: más código por cada columna y no resuelve quitar una clave foránea. C:
  pierde datos.

## ADR-W11: Reparto entre U5 y U6 — U5 entrega todo lo que el docente usa durante el reto

- **Context** — `unit-of-work.md` pone el resumen del panel en U6, pero el panel (`admin.js`) no se monta
  sin `GET /api/admin/resumen` (`refrescar()` la pide antes de dibujar nada): hoy el panel de Cloudflare
  falla justo después de entrar porque el corte no tiene esa ruta. U5 tiene que cambiar el panel para la
  clave docente, los colegios y los relojes (FR11.5). **Revisión 2026-10-26:** el humano fijó como
  criterio de aceptación «que ya todos los paneles funcionen, el dash, el de admin y el de los
  estudiantes».

| | A. U5 trae el resumen completo (con puesto, puesto en el grado, nota y experimento, que U4 ya calcula) | B. U5 trae un resumen parcial sin clasificación y U6 lo completa | C. Seguir `unit-of-work.md` al pie de la letra: resumen en U6 |
|---|---|---|---|
| Panel usable al cerrar U5 | Sí | Sí, con columnas vacías | No |
| Cambios en la misma ruta en dos unidades | No | Sí | No |
| Respeta el dueño de `components.md` (Resultados) | La ruta la implementa `reto.js`, que llama a `Clasificacion` y `Experimento` de U4; el dueño lógico no cambia | Igual | Sí |

- **Decision** — A. U5 entrega todas las rutas que usan el panel y el estudiante **durante** el reto:
  `login`, `resumen`, `estado` (del docente), `config`, `colegios` (GET y POST), `participante`, y las del
  estudiante (`colegios`, `registro`, `entrar`, `estado`, `comenzar`, `responder`, `finalizar`, `evento`),
  más `GET /api/publico` con todo lo que no es clasificación ni experimento (conteo, `colegios[]` con su
  reloj). U6 entrega lo que sale **después** o es exportación: `ranking`, `por_grado` y `experimento` en
  `/api/publico`; `revision`, `puesto`, `puesto_grado` y `nota` en `/api/estado`; los dos CSV, el paquete,
  las copias y `reiniciar`; y la comprobación final de que cada llamada de las tres pantallas tiene ruta y
  prueba (criterio del 2026-10-26, U6 «Pantallas completas»). Se anota como desviación de
  `unit-of-work.md` con este motivo.
- **Consequences** — A favor: al cerrar U5, el panel y la pantalla del estudiante funcionan de punta a
  punta para un reto completo (abrir, arrancar colegios, cerrar, publicar). En contra: U6 toca
  `/api/publico` y `/api/estado`, que U5 ya tiene; son agregados de claves, seguros por contrato (C1,
  «Agregar es seguro»). Mientras falte U6, los botones de descarga y «Reiniciar» responden 404.
- **Alternatives Rejected** — B: dos cambios a la misma ruta. C: pantallas inutilizables una tanda entera.

## ADR-W12: Intentos de clave y cierre del reto

- **Context** — OQ6 preguntaba si hace falta un límite de intentos fallidos de clave; ADR-010 lo cerró:
  «sin límite de intentos». OQ8 preguntaba si el reto se cierra solo; con una sala, la pregunta de cuántas
  salas a la vez desaparece (revisión 2026-10-25).

| Tema | A. Elegida | B. Rechazada | Por qué |
|---|---|---|---|
| Intentos de clave | Sin bloqueo; la espera de 600 ms que U1 aplica a códigos que no existen se aplica también a una clave incorrecta, fuera del bloqueo del objeto | Bloquear la clave tras n intentos | La clave docente tiene 12 caracteres o más (ADR-010); un bloqueo dejaría al docente fuera de su panel por un ataque trivial a mitad del reto |
| Cierre automático | El reto no se cierra solo: cada colegio vence solo (ADR-004, ADR-011) y el docente cierra cuando quiere, como hoy | Pasar el reto a «cerrado» cuando venza el último colegio | Hoy el reto sigue «abierto» hasta que el docente lo cierra; cambiarlo altera el flujo de estados (`project.md`, «Forbidden»), y un colegio puede arrancar tarde |
| Colegios a la vez | Sin tope en el código; la guía recomienda lo de NFR1 (40 equipos de 3 colegios) | Un tope en `agregar` | Un tope rechaza un reto real por una estimación |

- **Decision** — Las tres de la columna A.
- **Consequences** — U2 mide el consumo con la carga de NFR1 y U17 lo anota.

## ADR-W13: El colegio se muestra siempre por su nombre definitivo, resuelto al leer

**Estado:** reemplazado el 2026-10-25 por ADR-009. Sin catálogo ni colegios provisionales no hay
`unido_a`: cada participante guarda el `id_colegio` de la lista del docente y el nombre sale de la tabla
`colegios` con un `JOIN` (`nombre_de_colegio`). Se conserva el texto anterior solo como historia en el
control de versiones.

## ADR-W19: Migración desde el corte: apartar lo de varias salas y empezar el reto limpio

- **Context** — El corte desplegado (U1) guarda `salas`, `sala_colegios`, colegios provisionales y
  participantes con `id_sala`. Solo tiene datos de las corridas de la prueba común mínima: ningún reto real
  se hizo en Workers. El esquema nuevo (`components.md`, `contract-summary.md`, «Qué cambia respecto al
  corte») no tiene dónde poner varias salas, y juntar sus participantes en un solo reto puede chocar con el
  índice único (nombre, colegio y grado) y mezclar estados distintos.

| | A. Apartar: renombrar las tablas del corte a `v1_*`, crear el esquema nuevo vacío y que U6 guarde lo apartado como una copia | B. Fusionar: pasar la sala más reciente a `reto` y todos sus participantes y colegios a las tablas nuevas | C. Borrar las tablas del corte |
|---|---|---|---|
| Pierde datos (NFR4) | No: quedan en `v1_*` y luego en una copia descargable | No, salvo choques del índice único | Sí |
| Datos de prueba en el reto nuevo | No: el docente empieza con lista y reto vacíos | Sí: colegios y equipos de prueba aparecen en el panel | No |
| Riesgo al migrar | Bajo: `ALTER TABLE … RENAME` mueve también las claves foráneas | Alto: reglas de fusión para casos que no existen en el aula | Nulo |
| Costo | Bajo | Medio | Muy bajo |

- **Decision** — A. La versión 2, en una sola transacción:
  1. `ALTER TABLE` renombra `salas`, `sala_colegios`, `colegios`, `participantes`, `respuestas` y
     `eventos` a `v1_salas`, `v1_sala_colegios`, `v1_colegios`, `v1_participantes`, `v1_respuestas` y
     `v1_eventos` (SQLite actualiza las referencias entre ellas).
  2. `DROP INDEX participante_unico` y `participantes_estado`, que quedaron en `v1_participantes` y cuyos
     nombres usa el esquema nuevo.
  3. Crea el esquema nuevo de `functional-design/entities.md` (Reto, Colegio, Participante, Respuesta,
     Evento) y la fila única de `reto` con los valores por defecto (estado «inscripción», código de 4
     letras al azar del `ALFABETO`, evento «Reto», duración del banco, retro y modo sorpresa encendidos).
  La versión 3 (U6) guarda las tablas `v1_*` como una copia `migracion_v1.sql` si tienen alguna fila, y
  las borra. Un objeto nuevo pasa por las versiones 1, 2 y 3 seguidas, sin copia porque `v1_*` está vacío.
  Antes de desplegar U5 se prueba la migración con `wrangler dev` sobre un objeto local que tenga datos
  del corte (comprobación de U5 en `functional-spec.md`).
- **Consequences** — A favor: nada se pierde y el docente no ve restos de las pruebas. En contra: entre
  el despliegue de U5 y el de U6 las tablas `v1_*` ocupan lugar en el objeto (pocos kilobytes) y no se
  pueden descargar; nadie las necesita en ese tiempo.
- **Alternatives Rejected** — B: reglas de fusión sin caso real y con datos de prueba a la vista. C:
  viola NFR4.

## ADR-W20: El 503 y el límite diario de peticiones

- **Context** — El contrato (Q4-A, pregunta abierta de U5) pide 503 `{"error": "El servicio no responde.
  Intenta de nuevo en un momento."}` si el Durable Object no responde o la plataforma está sin cuota. En
  el plan gratuito, al pasar las 100.000 peticiones del día, Cloudflare «Returns a Cloudflare `1027` error
  page» y el Worker no corre (https://developers.cloudflare.com/workers/platform/limits/, consultado el
  2026-10-26).

| | A. 503 del Worker cuando falla el objeto; la cuota diaria la vigila la prueba común | B. Contar peticiones en el objeto y responder 503 antes de llegar al límite | C. Pasar a un plan de pago |
|---|---|---|---|
| Cubre el objeto caído o sobrecargado | Sí (`worker.js` ya captura el error de `stub.fetch`) | Sí | Sí |
| Cubre la cuota diaria | No: la página 1027 la da Cloudflare antes del Worker | Solo en parte: el conteo propio no es el de Cloudflare y cada conteo es otra escritura | Sí |
| Costo | Ninguno | Escrituras extra en cada petición | Viola NFR6 |

- **Decision** — A. `worker.js` responde el 503 del contrato cuando `stub.fetch` lanza un error
  (objeto que no responde, reiniciado o sobrecargado) y el error queda en el registro sin datos de la
  petición. La cuota diaria no se detecta en el código: NFR6 exige que un reto use menos del 50 % de la
  cuota, U2 cuenta las peticiones de su carga (`peticiones` del JSON de C3) y U17 lo compara con las
  100.000 del día. La guía de U17 dice qué hacer si aparece la página 1027 (esperar a la medianoche UTC,
  las 19:00 de Colombia; nada se pierde). El navegador no reintenta un POST por su cuenta.
- **Consequences** — A favor: ningún código extra. En contra: con la cuota agotada el estudiante ve una
  página de Cloudflare en inglés y no el mensaje del reto; con la carga de NFR1 no se llega a ese punto.
- **Alternatives Rejected** — B: más escrituras por petición y un conteo que no coincide con el de
  Cloudflare. C: viola NFR6.
