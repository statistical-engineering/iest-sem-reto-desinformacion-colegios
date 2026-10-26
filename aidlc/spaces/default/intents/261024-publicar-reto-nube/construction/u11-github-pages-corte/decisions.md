# ADR de la opción GitHub Pages (U11)

**Estado:** decidido por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). Cumple FR12.2b: este ADR va antes del código de `despliegues/github-pages/`.
Las cuotas se consultaron el 2026-10-25 en la documentación oficial, con su URL en cada tabla; ninguna
cifra viene de memoria (A6 de `requirements.md`).

GitHub Pages solo sirve archivos estáticos («a static site hosting service that takes HTML, CSS, and
JavaScript files straight from a repository»,
https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages). Por eso esta
opción son **dos piezas**: las pantallas en Pages y la API en otro servicio gratuito, que elige el
ADR-G1. La conclusión para U17 está al final («Recomendación para U17»).

## ADR-G1: La API corre en PythonAnywhere (plan gratuito)

- **Context** — Hace falta un servicio gratuito para la API que cumpla a la vez: sin tarjeta (NFR6),
  persistencia que sobreviva reinicios (NFR4), que no se duerma a mitad de un reto de 90 minutos (NFR5),
  una sola instancia o serialización por sala («revisar y escribir sin cruzarse», `components.md`), sin
  código compartido con `despliegues/cloudflare/` (FR12.2), y que se pueda probar en esta máquina con lo
  instalado: Node 24, Python 3.12, `npx`; no hay `deno` ni `bun`, y no se instala nada sin aprobación.
  Además tiene que poder responder a la consulta previa de CORS con cabeceras propias (hallazgo C-04).

