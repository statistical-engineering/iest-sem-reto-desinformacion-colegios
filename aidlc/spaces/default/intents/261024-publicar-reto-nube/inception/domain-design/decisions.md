# Decisiones de diseño del dominio

Registro de decisiones de arquitectura (ADR) de Domain Design. Cada ADR compara al menos tres
alternativas con su costo y fue aprobado por el humano el 2026-10-25. Valen para cada versión de la nube
(FR12.2); la versión local (`2_Aplicacion_Reto/`) no cambia. Lo propio de cada plataforma va en el ADR de
cada opción (FR12.2b).

## ADR-001: Cómo se separan las reglas del reto en cada versión

**Estado:** aprobado por el humano (2026-10-25). Reemplaza la versión
anterior («Partir `servidor.py` en pocos módulos por capa», Q1-A). Esa versión daba por hecho el núcleo
puro de FR7.1, y FR7.1 se reescribió porque venía del pedido inicial y no de una necesidad del problema.

- **Context** — Cada versión de la nube (FR12.2) da los mismos resultados que la versión local con las
  mismas respuestas: puntos, bono, desempates, vencimiento, limpieza de la inscripción y transiciones de
  estado (NFR11, FR5.5). Además, tiene pruebas de esas reglas que corren sin servidor ni base (FR7.1,
  FR10.5). Son dos lenguajes:
  - Python: Render, Cloudflare Containers y, probablemente, la API de GitHub Pages.
  - JavaScript: Workers y Apps Script.

  Varias reglas dependen de la hora (ADR-004), así que las pruebas tienen que poder fijarla. En
  `servidor.py` hay 9 funciones que ya son reglas puras: `fraccion`, `validar_respuesta`,
  `version_publica`, `examen_publico`, `variante_de`, `resolver`, `rng_para`, `a_numero` y `puesto_de`.
  Otras 6 mezclan regla con SQL o con la hora: `clasificacion`, `experimento`, `finalizar`,
  `vencer_tiempos`, `estado_participante` y la validación de `registrar`.

| | A. Reglas que reciben datos y la hora, y devuelven datos | B. Reglas junto a la base, probadas con una base de prueba | C. Copiar el servidor de hoy y probar solo por HTTP |
|---|---|---|---|
| Cómo es | Un módulo `reglas` por versión. La base y la red quedan alrededor y le pasan los datos y `ahora` | Cada servicio hace consulta + regla, como hoy. Las pruebas usan una base de prueba y un reloj falso | Python: `servidor.py` copiado tal cual. JS: reescrito directo. Solo la prueba común lo verifica |
| Costo de construir | Separar las 6 funciones mezcladas. Las 9 puras se copian | Bajo en Python. Alto en Apps Script: Sheets no tiene base de prueba y hay que simular la hoja | El más bajo |
| Costo de probar | Bajo: «estos datos y esta hora dan este resultado», igual en los dos lenguajes | Medio o alto: una base de prueba por plataforma, y cada desempate exige insertar filas | Alto: cada prueba exige desplegar, y el vencimiento exige esperar o abrir una ruta para mover el reloj (OQ3) |
| ¿Cumple FR7.1 y FR10.5? | Sí | Sí, con base de prueba | No |

- **Decision** — A, aplicada solo a las reglas de la lista. Es la única de las tres cuyo costo de
  prueba no depende del almacenamiento de cada plataforma: B se encarece justo en Apps Script, y C deja
  sin pruebas unitarias las reglas que más fallan (tiempo y desempates). Lo demás (catálogo, salas,
  exportación y panel) va directo contra la base de cada plataforma, sin capas extra.
- **Consequences** — A favor: los mismos casos de prueba de las reglas se escriben en Python y en JS.
  Si dos versiones difieren, la diferencia aparece en las pruebas y no el día del reto. En contra: cada
  carpeta lleva su propia copia de `reglas`, porque ninguna carpeta depende de otra (FR12.2). Durante la
  comparación puede haber hasta cinco copias; al final quedan dos, la ganadora y la de respaldo (FR12.6).
- **Alternatives Rejected** — B: su costo de prueba crece con cada plataforma, sobre todo con Sheets.
  C: no cumple FR7.1 ni FR10.5 y empuja a abrir una ruta para mover el reloj.
