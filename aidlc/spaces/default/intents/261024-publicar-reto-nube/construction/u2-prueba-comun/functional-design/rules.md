# Reglas — U2 `u2-prueba-comun`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** La prueba ahora usa el único reto del
> servicio con la clave docente (C2, ADR-010). Hace la calibración en ese mismo reto, la borra con
> «Reiniciar» y corre después el reto principal: 40 equipos de 3 colegios con relojes que arrancan a
> distinta hora (FR11.7, NFR1).
>
> - **Revisadas:** BR1.1, BR1.3, BR2.1, BR2.3, BR3.1, BR3.3, BR4.1 a BR4.6, BR5.1 a BR5.3, BR6.1 a
>   BR6.3, BR7.1, BR7.2, BR7.4, BR8.1 y BR8.2. BR6.2 y BR6.3 conservan su id, pero ahora cubren los
>   relojes por colegio y las claves.
> - **Nuevas:**
>   - BR1.5 (reto vacío antes de empezar) y BR1.6 (dejar el reto como estaba);
>   - BR4.7 (una comprobación `pantalla_*` por fila de U6), BR4.8 (los 10 tipos de respuesta), BR4.9
>     (acciones del docente y cierre) y BR4.10 (podio, por grado y nota);
>   - BR5.5 (modo sorpresa) y BR6.4 (errores de la lista de colegios);
>   - BR8.3 (`contrato_api.yaml`).
> - **Comprobaciones retiradas:** `salas_conteo`, `salas_ranking`, `salas_reloj` y `salas_csv`. Ya no
>   hay varias salas que mezclar.

Las reglas de la prueba común completa. Salen de varias fuentes:

- `requirements.md`: FR12.3, FR12.5, FR6.3, FR11.7, FR2.5 y NFR1 a NFR12;
- `unit-of-work.md`, la definición de U2;
- `contract-summary.md`: C1, C2, C3 y la sección «La prueba común con una sola sala»;
- `contract-design-questions.md`: D1 a D10, en especial D6, D8 y D9;
- `bolt-plan.md`, B2;
- lo que U5 y U6 exigen de U2, en la sección «Prueba común» de sus `functional-spec.md`;
- las 30 comprobaciones que imprime `2_Aplicacion_Reto/pruebas/simulacro.py`, que se replican contra una
  URL sin debilitar ninguna.

Las decisiones las tomó el asistente con la potestad que dio el humano («potestad absoluta para decidir»,
2026-10-25).