| | A. PythonAnywhere, plan gratuito | B. Otro Worker de Cloudflare | C. Vercel Hobby + Neon Free | D. Deno Deploy Free | E. Supabase Free | F. Render free | G. Netlify Functions + Blobs | H. Fly.io |
|---|---|---|---|---|---|---|---|---|
| Costo y tarjeta | «$0/month»; la página no pide tarjeta (https://www.pythonanywhere.com/pricing/) | Gratis, sin tarjeta (U1, verificado 2026-10-25) | Hobby gratis, «non-commercial, personal use only» (https://vercel.com/docs/plans/hobby); Neon «$0/month» (https://neon.com/docs/introduction/plans) | «$0/month» (https://deno.com/deploy/pricing) | «from $0/month» (https://supabase.com/pricing) | Gratis, «750 Free instance hours» al mes (https://render.com/docs/free) | Gratis | «New organizations don't have a free tier» (https://docs.fly.io/about/pricing) |
| Persistencia | Disco propio de «512 MiB» (https://help.pythonanywhere.com/pages/FreeAccountsFeatures/): un archivo SQLite | SQLite del Durable Object | Postgres en Neon: «1 GB/project» | KV «1 GiB» | Postgres «500 MB database size per project» | «don't support … persistent disks»: **no cumple NFR4** | Blobs: «last write wins», «does not include a concurrency control mechanism» (https://docs.netlify.com/blobs/overview/) | — |
| ¿Se duerme a mitad del reto? | No hay un tiempo de inactividad que la apague; lo que vence es la app sin uso al cabo de «1 month expiry» (misma URL), y se prorroga con un clic | No | La función no; Neon «suspend after 5 minutes of inactivity», que «can't be disabled»: cada pausa del reto despierta la base | «Idle apps automatically shut down after ~20-30 seconds»: arranque en frío en cada pausa | «Free projects are paused after 1 week of inactivity»: hay que reactivar el proyecto antes de cada reto | «spins down after 15 minutes without receiving any inbound traffic», «about one minute» para volver | La función no | — |
| Sin cruzarse | «1 web app with 1 web worker»: un solo proceso, más `BEGIN IMMEDIATE` de SQLite (ADR-G5) | Un Durable Object | Transacciones de Postgres con bloqueo de fila | Operaciones atómicas de KV, sin transacciones de varias claves | Transacciones de Postgres | Un proceso | Solo escrituras condicionales (`onlyIfMatch`): hay que reintentar a mano | — |
| Cuota de peticiones | Los CPU-segundos «does not currently apply to your web apps» (https://help.pythonanywhere.com/pages/WhatAreCPUSeconds); ancho de banda «Low», sin cifra | 100.000 por día | 1.000.000 invocaciones y «4 CPU-hrs» al mes | «1M inbound HTTP requests per month», «10 hours of Active CPU» | «500,000» invocaciones de Edge Functions | — | — | — |
| ¿Se prueba en esta máquina? | Sí: Python 3.12 con `wsgiref` de la biblioteca estándar | Sí: `npx wrangler` (como U1) | A medias: las funciones con Node, pero no hay Postgres local y haría falta el paquete `pg` | No: exige `deno`, que no está instalado | No: Edge Functions corren en Deno | Sí | Sí para Node; no hay Blobs local sin la CLI de Netlify | — |
| Código compartido con `cloudflare/` | Ninguno: otro lenguaje | Sería una copia de `cloudflare/src/`: cumple la letra de FR12.2 y no su espíritu | Ninguno | Ninguno | Ninguno | Ninguno | Ninguno | — |
| Servicios externos de la opción (con Pages) | 2: GitHub y PythonAnywhere | 2: GitHub y Cloudflare | 3: GitHub, Vercel y Neon | 2 | 2 | 2 | 2 | — |
| CORS con cabecera propia | Sí: la API fija cualquier cabecera y responde `OPTIONS` | Sí | Sí | Sí | Sí | Sí | Sí | — |

- **Decision** — **A. PythonAnywhere.** Es la única columna que cumple todas las filas: gratis sin
  tarjeta, disco persistente propio, sin apagado por inactividad corta, un solo proceso, probable con la
  biblioteca estándar de Python y sin una línea en común con `cloudflare/`. B es la opción Cloudflare
  otra vez; C suma un tercer servicio; D y E exigen Deno; F pierde los datos al reiniciar; G no tiene
  candado; H no es gratis.

  Las cifras del plan gratuito que esta opción usa (consultadas el 2026-10-25):

| Cifra | Valor | Fuente |
|---|---|---|
| Precio | «$0/month» | https://www.pythonanywhere.com/pricing/ |
| Apps web | «1 web app with 1 web worker and 1 month expiry», en `<usuario>.pythonanywhere.com` con «free SSL support» | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ y https://www.pythonanywhere.com/pricing/ |
| Disco | «512 MiB of disk space» | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ |
| CPU | «100 CPU seconds» por día para consolas y tareas; «It does not currently apply to your web apps» | https://help.pythonanywhere.com/pages/WhatAreCPUSeconds |
| Vencimiento | «Unused web apps will expire after 1 month, rather than 3 months» (cambio de enero de 2026); se prorroga entrando y pulsando el botón de la pestaña Web, y avisan por correo una semana antes | https://blog.pythonanywhere.com/221/ y https://blog.pythonanywhere.com/129 |
| Salida a internet | Solo a una lista permitida; incluye `.github.com`, `.github.io` y `.githubusercontent.com`, así que `git clone` y `git pull` del repositorio funcionan | https://www.pythonanywhere.com/whitelist/ y https://help.pythonanywhere.com/pages/403ForbiddenError/ |
| Python | Las versiones dependen de la imagen del sistema de la cuenta («haggis» o «innit»); la API se escribe para Python 3.10 o más reciente, que está en las dos | https://help.pythonanywhere.com/pages/PythonVersions |
| MySQL y tareas programadas | Solo para cuentas creadas antes del 2026-01-15; no se usan | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ |

- **Consequences** — A favor: la API queda en Python, el lenguaje del equipo, con SQLite como hoy, así
  que la copia de «Reiniciar» vuelve a ser un `reto.db` (FR4.3) y las «calculadoras» de ADR-001 se
  prueban con `unittest` y `trace`, como manda `team.md`. En contra: hay que prorrogar la app cada mes
  (paso de la guía antes de cada reto); el ancho de banda gratuito no tiene cifra, así que NFR6 se cierra
  con la medición de U2; un solo worker atiende de a una petición, y una espera dentro de una petición
  frena a las demás (ADR-G5 saca la espera de BR3.4 del candado y la acorta). El código se sube con
  `git pull` desde una consola de PythonAnywhere, sin herramienta nueva.
- **Alternatives Rejected** — B: duplica la opción Cloudflare y la deja dominada por construcción. C:
  tres servicios y una base que no corre en esta máquina. D y E: Deno. F: sin disco persistente. G: sin
  candado ni transacciones. H: sin plan gratuito. Apps Script: no lee cabeceras ni fija códigos de estado
  (`contract-design/reviews/review-01.md`, C-01).

## ADR-G2: Pages publica `web/` como sitio de proyecto con un flujo manual de GitHub Actions

- **Context** — GitHub Pages se incluye en GitHub Free «in public repositories»
  (https://docs.github.com/en/get-started/learning-about-github/githubs-plans); el repositorio ya es
  público (decisión del humano, 2026-10-25). Un sitio de proyecto vive en
  «http(s)://<owner>.github.io/<repositoryname>»
  (https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages), así que las
  rutas absolutas de hoy (`/static/css/reto.css`, `href="/"`, `href="/tablero"`) dejan de servir. Hay
  dos formas de publicar: «publish when changes are pushed to a specific branch» (raíz o `/docs` de la
  rama) o «write a GitHub Actions workflow to publish your site»
  (https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
  Las pantallas están en `despliegues/github-pages/web/`, que no es ni la raíz ni `/docs`.

| | A. Flujo de Actions solo manual (`workflow_dispatch`) que sube `despliegues/github-pages/web/` | B. Rama `gh-pages` con la carpeta en su raíz (`git subtree push`) | C. Mover las pantallas a `/docs` de `develop` |
|---|---|---|---|
| Despliegue a mano (FR5.2) | Sí: alguien pulsa «Run workflow» | Sí: alguien hace el push | No: cada push a la rama publica solo |
| Piezas nuevas | Un archivo `.github/workflows/publicar-pages.yml` | Una rama de larga vida más (contra `team.md`, «Way of Working») | Mueve `web/` fuera de la carpeta de la opción (contra `despliegues/LEEME.md`) |
| Volver atrás | «Run workflow» sobre la referencia anterior, o «Re-run jobs» de una corrida anterior | Otro push | Revertir el commit |
| Cuota | Actions «2,000 minutes per month» en GitHub Free; cada publicación tarda alrededor de un minuto | Los «10 builds per hour» del modo rama | Igual que B |

- **Decision** — **A.** El flujo `.github/workflows/publicar-pages.yml` solo se dispara con
  `workflow_dispatch`, usa `actions/configure-pages@v5`, `actions/upload-pages-artifact@v4` con
  `path: despliegues/github-pages/web` y `actions/deploy-pages@v4`, con los permisos mínimos que pide la
  guía («pages: write» e «id-token: write») y el entorno `github-pages`
  (https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
  El origen del sitio se fija a «GitHub Actions» en Settings → Pages. **No es CI**: no corre al fusionar
  ni al subir cambios; aun así es un archivo de workflow nuevo, y `team.md` nombra a `revisar-pr.yml`
  como la única CI aprobada, así que el humano lo aprueba junto con este ADR.

  Forma de `web/` (la genera `herramientas/copiar.sh`, igual que en U1, con su propio parche):

| En `2_Aplicacion_Reto/web/` | En `despliegues/github-pages/web/` | Por qué |
|---|---|---|
| `estudiante.html` | `index.html` | `/` |
| `admin.html` | `admin/index.html` | `/admin` sin depender de que Pages resuelva `admin.html`; Pages siempre sirve el `index.html` de una carpeta |
| `tablero.html` | `tablero/index.html` | `/tablero?sala=` |
| `css/`, `js/` | `static/css/`, `static/js/` más `static/js/config.js` | Mismas rutas que las otras opciones; `config.js` lleva la URL de la API (ADR-G4) |
| — | `.nojekyll` | Pages no pasa los archivos por Jekyll |

  Todas las referencias del HTML pasan a relativas (`./static/...` en `index.html`, `../static/...`,
  `../` y `../tablero/` en las otras dos), así el sitio funciona con el prefijo `/<repositorio>/` y
  también en `http://localhost` al probar.
- **Consequences** — A favor: una sola carpeta de opción, despliegue a mano y el mismo nombre de rutas
  que las otras opciones para la prueba común. En contra: Pages pone `Cache-Control: max-age=600` a sus
  archivos, así que un cambio de pantallas tarda hasta 10 minutos en llegar a un navegador que ya las
  abrió; la guía dice publicar sin reto en curso y esperar esos minutos antes de la prueba de humo.
- **Alternatives Rejected** — B: una rama más de larga vida. C: saca las pantallas de la carpeta de la
  opción y publica solo.

## ADR-G3: Python de la biblioteca estándar, WSGI, tabla de rutas y sin capa de base

- **Context** — FR7.2 pide que cada ruta declare su nivel de acceso y que el ADR decida cómo se
  despachan; FR7.3 pide decidir si hay capa aparte de base de datos; FR7.6 y `team.md` fijan `unittest`,
  `trace` y ruff. PythonAnywhere ejecuta una aplicación WSGI que importa desde un archivo de su pestaña
  Web; no exige framework.

| | A. WSGI a mano con la biblioteca estándar | B. Flask | C. Copiar `servidor.py` entero y adaptarlo |
|---|---|---|---|
| Dependencias nuevas | Ninguna | Una (Flask) y sus transitivas: requieren aprobación (FR7.6) | Ninguna |
| Rutas | Tabla `"MÉTODO /ruta" → (nivel, función)`, como ADR-W3 | Decoradores; el nivel de acceso quedaría repartido | Cadenas de `if` de hoy (lo que FR7.2 quiere evitar) |
| Pruebas sin servidor | `application(environ, start_response)` se llama directo en `unittest` | Cliente de prueba de Flask | Hace falta levantar `http.server` |
| Prueba en local | `wsgiref.simple_server` | `flask run` | Igual que hoy |

- **Decision** — **A.** Archivos: `src/wsgi.py` (Arranque y ApiHttp: lee configuración y secretos, valida
  el banco, abre SQLite, CORS, JSON, tabla de rutas con nivel y una sola salida de errores),
  `src/servicio.py` (Acceso, Salas, CatalogoColegios, Inscripcion, Examen y, en U14, Resultados y
  Exportacion, con su SQL dentro), `src/reglas.py` (las «calculadoras» de C4, sin E/S) y
  `src/servidor_local.py` (solo para probar: `wsgiref` para la API y `http.server` para `web/`, en dos
  puertos distintos para que CORS se ejercite). No hay capa aparte de base de datos (FR7.3): hay una sola
  implementación, SQLite. Pruebas con `unittest` en `pruebas/`, cobertura con
  `python3 -m trace --count --missing` sobre `src/`, ruff con el `[tool.ruff]` del repositorio, y el
  `pyproject.toml` de la raíz sin cambios porque no hay paquetes.
- **Consequences** — A favor: cero dependencias, el mismo juego de herramientas que el resto del
  repositorio y pruebas de la API que llaman a `application` sin red. En contra: hay que escribir a mano
  lo que un framework regala (leer el cuerpo con tope, cabeceras, `OPTIONS`), unas 80 líneas.
- **Alternatives Rejected** — B: una dependencia que no aporta nada que no quepa en 80 líneas. C:
  arrastra la mezcla de SQL, reloj y HTTP que FR7 quiere separar.

## ADR-G4: CORS con origen exacto y URL base de la API en `config.js`

- **Context** — Las pantallas viven en `https://<cuenta>.github.io` y la API en
  `https://<usuario>.pythonanywhere.com`. `web/js/` llama con rutas relativas (`fetch("/api/...")`) y
  manda las cabeceras `Authorization` y `X-Clave-Admin`, que obligan al navegador a una consulta previa
  `OPTIONS`. El contrato no definía CORS ni la URL base (hallazgo C-04; Delivery Planning Q4-A lo asigna a
  U11).

| | A. Origen exacto en una variable de la API y URL base en `static/js/config.js` | B. `Access-Control-Allow-Origin: *` | C. Un proxy en Pages |
|---|---|---|---|
| Seguridad | Solo el sitio de Pages puede llamar con claves desde un navegador | Cualquier página puede llamar a la API con una clave robada | — |
| Cambios en `web/js/` | Una línea por archivo: `RETO_API + ruta` | Igual | — |
| ¿Posible en Pages? | Sí | Sí | No: Pages no ejecuta código |

- **Decision** — **A.** La API lee `RETO_ORIGENES` (lista de orígenes separados por coma, sin barra final;
  en local incluye `http://localhost:8792`). Toda respuesta a una petición con `Origin` permitido lleva
  `Access-Control-Allow-Origin: <ese origen>`, `Vary: Origin` y, en las descargas,
  `Access-Control-Expose-Headers: Content-Disposition`. `OPTIONS` sobre `/api/*` responde 204 con
  `Access-Control-Allow-Methods: GET, POST, OPTIONS`,
  `Access-Control-Allow-Headers: Content-Type, Authorization, X-Clave-Admin` y
  `Access-Control-Max-Age: 600`. Un `Origin` no permitido no recibe las cabeceras y el navegador bloquea
  la respuesta. Nunca `*`, nunca credenciales de cookie. Las pantallas cargan
  `static/js/config.js` (`window.RETO_API = "https://<usuario>.pythonanywhere.com";`, sin barra final) y
  el helper `api()` de `estudiante.js`, el de `admin.js` y el `fetch` de `tablero.html` anteponen
  `window.RETO_API`. `config.js` es un archivo versionado en `herramientas/` que `copiar.sh` copia: la URL
  de la API es pública y no es un secreto.

  Cambios en la tabla «Cambios que exige el navegador» del contrato (FR4.1), solo para esta opción:

| Archivo de `web/` | Cambio | Motivo |
|---|---|---|
| `static/js/config.js` (nuevo) | URL base de la API | Pantallas y API en dominios distintos (C-04) |
| `static/js/estudiante.js`, `static/js/admin.js`, `tablero/index.html` | `fetch(window.RETO_API + ruta, …)` | Idem |
| `index.html`, `admin/index.html`, `tablero/index.html` | rutas relativas y `<script src=".../static/js/config.js">` | Prefijo `/<repositorio>/` del sitio de proyecto |

  La prueba común recibe `--url-web` (opcional; por defecto igual a `--url`) para pedir las pantallas en
  un origen y la API en otro. Es un agregado de tres líneas a `despliegues/prueba_comun/src/prueba.py`,
  seguro según «Reglas de dueño y de cambio» del contrato (agregar es seguro); U2 lo conserva.
- **Consequences** — A favor: la clave solo sale desde el sitio de Pages. En contra: cada petición con
  cabecera propia lleva un `OPTIONS` previo (el navegador lo guarda 600 s), y hay que cambiar la URL en
  `config.js` si cambia el usuario de PythonAnywhere.
- **Alternatives Rejected** — B: abre la API a cualquier página. C: imposible en Pages.

## ADR-G5: SQLite en disco, un candado del proceso y `BEGIN IMMEDIATE`; copia de sala como `reto.db`

- **Context** — Hay que guardar salas, colegios, participantes, respuestas, eventos y copias de forma
  persistente (NFR4) y hacer «revisar y escribir sin cruzarse» (`components.md`). PythonAnywhere da un
  worker y un disco de 512 MiB. FR4.3 pide que la copia de «Reiniciar» sea «`reto.db` en las opciones
  con SQLite» y ADR-005 que lleve solo las filas de esa sala (R-05).

| | A. Un archivo SQLite, un `threading.Lock` del proceso y `BEGIN IMMEDIATE` en cada escritura | B. Un archivo SQLite por sala | C. MySQL de PythonAnywhere |
|---|---|---|---|
| Sin cruzarse | El candado hace pasar las peticiones de a una, como `LOCK` en `servidor.py`; `BEGIN IMMEDIATE` protege además si la plataforma llegara a usar hilos | Por sala, pero la unicidad global (códigos, colegios) exige otra base más | Transacciones |
| Unicidad global | `UNIQUE` en una sola base | Imposible con una base por sala | `UNIQUE` |
| Copia de una sala | Una base nueva con `ATTACH` e `INSERT … SELECT … WHERE sala = ?` | Copiar el archivo | Volcado SQL |
| Plan gratuito | Sí | Sí | Solo cuentas creadas antes del 2026-01-15 |

- **Decision** — **A.** `RETO_DATOS/reto.db` (por defecto `datos/` junto a `src/`, ignorado por git; en
  PythonAnywhere `~/reto_datos/`), con `PRAGMA journal_mode=WAL`, `busy_timeout=5000` y
  `foreign_keys=ON`. Tablas como en U1: `salas`, `colegios`, `sala_colegios`, `participantes`,
  `respuestas`, `eventos`, con `UNIQUE` en códigos, token, nombre normalizado, (sala, nombre normalizado,
  colegio, grado) y (participante, pregunta); U14 agrega `copias`. Cada petición corre dentro del candado;
  cada escritura, en `BEGIN IMMEDIATE … COMMIT`. La espera corta de BR3.4 (código personal inexistente)
  se hace **fuera del candado** y dura 0,3 s, porque con un solo worker una espera larga frena a toda la
  sala; es la aplicación de la suposición A3 de `requirements.md`. La copia de «Reiniciar» y la del
  paquete son un `reto.db` nuevo con el mismo esquema y solo las filas de la sala, sin las columnas
  `token`, `semilla`, `codigo` ni `clave_huella` (C-06), guardado como blob en `copias`.
- **Consequences** — A favor: reproduce la conducta de hoy (un candado y una base) y la copia se abre
  con cualquier visor de SQLite. En contra: 40 personas y 10 tableros pasan por un solo proceso; U2 mide
  el p95. Un error de SQLite que no se resuelve en 5 s responde 503 (contrato C1).
- **Alternatives Rejected** — B: rompe la unicidad global. C: no está en las cuentas nuevas.

## ADR-G6: Claves, ids opacos y secretos fuera del repositorio

- **Decision** — Huella de la clave de sala = SHA-256 del secreto en hexadecimal (`hashlib`),
  comparación con `hmac.compare_digest` y en mayúsculas (C-03). Id opaco = «o» + 11 caracteres base32 en
  minúsculas de HMAC-SHA256(semilla, `pregunta_id|id`) con `hmac` (ADR-006), 16 si dos chocan en la misma
  pregunta; el orden que ve el navegador es el alfabético de los ids opacos. La clave del semillero y la
  lista de orígenes llegan por variables de entorno (`CLAVE_SEMILLERO`, `RETO_ORIGENES`, `RETO_DATOS`); en
  PythonAnywhere no hay pantalla de variables, así que el archivo WSGI de la pestaña Web (fuera del
  repositorio) las fija leyendo `~/.reto_secretos/clave_semillero.txt` (permisos 600), según la plantilla
  `herramientas/wsgi_pythonanywhere.ejemplo.py`. Sin clave de 12 caracteres o más, o con un guion, las
  rutas de administración responden 500 y el registro dice por qué (igual que U1-S4).
- **Alternatives Rejected** — Guardar la clave en el repositorio o en `config.js`: el repositorio es
  público. PBKDF2 o bcrypt: el secreto de sala ya tiene 80 bits al azar.

## ADR-G7: Banco dentro de `src/`, nunca en Pages

- **Decision** — `src/banco.json` es una copia sin cambios de `2_Aplicacion_Reto/banco_preguntas.json`
  hecha por `herramientas/copiar.sh`, con su huella sha256 en `src/banco_huella.json` (regla de
  `project.md`: la `version` de Python no se recalcula igual en otro lenguaje; aquí sí se podría, pero se
  mantiene la huella para que la prueba común y U17 comparen igual en todas las opciones). Vive en
  PythonAnywhere, nunca en `web/`: el flujo de Pages solo sube `despliegues/github-pages/web/`, así que el
  banco no puede llegar a GitHub Pages ni por error (NFR8). Al arrancar, la API se niega a servir si el
  banco no suma 1.000 puntos o su huella no coincide.

## Recomendación para U17: la opción queda dominada por construcción

Evidencia, con la regla de parsimonia de `project.md` y el orden de FR12.6:

1. **Toda API que cumple las restricciones puede servir ella misma las siete pantallas.** PythonAnywhere
   tiene «Static files» en la pestaña Web (igual que Cloudflare tiene recursos estáticos). Las únicas
   plataformas que no sirven estáticos son las de solo funciones, y ninguna pasó la tabla de ADR-G1.
2. **Pages solo agrega piezas.** Frente a «la misma API sirviendo `web/`», la variante con Pages suma un
   servicio externo más (GitHub Pages, criterio 1 de FR12.6), una pieza propia más (el flujo
   `publicar-pages.yml`, criterio 2), más líneas (CORS, `config.js`, `--url-web`, el parche de rutas
   relativas, criterio 3), una consulta `OPTIONS` por petición con cabecera y una espera de hasta 10
   minutos por la caché de Pages tras cada publicación. No da nada a cambio que FR12.5 mida: el enlace es
   igual de fijo y las pantallas pesan unos cientos de KB por sesión.
3. **Por tanto, Pages nunca puede ganar por FR12.6** a la opción «API sola» del mismo servicio: en el
   mejor caso empata en «pasa todo» y pierde en el criterio 1.

Recomendación: **no construir U11 a U14 tal como están** y anotar en `COMPARACION.md` «GitHub Pages:
dominada por construcción (ADR-G1, «Recomendación para U17»)». Si el semillero quiere una segunda opción
gratuita con disco y en Python, lo parsimonioso es una **sexta opción «PythonAnywhere sola»** (API y
pantallas en el mismo servicio), que exige aprobación del humano porque FR12.2 lista cinco opciones. Ese
diseño es este mismo menos ADR-G2 y ADR-G4 (sin flujo de Pages, sin CORS ni `config.js`, con el mapeo de
estáticos de PythonAnywhere), y sus unidades serían las cuatro de esta opción con esos recortes. Mientras
el humano no decida, los artefactos de U11 a U14 describen lo que se construiría si se mantuviera la
opción con Pages.

## Sources

- `inception/requirements-analysis/requirements.md`: FR4.1, FR4.3, FR5.1, FR5.2, FR7.1 a FR7.6, FR12.2,
  FR12.2b, FR12.5, FR12.6, NFR4, NFR5, NFR6, NFR8, NFR9, A3, A6, OQ1.
- `inception/domain-design/decisions.md`: ADR-001, ADR-003, ADR-004, ADR-005, ADR-006.
- `inception/contract-design/contract-summary.md` y `reviews/review-01.md` (C-01, C-03, C-04, C-06, C-15).
- `inception/delivery-planning/delivery-planning-questions.md` (Q2-A, Q4-A, Q6-A, Q8-A).
- `construction/u1-cloudflare-corte/decisions.md` (ADR-W1 a ADR-W5, cuotas de Cloudflare verificadas el
  2026-10-25).
- `despliegues/LEEME.md`, `despliegues/github-pages/LEEME.md`, `despliegues/prueba_comun/LEEME.md`.
- Documentación oficial consultada el 2026-10-25: las URL de cada tabla.
