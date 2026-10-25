# Evaluación de calidad del código

Commit `99462c96268e29bde1738af0b4817d96df9a3989`. Análisis estático por lectura; no se ejecutó ninguna
prueba ni programa del proyecto. Los números de línea se refieren a `2_Aplicacion_Reto/servidor.py`
salvo que se indique otro archivo.

## Resumen

| Aspecto | Valoración | Comentario |
|---|---|---|
| Claridad de nombres | Buena | Español consistente, nombres de dominio (`finalizar`, `clasificacion`, `vencer_tiempos`) |
| Tamaño de funciones | Regular | La mayoría es corta; `do_POST` (65 líneas, más de 20 ramas), `estado_participante`, `experimento` y `version_publica` superan con holgura una complejidad ciclomática de 10 |
| Manejo de errores | Regular | `ErrorAPI` con código HTTP y un `try` amplio en el borde HTTP; pero validación con `assert`, `ValueError` sin capturar que terminan en 500 y `except Exception: pass` en `iniciar_internet.py` |
| Presencia de pruebas | Regular | Una prueba de aceptación de extremo a extremo muy completa; ninguna prueba unitaria |
| Duplicación | Regular | Helpers repetidos entre JS y Python y entre scripts (detalle abajo) |
| Código muerto | Buena | Sin bloques comentados ni marcas TODO/FIXME/HACK; solo un `"max"` repetido en una tupla |

## Pruebas existentes

| Elemento | Estado |
|---|---|
| `2_Aplicacion_Reto/pruebas/simulacro.py` | Prueba de aceptación por HTTP contra un servidor real (puerto 8765, BD temporal). 29 comprobaciones agrupadas en 7 bloques: inscripción, respuestas, reloj global, tiempo, calificación (1.000 y 0 puntos, bono), clasificación (puestos 1..N), revisión/experimento/CSV y reinicio. `LEEME.md` y `METODOLOGIA…md` §4.5 dicen 27 |
| Lo que comprueba del invariante de respuestas | Que el JSON de `misiones` de `/api/estado` no contenga las cadenas `"respuesta"`, `"explicacion"`, `"tolerancia"` ni `revision` durante el reto (paso 2) |
| Lo que **no** comprueba | `/api/publico` en estado `cerrado`; la relación entre ids públicos y claves; transiciones de estado inválidas; entradas malformadas que producen 500; concurrencia real |
| Pruebas unitarias | No existen. `unittest` es el marco aprobado para pruebas nuevas (`aidlc/spaces/default/memory/project.md`) |
| Cobertura | Sin configuración ni medición |
| Ejecución | Manual o por lanzadores (`PROBAR_ANTES_DEL_RETO.*`, `REGENERAR_TODO.*`); sin CI |
| Determinismo | `random.seed(7)` fija las respuestas simuladas, pero los tokens, códigos y semillas del servidor son aleatorios (`secrets`), así que la prueba no es reproducible bit a bit |

## Mezcla de lógica pura con E/S

La regla del proyecto pide «núcleo funcional, E/S en los bordes» (`.claude/rules/python-code.md`,
«Diseño y patrones»). Hoy la lógica de dominio lee directamente el global `DB`, la configuración
(`cfg`) y el reloj (`time.time()`):

| Función (líneas) | Lógica pura que contiene | E/S que mezcla | Qué separar |
|---|---|---|---|
| `a_numero`, `validar_respuesta`, `fraccion` (177-257) | Lectura de números, validación de forma, crédito parcial por tipo | Ninguna | Ya son puras; falta sacarlas del módulo con efectos al importar y reemplazar `assert` |
| `rng_para`, `variante_de`, `resolver`, `version_publica`, `examen_publico` (103-173) | Variantes, barajado, filtrado de claves públicas, bloqueo del dossier | Leen el global `BANCO` | Recibir el banco como parámetro |
| `finalizar` (273-290) | Fórmula del bono y de los tiempos usados | Consulta `MAX(momento)`, `recalcular_puntos` (SQL), `duracion_seg()` (SQL), `UPDATE` | Función pura `calcular_cierre(inicio, ahora, duracion, ultima, puntos)` + escritura aparte |
| `vencer_tiempos` (293-297) | Predicado «intento vencido» | `time.time()`, `SELECT`, `duracion_seg()` por cada participante | Recibir `ahora`, `duracion` y la lista |
| `clasificacion` (300-314) | Orden total de 5 criterios y nota 1-5 | `SELECT … WHERE estado='finalizado'` | Función pura sobre filas; `puesto_de` la recalcula entera por participante |
| `experimento` (325-374) | Tasas, discernimiento, «sabiduría de la multitud» | `JOIN` de respuestas y participantes | Función pura sobre respuestas ya leídas |
| `estado_participante`, `publico`, `resumen_admin` (378-460) | Qué se muestra según estado y opciones (incluida la regla de cuándo hay `revision`) | Varias consultas SQL, `cfg`, `time.time()` | Separar la regla de visibilidad (pura y probable) de la lectura |
| `registrar`, `comenzar`, `responder`, `cambiar_estado`, `accion_participante`, `reiniciar` (520-652) | Reglas de inscripción, reloj global, orden de fases, una respuesta por pregunta, efectos de cada transición | SQL intercalado con cada regla; `time.sleep` en `entrar` | Devolver «decisión + cambios» desde una función pura y aplicar los cambios en la capa de persistencia |
| `Manejador.do_POST` → `/api/admin/config` (755-773) | Validación de sala, límites de duración, regla «solo antes de abrir» | `set_cfg` en línea dentro del manejador HTTP | Mover a una función de acción como las demás |
| `main` (852-908) | Selección de URLs públicas | Argumentos, archivos, red, hilos y globals | Mantener como borde |

