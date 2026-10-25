# Documentación de la API

API HTTP propia de `2_Aplicacion_Reto/servidor.py` (clase `Manejador`, métodos `do_GET` y `do_POST`).
Todas las respuestas llevan `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`. Las claves
JSON y las rutas **no se renombran**: las usan `web/js/` y `tablero.html` (`.claude/rules/python-code.md`, «Idioma»).

## Convenciones generales

| Aspecto | Comportamiento |
|---|---|
| Formato | JSON UTF-8 (`ensure_ascii=False`) salvo páginas y CSV |
| Cuerpo de POST | JSON; vacío se lee como `{}`; más de 65.536 bytes → 413; JSON inválido → 400 |
| Errores | `{"error": "<mensaje en español>"}` con 400, 401, 403, 404 o 413; cualquier otra excepción → 500 `{"error": "Error interno del servidor."}` y la traza a `stderr` |
| Autenticación del estudiante | Cabecera `Authorization: Bearer <token>` (token de `secrets.token_urlsafe(24)`) |
| Autenticación del docente | Cabecera `X-Clave-Admin: <clave>` o parámetro de consulta `?clave=`; se compara en mayúsculas con `secrets.compare_digest` |
| Barrera de inscripción | Código de sala (4 caracteres por defecto) dentro del cuerpo |
| Serialización | Toda la API corre dentro de `with LOCK:` y empieza con `vencer_tiempos()` |
| Versionado | No hay; la versión del banco viaja en `/api/admin/resumen` → `banco.version` |
| Límite de peticiones | No hay; solo `entrar` espera 0,6 s ante un código inexistente |

Quién llama a cada ruta se tomó de las llamadas `api(...)`/`fetch(...)` de `web/js/estudiante.js`,
`web/js/admin.js` y del `<script>` de `web/tablero.html`; los clientes de prueba (`pruebas/simulacro.py`,
`modo_prueba.py`) se indican aparte.

## Páginas y archivos estáticos

| Método | Ruta | Quién | Autenticación | Respuesta |
|---|---|---|---|---|
| GET | `/` | estudiante | ninguna | `web/estudiante.html` |
| GET | `/admin` | docente | ninguna para la página (la clave se pide en la API) | `web/admin.html` |
| GET | `/tablero` | tablero | ninguna | `web/tablero.html` |
| GET | `/static/<ruta>` | las tres páginas | ninguna | Archivo bajo `web/` (`css/reto.css`, `js/*.js`); se rechaza lo que quede fuera de `web/` tras `resolve()` (404) |

Las páginas y los estáticos se sirven **fuera** del lock global.

## Rutas de la API

### Estudiante

| Método | Ruta | Autenticación | Petición (claves JSON) | Respuesta (claves JSON) | Llamada desde | Errores típicos |
|---|---|---|---|---|---|---|
| POST | `/api/registro` | código de sala en el cuerpo | `nombre`, `colegio`, `grado` (`"9"`, `"10"`, `"11"`), `integrantes`, `sala` | `token`, `codigo` | `estudiante.js` `ingreso()` (pestaña «Inscribirme») | 400 inscripciones cerradas, sala incorrecta, nombre corto, grado inválido, duplicado |
| POST | `/api/entrar` | ninguna (el código de 5 caracteres es la credencial) | `codigo` | `token`, `codigo` | `estudiante.js` `ingreso("codigo")` | 404 código no encontrado (tras 0,6 s) |
| GET | `/api/estado` | Bearer | — | `reto` {`titulo`, `evento`, `estado`, `n_misiones`, `duracion_min`, `puntos_totales`, `bono_max`, `retro`, `reloj_global`}; `participante` {`codigo`, `nombre`, `colegio`, `grado`, `estado`, `restante_seg`, `tiempo_usado`, y si aplica `puntos`, `bono`, `total`, `puesto`, `nota`}; `respuestas` {`<pregunta_id>`: {`respuesta`, y con retro `puntos`, `max`, `fraccion`}}; `servidor_ahora`; `misiones` (si `en_curso` o `finalizado`); `revision` (ver abajo) | `estudiante.js` `cargar()` (al entrar, tras cada envío, sondeo de 4 s y 20 s) | 401 sesión no encontrada |
| POST | `/api/comenzar` | Bearer | `{}` | `ok` | `estudiante.js` `espera()` | 400 reto no abierto, tiempo global terminado |
| POST | `/api/responder` | Bearer | `pregunta` (id), `respuesta` (forma según el tipo) | `ok`; con retro también `puntos`, `max`, `fraccion` | `estudiante.js` `tarjetaPregunta()` | 400 intento terminado, reto cerrado, tiempo vencido, pregunta desconocida o no visible, ya respondida, falta la parte requerida, formato no válido |
| POST | `/api/finalizar` | Bearer | `{}` | `ok` | `estudiante.js` `mapa()` (botón «Entregar mi reto») | 401 |
| POST | `/api/evento` | Bearer | `tipo` (`"salida"`) | `ok` | `estudiante.js` `visibilitychange` | 401 |

