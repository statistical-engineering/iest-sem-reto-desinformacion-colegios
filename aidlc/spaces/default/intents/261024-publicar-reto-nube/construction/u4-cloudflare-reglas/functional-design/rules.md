# Reglas — U4 `u4-cloudflare-reglas`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Las reglas valen para un solo reto con varios
> colegios, cada uno con su reloj (FR3.1, FR11, ADR-011). Cambian BR1.2, BR3.1, BR3.3, BR4.1 a BR4.4,
> BR5.3, BR5.4, BR6.1, BR6.2 y BR7.2; el 4.º criterio del orden pasa de `fin` a `tiempo_usado` (FR2.6).
> Nuevas: BR2.5 (redondeo), BR3.4 (por grado), BR4.5 a BR4.8 (relojes por colegio), BR5.5 (lista de
> colegios) y BR7.3 (caso obligatorio de dos colegios). Los ids que siguen valiendo no cambian.

Las reglas puras de la opción Cloudflare Workers: las seis «calculadoras» de ADR-001 con la forma del
contrato C4 (`contract-summary.md`, «C4. Forma de las reglas»). Salen de `requirements.md` (FR2, FR3,
FR6, FR7.1, FR7.4, FR10, FR11), de `components.md` (capa Reglas) y de `servidor.py`, que define la conducta
que no cambia. Las decisiones propias de la unidad están en `../decisions.md` (ADR-W6 a ADR-W9). Ninguna
regla lee la base ni el reloj: la hora llega como argumento, y ninguna escribe en el registro.