Consecuencias observables: `simulacro.py` debe alterar la BD (`UPDATE participantes SET inicio = inicio - 6000`)
para probar el vencimiento, e importar `servidor` exige que exista `banco_preguntas.json`.

## Enrutamiento por cadenas de `if`

- `do_GET` (702-735) y `do_POST` (737-802) comparan `url.path` en secuencia: 5 rutas GET de API, 11
  POST, más páginas y estáticos.
- La autorización está mezclada con el orden: en `do_POST`, todo lo que no sea `registro`, `entrar` ni
  `/api/admin/*` exige token **antes** de saber si la ruta existe (una ruta desconocida da 401, no 404).
- El método no forma parte de la clave: `GET /api/registro` da 404 por caída al final, no 405.
- Las rutas `/api/admin/*` tienen dos respuestas de éxito distintas (`return self.enviar(...)` en
  algunas ramas, `{"ok": True}` común al final en otras).
- La regla del proyecto propone un `dict` de ruta a función (`.claude/rules/python-code.md`,
  «Complejidad, no longitud»). La autorización (`público`, `estudiante`, `docente`) puede ser un dato
  de cada entrada.

## Estado global en memoria

| Global | Definido | Mutado | Riesgo |
|---|---|---|---|
| `BANCO`, `PREGUNTAS`, `PUNTOS_TOTALES`, `BONO_MAX` | Al importar (45-48) | Nunca | Importar el módulo lee un archivo; no se puede cargar otro banco en pruebas sin tocar el archivo |
| `DB` | `None` (51) | `main()` vía `global` | Toda función de dominio depende de que `main()` ya haya corrido |
| `CLAVE_ADMIN`, `URLS`, `RUTA_DB` | Vacíos (52-54) | `main()` vía `global` | Igual |
| `LOCK` | `threading.RLock()` (50) | — | Serializa toda la API en un proceso; no protege nada entre procesos o instancias |
| Hilo `vigilante` | `main()` | Bucle infinito cada 3 s | Solo una instancia debe vencer tiempos; con dos, ambas escribirían |
| Conexión SQLite compartida entre hilos (`check_same_thread=False`, `isolation_level=None`) | `conectar` | — | Segura solo porque el `LOCK` serializa; las escrituras de varias sentencias (`finalizar`, `reiniciar`) no son transaccionales |

## Hallazgos de confidencialidad y seguridad

