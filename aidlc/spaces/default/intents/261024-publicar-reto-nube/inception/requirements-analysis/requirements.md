# Requisitos: publicar el reto en la nube y refactorizar el servidor

Intención `261024-publicar-reto-nube`, alcance `classic`, proyecto brownfield, profundidad Standard.
Las respuestas citadas como Q1-Q9 están en `requirements-analysis-questions.md` (misma carpeta); las
de Practices Discovery, en `aidlc/spaces/default/intents/261024-publicar-reto-nube/inception/practices-discovery/team-practices.md`.

**Revisión del 2026-10-25 (reajuste a una sola sala).** El humano pegó las reglas de negocio del reto
(copia textual en `reglas-de-negocio-2026-10-25.md`, misma carpeta) y dijo: «esto lo controla un solo
profesor en un solo panel. no con varios profesores con varios paneles. es solo una sala.» Esta revisión:

- reemplaza FR11 (antes «varios retos en paralelo, uno por sala») por **una sola sala con varios
  colegios y un reloj por colegio**;
- agrega el podio general, la clasificación por grado y la nota (FR2.5);
- ajusta NFR1 y NFR9 a una sola sala y una sola clave docente;
- deja **solo Cloudflare** para construir y desplegar (FR12.2c); las demás opciones quedan documentadas.

Las decisiones abiertas que dejaban las reglas las tomó el asistente con la potestad que dio el humano
(«potestad absoluta para decidir»); cada una lleva la marca «decisión del asistente».

## Intent analysis

**Qué se busca.** Que el reto «Detectives de la desinformación» se pueda jugar desde un **enlace fijo
en internet** que **no dependa del computador del docente**, **sin costo** (Q5-A), con una arquitectura
validada y patrones elegidos en los ADR comparando alternativas (pedido inicial, puntos 4 y 5).

**Cómo se elige el hosting** (decisión del humano, 2026-10-25, en la revisión de Domain Design). La
versión local (`2_Aplicacion_Reto/`) queda **congelada**: no se refactoriza ni recibe funciones
nuevas, y sigue siendo la línea base y el respaldo. Cada opción de hosting se construye y se despliega
**por separado**, en su propia carpeta, y al final se comparan todas con la misma prueba. Gana la más
simple que pase todo (FR12).

**Por qué.** Hoy hay tres modos (`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/business-overview.md`,
«Contexto de despliegue actual»): red local y túnel temporal dependen del computador del docente;
Render con disco da enlace fijo pero es de pago (≈ US$ 7/mes según `PUBLICAR_EN_INTERNET.md`, cifra
por verificar en la documentación oficial). El servidor es un monolito de un archivo con lógica de
dominio, SQL, reloj y HTTP mezclados (`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/code-structure.md`,
«Mapa de secciones de `servidor.py`»), y un `RLock`, un hilo vigilante y un archivo SQLite de proceso
que obligan a una sola instancia con disco local (`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/architecture.md`,
«Dónde vive cada pieza de estado»).

**Tipo de cambio.** Una versión nueva en la nube, en Cloudflare (FR12.2c), construida al lado de la
versión local sin tocarla. Lleva las dos correcciones de confidencialidad (FR6) y las tres
funcionalidades nuevas pedidas en esta etapa: datos organizados (FR9), entrada limpia (FR10) y una sola
sala con varios colegios, cada uno con su propio reloj (FR11). Las demás opciones de hosting quedan en
la tabla de comparación solo con su documentación.
Alcance: todo el sistema (servidor, despliegue, guía de publicación). Complejidad: estándar a alta por
el riesgo de integración (cambiar de hosting y de estructura a la vez), que es la razón del corte
delgado primero (`team-practices.md`, «Walking Skeleton»).

**Regla rectora.** No cambia la conducta visible del reto: pantallas, preguntas, puntajes, desempates
ni flujo de estados (Q1 y Q8 de Practices Discovery). Solo se permite corregir fugas de respuestas antes
de «resultados» (Q7-A).

## Functional requirements

Los requisitos FR1-FR4 fijan la **conducta que se conserva**. Cada versión de la nube los cumple, y se
verifican con la prueba común de FR12.3, que repite las comprobaciones de `pruebas/simulacro.py 40`
contra la URL desplegada sin debilitar ninguna. Desde FR5 hasta FR11, todo requisito aplica a cada
versión de la nube y no a la versión local, que no cambia (FR12.1).

### FR1. Conservar el flujo del reto

- **FR1.1** El sistema conserva los cuatro estados del reto `inscripcion` → `abierto` → `cerrado` →
  `resultados` y «Reiniciar» (con copia de seguridad y confirmación BORRAR) con la misma conducta de hoy
  (`architecture.md`, «Flujo de estados del reto»).
- **FR1.2** El sistema conserva los estados del participante `registrado`, `en_curso`, `finalizado`,
  `no_inicio`, `descalificado` y sus transiciones (`architecture.md`, «Flujo de estados del
  participante»).
- **FR1.3** El sistema conserva la inscripción con código de sala, el código de 5 caracteres y la
  recuperación de sesión con ese código (`business-overview.md`, «Funcionalidad clave»).

### FR2. Conservar la calificación y la clasificación

- **FR2.1** La calificación con crédito parcial de los 10 tipos de pregunta da los mismos puntos que hoy
  para la misma respuesta (`business-overview.md`, «Funcionalidad clave»).
- **FR2.2** El bono de tiempo sigue la fórmula actual `20 × (puntos / 1.000) × (1 − t_última / duración)`
  (`architecture.md`, «Calificación»).
- **FR2.3** La clasificación sigue siendo un orden total con los desempates actuales: total ↓, puntos
  ↓, momento de la última respuesta ↑, hora de entrega ↑, orden de inscripción ↑
  (`architecture.md`, «Calificación»).
- **FR2.4** Cada pregunta se acepta una sola vez por participante, y la fase «¿es verdad?» del Exp. 01
  sigue exigiendo antes «¿lo compartirías?».
- **FR2.5 Podio general, clasificación por grado y nota** (reglas de negocio, §1 y §7). El podio
  (1.°, 2.° y 3.°) se calcula entre **todos los equipos de todos los colegios** de la sala, con el orden
  total de FR2.3. También hay clasificación por grado (9.°, 10.° y 11.°) con el mismo orden. La nota va
  de 1,0 a 5,0: `1 + 4 × puntos / 1.000`, sin el bono.
