# Decisiones de diseño del dominio

Registro de decisiones de arquitectura (ADR) de Domain Design. Cada una sale de una respuesta tuya en
`domain-design-questions.md`. La decisión del hosting no está aquí: va en el ADR de NFR Design.

## ADR-001: Partir `servidor.py` en pocos módulos por capa

- **Context** — `servidor.py` tiene 913 líneas que mezclan reglas, SQL, reloj y HTTP
  (`codekb/.../code-structure.md`, «Mapa de secciones de `servidor.py`»). Con varias salas (FR11), el
  paquete de datos (FR9) y la limpieza de entrada (FR10), el archivo crece. FR7.1 pide separar el núcleo
  puro de la E/S. Cada PR tiene un máximo de 400 líneas (`team.md`, «Corrections»).
- **Decision** — Q1-A. Se arma un núcleo puro (`nucleo/`, un módulo por decisión: banco, calificación,
  clasificación, ciclo de sala, limpieza, experimento). Los servicios (salas, catálogo, acceso,
  inscripción, examen, resultados), la persistencia, la exportación, la API HTTP y el arranque van
  aparte. Los 20 componentes de `components.md` son bloques lógicos; Units Generation decide cómo se
  agrupan en archivos y PR.
- **Consequences** — A favor: el núcleo se prueba con `unittest` sin servidor ni base (NFR12), y cada
  módulo cabe en un PR. En contra: hay que mover código en varios PR y `simulacro.py`, que hoy importa
  `servidor` como módulo, tiene que seguir funcionando (FR11.7). Ese cuidado se planifica en Units
  Generation.
- **Alternatives Rejected** — Un archivo por componente (Q1-B): unos 20 archivos para un servidor
  pequeño, con más importaciones cruzadas. Un solo `servidor.py` ordenado (Q1-C): no cumple FR7.1.

## ADR-002: Catálogo único de colegios del semillero

- **Context** — La lista cerrada de colegios (FR10.3) existe para que los datos lleguen limpios. Si cada
  sala escribe su propia lista, el mismo colegio puede quedar con nombres distintos entre retos, y unir
  los datos de varios años exige limpiar a mano (FR9).
- **Decision** — Q2-A. El componente CatalogoColegios mantiene una lista única con un `id_colegio`
  estable. La clave general del semillero agrega o corrige colegios; un nombre que, normalizado, ya
  existe se rechaza como duplicado. Cada sala elige del catálogo los colegios que participan, y el
  participante guarda el `id_colegio`.
- **Consequences** — A favor: el mismo colegio tiene el mismo identificador en todos los retos y años,
  así que los paquetes de datos se unen sin limpieza. En contra: antes del reto alguien del semillero
  tiene que tener el colegio en el catálogo. Qué pasa si el día del reto falta uno sigue abierto (OQ7) y
  se decide en Functional Design.
- **Alternatives Rejected** — Lista propia de cada sala (Q2-B): vuelve a ensuciar los datos entre
  retos. Catálogo con altas desde la sala (Q2-C): cada docente podría crear duplicados con otra
  ortografía.

## ADR-003: Clave de sala generada por el servidor y regenerable

- **Context** — Cada sala tiene su clave docente y la clave general del semillero crea las salas
  (FR11.5). NFR9 pide comparar en tiempo constante, que la clave viaje solo en la cabecera
  `X-Clave-Admin` y que tenga al menos 12 caracteres.
- **Decision** — Q3-C. Al crear la sala, el servidor genera una clave larga y aleatoria, la muestra una
  sola vez y guarda solo su huella (`clave_huella` en Sala). Con la clave general, el semillero puede
  regenerarla, y desde ese momento la anterior deja de servir. Acceso verifica toda clave y una clave de
  sala nunca abre otra sala.
- **Consequences** — A favor: no hay claves débiles escritas a mano, y una clave filtrada o perdida se
  reemplaza sin tocar la sala ni sus datos. Como solo se guarda la huella, el paquete de datos tampoco
  puede filtrar la clave (FR9.5). En contra: el docente no puede recuperar una clave perdida, solo
  pedir una nueva. Cómo se calcula la huella se fija en Functional Design.
- **Alternatives Rejected** — Generada y mostrada una vez, sin regenerar (Q3-A): una clave perdida
  deja la sala sin dueño. Escrita por el semillero (Q3-B): claves más fáciles de adivinar.

## ADR-004: El tiempo vence al consultar, sin hilo vigilante

