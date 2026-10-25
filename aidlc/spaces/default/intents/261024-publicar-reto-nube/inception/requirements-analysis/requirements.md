# Requisitos: publicar el reto en la nube y refactorizar el servidor

Intención `261024-publicar-reto-nube`, alcance `classic`, proyecto brownfield, profundidad Standard.
Las respuestas citadas como Q1-Q9 están en `requirements-analysis-questions.md` (misma carpeta); las
de Practices Discovery, en `aidlc/spaces/default/intents/261024-publicar-reto-nube/inception/practices-discovery/team-practices.md`.

## Intent analysis

**Qué se busca.** Que el reto «Detectives de la desinformación» se pueda jugar desde un **enlace fijo
en internet** que **no dependa del computador del docente**, **sin costo** (Q5-A), y que el servidor
quede **refactorizado** con una arquitectura validada: núcleo puro separado de la E/S y patrones
justificados por `.claude/rules/python-code.md` (pedido inicial, puntos 4 y 5).

**Por qué.** Hoy hay tres modos (`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/business-overview.md`,
«Contexto de despliegue actual»): red local y túnel temporal dependen del computador del docente;
Render con disco da enlace fijo pero es de pago (≈ US$ 7/mes según `PUBLICAR_EN_INTERNET.md`, cifra
por verificar en la documentación oficial). El servidor es un monolito de un archivo con lógica de
dominio, SQL, reloj y HTTP mezclados (`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/code-structure.md`,
«Mapa de secciones de `servidor.py`»), y un `RLock`, un hilo vigilante y un archivo SQLite de proceso
que obligan a una sola instancia con disco local (`aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/architecture.md`,
«Dónde vive cada pieza de estado»).

**Tipo de cambio.** Migración de despliegue + refactor interno con dos correcciones de confidencialidad, más tres
funcionalidades nuevas pedidas en esta etapa: datos organizados (FR9), entrada limpia (FR10) y varias
salas en paralelo (FR11).
Alcance: todo el sistema (servidor, despliegue, guía de publicación). Complejidad: estándar a alta por
el riesgo de integración (cambiar de hosting y de estructura a la vez), que es la razón del corte
delgado primero (`team-practices.md`, «Walking Skeleton»).

**Regla rectora.** No cambia la conducta visible del reto: pantallas, preguntas, puntajes, desempates
ni flujo de estados (Q1 y Q8 de Practices Discovery). Solo se permite corregir fugas de respuestas antes
de «resultados» (Q7-A).

## Functional requirements

Los requisitos FR1-FR4 fijan la **conducta que se conserva**; se verifican con
`python3 pruebas/simulacro.py 40` («TODO BIEN») sobre la versión nueva, sin debilitarlo.

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

### FR3. Conservar el reloj medido por el servidor

- **FR3.1** El tiempo de cada intento lo mide el servidor (reloj global por defecto o individual desde
  «Comenzar»); el navegador solo muestra la cuenta regresiva.
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
  reiniciar.

### FR5. Publicación con enlace fijo

- **FR5.1** El reto queda accesible desde un enlace HTTPS fijo que no cambia entre retos ni depende de
  que el computador del docente esté encendido.
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
- **FR5.5** Si la opción elegida exige reescribir el servidor en otro lenguaje o runtime, la versión de
  la nube debe pasar las mismas comprobaciones del simulacro (incluidas las de FR6.3) corriendo contra
  la URL desplegada, y dar los mismos puntos y la misma clasificación que `servidor.py` para las mismas
  respuestas.
- **FR5.4** Los modos actuales de red local, túnel temporal y modo prueba siguen funcionando para quien
  no tenga internet estable, salvo que el ADR justifique retirarlos.

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
- **FR6.3** El simulacro gana una comprobación por cada fuga, que falla con el código de hoy y pasa con
  el corregido. Las 29 comprobaciones existentes se conservan sin debilitarse.

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

- **FR7.1** La lógica de dominio (calificación, bono, clasificación, reloj y vencimiento, experimento,
  versión pública del examen, transiciones de estado, validación del banco al cargarlo) queda en
  funciones puras que reciben datos (incluido `ahora`) y devuelven datos, sin SQL, HTTP, `time.time()`
  ni variables de entorno (`.claude/rules/python-code.md`, «Diseño y patrones»).
- **FR7.2** Las rutas HTTP se despachan con una tabla de (método, ruta) a función, con el nivel de
  acceso (público, token, docente) como dato de la ruta, en vez de cadenas de `if`.
- **FR7.3** Se crea un puerto de persistencia solo si la opción elegida en el ADR implica una segunda
  implementación real (por ejemplo SQLite local y otra base en la nube). Si no, no se crea la
  abstracción.