- **FR2.6 Tiempos relativos al reloj del colegio** (decisión del asistente). Como cada colegio arranca
  a una hora distinta (FR3.1), el bono y el desempate por «última respuesta más temprana» y «entrega
  más temprana» usan los minutos transcurridos desde el arranque del colegio de cada equipo, no la hora
  del reloj de pared. Así un colegio que empezó 10 minutos tarde no pierde bono ni desempates. La
  «inscripción más temprana» sí usa la hora real, porque todos se inscriben antes de arrancar.

### FR3. Conservar el reloj medido por el servidor

- **FR3.1 Un reloj por colegio** (reglas de negocio, §4.1; antes: reloj global o individual). El
  tiempo lo mide el servidor y el navegador solo muestra la cuenta regresiva. Cada colegio de la sala
  tiene su propio reloj de 90 minutos, que empieza cuando el docente lo arranca desde el panel (decisión
  del asistente: es el docente quien sabe cuándo un colegio está listo):
  - «Abrir el reto» pasa la sala a `abierto` y arranca a la vez el reloj de todos los colegios que ya
    tienen equipos inscritos; es el caso ideal en que todos empiezan juntos.
  - Un colegio que llega tarde se arranca después con su propio botón «Arrancar reloj» en el panel, y
    tiene sus 90 minutos completos desde ese momento.
  - Cada arranque pide confirmación, como los cambios de estado.
  - Un equipo solo puede pulsar «Comenzar» cuando su colegio ya arrancó; su tiempo corre desde el
    arranque del colegio, aunque pulse «Comenzar» después. Mientras tanto ve «Tu colegio todavía no ha
    empezado. Espera la señal del docente.».
  - El reloj de un colegio no se detiene si se cierra la página; al vencer, el servidor entrega
    automáticamente lo de cada equipo de ese colegio (FR3.2).
  - «Cerrar el reto» entrega lo pendiente de todos los colegios, hayan vencido o no.
- **FR3.2** Toda consulta (del estudiante, el tablero, el panel o una descarga) ve como entregados los
  intentos vencidos, con la hora de entrega igual al vencimiento exacto; puntos, bono, clasificación y
  CSV salen iguales que hoy. No hace falta un proceso aparte que revise cada pocos segundos (reescrito
  en Domain Design, Q7-A, 2026-10-25; antes: vigilante cada 3 s con ≤ 5 s de retraso).
- **FR3.3** Si el servicio se cae o se duerme, el reloj sigue corriendo durante la caída y, al volver,
  lo vencido se entrega (Q4-A, igual que hoy).

### FR4. Conservar la API que consume el navegador

- **FR4.1** Se mantienen las rutas HTTP y las claves JSON que usa `web/js/` (5 GET y 11 POST,
  `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/api-documentation.md`). Cualquier cambio
  que exija el frontend se lista en el contrato de la API con su motivo y su archivo de `web/js/`.
- **FR4.2** Las páginas `/`, `/admin` y `/tablero` y sus estáticos se sirven sin cambios visibles.
- **FR4.3** Se mantienen las exportaciones CSV de resultados y respuestas y la copia de seguridad al
  reiniciar. Esa copia es una **copia completa de los datos que se puede volver a abrir**: `reto.db` en
  las opciones con SQLite, y en las demás el formato que fije su ADR (por ejemplo, un volcado SQL de D1
  o una copia de la hoja de cálculo).

### FR5. Publicación con enlace fijo

- **FR5.1** Cada versión de la nube queda accesible desde su propio enlace HTTPS fijo, que no cambia
  entre retos ni depende de que el computador del docente esté encendido. Al final, el docente usa solo
  el enlace de la opción ganadora (FR12.5).
- **FR5.2** El despliegue es manual: lo lanza una persona del semillero, nunca con un reto en curso, y
  volver atrás es redesplegar la versión anterior (Practices Discovery Q6; `team-practices.md`,
  «Deployment»).
- **FR5.3** Flujo de ramas para desplegar (decisión del humano en la aprobación de esta etapa, que
  reemplaza a `team-practices.md` en este punto; regla general, 2026-10-25): cada cambio se hace en su
  propia rama de trabajo con prefijo de tipo (`feat/`, `fix/`, `refactor/`, `chore/`…; por ejemplo,
  `refactor/code-cleanup`), creada desde `develop`. Pasa a `develop` (creada desde `main`) solo por PR,
  para dejar trazabilidad, y se repite rama por rama hasta llegar a la versión final. Mientras se prueba, el hosting
  despliega desde `develop`. Cuando la versión final está desplegada y verificada desde `develop`, un PR
  revisado la lleva a `main`, y el despliegue definitivo sale de `main`. Mientras tanto no se hace ningún
  push a `main`.
- **FR5.4** Los modos actuales de red local, túnel temporal y modo prueba siguen funcionando igual que
  hoy, porque `2_Aplicacion_Reto/` no cambia (FR12.1).
- **FR5.5** Una versión de la nube que reescriba el servidor en otro lenguaje o runtime pasa la prueba
  común (FR12.3), incluidas las comprobaciones de FR6.3, y da los mismos puntos y la misma clasificación
  que `servidor.py` para las mismas respuestas.

Criterios de aceptación:

```gherkin
Given el servicio publicado y un reto en «inscripcion»
When un estudiante abre el enlace fijo desde datos móviles
Then ve la pantalla de inscripción igual que en red local

Given el computador del docente apagado
When el docente abre el panel desde otro equipo con su clave
Then puede abrir, cerrar y publicar el reto

Given un reto en curso
When la persona del semillero sigue la guía de despliegue
Then el primer paso de la guía le pide abrir el panel y confirmar que el estado es «inscripcion»
    sin participantes o «resultados», y no seguir si no lo es
```

### FR6. Corregir las fugas de respuestas antes de «resultados» (Q7-A)

- **FR6.1** `GET /api/publico` no entrega, mientras el reto no esté en `resultados`, ningún campo del
  experimento que revele o permita deducir el veredicto de cada publicación: ni
  `experimento.por_publicacion[].verdad` ni `multitud_acierta` (hoy salen ya en `cerrado`,
  `servidor.py:433-434`; `code-quality-assessment.md`, hallazgo S2). Lo que el tablero muestra en
  «cerrado» sin esos campos se conserva; si el tablero usa alguno en «cerrado», el contrato de la API
  lo lista.
