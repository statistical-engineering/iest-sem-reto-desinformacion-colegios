# Contratos del reto en la nube

Qué datos cruzan cada frontera, con qué forma y qué pasa si algo falla. Sale de las unidades y sus
dependencias (`unit-of-work.md`, `unit-of-work-dependency.md`), de los componentes (`components.md`), de
los ADR (`decisions.md`, ADR-009 a ADR-011) y de los requisitos revisados (`requirements.md`). Las
respuestas de la primera versión de esta etapa están en `contract-design-questions.md` (Q1 a Q6, todas A,
2026-10-25); las decisiones de esta revisión, en su sección «Revisión 2026-10-25».

**Revisión del 2026-10-25 (una sola sala, solo Cloudflare).** La versión anterior de este documento estaba
escrita para varias salas en paralelo y cinco opciones de hosting. El humano fijó que «esto lo controla un
solo profesor en un solo panel. no con varios profesores con varios paneles. es solo una sala.»
(`../requirements-analysis/reglas-de-negocio-2026-10-25.md`). Este contrato vale para **la versión de
Cloudflare Workers** (`despliegues/cloudflare/`, FR12.2c), con **una sola sala, un solo docente, una sola
clave docente y un reloj por colegio** (FR11, ADR-010, ADR-011). Desaparecen la clave del semillero, las
claves de sala, `?sala=`, crear y borrar salas, el catálogo del semillero y los colegios «provisionales».
Entran la lista de colegios del docente, «Arrancar reloj», el podio general con clasificación por grado y
nota, el paquete `.zip` y las copias de «Reiniciar».

## Contratos

| # | Proveedor | Consumidor | Mecanismo | Dueño |
|---|---|---|---|---|
| C1 | Cloudflare Workers (U1, U4 a U6) | External: navegador (`web/js/estudiante.js`, `web/js/admin.js`, `web/tablero.html`) | REST/HTTP, JSON | Prueba común (U1 la creó, U2 la completa) |
| C2 | Cloudflare desplegado y la versión local (`2_Aplicacion_Reto/`) | Prueba común (U1, U2) | REST/HTTP, la misma API de C1 | Prueba común (U2) |
| C3 | Prueba común (U2) | Comparación (U17) | Esquema compartido: un JSON por corrida | U2 |
| C4 | Reglas (U4) | Reto, colegios, examen y resultados (U5, U6) | Llamada a función dentro del servicio | U4 es dueña del código; la forma y la tabla de casos, del contrato |
| C5 | Exportación (U6) | External: carpeta privada del semillero (FR9.4) | Esquema compartido: paquete `.zip` | Contrato (U2); el diccionario de FR9.3 lo describe |

Las fronteras entre unidades de la misma opción son llamadas a funciones dentro del mismo servicio
(`unit-of-work-dependency.md`, «Puntos de integración»). C4 fija su forma para que la tabla de casos
(`despliegues/prueba_comun/casos_reglas.json`) se pueda copiar a las pruebas sin reescribirla.

**Opciones que no se construyen (FR12.2c).** Los contratos de Google Apps Script, GitHub Pages, Render y
Cloudflare Containers quedan **fuera de este documento**: esas opciones no se construyen ni se despliegan,
así que no hay API, archivo de mediciones ni paquete que cumplir. En `despliegues/COMPARACION.md` entran
solo con su documentación (U15, U16) o marcadas «no pasa» / «no se construye» con el motivo. Si el humano
reabre una de ellas, su contrato se escribe en ese momento a partir de este, sin compartir código (FR12.2).

## C1 y C2. API HTTP

**Dónde vive.** `despliegues/prueba_comun/contrato_api.yaml` (Q1-A). Todavía no existe: el bloque de
abajo es su contenido inicial completo, y U2 lo crea tal cual. Las 16 rutas de hoy (5 GET y 11 POST,
`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/api-documentation.md`) se mantienen con sus
rutas y claves JSON (FR4.1); lo que se agrega va marcado «nueva» y lo que se quita está en «Rutas y claves
eliminadas». Las claves JSON y las rutas que usa `web/js/` **no se renombran** (`CLAUDE.md`, «Convenciones
de idioma y código»).

### Reglas comunes

- **Niveles de acceso (FR7.2, ADR-010).** Cada ruta declara uno de tres niveles; una ruta sin nivel no
  responde (404 «No encontrado.»):
  - `publico`: sin credencial;
  - `token`: cabecera `Authorization: Bearer <token>` del participante; sin token o con uno que no existe,
    401 «Sesión no encontrada. Vuelve a entrar con tu código.»;
  - `clave`: cabecera `X-Clave-Admin` con la clave docente; cubre todo `/api/admin/*`.
- **Clave docente (NFR9, ADR-010, FR9.5).** Es el secreto `CLAVE_DOCENTE` de Cloudflare (`npx wrangler
  secret put CLAVE_DOCENTE`; en local, `.dev.vars`). Arranque se niega a arrancar si tiene menos de 12
  caracteres y lo dice en el registro sin mostrarla. Se compara **en tiempo constante**, después de quitar
  los espacios de los extremos y **sin cambiar mayúsculas**. Solo viaja en la cabecera `X-Clave-Admin`:
  una petición a `/api/admin/*` que traiga `clave` en la URL (`?clave=`) recibe 403 aunque la cabecera sea
  correcta, para que la clave nunca quede en los registros del hosting (`project.md`, «Corrections»).
  Clave ausente o incorrecta: 403 `{"error": "Clave de docente incorrecta."}` sin ningún otro dato. No hay
  límite de intentos (OQ6 cerrada en ADR-010). Hay una sola clave: no existe rol ni prefijo de sala.
- **Una sola sala (FR11.1, ADR-011).** Ninguna ruta recibe ni acepta `?sala=`; si llega, se ignora. El
  «código de sala» sigue existiendo: lo fija el docente en `/api/admin/config` y lo escriben los
  estudiantes al inscribirse, como hoy.
- **Chequeo de salud.** `GET /api/publico` sin parámetros responde 200 con los datos del tablero y es el
  `healthCheckPath` del hosting (`project.md`, «Corrections», regla del 2026-10-26).
- **Errores (Q4-A).** `{"error": "<mensaje en español>"}` con 400, 401, 403, 404 o 413, como hoy; 500
  `{"error": "Error interno del servidor."}` sin detalles, con la traza en el registro; **503**
  `{"error": "El servicio no responde. Intenta de nuevo en un momento."}` si el Durable Object no responde
  o la plataforma está sin cuota (`worker.js`). El navegador no reintenta un POST por su cuenta.