- **No decide** — Cómo se despachan las rutas ni si hay una capa de base de datos (FR7.2 y FR7.3).
  Eso va en el ADR de cada opción (FR12.2b), porque depende de la plataforma.

## ADR-002: Catálogo único de colegios del semillero

**Estado:** aprobado por el humano (2026-10-25). Revisa la versión anterior
(Q2-A) con la comparación de costos y resuelve el hallazgo R-06 de la primera revisión: quién elige los
colegios de cada sala y qué pasa si falta uno el día del reto (OQ7).

- **Context** — La lista cerrada de colegios (FR10.3) existe para que los datos lleguen limpios: que
  «IE San José» y «colegio san jose» no queden como dos colegios. Los paquetes de varios años se unen
  por el colegio (FR9.2). Aplica igual en las cinco versiones.

| | A. Un catálogo único del semillero | B. Una lista propia en cada sala | C. Un catálogo único al que cualquier docente agrega |
|---|---|---|---|
| Cómo es | El semillero mantiene la lista con un `id_colegio` fijo. Cada docente elige de ahí los colegios de su sala | Cada docente escribe la lista de su sala antes del reto | Un catálogo, pero el docente agrega colegios nuevos con su clave de sala |
| Costo de construir | Medio: el catálogo, más una pantalla del semillero y la elección en la sala | Bajo: un campo de texto por sala | Medio: igual que A, sin el paso del semillero |
| Costo en los datos | Ninguno: el mismo colegio tiene el mismo id siempre | Alto: el mismo colegio sale con nombres distintos entre retos y hay que limpiar a mano | Medio: cada docente puede crear un duplicado con otra ortografía |
| Si falta un colegio el día del reto | Ver la decisión | Lo escribe el docente | Lo agrega el docente |

- **Decision** — A, con una salida para el día del reto:
  - el semillero, con su clave, agrega y corrige colegios del catálogo, y un nombre que ya existe
    (normalizado) se rechaza;
  - el docente, con la clave de su sala, elige del catálogo los colegios de su sala;
  - si falta un colegio el día del reto, el docente lo agrega a su sala marcado **«provisional»**. El
    semillero después lo confirma o lo une con uno que ya existía, y el paquete de datos lleva el
    `id_colegio` definitivo.

  A gana porque es la única de las tres que no ensucia los datos entre retos, y unir los datos de varios
  años es el motivo de FR10.3. La salida «provisional» evita que el reto dependa de que alguien del
  semillero esté disponible ese día.
- **Consequences** — A favor: el mismo colegio tiene el mismo id en todos los retos y años. En contra:
  hay una pantalla más para el semillero y un paso para unir provisionales. FR10.3 decía «el docente
  carga la lista»: hay que ajustar esa frase en los requisitos para que diga esto.
- **Alternatives Rejected** — B: vuelve a ensuciar los datos, que es justo lo que FR10.3 quiere evitar.
  C: los duplicados entran sin que nadie los revise.

## ADR-003: Clave de sala generada por el servidor y regenerable

**Estado:** aprobado por el humano (2026-10-25). Revisa la versión anterior
(Q3-C) con la comparación de costos y con los dos tipos de clave de NFR9.

- **Context** — Hay dos claves (NFR9): la del semillero, que es un secreto del hosting, y la de cada
  sala, que tiene el docente. Las dos tienen al menos 12 caracteres, se comparan en tiempo constante y
  viajan solo en la cabecera `X-Clave-Admin`. Una clave de sala nunca abre otra sala (FR11.5). Aplica
  igual en las cinco versiones.

| | A. Generada por el servidor y regenerable | B. Generada por el servidor, sin regenerar | C. Escrita por el semillero al crear la sala |
|---|---|---|---|
| Cómo es | Al crear la sala, el servidor genera una clave aleatoria, la muestra una vez y guarda solo su huella. El semillero puede pedir una nueva | Igual que A, pero no se puede cambiar | El semillero inventa la clave y el servidor guarda su huella |
| Costo de construir | Bajo: generar, guardar la huella y una acción «regenerar» | El más bajo | Bajo, pero hay que validar que la clave sea fuerte |
| Riesgo | Bajo: una clave perdida o filtrada se reemplaza sin tocar la sala | Alto: una clave perdida deja la sala sin dueño a mitad del reto | Medio: las claves escritas a mano son más fáciles de adivinar |