- **FR6.2** Los identificadores de opciones, ítems y partes que llegan al navegador por `/api/estado`
  son opacos: no contienen el texto, la posición en el banco ni ningún dato derivado de la clave, y su
  orden de envío no es el orden de autoría del banco. La corrección se hace en el servidor, sin editar
  `banco_preguntas.json` ni el script que lo genera (archivo generado y fuera de alcance), y sin
  cambiar lo que el estudiante ve. La base de datos y `respuestas.csv` siguen guardando los
  identificadores del banco (el servidor traduce al recibir), para que FR4.3 no cambie.
- **FR6.3** La prueba común (FR12.3) tiene una comprobación por cada fuga: falla con el código de hoy
  y pasa con el corregido. `simulacro.py` no cambia (FR12.1), y sus 29 comprobaciones se conservan sin
  debilitarse.

```gherkin
Given un reto en «cerrado» con respuestas del Exp. 01
When el tablero pide GET /api/publico
Then la respuesta no contiene «verdad» ni «multitud_acierta» en el experimento

Given un reto en «resultados»
When el tablero pide GET /api/publico
Then la respuesta contiene el experimento completo, igual que hoy

Given el reto abierto y un participante inscrito
When pide GET /api/estado
Then ningún identificador de opción, ítem o parte coincide con el identificador del banco
And para cada pregunta de 3 o más opciones, en al menos una de 20 inscripciones el orden enviado
    difiere del orden del banco
And la calificación de una respuesta correcta da los mismos puntos que hoy
And respuestas.csv guarda los identificadores del banco
```

### FR7. Refactor con arquitectura validada

El título se mantiene, pero cambia a quién aplica: estos requisitos son para el código de cada versión
de la nube. La versión local no se refactoriza (FR12.1).

- **FR7.1** La forma de separar las reglas del reto (calificación, bono, clasificación, reloj y
  vencimiento, experimento, versión pública del examen, transiciones de estado, validación del banco)
  del acceso a la base, la red y el reloj la decide un ADR. Ese ADR compara al menos dos alternativas,
  cada una con su costo, y explica por qué elige una. Se cumple si cada regla de esa lista tiene
  pruebas unitarias que corren sin servidor ni base (NFR12). Antes este punto exigía «funciones puras
  sin SQL, HTTP ni `time.time()`»: venía del pedido inicial y no de una necesidad del problema
  (decisión del humano, 2026-10-25), así que pasa a ser una opción más dentro del ADR.
- **FR7.2** Cada ruta HTTP tiene su nivel de acceso (público, token o clave docente), y una ruta sin nivel declarado no responde. Cómo se despachan las rutas (por ejemplo, una
  tabla en vez de cadenas de `if`) lo decide el ADR con la misma comparación que FR7.1.
- **FR7.3** El ADR también decide si se crea una capa aparte para la base de datos. Solo se justifica
  si hay al menos dos implementaciones reales.
- **FR7.4** El servidor rechaza las transiciones de estado del reto que el panel nunca ofrece. Las que
  el panel ofrece hoy siguen permitidas. Hoy el servidor acepta cualquiera (`architecture.md`, «Flujo
  de estados del reto»). Motivo: pasar de `resultados` a `abierto` reabriría las respuestas después de
  mostrar la revisión con la clave (`code-quality-assessment.md`, hallazgo S5), así que es una
  corrección de fuga y no un cambio visible. La lista exacta sale de los botones del panel en `web/js/`,
  y cómo se valida lo decide el diseño.
- **FR7.5** Se entrega una lista priorizada de refactors, cada uno con su riesgo y la prueba que lo
  cubre (pedido inicial, punto 5).
- **FR7.6** Código, identificadores y docstrings en español, en cualquier lenguaje. Las versiones en
  Python manejan sus dependencias con uv (`pyproject.toml` + `uv.lock`). Cada paquete nuevo, en
  cualquier lenguaje, requiere aprobación del humano (decisión del humano, 2026-10-25, que reemplaza
  «sin dependencias nuevas en la app»).

### FR8. Documentación para el despliegue

- **FR8.0** Mientras se comparan, cada carpeta de opción tiene su propio `LEEME.md` con los pasos para
  desplegarla. `PUBLICAR_EN_INTERNET.md` se reescribe solo para la opción ganadora (FR12.5).
- **FR8.1** `PUBLICAR_EN_INTERNET.md` describe los pasos del nuevo despliegue para la persona del
  semillero que lo crea (Q6-A), como pasos numerados que no exigen escribir código, y lo que el docente
  hace el día del reto: abrir el enlace fijo y usar el panel con su clave. Pasa si alguien del
  semillero que no participó en el diseño despliega siguiendo solo la guía.
- **FR8.2** La guía incluye la prueba de humo antes del reto, cómo volver a la versión anterior y el
  cierre del reto (NFR10.1): primero el respaldo con nombres en el lugar privado del semillero y después
  el borrado en la nube, incluidas las copias de seguridad que guarda «Reiniciar». Los CSV descargados
  se guardan en ese lugar privado y nunca en el repositorio, que es público.
- **FR8.3** La guía corrige la frase de que el reloj y la clasificación viven solo en memoria: hoy salen
  de SQLite (`architecture.md`, «Dónde vive cada pieza de estado»).

### FR9. Datos del semillero organizados (pedido del humano, 2026-10-25)

Hoy el panel descarga dos CSV sueltos (resultados y respuestas, `servidor.py`, funciones de exportación)
y «Reiniciar» guarda una copia de la base. No hay metadatos que digan de qué reto, banco o versión salió
cada archivo, ni un diccionario de las columnas.

- **FR9.1 Paquete de respaldo por reto.** El panel docente ofrece una descarga más, un `.zip` con nombre
  `AAAA-MM-DD_<sala>_reto.zip`, que contiene:
  - `participantes.csv`, `respuestas.csv`, `eventos.csv` y `colegios.csv` (la lista de FR10.3), uno
    por tabla de la base;
  - la copia completa de los datos del reto que define FR4.3. En las opciones con SQLite es
    `reto.db`, hecha con `VACUUM INTO` como hoy en «Reiniciar»;
    en las demás es el formato de su ADR;
  - `metadatos.json`, con la fecha y hora de inicio y fin del reto, la sala, el nombre del evento, la
    duración, el número de participantes, la versión (huella) del banco y la versión de la app.

  Los dos CSV que existen hoy no cambian de columnas ni de formato, para no cambiar lo que el docente ya
  usa (Out of scope). El paquete es lo que se guarda en el lugar privado del semillero (NFR10.1).