```yaml
rules:
  - id: BR1.1
    statement: 'Toda respuesta que sale al navegador o llega de él se traduce entre ids del banco e ids opacos segun el tipo de pregunta.'
    category: policy
    applies_to: 'Banco: respuesta_opaca y traducir_respuesta'
    trigger: 'al devolver respuestas y revision en /api/estado y al recibir /api/responder'
    logic: 'opcion texto a texto; multiple lista a lista; clasificar, compartir y recordatorio las claves del objeto (items o publicaciones) se traducen y los valores (categorias) quedan como estan; ordenar lista; construir las claves (partes) y los valores (opciones de esa parte) se traducen; texto, estimar y numero no se traducen; el ambito de items y publicaciones de m1_* es m1_posts, como en U1; IF algun id opaco no corresponde THEN traducir_respuesta devuelve null'
    violation: 'null, que reto.js convierte en 400 «Respuesta incompleta o con formato no válido.»'
    source: 'FR6.2, ADR-006, C-02 (ids opacos tambien en respuestas y revision)'
  - id: BR1.2
    statement: 'La revision de una pregunta en resultados trae la respuesta de la variante con ids opacos y su explicacion; nunca antes.'
    category: policy
    applies_to: 'Banco: revision_publica'
    trigger: 'U5 la llama en /api/estado solo con el reto en resultados y el participante finalizado'
    logic: 'revision_publica(banco, semilla, grupo) devuelve, por cada pregunta visible para el grupo, {respuesta: respuesta_opaca(...), explicacion}; la regla no decide cuando se llama: es pura, y la condicion la aplica quien la llama'
    violation: no aplica
    source: 'FR6.2, NFR8, estado_participante() de servidor.py'
  - id: BR1.3
    statement: 'El examen publico cubre los 10 tipos con la misma lista blanca de claves de hoy.'
    category: policy
    applies_to: 'Banco: examen_publico'
    trigger: al armar las misiones
    logic: 'las claves publicas son las de version_publica() de servidor.py (id, tipo, enunciado, puntos, unidad, min, max, paso, grafico, tabla, categorias, estilo, requiere, experimento, entero, simulador) mas opciones, publicaciones, items y partes con ids opacos; respuesta, explicacion, tolerancia, solo_grupo y variantes nunca salen'
    violation: 'una prueba de U1 falla («examen_publico no trae ninguna clave secreta»)'
    source: 'FR4.1, NFR8, BR6.2 de U1'
  - id: BR2.1
    statement: 'validar_respuesta acepta la misma forma por tipo que servidor.py y la devuelve normalizada.'
    category: validation
    applies_to: 'Calificacion: validar_respuesta'
    trigger: cada respuesta ya traducida a ids del banco
    logic: 'opcion texto que es id de una opcion; multiple lista de ids de opciones distintos, devuelta ordenada; clasificar, compartir y recordatorio objeto cuyas claves son exactamente los ids de items (o publicaciones) y cuyos valores son ids de categorias; ordenar lista con exactamente los ids de items; construir objeto con exactamente las partes y una opcion de cada parte; texto cadena no vacia tras recortar de largo <= max + 50 (max 700 si falta), devuelta recortada; estimar y numero a_numero(respuesta, entero) y estimar ademas min <= x <= max; cualquier otra cosa es error de formato'
    violation: '{error: formato}, que reto.js convierte en 400 «Respuesta incompleta o con formato no válido.»'
    source: 'FR2.1, FR2.4, validar_respuesta() de servidor.py'
  - id: BR2.2
    statement: 'a_numero lee coma o punto como decimal y puntos de miles igual que hoy.'
    category: calculation
    applies_to: 'Calificacion: a_numero'
    trigger: respuestas de estimar y numero
    logic: 'si ya es numero se devuelve; se quitan los caracteres que no son digito ASCII, coma, punto o guion; sin digitos es error; IF entero y la forma es -?d{1,3}([.,]d{3})+ THEN se quitan los separadores; IF hay coma y punto THEN el punto es de miles y la coma decimal; IF hay mas de una coma o mas de un punto THEN todos son de miles; ELSE la coma es decimal'
    violation: 'error de formato'
    source: 'FR2.1, a_numero() de servidor.py (dígitos no ASCII: diferencia aceptada, ADR-W8)'
  - id: BR2.3
    statement: 'fraccion da el mismo credito parcial que hoy para los 10 tipos, en el mismo orden de operaciones.'
    category: calculation
    applies_to: 'Calificacion: fraccion'
    trigger: cada respuesta validada
    logic: 'sin puntos 0; compartir, recordatorio y texto 0; opcion 1 si coincide; multiple max(0, (|sel y cor| - |sel menos cor|) / |cor|); clasificar aciertos / total de la clave; ordenar pares bien ordenados / pares totales; construir partes acertadas / partes de la clave; estimar max(0, 1 - |r - ok| / tolerancia); numero 1 si |r - ok| <= tol + 1e-9, 0,5 si tol > 0 y |r - ok| <= 3 tol + 1e-9, si no 0; un tipo desconocido lanza RangeError'
    violation: 'RangeError (error interno 500): el banco validado nunca trae un tipo desconocido'
    source: 'FR2.1, NFR11, fraccion() de servidor.py, ADR-W8'
  - id: BR2.4
    statement: 'El bono y el cierre del intento siguen la formula de hoy, con todos los tiempos medidos desde inicio, que es el arranque del colegio.'
    category: calculation
    applies_to: 'Calificacion: bono y cerrar_intento'
    trigger: entregar, vencer y cerrar
    logic: 'bono = bono_max x (puntos / puntos_totales) x (1 - tiempo_respuestas / duracion); fin = min(ahora, inicio + duracion); tiempo_usado = max(0, fin - inicio); tiempo_respuestas = min(duracion, max(0, (ultima o fin) - inicio)); total = puntos + bono; inicio es el arranque del colegio del participante aunque haya pulsado «Comenzar» despues (BR4.6), asi un colegio que arranco tarde no pierde bono'
    violation: no aplica
    source: 'FR2.2, FR2.6, finalizar() de servidor.py'
  - id: BR2.5
    statement: 'Todo redondeo de las reglas da el mismo numero que round de Python, tambien en los empates exactos.'
    category: calculation
    applies_to: 'comun.js: redondear(x, d), usado por Clasificacion, por el resumen (U5) y por los CSV (U6)'
    trigger: cada redondeo
    logic: 'r = Number(x.toFixed(d)); IF x x 10^d es exactamente un entero mas 0,5 (comprobado con la mantisa y el exponente del doble en BigInt) THEN se elige el vecino cuyo ultimo digito es par; ELSE r; d entre 0 y 9; x no finito no se redondea (no ocurre con datos validos)'
    violation: no aplica
    source: 'NFR11, ADR-W8 (revisión 2026-10-25)'
  - id: BR3.1
    statement: 'ordenar da el orden total de todo el reto, entre todos los colegios, con los desempates de hoy medidos desde el arranque de cada colegio, y nunca dos puestos iguales.'
    category: calculation
    applies_to: 'Clasificacion: ordenar'
    trigger: 'ranking, podio, resumen, CSV y puesto del participante'
    logic: 'recibe solo participantes finalizados (ParticipanteParaOrden), de todos los colegios; clave de orden: -redondear(total, 9), -redondear(puntos, 9), tiempo_respuestas asc, tiempo_usado asc, id asc (FR2.3 con FR2.6: «hora de entrega» es tiempo_usado, relativo al arranque; «orden de inscripcion» es id, hora real); devuelve FilaClasificada con puesto 1..n y los redondeos de clasificacion() (puntos, bono y total a 4; nota a 2; tiempo_usado a 1; tiempo_respuestas a 3); el id es unico, asi que el orden es total; con todos los inicio iguales da el mismo orden que clasificacion() de servidor.py, que usa fin'
    violation: no aplica
    source: 'FR2.3, FR2.6, NFR11, FR11.2, FR11.7, clasificacion() de servidor.py, contrato C4'
  - id: BR3.2
    statement: 'La nota es 1 + 4 x puntos / 1.000, redondeada a 2 decimales, sobre los puntos y no sobre el total.'
    category: calculation
    applies_to: 'Clasificacion: nota'
    trigger: ranking, por grado y vista del participante
    logic: 'nota(puntos, puntos_totales) = redondear(1 + 4 x puntos / puntos_totales, 2), en ese orden de operaciones; va de 1,0 a 5,0'
    violation: no aplica
    source: 'FR2.5, clasificacion() y estado_participante() de servidor.py'
  - id: BR3.3
    statement: 'puesto_de devuelve el puesto general y el puesto en el grado de un participante, o null si no esta finalizado.'
    category: calculation
    applies_to: 'Clasificacion: puesto_de'
    trigger: vista del participante en resultados
    logic: 'busca el id en por_grado(ordenar(finalizados del reto)) y devuelve {puesto, puesto_grado, nota}'
    violation: no aplica
    source: 'FR2.5, puesto_de() de servidor.py, D2 del contrato'
  - id: BR3.4
    statement: 'por_grado da el orden de cada grado con el mismo criterio del orden general y le pone puesto_grado a cada fila.'
    category: calculation
    applies_to: 'Clasificacion: por_grado'
    trigger: tablero en resultados, resumen, CSV del paquete y vista del participante
    logic: 'recibe la salida de ordenar; para cada grado de 9, 10 y 11, en el orden general, puesto_grado = 1..n del grado; devuelve {lista: filas con puesto_grado, por_grado: {"9": [...], "10": [...], "11": [...]}}; un grado sin finalizados da lista vacia; no reordena: el orden dentro del grado es el general filtrado, asi el podio de un grado nunca contradice el general'
    violation: no aplica
    source: 'FR2.5, D4 del contrato (por_grado y puesto_grado)'
  - id: BR4.1
    statement: 'Solo se permiten las transiciones del reto que ofrece el panel; repetir el estado actual no es una transicion.'
    category: constraint
    applies_to: 'CicloDelReto: transicion_permitida'
    trigger: POST /api/admin/estado
    logic: 'permitidas: inscripcion a abierto, abierto a cerrado, cerrado a resultados (los tres botones de admin.js); todo lo demas es falso; pedir el estado actual lo atiende reto.js como «ok sin hacer nada» antes de llamar; reiniciar no pasa por aqui (U6)'
    violation: '400 «Ese cambio de estado no está permitido.» en reto.js'
    source: 'FR7.4, FR1.1, admin.js (botones Abrir, Cerrar, Publicar), contrato «Cambios de estado»'
  - id: BR4.2
    statement: 'La hora de entrega de un intento es la menor entre ahora, inicio + duracion y el cierre del reto, con su motivo; inicio es el arranque de su colegio.'
    category: calculation
    applies_to: 'CicloDelReto: hora_de_entrega'
    trigger: antes de toda operacion (vencer por colegio, ADR-004)
    logic: 'IF cierre no es null y cierre <= ahora y cierre < inicio + duracion THEN {cierre, motivo cierre}; IF ahora >= inicio + duracion THEN {inicio + duracion, motivo tiempo}; ELSE nada; cierre es cerrado_en del reto; como inicio es el arranque, cada colegio vence a su hora'
    violation: no aplica
    source: 'FR3.1, FR3.2, FR3.3, ADR-004, ADR-011'
  - id: BR4.3
    statement: 'Al cerrar el reto, quien nunca empezo pasa a no_inicio y quien esta en curso se entrega con motivo cierre, en todos los colegios.'
    category: calculation
    applies_to: 'CicloDelReto: estado_tras_cierre'
    trigger: transicion a cerrado
    logic: 'registrado a no_inicio; en_curso a finalizado con motivo cierre (cerrar_intento con ahora = hora del cierre); finalizado, descalificado y no_inicio quedan igual; da igual si el colegio arranco o vencio'
    violation: no aplica
    source: 'FR1.2, FR3.1 («Cerrar el reto» entrega lo pendiente de todos los colegios), cambiar_estado() de servidor.py'
  - id: BR4.4
    statement: 'El reto admite inscripciones solo en inscripcion y abierto.'
    category: constraint
    applies_to: 'CicloDelReto: admite_inscripciones'
    trigger: POST /api/registro
    logic: 'true si estado es inscripcion o abierto'
    violation: '400 «Las inscripciones están cerradas.» en reto.js'
    source: 'FR1.3, registrar() de servidor.py'
  - id: BR4.5
    statement: 'Un colegio se arranca solo con el reto abierto y una sola vez.'
    category: constraint
    applies_to: 'CicloDelReto: puede_arrancar_colegio'
    trigger: 'POST /api/admin/colegios con accion arrancar'
    logic: 'IF estado_reto no es abierto THEN {ok: false, mensaje: «Abre el reto antes de arrancar un colegio.»}; IF arranque no es null THEN {ok: false, mensaje: «Ese colegio ya arrancó.»}; ELSE {ok: true}; no hay regla para deshacer un arranque'
    violation: '400 con el mensaje, en reto.js'
    source: 'FR3.1, FR11.5, ADR-011'
  - id: BR4.6
    statement: 'Un equipo comienza solo con el reto abierto, su colegio arrancado y el reloj de su colegio sin vencer; su inicio es el arranque del colegio.'
    category: constraint
    applies_to: 'CicloDelReto: puede_comenzar'
    trigger: POST /api/comenzar
    logic: 'en este orden: IF estado_participante no es registrado THEN {resultado: sin_cambio} (como hoy, responde ok sin hacer nada); IF estado_reto no es abierto THEN {rechazo, «El reto todavía no ha empezado. Espera la señal del docente.»}; IF arranque es null THEN {rechazo, «Tu colegio todavía no ha empezado. Espera la señal del docente.»}; IF ahora >= arranque + duracion THEN {rechazo, «El tiempo del reto ya terminó.»}; ELSE {resultado: comenzar, inicio: arranque}'
    violation: '400 con el mensaje, en reto.js'
    source: 'FR3.1, FR11.3, comenzar() de servidor.py (reloj global), contrato (/api/comenzar)'
  - id: BR4.7
    statement: 'El estado del reloj de un colegio sale solo de su arranque, la duracion y la hora.'
    category: calculation
    applies_to: 'CicloDelReto: estado_reloj'
    trigger: 'GET /api/admin/colegios, resumen, /api/publico (colegios[]) y /api/estado (colegio_restante_seg)'
    logic: 'IF arranque es null THEN {sin_arrancar, restante_seg: null}; IF ahora >= arranque + duracion THEN {vencido, restante_seg: 0}; ELSE {corriendo, restante_seg: arranque + duracion - ahora}; el estado del reto no cambia el reloj: tras cerrar, un colegio corriendo se sigue mostrando con su resta (el panel ya no lo usa para nada)'
    violation: no aplica
    source: 'FR11.5, ADR-011, contrato «Lista de colegios y relojes»'
  - id: BR4.8
    statement: 'Al abrir el reto se arrancan a la vez todos los colegios que ya tienen al menos un equipo inscrito; los demas quedan sin arrancar.'
    category: calculation
    applies_to: 'CicloDelReto: colegios_al_abrir'
    trigger: transicion de inscripcion a abierto
    logic: 'recibe [{id_colegio, arranque, equipos}] y ahora; devuelve los id_colegio con equipos >= 1 y arranque null, en orden de id_colegio; equipos cuenta participantes no descalificados; con un solo colegio con equipos, todos comparten la hora de inicio, como el reloj global de hoy (FR11.7)'
    violation: no aplica
    source: 'FR3.1, FR11.7, ADR-011, contrato «Cambios de estado»'
  - id: BR5.1
    statement: 'normalizar_texto aplica los cuatro pasos de FR10.2 y no cambia mayusculas ni tildes.'
    category: validation
    applies_to: 'LimpiezaEntrada: normalizar_texto'
    trigger: cada texto que llega del navegador
    logic: 'forma NFC; caracteres de control pasan a espacio; caracteres de formato (ancho cero) se quitan; espacios repetidos se juntan; se recorta al largo en caracteres (60 nombre, 200 integrantes, 80 colegio y evento); es la funcion limpiar de U1 con ese nombre de C4'
    violation: no aplica
    source: 'FR10.2 (referencia del generador, ADR-W7)'
  - id: BR5.2
    statement: 'normalizar_integrantes separa por comas, limpia cada nombre, quita vacios y los une con coma y espacio; n_integrantes los cuenta.'
    category: validation
    applies_to: 'LimpiezaEntrada: normalizar_integrantes'
    trigger: POST /api/registro
    logic: 'partes = texto.split(coma) con normalizar_texto(parte, 200) cada una; se descartan las vacias; resultado = partes unidas con «, » recortado a 200; n_integrantes = numero de partes; vacio da «» y 0'
    violation: no aplica
    source: 'FR10.4'
  - id: BR5.3
    statement: 'validar_inscripcion aplica en el servidor todas las reglas de los campos, con los mensajes de hoy.'
    category: validation
    applies_to: 'LimpiezaEntrada: validar_inscripcion'
    trigger: POST /api/registro
    logic: 'en este orden, sobre los campos ya normalizados: nombre con menos de 3 caracteres «Escribe tu nombre (o el del equipo).»; grado fuera de 9, 10, 11 «Elige el grado: 9, 10 u 11.»; colegio vacio o que no es un id_colegio de la lista del docente (ids_colegios) «Elige tu colegio de la lista.»; devuelve la lista de errores (vacia si todo esta bien); la regla de repetido no va aqui porque necesita la base (U5)'
    violation: 'el primer mensaje de la lista, con 400, en reto.js'
    source: 'FR10.1, FR10.3, registrar() de servidor.py, ADR-009'
  - id: BR5.4
    statement: 'normalizar_nombre_colegio da el nombre comparable de un colegio: limpio, sin tildes y en minusculas.'
    category: validation
    applies_to: 'LimpiezaEntrada: normalizar_nombre_colegio (alias normalizar_nombre de U1)'
    trigger: al agregar colegios a la lista del docente
    logic: 'normalizar_texto(texto, 80), forma NFD, sin marcas diacriticas, en minusculas; «IE San José» y «ie san jose» dan lo mismo'
    violation: no aplica
    source: 'FR10.3, ADR-009 (rechaza nombres normalizados repetidos)'
  - id: BR5.5
    statement: 'preparar_colegios convierte lo que pega el docente en la lista de nombres que se agregan, o en el error del primero que no sirve.'
    category: validation
    applies_to: 'LimpiezaEntrada: preparar_colegios'
    trigger: 'POST /api/admin/colegios con accion agregar'
    logic: 'entrada {nombres o nombre, existentes: [{id_colegio, nombre, nombre_normalizado}]}; se parte nombres por saltos de linea (nombre es una sola linea); cada linea pasa por normalizar_texto(linea, 80); las vacias se omiten; IF una linea tiene menos de 3 letras (caracteres de la categoria Unicode L) THEN error «Escribe el nombre del colegio (al menos 3 letras).»; IF no queda ninguna linea THEN el mismo error; IF el nombre normalizado de una linea esta en existentes THEN error «Ese colegio ya existe.» con existente {id_colegio, nombre}; dos lineas iguales tras normalizar dentro del mismo texto cuentan una vez, con la primera forma escrita (decision del asistente: el docente quiso un solo colegio); si hay error no se agrega ninguno (todo o nada, D3)'
    violation: '400 con el mensaje (y existente cuando aplica) en reto.js'
    source: 'ADR-009, FR10.1, FR10.3, D3 del contrato'
  - id: BR6.1
    statement: 'calcular reproduce experimento() de hoy sobre las respuestas de todo el reto, sin descalificados.'
    category: calculation
    applies_to: 'Experimento: calcular'
    trigger: resumen del panel y tablero
    logic: 'recibe banco y filas {participante_id, grupo, estado, pregunta_id, respuesta} de todos los colegios; descarta estado descalificado; completos = quienes respondieron m1_compartir y m1_veracidad; IF n < 2 THEN {n, listo: false}; tasas por grupo A/B y clase en porcentaje (100 x aciertos / casos), null si no hay casos; multitud con veredicto V si pct_v >= 50; por_publicacion con id, verdad, pct_cree_verdadera, pct_compartiria, multitud_acierta y texto de la publicacion; mismo orden de operaciones que servidor.py; el reparto A/B es de toda la sala (FR11.2)'
    violation: no aplica
    source: 'FR11.2, experimento() de servidor.py, ADR-W8'
  - id: BR6.2
    statement: 'La version publica del experimento es nada en inscripcion y abierto, {n, listo} en cerrado y el objeto completo en resultados.'
    category: policy
    applies_to: 'Experimento: experimento_publico'
    trigger: GET /api/publico
    logic: 'IF estado es resultados THEN el objeto completo; IF estado es cerrado THEN {n, listo}; ELSE null (reto.js no envia la clave experimento, como hoy)'
    violation: 'la comprobacion de fugas de la prueba comun (FR6.3) falla'
    source: 'FR6.1, ADR-W9, D5 del contrato, publico() de servidor.py'
  - id: BR7.1
    statement: 'Cada funcion de C4 pasa todos los casos de la tabla compartida, y la copia de la tabla no puede estar vieja.'
    category: validation
    applies_to: 'pruebas/casos_reglas.test.js y herramientas/verificar.sh'
    trigger: cada corrida de pruebas
    logic: 'el test lee pruebas/casos_reglas.json, agrupa por regla y funcion y compara salida con salida_esperada (igualdad estricta, o |a - b| <= tolerancia cuando el caso la trae); verificar.sh compara sha256 de la copia con despliegues/prueba_comun/casos_reglas.json y se detiene si difieren'
    violation: 'node --test falla; verificar.sh se detiene con «la copia de casos_reglas.json está vieja: corre copiar.sh»'
    source: 'FR7.1, FR10.5, NFR12, C4, ADR-W7'
  - id: BR7.2
    statement: 'Las reglas se prueban sin servidor ni base, con un caso valido y al menos dos invalidos por regla de validacion.'
    category: validation
    applies_to: 'pruebas/*.test.js'
    trigger: cada corrida de pruebas
    logic: 'validar_respuesta: por tipo, uno valido y dos invalidos; a_numero: coma, punto, miles, entero, sin digitos; normalizar_texto: NFC, ancho cero, control, espacios; validar_inscripcion: nombre corto, grado, colegio fuera de la lista; preparar_colegios: lista valida, nombre corto, repetido con la lista, repetido dentro del texto; transicion_permitida: las 3 permitidas y 4 prohibidas; puede_comenzar y puede_arrancar_colegio: cada motivo; redondear: un empate exacto por cada numero de decimales usado; el banco real solo se usa para estructura y para comprobar que no sale ninguna clave secreta'
    violation: 'cobertura de lineas menor que 80 % en src/reglas/'
    source: 'FR10.5, NFR12, phases/construction.md («Testing Standards»)'
  - id: BR7.3
    statement: 'La tabla trae el caso obligatorio de dos colegios: con arranques distintos el orden usa los tiempos relativos, y con los mismos arranques coincide con la version local.'
    category: validation
    applies_to: 'casos de Clasificacion.ordenar y Calificacion.cerrar_intento'
    trigger: al generar la tabla (ADR-W7)
    logic: 'caso A: colegio 1 arranca en t0 y colegio 2 en t0 + 600 s; dos equipos, uno por colegio, con los mismos puntos y la ultima respuesta a los mismos minutos de su arranque: mismo bono y el desempate lo decide tiempo_usado y despues id, nunca la hora de pared; caso B: los mismos equipos con los dos arranques en t0: la salida es igual a la de clasificacion() de servidor.py; el generador se detiene si B no coincide'
    violation: 'generar_casos.py se detiene; node --test falla'
    source: 'FR2.6, FR11.7, contrato C4 (caso_obligatorio)'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.3 | Banco: traducción opaca por tipo, revisión y examen público completo |
| BR2 | BR2.1–BR2.5 | Calificacion: validación, `a_numero`, fracción de los 10 tipos, bono y cierre desde el arranque, redondeo como Python |
| BR3 | BR3.1–BR3.4 | Clasificacion: orden total del reto, nota, puesto y puesto por grado |
| BR4 | BR4.1–BR4.8 | CicloDelReto: transiciones, entrega por colegio, cierre, inscripciones, arrancar, comenzar, estado del reloj y colegios al abrir |
| BR5 | BR5.1–BR5.5 | LimpiezaEntrada: texto, integrantes, inscripción, nombre comparable y lista de colegios |
| BR6 | BR6.1–BR6.2 | Experimento: cálculo de todo el reto y versión pública |
| BR7 | BR7.1–BR7.3 | Pruebas con la tabla compartida, sin servidor, y el caso de dos colegios |

Lo que necesita base o reloj (nombre repetido, grupo A/B, códigos únicos, guardar un arranque, escribir la
entrega) no es regla: lo hacen U5 y U6 en `reto.js`, llamando a estas funciones.
