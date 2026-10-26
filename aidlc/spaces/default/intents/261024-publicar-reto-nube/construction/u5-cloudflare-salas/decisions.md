# ADR de la opción Cloudflare Workers (U5, salas)

**Estado:** aprobado por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). Continúa ADR-W1 a ADR-W5 (`../u1-cloudflare-corte/decisions.md`) y ADR-W6 a
ADR-W9 (`../u4-cloudflare-reglas/decisions.md`). Límites consultados el 2026-10-25 en
https://developers.cloudflare.com/durable-objects/platform/limits/ («Maximum SQL statement length
100 KB», «Maximum bound parameters per query 100»).

## ADR-W10: Cambios de esquema con `PRAGMA user_version` y una lista ordenada de migraciones

- **Context** — U1 crea las tablas con `CREATE TABLE IF NOT EXISTS` en el constructor del objeto. U5 es
  el primer cambio de esquema sobre un objeto que ya puede tener datos (el corte desplegado):
  `colegios.unido_a` (ADR-002) y `salas.version_esquema` no existen. `CREATE TABLE IF NOT EXISTS` no agrega
  columnas a una tabla que ya existe, y las `migrations` de `wrangler.jsonc` son de clases de objetos,
  no de SQL.

| | A. `PRAGMA user_version` y lista `MIGRACIONES[]` con una sentencia por versión | B. Mirar `PRAGMA table_info` y agregar lo que falte | C. Borrar y recrear las tablas |
|---|---|---|---|
| Datos existentes | Se conservan | Se conservan | Se pierden (viola NFR4) |
| Repetible | Sí: cada versión corre una vez | Sí, pero cada columna exige su propia comprobación | Sí |
| Volver atrás | Una versión anterior del código no conoce la columna y la ignora | Igual | No |
| Costo | Bajo: 10 líneas en el arranque | Medio | Bajo |

- **Decision** — A. `ESQUEMA` de U1 queda como versión 1; `MIGRACIONES = [{version: 2, sql: [...]}, ...]`.
  Al arrancar, dentro de `blockConcurrencyWhile`, se leen `PRAGMA user_version`, se corren en orden las
  versiones mayores dentro de `transactionSync` y se escribe el número nuevo. Versión 2 (U5):
  `ALTER TABLE colegios ADD COLUMN unido_a TEXT REFERENCES colegios (id_colegio)`. Las versiones
  siguientes (U6: tabla `copias`) se agregan a la lista, nunca se editan las anteriores.
- **Consequences** — A favor: desplegar U5 sobre los datos del corte no pierde nada; `rollback` sigue
  funcionando. En contra: una columna nueva es nullable siempre (ALTER TABLE de SQLite); por eso
  `unido_a` es opcional por diseño.
- **Alternatives Rejected** — B: más código por cada columna. C: pierde datos.

## ADR-W11: Reparto entre U5 y U6 — U5 entrega todo lo que el docente usa durante el reto

- **Context** — `unit-of-work.md` pone `GET /api/admin/resumen` en U6 («resumen del panel»), pero el
  panel (`admin.js`) no se monta sin esa ruta (`refrescar()` la pide antes de dibujar nada), y U5 tiene
  que cambiar el panel para salas, claves y catálogo (FR11.5). Dejar el resumen en U6 obligaría a
  construir pantallas que no se pueden abrir hasta la unidad siguiente.

| | A. U5 trae el resumen completo (con puesto, nota y experimento, que U4 ya calcula) | B. U5 trae un resumen parcial sin clasificación y U6 lo completa | C. Seguir `unit-of-work.md` al pie de la letra: resumen en U6 |
|---|---|---|---|
| Panel usable al cerrar U5 | Sí | Sí, con columnas vacías | No |
| Cambios en la misma ruta en dos unidades | No | Sí | No |
| Respeta el dueño de `components.md` (Resultados) | La ruta la implementa `reto.js`, que llama a `Clasificacion` y `Experimento` de U4; el dueño lógico no cambia | Igual | Sí |