- **FR9.2 Formato estable.** En el paquete, los CSV van en UTF-8 y con encabezado. Las fechas van en ISO
  8601 con zona horaria (`2026-11-03T08:15:00-05:00`) y los decimales con punto. Cada fila lleva el
  identificador estable del participante y de la pregunta del banco, nunca el identificador opaco de
  FR6.2. Así se pueden unir tablas y retos sin ambigüedad.
- **FR9.3 Diccionario de datos.** El repositorio guarda `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`
  (nombre por confirmar en el diseño), sin datos de participantes. Describe cada archivo del paquete y
  cada columna: tipo, unidades, valores posibles y de dónde sale.
- **FR9.4 Organización en el Drive del semillero** (decisión del humano, 2026-10-25). La guía de
  cierre (FR8.2) indica una carpeta compartida del semillero con acceso restringido. Dentro va una
  carpeta por año y en ella un `.zip` por reto, sin cambiarle el nombre, así quedan ordenados por fecha.

- **FR9.5 Solo el docente descarga** (decisión del humano, 2026-10-25). El paquete se sirve solo por una
  ruta `/api/admin/*`. Lo descarga quien tenga la clave docente (NFR9). La
  clave viaja en la cabecera `X-Clave-Admin`. Sin clave o con una clave incorrecta, la respuesta es 403 y no trae datos.
  El paquete nunca lleva ninguna clave. `participantes.csv` tampoco trae el `token` de sesión de cada
  participante.

```gherkin
Given un reto en «resultados»
When alguien pide el paquete sin la clave docente o con una clave incorrecta
Then el servidor responde 403 y no entrega ningún dato
```

```gherkin
Given un reto en «resultados» con 40 participantes
When el docente descarga el paquete del semillero
Then el .zip se llama con la fecha y la sala del reto
And trae participantes.csv con 40 filas, respuestas.csv, eventos.csv, la copia completa de los datos de la sala y metadatos.json
And metadatos.json trae la huella del banco y la versión de la app con que se jugó
And cada columna del paquete aparece en el diccionario de datos
```

### FR10. Datos limpios desde la entrada (pedido del humano, 2026-10-25)

Hoy `registrar` en `servidor.py` ya quita espacios de sobra, recorta el largo, exige un nombre de al
menos 3 letras, exige grado 9, 10 u 11 y rechaza un nombre repetido en el mismo colegio y grado. Le
falta lo siguiente: el colegio puede llegar vacío si alguien salta el navegador, no se normaliza Unicode
y no se quitan caracteres de control ni invisibles. Además, el mismo colegio escrito de varias formas
(«IE San José», «colegio san jose») queda como si fueran colegios distintos; FR10.3 lo resuelve con una
lista cerrada.

- **FR10.1 Validar en el servidor, no solo en el navegador.** Toda regla de los campos de inscripción
  (obligatorio, largo, valores permitidos) se valida en el servidor. Se valida igual aunque la petición no
  venga de `web/js/`. Se agrega la regla «colegio obligatorio, al menos 3 letras», que hoy solo exige el
  navegador (excepción aprobada por el humano, 2026-10-25). Se usa el mismo estilo de mensaje que ya
  existe.
- **FR10.2 Normalizar el texto.** Antes de validar y guardar, cada texto pasa por estos pasos:
  - forma Unicode NFC;
  - quitar caracteres de control e invisibles (ancho cero, por ejemplo);
  - juntar espacios repetidos;
  - recortar al largo de hoy (60 el nombre, 200 los integrantes; 80 cada colegio de la lista).

  El texto se guarda como lo escribió la persona después de esa limpieza: no se cambian mayúsculas ni
  tildes, porque el tablero lo muestra (conducta visible).
- **FR10.3 Colegio de una lista cerrada** (decisión del humano, 2026-10-25, excepción aprobada a «no
  cambiar la conducta visible»). En «inscripción», antes de abrir el reto, el docente carga
  desde su panel la lista de colegios que participan; si falta uno el día del reto, lo agrega en ese
  momento (revisión del 2026-10-25: con un solo docente ya no hay catálogo del semillero ni colegios
  «provisionales»). La sala mezcla equipos de varios colegios, cada uno con su reloj (FR3.1, FR11). En la pantalla de inscripción, el campo «Colegio» deja de ser
  texto libre y pasa a ser una lista para elegir. El servidor guarda el identificador del colegio, y
  rechaza cualquier valor que no esté en la lista. El nombre del colegio se muestra igual que está
  escrito en el catálogo. El control de nombre repetido compara el identificador del colegio en lugar del texto
  (excepción aprobada «repetido por clave»). Cómo se carga la lista (pegar un nombre por línea, subir un
  CSV) y qué pasa si falta un colegio el día del reto se fija en el diseño.
- **FR10.4 Integrantes como lista.** El servidor normaliza los integrantes así: los separa por comas,
  limpia cada nombre con FR10.2, quita los vacíos y los vuelve a unir con «, ». El paquete de FR9 los
  trae además contados (`n_integrantes`).
- **FR10.5 Las reglas se prueban solas.** La normalización y la validación tienen pruebas unitarias que
  corren sin servidor ni base. En Python se escriben con `unittest`; en otro lenguaje, el runner de
  pruebas se elige en el ADR de esa opción y requiere aprobación. Cada regla tiene un caso válido y al
  menos dos inválidos (NFR12, `phases/construction.md`, «Testing Standards»).

```gherkin
Given el formulario de inscripción
When llega al servidor un colegio vacío o solo con espacios
Then el servidor responde con un mensaje de error y no crea el participante

Given un nombre con espacios dobles y un carácter de ancho cero
When el participante se inscribe
Then se guarda el nombre sin el carácter invisible y con un solo espacio
And el tablero lo muestra con las mismas mayúsculas y tildes que escribió

Given el docente cargó la lista «IE San José» y «Colegio Nacional»
When un estudiante se inscribe
Then elige su colegio de esa lista y no puede escribir otro
And si una petición trae un colegio que no está en la lista, el servidor la rechaza
```

### FR11. Una sola sala, un solo docente, un reloj por colegio (revisión del 2026-10-25)