**Forma de `misiones[]` en `/api/estado`** (`examen_publico`, `version_publica`): cada misión trae
`id`, `titulo`, `subtitulo`, `intro`, `glosario`, `lectura`, `dossier` (o `{titulo, bloqueado: true, n}`
mientras la hipótesis no esté registrada), `preguntas[]` y `puntos`. Cada pregunta pública trae solo
las claves de una lista blanca: `id`, `tipo`, `enunciado`, `puntos`, `unidad`, `min`, `max`, `paso`,
`grafico`, `tabla`, `categorias`, `estilo`, `requiere`, `experimento`, `entero`, `simulador`, más
`opciones`, `items`, `partes` o `publicaciones` barajados por participante. Nunca `respuesta`,
`explicacion` ni `tolerancia` (lo comprueba `simulacro.py`, paso 2).

**Forma de `respuesta` en `/api/responder`** (`validar_respuesta`):

| Tipo de pregunta | Forma esperada |
|---|---|
| `opcion` | texto: id de una opción |
| `multiple` | lista de ids distintos de opciones |
| `clasificar`, `compartir`, `recordatorio` | objeto {id de ítem o publicación: id de categoría} con todos los ítems |
| `ordenar` | lista con todos los ids de ítems en orden |
| `construir` | objeto {id de parte: id de opción} con todas las partes |
| `texto` | texto no vacío de hasta `max` + 50 caracteres |
| `estimar`, `numero` | número o texto numérico (coma o punto decimal; `a_numero`); `estimar` debe quedar entre `min` y `max` |

### Tablero (público)

| Método | Ruta | Autenticación | Respuesta (claves JSON) | Llamada desde |
|---|---|---|---|---|
| GET | `/api/publico` | ninguna | `evento`, `titulo`, `estado`, `sala`, `urls`, `duracion_min`, `abierto_en`, `cerrado_en`, `servidor_ahora`, `modo_sorpresa`, `reloj_global`, `conteo` {`inscritos`, `en_curso`, `finalizados`}; `ranking[]` {`puesto`, `nombre`, `colegio`, `grado`, `total`, `puntos`} (top 10) si el estado es `resultados` o el modo sorpresa está apagado; `experimento` (ver abajo) si el estado es `cerrado` o `resultados` | `tablero.html` `sondear()` cada 2 s; también `modo_prueba.py`, `simulacro.py` y el `healthCheckPath` de `render.yaml` |

`experimento` (`servidor.py` `experimento`): `{n, listo: false}` con menos de 2 participantes
completos; si no, `n`, `listo`, `total_posts`, `clase`, `grupo_sin_recordatorio`,
`grupo_con_recordatorio` (cada uno con `n`, `comparte_falsas`, `comparte_verdaderas`, `cree_falsas`,
`cree_verdaderas`, `discernimiento_compartir`, `discernimiento_creer`), `multitud`
{`aciertos_multitud`, `promedio_individual`, `mejor_individual`, `pct_estudiantes_superados`} y
`por_publicacion[]` {`id`, `verdad`, `pct_cree_verdadera`, `pct_compartiria`, `multitud_acierta`, `texto`}.

### Docente

Todas exigen la clave docente; sin ella → 403 «Clave de docente incorrecta.» antes de mirar la ruta.