- **Decision** — A. Es la única de las tres que resuelve una clave perdida o filtrada sin perder la sala
  ni sus datos, y cuesta casi lo mismo que B. Al regenerar, la clave anterior deja de servir en ese
  momento. Como solo se guarda la huella, ni la base ni el paquete de datos pueden filtrar la clave
  (FR9.5).
- **Consequences** — A favor: no hay claves débiles ni claves guardadas en texto plano. En contra: una
  clave perdida no se recupera, se pide otra al semillero. Los estudiantes nunca usan esta clave: usan
  el código de sala y su código personal, como hoy. El semillero entrega la clave al docente por un
  canal privado, y la guía del docente pide no compartirla en grupos ni proyectarla. Cómo se calcula la huella se fija en el ADR
  de cada opción.
- **Alternatives Rejected** — B: una clave perdida deja la sala sin dueño. C: las claves escritas a mano
  son más fáciles de adivinar.

## ADR-004: El tiempo vence al consultar, sin hilo vigilante

**Estado:** aprobado por el humano (2026-10-25). Revisa la versión anterior
(Q4-A, Q7-A) con la comparación de costos en las cinco plataformas, y resuelve los hallazgos R-01 (quién
entrega al cerrar la sala) y R-09 (que una entrega no pase dos veces).

- **Context** — Hoy un hilo `vigilante` revisa cada 3 s los intentos vencidos (`servidor.py`,
  `vigilante`), y `finalizar` pone la hora de entrega en `fin = min(ahora, inicio + duración)`. Al
  cerrar la sala, `cambiar_estado` entrega los intentos en curso con la hora del cierre y el motivo
  `cierre`, y pasa a `no_inicio` a quien nunca empezó. La hora de entrega es el 4.º criterio de desempate
  (FR2.3), así que tiene que salir exacta.

| | A. Vence al consultar | B. Un hilo que revisa cada pocos segundos (como hoy) | C. Un temporizador de cada plataforma |
|---|---|---|---|
| Cómo es | Antes de responder cualquier petición de una sala, se entregan los intentos que ya vencieron, con su hora exacta | Un proceso aparte revisa todo cada 3 s | Una alarma programada (por ejemplo la del Durable Object o un activador de Apps Script) entrega a su hora |
| ¿Funciona en las cinco? | Sí: no necesita nada de la plataforma | No: Workers y Apps Script no tienen hilos, y una instancia dormida no revisa nada | Sí, pero con un mecanismo distinto en cada una, cada uno con sus propios límites (por verificar en la documentación oficial) |
| Costo de construir | Bajo: una regla de las «calculadoras» de ADR-001, llamada en cada lectura | Bajo en Python; imposible en JS | Alto: cinco mecanismos distintos |
| Costo de probar | Bajo: se prueba con una hora fija, sin esperar | Alto: hay que esperar o mover el reloj | Alto: hay que simular la alarma de cada plataforma |

- **Decision** — A. Es la única que funciona igual en las cinco plataformas sin un mecanismo propio de
  cada una, y se prueba sin esperar. Reglas exactas:
  - la hora de entrega es la menor entre ahora, el vencimiento (`inicio + duración`) y el cierre de la
    sala, y el motivo es `tiempo` o `cierre`, según cuál llegó primero;
  - al cerrar la sala, quien nunca empezó pasa a `no_inicio`;
  - un solo componente, **Examen**, es dueño de escribir la entrega. Salas al cerrar, y Resultados y
    Exportación antes de leer, le piden a Examen que aplique la regla (R-01);
  - entregar es idempotente: un intento pasa de `en_curso` a `finalizado` una sola vez, dentro de una
    transacción, aunque dos lecturas lleguen a la vez (R-09). El mecanismo de cada plataforma va en su
    ADR.
- **Consequences** — A favor: puntos, bono, clasificación y CSV salen iguales que hoy, y el reloj se
  prueba con una hora fija. En contra: la fila de la base se escribe cuando alguien consulta, no a los
  3 s. Desde fuera no se nota, porque toda lectura aplica la regla antes.
- **Alternatives Rejected** — B: no existe en Workers ni en Apps Script, y no revisa nada si la
  instancia se duerme. C: cinco mecanismos distintos para la misma regla, más difíciles de probar.

## ADR-005: Cada dato lleva su sala, y cada petición dice de qué sala es

