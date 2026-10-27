# Decisiones de diseño del dominio

Registro de decisiones de arquitectura (ADR) de Domain Design. Cada ADR compara al menos dos
alternativas con su costo. ADR-001 a ADR-008 fueron aprobados por el humano el 2026-10-25. Valen para la
versión de la nube que se construye, Cloudflare (FR12.2c); la versión local (`2_Aplicacion_Reto/`) no
cambia. Lo propio de la plataforma va en el ADR de la opción (FR12.2b).

**Revisión del 2026-10-25 (una sola sala).** El humano fijó que «esto lo controla un solo profesor en un
solo panel. no con varios profesores con varios paneles. es solo una sala.» y pegó las reglas de negocio
(`../requirements-analysis/reglas-de-negocio-2026-10-25.md`). Con eso, ADR-002, ADR-003 y ADR-005 quedan
reemplazados por ADR-009, ADR-010 y ADR-011; su texto se conserva como historia. ADR-004 se ajusta para
que el vencimiento sea por colegio. Lo que no salió del humano lleva la marca «decisión del asistente», con
la potestad que él dio en la revisión de los requisitos.

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
  sin pruebas unitarias las reglas que más fallan (tiempo y desempates). Lo demás (reto, colegios,
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

**Estado:** Reemplazado por ADR-009 (revisión 2026-10-25). Con un solo docente ya no hay semillero que
mantenga un catálogo ni colegios «provisionales»; FR10.3 vuelve a decir que el docente carga la lista. El
texto de abajo se conserva como historia.

Aprobado por el humano (2026-10-25). Revisa la versión anterior
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

**Estado:** Reemplazado por ADR-010 (revisión 2026-10-25). Hay una sola clave docente (NFR9), así que no
hay claves de sala que generar, guardar como huella ni regenerar. El texto de abajo se conserva como
historia.

Aprobado por el humano (2026-10-25). Revisa la versión anterior
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
entrega al cerrar el reto) y R-09 (que una entrega no pase dos veces). Ajustado en la revisión del
2026-10-25: el vencimiento es **por colegio**, porque cada colegio tiene su propio reloj (FR3.1,
ADR-011); la regla no cambia, solo el `inicio` de cada participante, que ahora es el arranque de su
colegio.

- **Context** — Hoy un hilo `vigilante` revisa cada 3 s los intentos vencidos (`servidor.py`,
  `vigilante`), y `finalizar` pone la hora de entrega en `fin = min(ahora, inicio + duración)`. Al
  cerrar el reto, `cambiar_estado` entrega los intentos en curso con la hora del cierre y el motivo
  `cierre`, y pasa a `no_inicio` a quien nunca empezó. La hora de entrega es el 4.º criterio de desempate
  (FR2.3), así que tiene que salir exacta. Con un reloj por colegio, `inicio + duración` es distinto para
  cada colegio, y al vencer uno se entregan solo sus equipos (FR3.1).

| | A. Vence al consultar | B. Un hilo que revisa cada pocos segundos (como hoy) | C. Un temporizador de cada plataforma |
|---|---|---|---|
| Cómo es | Antes de responder cualquier petición del reto, se entregan los intentos que ya vencieron, con su hora exacta | Un proceso aparte revisa todo cada 3 s | Una alarma programada (por ejemplo la del Durable Object o un activador de Apps Script) entrega a su hora |
| ¿Funciona en las cinco? | Sí: no necesita nada de la plataforma | No: Workers y Apps Script no tienen hilos, y una instancia dormida no revisa nada | Sí, pero con un mecanismo distinto en cada una, cada uno con sus propios límites (por verificar en la documentación oficial) |
| Costo de construir | Bajo: una regla de las «calculadoras» de ADR-001, llamada en cada lectura | Bajo en Python; imposible en JS | Alto: cinco mecanismos distintos |
| Costo de probar | Bajo: se prueba con una hora fija, sin esperar | Alto: hay que esperar o mover el reloj | Alto: hay que simular la alarma de cada plataforma |

- **Decision** — A. Es la única que funciona igual en las cinco plataformas sin un mecanismo propio de
  cada una, y se prueba sin esperar. Reglas exactas:
  - la hora de entrega es la menor entre ahora, el vencimiento (`inicio + duración`, donde `inicio` es
    el arranque del colegio del participante) y el cierre del reto, y el motivo es `tiempo` o `cierre`,
    según cuál llegó primero; así cada colegio vence por su cuenta y solo se entregan sus equipos;
  - al cerrar el reto, quien nunca empezó pasa a `no_inicio`;
  - un solo componente, **Examen**, es dueño de escribir la entrega. Reto al cerrar, y Resultados y
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