- **FR7.4** Las transiciones de estado del reto se validan con una tabla de transiciones permitidas.
  Las transiciones que el panel ofrece hoy siguen permitidas; las que el panel nunca ofrece se rechazan
  (hoy el servidor acepta cualquiera, `architecture.md`, «Flujo de estados del reto»). Motivo: pasar de
  `resultados` a `abierto` reabriría las respuestas después de mostrar la revisión con la clave
  (`code-quality-assessment.md`, hallazgo S5), así que es una corrección de fuga, no un cambio visible.
  La tabla exacta se fija en el diseño a partir de los botones de `web/js/` del panel.
- **FR7.5** Se entrega una lista priorizada de refactors, cada uno con su riesgo y la prueba que lo
  cubre (pedido inicial, punto 5).
- **FR7.6** Código, identificadores y docstrings en español. La app puede tener dependencias, manejadas
  con uv (`pyproject.toml` + `uv.lock`); cada paquete nuevo requiere aprobación del humano (decisión del
  humano, 2026-10-25, que reemplaza «sin dependencias nuevas en la app»).

### FR8. Documentación para el despliegue

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
  - `reto.db`, una copia consistente de la base (`VACUUM INTO`, como hoy en «Reiniciar»);
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
  ruta `/api/admin/*`, con la misma clave docente de los CSV de hoy. La clave viaja en la cabecera
  `X-Clave-Admin` (NFR9). Sin clave o con una clave incorrecta, la respuesta es 403 y no trae datos.
  El paquete nunca lleva la clave docente. `participantes.csv` tampoco trae el `token` de sesión de cada
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
And trae participantes.csv con 40 filas, respuestas.csv, eventos.csv, reto.db y metadatos.json
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
  cambiar la conducta visible»). En «inscripción», antes de abrir el reto, el docente carga en el panel
  la lista de colegios que participan en su sala; una sala puede mezclar estudiantes de
  varios colegios (decisión del humano, 2026-10-25). En la pantalla de inscripción, el campo «Colegio» deja de ser
  texto libre y pasa a ser una lista para elegir. El servidor guarda el identificador del colegio, y
  rechaza cualquier valor que no esté en la lista. El nombre del colegio se muestra igual que lo escribió
  el docente. El control de nombre repetido compara el identificador del colegio en lugar del texto
  (excepción aprobada «repetido por clave»). Cómo se carga la lista (pegar un nombre por línea, subir un
  CSV) y qué pasa si falta un colegio el día del reto se fija en el diseño.
- **FR10.4 Integrantes como lista.** El servidor normaliza los integrantes así: los separa por comas,
  limpia cada nombre con FR10.2, quita los vacíos y los vuelve a unir con «, ». El paquete de FR9 los
  trae además contados (`n_integrantes`).
- **FR10.5 Las reglas viven en el núcleo puro.** La normalización y la validación son funciones puras,
  sin E/S, probadas con `unittest`. Cada regla tiene un caso válido y al menos dos inválidos (NFR12,
  `phases/construction.md`, «Testing Standards»).

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

### FR11. Varios retos en paralelo, uno por sala (decisión del humano, 2026-10-25)

Hoy el servidor lleva un solo reto: en la tabla `config` hay un solo `estado`, una sola `sala` y una
sola duración (`servidor.py`, `inicializar_config`). Puede pasar que haya retos al mismo tiempo en
lugares distintos. Este cambio se aprueba como excepción a «no cambiar la conducta visible», solo en lo
que diga cada punto de abajo.

- **FR11.1 Un servidor, varias salas.** Con un solo enlace fijo hay varias salas, cada una con su
  código. Cada sala tiene su propio estado (inscripción → abierto → cerrado → resultados), su duración,
  su reloj y su configuración (modo sorpresa, retroalimentación, nombre del evento).
- **FR11.2 La sala separa todo.** Cada participante, respuesta y evento pertenece a una sala. Dentro de
  cada sala se aplican igual que hoy:
  - la calificación;
  - el orden total sin empates (NFR11);
  - el reparto alternado de los grupos A/B del experimento;
  - el control de nombre repetido (FR10.3);
  - la lista de colegios (FR10.3);
  - la publicación de resultados (FR6, NFR8).

  Publicar resultados en una sala no revela nada de otra sala.
- **FR11.3 Pantalla del estudiante igual.** El estudiante ya escribe el código de sala al inscribirse;
  con ese código entra a su sala. Su pantalla no cambia.
- **FR11.4 Tablero por sala.** Cada sala tiene su tablero público y su clasificación; no hay ranking
  general (decisión del humano). El docente proyecta el tablero de su sala.