- **Una sola respuesta por pregunta.** Repetir `POST /api/responder` con la misma pregunta da 400 «Esa
  pregunta ya fue respondida.», así que un reintento de la persona nunca suma dos veces.
- **Cuerpo de POST.** JSON; vacío se lee como `{}`; más de 65.536 bytes da 413 «Petición demasiado
  grande.»; JSON roto o que no es objeto da 400 «JSON no válido.».
- **Cabeceras de toda respuesta.** `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`, como hoy.
- **Horas.** Todas en segundos desde 1970 (número con decimales), medidas por el servidor (NFR11). Los
  tiempos de bono y desempate son relativos al arranque del colegio del participante (FR2.6).
- **Antes de atender cualquier ruta** se aplica la entrega por tiempo de los intentos vencidos, por colegio
  (ADR-004): toda consulta ve como entregado lo que ya venció (FR3.2).
- **Confidencialidad (NFR8, FR6).** Ninguna ruta `publico` ni `token` entrega respuestas correctas,
  explicaciones, veredictos ni `multitud_acierta` antes de `resultados`. Los ids de opciones, ítems, partes
  y publicaciones que salen por `/api/estado` son opacos por participante (ADR-006) y `/api/responder` los
  recibe opacos. El banco nunca se sirve como archivo.

### Tabla de rutas

Veintitrés rutas: las 16 de hoy, `GET /api/colegios` (que trajo el corte) y 6 nuevas del panel. Las
columnas «Cuerpo» y «Respuesta» nombran claves JSON; «como hoy» remite a `api-documentation.md`.

| Método | Ruta | Nivel | Cuerpo | Respuesta 200 | Errores |
|---|---|---|---|---|---|
| GET | `/api/publico` | `publico` | — | Tablero y salud: `evento`, `titulo`, `estado`, `sala`, `urls`, `duracion_min`, `abierto_en`, `cerrado_en`, `servidor_ahora`, `modo_sorpresa`, `reloj_global` (siempre `true`), `conteo` {`inscritos`, `en_curso`, `finalizados`}, **`colegios[]`** (nueva) {`id_colegio`, `nombre`, `arranque`, `restante_seg`}; `ranking[]` (top 10) {`puesto`, `nombre`, `colegio`, `grado`, `total`, `puntos`, **`nota`**, **`puesto_grado`**} y **`por_grado`** (nueva) {`"9"`, `"10"`, `"11"`: top 10 de ese grado con las mismas claves} solo en `resultados` o con modo sorpresa apagado; `experimento` solo en `cerrado` (`{n, listo}`) y `resultados` (completo) | 503 |
| GET | `/api/colegios` | `publico` | — | `colegios[]` {`id_colegio`, `nombre`}, ordenados por nombre. Sin parámetros; `?sala=` se ignora | — |
| POST | `/api/registro` | `publico` | `nombre`, `colegio` (**`id_colegio`** de `/api/colegios`), `grado` (`"9"`, `"10"`, `"11"`), `integrantes`, `sala` | `token`, `codigo` | 400 «Las inscripciones están cerradas.», «El código de sala no es correcto. Míralo en el tablero.», «Escribe tu nombre (o el del equipo).», «Elige el grado: 9, 10 u 11.», «Elige tu colegio de la lista.», «Ya hay alguien inscrito con ese nombre en ese colegio y grado. …» |
| POST | `/api/entrar` | `publico` | `codigo` | `token`, `codigo` | 404 «No encontramos ese código. Revísalo (son 5 caracteres).» tras 0,6 s |
| GET | `/api/estado` | `token` | — | Como hoy, ids opacos, más **`participante.colegio_arranque`** y **`participante.colegio_restante_seg`**; en `resultados` y `finalizado` también **`participante.puesto_grado`**. Detalle en «Qué ve el estudiante de su reloj» | 401 |
| POST | `/api/comenzar` | `token` | `{}` | `ok` | 400 «El reto todavía no ha empezado. Espera la señal del docente.», **«Tu colegio todavía no ha empezado. Espera la señal del docente.»**, «El tiempo del reto ya terminó.» |
| POST | `/api/responder` | `token` | `pregunta` (id), `respuesta` (ids opacos; forma por tipo como hoy) | `ok`; con retro `puntos`, `max`, `fraccion` | 400 «Tu intento ya terminó.», «El reto está cerrado.», «Pregunta desconocida.», «Pregunta no disponible.», «Esa pregunta ya fue respondida.», «Primero responde la parte anterior de esta misión.», «Respuesta incompleta o con formato no válido.» |
| POST | `/api/finalizar` | `token` | `{}` | `ok` | 401 |
| POST | `/api/evento` | `token` | `tipo` (`"salida"`) | `ok` | 401 |
| POST | `/api/admin/login` | `clave` | `{}` | `ok` (solo esa clave; `rol` y `sala` del corte desaparecen) | 403 |
| GET | `/api/admin/resumen` | `clave` | — | Como hoy (`config`, `urls`, `banco`, `participantes[]`, `experimento` completo, `servidor_ahora`) más **`colegios[]`** y, en cada participante, **`id_colegio`** y **`puesto_grado`**. Detalle en «Resumen del panel» | 403 |
| POST | `/api/admin/estado` | `clave` | `estado` ∈ {`inscripcion`, `abierto`, `cerrado`, `resultados`} | `ok` | 400 «Estado no válido.», **«Ese cambio de estado no está permitido.»** (FR7.4) |
| POST | `/api/admin/config` | `clave` | Cualquiera de `modo_sorpresa` (bool), `retro` (bool), `sala` (3 a 8 letras o números), `evento`, `duracion_min` (10 a 240, solo en `inscripcion`) | `ok` | 400 «La sala debe tener de 3 a 8 letras o números.», «La duración solo se cambia antes de abrir el reto.», **«El reloj es por colegio y ya no se configura.»** si llega `reloj_global` |
| GET | `/api/admin/colegios` | `clave` | — | `colegios[]` {`id_colegio`, `nombre`, `arranque`, `equipos`, `reloj` {`estado`, `restante_seg`}} (nueva, FR11.5) | 403 |
| POST | `/api/admin/colegios` | `clave` | `accion` ∈ {`agregar`, `quitar`, `arrancar`} con sus claves (ver «Lista de colegios y relojes») | `agregar`: `ok`, `agregados[]` {`id_colegio`, `nombre`}; `quitar`: `ok`; `arrancar`: `ok`, `arranque` | 400 «Escribe el nombre del colegio (al menos 3 letras).», «Ese colegio ya existe.» (+ `existente`), «Los colegios se agregan o se quitan antes de cerrar el reto.», «Ese colegio ya tiene equipos inscritos; no se puede quitar.», «Abre el reto antes de arrancar un colegio.», «Ese colegio ya arrancó.», «Acción no válida.»; 404 «No existe ese colegio.» |
| POST | `/api/admin/participante` | `clave` | `id`, `accion` ∈ {`finalizar`, `descalificar`, `reactivar`, `eliminar`} | `ok` | 404 «Participante no encontrado.»; 400 «Acción no válida para este participante.» |
| GET | `/api/admin/resultados.csv` | `clave` | — | CSV `;` con BOM, mismas columnas que hoy; la columna `colegio` lleva el nombre | 403 |
| GET | `/api/admin/respuestas.csv` | `clave` | — | CSV `;` con BOM, mismas columnas que hoy, con los ids del banco | 403 |
| GET | `/api/admin/paquete.zip` | `clave` | — | `application/zip`, nombre `AAAA-MM-DD_<sala>_reto.zip`, contenido en C5 (nueva, FR9.1) | 403 |
| POST | `/api/admin/reiniciar` | `clave` | `confirmar` = `"BORRAR"` | `ok`, `copia` (**ahora el `id_copia`** de la copia guardada, no un nombre de archivo) | 400 «Escribe BORRAR para confirmar.» |
| GET | `/api/admin/copias` | `clave` | — | `copias[]` {`id_copia`, `creada`, `nombre_archivo`, `bytes`} (nueva, R-17) | 403 |
| GET | `/api/admin/copia?id=<id_copia>` | `clave` | — | El archivo de la copia (`Content-Disposition: attachment`), formato del ADR de U6 (FR4.3) (nueva) | 404 «No existe esa copia.» |
| POST | `/api/admin/copia/borrar` | `clave` | `id_copia` | `ok` (nueva, NFR10.1) | 404 «No existe esa copia.» |