**Estado:** Reemplazado por ADR-011 (revisión 2026-10-25). Hay una sola sala (FR11.1): ningún dato lleva
sala, el tablero pide `GET /api/publico` sin `?sala=` y la clave no lleva prefijo. El texto de abajo se
conserva como historia.

Aprobado por el humano (2026-10-25). Revisa la versión anterior
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
| Entregar por vencimiento del reloj de su colegio o por cierre del reto | Examen (ADR-004) |

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

## ADR-009: La lista de colegios la carga el docente en su panel

**Estado:** propuesto en la revisión del 2026-10-25; reemplaza a ADR-002. Fuente: FR10.3 revisado («con
un solo docente ya no hay catálogo del semillero ni colegios "provisionales"») y la frase del humano «es
solo una sala». Resuelve OQ7 (cómo se carga la lista y qué pasa si falta un colegio el día del reto).

- **Context** — La lista cerrada de colegios (FR10.3) existe para que «IE San José» y «colegio san jose»
  no queden como dos colegios, y para que el reloj por colegio (FR3.1) agrupe bien a los equipos. Con un
  solo docente y un solo panel ya no hay quién mantenga un catálogo entre retos. Los paquetes de varios
  retos se unen por `colegios.csv` (FR9.1, FR9.2). Toda entrada pasa por LimpiezaEntrada (FR10.2) y
  solo el docente, con su clave, toca la lista (NFR9).

| | A. El docente carga la lista en su panel | B. Catálogo único del semillero (ADR-002) | C. Texto libre normalizado, sin lista |
|---|---|---|---|
| Cómo es | En `inscripcion` o `abierto`, el docente agrega colegios uno a uno o pega un nombre por línea; el servidor genera el `id_colegio`, normaliza el nombre y rechaza un repetido. Un colegio se quita solo si no tiene equipos. Si falta uno el día del reto, lo agrega en ese momento | El semillero mantiene la lista con un id fijo entre años; el docente elige de ahí y agrega «provisionales» | El estudiante escribe el colegio; el servidor agrupa por nombre normalizado |
| Costo de construir | Bajo: una tabla de colegios, dos rutas del panel y la lista en la inscripción | Medio: catálogo, pantalla del semillero, elección, provisionales y unión posterior | El más bajo |
| Costo en los datos | Bajo: el id es estable dentro del reto; entre retos se unen por nombre normalizado en `colegios.csv` | Ninguno: el mismo id siempre | Alto: un error de ortografía parte un colegio en dos relojes |
| ¿Sirve para el reloj por colegio? | Sí: el colegio es una fila con `arranque` | Sí | No con seguridad: dos grafías del mismo colegio serían dos relojes |

- **Decision** — A. Es la más parsimoniosa que cumple FR10.3 y FR3.1 con un solo docente: no exige un
  actor que ya no existe (B) y no deja que una grafía distinta cree un reloj aparte (C). Detalles que son
  decisión del asistente: la lista se carga pegando un nombre por línea o agregando uno a uno; el
  servidor genera el `id_colegio`; un nombre repetido (normalizado) se rechaza con el mensaje del estilo
  de hoy; un colegio con equipos no se quita ni se renombra (si el docente se equivocó, lo quita y lo
  agrega de nuevo mientras no tenga equipos); se agrega también en `abierto`, para el colegio que llega
  el día del reto sin estar en la lista; cada nombre se recorta a 80 caracteres (FR10.2).
- **Consequences** — A favor: una sola pantalla, la del docente, y ninguna pieza del semillero en el
  servidor. El reloj por colegio tiene una fila clara donde guardar `arranque`. En contra: el
  `id_colegio` no se conserva entre retos; unir varios años se hace por nombre normalizado en
  `colegios.csv`, y el diccionario de datos (FR9.3) lo advierte. «Reiniciar» borra la lista junto con el
  reto (FR11.6, decisión del asistente), así que el docente la vuelve a cargar en el siguiente reto.
- **Alternatives Rejected** — B: exige un actor y una pantalla que el humano quitó. C: no garantiza que
  un colegio tenga un solo reloj.

## ADR-010: Una sola clave docente como secreto del hosting

**Estado:** propuesto en la revisión del 2026-10-25; reemplaza a ADR-003. Fuente: NFR9 revisado («Hay
una sola clave, la del docente … Vive como secreto del hosting, tiene al menos 12 caracteres, se compara
en tiempo constante … solo viaja en la cabecera `X-Clave-Admin`»), FR9.5, FR11.5 y la regla de
`project.md` («NEVER aceptar la clave docente … en la URL (?clave=)»). Cierra OQ6 (límite de intentos).

- **Context** — Hoy `servidor.py` compara la clave con `secrets.compare_digest`, pero la acepta también en
  `?clave=` (`es_admin`), la guarda en `datos/clave_docente.txt` y la genera con 6 caracteres si nadie la
  fija. En la nube la URL queda en los registros del hosting y el repositorio es público, así que la
  clave no puede vivir en un archivo del repositorio ni en la URL. Con una sola sala no hay clave del
  semillero ni clave por sala.