- **FR11.5 Panel y claves por sala.** Cada docente maneja solo su sala con su propia clave. Una clave
  de una sala no lee ni cambia otra sala, y cualquier intento recibe 403. La clave general del
  semillero, configurada como secreto en el hosting (NFR9), crea y cierra salas, y entrega la clave de
  cada sala al docente que la va a usar. Estos son los cambios visibles del panel, aprobados como
  excepción.
- **FR11.6 Datos por sala.** El paquete de FR9 es por sala, se llama con su fecha y su código de sala
  y lo descarga quien tenga la clave de esa sala o la del semillero. «Reiniciar» y el borrado de
  NFR10.1 se aplican a una sala sin tocar las demás.
- **FR11.7 Sin regresión.** Un reto con una sola sala se comporta como hoy para el estudiante y el
  tablero. `simulacro.py 40` sigue terminando en «TODO BIEN» con una sala. Se agrega una prueba con
  varias salas a la vez que verifica que no se mezclan las clasificaciones, los relojes ni las
  respuestas. Esa prueba es nueva; `simulacro.py` no se debilita.

```gherkin
Given dos salas abiertas a la vez, «KQMT» en un colegio y «PRWX» en otro
When el docente de «KQMT» cierra su reto y publica resultados
Then «PRWX» sigue abierta con su propio reloj
And el tablero de «PRWX» no muestra a nadie de «KQMT»
And con la clave de «KQMT» no se puede descargar ni cambiar nada de «PRWX»
```

## Non-functional requirements

- **NFR1 Carga.** Puede haber varios retos en paralelo en lugares distintos, más de cinco salas a la
  vez (FR11). Contando a todas las personas de todas las salas, el máximo sigue siendo 40 al mismo
  tiempo, cada una en su computador; lo normal son unas 25 (Q1, Q9-A; decisión del humano,
  2026-10-25). Las salas son de tamaños distintos (por ejemplo, 5 personas en un colegio y 10 en otro).
  El diseño se prueba con 10 salas abiertas a la vez, de tamaños desiguales (de 1 a 10 personas), que
  suman 40 participantes durante 90 minutos. El 10 es una propuesta, no salió de tus respuestas; se confirma en el ADR. Cada sala abre
  su propio tablero, y el ADR suma esas peticiones al consumo de NFR6.
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
- **NFR9 Clave docente.** Las rutas `/api/admin/*` exigen la clave docente comparada en tiempo
  constante; la clave se configura en el hosting como secreto, nunca en el repositorio ni en el
  registro (`project.md`, «Forbidden»). La clave solo viaja en la cabecera `X-Clave-Admin`, no en la URL
  (`?clave=`), para que no quede en los registros del hosting, salvo que el contrato de la API muestre
  que `web/js/` la necesita. La guía pide una clave de al menos 12 caracteres.
- **NFR10 Datos personales.** Los datos de menores (nombre, colegio, grado, integrantes, respuestas)
  pueden quedar en servidores del proveedor fuera de Colombia si el acceso docente va con clave y los
  datos se borran al terminar el reto (Q8-A). La otra condición de Q8-A, «repositorio privado», ya no se
  cumple: el humano decidió el 2026-10-25 dejar el repositorio público (ver «Constraints»). El
  repositorio nunca contiene datos de participantes.
- **NFR10.1 Respaldo antes de borrar** (decisión del humano, 2026-10-25). Al terminar cada reto, antes de
  borrar nada en la nube, se descarga un respaldo completo y **con nombres** (los CSV de resultados y de
  respuestas y una copia de la base de datos) a un lugar privado del semillero, fuera del repositorio
  (el Drive del semillero con acceso restringido, FR9.4). Solo después se borran del proveedor los datos y las
  copias de seguridad que guarda «Reiniciar»; al final no queda en el proveedor ningún archivo ni fila
  con datos de participantes. La guía indica cada paso y quién lo hace.

```gherkin
Given un reto en «resultados»
When la persona del semillero sigue la guía de cierre
Then descarga los CSV y la copia de la base al lugar privado del semillero
And comprueba que el respaldo abre y tiene una fila por participante
And solo entonces borra los datos de la nube
And el proveedor ya no tiene archivos ni filas con datos de participantes
```
- **NFR11 Orden total y tiempo del servidor.** La clasificación nunca empata y todo tiempo se mide con
  el reloj del servidor también en el hosting nuevo (`project.md`, «Mandated»).
- **NFR12 Mantenibilidad.** 80 % de cobertura de líneas del código nuevo o tocado, medido en local con
  `trace` de la biblioteca estándar; pruebas nuevas con `unittest`; complejidad ciclomática ≤ 10 por
  función revisada a mano (`team-practices.md`, «Testing Posture» y «Code Style»).