**Estado:** aprobado por el humano (2026-10-25). Revisa la versión anterior
(Q5-C) con la comparación de costos y resuelve los hallazgos R-03 (cómo indica su sala cada petición) y
R-05 (que la copia de una sala no lleve datos de otras).

- **Context** — Con un solo enlace hay varias salas a la vez (FR11.1). Cada sala se descarga, se
  reinicia y se borra sin tocar las demás (FR11.6, NFR10.1), y una clave de sala no abre otra (FR11.5).
  La forma del almacén cambia en cada opción: una tabla con columna `sala` en SQLite, un Durable Object
  por sala en Workers, una hoja por sala en Sheets.

| | A. Un solo servicio; cada dato lleva su sala | B. Un despliegue aparte por cada sala | C. Fijar ya la misma forma de almacén en las cinco opciones |
|---|---|---|---|
| Cómo es | Participante, Respuesta y Evento llevan la sala (Intento ya no existe, ADR-007). Cada opción guarda eso como le quede mejor | Cada reto tiene su propio servicio y su propio enlace; el código no sabe de salas | Por ejemplo, «una tabla con columna `sala`» en todas |
| Costo de construir | Medio: separar por sala en cada consulta | Bajo en código, alto en operación: el semillero despliega y configura un servicio por reto | Alto: Workers y Sheets no tienen tablas SQL; habría que forzar la forma |
| Costo de operar | Bajo: un enlace y un despliegue | Alto: n enlaces, n despliegues y n veces la cuota | Igual que A |
| ¿Cumple lo pedido? | Sí | No: va contra «un servidor, varias salas» (FR11.1) | Sí, pero ata el dominio a una plataforma |

- **Decision** — A. Es la única que cumple FR11.1 sin atar las cinco opciones a una sola forma de
  almacén. Cómo guarda cada opción la sala va en su ADR (FR12.2b). Cómo dice cada petición de qué sala es:

| Quién pide | Cómo se sabe la sala |
|---|---|
| Tablero (público) | El enlace del tablero lleva el código: `/tablero?sala=KQMT`, y pide `/api/publico?sala=KQMT` |
| Estudiante al inscribirse | El código de sala que escribe, como hoy |
| Estudiante ya inscrito | Su sesión: la sala sale de su inscripción |
| Estudiante que vuelve con su código personal | El código personal es único en todo el servicio, no solo en la sala, así que la pantalla no cambia (FR11.3) |
| Docente | La clave de sala empieza con el código de la sala, por ejemplo `KQMT-…`. El servidor separa el código, busca la sala y compara el resto con la huella en tiempo constante. El docente sigue pegando una sola cadena |
| Semillero | Su clave abre todas las salas, así que cada acción dice la sala explícitamente |

  La copia de datos de una sala (FR4.3, FR9.1) lleva **solo las filas de esa sala**, cualquiera sea la
  forma del almacén. Con una base compartida no se usa `VACUUM INTO` de la base entera, porque copiaría
  las demás salas (R-05).
- **Consequences** — A favor: un solo enlace y un solo despliegue para todos los colegios, y cada sala
  queda aislada. En contra: el enlace del tablero cambia (lleva `?sala=`). Ese es un cambio visible, ya
  aprobado como parte de «tablero por sala» (FR11.4), y va en el contrato de la API. Las pantallas no
  cambian.
- **Alternatives Rejected** — B: multiplica enlaces, despliegues y cuota, y contradice FR11.1. C: obliga
  a forzar tablas SQL donde la plataforma no las tiene.

## ADR-006: Ids opacos derivados de la semilla del participante

**Estado:** aprobado por el humano (2026-10-25). Revisa la versión anterior
(Q6-A) con la comparación de costos en los dos lenguajes.

- **Context** — Hoy los identificadores de opciones, ítems y partes que recibe el navegador siguen el
  orden en que se escribió el banco, y de ahí se puede deducir la respuesta (FR6.2). La base y los CSV
  siguen guardando los ids del banco (FR6.2, FR9.2), así que el servidor traduce al recibir.

