# Reglas — U2 `u2-prueba-comun`

Las reglas de la prueba común completa. Salen de `requirements.md` (FR12.3, FR12.5, FR6.3, FR11.7, NFR1 a
NFR12), de `unit-of-work.md` (U2), del contrato (`contract-summary.md`, C2 y C3), de `bolt-plan.md` (B2:
hallazgos C-09, C-14 y C-15) y de las 29 comprobaciones de `2_Aplicacion_Reto/pruebas/simulacro.py`, que se
replican contra una URL sin debilitar ninguna. Decisiones tomadas por el asistente con la potestad que
dio el humano («potestad absoluta para decidir», 2026-10-25).

```yaml
rules:
  - id: BR1.1
    statement: 'La prueba recibe la URL, la clave y la opción por argumentos o variables de entorno, y nunca escribe la clave en la URL, en la salida ni en el JSON.'
    category: policy
    applies_to: 'arranque de la prueba'
    trigger: cada corrida
    logic: '--url o PRUEBA_URL, --clave o PRUEBA_CLAVE, --modo nube|local, --opcion local|cloudflare|apps_script|github_pages; sin URL, clave u opción termina con código 2; las claves van solo en X-Clave-Admin; ?clave= solo se usa para comprobar que da 403'
    violation: 'código 2 con el mensaje de qué falta'
    source: 'FR12.3, NFR9, C3 («nunca lleva la URL con clave»)'
  - id: BR1.2
    statement: 'Termina en «TODO BIEN» (código 0) o con la lista de comprobaciones que fallaron (código 1), y siempre escribe el JSON de mediciones.'
    category: policy
    applies_to: 'fin de la corrida'
    trigger: cada corrida
    logic: 'IF no hay fallas THEN imprime «TODO BIEN: la opción cumple la prueba común.» y código 0; ELSE imprime «N fallas:» y cada mensaje, código 1; en los dos casos escribe el JSON (BR8.1); IF no hay conexión THEN código 2 y no escribe el JSON'
    violation: no aplica
    source: 'unit-of-work.md (U2, «salida»)'
  - id: BR1.3
    statement: 'Una comprobación esencial que falla detiene la corrida; una no esencial solo se anota.'
    category: policy
    applies_to: 'todas las comprobaciones'
    trigger: cada comprobación
    logic: 'IF esencial y no pasa THEN se agrega «la prueba se detuvo en <paso>» y se salta al cierre (BR8.1); son esenciales las que crean la sala, inscriben, comienzan y arman la clave por texto'
    violation: no aplica
    source: 'prueba.py de U1 (correr)'
  - id: BR1.4
    statement: 'Cualquier respuesta 5xx sin JSON se trata como {"error": "la respuesta no es JSON"} y cuenta como falla de la comprobación en curso, nunca como excepción.'
    category: validation
    applies_to: 'toda petición'
    trigger: cada respuesta
    logic: 'el cuerpo se intenta leer como JSON; IF falla THEN {"error": ...}; un 503 de la plataforma se anota en el detalle de la comprobación; la prueba no reintenta un POST (contrato C1)'
    violation: no aplica
    source: 'C-15, contrato C1'
  - id: BR2.1
    statement: 'La prueba no conoce el banco: toda respuesta correcta sale de revision después de publicar resultados en una sala de calibración.'
    category: policy
    applies_to: 'calibración (paso 3)'
    trigger: antes de las salas del reto
    logic: 'IF modo nube THEN crea la sala «calibración» con su colegio provisional; IF modo local THEN usa la única sala; la clave queda en memoria y nunca se escribe ni se imprime; no se lee banco_preguntas.json ni ningún otro archivo del repositorio'
    violation: no aplica
    source: 'NFR8, project.md («Forbidden»: respuestas fuera de material y artefactos), brief de U2'
  - id: BR2.2
    statement: 'La variante de cada pregunta se reconoce por su huella: sha256 de los textos visibles sin ids ni orden.'
    category: calculation
    applies_to: 'calibración y guion'
    trigger: cada /api/estado con misiones
    logic: 'huella = sha256(JSON ordenado de {enunciado, textos de opciones, ítems, publicaciones y categorías ordenados alfabéticamente, etiquetas de partes con los textos de sus opciones, min, max}); la misma pregunta con dos huellas distintas son dos variantes'
    violation: no aplica
    source: 'banco_preguntas.json (m2_trampas tiene 4 variantes que cambian solo los ítems), ADR-006'
  - id: BR2.3
    statement: 'Se inscriben 40 calibradores, se eligen representantes que cubran cada (pregunta, huella) y solo ellos responden todo; la clave por texto sale de su revision.'
    category: calculation
    applies_to: 'calibración (paso 3)'
    trigger: sala de calibración abierta
    logic: 'cada calibrador comienza y pide /api/estado; se eligen representantes de forma voraz hasta cubrir todas las (pregunta, huella) vistas; los representantes responden cada pregunta con una respuesta válida cualquiera (primera opción, categoría igual para todos, orden recibido, mitad del rango) y entregan; la sala pasa a cerrado y a resultados; de revision de cada representante se arma ClavePorTexto traduciendo ids opacos a textos con sus propias misiones; la probabilidad de no ver una de 4 variantes con 40 calibradores es 4 × (3/4)^40 ≈ 0,00004'
    violation: 'esencial: «no se pudo armar la clave por texto» detiene la corrida'
    source: 'ADR-006 (la clave solo con la sala en resultados), FR6.3'
  - id: BR2.4
    statement: 'Un participante del reto cuya huella no esté en la clave por texto es una falla, nunca una adivinanza.'
    category: validation
    applies_to: 'guion (paso 5)'
    trigger: al armar las respuestas de un participante
    logic: 'IF (pregunta, huella) no está en ClavePorTexto THEN falla «clave_por_texto_completa» con el id de la pregunta y el participante responde esa pregunta como «fallo»; puntos_esperados no la cuenta'
    violation: 'falla no esencial con el id de la pregunta'
    source: BR2.3
  - id: BR3.1
    statement: 'El guion es determinista: la semilla 7 y el índice k fijan el papel, el grado y qué preguntas acierta cada participante.'
    category: calculation
    applies_to: 'guion'
    trigger: antes de inscribir
    logic: 'random.Random(semilla_guion) como random.seed(7) de simulacro.py; papel por k: 0 perfecto, 1 cero, 2 parcial, 3 vencido_sin_respuestas, 4 y 5 vencido_al_final, 6 llega_tarde, los demás normal con acierto si azar < 0,25 + 0,7 × nivel; los papeles 0 a 6 van en la sala más grande'
    violation: no aplica
    source: 'simulacro.py (main, «2) Respuestas»), NFR11'
  - id: BR3.2
    statement: 'Cada respuesta se arma con la clave por texto y los ids que ese participante recibió: acertar, fallar o a medias.'
    category: calculation
    applies_to: 'guion'
    trigger: cada pregunta de cada participante
    logic: 'acertar: la respuesta correcta traducida a los ids del participante; fallar: opcion otra opción, multiple una opción fuera de la clave, clasificar cada ítem en otra categoría, ordenar al revés, construir otra opción en cada parte, numero clave + 1000, estimar el extremo del rango más lejano, texto una conclusión fija, compartir y recordatorio una categoría cualquiera (sin puntos); a medias: clasificar y construir aciertan la primera mitad redondeada hacia arriba por orden alfabético del texto y fallan el resto, multiple la clave más una opción de sobra, ordenar la clave con los dos primeros intercambiados, los demás tipos como acertar'
    violation: no aplica
    source: 'simulacro.py (respuesta_para), api-documentation.md (forma de cada tipo), FR2.1'
  - id: BR3.3
    statement: 'Los puntos esperados de un participante son la suma de los puntos de las preguntas que el guion decidió acertar; a medias no suma a lo esperado.'
    category: calculation
    applies_to: 'guion y calificación (paso 8)'
    trigger: al armar el guion
    logic: 'puntos_esperados = Σ puntos públicos de las preguntas con decisión acertar; las preguntas sin clave (hipótesis, informe, compartir, recordatorio) valen 0; para el papel parcial solo se registran las fracciones y se exige 0 < fracción < 1 en clasificar, multiple, ordenar y construir'
    violation: no aplica
    source: 'FR2.1, NFR11'
  - id: BR4.1
    statement: 'La parte base repite las 29 comprobaciones de simulacro.py por HTTP, con la misma condición o una equivalente que no abra la base ni mueva el reloj.'
    category: policy
    applies_to: 'parte base'
    trigger: cada corrida
    logic: 'la tabla «Parte base» de functional-spec.md da la equivalencia de cada una; una comprobación solo se reemplaza por otra que verifique la misma propiedad por la API'
    violation: no aplica
    source: 'FR12.3, FR6.3, unit-of-work.md (U2, «sin debilitar ninguna»)'
  - id: BR4.2
    statement: 'El vencimiento se prueba con duracion_min = 10 y espera real; la exactitud se verifica con tiempo_usado igual a la duración.'
    category: calculation
    applies_to: 'paso 7'
    trigger: salas abiertas con reloj global
    logic: 'cada sala del reto se configura con duracion_min = --duracion-min (mínimo 10) antes de abrirla; la prueba espera hasta abierto_en + duración + 2 s; después, el vencido_sin_respuestas aparece finalizado con tiempo_usado_min × 60 == duración (± 0,001 s) y motivo tiempo; responder da 400; comenzar del que llega tarde da 400 «ya terminó»'
    violation: no aplica
    source: 'C-09, FR3.2, FR3.3, OQ3'
  - id: BR4.3
    statement: 'El bono al final del tiempo se verifica sin mover el reloj: 0 para quien no respondió y acotado por la fórmula para quien respondió en los últimos 15 s.'
    category: calculation
    applies_to: 'paso 8'
    trigger: después del vencimiento
    logic: 'vencido_sin_respuestas: bono == 0 y puntos == 0; vencido_al_final: su última pregunta se envía en abierto_en + duración − 15 s, y se exige bono ≤ 20 × (puntos / 1.000) × (15 / duración) + 0,001 y tiempo_usado igual a la duración; es la misma propiedad de simulacro.py («quien responde su última pregunta al final del tiempo no recibe bono») con el tiempo real en vez de inicio − 6.000'
    violation: no aplica
    source: 'simulacro.py («4) Calificación»), FR2.2'
  - id: BR4.4
    statement: 'El reloj global se verifica con lo que devuelve la API: el inicio de cada participante coincide con abierto_en.'
    category: calculation
    applies_to: 'paso 5'
    trigger: participantes en curso
    logic: 'inicio_k = servidor_ahora + restante_seg − duración, con los tres valores de un mismo /api/estado; se exige |inicio_k − abierto_en| < 0,01 s para todos los participantes en curso de la sala; abierto_en sale de /api/publico?sala='
    violation: no aplica
    source: 'simulacro.py («2b) Reloj global»), FR3.1'
  - id: BR4.5
    statement: 'Los datos que simulacro.py lee de la base salen de /api/admin/resumen: grupo, id, puntos, bono, tiempo_usado, tiempo_respuestas y puesto.'
    category: policy
    applies_to: 'parte base'
    trigger: cada comprobación que hoy lee SQLite
    logic: 'el grupo A/B para el recordatorio, el id para eliminar al que llega tarde y las cifras de calificación se leen del resumen con la clave de la sala; la clasificación se recalcula con los campos del resumen (total y puntos redondeados a 9 decimales desc, tiempo_respuestas asc, tiempo_usado asc, orden de la lista asc) y debe coincidir con puesto'
    violation: no aplica
    source: 'FR2.3, NFR11, api-documentation.md (resumen)'
  - id: BR4.6
    statement: 'La copia de «Reiniciar» se verifica por la API: en la nube aparece en /api/admin/copias; en local se exige que la respuesta la nombre.'
    category: policy
    applies_to: 'paso 10'
    trigger: después de reiniciar
    logic: 'IF nube THEN GET /api/admin/copias?sala= contiene el id_copia devuelto (ruta de U6; mientras no exista, la comprobación falla y lo dice); IF local THEN copia es un nombre no vacío que termina en .db, y el archivo lo sigue comprobando simulacro.py; en los dos casos conteo.inscritos == 0'
    violation: no aplica
    source: 'simulacro.py («7) Reinicio»), contrato C1 (/api/admin/copias)'
  - id: BR5.1
    statement: 'Ninguna clave secreta llega sin clave docente antes de resultados: ni en /api/estado, ni en /api/publico, ni en /api/colegios.'
    category: policy
    applies_to: 'parte fugas'
    trigger: cada /api/estado y /api/publico que la prueba pide antes de resultados
    logic: 'claves secretas = {respuesta dentro de misiones, explicacion, tolerancia, verdad, multitud_acierta, veredicto} y la clave revision; se recorren todas las respuestas a cualquier profundidad; la lista se amplía con cada clave nueva del contrato que llegue sin clave docente (C-14)'
    violation: 'falla fuga_<ruta>_<estado>'
    source: 'FR6.3, NFR8, C-14'
  - id: BR5.2
    statement: 'En cerrado, con respuestas del Exp. 01, /api/publico no trae verdad ni multitud_acierta; en resultados sí.'
    category: policy
    applies_to: 'parte fugas (paso 3 y paso 9)'
    trigger: sala en cerrado y luego en resultados
    logic: 'fuga_verdad_cerrado: claves_de(publico.experimento) no contiene verdad ni multitud_acierta; experimento_completo_resultados: en resultados por_publicacion[] trae verdad y multitud_acierta; falla con la versión local de hoy y pasa después de U3'
    violation: 'falla fuga_verdad_cerrado'
    source: FR6.1
  - id: BR5.3
    statement: 'Todos los ids de opciones, ítems, publicaciones y partes que ve el navegador son opacos, y el orden de las opciones no es el mismo para todos.'
    category: policy
    applies_to: 'parte fugas (paso 5)'
    trigger: el primer /api/estado de cada participante del reto
    logic: 'fuga_ids_opacos: cada id cumple ^o[a-z2-7]{11}([a-z2-7]{5})?$; fuga_orden_banco: para cada pregunta con 3 o más opciones o ítems, entre los participantes del reto hay al menos dos órdenes distintos de textos (con 40 inscripciones, un mismo orden para todos delata el orden del banco); con 20 o menos participantes la comprobación se anota como no aplicable'
    violation: 'falla fuga_ids_opacos o fuga_orden_banco'
    source: 'FR6.2, FR6.3 (criterio «al menos una de 20 inscripciones»)'
  - id: BR5.4
    statement: 'respuestas.csv guarda ids del banco, nunca opacos.'
    category: validation
    applies_to: 'parte fugas (paso 9)'
    trigger: descarga de /api/admin/respuestas.csv
    logic: 'ningún valor de la columna respuesta contiene un texto con la forma opaca; la respuesta de la pregunta «opcion» del perfecto aparece con un id distinto del opaco que envió'
    violation: 'falla csv_ids_del_banco'
    source: 'FR6.2, FR9.2'
  - id: BR6.1
    statement: 'En la nube hay 10 salas de tamaños desiguales que suman 40 y abren a la vez; en local hay una sala de 40.'
    category: policy
    applies_to: 'paso 4'
    trigger: modo nube
    logic: 'tamaños 10, 7, 6, 5, 4, 3, 2, 1, 1, 1 (de 1 a 10, suman 40); con --participantes distinto de 40 se reparten proporcionalmente conservando una sala de 1; cada sala tiene su colegio provisional con nombre único por corrida; en local --salas se ignora'
    violation: no aplica
    source: 'NFR1, FR12.5'
  - id: BR6.2
    statement: 'Las salas no se mezclan: conteos, ranking, resumen y CSV de una sala solo traen a sus participantes, y su reloj es propio.'
    category: validation
    applies_to: 'parte salas (pasos 5 y 9)'
    trigger: modo nube
    logic: 'salas_conteo: conteo.inscritos de cada sala == su tamaño; salas_ranking: ningún nombre de otra sala en ranking ni en resumen; salas_reloj: cerrar la sala más grande deja las demás en abierto con su abierto_en intacto; salas_csv: resultados.csv de una sala tiene tamaño + 1 líneas; se anotan como no aplicables en modo local'
    violation: 'falla salas_<qué>'
    source: 'FR11.7, FR11.2'
  - id: BR6.3
    statement: 'Con clave ausente, incorrecta o de otra sala, toda ruta /api/admin/* da 403 sin datos.'
    category: authorization
    applies_to: 'parte salas y base (paso 2 y paso 9)'
    trigger: cada corrida
    logic: 'claves_403: sin cabecera 403 (base: «el panel docente exige la clave»); clave inventada 403; en nube la clave de la sala A sobre /api/admin/resumen?sala=B y /api/admin/resultados.csv?sala=B da 403 y el cuerpo no trae participantes; ?clave= en la URL da 403'
    violation: 'falla claves_403'
    source: 'NFR9, FR9.5, FR11.5'
  - id: BR7.1
    statement: 'La latencia se mide durante la carga: p95 de responder + estado por participante y p95 del tablero sondeando cada 2 s.'
    category: calculation
    applies_to: 'paso 5'
    trigger: fase de respuestas
    logic: '40 hilos, uno por participante, cada uno envía sus respuestas en orden y tras cada POST /api/responder pide GET /api/estado; se mide ida y vuelta de los dos juntos; 10 hilos de tablero (uno por sala; en local 10 sobre la misma sala) piden GET /api/publico?sala= cada 2 s mientras dure la fase; p95 = percentil 95 por el método del vecino más cercano sobre todas las muestras; umbrales 1.000 ms y 1.500 ms'
    violation: 'falla nfr_p95_responder o nfr_p95_tablero; las cifras van al JSON aunque fallen'
    source: 'NFR2, NFR3'
  - id: BR7.2
    statement: 'El reinicio a mitad de la prueba lo provoca quien prueba o un comando; la prueba compara el resumen de cada sala antes y después.'
    category: policy
    applies_to: 'paso 6'
    trigger: --reinicio manual o comando
    logic: 'después de la fase de respuestas se guarda el resumen de cada sala (estado, puntos, respondidas y bono por código); IF manual THEN imprime «Reinicia el servicio y pulsa Enter» y espera; IF comando THEN ejecuta el comando y espera a que /api/publico responda 200 (hasta 120 s); después compara: sobrevive_reinicio = igualdad exacta; IF ninguno THEN sobrevive_reinicio = null y no se comprueba'
    violation: 'falla nfr_sobrevive_reinicio'
    source: 'NFR4, FR3.3'
  - id: BR7.3
    statement: 'El arranque en frío es la latencia de la primera petición cuando quien prueba lo pide; si no, es null.'
    category: calculation
    applies_to: 'paso 1'
    trigger: --frio
    logic: 'arranque_frio_ms = ida y vuelta del primer GET /api/publico; umbral 30.000 ms; el LEEME pide correr con --frio después de 15 minutos sin tocar el servicio; sin --frio el valor es null y no hay comprobación'
    violation: 'falla nfr_arranque_frio'
    source: NFR5
  - id: BR7.4
    statement: 'Se cuentan todas las peticiones de la corrida para compararlas con la cuota gratuita.'
    category: calculation
    applies_to: 'toda la corrida'
    trigger: cada petición
    logic: 'peticiones = número de peticiones HTTP enviadas, incluidas las de calibración y los sondeos; va al JSON; la cuota y el porcentaje los calcula U17 con la URL oficial de cada opción'
    violation: no aplica
    source: NFR6
  - id: BR8.1
    statement: 'El JSON de mediciones sigue el esquema C3 con version_esquema 1 y se escribe en mediciones/<opcion>_<AAAA-MM-DD>.json.'
    category: validation
    applies_to: 'cierre de la corrida'
    trigger: fin de la corrida
    logic: 'se valida con validar_medicion antes de escribir (claves obligatorias y tipos); --salida cambia la ruta; una corrida el mismo día sobrescribe el archivo; el JSON no lleva URL con clave, claves, tokens, nombres de la corrida ni respuestas correctas; fracciones lleva {k, pregunta_id, fraccion} y duracion_min como claves agregadas'
    violation: 'no se escribe y la corrida termina con código 1 y el motivo'
    source: 'contrato C3, FR12.4'
  - id: BR8.2
    statement: 'Con --referencia, las fracciones de la corrida se comparan con las de un JSON de la versión local: mismos (k, pregunta_id) y misma fracción.'
    category: validation
    applies_to: 'cierre de la corrida'
    trigger: --referencia <json>
    logic: 'mismas_fracciones_que_local: el conjunto de (k, pregunta_id, fraccion) es idéntico; la referencia es la corrida en --modo local con la misma semilla y participantes; las preguntas con huella desconocida (BR2.4) se excluyen y se anotan en el detalle'
    violation: 'falla mismas_fracciones_que_local con las diferencias (solo ids y fracciones)'
    source: 'NFR11, FR5.5'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.4 | Entrada, salida, detención y tolerancia a 5xx |
| BR2 | BR2.1–BR2.4 | Calibración y clave por texto sin leer el banco |
| BR3 | BR3.1–BR3.3 | Guion determinista y puntos esperados |
| BR4 | BR4.1–BR4.6 | Parte base: equivalencias por HTTP de las 29 comprobaciones |
| BR5 | BR5.1–BR5.4 | Parte fugas (FR6.3) |
| BR6 | BR6.1–BR6.3 | Varias salas y claves (FR11.7, NFR9) |
| BR7 | BR7.1–BR7.4 | Mediciones de NFR2 a NFR6 |
| BR8 | BR8.1–BR8.2 | JSON de C3 y comparación con la versión local |

`casos_reglas.json` (contrato C4) no es de esta unidad: lo empieza U4.