- **Decision** — A. U5 entrega las rutas que el docente usa **durante** el reto: `login`, `resumen`,
  `estado`, `config`, `participante`, `salas*`, `catalogo`, `colegios`. U6 entrega lo que sale
  **después**: `revision`, `puesto` y `nota` en `/api/estado`, `ranking` y `experimento` en
  `/api/publico`, los dos CSV, el paquete, las copias y `reiniciar`. Se anota como desviación de
  `unit-of-work.md` con este motivo.
- **Consequences** — A favor: al cerrar U5, el panel funciona de punta a punta para un reto completo
  (abrir, cerrar, publicar). En contra: U6 toca `/api/publico` y `/api/estado`, que U1 y U5 ya tienen;
  son agregados de claves, seguros por contrato (C1, «Agregar es seguro»).
- **Alternatives Rejected** — B: dos cambios a la misma ruta. C: pantallas inutilizables una tanda entera.

## ADR-W12: Preguntas abiertas OQ6 y OQ8 — sin bloqueo por intentos, sin cierre automático, 10 salas

- **Context** — OQ6 pregunta si hace falta un límite de intentos fallidos de clave; OQ8, cuántas salas
  puede haber a la vez y si una sala vencida se cierra sola (`components.md`, «Pendiente para NFR
  Design»).

| Tema | A. Elegida | B. Rechazada | Por qué |
|---|---|---|---|
| Intentos de clave | Sin bloqueo; solo la espera de 600 ms que U1 ya aplica a códigos que no existen se aplica también a una clave incorrecta, fuera del bloqueo del objeto | Bloquear la clave tras n intentos | El secreto tiene 16 caracteres de un alfabeto de 32 (80 bits) y la clave del semillero 12 o más: adivinar es inviable; un bloqueo dejaría a un docente fuera de su sala por un ataque trivial a mitad del reto (cambio de conducta visible) |
| Cierre automático | La sala no se cierra sola: cada intento vence solo (ADR-004) y el docente cierra cuando quiere, como hoy | Pasar la sala a «cerrado» cuando venza el reloj global | Hoy la sala sigue «abierto» hasta que el docente la cierra; cambiarlo altera el flujo de estados (`project.md`, «Forbidden») |
| Salas a la vez | Sin tope en el código; la guía recomienda hasta 10 salas abiertas a la vez, que es la cifra con la que NFR1 y U1-E2 estimaron el consumo | Un tope en `crear_sala` | Un tope rechaza un reto real por una estimación; `GET /api/admin/salas` deja ver cuántas hay |

- **Decision** — Las tres de la columna A.
- **Consequences** — El consumo con más de 10 salas abiertas a la vez puede acercarse al 50 % de la
  cuota (U1-E2); U2 lo mide y U17 lo anota.

## ADR-W13: El colegio se muestra siempre por su nombre definitivo, resuelto al leer

- **Context** — C-11 (revisión del contrato): `colegio` en `/api/estado`, `/api/publico`, el resumen y
  los CSV tiene que ser el nombre del catálogo, y el paquete el `id_colegio` definitivo. Con «unir» un
  provisional apunta a otro colegio (`unido_a`).

| | A. Resolver al leer: `COALESCE(unido_a, id_colegio)` en cada consulta | B. Reescribir `participantes.id_colegio` al unir | C. Guardar el nombre en `participantes` |
|---|---|---|---|
| Deshacer una unión | Posible: se borra `unido_a` | No sin rastro | No |
| Consultas | Un `JOIN` más | Ninguna | Ninguna |
| Datos limpios (FR10.3) | Sí | Sí | No: el nombre se desactualiza |

- **Decision** — A, con `unido_a` de un solo salto: solo se puede unir un provisional a un colegio que
  no es provisional ni está unido; el servidor lo rechaza con 400. Una sola función en `reto.js`,
  `colegio_definitivo(id)`, y una vista SQL `colegios_definitivos` para los `JOIN`.
- **Consequences** — A favor: unir y deshacer no tocan a los participantes. En contra: cada lectura con
  colegio lleva el `JOIN`; con 40 filas no se nota.
- **Alternatives Rejected** — B: destruye la información de qué provisional era. C: ensucia los datos.