Las páginas `/`, `/admin`, `/tablero` y `/static/*` las sirve Cloudflare como recursos estáticos de `web/`
sin pasar por el Worker (FR4.2); todo lo demás que no sea `/api/*` da 404.

### Qué ve el estudiante de su reloj (FR3.1, FR11.3, NFR8)

`GET /api/estado` conserva todas sus claves. Dentro de `participante` se agregan dos y, en resultados, una
tercera:

| Clave | Valor | Para qué |
|---|---|---|
| `participante.colegio_arranque` | hora en que el docente arrancó el colegio del participante, o `null` si no ha arrancado | La pantalla de espera muestra «Tu colegio todavía no ha empezado. Espera la señal del docente.» cuando `reto.estado` es `abierto` y esta clave es `null`; habilita «Comenzar» solo cuando tiene valor |
| `participante.colegio_restante_seg` | segundos que le quedan al reloj de su colegio (`arranque + duracion − ahora`, mínimo 0), o `null` si no ha arrancado | Avisa cuánto tiempo tiene antes de pulsar «Comenzar»; coincide con `restante_seg` una vez en curso |
| `participante.puesto_grado` | puesto dentro de su grado, solo en `resultados` y `finalizado` (junto a `puesto` y `nota`, como hoy) | Pantalla final (FR2.5) |

`restante_seg` sigue igual que hoy: segundos que quedan al participante `en_curso`, calculados con su
`inicio`, que ahora es el arranque de su colegio. `reto.reloj_global` se mantiene en el JSON con el valor
fijo `true` porque `web/js/` la lee (FR4.1); la copia de `estudiante.js` deja de usarla para elegir
textos y describe el reloj por colegio. Nada de esto revela respuestas: `revision` sigue llegando solo en
`resultados` y con el participante `finalizado`.

### Lista de colegios y relojes (ADR-009, ADR-011, FR11.5)

`POST /api/admin/colegios` lleva `accion` y estas claves:

| `accion` | Claves | Regla | Respuesta |
|---|---|---|---|
| `agregar` | `nombres` (texto con un nombre por línea) o `nombre` (uno solo) | Solo con el reto en `inscripcion` o `abierto`. Cada línea pasa por LimpiezaEntrada (NFC, sin invisibles, espacios juntos, 80 caracteres) y necesita al menos 3 letras. Si una línea está vacía tras limpiar se omite; si un nombre normalizado ya existe en la lista, **no se agrega ninguno** y se responde 400 «Ese colegio ya existe.» con `existente` {`id_colegio`, `nombre`}. El servidor genera `id_colegio` | `ok`, `agregados[]` {`id_colegio`, `nombre`} |
| `quitar` | `id_colegio` | Solo en `inscripcion` o `abierto` y solo si el colegio no tiene equipos | `ok` |
| `arrancar` | `id_colegio` | Solo con el reto en `abierto` y el colegio sin `arranque`; pone `arranque = ahora`. No se repite ni se deshace | `ok`, `arranque` |

`GET /api/admin/colegios` y `colegios[]` de `/api/admin/resumen` traen, por colegio: `id_colegio`,
`nombre`, `arranque` (hora o `null`), `equipos` (participantes no descalificados) y `reloj`
{`estado` ∈ {`sin_arrancar`, `corriendo`, `vencido`}, `restante_seg` (`null` si no arrancó, 0 si venció)}.
«Abrir el reto» (`POST /api/admin/estado` con `abierto`) fija `abierto_en` y pone `arranque = ahora` en
cada colegio que ya tiene al menos un equipo inscrito; los demás se arrancan uno a uno. Un colegio que se
agrega con el reto `abierto` nace sin arranque. «Reiniciar» borra la lista junto con el reto.

### Cambios de estado (FR1.1, FR7.4)

`POST /api/admin/estado` acepta solo las transiciones que ofrece el panel; cualquier otra da 400 «Ese
cambio de estado no está permitido.». Pedir el estado actual responde `ok` sin hacer nada.

| De | A | Efectos |
|---|---|---|
| `inscripcion` | `abierto` | Fija `abierto_en` si no existía; arranca los colegios con equipos |
| `abierto` | `cerrado` | Entrega con motivo `cierre` a todo `en_curso` de todos los colegios, hayan vencido o no; pasa a `no_inicio` a quien sigue `registrado`; fija `cerrado_en` |
| `cerrado` | `resultados` | Publica: el tablero muestra podio, clasificación general y por grado y el experimento completo; el estudiante ve `puesto`, `puesto_grado`, `nota` y `revision` |

### Resumen del panel (FR11.5, FR2.5)