| | A. Ids calculados a partir de la semilla del participante | B. Ids al azar guardados en la base | C. Solo barajar el orden, sin cambiar los ids |
|---|---|---|---|
| Cómo es | Una función (HMAC con la semilla secreta, el id de la pregunta y el de la opción) da el id que ve el navegador, y la misma función traduce de vuelta | Al inscribirse se sortea un id por opción y se guarda la tabla de equivalencias | Se envían las opciones en otro orden, con los mismos ids del banco |
| Costo de construir | Bajo: una función en las «calculadoras» de ADR-001. Python y JS traen HMAC (`hmac` en Python, Web Crypto en Workers, `Utilities` en Apps Script) | Medio: una tabla más, que hay que respaldar y borrar al cerrar (NFR10.1) | El más bajo |
| ¿Cierra la fuga? | Sí | Sí | No: los ids siguen diciendo la posición en el banco |

- **Decision** — A. Cierra la fuga igual que B, pero sin datos nuevos que guardar, respaldar ni borrar,
  y se prueba sin base. Cada participante ve ids distintos para la misma pregunta.
- **Consequences** — A favor: nada nuevo en la base ni en el paquete de datos. En contra: la semilla
  tiene que seguir siendo secreta; hoy ya lo es, porque nunca sale al navegador. La función tiene que
  ser la misma mientras haya un reto en curso, y eso ya lo cubre la regla de no desplegar con un reto en
  curso (`project.md`, «Forbidden»). No hace falta que dé lo mismo entre versiones distintas, porque
  cada versión es independiente.
- **Alternatives Rejected** — B: una tabla más con datos de cada participante, sin ventaja visible. C:
  no cumple FR6.2.

## ADR-007: Un solo Participante, con un dueño por cada grupo de datos

**Estado:** aprobado por el humano (2026-10-25). Cambia la versión anterior
(«Intento separado de Participante»), que fue una decisión del arquitecto y no una respuesta del humano.
Con la comparación de costos en cinco versiones, gana la alternativa más simple. Resuelve el hallazgo
R-02: quién es dueño del estado del participante y de cada acción del docente.

- **Context** — Hoy la tabla `participantes` guarda quién es la persona (nombre, colegio, grado,
  integrantes) y lo que pasa en el reto (estado, inicio, entrega, puntos, bono). El docente tiene cuatro
  acciones sobre un participante (`accion_participante` en `servidor.py`): `descalificar`, `reactivar`,
  `finalizar` y `eliminar`. `eliminar` solo vale si el participante nunca empezó (`registrado` o
  `no_inicio`). El problema es que no quede claro quién puede cambiar cada dato.

| | A. Dos entidades: Participante (quién es) e Intento (qué pasa en el reto) | B. Una entidad, con un dueño por cada grupo de datos | C. Una entidad sin dueños, como hoy |
|---|---|---|---|
| Cómo es | Inscripción es dueña de Participante y Examen de Intento | Participante es una sola entidad. Inscripción escribe los datos de la persona; Examen escribe el estado y los datos del reto | Cualquier función escribe cualquier campo |
| Costo de construir | Alto en cinco versiones: dos entidades, uniones en cada vista y borrado en cascada entre dos dueños | Bajo: una entidad, como hoy, más la regla de quién escribe qué | El más bajo |
| Costo en los datos | Los CSV tienen que juntar las dos para quedar iguales a hoy (FR4.3) | Ninguno: los CSV salen como hoy | Ninguno |
| ¿Queda claro el dueño? | Sí | Sí | No |

- **Decision** — B. Deja tan claro como A quién escribe cada dato, sin dos entidades que unir en cinco
  versiones ni CSV que rearmar. Con las «calculadoras» de ADR-001, la limpieza de la inscripción ya no se
  mezcla con el cálculo de puntos. Dueños:

| Dato o acción | Dueño |
|---|---|
| Nombre, colegio, grado, integrantes; crear el participante | Inscripción |
| `eliminar` (solo si está en `registrado` o `no_inicio`): borra al participante y sus eventos | Inscripción |
| Estado (`registrado`, `en_curso`, `finalizado`, `no_inicio`, `descalificado`), inicio, entrega, puntos y bono | Examen |
| `finalizar`, `descalificar` y `reactivar` | Examen |
| Entregar por vencimiento o por cierre de la sala | Examen (ADR-004) |

- **Consequences** — A favor: una sola entidad en las cinco versiones, CSV iguales a hoy y un dueño
  claro por cada dato. En contra: los dos dueños comparten la misma fila. La regla «solo Examen cambia el
  estado» se revisa en el PR, y la cubren las pruebas de las acciones del docente.
- **Alternatives Rejected** — A: duplica entidades, uniones y borrados en cinco versiones sin cambiar
  nada visible. C: deja el problema como está.

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