- **Context** — Hoy un hilo `vigilante` revisa cada 3 s los intentos vencidos (`servidor.py`,
  `vigilante`). Con varias salas, y en hostings que duermen la instancia o no permiten hilos, ese hilo
  no sirve. `finalizar` ya pone la hora de entrega en el vencimiento exacto,
  `fin = min(ahora, inicio + duración)`, y el bono se mide con la última respuesta.
- **Decision** — Q4-A y Q7-A. CicloDeSala decide con la hora del servidor, que recibe como argumento,
  si un intento venció y cuál es su hora de entrega. Examen y Resultados aplican el vencimiento antes de
  responder cualquier petición que toque esa sala. FR3.2 se reescribió para decir eso: toda consulta ve
  como entregados los intentos vencidos, con la hora de entrega igual al vencimiento.
- **Consequences** — A favor: funciona en cualquier hosting; el reloj se prueba sin esperar; puntos,
  bono, clasificación y CSV salen iguales que hoy. En contra: la fila en la base se escribe cuando
  alguien consulta, no a los 3 s. Nadie lo nota desde fuera, porque toda lectura aplica primero el
  vencimiento; las vistas que leen la base sin pasar por el servicio deben hacer lo mismo.
- **Alternatives Rejected** — Mantener el hilo (Q4-B): limita los hostings posibles. Hilo más
  temporizador del hosting (Q4-C): dos caminos para la misma regla sin ganar nada que se vea.

## ADR-005: El dominio exige la sala en cada dato; la forma del almacén la decide el ADR

- **Context** — Cada sala se descarga, se reinicia y se borra sin tocar las demás (FR11.6, NFR10.1). La
  forma natural del almacén depende del hosting, que todavía no se elige: un almacén por sala en
  Cloudflare, una base con columna de sala en Render.
- **Decision** — Q5-C. Cada Participante pertenece a una Sala, y su Intento, sus Respuestas y sus
  Eventos cuelgan de él. Toda operación de Persistencia recibe la sala. El ADR del hosting elige entre
  una base con columna de sala y un almacén por sala. El puerto de persistencia se crea solo si ese ADR
  trae una segunda implementación real (FR7.3).
- **Consequences** — A favor: no se fija una decisión de infraestructura antes de tener la evidencia de
  cuotas y latencias (NFR6). En contra: Functional Design no puede cerrar el esquema físico hasta el
  ADR. Se acepta, porque el ADR llega antes de Code Generation.
- **Alternatives Rejected** — Una base con columna de sala fijada desde ya (Q5-A) y un almacén por sala
  fijado desde ya (Q5-B): las dos atan el dominio a un hosting antes de evaluarlo.

## ADR-006: Ids opacos derivados de la semilla del participante

- **Context** — Hoy los identificadores de opciones, ítems y partes siguen el orden en que se escribió
  el banco, y de ahí se puede deducir la respuesta (FR6.2). La base y los CSV deben seguir usando los
  ids del banco (FR9.2).
- **Decision** — Q6-A. Banco deriva los ids opacos con una función pura a partir de la semilla secreta
  del participante y del id de la pregunta, y traduce de vuelta al calificar. No se guarda ninguna tabla
  nueva.
- **Consequences** — A favor: no hay datos nuevos que respaldar ni borrar, y la traducción se prueba
  sin base. Para el navegador cada participante ve ids distintos. En contra: la semilla tiene que seguir
  siendo secreta. Hoy ya lo es, porque nunca sale al navegador. La función tiene que ser estable entre
  versiones de la app mientras haya un reto en curso; como no se despliega con un reto en curso
  (`project.md`, «Forbidden»), eso ya está cubierto.
- **Alternatives Rejected** — Ids al azar guardados en la base (Q6-B): una tabla más que respaldar y
  borrar, sin una ventaja que se vea.

## ADR-007: Intento separado de Participante

- **Context** — Hoy la tabla `participantes` mezcla quién es la persona (nombre, colegio, grado) con lo
  que pasa en el reto (inicio, entrega, puntos, bono). Si dos componentes escriben la misma entidad, no
  queda claro quién es su dueño.
- **Decision** — Inscripcion es dueña de Participante y Examen es dueño de Intento, con identificador
  `participante_id`. Es una decisión lógica: si la base sigue con una tabla o pasa a dos se decide en
  Functional Design, sin cambiar las claves JSON ni las columnas de los CSV de hoy (FR4.3).
