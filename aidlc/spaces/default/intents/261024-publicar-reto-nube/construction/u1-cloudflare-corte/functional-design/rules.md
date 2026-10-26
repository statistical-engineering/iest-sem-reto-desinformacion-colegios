# Reglas — U1 `u1-cloudflare-corte`

Las reglas del corte delgado. Salen de `requirements.md`, de `components.md` (domain-design/), del
contrato (`contract-summary.md`) y de la versión local (`servidor.py`, que define la conducta que no
cambia). Las respuestas de este diseño están en `functional-design-questions.md` (Q1 a Q5, todas A).
Revisadas con los hallazgos F-01 a F-13 de `reviews/review-01.md` (decisión del humano: «te dejo
potestad absoluta para decidir y corregir», 2026-10-25).

```yaml
rules:
  - id: BR1.1
    statement: 'Cada ruta declara su nivel de acceso en una tabla de rutas; una ruta que no está en la tabla da 404.'
    category: authorization
    applies_to: 'todas las rutas (tabla en functional-spec.md, «Rutas del corte»)'
    trigger: cada petición
    logic: 'IF la ruta no está en la tabla THEN 404; IF el nivel es token y no hay token válido THEN 401 «Sesión no encontrada. Vuelve a entrar con tu código.»; IF el nivel es clave y la clave no corresponde THEN 403'
    violation: '{error} con 401, 403 o 404, como hoy'
    source: FR7.2
  - id: BR1.2
    statement: 'Las claves llegan solo por la cabecera X-Clave-Admin y se comparan en mayúsculas, en tiempo constante.'
    category: authorization
    applies_to: 'rutas /api/admin/*'
    trigger: cada petición con clave
    logic: 'la clave se pasa a mayúsculas; IF tiene la forma <código>-<secreto> y existe la sala con ese código THEN el secreto se compara con su huella; IF tiene esa forma y la sala no existe THEN 403 con el mismo mensaje; ELSE se compara con la clave del semillero, que no lleva guion; ?clave= en la URL no se acepta'
    violation: '403 «Clave de docente incorrecta.»; nunca se registra la clave'
    source: 'FR7.2, FR9.5, FR11.5 (contrato C1, hallazgos C-03 y C-10)'
  - id: BR1.3
    statement: 'Con la clave de una sala solo se actúa sobre esa sala; con la del semillero hay que nombrar la sala.'
    category: authorization
    applies_to: 'rutas /api/admin/* de una sala'
    trigger: cada petición con clave
    logic: 'IF clave de sala y ?sala= distinto THEN 403; IF clave del semillero y falta ?sala= en una ruta de sala THEN 400 «Falta la sala.»'
    violation: 403 o 400 sin datos
    source: FR11.5
  - id: BR1.4
    statement: 'Los códigos que escribe una persona (sala y código personal) se comparan en mayúsculas y sin espacios, como hoy.'
    category: validation
    applies_to: 'POST /api/registro, POST /api/entrar, ?sala='
    trigger: cada petición con un código
    logic: 'código = texto limpio, recortado a 10 caracteres y en mayúsculas'
    violation: no aplica
    source: 'FR1.3, FR11.3 (hallazgo C-03)'
  - id: BR2.1
    statement: 'Crear una sala es solo del semillero; el servidor genera el código y la clave.'
    category: policy
    applies_to: 'POST /api/admin/salas/crear'
    trigger: el semillero crea una sala
    logic: 'IF la clave no es la del semillero THEN 403; ELSE código de 4 letras del alfabeto sin 0, O, 1 ni I (el ALFABETO de hoy), único en todo el servicio (si choca, genera otro); clave = <código>-<secreto> con secreto de 16 caracteres del mismo alfabeto; guarda solo la huella del secreto y devuelve la clave una vez'
    violation: 403
    source: 'FR11.5, ADR-003'
  - id: BR2.2
    statement: 'En el corte, la sala solo pasa de inscripción a abierto.'
    category: constraint
    applies_to: 'POST /api/admin/estado'
    trigger: el docente o el semillero cambia el estado
    logic: 'IF el nuevo estado es igual al actual THEN no hace nada y responde ok, como hoy; IF actual es inscripcion y nuevo es abierto THEN cambia y guarda la hora de apertura si no estaba; ELSE 400 «Ese cambio de estado llega en otra versión.» (U5 completa las transiciones)'
    violation: '400 con el motivo'
    source: 'FR7.4 (parcial; U5 lo completa)'
  - id: BR2.3
    statement: 'El docente agrega colegios provisionales a su sala, sin repetir nombres en el servicio.'
    category: validation
    applies_to: 'POST /api/admin/colegios con accion provisional'
    trigger: el docente agrega un colegio
    logic: 'IF el nombre normalizado ya existe THEN 400 con la clave «existente» (el colegio que ya existe); ELSE crea el colegio provisional y la sala lo ofrece'
    violation: 400 con el colegio existente
    source: 'FR10.3, ADR-002'
  - id: BR3.1
    statement: 'La inscripción exige sala abierta a inscripciones, nombre, colegio de la lista y grado válido.'
    category: validation
    applies_to: 'POST /api/registro'
    trigger: un estudiante se inscribe
    logic: 'en este orden: IF no existe la sala con ese código THEN 400 «El código de sala no es correcto. Míralo en el tablero.»; IF la sala no está en inscripcion ni abierto THEN 400 «Las inscripciones están cerradas.»; IF nombre limpio tiene menos de 3 caracteres THEN 400 «Escribe tu nombre (o el del equipo).»; IF grado no es 9, 10 u 11 THEN 400 «Elige el grado: 9, 10 u 11.»; IF colegio no es un id de la lista de la sala THEN 400 «Elige tu colegio de la lista.»'
    violation: 400 con el mensaje
    source: 'FR1.3, FR10.3, FR11.3'
  - id: BR3.2
    statement: 'No se repite un participante con el mismo nombre, colegio y grado en la sala.'
    category: constraint
    applies_to: 'POST /api/registro'
    trigger: un estudiante se inscribe
    logic: 'IF ya existe en la sala el mismo nombre (sin mayúsculas) con el mismo id_colegio y grado THEN 400 con el mensaje de hoy'
    violation: '400 «Ya hay alguien inscrito con ese nombre en ese colegio y grado…»'
    source: 'FR1.3, FR10.3'
  - id: BR3.3
    statement: 'El grupo A/B se alterna por orden de inscripción dentro de la sala.'
    category: calculation
    applies_to: 'POST /api/registro'
    trigger: un estudiante se inscribe
    logic: 'grupo = A si el número de inscritos de la sala es par, B si es impar; revisar y escribir sin cruzarse con otra inscripción de la misma sala'
    violation: no aplica
    source: 'FR1.3, components.md («Revisar y escribir sin cruzarse»)'
  - id: BR3.4
    statement: 'Cada inscrito recibe un código personal de 5 caracteres único en todo el servicio, un token y una semilla secretos.'
    category: policy
    applies_to: 'POST /api/registro y POST /api/entrar'
    trigger: un estudiante se inscribe o vuelve a entrar
    logic: 'código de 5 caracteres del ALFABETO; IF ya existe THEN genera otro; token de 24 bytes al azar; semilla de 8 bytes al azar; entrar con un código inexistente responde 404 después de una espera corta'
    violation: '404 «No encontramos ese código. Revísalo (son 5 caracteres).»'
    source: FR1.3
  - id: BR4.1
    statement: 'Comenzar guarda la hora del servidor.'
    category: calculation
    applies_to: 'POST /api/comenzar'
    trigger: el estudiante comienza
    logic: 'IF estado del participante no es registrado THEN no hace nada; IF la sala no está abierta THEN 400 «El reto todavía no ha empezado. Espera la señal del docente.»; inicio = hora de apertura de la sala si reloj_global, si no ahora; IF reloj_global y ahora >= inicio + duración THEN 400 «El tiempo del reto ya terminó.»'
    violation: 400 con el mensaje de hoy
    source: FR3.1
  - id: BR4.2
    statement: 'Antes de toda operación sobre un participante, se aplica la entrega por tiempo.'
    category: calculation
    applies_to: 'toda petición con token y toda acción sobre la sala'
    trigger: antes de responder, entregar, registrar un evento o consultar el estado
    logic: 'IF el participante está en_curso y ahora >= inicio + duración THEN entrega con motivo tiempo (BR4.3) una sola vez; el cierre de la sala lo agrega U5'
    violation: 'después de vencido, responder da 400 «Tu intento ya terminó.», como hoy'
    source: 'FR3.1, ADR-004'
  - id: BR4.3
    statement: 'Entregar cierra el intento con la hora de entrega, el tiempo usado y el bono.'
    category: calculation
    applies_to: 'POST /api/finalizar y la entrega por tiempo'
    trigger: el estudiante entrega o vence su tiempo
    logic: 'IF no está en_curso THEN no hace nada; fin = la menor entre ahora e inicio + duración; tiempo_usado = fin - inicio; tiempo_respuestas = segundos desde inicio hasta la última respuesta (o fin si no hay), con tope en la duración; bono = 20 x (puntos / 1.000) x (1 - tiempo_respuestas / duración); total = puntos + bono; estado finalizado con motivo entrega o tiempo'
    violation: no aplica
    source: 'FR3.1, FR2.2 (fórmula de hoy; U4 la vuelve «calculadora» con sus casos)'
  - id: BR4.4
    statement: 'Una salida de pantalla suma uno a las salidas del participante en curso.'
    category: calculation
    applies_to: 'POST /api/evento'
    trigger: el navegador avisa una salida
    logic: 'IF tipo es salida y el participante está en_curso THEN salidas + 1 y se registra el evento con la hora del servidor; siempre responde ok, como hoy'
    violation: no aplica
    source: 'FR4.1 (ruta que usa estudiante.js)'
  - id: BR5.1
    statement: 'Cada pregunta se responde una sola vez, en orden y solo si es visible para el grupo.'
    category: constraint
    applies_to: 'POST /api/responder'
    trigger: el estudiante responde
    logic: 'en este orden: IF el participante no está en_curso THEN 400 «Tu intento ya terminó.»; IF la sala no está abierta THEN 400 «El reto está cerrado.»; IF la pregunta no existe THEN 400 «Pregunta desconocida.»; IF no es visible para su grupo THEN 400 «Pregunta no disponible.»; IF ya respondida THEN 400 «Esa pregunta ya fue respondida.»; IF tiene requiere sin responder THEN 400 «Primero responde la parte anterior de esta misión.»; revisar y escribir sin cruzarse con otra operación de la misma sala'
    violation: 400 con el mensaje de hoy
    source: FR2.4
  - id: BR5.2
    statement: 'En el corte solo se califican preguntas de tipo opcion, sobre la variante del participante.'
    category: calculation
    applies_to: 'POST /api/responder'
    trigger: el estudiante responde
    logic: 'la pregunta se resuelve con la variante que da la semilla; IF tipo es opcion THEN la respuesta tiene que ser el id opaco de una de sus opciones, se traduce al id del banco y fraccion = 1 si coincide con la respuesta de la variante y 0 si no; IF la pregunta no tiene puntos THEN fraccion = 0; puntos = fraccion x puntos; IF otro tipo THEN 400 «Tipo de pregunta aún no disponible.»'
    violation: '400 «Respuesta incompleta o con formato no válido.» si el id no corresponde'
    source: 'FR2.4 (U4 completa FR2.1)'
  - id: BR6.1
    statement: 'Los ids de opciones, ítems y partes que salen al navegador son opacos y se calculan con la semilla del participante.'
    category: policy
    applies_to: 'GET /api/estado (misiones, respuestas y revision) y POST /api/responder'
    trigger: al armar el examen, al devolver respuestas y al recibir una
    logic: 'id opaco = «o» + los primeros 11 caracteres en base32 de HMAC-SHA256 con clave la semilla y mensaje pregunta_id|id del banco (ADR-006); IF dos ids de la misma pregunta coinciden THEN se usan 16 caracteres para esa pregunta; el orden se baraja con la semilla; al recibir se traduce de vuelta; respuestas[].respuesta y revision[].respuesta salen también opacos'
    violation: 'un id opaco que no corresponde da 400 «Respuesta incompleta o con formato no válido.»'
    source: 'FR6.2, ADR-006 (hallazgos C-02 y C-05)'
  - id: BR6.2
    statement: 'El examen público nunca trae respuesta, explicación ni tolerancia, y el dossier sigue bloqueado hasta su hipótesis.'
    category: policy
    applies_to: 'GET /api/estado'
    trigger: al armar las misiones
    logic: 'solo las claves de la lista blanca de hoy; revision solo en resultados para un participante finalizado'
    violation: no aplica
    source: 'FR4.1, NFR8'
  - id: BR6.3
    statement: 'El banco nunca se sirve como archivo y su copia se rechaza si no suma 1.000 puntos o si su versión no coincide.'
    category: validation
    applies_to: arranque y archivos estáticos
    trigger: al arrancar y al pedir un archivo
    logic: 'IF la copia del banco no suma 1.000 o su huella no coincide THEN el servicio no arranca; IF piden el banco por URL THEN 404'
    violation: 'no arranca / 404'
    source: 'NFR8, project.md («Mandated», 1.000 puntos)'
  - id: BR7.1
    statement: 'GET /api/publico sin ?sala= responde solo {"ok": true}; con ?sala= trae lo básico del tablero de esa sala.'
    category: policy
    applies_to: 'GET /api/publico'
    trigger: chequeo de salud o tablero
    logic: 'IF falta ?sala= THEN {ok: true}; ELSE evento, titulo, estado, sala, duracion_min, abierto_en, servidor_ahora, reloj_global y conteo de esa sala, con las claves de hoy; ranking y experimento llegan con U6'
    violation: '404 «No existe esa sala.» si el código no existe'
    source: 'FR5.1, FR11.4, contrato C1'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.4 | Acceso por ruta, claves y códigos en mayúsculas |
| BR2 | BR2.1–BR2.3 | Crear y abrir sala, colegios provisionales |
| BR3 | BR3.1–BR3.4 | Inscripción y códigos |
| BR4 | BR4.1–BR4.4 | Comenzar, entrega por tiempo, entregar y salidas |
| BR5 | BR5.1–BR5.2 | Responder y calificar `opcion` |
| BR6 | BR6.1–BR6.3 | Ids opacos y lo que nunca sale al navegador |
| BR7 | BR7.1 | Salud y tablero básico |

La copia de «Reiniciar» y el paquete sin `token`, `semilla`, `codigo` ni `clave_huella` (C-06) no entran en
el corte: los define U6 (`bolt-plan.md`, B11).