Reemplaza el FR11 anterior («varios retos en paralelo, uno por sala»). El humano: «esto lo controla un
solo profesor en un solo panel. no con varios profesores con varios paneles. es solo una sala.» A la
sala entran equipos de varios colegios y cada colegio tiene su propio reloj (FR3.1). Este cambio se
aprueba como excepción a «no cambiar la conducta visible», solo en lo que diga cada punto de abajo.

- **FR11.1 Un enlace, una sala.** El servicio lleva un solo reto a la vez, con un solo estado
  (inscripción → abierto → cerrado → resultados), una sola configuración (modo sorpresa,
  retroalimentación, nombre del evento) y un código de sala. Ese código lo fija el docente y los
  estudiantes lo escriben al inscribirse, como hoy (reglas de negocio, §3).
- **FR11.2 Varios colegios en la sala.** Los equipos eligen su colegio de la lista (FR10.3). El colegio
  agrupa a los equipos para el reloj (FR3.1); la calificación, el orden total, el reparto A/B del
  experimento y la publicación de resultados son de toda la sala.
- **FR11.3 Pantalla del estudiante igual.** Lo único nuevo que ve es el aviso de espera mientras su
  colegio no ha arrancado (FR3.1).
- **FR11.4 Un tablero.** Un solo tablero público con el podio general y la clasificación por grado
  (FR2.5). El docente lo proyecta.
- **FR11.5 Un panel, una clave.** Un solo panel docente con una sola clave (NFR9). Lo nuevo del panel:
  la lista de colegios con el estado de su reloj (sin arrancar, minutos que quedan, vencido) y el botón
  «Arrancar reloj» de cada colegio, con confirmación.
- **FR11.6 Datos de la sala.** El paquete de FR9 es uno por reto, con su fecha y su código de sala.
  «Reiniciar» borra el reto entero tras escribir BORRAR y guarda antes una copia automática.
- **FR11.7 Sin regresión.** Con un solo colegio arrancado al abrir, el reto se comporta como hoy con el
  reloj global. La prueba común (FR12.3) agrega un caso con dos colegios arrancados a distinta hora que
  verifica que cada uno tiene sus 90 minutos y que el bono se mide desde el arranque de su colegio.

```gherkin
Given una sala con equipos de «IE San José» y «Colegio Nacional»
And el docente abre el reto cuando solo «IE San José» tiene equipos listos
When «Colegio Nacional» llega 10 minutos tarde y el docente pulsa su «Arrancar reloj»
Then los equipos de «Colegio Nacional» tienen 90 minutos desde ese momento
And al vencer los 90 minutos de «IE San José» solo se entregan sus equipos
And el podio del tablero se calcula entre todos los equipos de los dos colegios
```

### FR12. Un despliegue por opción y comparación al final (decisión del humano, 2026-10-25)

- **FR12.1 La versión local no cambia.** Ningún commit de esta intención modifica `2_Aplicacion_Reto/`,
  incluidos `servidor.py`, `web/`, los lanzadores y `pruebas/simulacro.py`. Se comprueba con
  `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/`, que debe salir vacío. `c87c80d` es el último
  commit de `develop` antes de esta decisión, ya con el formato de ruff aplicado. El comando mira solo
  commits: el cambio pendiente, solo de fin de línea, en `INICIAR_RETO_INTERNET.bat` queda sin
  commitear y fuera de esta intención. La única excepción posible es la de OQ9, si el humano la aprueba.
- **FR12.2 Una carpeta por opción.** Cada opción vive en su propia carpeta bajo `despliegues/`, en
  `develop` (estructura ya creada, ver `despliegues/LEEME.md`). Son cinco opciones, las cuatro del
  pedido inicial (punto 3) más GitHub Pages, que pidió el humano en esta etapa:

| Opción | Carpeta | Del pedido |
|---|---|---|
| Cloudflare Workers + un Durable Object con SQLite | `cloudflare/` | a |
| Cloudflare Containers con el `Dockerfile` actual | `cloudflare-containers/` | b |
| Google Apps Script + Google Sheets | `apps-script/` | c |
| Render con Docker y disco persistente (línea base) | `render/` | d |
| GitHub Pages para las pantallas, con la API en otro servicio | `github-pages/` | pedido en esta etapa |

  Ninguna carpeta depende de otra. Las pantallas de `web/` se pueden reutilizar copiándolas, sin cambiar
  lo que ve el estudiante (FR4.2). Cloudflare Containers volvió a la lista porque estaba en el pedido
  inicial y se había quitado sin motivo. Si el humano la descarta, se borra su carpeta y se anota aquí
  por qué.
- **FR12.2c Solo Cloudflare se construye** (revisión del 2026-10-25; el humano: «lo referente solo a
  cloudflare»). Solo la opción `cloudflare/` se construye, se prueba y queda lista para desplegar. Las
  demás quedan en la tabla de comparación así:
  - Render y Cloudflare Containers: solo con datos de la documentación oficial, ya cargados (U15, U16).
  - Google Apps Script: «no pasa», con el motivo ya registrado en Contract Design.
  - GitHub Pages: «no se construye», por esta decisión; su carpeta queda solo con su `LEEME.md`.

  La elección de FR12.6 se hace con esa tabla; si Cloudflare pasa todo, es la elegida sin respaldo
  construido.
- **FR12.2a Costo durante la comparación.** Ninguna opción genera cargos sin que el humano apruebe antes
  el monto y un tope. Render con disco es de pago según `render.yaml` («plan de pago más barato (lo
  necesario para tener disco)»). Mientras ese pago no se apruebe, Render entra en la tabla solo con
  datos de la documentación oficial y marcado «no cumple NFR6», sin desplegarse. Lo mismo vale para
  cualquier otra opción cuyo plan gratuito no alcance.
- **FR12.2b Qué se aprueba antes de construir.** Cada opción tiene su propio ADR, aprobado por el humano
  antes de escribir su código, con lenguaje, runtime, dependencias con versión exacta, herramientas de
  prueba y la forma de su copia de datos (FR4.3). Ese ADR cuenta como la aprobación de sus
  dependencias. El ADR final de FR12.5 es aparte y solo elige.