`GET /api/admin/resumen` conserva `config` (valores como texto; `config.reloj_global` queda fijo en
`"1"` porque `admin.js` lo lee), `urls`, `banco`, `participantes[]`, `experimento` (completo en cualquier
estado: es ruta del docente) y `servidor_ahora`. Cambia así:

- `participantes[]` agrega `id_colegio` y `puesto_grado`; `colegio` sigue siendo el nombre, `puesto` el
  general y `nota` como hoy. `restante_seg` y `tiempo_usado` salen del arranque del colegio.
- agrega `colegios[]` con la forma de «Lista de colegios y relojes».

Podio general = `puesto` 1, 2 y 3 de `participantes[]`; la clasificación por grado se obtiene filtrando
por `grado` y leyendo `puesto_grado`. El panel ve todo sin importar el modo sorpresa.

### Podio, clasificación por grado y modo sorpresa (FR2.5, FR6.1, FR11.4)

En `GET /api/publico`:

- `ranking[]` (top 10 del orden total entre todos los colegios) y `por_grado` (top 10 de cada grado con
  el mismo orden) se envían solo cuando `estado` es `resultados` **o** `modo_sorpresa` está apagado, como
  hoy con `ranking`. El podio son los tres primeros de `ranking`. Cada fila trae `puesto`, `puesto_grado`,
  `nombre`, `colegio`, `grado`, `total`, `puntos` y `nota`.
- con modo sorpresa encendido, antes de `resultados` no salen `ranking` ni `por_grado`, y el tablero
  muestra «La clasificación se revela al final», como hoy.
- `experimento` sale en `cerrado` solo como `{n, listo}` (lo único que el tablero usa en ese estado, para
  su firma de cambios) y completo en `resultados`. Así nunca salen `por_publicacion[].verdad` ni
  `multitud_acierta` antes de publicar (FR6.1).
- `colegios[]` {`id_colegio`, `nombre`, `arranque`, `restante_seg`} sale en todo estado, para que el
  tablero muestre el reloj de cada colegio; `abierto_en` y `duracion_min` siguen y dan el reloj de
  referencia de hoy.

### Cambios que exige el navegador (FR4.1)

Son las copias en `despliegues/cloudflare/web/`; `2_Aplicacion_Reto/web/` no cambia (FR12.1).

| Archivo de `web/` | Cambio | Motivo |
|---|---|---|
| `tablero.html` | Deja de leer `?sala=` de su URL y de pasarla a `/api/publico`; muestra el reloj de cada colegio con `colegios[]`; agrega la diapositiva o el bloque de clasificación por grado y la nota con `por_grado` | Una sala (FR11.4); podio general y por grado (FR2.5) |
| `js/estudiante.js` | La lista «Colegio» se llena con `GET /api/colegios` al abrir el formulario, sin esperar el código de sala; en la sala de espera muestra «Tu colegio todavía no ha empezado. Espera la señal del docente.» y habilita «Comenzar» con `colegio_arranque`; los textos de reglas describen el reloj por colegio en vez de leer `reloj_global`; la pantalla final muestra `puesto_grado` | FR10.3, FR3.1, FR11.3, FR2.5 |
| `js/admin.js` | Al entrar, no pasa la clave a mayúsculas (`toUpperCase`) porque la clave docente se compara tal cual (ADR-010); el aviso de dónde está la clave deja de nombrar `datos/clave_docente.txt` | NFR9, ADR-010 |
| `js/admin.js` | Desaparece el interruptor «Reloj global» y sus textos; en su lugar, la lista de colegios con el estado de cada reloj, «Agregar colegios» (un nombre por línea), «Quitar» y «Arrancar reloj» con confirmación doble | ADR-011, FR11.5, ADR-009 |
| `js/admin.js` | Botón «⬇ Paquete del semillero (.zip)»; lista de copias con «Descargar» y «Borrar» cada una; el aviso de «Reiniciar» muestra el `id_copia` en vez de `datos/<archivo>` | FR9.1, R-17, NFR10.1 |
| `js/admin.js` | Columna o filtro «Puesto en el grado» con `puesto_grado` | FR2.5 |

El estudiante no ve otro cambio (FR11.3). Son las excepciones aprobadas en `components.md`, «Cambios que
el docente y el estudiante ven».

### Rutas y claves eliminadas

Todo esto existía en el contrato anterior o en el corte desplegado (`despliegues/cloudflare/src/reto.js`)
y **se quita**; la prueba común comprueba que responden 404 (ruta) o se ignoran (parámetro):

| Qué | Dónde estaba | Por qué |
|---|---|---|
| `POST /api/admin/salas/crear`, `GET /api/admin/salas`, `POST /api/admin/salas/clave`, `POST /api/admin/salas/borrar` | Contrato anterior; `crear` también en `reto.js` | Una sola sala (FR11.1, ADR-011) |
| `GET` y `POST /api/admin/catalogo` | Contrato anterior | Sin catálogo del semillero (ADR-009) |
| `GET /api/admin/copia?sala=` y `GET /api/admin/copias?sala=`: el parámetro | Contrato anterior | Sin `?sala=` |
| Parámetro `?sala=` en `/api/publico`, `/api/colegios` y `/api/admin/*` | Contrato anterior y `reto.js` | Se ignora; `GET /api/publico` sin parámetros devuelve el tablero |
| Respuesta `{"ok": true}` sola en `GET /api/publico` sin `?sala=` | Contrato anterior y `reto.js` | Reemplazada por los datos del tablero, que también son el chequeo de salud |
| Niveles `semillero` y `sala`; claves `rol` y `sala` en `/api/admin/login` | `reto.js` | Un solo nivel `clave` (ADR-010) |
| Secreto `CLAVE_SEMILLERO`, prefijo `<código>-` y huella de clave de sala | `reto.js`, `wrangler.jsonc` | Secreto `CLAVE_DOCENTE` (ADR-010) |
| `accion: "provisional"` y la clave `provisional` en `existente` | `reto.js` | Sin colegios provisionales (ADR-009) |
| `reloj_global` como opción configurable en `/api/admin/config` | Hoy y `reto.js` | Reloj por colegio (ADR-011); la clave sigue en el JSON con valor fijo |
| `copia` como nombre de archivo en `/api/admin/reiniciar` | Hoy | Ahora es `id_copia` (R-17) |

### Qué cambia respecto al corte desplegado (`reto.js`)

Para que Construction (U4 a U6) sepa qué romper y qué conservar del corte de U1:

| Se conserva | Se cambia |
|---|---|
| El Worker que pasa `/api/*` al único Durable Object y responde 404 y 503 (`worker.js`) | Tabla `RUTAS`: quitar `salas/crear`; `GET /api/publico` y `GET /api/colegios` sin `?sala=`; `POST /api/admin/colegios` pasa a nivel `clave` con acciones `agregar`, `quitar`, `arrancar`; agregar las rutas nuevas del panel |
| `blockConcurrencyWhile` para atender de a una (R-10), `transactionSync` para escribir | `dar_acceso` queda con tres niveles; `acceso_admin` compara `X-Clave-Admin` con `CLAVE_DOCENTE` sin `toUpperCase` y rechaza `?clave=`; desaparecen `sala_de_acceso`, `sala_por_codigo` y `sala_de` |
| `leer_cuerpo`, `respuesta_json`, `ErrorAPI`, los mensajes de error existentes | Esquema: la tabla `salas` pasa a una fila `reto` (`codigo`, `estado`, `duracion_min`, `modo_sorpresa`, `retro`, `evento`, `abierto_en`, `cerrado_en`) sin `clave_huella` ni `reloj_global`; `colegios` gana `arranque` y pierde `provisional`; desaparece `sala_colegios`; `participantes` pierde `id_sala`; aparece `copias` (`id_copia`, `creada`, `nombre_archivo`, `contenido`) |
| `vencer_tiempos` antes de cada petición y `cerrar` (ADR-004) | `vencer_tiempos` ya no une con `salas`: usa la duración del reto y el `inicio` de cada participante (que es el arranque de su colegio); `cerrar_intento` recibe el mismo `inicio` |
| `registrar` (limpieza, repetido por `id_colegio` y grado, grupo A/B, código único), `entrar`, `responder`, `finalizar`, `evento`, ids opacos (ADR-006) | `registrar` compara `sala` con `reto.codigo` y busca el colegio en `colegios`; `comenzar` exige `arranque` del colegio y usa `inicio = arranque`; `estado` agrega `colegio_arranque`, `colegio_restante_seg` y, en resultados, `puesto`, `puesto_grado`, `nota` y `revision` |
| `revisar_banco` con la huella propia (`project.md`, «Corrections») | `cambiar_estado` aplica las tres transiciones con sus efectos; `login` responde solo `ok`; `crear_sala` se borra; `agregar_colegio` se reescribe como las tres acciones |
| `banco.json`, `banco_huella.json`, `reglas.js` (se completa en U4) | `publico` devuelve el tablero sin parámetro, con `colegios[]`, `ranking`, `por_grado` y el experimento recortado en `cerrado`; se agregan `resumen`, `config`, `participante`, los dos CSV, `paquete.zip`, `copias`, `copia` y `copia/borrar` |
| Las páginas copiadas en `web/` | Las copias cambian como dice «Cambios que exige el navegador»; el parche `herramientas/cambios_web.patch` se rehace |

### Contenido inicial de `contrato_api.yaml`