| | A. Secreto del hosting, solo por cabecera | B. Clave guardada en la base como huella, regenerable (ADR-003) | C. Archivo `clave_docente.txt` junto a la base, como hoy |
|---|---|---|---|
| Cómo es | Arranque lee la clave del secreto del hosting y se niega a arrancar si tiene menos de 12 caracteres; Acceso la compara en tiempo constante con `X-Clave-Admin`; `?clave=` da 403 | El servidor genera la clave, la muestra una vez y guarda su huella; el panel la regenera | El servidor la lee o la genera en un archivo del disco persistente |
| Costo de construir | El más bajo: leer un secreto y comparar | Medio: tabla o fila de huella, ruta para regenerar y mostrarla una vez | Bajo, pero exige disco persistente y un archivo que no entra en la copia |
| Riesgo | Bajo: no está en la base, el paquete ni el repositorio; cambiarla es cambiar el secreto y redesplegar | Bajo, pero una regeneración a mitad del reto deja al docente afuera | Medio: la clave generada hoy tiene 6 caracteres y vive en disco |
| ¿Cumple NFR9? | Sí | Sí, con una pieza más | No sin cambios: largo y ubicación |

- **Decision** — A. Cumple NFR9 con la menor cantidad de piezas y deja la clave fuera de la base, del
  paquete y del repositorio. Reglas exactas:
  - la clave viaja solo en `X-Clave-Admin`; una clave ausente, incorrecta o pasada en `?clave=` recibe
    403 sin datos (FR9.5), y A4 confirma que ningún cliente de `web/js/` usa `?clave=`;
  - se compara en tiempo constante, byte a byte, después de quitar los espacios de los extremos y sin
    cambiar mayúsculas (decisión del asistente: hoy el servidor la pasa a mayúsculas porque la genera de
    un alfabeto sin minúsculas; con una clave de 12 o más caracteres fijada por una persona, cambiar las
    mayúsculas la debilitaría);
  - Arranque se niega a arrancar si el secreto tiene menos de 12 caracteres, y lo dice en el registro sin
    mostrar la clave (decisión del asistente: así el requisito se comprueba en el despliegue y no en una
    revisión);
  - no hay límite de intentos fallidos (OQ6): con 12 o más caracteres y 403 sin pista, un límite cambiaría
    la conducta del panel sin necesidad; si el hosting ofrece limitar peticiones sin código, NFR Design lo
    anota como opcional.
- **Consequences** — A favor: una pieza menos en la base y en el paquete, y nada que regenerar desde el
  panel. En contra: cambiar la clave exige cambiar el secreto y redesplegar, y eso solo se hace sin un
  reto en curso (`project.md`, «Forbidden»); la guía de despliegue (FR8.1) dice cómo fijar el secreto y
  que tenga al menos 12 caracteres. La clave no se registra nunca (`.claude/rules/python-code.md`,
  «Logs»).
- **Alternatives Rejected** — B: una pieza más para un problema que ya no existe sin salas. C: la clave
  en disco con 6 caracteres no cumple NFR9 y queda fuera de la copia de datos.

## ADR-011: Una sola sala y un reloj por colegio arrancado por el docente

**Estado:** propuesto en la revisión del 2026-10-25; reemplaza a ADR-005. Fuente: el humano («esto lo
controla un solo profesor en un solo panel … es solo una sala.») y las reglas de negocio §4.1 («los
relojes son independientes para cada colegio … se garantiza que cada colegio tenga sus 90 min sin importar
si empezaron 5 o 10 min mas tarde»), §1 («el podio es general») y §7 («Clasificación general y por
grado»); FR2.5, FR2.6, FR3.1, FR11. Quién arranca cada reloj y cómo se miden los tiempos no salió del
humano: son decisión del asistente, marcadas abajo.

- **Context** — Hoy `servidor.py` tiene un solo reto con reloj global (todos desde `abierto_en`) o
  individual (cada equipo desde su «Comenzar»). A la sala entran equipos de varios colegios y cada
  colegio llega listo a una hora distinta. Hay que garantizar los 90 minutos de cada colegio sin que el
  bono ni los desempates castiguen al que empezó tarde, y sin cambiar nada más de lo visible (FR11.3).