- **FR12.3 La misma prueba para todas.** Una prueba común, nueva y fuera de `2_Aplicacion_Reto/`
  porque esa carpeta no cambia, corre contra la URL de cada versión desplegada. Tiene dos partes:
  - **Parte base:** las mismas comprobaciones de las 29 de `simulacro.py 40`, sin debilitar ninguna.
  - **Parte nueva:** las comprobaciones de las fugas (FR6.3) y de los relojes por colegio (FR11.7), la medición de
    NFR2 y NFR3, un reinicio a mitad de la prueba (NFR4) y el arranque en frío (NFR5).

  Contra la versión local se espera esto: la parte base da «TODO BIEN», igual que `simulacro.py`, y así
  se valida la prueba común. Las comprobaciones de fugas fallan mientras OQ9 no se apruebe, y pasan si
  se aprueba y se corrigen. Las de relojes por colegio no aplican, porque la versión local tiene un solo reloj.
  Contra cada versión de la nube, las dos partes tienen que dar «TODO BIEN».
- **FR12.4 Tabla de comparación.** Al final, una tabla (`despliegues/COMPARACION.md`) pone las cinco
  opciones lado a lado con lo que midió la prueba común. Las filas son:
  - si pasa la prueba («TODO BIEN»);
  - la latencia p95 al responder y del tablero;
  - si sobrevive al reinicio;
  - el arranque en frío;
  - el consumo frente a la cuota gratuita, con la URL oficial;
  - el costo en US$;
  - las piezas, servicios y líneas de código;
  - los pasos que sigue la persona del semillero para desplegar.
- **FR12.5 Qué es «pasa todo».** Una opción pasa todo cuando cumple cada NFR según la tabla de abajo.

| NFR | Cómo se da por cumplido en cada opción |
|---|---|
| NFR1 Carga | Prueba común con 40 equipos de 3 colegios arrancados a distinta hora |
| NFR2, NFR3 Rapidez | Prueba común: p95 medido contra la URL |
| NFR4 Persistencia | Prueba común: reinicio a mitad de la prueba, sin perder datos |
| NFR5 Arranque en frío | Prueba común: primera petición tras dormir |
| NFR6 Costo | Documentación oficial citada con URL y consumo medido en la prueba ≤ 50 % de la cuota |
| NFR7 Operación | Alguien del semillero que no la construyó la despliega solo con su `LEEME.md` |
| NFR8 Confidencialidad | Prueba común: comprobaciones de fugas (FR6.3) |
| NFR9 Claves | Prueba común: 403 con clave ausente, incorrecta o en la URL; revisión del código en el PR |
| NFR10, NFR10.1 Datos personales | Se sigue la guía de cierre y se comprueba que el proveedor no queda con filas ni archivos de participantes |
| NFR11 Orden total y tiempo | Prueba común: mismos puntos y misma clasificación que la versión local con las mismas respuestas |
| NFR12 Mantenibilidad | Cobertura medida con la herramienta del ADR de la opción |

- **FR12.6 Cómo se elige.** Entre las opciones que pasan todo, gana la más simple, comparando en este
  orden y pasando al siguiente criterio solo si hay empate (`project.md`, «Corrections»):
  1. menos servicios externos;
  2. menos piezas propias que desplegar;
  3. menos líneas de código.

  Si persiste el empate, decide el humano con la tabla. El humano aprueba la elección en un ADR. Ese ADR
  nombra también la **alternativa de respaldo**: la segunda opción que pasa todo, que conserva su
  carpeta, su ADR y su fila en la tabla. Las carpetas de las demás opciones se borran en un commit
  propio, después de esa aprobación. Si ninguna opción pasa todo, se aplica OQ2.

```gherkin
Given las versiones desplegadas, cada una con su enlace
When se corre la prueba común contra cada enlace
Then cada versión obtiene su fila en la tabla de comparación con los mismos criterios
And git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/ sale vacío
And gana la versión que pasa todo según FR12.5 y queda primera en el orden de FR12.6
And la segunda que pasa todo conserva su carpeta como respaldo
```

## Non-functional requirements

Cada versión de la nube se mide contra estos requisitos con la prueba común (FR12.3). La versión local
no se vuelve a medir: queda como línea base.

- **NFR1 Carga.** Un solo reto a la vez (FR11, revisión del 2026-10-25; vuelve a valer Q9-A, «un
  solo reto a la vez»). Hasta 40 equipos al mismo tiempo, cada uno en su computador, de varios colegios;
  lo normal son unos 25 (Q1). El diseño se prueba con 40 equipos de 3 colegios cuyos relojes arrancan a
  distinta hora, durante 90 minutos, con el tablero pidiendo cada 2 s.
- **NFR2 Rapidez al responder.** Con 40 participantes activos, en el 95 % de los envíos pasa ≤ 1 s
  desde que el estudiante pulsa «Enviar» hasta que ve «Respuesta guardada» (Q3-A). Se mide como el
  tiempo de ida y vuelta de `POST /api/responder` más el `GET /api/estado` que le sigue, desde un
  cliente contra el servicio desplegado.
- **NFR3 Rapidez del tablero.** Con 40 participantes activos, el 95 % de los `GET /api/publico`
  completa en ≤ 1,5 s, con el tablero pidiendo cada 2 s (Q3-A).
- **NFR4 Persistencia.** Ninguna respuesta, puntaje ni entrega que haya recibido respuesta 200 se
  pierde por un reinicio, un despliegue o que la instancia se duerma. Se verifica reiniciando el
  servicio a mitad de un simulacro y comprobando que puntajes, respuestas y clasificación quedan iguales.
- **NFR5 Arranque en frío.** Si el hosting duerme la instancia, la primera petición tras despertar
  responde en ≤ 30 s (propuesta, no salió de tus respuestas; se confirma en el ADR) y la guía indica abrir el enlace unos minutos antes del reto para despertarla. La
  cifra exacta se fija en el ADR con la documentación oficial del hosting elegido.
- **NFR6 Costo.** US$ 0: solo planes gratuitos (Q5-A). Con pocos retos al año (Q2-A), el servicio puede
  quedar inactivo meses sin generar cargos ni perder la configuración. Cada límite y cuota del plan
  gratuito se verifica en la documentación oficial actual y se cita con su URL en el ADR. El ADR estima
  el consumo de una sesión de 90 minutos con 40 participantes (peticiones, escrituras, tiempo de
  cómputo) y muestra que usa como máximo el 50 % de la cuota diaria o mensual que aplique, y dice qué
  pasa si la cuota se agota a mitad del reto.