- **Consequences** — A favor: cada bloque escribe solo lo suyo y la limpieza de entrada no se mezcla
  con el cálculo de puntos. En contra: las vistas tienen que juntar las dos para mostrar el ranking.
- **Alternatives Rejected** — Un solo dueño, Inscripcion, para todo: Examen tendría que escribir datos
  ajenos, que es el olor de diseño que esta etapa pide evitar.

## ADR-008: Adoptar ruff como formateador y linter de Python (reabre Q5-D)

- **Context** — En Practices Discovery (Q5-D) el equipo decidió no usar linter ni formateador y revisar
  el estilo a mano en el PR. El 2026-10-25 el humano reabrió esa decisión: una regla revisada a mano no
  se puede comprobar con herramienta, y `.claude/rules/python-code.md` debe tener solo líneas
  comprobables.
- **Decision** — Ruff 0.17.0 formatea y revisa el Python. Va en el grupo `dev` de `pyproject.toml` y en
  `.pre-commit-config.yaml` con la misma versión, y su configuración (`[tool.ruff]`) es la fuente del
  estilo. Entra así:
  - Un PR de solo formato, «style: aplicar ruff format», con todo el Python actual. Queda exento del
    límite de 400 líneas porque no cambia la conducta. Lo prueban `ruff format --check`, la suite
    `unittest` y `pruebas/simulacro.py 40` en «TODO BIEN». Su commit se anota en `.git-blame-ignore-revs`.
  - En ese PR, las faltas que el código ya tenía quedan marcadas con `# noqa: <código>` en su línea
    (`ruff check --add-noqa`), sin cambiar la lógica.
  - `D`, `ANN` y `N` se ignoran por archivo en el código viejo (`servidor.py`, `simulacro.py`,
    `modo_prueba.py`, `iniciar_internet.py` y los scripts de datos). `E`, `W`, `F`, `B`, `BLE`, `S110` y
    `S608` corren sobre todo desde ya. Cada archivo sale de `per-file-ignores` en el PR que lo refactoriza.
- **Consequences** — A favor: el estilo se comprueba solo, en local y en la revisión de PR, y el
  código nuevo cumple las reglas desde el primer commit. En contra: una dependencia de desarrollo más,
  un PR grande de formato que se revisa con `git diff -w`, y `noqa` temporales en el código viejo.
  Se miden con `grep -rc "# noqa" --include=*.py .`. Son 86 líneas con 88 códigos, contados después
  del segundo `ruff format`; el conteo de 81 era anterior a ese paso.

| Archivo | Líneas con `noqa` | Códigos |
|---|---|---|
| `4_Codigo_y_datos/scripts/construir_banco.py` | 61 | `E501` ×55, `PLR0913` ×3, `F541` ×2, `B905`, `C901` |
| `2_Aplicacion_Reto/servidor.py` | 10 | `C901` ×3, `BLE001` ×3, `B904` ×2, `B007`, `E731` |
| `4_Codigo_y_datos/scripts/generar_analisis.py` | 9 | `E501` ×7, `B905`, `I001` |
| `2_Aplicacion_Reto/pruebas/simulacro.py` | 3 | `C901` ×2, `S608` |
| `2_Aplicacion_Reto/iniciar_internet.py` | 2 | `BLE001` ×2, `S110` |
| `4_Codigo_y_datos/scripts/estilo_graficos.py` | 1 | `B905` |

- **Deuda que no es de estilo** (se corrige en el PR que refactoriza cada archivo, con su prueba):
  - `S110` en `iniciar_internet.py`: un `except Exception: pass` se traga el error sin decir nada.
  - `B904` ×2 en `servidor.py` (`ErrorAPI` de respuesta mal formada y de JSON no válido): el `raise`
    dentro del `except` pierde la causa original; va con `from`.
  - `S608` en `simulacro.py`: arma el SQL con una f-string. Hoy solo interpola marcadores `?`, así
    que no hay inyección, pero el patrón queda marcado.
  - `BLE001` ×5 y `B905` ×3: capturas de `Exception` sin decidir nada y `zip` sin `strict=`; se
    revisan caso por caso (`strict=` solo existe desde 3.10, así que no aplica en `2_Aplicacion_Reto/`).
- **Alternatives Rejected** — Seguir revisando a mano: no se puede comprobar con herramienta. Excluir
  el código viejo con `extend-exclude`: dejaba archivos enteros sin revisar, incluso para errores
  reales (`F`, `B`). Formatear cada archivo cuando se toque: mezcla formato y lógica en el mismo PR y
  lo hace difícil de revisar.