```yaml
rules:
  - id: BR1.1
    statement: 'La prueba recibe la URL, la clave docente, el modo, la opción y el vencimiento por argumentos o variables de entorno, y nunca escribe la clave en la URL, en la salida ni en el JSON.'
    category: policy
    applies_to: 'arranque de la prueba'
    trigger: cada corrida
    logic: '--url o PRUEBA_URL, --clave o PRUEBA_CLAVE (siempre la clave docente, C2), --modo nube|local, --opcion local|cloudflare, --vencimiento esperar|omitir; sin URL, clave u opción termina con código 2; la clave va solo en X-Clave-Admin, sin recortar ni cambiar mayúsculas; ?clave= solo se usa para comprobar que da 403 (BR6.3)'
    violation: 'código 2 con el mensaje de qué falta'
    source: 'FR12.3, NFR9, D6, C3 («nunca lleva la URL con clave»)'
  - id: BR1.2
    statement: 'Termina en «TODO BIEN» (código 0) o con la lista de comprobaciones que fallaron (código 1), y siempre escribe el JSON de mediciones.'
    category: policy
    applies_to: 'fin de la corrida'
    trigger: cada corrida
    logic: 'IF no hay fallas THEN imprime «TODO BIEN: la opción cumple la prueba común.» y código 0; ELSE imprime «N fallas:» y cada mensaje, código 1; en los dos casos imprime «No aplican: N» con los ids y escribe el JSON (BR8.1); IF no hay conexión THEN código 2 y no escribe el JSON'
    violation: no aplica
    source: 'unit-of-work.md (U2, «salida»)'
  - id: BR1.3
    statement: 'Una comprobación esencial que falla detiene la corrida; una no esencial solo se anota.'
    category: policy
    applies_to: 'todas las comprobaciones'
    trigger: cada comprobación
    logic: 'IF esencial y no pasa THEN se agrega «la prueba se detuvo en <paso>» y se salta al cierre (BR1.6 y BR8.1); son esenciales: entrar al panel con la clave docente, agregar los colegios de prueba, inscribir, comenzar, abrir y publicar el reto, «Reiniciar» tras la calibración y armar la clave por texto'
    violation: no aplica
    source: 'prueba.py de U1 (correr)'
  - id: BR1.4
    statement: 'Cualquier respuesta 5xx sin JSON se trata como {"error": "la respuesta no es JSON"} y cuenta como falla de la comprobación en curso, nunca como excepción.'
    category: validation
    applies_to: 'toda petición'
    trigger: cada respuesta
    logic: 'el cuerpo se intenta leer como JSON; IF falla THEN {"error": ...}; un 503 del servicio (ADR-W20 de U5) o la página 1027 de la cuota diaria de Cloudflare se anotan en el detalle con su código; la prueba no reintenta un POST (contrato C1)'
    violation: no aplica
    source: 'C-15, contrato C1, ADR-W20 de U5'
  - id: BR1.5
    statement: 'La prueba solo corre sobre un reto vacío: en inscripción y sin inscritos.'
    category: policy
    applies_to: 'paso 2'
    trigger: antes de la primera escritura
    logic: 'lee /api/admin/resumen (nube) o /api/admin/estado y /api/publico (local); IF estado != inscripcion OR participantes no está vacía THEN termina con código 2 y «El reto tiene datos. Descarga su paquete y usa «Reiniciar» en el panel, o corre la prueba contra wrangler dev.», sin escribir nada ni el JSON'
    violation: 'código 2 sin tocar el reto'
    source: 'project.md («Forbidden»: no cambiar el banco ni el código con un reto en curso; «Mandated»: desplegar solo sin reto en curso), NFR10.1 (respaldo antes de borrar)'
  - id: BR1.6
    statement: 'Al terminar, la prueba deja el reto como lo encontró: vacío, con la misma configuración, la misma lista de colegios y sin las copias que ella creó.'
    category: policy
    applies_to: 'paso 12'
    trigger: fin de la corrida, también tras una esencial que falló
    logic: 'IF el reto tiene datos de la prueba THEN «Reiniciar» con BORRAR; POST /api/admin/config con duracion_min, modo_sorpresa y retro de ConfiguracionInicial; agregar los nombres de ConfiguracionInicial.colegios en una sola llamada (agregar con nombres); POST /api/admin/copia/borrar por cada id de copias_creadas, nunca de ConfiguracionInicial.copias; en local solo se restaura la configuración y las copias quedan como archivo (la versión local no las borra); un fallo aquí es la falla «reto_restaurado» con lo que no se pudo restaurar'
    violation: 'falla reto_restaurado (no esencial)'
    source: 'D7 (copias que el docente borra), FR11.6, ADR-009 (los id_colegio no se conservan entre retos)'
  - id: BR2.1
    statement: 'La prueba no conoce el banco: toda respuesta correcta sale de revision después de publicar los resultados de un reto de calibración, que después se borra con «Reiniciar».'
    category: policy
    applies_to: 'calibración (paso 3)'
    trigger: antes del reto principal
    logic: 'en el mismo y único reto: nube agrega el colegio «Colegio Calibración <sufijo>»; local escribe ese nombre como texto; se fija duracion_min (BR4.2), se inscribe, se abre, se cierra, se publica, se arma la clave y se reinicia con BORRAR; la copia va a copias_creadas; la clave queda en memoria y nunca se escribe ni se imprime; no se lee banco_preguntas.json ni ningún otro archivo del repositorio'
    violation: no aplica
    source: 'NFR8, ADR-011 (una sala), project.md («Forbidden»: nunca respuestas en material ni artefactos)'
  - id: BR2.2
    statement: 'La variante de cada pregunta se reconoce por su huella: sha256 de los textos visibles sin ids ni orden.'
    category: calculation
    applies_to: 'calibración y guion'
    trigger: cada /api/estado con misiones
    logic: 'huella = sha256(JSON ordenado de {enunciado, textos de opciones, ítems, publicaciones y categorías ordenados alfabéticamente, etiquetas de partes con los textos de sus opciones, min, max}); la misma pregunta con dos huellas distintas son dos variantes'
    violation: no aplica
    source: 'banco_preguntas.json (m2_trampas tiene 4 variantes que cambian solo los ítems), ADR-006'
  - id: BR2.3
    statement: 'Se inscriben 40 calibradores, se eligen representantes que cubran cada (pregunta, huella) y solo ellos responden todo; la clave por texto sale de su revision con el reto en resultados.'
    category: calculation
    applies_to: 'calibración (paso 3)'
    trigger: reto de calibración abierto
    logic: 'en la nube, al abrir arranca el colegio de calibración (tiene equipos); cada calibrador comienza y pide /api/estado; se eligen representantes de forma voraz hasta cubrir todas las (pregunta, huella) vistas; los representantes responden cada pregunta con una respuesta válida cualquiera (primera opción, la misma categoría para todos, el orden recibido, la mitad del rango) y entregan; el reto pasa a cerrado y a resultados; de la revision de cada representante se arma ClavePorTexto, traduciendo ids opacos a textos con sus propias misiones; la probabilidad de no ver una de 4 variantes con 40 calibradores es 4 × (3/4)^40 ≈ 0,00004'
    violation: 'esencial: «no se pudo armar la clave por texto» detiene la corrida'
    source: 'ADR-006 (la clave solo con el reto en resultados), FR6.3'
  - id: BR2.4
    statement: 'Un participante del reto principal cuya huella no esté en la clave por texto es una falla, nunca una adivinanza.'
    category: validation
    applies_to: 'guion (paso 5)'
    trigger: al armar las respuestas de un participante
    logic: 'IF (pregunta, huella) no está en ClavePorTexto THEN falla «clave_por_texto_completa» con el id de la pregunta, y el participante responde esa pregunta como «fallo»; puntos_esperados no la cuenta'
    violation: 'falla no esencial con el id de la pregunta'
    source: BR2.3
  - id: BR3.1
    statement: 'El guion es determinista: la semilla 7 y el índice k fijan el colegio, el papel, el grado y qué preguntas acierta cada participante.'
    category: calculation
    applies_to: 'guion'
    trigger: antes de inscribir
    logic: 'random.Random(semilla_guion), como random.seed(7) de simulacro.py; colegio por k según BR6.1; papel por k: 0 perfecto, 1 cero, 2 parcial, 3 vencido_sin_respuestas, 4 y 5 vencido_al_final, 6 llega_tarde, el último de A entregado_docente (todos en el colegio A); el primero de B no_inicia; el primero de C vencido_colegio; los demás normal, con acierto si azar < 0,25 + 0,7 × nivel; grado = 9, 10 u 11 según k mod 3'
    violation: no aplica
    source: 'simulacro.py (main, «2) Respuestas»), NFR11, FR11.7'
  - id: BR3.2
    statement: 'Cada respuesta se arma con la clave por texto y los ids que ese participante recibió: acertar, fallar o a medias.'
    category: calculation
    applies_to: 'guion'
    trigger: cada pregunta de cada participante
    logic: 'acertar: la respuesta correcta traducida a los ids del participante; fallar: opcion otra opción, multiple una opción fuera de la clave, clasificar cada ítem en otra categoría, ordenar al revés, construir otra opción en cada parte, numero clave + 1000, estimar el extremo del rango más lejano, texto una conclusión fija, compartir y recordatorio una categoría cualquiera (sin puntos); a medias: clasificar y construir aciertan la primera mitad redondeada hacia arriba por orden alfabético del texto y fallan el resto, multiple la clave más una opción de sobra, ordenar la clave con los dos primeros intercambiados, los demás tipos como acertar'
    violation: no aplica
    source: 'simulacro.py (respuesta_para), api-documentation.md (forma de cada tipo), FR2.1'
  - id: BR3.3
    statement: 'Los puntos esperados de un participante son la suma de los puntos de las preguntas que el guion decidió acertar y que alcanzó a enviar; a medias no suma a lo esperado.'
    category: calculation
    applies_to: 'guion y calificación (paso 8)'
    trigger: al armar el guion y al entregar
    logic: 'puntos_esperados = Σ puntos públicos de las preguntas con decisión acertar que recibieron 200 en /api/responder; las preguntas sin clave (hipótesis, informe, compartir, recordatorio) valen 0; al entregado_docente solo le cuentan las enviadas antes de que el panel lo entregue; para el papel parcial solo se registran las fracciones y se exige 0 < fracción < 1 en clasificar, multiple, ordenar y construir'
    violation: no aplica
    source: 'FR2.1, NFR11'
  - id: BR4.1
    statement: 'La parte base repite las 30 comprobaciones de simulacro.py por HTTP, con la misma condición o una equivalente que no abra la base ni mueva el reloj, y agrega las comprobaciones de pantallas, tipos, acciones y resultados.'
    category: policy
    applies_to: 'parte base'
    trigger: cada corrida
    logic: 'la tabla «Parte base» de functional-spec.md da la equivalencia de cada una; una comprobación solo se reemplaza por otra que verifique la misma propiedad por la API; una comprobación que necesita algo que la versión local no tiene (lista de colegios, por grado, paquete, copias por la API) va a no_aplica en modo local con ese motivo, nunca a pasa'
    violation: no aplica
    source: 'FR12.3, FR6.3, unit-of-work.md (U2, «sin debilitar ninguna»), ADR-W21 de U6'
  - id: BR4.2
    statement: 'El vencimiento se prueba esperando el fin real de cada reloj: con 2 minutos contra wrangler dev (D9), con 10 contra la versión local y nunca contra la URL pública.'
    category: calculation
    applies_to: 'paso 7'
    trigger: --vencimiento esperar
    logic: 'antes de abrir se fija duracion_min = --duracion-min con POST /api/admin/config y se lee lo que guardó el servidor; wrangler dev acepta 1 o más porque .dev.vars trae DURACION_MINIMA_MIN=1 (D9) y la prueba usa 2 para que 40 equipos alcancen a responder; la prueba espera hasta arranque_C + duración + 2 s (en local, abierto_en + duración + 2 s); después, el vencido_sin_respuestas aparece finalizado con tiempo_usado igual a la duración (± 0,001 s) y motivo tiempo; responder da 400; comenzar del que llega tarde da 400 «ya terminó»; IF --vencimiento omitir THEN base_comenzar_vencido, base_vence_solo, base_fuera_de_tiempo, la parte del vencido en base_bono_final y relojes_vence_por_colegio van a no_aplica con el motivo «sin vencimiento real contra la URL pública (D9)», y el reto se cierra a mano'
    violation: no aplica
    source: 'D9, C-09, FR3.2, FR3.3, OQ3, bolt-plan.md (B2)'
  - id: BR4.3
    statement: 'El bono se verifica sin mover el reloj y medido desde el arranque del colegio: 0 para quien no respondió y acotado por la fórmula para quien respondió en los últimos 15 s.'
    category: calculation
    applies_to: 'paso 8'
    trigger: después del vencimiento (o del cierre, con omitir)
    logic: 'vencido_sin_respuestas: bono == 0 y puntos == 0; vencido_al_final: su última pregunta se envía en arranque_A + duración − 15 s, y se exige bono ≤ 20 × (puntos / 1.000) × (15 / duración) + 0,01 (el resumen redondea a 2) y tiempo_usado igual a la duración; es la misma propiedad de simulacro.py («quien responde su última pregunta al final del tiempo no recibe bono») con el tiempo real en vez de inicio − 6.000'
    violation: no aplica
    source: 'simulacro.py («4) Calificación»), FR2.2, FR2.6'
  - id: BR4.4
    statement: 'El reloj de cada participante sale del de su colegio: su inicio coincide con el arranque del colegio.'
    category: calculation
    applies_to: 'paso 5'
    trigger: participantes en curso
    logic: 'inicio_k = servidor_ahora + colegio_restante_seg − duración, con los tres valores de un mismo /api/estado; se exige |inicio_k − colegio_arranque| < 0,01 s para todos los participantes en curso; para el colegio A, colegio_arranque es abierto_en; en local se usa restante_seg y abierto_en, como en simulacro.py'
    violation: no aplica
    source: 'simulacro.py («2b) Reloj global»), FR3.1, FR11.7, ADR-011, D2'
  - id: BR4.5
    statement: 'Los datos que simulacro.py lee de la base salen de /api/admin/resumen: id, id_colegio, grupo, puntos, bono, total, tiempo_usado, tiempo_respuestas, puesto, puesto_grado y nota.'
    category: policy
    applies_to: 'parte base'
    trigger: cada comprobación que hoy lee SQLite
    logic: 'el grupo A/B para el recordatorio, el id para las acciones del docente y para eliminar al que llega tarde y las cifras de calificación se leen del resumen con la clave docente; la lista ordenada por puesto debe respetar el orden de U4 (total ↓, puntos ↓, tiempo_respuestas ↑, tiempo_usado ↑, id ↑), con comparaciones no estrictas porque el resumen redondea a 2 decimales, y puesto va de 1 a n sin repetir'
    violation: no aplica
    source: 'FR2.3, NFR11, api-documentation.md (resumen), contrato C1 («Resumen del panel»)'
  - id: BR4.6
    statement: 'La copia de «Reiniciar» se verifica por la API: en la nube aparece en /api/admin/copias, se descarga y se borra; en local se exige que la respuesta la nombre.'
    category: policy
    applies_to: 'paso 10'
    trigger: después de reiniciar
    logic: 'IF nube THEN copia es un id_copia; GET /api/admin/copias lo contiene; GET /api/admin/copia?id= responde 200 con un cuerpo no vacío; POST /api/admin/copia/borrar lo quita de la lista; IF local THEN copia es un nombre no vacío que termina en .db, y el archivo lo sigue comprobando simulacro.py; en los dos casos conteo.inscritos == 0 y el estado vuelve a inscripcion; en la nube la lista de colegios queda vacía (U6, BR5.2)'
    violation: no aplica
    source: 'simulacro.py («7) Reinicio»), D7, contrato C1 (/api/admin/copias)'
  - id: BR4.7
    statement: 'Cada fila de la tabla «Pantallas completas» de U6 tiene su comprobación pantalla_* en la parte base: la ruta responde y trae las claves que la pantalla lee.'
    category: validation
    applies_to: 'parte base (pasos 3 a 10)'
    trigger: la primera vez que la corrida usa cada ruta, en el estado que pide la fila
    logic: 'pantalla_<id> pasa IF el código es 200 (o el error que espera la pantalla) AND el cuerpo trae cada clave de la columna «Qué usa la pantalla» de U6; los archivos (CSV, zip, copia) se exigen con su Content-Type y un cuerpo no vacío; en modo local, pantalla_colegios, pantalla_colegios_admin, pantalla_paquete, pantalla_copias, pantalla_copia y pantalla_copia_borrar van a no_aplica («la versión local no tiene esa ruta»)'
    violation: 'falla pantalla_<id> con la clave que faltó'
    source: 'criterio del humano (2026-10-26): «que ya todos los paneles funcionen, el dash, el de admin y el de los estudiantes»; ADR-W21 y BR10.2 de U6; FR4.1'
  - id: BR4.8
    statement: 'Cada uno de los 10 tipos de respuesta tiene una respuesta aceptada y una rechazada, y la rechazada no gasta la pregunta.'
    category: validation
    applies_to: 'parte base (paso 5)'
    trigger: el primer participante normal que recibe cada tipo
    logic: 'antes de su respuesta del guion, envía una inválida: un id que no está entre los suyos (opcion, multiple, compartir, recordatorio, clasificar, ordenar, construir), un texto vacío (texto) o un valor que no es número (estimar, numero); se exige 400; después la del guion da 200; tipos_respuesta pasa IF los 10 tipos cumplen las dos cosas'
    violation: 'falla tipos_respuesta con el tipo'
    source: 'U5 («Prueba común»: una respuesta de cada uno de los 10 tipos aceptada y una rechazada), FR2.4'
  - id: BR4.9
    statement: 'Las cuatro acciones del docente funcionan y cerrar entrega a todos y deja «No inició» a quien no empezó.'
    category: validation
    applies_to: 'parte base (pasos 5 y 9)'
    trigger: reto principal abierto y al cerrarlo
    logic: 'acciones_docente: con POST /api/admin/participante, «anular» y «reactivar» a un participante normal (el resumen lo muestra descalificado y luego en curso, con sus respuestas intactas), «entregar» al entregado_docente (finalizado) y «eliminar» al que llega tarde (desaparece del resumen); cierre_no_inicio: tras cerrar, el no_inicia está en no_inicio y ningún participante queda en_curso'
    violation: 'falla acciones_docente o cierre_no_inicio'
    source: 'U5 («Prueba común»: cerrar entrega a todos y deja «No inició»; las cuatro acciones del docente), contrato C1 («Cambios de estado»)'
  - id: BR4.10
    statement: 'En resultados, el tablero y el estudiante muestran el podio general, la clasificación por grado y la nota, coherentes con el resumen.'
    category: validation
    applies_to: 'parte base (paso 9)'
    trigger: reto principal en resultados
    logic: 'resultados_por_grado: por_grado trae "9", "10" y "11"; cada lista es la del orden general filtrada por grado, con puesto_grado de 1 a n sin repetir, como mucho 10 filas; resultados_nota: nota y puesto_grado de cada fila de ranking y de por_grado son los del mismo participante en /api/admin/resumen; base_revision además exige puesto_grado y nota en /api/estado del finalizado; en local, resultados_por_grado va a no_aplica y resultados_nota se compara solo en ranking'
    violation: 'falla resultados_por_grado o resultados_nota'
    source: 'FR2.5, D2, D4, U6 («Prueba común»)'
  - id: BR5.1
    statement: 'Ninguna clave secreta llega sin clave docente antes de resultados: ni en /api/estado, ni en /api/publico, ni en /api/colegios.'
    category: policy
    applies_to: 'parte fugas'
    trigger: cada /api/estado, /api/publico y /api/colegios que la prueba pide antes de resultados
    logic: 'claves secretas = {respuesta dentro de misiones, explicacion, tolerancia, verdad, multitud_acierta, veredicto} y la clave revision; se recorren todas las respuestas a cualquier profundidad; fuga_revision_antes es la de revision; la lista se amplía con cada clave nueva del contrato que llegue sin clave docente (C-14)'
    violation: 'falla fuga_<ruta>_<estado> o fuga_revision_antes'
    source: 'FR6.3, NFR8, C-14, U6 («Prueba común»)'
  - id: BR5.2
    statement: 'En cerrado, /api/publico solo trae n y listo del experimento; en resultados lo trae completo.'
    category: policy
    applies_to: 'parte fugas (pasos 3 y 9)'
    trigger: reto en cerrado y luego en resultados, en la calibración y en el principal
    logic: 'fuga_verdad_cerrado: claves_de(publico.experimento) ⊆ {n, listo}; experimento_completo_resultados: en resultados por_publicacion[] trae verdad y multitud_acierta; falla con la versión local de hoy y pasa con Cloudflare (D5)'
    violation: 'falla fuga_verdad_cerrado'
    source: 'FR6.1, D5'
  - id: BR5.3
    statement: 'Todos los ids de opciones, ítems, publicaciones y partes que ve el navegador son opacos, y el orden de las opciones no es el mismo para todos.'
    category: policy
    applies_to: 'parte fugas (paso 5)'
    trigger: el primer /api/estado de cada participante del reto principal
    logic: 'fuga_ids_opacos: cada id cumple ^o[a-z2-7]{11}([a-z2-7]{5})?$; fuga_orden_banco: para cada pregunta con 3 o más opciones o ítems, entre los participantes hay al menos dos órdenes distintos de textos; con 20 o menos participantes la comprobación va a no_aplica'
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
  - id: BR5.5
    statement: 'Con modo sorpresa, ranking y por_grado se ocultan juntos hasta publicar; sin él, salen juntos.'
    category: policy
    applies_to: 'parte fugas (paso 5)'
    trigger: reto principal abierto
    logic: 'sorpresa_oculta_juntos: POST /api/admin/config con modo_sorpresa true; GET /api/publico no trae ranking ni por_grado; con false trae los dos; el valor se deja como estaba en ConfiguracionInicial; en local se mira solo ranking'
    violation: 'falla sorpresa_oculta_juntos'
    source: 'D4, U6 («Prueba común»: ranking y por_grado ocultos juntos con modo sorpresa)'
  - id: BR6.1
    statement: 'El reto principal tiene 40 equipos de 3 colegios cuyos relojes arrancan a 0, 20 y 40 segundos de la apertura.'
    category: policy
    applies_to: 'pasos 4 y 5'
    trigger: modo nube
    logic: 'tamaños A 20, B 12 y C 8 (suman 40, NFR1); con --participantes distinto de 40: A = la mitad redondeada hacia arriba, C = la quinta parte redondeada hacia arriba (mínimo 2) y B el resto; los colegios se agregan en inscripción con una sola llamada (agregar con nombres); los equipos de A se inscriben antes de abrir y los de B y C después, para que al abrir arranque solo A; B y C se arrancan con «Arrancar reloj» a 20 y 40 s de abierto_en; en local los tres nombres van como texto, todos se inscriben antes de abrir y el reloj es uno solo'
    violation: no aplica
    source: 'NFR1, FR11.7, FR12.5, ADR-011 (abrir arranca los colegios con equipos), contrato C2'
  - id: BR6.2
    statement: 'Cada colegio tiene su reloj: arranca a su hora, sus participantes cuentan desde ahí y vence por su cuenta.'
    category: validation
    applies_to: 'parte relojes (pasos 4, 5 y 7)'
    trigger: modo nube; en local toda la parte va a no_aplica («la versión local tiene un solo reloj», FR12.3)
    logic: 'relojes_arranques: en colegios[] del resumen, arranque_A = abierto_en y arranque_A < arranque_B < arranque_C con al menos 15 s entre cada uno; relojes_espera_colegio: un equipo de C que pulsa comenzar antes del arranque de C recibe 400 «Tu colegio todavía no ha empezado. Espera la señal del docente.» y, tras arrancar, comenzar da 200; relojes_inicio_por_colegio: BR4.4 para los tres colegios; relojes_bono_desde_arranque: para un participante de B y uno de C, con servidor_ahora de los /api/estado de antes y de después de su última respuesta, se exige servidor_ahora_antes − arranque ≤ tiempo_respuestas ≤ servidor_ahora_despues − arranque y bono igual a 20 × (puntos / 1.000) × (1 − tiempo_respuestas / duración) con tolerancia de 0,01; relojes_vence_por_colegio (solo con esperar): en arranque_A + duración + 2 s el vencido_sin_respuestas de A está finalizado y el vencido_colegio de C sigue en curso con colegio_restante_seg > 0; en arranque_C + duración + 2 s el de C está finalizado con tiempo_usado igual a la duración; relojes_conteo: equipos de cada colegio igual a su tamaño'
    violation: 'falla relojes_<qué>'
    source: 'FR11.7, FR2.6, FR11.5, ADR-011, U5 («Prueba común»: un colegio arrancado tarde que vence a su hora)'
  - id: BR6.3
    statement: 'Toda ruta /api/admin/* exige la clave docente exacta en la cabecera; la clave en la URL da 403 y las rutas quitadas dan 404.'
    category: authorization
    applies_to: 'parte claves y base (paso 2)'
    trigger: cada corrida
    logic: 'base_panel_clave: sin cabecera 403; claves_incorrecta: una clave inventada 403 y sin datos; claves_url: ?clave=<la correcta> con la cabecera correcta 403 (D6); claves_mayusculas: la clave con las mayúsculas cambiadas 403; claves_espacios: la clave con espacios en los extremos 200 (ADR-010 recorta); claves_login: POST /api/admin/login responde solo ok, sin rol; claves_rutas_quitadas: POST /api/admin/salas/crear 404; claves_publico_sin_sala: GET /api/publico sin parámetros trae estado, conteo y colegios[]; en local solo aplica base_panel_clave y claves_incorrecta, las demás van a no_aplica («la versión local no cambia», FR12.1)'
    violation: 'falla claves_<qué>'
    source: 'NFR9, FR9.5, ADR-010, D6, contrato C2, project.md («Corrections»: nunca la clave en la URL)'
  - id: BR6.4
    statement: 'La lista de colegios rechaza lo que el contrato rechaza y no cambia nada cuando rechaza.'
    category: validation
    applies_to: 'parte relojes (pasos 4 y 5)'
    trigger: modo nube
    logic: 'colegios_errores: agregar «ab» da 400 «Escribe el nombre del colegio (al menos 3 letras).»; agregar un nombre que ya existe (con otras mayúsculas) junto a uno nuevo da 400 «Ese colegio ya existe.» con existente y no agrega el nuevo; quitar un colegio con equipos da 400 «Ese colegio ya tiene equipos inscritos; no se puede quitar.»; arrancar antes de abrir da 400 «Abre el reto antes de arrancar un colegio.»; arrancar dos veces da 400 «Ese colegio ya arrancó.»; quitar un colegio sin equipos da 200 y desaparece de /api/colegios'
    violation: 'falla colegios_errores con el caso'
    source: 'contrato C1 (POST /api/admin/colegios), D3, U5 (BR4.2 a BR4.4)'
  - id: BR7.1
    statement: 'La latencia se mide durante la carga: p95 de responder + estado por participante, p95 del tablero sondeando cada 2 s y p95 del panel sondeando cada 3 s.'
    category: calculation
    applies_to: 'paso 5'
    trigger: fase de respuestas
    logic: 'un hilo por participante, que envía sus respuestas en orden y tras cada POST /api/responder pide GET /api/estado; se mide la ida y vuelta de los dos juntos; un hilo de tablero pide GET /api/publico cada 2 s y un hilo de panel pide GET /api/admin/resumen cada 3 s (como admin.js) mientras dure la fase; p95 = percentil 95 por el método del vecino más cercano; umbrales 1.000 ms (responder) y 1.500 ms (tablero); p95_resumen_ms se anota sin umbral'
    violation: 'falla nfr_p95_responder o nfr_p95_tablero; las cifras van al JSON aunque fallen'
    source: 'NFR2, NFR3, admin.js (refresco cada 3 s)'
  - id: BR7.2
    statement: 'El reinicio a mitad de la prueba lo provoca quien prueba o un comando; la prueba compara el resumen antes y después.'
    category: policy
    applies_to: 'paso 6'
    trigger: --reinicio manual o comando
    logic: 'después de la fase de respuestas se guarda el resumen del reto (estado, puntos, respondidas y bono por código, y colegios[] con su arranque); IF manual THEN imprime «Reinicia el servicio y pulsa Enter» y espera; IF comando THEN ejecuta el comando y espera a que /api/publico responda 200 (hasta 120 s); después compara: sobrevive_reinicio = igualdad exacta; los relojes siguieron corriendo durante la caída (FR3.3); IF ninguno THEN sobrevive_reinicio = null y no se comprueba'
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
    logic: 'peticiones = número de peticiones HTTP enviadas, incluidas las de calibración, los sondeos y la restauración; va al JSON; U17 lo compara con las 100.000 peticiones diarias del plan gratuito de Workers (https://developers.cloudflare.com/workers/platform/limits/) y con lo que pide un reto real de 90 minutos'
    violation: no aplica
    source: 'NFR6, ADR-W20 de U5'
  - id: BR8.1
    statement: 'El JSON de mediciones sigue el esquema C3 revisado, con version_esquema 1, y se escribe en mediciones/<opcion>_<AAAA-MM-DD>.json.'
    category: validation
    applies_to: 'cierre de la corrida'
    trigger: fin de la corrida
    logic: 'se valida con validar_medicion antes de escribir (claves obligatorias, tipos y parte ∈ {base, fugas, relojes, claves, nfr}); nfr.colegios = colegios arrancados a distinta hora (3 en la nube, 1 en local); las comprobaciones de no_aplica no van en comprobaciones sino en nfr.no_aplica con su motivo; --salida cambia la ruta; una corrida el mismo día sobrescribe el archivo; el JSON no lleva URL con clave, claves, tokens, nombres de la corrida ni de colegios, ni respuestas correctas; fracciones lleva {k, pregunta_id, fraccion}; duracion_min, vencimiento y encabezados_csv van como claves agregadas'
    violation: 'no se escribe y la corrida termina con código 1 y el motivo'
    source: 'contrato C3, D8, FR12.4'
  - id: BR8.2
    statement: 'Con --referencia, la corrida se compara con un JSON de la versión local: mismas fracciones por (k, pregunta_id) y mismos encabezados de los dos CSV.'
    category: validation
    applies_to: 'cierre de la corrida'
    trigger: --referencia <json>
    logic: 'mismas_fracciones_que_local: el conjunto de (k, pregunta_id, fraccion) es idéntico, sin contar al entregado_docente ni a las preguntas con huella desconocida (BR2.4), que se anotan en el detalle; mismos_csv_que_local: encabezados_csv.resultados y encabezados_csv.respuestas son idénticos (FR4.3: los CSV no cambian de columnas); la referencia es la corrida en --modo local con la misma semilla y participantes'
    violation: 'falla mismas_fracciones_que_local o mismos_csv_que_local con las diferencias (solo ids, fracciones y nombres de columna)'
    source: 'NFR11, FR5.5, FR4.3, U6 («Prueba común»: CSV iguales a los de la versión local)'
  - id: BR8.3
    statement: 'U2 crea despliegues/prueba_comun/contrato_api.yaml tal cual el contenido inicial del contrato, y toda ruta que llama la prueba está en él.'
    category: policy
    applies_to: 'entrega de la unidad'
    trigger: el primer push de U2
    logic: 'el archivo se copia del bloque «Contenido inicial de contrato_api.yaml» de contract-summary.md sin editarlo; pruebas/test_contrato.py lee el YAML con un lector mínimo de rutas (sin paquetes) y exige que cada (método, ruta) que usa cliente.py exista en paths; U6 lo usa en pantallas.test.js (ADR-W21)'
    violation: 'falla de test_contrato.py con la ruta que falta'
    source: 'contrato C1 y C2 («Dónde vive»: U2 lo crea tal cual), ADR-W21 de U6'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.6 | Entrada, salida, detención, tolerancia a 5xx, reto vacío y restauración |
| BR2 | BR2.1–BR2.4 | Calibración en el mismo reto y clave por texto sin leer el banco |
| BR3 | BR3.1–BR3.3 | Guion determinista, papeles por colegio y puntos esperados |
| BR4 | BR4.1–BR4.10 | Parte base: las 30 de `simulacro.py`, pantallas, tipos, acciones y resultados |
| BR5 | BR5.1–BR5.5 | Parte fugas (FR6.3) y modo sorpresa |
| BR6 | BR6.1–BR6.4 | Relojes por colegio (FR11.7), claves (NFR9) y lista de colegios |
| BR7 | BR7.1–BR7.4 | Mediciones de NFR2 a NFR6 |
| BR8 | BR8.1–BR8.3 | JSON de C3, comparación con la versión local y `contrato_api.yaml` |

`casos_reglas.json` (contrato C4) no es de esta unidad: lo empieza U4.