| # | Hallazgo | Evidencia | Severidad |
|---|---|---|---|
| S1 | **Ids públicos correlacionados con la clave.** Los ids de opciones (`a`, `b`, …), de ítems (`p1`…, `e1`…, `v1`…, `<qid>_1`…) y de partes se asignan por la posición en la lista de autoría. En el banco actual, ese orden se correlaciona fuertemente con la respuesta en las preguntas de opción única, en las partes de `construir` y en la mayoría de las de `clasificar` (verificado con un script sobre `banco_preguntas.json`; no se reproducen conteos ni claves). El barajado cambia el orden visual, pero los ids viajan en el JSON de `/api/estado` y se ven en las herramientas del navegador | `construir_banco.py` `opciones` (línea 130), `mision_compartir` (234), `mision_detectives` (324, 332), `q_evaluar` (171), `q_construir` (188); `servidor.py` `version_publica` (127-158) | Alta: debilita el invariante «las respuestas nunca salen al navegador» |
| S2 | **`/api/publico` revela el veredicto del Exp. 01 antes de publicar.** Con el estado `cerrado` ya incluye `experimento.por_publicacion[].verdad` y `multitud_acierta`, sin autenticación. En `cerrado` nadie puede responder, pero contradice la letra del invariante y la ruta está abierta a internet | `publico` (433-434), `experimento` (359) | Media |
| S3 | **`time.sleep(0,6)` dentro del lock global.** Cada código incorrecto en `/api/entrar` congela todas las peticiones de API 0,6 s; varios intentos seguidos degradan a toda la clase | `entrar` (550) dentro de `with LOCK` (742) | Media (disponibilidad) |
| S4 | **Validación con `assert`.** `validar_respuesta` usa `assert`; con `python -O` desaparece la validación y respuestas malformadas llegan a `fraccion` | 196-225; regla «`assert` no valida entradas» de `.claude/rules/python-code.md` | Media |
| S5 | **Sin validación de transiciones.** `POST /api/admin/estado` acepta cualquier estado desde cualquier otro (por ejemplo `resultados` → `abierto`, que reabre respuestas después de mostrar la revisión) | `cambiar_estado` (607-619) | Media (error del docente) |
| S6 | **Clave docente por URL.** `es_admin` acepta `?clave=`; en un hosting la URL puede quedar en registros de proxies e historial. Ningún cliente del repo la usa | 698 | Baja |
| S7 | **Sin límite de intentos para la clave docente.** Comparación en tiempo constante, pero sin espera ni bloqueo; la clave autogenerada tiene 6 caracteres de un alfabeto de 32 | `es_admin`, `main` (875) | Media en internet, baja en LAN |
| S8 | **El panel no está restringido a localhost.** `LEEME.md` dice que «siempre se abre desde el computador del docente», pero `/admin` y `/api/admin/*` responden a cualquiera que tenga la clave | `PAGINAS`, `do_GET`/`do_POST` | Baja (la clave protege), relevante en la nube |
| S9 | **Datos de menores en una ruta pública.** `/api/publico` publica `nombre`, `colegio` y `grado` del top 10 sin autenticación cuando hay resultados o el modo sorpresa está apagado | `publico` (430-432); `GUIA_DOCENTE.md` §10 | Media en internet |
| S10 | **HTTP sin cifrar en la red local.** La clave docente y los tokens viajan en claro por el wifi del colegio | `ThreadingHTTPServer` sin TLS | Baja (contexto de aula) |
| S11 | **Inyección de fórmulas en CSV.** Nombres o respuestas que empiecen con `=`, `+`, `-` o `@` se exportan tal cual y Excel podría evaluarlos | `csv_resultados`, `csv_respuestas` | Baja |
| S12 | **Binario externo sin verificar.** `iniciar_internet.py` descarga `cloudflared` `latest` y lo ejecuta sin suma de verificación | `buscar_cloudflared` | Baja |
| S13 | **Archivos locales que podrían subirse.** `.herramientas/` (cloudflared) y `python/` (Python embebido que busca `INICIAR_RETO_INTERNET.bat`) no están en `.gitignore` ni en `.dockerignore` | `.gitignore`, `.dockerignore` | Baja |

Retroalimentación inmediata: con `retro == "1"` (valor por defecto, `inicializar_config`), `/api/responder`
y `/api/estado` devuelven la fracción de acierto de cada respuesta propia durante el reto. No revela la
clave, pero sí si se acertó; es una opción documentada del docente.

## Riesgos para publicar en la nube