| | A. Una sala; reloj por colegio arrancado por el docente; tiempos relativos al arranque | B. Varias salas, una por colegio (ADR-005) | C. Una sala con un solo reloj global, como hoy | D. Reloj del colegio que arranca solo con el primer «Comenzar» de ese colegio |
|---|---|---|---|---|
| Cómo es | Colegio lleva `arranque`. «Abrir el reto» arranca los colegios que ya tienen equipos; «Arrancar reloj» arranca uno que llega tarde; el inicio del equipo es el arranque de su colegio; entrega = min(ahora, arranque + duración, cierre); bono y desempate miden desde el arranque del colegio | Cada colegio es una sala con su clave, su tablero y su reloj | Un solo `abierto_en`; el que llega tarde pierde minutos | Igual que A, pero el reloj lo dispara el primer equipo del colegio que pulsa «Comenzar» |
| Costo de construir | Bajo: una columna, una acción del panel y pasar el arranque a la hora de entrega | Alto: todo lo de ADR-002, 003 y 005 | El más bajo: nada | Bajo, igual que A sin el botón |
| ¿Cumple las reglas de negocio? | Sí: 90 minutos por colegio, podio general entre todos | Sí los 90 minutos, pero el podio general exige cruzar salas | No: un colegio tardío no tiene sus 90 minutos | Sí los 90 minutos, pero el reloj arranca cuando un equipo decide, no cuando el colegio está listo, y un equipo apurado les quita tiempo a los demás de su colegio |
| ¿Un solo panel y una sola clave? | Sí | No | Sí | Sí |

- **Decision** — A. Es la única que cumple «es solo una sala», los 90 minutos por colegio y el podio
  general con una columna y un botón más. Reglas exactas (las marcadas son decisión del asistente):
  - **el docente arranca cada colegio** desde el panel, con confirmación, porque es quien sabe cuándo un
    colegio está listo (decisión del asistente; §4.1 solo dice «según cuando ellos hayan estado listos»);
  - **«Abrir el reto»** arranca a la vez los colegios que ya tienen al menos un equipo inscrito
    (decisión del asistente: es el caso ideal en que todos empiezan juntos y no exige un clic por
    colegio);
  - un arranque no se repite ni se deshace; un colegio se arranca solo con el reto en `abierto`;
  - **«Comenzar»** exige que el colegio del equipo haya arrancado; su `inicio` es el arranque del colegio,
    aunque pulse después, y mientras espera ve «Tu colegio todavía no ha empezado. Espera la señal del
    docente.» (FR3.1);
  - la entrega sigue la regla de ADR-004 con ese `inicio`, así que cada colegio vence por su cuenta y
    «Cerrar el reto» entrega a todos;
  - **tiempos relativos al arranque del colegio** (FR2.6, decisión del asistente): el bono usa
    `tiempo_respuestas` desde el `inicio` (ya es así hoy) y el desempate usa `tiempo_respuestas` ↑ y luego
    `tiempo_usado` ↑ (`fin − inicio`) en vez de la hora absoluta de entrega; la inscripción más temprana
    sigue siendo absoluta. Con un solo colegio arrancado al abrir, todos los `inicio` son iguales y el
    orden es idéntico al de hoy (FR11.7);
  - **podio general y clasificación por grado** (FR2.5): un solo orden total entre todos los equipos; el
    podio son sus tres primeros; la clasificación por grado es el mismo orden filtrado por 9.°, 10.° y
    11.°; la nota es `1 + 4 × puntos / 1.000` sin el bono. El experimento A/B y la publicación de
    resultados son de toda la sala (FR11.2);
  - **sin `reloj_global`**: el selector de hoy desaparece del panel porque el reloj por colegio lo
    reemplaza (decisión del asistente); qué devuelve la API en esa clave, que `web/js/` sigue leyendo
    (FR4.1), lo fija el contrato de la API;
  - **un solo tablero** en `/tablero` y `GET /api/publico` sin parámetros, que es también el chequeo de
    salud (FR11.4). Esto revierte la regla aprendida en Contract Design de responder solo `{"ok": true}`
    sin `?sala=`, que era para varias salas.
- **Consequences** — A favor: una columna (`arranque`), una acción del panel y ningún cambio para el
  estudiante salvo el aviso de espera. Puntos, bono y orden salen iguales que hoy con un solo colegio. En
  contra: un equipo que se inscribe después del arranque de su colegio empieza con menos tiempo, igual que
  hoy con el reloj global; el panel muestra el reloj de cada colegio para que el docente lo vea. El 4.º
  desempate cambia de `fin` absoluto a `tiempo_usado`; es un cambio de conducta solo visible cuando hay
  dos colegios con arranques distintos, aprobado dentro de FR11 y FR2.6. La prueba común agrega el caso
  de dos colegios arrancados a distinta hora (FR11.7). Seguridad: solo la clave docente arranca relojes;
  nada nuevo sale al navegador antes de «resultados» (NFR8).
- **Alternatives Rejected** — B: contradice «es solo una sala» y multiplica claves, tableros y
  paneles. C: no da los 90 minutos al colegio que llega tarde. D: deja el arranque en manos de un
  estudiante y un equipo apurado les quita minutos a los demás de su colegio.
