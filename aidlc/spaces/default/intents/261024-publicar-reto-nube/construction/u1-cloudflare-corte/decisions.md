# ADR de la opción Cloudflare Workers (U1)

**Estado:** aprobado por el asistente con la potestad que dio el humano («te dejo potestad absoluta
para decidir y corregir si lo consideras necesario», 2026-10-25). Cumple FR12.2b: este ADR va antes del
código de `despliegues/cloudflare/`. Cuotas consultadas el 2026-10-25 en:
- https://developers.cloudflare.com/workers/platform/limits/ («Requests 100,000 per day», «CPU time
  per HTTP request 10 ms»);
- https://developers.cloudflare.com/durable-objects/platform/pricing/ («Workers Free plan can only
  create and access SQLite-backed Durable Objects», «SQLite rows written 100,000 per day»).

## ADR-W1: Un solo Durable Object con SQLite para todo el servicio

- **Context** — Hay que guardar salas, participantes y respuestas de forma persistente (NFR4) y hacer
  «revisar y escribir sin cruzarse» (`components.md`) con unicidad en todo el servicio (códigos de sala
  y personales, colegios). El pedido original nombraba «D1 + un Durable Object por reto».

| | A. Un Durable Object para todo, con su SQLite | B. Un Durable Object por sala + D1 para lo global | C. Solo D1 |
|---|---|---|---|
| Piezas | 1 | 2, y coordinar las dos | 1 |
| Sin cruzarse | Gratis: el objeto atiende una petición a la vez | Por sala; lo global exige transacciones entre D1 y el objeto | Hay que escribir transacciones a mano |
| Unicidad global | Restricción `UNIQUE` en una sola base | En D1, con riesgo de quedar a medias si falla el objeto | `UNIQUE` |
| Carga (40 personas) | Sobra: igual que el candado de hoy (`LOCK` en `servidor.py`) | Sobra | Sobra |
| Plan gratuito | Sí | Sí | Sí |

- **Decision** — A. Es la opción con menos piezas que cumple todo (regla de parsimonia de
  `project.md`). Reproduce la conducta de hoy: un solo candado y una sola base SQLite.
- **Consequences** — Las salas sí se esperan entre sí, pero con 40 personas en total la espera es de
  milisegundos. Si un día hiciera falta, se parte por sala sin cambiar la API.
- **Alternatives Rejected** — B: dos almacenes que coordinar sin necesidad. C: D1 no da la
  serialización que da el objeto.

## ADR-W2: JavaScript sin build, pruebas con `node:test`

- **Decision** — Módulos ES en JavaScript, sin TypeScript. Las reglas puras (`src/reglas.js`) se prueban
  con `node --test` de Node 24, que trae cobertura (`--experimental-test-coverage`). No hay
  `package.json` ni dependencias. Wrangler se usa con versión exacta, `npx wrangler@4.148.0`, solo para
  probar en local y desplegar.
- **Alternatives Rejected** — TypeScript: exige build. Vitest con el pool de Workers: paquetes nuevos.

## ADR-W3: Tabla de rutas y capas

- **Decision** — `src/worker.js` sirve las páginas de `web/` como recursos estáticos y pasa todo
  `/api/*` al Durable Object. `src/reto.js` tiene la clase del objeto, una tabla de rutas
  (`"MÉTODO /ruta" → {nivel, funcion}`, FR7.2) y el SQL. `src/reglas.js` tiene las «calculadoras» de
  C4, sin base ni reloj. No hay capa aparte de base de datos (FR7.3): hay una sola implementación.
- **Alternatives Rejected** — Un archivo por ruta: más archivos sin ganancia.

## ADR-W4: Claves e ids opacos

- **Decision** — Huella de la clave de sala = SHA-256 del secreto en hexadecimal; comparación en
  tiempo constante. La clave del semillero es el secreto `CLAVE_SEMILLERO` del Worker. Id opaco =
  «o» + 11 caracteres base32 de HMAC-SHA256(semilla, `pregunta_id|id`) (ADR-006). El orden que ve el
  navegador es el orden alfabético de los ids opacos: depende de la semilla y no del banco.
- **Alternatives Rejected** — bcrypt o PBKDF2: el secreto ya tiene 80 bits al azar; una huella lenta no
  agrega nada.

## ADR-W5: Banco dentro del código

- **Decision** — `src/banco.json` es una copia sin cambios de `2_Aplicacion_Reto/banco_preguntas.json`,
  hecha por `herramientas/copiar.sh`. Se importa en el código; no está en `web/`, así que nunca se sirve
  (NFR8). Al arrancar se rechaza si no suma 1.000 puntos.