| Riesgo | Por qué en este código | Alcance |
|---|---|---|
| **Instancia que se duerme** | El reloj se guarda como hora absoluta (`inicio`, `abierto_en`), así que una pausa no lo detiene; al volver, la primera petición o el vigilante entregan lo vencido. Pero mientras duerme no hay vencimiento, y el despertar tarda: el tablero y los estudiantes ven errores de red (`estudiante.js` muestra «Sin conexión») | Planes gratuitos o servicios que escalan a cero |
| **Disco efímero** | Sin `RETO_DATOS` en un volumen persistente, `reto.db` y `clave_docente.txt` se pierden en cada reinicio o despliegue (`PUBLICAR_EN_INTERNET.md`: «el plan gratis… borra la base de datos al reiniciar») | Cualquier contenedor sin disco |
| **Reinicios y despliegues** | Un despliegue reinicia el proceso; la BD sobrevive si está en disco, pero las peticiones en vuelo fallan y `banco_preguntas.json` nuevo cambia preguntas con el reto en curso (prohibido por `LEEME.md`) | Render y similares |
| **Una sola instancia** | `LOCK`, vigilante y conexión SQLite son del proceso; dos réplicas tendrían dos BD (disco por instancia) o dos escritores sin coordinación, y puestos o tiempos inconsistentes | Cualquier autoescalado o despliegue sin corte |
| **Modelo de proceso largo** | `http.server` + hilo de fondo necesitan un proceso Python persistente; no corre en plataformas por petición (Cloudflare Workers, Apps Script) sin reescribir el borde HTTP, el vigilante (alarma o cron) y la persistencia | Workers + D1 + Durable Object; Apps Script + Sheets |
| **Persistencia no SQLite** | Las reglas dependen de la PK `(participante_id, pregunta_id)` para «una sola vez», de `COUNT(*)` para alternar grupos y de lecturas consistentes para el orden total; un almacén sin transacciones (hojas de cálculo) necesita otro mecanismo de exclusión | Apps Script + Sheets |
| **Carga por sondeo** | Cada estudiante consulta `/api/estado` cada 20 s (en curso) o 4 s (esperando o entregado), el tablero cada 2 s y el panel cada 3 s; cada petición recorre `vencer_tiempos` y varias recalculan la clasificación completa (`puesto_de` llama a `clasificacion` por estudiante) | Plataformas que cobran por petición o por tiempo de CPU |
| **Chequeo de salud costoso** | `healthCheckPath: /api/publico` toma el lock, vence tiempos y calcula clasificación y experimento | Render |
| **Reloj del servidor** | Todo usa `time.time()` del proceso; en varias máquinas o funciones sin estado, el reloj de referencia debe ser único | Arquitecturas distribuidas |
| **URLs mostradas** | Con `RETO_HOSTING`/`RENDER` solo se muestra la URL pública (`main`, 879-883); otro hosting necesita `RETO_URL_PUBLICA` | Cualquier hosting nuevo |

## Deuda técnica

- **Archivo dios**: `servidor.py` reúne nueve responsabilidades en 913 líneas (ver `code-structure.md`).
- **Errores 500 evitables**: `int(d["duracion_min"])` (773), `int(d.get("id", 0))` (623) y un
  `Content-Length` no numérico (685) lanzan `ValueError` que acaba como 500. Un `Content-Length`
  negativo hace `rfile.read(-1)`, que espera al cierre de la conexión con el hilo ocupado (fuera del lock).
- **Escrituras no atómicas**: `finalizar` y `reiniciar` hacen varias sentencias en autocommit; un
  fallo a mitad deja estados intermedios.
- **Reactivación frágil**: `accion_participante` recupera el estado previo leyendo el texto de
  `motivo_fin` con una expresión regular (631).
- **Duplicación**: `h()` y `num()` en `estudiante.js` y `admin.js`; `aNumero` (JS) replica `a_numero`
  (Python); `num()` en `construir_banco.py`, `generar_analisis.py` y `generar_clave_respuestas.py`;
  `ELECCIONES` en `construir_banco.py` y `generar_analisis.py`; `MESES` en `construir_banco.py` y
  `estilo_graficos.py`.
- **Errores silenciados**: `log_message` no registra nada; `iniciar_internet.py` `mantener_despierto`
  hace `except Exception: pass`.
- **Sin tipos ni docstrings de función** en la mayor parte del código (reconocido en
  `.claude/rules/python-code.md`, «Estado actual»).
- **Finales de línea**: `INICIAR_RETO_INTERNET.bat` está modificado en el árbol de trabajo con LF en
  lugar de CRLF (mismo texto); `.gitattributes` exige CRLF para `.bat`.
- **Limpieza menor**: `"max"` aparece dos veces en la tupla de `version_publica` (130-131).

## Documentación

| Documento | Calidad | Desajustes con el código |
|---|---|---|
| `README.md`, `2_Aplicacion_Reto/LEEME.md`, `GUIA_DOCENTE.md` | Clara y orientada a docentes | `LEEME.md` y `METODOLOGIA…md` dicen 27 comprobaciones; hay 29. `LEEME.md` dice que el panel «siempre se abre desde el computador del docente»; el servidor no lo restringe |
| `PUBLICAR_EN_INTERNET.md` | Paso a paso sin comandos | Dice que el servidor «lleva el reloj y la clasificación en memoria»; ambos salen de SQLite (ver `architecture.md`). Describe `INICIAR_RETO_INTERNET` como «solo Mac», pero existe la versión `.bat` con `iniciar_internet.py` |
| Docstrings de módulo | Presentes en todos los `.py` | — |
| `METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md` | Detallada, con limitaciones declaradas | — |

## Linting y CI/CD

- No hay formateador, linter, verificador de tipos ni configuración de cobertura.
- No hay pipeline de CI: `simulacro.py` se corre a mano. El piso de 80 % de cobertura de líneas y la
  ejecución en CI del alcance `classic` (`aidlc/spaces/default/memory/org.md`, «Testing Posture») no
  tienen hoy infraestructura que los mida.