```yaml
openapi: 3.0.3
info:
  title: API del reto «Detectives de la desinformación» en Cloudflare
  version: "2.0"
  description: >
    Una sola sala, un solo docente, una sola clave docente y un reloj por colegio (FR11, ADR-009 a
    ADR-011). Las 16 rutas de hoy (api-documentation.md) se mantienen con sus claves JSON; aquí están
    todas las rutas, con lo que cambia y lo nuevo. Sin versión en la ruta (Q3-A). Ningún parámetro ?sala=.
components:
  securitySchemes:
    token:
      type: http
      scheme: bearer
      description: Token del participante, dado por /api/registro o /api/entrar.
    claveDocente:
      type: apiKey
      in: header
      name: X-Clave-Admin
      description: >
        Única clave; secreto CLAVE_DOCENTE del hosting, 12 caracteres o más, comparada en tiempo
        constante sin cambiar mayúsculas. Nunca en la URL: ?clave= da 403 aunque la cabecera sea correcta.
  schemas:
    Error:
      type: object
      required: [error]
      properties:
        error: {type: string}
    Ok:
      type: object
      required: [ok]
      properties:
        ok: {type: boolean}
    ColegioPublico:
      type: object
      required: [id_colegio, nombre]
      properties:
        id_colegio: {type: string}
        nombre: {type: string}
    ColegioTablero:
      type: object
      required: [id_colegio, nombre, arranque, restante_seg]
      properties:
        id_colegio: {type: string}
        nombre: {type: string}
        arranque: {type: [number, "null"], description: segundos desde 1970 o null si no arrancó}
        restante_seg: {type: [number, "null"], description: null si no arrancó, 0 si venció}
    ColegioPanel:
      allOf:
        - $ref: "#/components/schemas/ColegioTablero"
        - type: object
          required: [equipos, reloj]
          properties:
            equipos: {type: integer}
            reloj:
              type: object
              required: [estado, restante_seg]
              properties:
                estado: {type: string, enum: [sin_arrancar, corriendo, vencido]}
                restante_seg: {type: [number, "null"]}
    FilaRanking:
      type: object
      required: [puesto, puesto_grado, nombre, colegio, grado, total, puntos, nota]
      properties:
        puesto: {type: integer}
        puesto_grado: {type: integer}
        nombre: {type: string}
        colegio: {type: string}
        grado: {type: string, enum: ["9", "10", "11"]}
        total: {type: number}
        puntos: {type: number}
        nota: {type: number, description: 1 + 4 x puntos / 1.000, sin el bono}
    Copia:
      type: object
      required: [id_copia, creada, nombre_archivo, bytes]
      properties:
        id_copia: {type: string}
        creada: {type: number}
        nombre_archivo: {type: string}
        bytes: {type: integer}
  responses:
    Error400: {description: Petición inválida, content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
    Error401: {description: "Sesión no encontrada. Vuelve a entrar con tu código.", content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
    Error403: {description: "Clave de docente incorrecta.", content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
    Error404: {description: No existe, content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
    Error503: {description: "El servicio no responde. Intenta de nuevo en un momento.", content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
paths:
  /api/publico:
    get:
      summary: Tablero y chequeo de salud (cambia, FR6.1, FR11.4, FR2.5)
      description: >
        Sin parámetros. Claves de hoy (evento, titulo, estado, sala, urls, duracion_min, abierto_en,
        cerrado_en, servidor_ahora, modo_sorpresa, reloj_global siempre true, conteo) más colegios[].
        ranking[] (top 10 general) y por_grado solo en «resultados» o con modo_sorpresa apagado.
        experimento solo en «cerrado» ({n, listo}) y «resultados» (completo).
      responses:
        "200":
          description: Datos del tablero; un 200 es «sano» para el hosting.
          content:
            application/json:
              schema:
                type: object
                required: [evento, titulo, estado, sala, urls, duracion_min, abierto_en, cerrado_en, servidor_ahora, modo_sorpresa, reloj_global, conteo, colegios]
                properties:
                  colegios: {type: array, items: {$ref: "#/components/schemas/ColegioTablero"}}
                  ranking: {type: array, maxItems: 10, items: {$ref: "#/components/schemas/FilaRanking"}}
                  por_grado:
                    type: object
                    properties:
                      "9": {type: array, maxItems: 10, items: {$ref: "#/components/schemas/FilaRanking"}}
                      "10": {type: array, maxItems: 10, items: {$ref: "#/components/schemas/FilaRanking"}}
                      "11": {type: array, maxItems: 10, items: {$ref: "#/components/schemas/FilaRanking"}}
        "503": {$ref: "#/components/responses/Error503"}
  /api/colegios:
    get:
      summary: Colegios para la lista de la inscripción (FR10.3)
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                required: [colegios]
                properties:
                  colegios: {type: array, items: {$ref: "#/components/schemas/ColegioPublico"}}
  /api/registro:
    post:
      summary: Inscripción (cambia una clave, FR10.3)
      description: Mismas claves que hoy; «colegio» es el id_colegio de /api/colegios; «sala» se compara con el código del reto.
      responses:
        "200": {description: "{token, codigo}"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/entrar:
    post:
      summary: Volver a entrar con el código personal (igual que hoy)
      responses:
        "200": {description: "{token, codigo}"}
        "404": {$ref: "#/components/responses/Error404"}
  /api/estado:
    get:
      summary: Estado del participante (agrega claves, FR3.1, FR6.2)
      description: >
        Mismas claves que hoy; ids opacos (ADR-006). participante.colegio_arranque y
        participante.colegio_restante_seg siempre; participante.puesto_grado solo en «resultados» y
        «finalizado», junto a puesto, nota y revision.
      security: [{token: []}]
      responses:
        "200": {description: Mismas claves que hoy más las tres nuevas}
        "401": {$ref: "#/components/responses/Error401"}
  /api/comenzar:
    post:
      summary: Comenzar (cambia un mensaje, FR3.1)
      description: Exige reto «abierto» y colegio arrancado; el inicio es el arranque del colegio.
      security: [{token: []}]
      responses:
        "200": {description: "{ok: true}"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/responder:
    post:
      summary: Responder una vez (igual que hoy, ids opacos)
      security: [{token: []}]
      responses:
        "200": {description: "{ok, puntos?, max?, fraccion?}"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/finalizar:
    post:
      summary: Entregar (igual que hoy)
      security: [{token: []}]
      responses:
        "200": {description: "{ok: true}"}
  /api/evento:
    post:
      summary: Salida de pestaña (igual que hoy)
      security: [{token: []}]
      responses:
        "200": {description: "{ok: true}"}
  /api/admin/login:
    post:
      summary: Entrar al panel (igual que hoy)
      security: [{claveDocente: []}]
      responses:
        "200": {description: "{ok: true}"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/resumen:
    get:
      summary: Resumen del panel (agrega claves, FR11.5, FR2.5)
      description: >
        Como hoy más colegios[] (ColegioPanel) y, por participante, id_colegio y puesto_grado.
        config.reloj_global queda fijo en "1".
      security: [{claveDocente: []}]
      responses:
        "200": {description: Resumen}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/estado:
    post:
      summary: Cambiar el estado (cambia, FR7.4)
      description: Solo inscripcion→abierto, abierto→cerrado, cerrado→resultados; otra da 400.
      security: [{claveDocente: []}]
      responses:
        "200": {description: "{ok: true}"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/admin/config:
    post:
      summary: Configurar el reto (cambia, ADR-011)
      description: modo_sorpresa, retro, sala, evento, duracion_min como hoy; reloj_global da 400.
      security: [{claveDocente: []}]
      responses:
        "200": {description: "{ok: true}"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/admin/colegios:
    get:
      summary: Lista de colegios con su reloj (nueva, FR11.5)
      security: [{claveDocente: []}]
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                required: [colegios]
                properties:
                  colegios: {type: array, items: {$ref: "#/components/schemas/ColegioPanel"}}
    post:
      summary: Agregar, quitar o arrancar colegios (nueva, ADR-009, ADR-011)
      security: [{claveDocente: []}]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [accion]
              properties:
                accion: {type: string, enum: [agregar, quitar, arrancar]}
                nombres: {type: string, description: "agregar: un nombre por línea"}
                nombre: {type: string, description: "agregar: un solo nombre"}
                id_colegio: {type: string, description: "quitar y arrancar"}
      responses:
        "200": {description: "agregar: {ok, agregados[]}; quitar: {ok}; arrancar: {ok, arranque}"}
        "400": {$ref: "#/components/responses/Error400"}
        "404": {$ref: "#/components/responses/Error404"}
  /api/admin/participante:
    post:
      summary: Acciones sobre un participante (igual que hoy)
      security: [{claveDocente: []}]
      responses:
        "200": {description: "{ok: true}"}
        "400": {$ref: "#/components/responses/Error400"}
        "404": {$ref: "#/components/responses/Error404"}
  /api/admin/resultados.csv:
    get:
      summary: CSV de resultados (igual que hoy)
      security: [{claveDocente: []}]
      responses:
        "200": {description: "text/csv con BOM, separador ;"}
  /api/admin/respuestas.csv:
    get:
      summary: CSV de respuestas (igual que hoy)
      security: [{claveDocente: []}]
      responses:
        "200": {description: "text/csv con BOM, separador ;"}
  /api/admin/paquete.zip:
    get:
      summary: Paquete de datos del reto (nueva, FR9.1, FR9.5)
      security: [{claveDocente: []}]
      responses:
        "200": {description: "application/zip, nombre AAAA-MM-DD_<sala>_reto.zip, contenido en C5"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/reiniciar:
    post:
      summary: Reiniciar el reto (cambia el valor de «copia»)
      description: Pide confirmar = "BORRAR". Guarda primero una Copia y devuelve su id_copia.
      security: [{claveDocente: []}]
      responses:
        "200": {description: "{ok: true, copia: <id_copia>}"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/admin/copias:
    get:
      summary: Copias de «Reiniciar» (nueva, R-17)
      security: [{claveDocente: []}]
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                required: [copias]
                properties:
                  copias: {type: array, items: {$ref: "#/components/schemas/Copia"}}
  /api/admin/copia:
    get:
      summary: Descargar una copia (nueva)
      security: [{claveDocente: []}]
      parameters:
        - {name: id, in: query, required: true, schema: {type: string}}
      responses:
        "200": {description: Archivo de la copia, en el formato del ADR de U6 (FR4.3)}
        "404": {$ref: "#/components/responses/Error404"}
  /api/admin/copia/borrar:
    post:
      summary: Borrar una copia ya guardada en el lugar privado (nueva, NFR10.1)
      security: [{claveDocente: []}]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [id_copia]
              properties:
                id_copia: {type: string}
      responses:
        "200": {description: "{ok: true}"}
        "404": {$ref: "#/components/responses/Error404"}
```