| Método | Ruta | Petición (claves JSON) | Respuesta | Llamada desde |
|---|---|---|---|---|
| POST | `/api/admin/login` | `{}` | `ok` | `admin.js` `login()` |
| GET | `/api/admin/resumen` | — | `config` {`estado`, `sala`, `modo_sorpresa`, `retro`, `duracion_min`, `evento`, `abierto_en`, `cerrado_en`, `reloj_global`} (valores como texto), `urls`, `banco` {`version`, `preguntas`, `puntos_totales`, `bono_max`}, `participantes[]` {`id`, `codigo`, `nombre`, `colegio`, `grado`, `integrantes`, `grupo`, `estado`, `respondidas`, `total_preguntas`, `puntos`, `bono`, `total`, `tiempo_usado`, `tiempo_respuestas`, `restante_seg`, `salidas`, `puesto`, `nota`, `motivo_fin`}, `experimento`, `servidor_ahora` | `admin.js` `refrescar()` cada 3 s |
| GET | `/api/admin/resultados.csv` | — | CSV `;` con BOM: puesto, código, nombre, colegio, grado, integrantes, estado, puntos, bono, total, nota, tiempos, salidas, motivo y puntos por pregunta | `admin.js` `descargar()` |
| GET | `/api/admin/respuestas.csv` | — | CSV `;` con BOM: una fila por respuesta (código, nombre, grupo, pregunta, variante, respuesta del estudiante, fracción, puntos, máximo, segundos desde el inicio) | `admin.js` `descargar()` |
| POST | `/api/admin/estado` | `estado` ∈ {`inscripcion`, `abierto`, `cerrado`, `resultados`} | `ok` | `admin.js` `actualizar()` → `cambiar(...)` |
| POST | `/api/admin/config` | cualquiera de `modo_sorpresa` (bool), `retro` (bool), `sala` (3-8 letras o números), `evento`, `reloj_global` (bool, solo en `inscripcion`), `duracion_min` (10-240, solo en `inscripcion`) | `ok` | `admin.js` `interruptor()`, `filaCfg()`; `modo_prueba.py` |
| POST | `/api/admin/participante` | `id`, `accion` ∈ {`descalificar`, `reactivar`, `finalizar`, `eliminar`} | `ok` | `admin.js` `actualizarTabla()` |
| POST | `/api/admin/reiniciar` | `confirmar` = `"BORRAR"` | `ok`, `copia` (nombre del archivo de copia) | `admin.js` `montar()` (zona de peligro) |

`web/js/` siempre usa la cabecera `X-Clave-Admin`; el parámetro `?clave=` no lo usa ningún cliente
del repositorio.

## Rutas que devuelven respuestas correctas y bajo qué condición

| Ruta | Dato | Condición en el código | ¿Cumple «solo tras publicar resultados»? |
|---|---|---|---|
| `GET /api/estado` | `revision.<pregunta_id>.respuesta` y `.explicacion` de cada pregunta visible | `cfg("estado") == "resultados"` y participante `finalizado` (`estado_participante`, líneas 408-415) | Sí |
| `GET /api/estado` | `respuestas.<id>.puntos`, `.fraccion` | Con `retro == "1"` (valor por defecto) durante el reto | No revela la clave, pero sí si la respuesta propia fue correcta o parcial (función de retroalimentación configurable) |
| `POST /api/responder` | `puntos`, `max`, `fraccion` | Con `retro == "1"` | Igual que la fila anterior |
| `GET /api/publico` | `experimento.por_publicacion[].verdad` (veredicto real de cada publicación del Exp. 01, que es la clave de `m1_veracidad`) y `multitud_acierta` | Estado `cerrado` **o** `resultados` (`publico`, líneas 433-434) | **No**: sin autenticación y ya en `cerrado`, antes de publicar. Nadie puede responder en `cerrado`, pero el dato sale antes de lo que dice el invariante |
| `GET /api/admin/resumen` | `experimento.por_publicacion[].verdad` | Cualquier estado, con clave docente | Ruta del docente; no llega a estudiantes |
| `GET /api/admin/respuestas.csv` / `resultados.csv` | Respuesta del estudiante, fracción y puntos por pregunta | Cualquier estado, con clave docente | Ruta del docente |
| `GET /api/estado` → `misiones[]` | Los ids de `opciones`, `items` y `partes` | Siempre, durante el reto | **Riesgo indirecto**: los ids se asignan por la posición en la lista de autoría de `construir_banco.py` y ese orden se correlaciona con la clave (ver `code-quality-assessment.md`) |

## Clientes por archivo

| Archivo | Rutas que llama |
|---|---|
| `web/js/estudiante.js` | `/api/registro`, `/api/entrar`, `/api/estado`, `/api/comenzar`, `/api/responder`, `/api/finalizar`, `/api/evento` |
| `web/js/admin.js` | `/api/admin/login`, `/api/admin/resumen`, `/api/admin/estado`, `/api/admin/config`, `/api/admin/participante`, `/api/admin/reiniciar`, `/api/admin/resultados.csv`, `/api/admin/respuestas.csv` |
| `web/tablero.html` | `/api/publico` |
| `web/js/graficos.js` | ninguna (dibuja lo que recibe) |
| `pruebas/simulacro.py` | todas las rutas de API menos `/api/admin/login` y `/api/evento` |
| `modo_prueba.py` | `/api/admin/config`, `/api/admin/estado`, `/api/publico` |
