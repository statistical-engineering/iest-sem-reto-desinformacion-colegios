# Reglas — U4 `u4-cloudflare-reglas`

Las reglas puras de la opción Cloudflare Workers: las seis «calculadoras» de ADR-001 con la forma del
contrato C4 (`contract-summary.md`, «C4. Forma de las reglas»). Salen de `requirements.md` (FR2, FR3.2,
FR6, FR7.1, FR7.4, FR10), de `components.md` (capa Reglas) y de `servidor.py`, que define la conducta que
no cambia. Las decisiones propias de la unidad están en `../decisions.md` (ADR-W6 a ADR-W9). Ninguna regla
lee la base ni el reloj: la hora llega como argumento, y ninguna escribe en el registro.

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
    trigger: 'U6 la llama solo con sala en resultados y participante finalizado'
    logic: 'revision_publica(banco, semilla, grupo) devuelve, por cada pregunta visible para el grupo, {respuesta: respuesta_opaca(...), explicacion}; la regla no decide cuando se llama: es pura, y la condicion la aplica Resultados (U6)'
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
    statement: 'El bono y el cierre del intento siguen la formula de hoy.'
    category: calculation
    applies_to: 'Calificacion: bono y cerrar_intento'
    trigger: entregar, vencer y cerrar
    logic: 'como en U1 (BR4.3): bono = bono_max x (puntos / puntos_totales) x (1 - tiempo_respuestas / duracion); fin = min(ahora, inicio + duracion); tiempo_respuestas = min(duracion, max(0, (ultima o fin) - inicio))'
    violation: no aplica
    source: 'FR2.2, finalizar() de servidor.py'
  - id: BR3.1
    statement: 'ordenar da el orden total de una sala con los desempates de hoy y nunca dos puestos iguales.'
    category: calculation
    applies_to: 'Clasificacion: ordenar'
    trigger: 'ranking, resumen, CSV y puesto del participante'
    logic: 'recibe solo participantes finalizados de una sala; clave de orden: -redondear9(total), -redondear9(puntos), tiempo_respuestas asc, fin asc, id asc; devuelve FilaClasificada con puesto 1..n y los redondeos de clasificacion() (puntos, bono y total a 4; nota a 2; tiempo_usado a 1; tiempo_respuestas a 3); el id es unico, asi que el orden es total'
    violation: no aplica
    source: 'FR2.3, NFR11, FR11.2, clasificacion() de servidor.py'
  - id: BR3.2
    statement: 'La nota es 1 + 4 x puntos / 1.000, redondeada a 2 decimales, sobre los puntos y no sobre el total.'
    category: calculation
    applies_to: 'Clasificacion: nota'
    trigger: ranking y vista del participante
    logic: 'nota(puntos, puntos_totales) = redondear2(1 + 4 x puntos / puntos_totales)'
    violation: no aplica
    source: 'clasificacion() y estado_participante() de servidor.py'
  - id: BR3.3
    statement: 'puesto_de devuelve el puesto de un participante en el orden de su sala o null si no esta finalizado.'
    category: calculation
    applies_to: 'Clasificacion: puesto_de'
    trigger: vista del participante en resultados
    logic: 'busca el id en ordenar(finalizados de la sala)'
    violation: no aplica
    source: 'puesto_de() de servidor.py'
  - id: BR4.1
    statement: 'Solo se permiten las transiciones de sala que ofrece el panel; repetir el estado actual no es una transicion.'
    category: constraint
    applies_to: 'CicloDeSala: transicion_permitida'
    trigger: POST /api/admin/estado
    logic: 'permitidas: inscripcion a abierto, abierto a cerrado, cerrado a resultados (los tres botones de admin.js); todo lo demas es falso; reiniciar no pasa por aqui (U6); U1 solo tenia la primera'
    violation: '400 en reto.js (U5 fija el mensaje)'
    source: 'FR7.4, FR1.1, admin.js (botones Abrir, Cerrar, Publicar)'
  - id: BR4.2
    statement: 'La hora de entrega es la menor entre ahora, inicio + duracion y el cierre de la sala, con su motivo.'
    category: calculation
    applies_to: 'CicloDeSala: hora_de_entrega'
    trigger: antes de toda operacion sobre una sala
    logic: 'como en U1 (BR4.2) y ADR-004, ahora con cierre no nulo: IF cierre <= ahora y cierre < inicio + duracion THEN {cierre, motivo cierre}; IF ahora >= inicio + duracion THEN {inicio + duracion, motivo tiempo}; ELSE nada; un intento iniciado despues del cierre no existe (comenzar exige sala abierta)'
    violation: no aplica
    source: 'FR3.2, FR3.3, ADR-004'
  - id: BR4.3
    statement: 'Al cerrar la sala, quien nunca empezo pasa a no_inicio y quien esta en curso se entrega con motivo cierre.'
    category: calculation
    applies_to: 'CicloDeSala: estado_tras_cierre'
    trigger: transicion a cerrado
    logic: 'registrado a no_inicio; en_curso a finalizado con motivo cierre (via hora_de_entrega); finalizado, descalificado y no_inicio quedan igual'
    violation: no aplica
    source: 'FR1.2, cambiar_estado() de servidor.py'
  - id: BR4.4
    statement: 'La sala admite inscripciones solo en inscripcion y abierto.'
    category: constraint
    applies_to: 'CicloDeSala: admite_inscripciones'
    trigger: POST /api/registro
    logic: 'true si estado es inscripcion o abierto'
    violation: '400 «Las inscripciones están cerradas.» en reto.js'
    source: 'FR1.3, registrar() de servidor.py'
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
    logic: 'en este orden, sobre los campos ya normalizados: nombre con menos de 3 caracteres «Escribe tu nombre (o el del equipo).»; grado fuera de 9, 10, 11 «Elige el grado: 9, 10 u 11.»; colegio vacio o que no es un id de la lista de la sala «Elige tu colegio de la lista.»; devuelve la lista de errores (vacia si todo esta bien); la regla de repetido no va aqui porque necesita la base (U5)'
    violation: 'el primer mensaje de la lista, con 400, en reto.js'
    source: 'FR10.1, FR10.3, registrar() de servidor.py'
  - id: BR5.4
    statement: 'normalizar_nombre da el nombre comparable de un colegio: limpio, sin tildes y en minusculas.'
    category: validation
    applies_to: 'LimpiezaEntrada: normalizar_nombre'
    trigger: catalogo y colegios provisionales
    logic: 'normalizar_texto(texto, 80), forma NFD, sin marcas diacriticas, en minusculas; como en U1'
    violation: no aplica
    source: 'FR10.3, ADR-002'
  - id: BR6.1
    statement: 'calcular reproduce experimento() de hoy sobre las respuestas de una sola sala, sin descalificados.'
    category: calculation
    applies_to: 'Experimento: calcular'
    trigger: resumen del panel y tablero
    logic: 'recibe banco y filas {participante_id, grupo, estado, pregunta_id, respuesta} de la sala; descarta estado descalificado; completos = quienes respondieron m1_compartir y m1_veracidad; IF n < 2 THEN {n, listo: false}; tasas por grupo A/B y clase en porcentaje (100 x aciertos / casos), null si no hay casos; multitud con veredicto V si pct_v >= 50; por_publicacion con id, verdad, pct_cree_verdadera, pct_compartiria, multitud_acierta y texto de la publicacion; mismo orden de operaciones que servidor.py'
    violation: no aplica
    source: 'FR11.2, experimento() de servidor.py, ADR-W8'
  - id: BR6.2
    statement: 'Antes de resultados, la version publica del experimento es solo {n, listo}.'
    category: policy
    applies_to: 'Experimento: experimento_publico'
    trigger: GET /api/publico
    logic: 'IF estado es resultados THEN el objeto completo; ELSE {n, listo}'
    violation: 'la comprobacion de fugas de la prueba comun (FR6.3) falla'
    source: 'FR6.1, ADR-W9'
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
    logic: 'validar_respuesta: por tipo, uno valido y dos invalidos; a_numero: coma, punto, miles, entero, sin digitos; normalizar_texto: NFC, ancho cero, control, espacios; validar_inscripcion: nombre corto, grado, colegio; transicion_permitida: las 3 permitidas y 4 prohibidas; el banco real solo se usa para estructura y para comprobar que no sale ninguna clave secreta'
    violation: 'cobertura de lineas menor que 80 % en src/reglas/'
    source: 'FR10.5, NFR12, phases/construction.md («Testing Standards»)'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.3 | Banco: traducción opaca por tipo, revisión y examen público completo |
| BR2 | BR2.1–BR2.4 | Calificacion: validación, `a_numero`, fracción de los 10 tipos, bono y cierre |
| BR3 | BR3.1–BR3.3 | Clasificacion: orden total, nota y puesto |
| BR4 | BR4.1–BR4.4 | CicloDeSala: transiciones del panel, hora de entrega con cierre, estados al cerrar, inscripciones |
| BR5 | BR5.1–BR5.4 | LimpiezaEntrada: texto, integrantes, validación de la inscripción, nombre comparable |
| BR6 | BR6.1–BR6.2 | Experimento: cálculo por sala y versión pública |
| BR7 | BR7.1–BR7.2 | Pruebas con la tabla compartida y sin servidor |

Lo que necesita base o reloj (nombre repetido, grupo A/B, códigos únicos, escribir la entrega) no es
regla: lo hacen U5 y U6 en `reto.js`, llamando a estas funciones.