### La prueba común con una sola sala (C2)

`despliegues/prueba_comun/src/prueba.py` hoy recibe `--clave` como clave del semillero y crea una sala
(`--modo nube`). Con este contrato:

- `--clave` es siempre la **clave docente**, en la nube y en local (`unit-of-work.md`, U2);
- en vez de crear una sala, la prueba fija el código con `POST /api/admin/config` (`sala`), carga sus
  colegios de ensayo con `POST /api/admin/colegios` (`agregar`) y abre el reto; contra la versión local
  escribe el colegio como texto, porque esa versión no cambia (FR12.1);
- comprueba el 403 con clave ausente, incorrecta y con `?clave=` (NFR9), el 404 de las rutas eliminadas y
  que `GET /api/publico` sin parámetros devuelve el tablero;
- la prueba de relojes por colegio (FR11.7) arranca dos colegios a distinta hora con `arrancar` y verifica
  que cada uno vence por su cuenta y que el bono se mide desde su arranque;
- nunca imprime claves, tokens ni respuestas correctas.

## C3. Archivo de mediciones

Un JSON por corrida en `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` (Q5-A). U17 lo lee
para llenar `despliegues/COMPARACION.md` (FR12.4). Todavía no existe ninguna medición, así que el esquema
sigue en la versión 1 con dos ajustes: `salas` pasa a `colegios` y la parte `salas` de las comprobaciones
pasa a `relojes`.

```yaml
# esquema compartido (JSON Schema escrito en YAML)
$schema: "https://json-schema.org/draft/2020-12/schema"
title: Medición de una corrida de la prueba común
type: object
required: [version_esquema, opcion, url, inicio, fin, todo_bien, comprobaciones, nfr]
properties:
  version_esquema: {const: 1}
  opcion: {enum: [local, cloudflare]}
  url: {type: string}
  inicio: {type: string, format: date-time}
  fin: {type: string, format: date-time}
  todo_bien: {type: boolean}
  comprobaciones:
    type: array
    items:
      type: object
      required: [id, parte, pasa]
      properties:
        id: {type: string}          # nombre fijo de la comprobación, por ejemplo «fuga_verdad_cerrado»
        parte: {enum: [base, fugas, relojes, claves, nfr]}
        pasa: {type: boolean}
        detalle: {type: string}     # nunca una clave ni una respuesta correcta
  nfr:
    type: object
    required: [p95_responder_ms, p95_tablero_ms, sobrevive_reinicio, arranque_frio_ms, colegios, participantes, peticiones]
    properties:
      p95_responder_ms: {type: number}
      p95_tablero_ms: {type: number}
      sobrevive_reinicio: {type: [boolean, "null"]}   # null cuando no aplica
      arranque_frio_ms: {type: [number, "null"]}
      colegios: {type: integer}                         # colegios arrancados a distinta hora (NFR1: 3)
      participantes: {type: integer}
      peticiones: {type: integer}                       # para comparar con la cuota (NFR6)
```

El archivo nunca lleva la URL con clave, ninguna clave ni datos de participantes de un reto real.

## C4. Forma de las reglas

Mismos nombres, entradas y salidas en la opción construida y en la tabla de casos (Q6-A). La tabla,
`despliegues/prueba_comun/casos_reglas.json` («estos datos y esta hora dan este resultado», ADR-001), se
copia a `despliegues/cloudflare/pruebas/`. Ninguna regla lee la base ni el reloj: la hora llega como
argumento. Los nombres son los componentes de `components.md` (CicloDelReto reemplaza a CicloDeSala).

```yaml
# forma de las «calculadoras» (ADR-001); tipos en notación neutral
reglas:
  Banco:
    validar_banco: {entrada: [banco], salida: "lista de errores (vacía si está bien)"}
    examen_publico: {entrada: [banco, semilla, grupo, respondidas], salida: "misiones[] con ids opacos (FR6.2)"}
    traducir_opaco: {entrada: [semilla, pregunta_id, ids, respuesta_opaca], salida: "respuesta con ids del banco"}
  Calificacion:
    validar_respuesta: {entrada: [pregunta, respuesta], salida: "respuesta normalizada o error"}
    fraccion: {entrada: [pregunta, respuesta], salida: "número entre 0 y 1"}
    bono: {entrada: [puntos, tiempo_respuestas_seg, duracion_seg], salida: "número"}
    cerrar_intento: {entrada: [ahora, inicio, duracion_seg, ultima_respuesta, puntos], salida: "{fin, tiempo_usado, tiempo_respuestas, bono, total}"}
  Clasificacion:
    ordenar: {entrada: ["participantes finalizados"], salida: "lista con puesto, sin empates (NFR11): total ↓, puntos ↓, tiempo_respuestas ↑, tiempo_usado ↑, id ↑"}
    por_grado: {entrada: ["lista ordenada"], salida: "{grado: lista con puesto_grado}"}
    nota: {entrada: [puntos], salida: "nota sobre 5, dos decimales"}
  CicloDelReto:
    transicion_permitida: {entrada: [estado_actual, estado_nuevo], salida: booleano}
    puede_arrancar_colegio: {entrada: [estado_reto, arranque], salida: "booleano o motivo"}
    puede_comenzar: {entrada: [estado_reto, estado_participante, arranque, duracion_seg, ahora], salida: "booleano o motivo"}
    hora_de_entrega: {entrada: [ahora, inicio, duracion_seg, cierre], salida: "{hora, motivo: tiempo | cierre} o nada"}
    estado_reloj: {entrada: [arranque, duracion_seg, ahora], salida: "{estado: sin_arrancar | corriendo | vencido, restante_seg}"}
  LimpiezaEntrada:
    normalizar_texto: {entrada: [texto, largo], salida: texto}
    normalizar_integrantes: {entrada: [texto], salida: "{texto, n_integrantes}"}
    normalizar_nombre_colegio: {entrada: [texto], salida: "nombre normalizado para detectar repetidos"}
    validar_inscripcion: {entrada: [campos, ids_colegios], salida: "campos limpios o error"}
  Experimento:
    calcular: {entrada: ["participantes y respuestas del reto", estado_reto], salida: "objeto «experimento»; sin por_publicacion antes de resultados"}
casos_reglas:
  formato: "[{regla, funcion, entrada, salida_esperada}]"
  regla_de_oro: "la salida esperada se calcula con el servidor local, nunca se escribe a mano"
  no_lleva: "respuestas correctas del banco: los casos de Calificacion usan un banco de prueba propio"
  caso_obligatorio: "dos colegios con arranque distinto: Clasificacion.ordenar da el mismo orden que la versión local cuando los arranques coinciden (FR11.7)"
```