## Constraints

- **Tecnología de la app.** Python con dependencias manejadas por uv (`pyproject.toml` + `uv.lock`, Python
  3.12) y SQLite; HTML/CSS/JS sin frameworks ni build. Cada dependencia nueva requiere aprobación
  (decisión del humano, 2026-10-25). Si la opción elegida
  exige otro lenguaje o runtime en la nube (por ejemplo JavaScript en Workers o Apps Script), el ADR
  debe decirlo y tu aprobación del ADR cuenta como esa aprobación.
- **Sin código de producción hasta aprobar el ADR** (pedido inicial).
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
- **Sin CI.** Las pruebas corren en local antes del PR; es una excepción explícita tuya
  (`team-practices.md`, «Testing Posture»).
- **Prueba de aceptación.** `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` termina en
  «TODO BIEN» tras cada cambio del servidor; nunca se debilita.
- **Corte delgado primero.** Una versión mínima (inscribirse y responder una pregunta) desplegada en el
  hosting elegido y verificada con el simulacro y `GET /api/publico` antes de migrar el resto
  (`team-practices.md`, «Walking Skeleton»).

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
- Configurar CI en la nube y adoptar linter o formateador (Practices Discovery Q5/Q7).
- Entorno de ensayo en la nube aparte (Practices Discovery Q6).
- Reemplazar el sondeo (polling) por WebSockets o SSE, salvo que el ADR lo exija para cumplir NFR2-NFR3.

## Open questions

- **OQ1.** ¿Qué opción de hosting cumple a la vez US$ 0 (NFR6), persistencia sin pérdidas (NFR4), una
  sola instancia coherente para reloj y clasificación y las latencias de NFR2-NFR3? Se responde en el ADR
  con la tabla comparativa y las URL oficiales. Además de las cuatro alternativas del pedido, la tabla
  incluye GitHub Pages para servir `web/` (pedido del humano en esta etapa), combinado con un backend en
  otro servicio, porque Pages solo sirve archivos estáticos. El ADR verifica en la documentación
  oficial: con GitHub Free, Pages exige repositorio público, y el repositorio queda público por
  decisión del humano (ver «Constraints»). Entre las opciones que cumplen todos los requisitos se elige la más parsimoniosa: la
  que tenga menos piezas, servicios y cambios de código.
- **OQ2.** Si ninguna opción gratuita cumple todo, ¿qué se relaja? Se te preguntará en el diseño, no se
  decide aquí.
- **OQ3.** ¿Cómo se mide NFR2-NFR3 contra el servicio desplegado, dado que `simulacro.py` levanta su
  propio servidor local? Se define en el diseño (por ejemplo, un modo del simulacro contra una URL).
- **OQ4.** Sobre qué módulos exactos se mide el 80 % de NFR12 y con qué comando de `trace`.
- **OQ5.** El tablero `/tablero` muestra en internet nombres y colegios de menores (A2). Q8-A aceptó
  guardar los datos en la nube, pero no mostrarlos en una página pública. Decisión del humano en la
  aprobación de esta etapa: se decide en el diseño; el ADR propone opciones para que el humano elija.
- **OQ6.** Un límite de intentos fallidos de la clave docente cambia la conducta del panel; se decide en
  el diseño si hace falta además de la clave larga de NFR9.
- **OQ7.** Lista de colegios (FR10.3): cómo la carga el docente y qué hace si el día del reto llega un
  estudiante de un colegio que no está en la lista. Se decide en el diseño.
- **OQ8.** Varias salas (FR11): cómo crea el semillero una sala y le entrega la clave al docente
  (panel del semillero, comando, lista fija en la configuración), cuántas salas puede haber a la vez como
  máximo y si una sala vencida se cierra sola. Se decide en el diseño, con el consumo de cuota de NFR6.

## Sources

- Initial description: `aidlc/spaces/default/intents/261024-publicar-reto-nube/project-description.json` (pedido inicial, puntos 1-6 y «Fuera de alcance»).
- Respuestas de esta etapa: `requirements-analysis-questions.md`, Q1-Q9.
- Prácticas afirmadas: `aidlc/spaces/default/intents/261024-publicar-reto-nube/inception/practices-discovery/team-practices.md`.
- Base de conocimiento del código: `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/business-overview.md`, `architecture.md`, `code-structure.md`, `api-documentation.md`, `code-quality-assessment.md`.
- Reglas del proyecto: `aidlc/spaces/default/memory/project.md`, `.claude/rules/python-code.md`.