- **NFR7 Operación.** El docente no instala nada ni toca configuración: el día del reto abre el enlace y
  usa el panel con su clave. Crear y desplegar el servicio lo hace alguien del semillero siguiendo
  `PUBLICAR_EN_INTERNET.md` (Q6-A).
- **NFR8 Confidencialidad de respuestas.** Ninguna respuesta correcta, veredicto ni dato del que se
  pueda deducir la clave llega al navegador antes de `resultados` (`project.md`, «Forbidden»; FR6). El
  banco con respuestas nunca se sirve como archivo estático.
- **NFR9 Claves.** Hay una sola clave, la del docente (revisión del 2026-10-25; antes había clave del
  semillero y clave de sala). Vive como secreto del hosting, tiene al menos 12 caracteres, se compara en
  tiempo constante, nunca se escribe en el repositorio ni en el registro (`project.md`, «Forbidden») y
  solo viaja en la cabecera `X-Clave-Admin`, nunca en la URL (`?clave=`). Abre todas las rutas
  `/api/admin/*`. Con una clave ausente o incorrecta, la respuesta es 403 y no trae datos.
- **NFR10 Datos personales.** Los datos de menores (nombre, colegio, grado, integrantes, respuestas)
  pueden quedar en servidores del proveedor fuera de Colombia si el acceso docente va con clave y los
  datos se borran al terminar el reto (Q8-A). La otra condición de Q8-A, «repositorio privado», ya no se
  cumple: el humano decidió el 2026-10-25 dejar el repositorio público (ver «Constraints»). El
  repositorio nunca contiene datos de participantes.
- **NFR10.1 Respaldo antes de borrar** (decisión del humano, 2026-10-25). Al terminar cada reto, antes de
  borrar nada en la nube, se descarga un respaldo completo y **con nombres** (los CSV de resultados y de
  respuestas y la copia completa de los datos de FR4.3) a un lugar privado del semillero, fuera del repositorio
  (el Drive del semillero con acceso restringido, FR9.4). Solo después se borran del proveedor los datos y las
  copias de seguridad que guarda «Reiniciar»; al final no queda en el proveedor ningún archivo ni fila
  con datos de participantes. La guía indica cada paso y quién lo hace.

```gherkin
Given un reto en «resultados»
When la persona del semillero sigue la guía de cierre
Then descarga los CSV y la copia completa de los datos al lugar privado del semillero
And comprueba que el respaldo abre y tiene una fila por participante
And solo entonces borra los datos de la nube
And el proveedor ya no tiene archivos ni filas con datos de participantes
```
- **NFR11 Orden total y tiempo del servidor.** La clasificación nunca empata y todo tiempo se mide con
  el reloj del servidor también en el hosting nuevo (`project.md`, «Mandated»).
- **NFR12 Mantenibilidad.** El código nuevo tiene un 80 % de cobertura de líneas.
  - En Python se mide con `trace` de la biblioteca estándar, las pruebas usan `unittest` y ruff revisa
    la complejidad ciclomática ≤ 10 (ADR-008).
  - En otro lenguaje, la herramienta de cobertura y el límite de complejidad los fija el ADR de esa
    opción, y cada herramienta requiere aprobación.

  Fuente: `team-practices.md`, «Testing Posture».

## Constraints

- **Tecnología.** La versión local sigue en Python con SQLite y no cambia. Cada versión de la nube usa
  el lenguaje, el runtime y la base que apruebe su ADR (FR12.2b): las de Python manejan sus dependencias
  con uv (`pyproject.toml` + `uv.lock`, Python 3.12), y SQLite es obligatorio solo en las opciones que
  lo usan. Las pantallas siguen en HTML/CSS/JS sin frameworks ni build. Cada dependencia nueva requiere
  aprobación (decisión del humano, 2026-10-25), y el ADR de cada opción cuenta como esa aprobación.
- **Sin código de producción de una opción hasta aprobar su ADR** (pedido inicial, aplicado a cada
  opción por FR12.2b). La estructura de carpetas y los `LEEME.md` no son código de producción.
- **Repositorio público** (decisión del humano, 2026-10-25, riesgo aceptado). `3_Guia_docente/` y
  `banco_preguntas.json` contienen todas las respuestas y quedan visibles en internet. La regla
  «el repositorio debe ser privado» deja de aplicar. Lo que el servidor protege (FR6, NFR8) sigue igual:
  ninguna respuesta llega al navegador antes de «resultados».
- **Archivos generados intactos.** No se editan `banco_preguntas.json`, `CLAVE_DE_RESPUESTAS.md` ni
  `1_Analisis_de_datos/` (pedido inicial, «Fuera de alcance»).
- **Invariantes** de `CLAUDE.md`: banco de 1.000 puntos con `exigir(...)`, respuestas fuera del navegador
  hasta publicar, una respuesta por pregunta, tiempo del servidor, orden total, no cambiar nada con un
  reto en curso.
- **Ramas y fusión.** Regla general: cada rama de trabajo (`feat/`, `fix/`, `refactor/`, `chore/`…) →
  PR a `develop` (despliegues de prueba), tantas veces como haga falta → cuando `develop` tiene la
  versión final desplegada y verificada, un PR final revisado de `develop` a `main` (FR5.3). Ningún push a
  `main` hasta entonces.
- **Solo la CI aprobada.** La única CI es la revisión de PR, `.github/workflows/revisar-pr.yml`
  (`team.md`, «Corrections»). Corre los ganchos de pre-commit y el simulacro, y revisa el tamaño del PR.
  Las demás pruebas corren en local antes del PR.
- **Máximo 400 líneas de código por PR** (`team.md`, «Corrections»). Solo quedan exentos los PR
  `style:` que dejan igual el árbol sintáctico (ADR-008). Cada opción se construye en varios PR
  pequeños a `develop`.
- **Prueba de aceptación.** En la versión local, `python3 pruebas/simulacro.py 40` desde
  `2_Aplicacion_Reto/` sigue terminando en «TODO BIEN» y nunca se debilita. En cada versión de la nube,
  la prueba común (FR12.3) termina en «TODO BIEN» tras cada cambio de su servidor.