## C5. Paquete de datos

```yaml
# esquema compartido del .zip (FR9.1, FR9.2, FR9.5, R-11)
nombre: "AAAA-MM-DD_<sala>_reto.zip"
archivos:
  participantes.csv: "una fila por participante: id, nombre, id_colegio, colegio, grado, integrantes, n_integrantes, grupo, estado, creado, inicio, fin, motivo_fin, puntos, bono, total, tiempo_usado, tiempo_respuestas, salidas, puesto, puesto_grado, nota; sin token, semilla ni codigo personal"
  respuestas.csv: "una fila por respuesta: participante_id, pregunta_id del banco (nunca el opaco), variante, respuesta, fraccion, puntos, max_puntos, momento"
  eventos.csv: "una fila por evento: id_evento, participante_id, tipo, momento"
  colegios.csv: "los colegios del reto: id_colegio, nombre, arranque, equipos"
  copia: "la copia completa de los datos del reto, en el formato que fije el ADR de U6 (FR4.3), sin token, semilla ni codigo"
  metadatos.json:
    campos: [inicio, fin, sala, evento, duracion_min, participantes, colegios, version_banco, huella_banco, version_app]
formato:
  codificacion: UTF-8 con encabezado
  fechas: "ISO 8601 con zona horaria, por ejemplo 2026-11-03T08:15:00-05:00"
  decimales: punto
  nunca: [claves, token, semilla, codigo personal]
```

Los dos CSV de hoy (`resultados.csv`, `respuestas.csv` de `/api/admin/*.csv`) no cambian de columnas ni
de formato (FR4.3). La copia de «Reiniciar» (`/api/admin/copia`) lleva lo mismo que `copia` del paquete. El
diccionario de FR9.3 describe cada columna del paquete y advierte que `id_colegio` no se conserva entre
retos: varios años se unen por el nombre normalizado de `colegios.csv` (ADR-009).

## Reglas de dueño y de cambio

- **C1 y C2:** el dueño es la prueba común. La opción cumple el contrato cuando la prueba común da
  «TODO BIEN» contra su URL.
- **Agregar** una clave, una ruta o una comprobación es seguro: el cliente ignora lo que no conoce (Q3-A).
- **Quitar o renombrar** exige un ADR, la aprobación del humano y cambiar en el mismo push la copia de
  `web/` de la opción, `contrato_api.yaml` y la prueba común. Las eliminaciones de esta revisión ya están
  aprobadas con ADR-009 a ADR-011.
- **C3:** `version_esquema` sube con cualquier cambio que no sea agregar, a partir de la primera medición
  guardada; U17 rechaza una versión que no conoce.
- **C4:** la tabla de casos solo crece. U4 la escribe en el mismo push en que escribe las reglas.
- **C5:** igual que C1; además, cambiar una columna obliga a cambiar el diccionario de FR9.3 en el mismo
  push.
- Push directo a `develop` para el humano y el asistente; el resto del equipo por PR (`team.md`,
  «Corrections»). Antes de cada push: el simulacro y, si se tocó la opción o el contrato, la prueba común.

## Preguntas abiertas

| Contrato | Pregunta | Bloquea |
|---|---|---|
| C1 | `duracion_min` admite de 10 a 240 minutos (conducta de hoy). La prueba común necesita que un colegio venza sin esperar 10 minutos reales; hay que decidir si se permite una duración menor solo con una variable del entorno de prueba, o si la prueba espera | U2 |
| C1 | El 503 por cuota: el ADR de la opción dice cómo detecta el Worker que se quedó sin cuota, además del caso en que el Durable Object no responde | U5 |
| C5 | Formato de `copia` para el Durable Object con SQLite (volcado SQL, archivo SQLite u otro) lo fija el ADR de U6 | U6 |
| C1 | `colegios[]` en `GET /api/publico` muestra los nombres de los colegios en una página pública; los nombres ya salen en `ranking`, así que no es un dato nuevo, pero OQ5 (nombres de menores en el tablero) sigue abierta | — |

## Sources

- `../units-generation/unit-of-work.md` y `unit-of-work-dependency.md`: unidades U1, U2, U4 a U6, U17 y
  «Puntos de integración».
- `../domain-design/components.md`: «Quién pide y con qué», «El reloj de cada colegio», «Copias y
  "Reiniciar"», «Cambios que el docente y el estudiante ven», «Pendiente para Contract Design».
- `../domain-design/decisions.md`: ADR-001, ADR-004, ADR-006, ADR-007, ADR-009, ADR-010, ADR-011.
- `../requirements-analysis/requirements.md`: FR1 a FR4, FR6, FR7.2, FR7.4, FR9, FR10, FR11, FR12.2c,
  FR12.3, NFR8, NFR9, NFR11; `reglas-de-negocio-2026-10-25.md`, §1, §4, §7 y §9.
- `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/api-documentation.md`: las 16 rutas de hoy.
- `2_Aplicacion_Reto/servidor.py` (`publico`, `resumen_admin`, `estado_participante`, `clasificacion`,
  `cambiar_estado`, `accion_participante`, `reiniciar`, bloque de `config`), `2_Aplicacion_Reto/web/js/estudiante.js`,
  `admin.js` y `web/tablero.html`: qué lee cada pantalla.
- `despliegues/cloudflare/src/reto.js` (`RUTAS`, `ESQUEMA`, `dar_acceso`, `acceso_admin`),
  `worker.js`, `wrangler.jsonc` y `herramientas/cambios_web.patch`: el corte desplegado.
- `despliegues/prueba_comun/LEEME.md` y `src/prueba.py`: la prueba común mínima de hoy.
- `aidlc/spaces/default/memory/project.md`, «Corrections»: `X-Clave-Admin` sin `?clave=`,
  `GET /api/publico` sin parámetros, huella propia del banco.
- `contract-design-questions.md`: Q1 a Q6 y «Revisión 2026-10-25».
