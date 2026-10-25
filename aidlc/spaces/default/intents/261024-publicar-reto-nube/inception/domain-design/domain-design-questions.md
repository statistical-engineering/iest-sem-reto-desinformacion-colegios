# Preguntas de Domain Design

Ya está fijado en los requisitos: un servidor con varias salas en paralelo (FR11), datos organizados por
sala (FR9), entrada limpia con lista cerrada de colegios (FR10), núcleo puro separado de la E/S y sin
abstracción prematura (FR7, `.claude/rules/python-code.md`). El hosting todavía no se elige: lo decide
el ADR. Aquí solo va cómo se parten los bloques del código y quién es dueño de cada dato.

## Q1. [Arquitectura] ¿En cuántos módulos se parte `servidor.py`?

Hoy `servidor.py` tiene 913 líneas que mezclan reglas, SQL, reloj y HTTP. Con salas, paquete de datos y
limpieza de entrada crece más. El tamaño de cada módulo decide cuántos PR de 400 líneas hacen falta y
qué tan fácil es probar cada parte.

A. Pocos módulos por capa: `nucleo/` (reglas puras: banco, calificación, clasificación, reloj,
   limpieza), `servicio` (casos de uso: salas, inscripción, respuestas), `persistencia` (SQLite),
   `exportacion` (CSV y paquete), `http` (tabla de rutas) y `arranque`
B. Un módulo por componente del dominio (unos 10-12 archivos pequeños)
C. Dejar un solo `servidor.py` ordenado por secciones, solo con las funciones puras separadas
X. Other (please specify)

[Answer]: A

## Q2. [Datos] ¿La lista de colegios es de cada sala o es un catálogo del semillero?

La lista cerrada de colegios (FR10.3) evita que el mismo colegio quede escrito de varias formas. Si es
de cada sala, cada docente la carga y un mismo colegio puede tener nombres distintos entre retos. Si
es un catálogo, el colegio tiene el mismo identificador en todos los retos y años, y los datos del
semillero se pueden unir sin limpiar a mano.

A. Catálogo del semillero: el semillero mantiene una lista única con un identificador por colegio;
   cada sala elige de esa lista cuáles participan
B. Lista de cada sala: el docente la escribe al crear el reto, sin catálogo compartido
C. Catálogo del semillero, y el docente puede agregar un colegio nuevo al catálogo desde su sala
X. Other (please specify)

[Answer]: A

## Q3. [Seguridad] ¿Cómo nace la clave docente de cada sala?

Cada sala tiene su propia clave y la clave general del semillero crea las salas (FR11.5). Hay que
decidir quién inventa la clave de cada sala.

A. El servidor la genera al crear la sala (larga y aleatoria) y se la muestra una sola vez al semillero
   para que se la entregue al docente
B. El semillero la escribe al crear la sala (mínimo 12 caracteres)
C. El servidor la genera y además el semillero la puede volver a generar si el docente la pierde
X. Other (please specify)

[Answer]: C

## Q4. [Arquitectura] ¿Cómo vence el tiempo de cada sala y de cada participante?

Hoy un hilo «vigilante» revisa cada 3 s quién se pasó del tiempo. Con varias salas, y en algunos
hostings que duermen la instancia o no permiten hilos, un hilo así no sirve. La otra forma es calcular
el vencimiento con la hora del servidor cada vez que llega una petición. El tiempo lo sigue midiendo
el servidor en los dos casos (NFR11).

A. Vencimiento al consultar: una función pura decide, con la hora del servidor, si una sala o un
   participante ya venció, y se aplica en cada petición que los toca; sin hilo
B. Mantener el hilo vigilante, uno para todas las salas
C. Las dos cosas: vencimiento al consultar y además un temporizador del hosting si existe
X. Other (please specify)

[Answer]: A

## Q5. [Datos] ¿Los datos de las salas van juntos o separados?

Cada sala debe poder descargarse, reiniciarse y borrarse sin tocar las demás (FR11.6, NFR10.1).

A. Una sola base con una columna de sala en cada tabla; borrar una sala es borrar sus filas
B. Un almacén separado por sala (un archivo o un objeto por sala); borrar una sala es borrar su
   almacén, y el catálogo de colegios y la lista de salas van en un almacén general
C. Lo decide el ADR según el hosting elegido; el dominio solo exige que cada dato tenga su sala
X. Other (please specify)

[Answer]: C

## Q6. [Seguridad] ¿Cómo se esconden los identificadores de las opciones (FR6.2)?

Hoy los identificadores de las opciones siguen el orden en que se escribió el banco, y de ahí se puede
adivinar la respuesta. Hay que dar a cada participante identificadores opacos y traducirlos de vuelta
al calificar; la base y los CSV guardan los del banco (FR6.2).

A. Derivarlos de la semilla del participante con una función pura (sin guardar nada nuevo)
B. Generarlos al azar al comenzar y guardar la tabla de traducción en la base
X. Other (please specify)

[Answer]: A

## Q7. [Arquitectura] El vencimiento al consultar (Q4-A) choca con la letra de FR3.2

FR3.2 dice que los intentos vencidos «se entregan solos, aunque ningún navegador haga peticiones, con a
lo sumo 5 segundos de retraso». Con Q4-A no hay hilo: el intento vencido se entrega en la primera
petición que lo toca (del estudiante, el tablero, el panel o una descarga). Hoy `finalizar` ya pone la
hora de entrega en el vencimiento exacto (`fin = min(ahora, inicio + duración)`) y el bono se mide con
la última respuesta, así que puntos, bono, clasificación y CSV salen iguales. Lo único que cambia es que
la fila en la base se escribe cuando alguien mira, no a los 3 s.

A. Reescribir FR3.2: «toda consulta ve como entregados los intentos vencidos, con la hora de entrega
   igual al vencimiento; no hace falta un proceso aparte»
B. Mantener FR3.2 tal cual y volver al hilo vigilante o a un temporizador del hosting (cambia Q4 a B o C)
X. Other (please specify)

[Answer]: A