- **Corte delgado primero, en cada opción.** Antes de construir todo, cada opción despliega una versión
  mínima que deja inscribirse y responder una pregunta, y se verifica con la parte correspondiente de la
  prueba común y con `GET /api/publico`. Para esta intención, esto reemplaza el criterio de
  `team-practices.md` («Walking Skeleton»), que medía el corte con `simulacro.py` en la versión local:
  esa versión ya no cambia, así que no prueba lo que se despliega. El humano aprueba **un punto de
  control por opción**, después de su corte delgado. Propuesta, no salió de tus respuestas: una opción
  que no pasa su corte delgado se registra en la tabla con el motivo y no se sigue construyendo.

## Assumptions

- **A1.** «Fuera de Colombia» es aceptable para cualquier región del proveedor elegido (Q8-A); no hay
  exigencia de región. Responsable: semillero.
- **A2.** El ranking público con nombres y colegios en `/tablero` se conserva tal cual: cambiarlo
  alteraría la conducta visible. Se documenta como riesgo de privacidad, no se corrige aquí.
- **A3.** El `time.sleep(0.6)` dentro del bloqueo global de `/api/entrar` (anti fuerza bruta) se puede
  sacar del bloqueo sin cambiar la conducta visible, porque solo retrasa la respuesta de un código
  incorrecto (`code-quality-assessment.md`, «Riesgos para publicar en la nube»). Si el diseño lo
  considera un cambio de conducta, se mantiene.
- **A4.** El revisor indica que ningún cliente de `web/js/` usa `?clave=`; si el contrato de la API lo
  confirma, se retira sin cambio visible (NFR9).
- **A5.** Corregir FR6.2 en el servidor (identificadores opacos por participante) no exige regenerar el
  banco. Si el diseño demuestra que no es posible sin tocar el banco, se vuelve a preguntar.
- **A6.** Las cifras de cuotas, precios y latencias de los proveedores no se toman de memoria; se
  verifican en la documentación oficial al evaluar las alternativas.

## Out of scope

- Cambiar preguntas, cifras, contenido pedagógico o el banco (pedido inicial).
- Cambiar pantallas, textos, puntajes, desempates o el flujo de estados (Practices Discovery Q1/Q8).
  Excepciones aprobadas por el humano el 2026-10-25: la lista cerrada de colegios, el mensaje de
  colegio obligatorio y el control de repetido por colegio (FR10.1, FR10.3), además de la descarga del
  paquete del semillero en el panel (FR9.1).
- Cualquier CI distinta de la revisión de PR ya aprobada (`.github/workflows/revisar-pr.yml`). Ruff ya
  se adoptó (ADR-008), así que deja de estar fuera de alcance.
- Cualquier cambio en `2_Aplicacion_Reto/` (FR12.1), salvo lo que se apruebe en OQ9.
- Entorno de ensayo en la nube aparte (Practices Discovery Q6).
- Reemplazar el sondeo (polling) por WebSockets o SSE, salvo que el ADR lo exija para cumplir NFR2-NFR3.

## Open questions

- **OQ1.** ¿Qué opción de hosting cumple a la vez US$ 0 (NFR6), persistencia sin pérdidas (NFR4), una
  sola instancia coherente para reloj y clasificación y las latencias de NFR2-NFR3? Ya no se responde
  solo con documentación: se responde desplegando las cinco opciones de FR12.2 y midiéndolas con la
  prueba común (FR12). Las opciones de pago no se despliegan sin aprobación (FR12.2a). Los límites y
  cuotas se siguen citando con su URL oficial. Para GitHub Pages, el ADR verifica en la documentación
  oficial que con GitHub Free exige repositorio público; el repositorio queda público por decisión del
  humano (ver «Constraints»). La elección sigue FR12.5 y FR12.6.
- **OQ2.** Si ninguna opción gratuita cumple todo, ¿qué se relaja? Se te preguntará en el diseño, no se
  decide aquí.
- **OQ3.** ¿Cómo se mide NFR2-NFR3 contra el servicio desplegado? Queda resuelta en parte por FR12.3:
  una prueba común nueva que apunta a una URL. El diseño fija cómo reemplaza las comprobaciones que hoy
  abren la base directamente (`simulacro.py` lee y cambia `config.abierto_en`). Cualquier mecanismo de
  prueba que mueva el reloj queda apagado en un despliegue real, o protegido con la clave docente.
  Si no se puede cumplir ninguna de las dos cosas, se descarta y la prueba espera el tiempo real, porque
  una ruta pública para mover el reloj rompería FR3.1 y NFR8.
- **OQ9.** La versión local tiene hoy las fugas de FR6: el veredicto en «cerrado» y los identificadores
  del banco. Al congelarla, las conserva, aunque `project.md` («Forbidden») prohíbe enviar respuestas
  al navegador antes de «resultados». ¿Se permite corregir solo esas fugas en `2_Aplicacion_Reto/`, con
  el simulacro en «TODO BIEN», como única excepción a FR12.1? Lo decide el humano.
- **OQ4.** Sobre qué módulos exactos se mide el 80 % de NFR12 y con qué comando de `trace`.
- **OQ5.** El tablero `/tablero` muestra en internet nombres y colegios de menores (A2). Q8-A aceptó
  guardar los datos en la nube, pero no mostrarlos en una página pública. Decisión del humano en la
  aprobación de esta etapa: se decide en el diseño; el ADR propone opciones para que el humano elija.
- **OQ6.** Un límite de intentos fallidos de la clave docente cambia la conducta del panel; se decide en
  el diseño si hace falta además de la clave larga de NFR9.
- **OQ7.** Lista de colegios (FR10.3): cómo la carga el docente y qué hace si el día del reto llega un
  estudiante de un colegio que no está en la lista. Se decide en el diseño.
- **OQ8.** Cerrada en la revisión del 2026-10-25: hay una sola sala y una sola clave docente (FR11,
  NFR9), así que no hay que crear salas ni repartir claves.

## Sources

- Initial description: `aidlc/spaces/default/intents/261024-publicar-reto-nube/project-description.json` (pedido inicial, puntos 1-6 y «Fuera de alcance»).
- Respuestas de esta etapa: `requirements-analysis-questions.md`, Q1-Q9.
- Prácticas afirmadas: `aidlc/spaces/default/intents/261024-publicar-reto-nube/inception/practices-discovery/team-practices.md`.
- Base de conocimiento del código: `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/business-overview.md`, `architecture.md`, `code-structure.md`, `api-documentation.md`, `code-quality-assessment.md`.
- Reglas del proyecto: `aidlc/spaces/default/memory/project.md`, `.claude/rules/python-code.md`.
