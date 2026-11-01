# Reglas — U5 `u5-cloudflare-salas` (reto, colegios y relojes)

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Una sola sala, una clave docente y un reloj
> por colegio (ADR-009 a ADR-011, contrato revisado). **Retiradas:** BR1.2 (regenerar clave de sala),
> BR2.1 (listar salas), BR2.4 (borrar sala), BR3.1 y BR3.2 (catálogo del semillero) y BR4.1 (colegios de
> la sala); sus ids no se reutilizan. **Cambian:** BR1.1, BR1.3, BR2.2, BR2.3, BR2.5, BR5.1, BR5.2, BR6.2,
> BR6.3, BR7.1 y BR8.1. **Nuevas:** BR1.4 a BR1.6 (clave docente), BR4.2 a BR4.5 (colegios y relojes),
> BR6.4 y BR6.5 (comenzar y lo que ve el estudiante), BR7.2 (tablero en U5) y BR9.1 (cada llamada de las
> pantallas tiene ruta, criterio del humano del 2026-10-26).

Las reglas de Acceso, CicloDelReto, Colegios, Inscripcion y Examen completos. Salen de `requirements.md`
(FR1, FR2.4, FR3, FR7.2, FR7.4, FR10, FR11, NFR9), de `components.md`, del contrato
(`contract-summary.md`, C1) y de `servidor.py`. Las reglas de U1
(`../../u1-cloudflare-corte/functional-design/rules.md`) que no son de varias salas siguen vigentes. Las
calculadoras son las de U4 (`../../u4-cloudflare-reglas/functional-design/rules.md`). Decisiones en
`../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20).

```yaml
rules:
  - id: BR1.1
    statement: 'Cada ruta declara uno de tres niveles; lo que no esta en la tabla da 404.'
    category: authorization
    applies_to: 'todas las rutas (tabla en functional-spec.md, «Rutas»)'
    trigger: cada petición
    logic: 'niveles publico (sin credencial), token (Authorization: Bearer <token>; sin token o con uno que no existe, 401 «Sesión no encontrada. Vuelve a entrar con tu código.») y clave (X-Clave-Admin con la clave docente, todo /api/admin/*); desaparecen los niveles sala y semillero y las funciones sala_de_acceso, sala_por_codigo y sala_de; ?sala= se ignora en toda ruta; las rutas del corte que ya no existen (salas/crear, salas, salas/clave, salas/borrar, catalogo) dan 404 «No encontrado.»'
    violation: '401, 403 o 404'
    source: 'FR7.2, FR11.1, ADR-010, contrato «Reglas comunes» y «Rutas y claves eliminadas»'
  - id: BR1.2
    statement: 'Retirada el 2026-10-25: no hay claves de sala que regenerar (ADR-010).'
    category: policy
    applies_to: 'ninguna'
    trigger: no aplica
    logic: 'POST /api/admin/salas/clave da 404 (BR1.1)'
    violation: no aplica
    source: 'ADR-010'
  - id: BR1.3
    statement: 'Una clave ausente o incorrecta responde 403 tras la misma espera corta que un codigo inexistente; no hay bloqueo por intentos.'
    category: policy
    applies_to: 'rutas de nivel clave'
    trigger: clave ausente o incorrecta
    logic: 'esperar 600 ms fuera del bloqueo del objeto, como entrar; sin contador de intentos (ADR-010, ADR-W12); responde 403 {"error": "Clave de docente incorrecta."} sin ningun otro dato'
    violation: '403 «Clave de docente incorrecta.»'
    source: 'NFR9, OQ6 (cerrada en ADR-010), ADR-W12'
  - id: BR1.4
    statement: 'La clave docente se compara con el secreto CLAVE_DOCENTE en tiempo constante, quitando los espacios de los extremos y sin cambiar mayusculas.'
    category: authorization
    applies_to: 'acceso_admin en reto.js'
    trigger: cada petición de nivel clave
    logic: 'recibida = (cabecera X-Clave-Admin o «»).trim(); ok = iguales_en_tiempo_constante(sha256_hex(recibida), sha256_hex(env.CLAVE_DOCENTE.trim())); nunca toUpperCase; la clave no se registra ni se guarda en la base; desaparece CLAVE_SEMILLERO'
    violation: 'BR1.3'
    source: 'NFR9, ADR-010, D6 del contrato'
  - id: BR1.5
    statement: 'Una peticion a /api/admin/* con clave en la URL recibe 403 aunque la cabecera sea correcta.'
    category: authorization
    applies_to: 'rutas de nivel clave'
    trigger: la URL trae el parámetro clave
    logic: 'IF url.searchParams.has("clave") THEN 403 «Clave de docente incorrecta.» antes de mirar la cabecera; asi la clave nunca queda en los registros del hosting'
    violation: 403
    source: 'FR9.5, D6 del contrato, project.md («Corrections»: sin ?clave=)'
  - id: BR1.6
    statement: 'El servicio no atiende si CLAVE_DOCENTE falta o tiene menos de 12 caracteres.'
    category: constraint
    applies_to: 'arranque del objeto'
    trigger: cada arranque
    logic: 'IF env.CLAVE_DOCENTE falta o env.CLAVE_DOCENTE.trim() tiene menos de 12 caracteres THEN el registro dice «CLAVE_DOCENTE falta o tiene menos de 12 caracteres» sin mostrarla y toda peticion recibe 500 «Error interno del servidor.», tambien el chequeo de salud, para que el despliegue no pase la prueba de humo'
    violation: '500 en toda ruta'
    source: 'NFR9, ADR-010, contrato «Reglas comunes»'
  - id: BR2.1
    statement: 'Retirada el 2026-10-25: no hay lista de salas (FR11.1).'
    category: policy
    applies_to: 'ninguna'
    trigger: no aplica
    logic: 'GET /api/admin/salas da 404 (BR1.1)'
    violation: no aplica
    source: 'FR11.1, ADR-011'
  - id: BR2.2
    statement: 'Configurar el reto sigue las reglas de hoy; el reloj ya no se configura.'
    category: validation
    applies_to: 'POST /api/admin/config'
    trigger: el docente guarda un campo
    logic: 'IF reloj_global en el cuerpo THEN 400 «El reloj es por colegio y ya no se configura.» sin aplicar nada; modo_sorpresa y retro (booleanos) en cualquier estado; sala = normalizar_texto(sala, 8) en mayusculas; IF no cumple [A-Z0-9]{3,8} THEN 400 «La sala debe tener de 3 a 8 letras o números.»; evento limpio a 80 y «Reto» si queda vacio; duracion_min solo en inscripcion, si no 400 «La duración solo se cambia antes de abrir el reto.»; duracion_min = max(minimo, min(240, entero)) con minimo = 10, o DURACION_MINIMA_MIN si esa variable existe en el entorno (solo .dev.vars de wrangler dev, D9; entero de 1 a 10); todo en una transaccion'
    violation: 400 con el mensaje
    source: 'FR11.1, D1 y D9 del contrato, bloque config de servidor.py'
  - id: BR2.3
    statement: 'Cambiar el estado aplica transicion_permitida con sus efectos: abrir arranca los colegios con equipos y cerrar entrega lo de todos los colegios.'
    category: calculation
    applies_to: 'POST /api/admin/estado'
    trigger: el docente pulsa Abrir, Cerrar o Publicar
    logic: 'IF estado no valido THEN 400 «Estado no válido.»; IF igual al actual THEN ok sin hacer nada; IF !transicion_permitida THEN 400 «Ese cambio de estado no está permitido.»; abierto: abierto_en = COALESCE(abierto_en, ahora) y arranque = ahora para cada id de colegios_al_abrir(colegios con su conteo de equipos); cerrado: cerrado_en = COALESCE(cerrado_en, ahora), cada en_curso se cierra con cerrar(participante, ahora, cierre) y cada registrado pasa a no_inicio (estado_tras_cierre); resultados: solo el estado; todo en una transaccion; se registra el cambio sin datos'
    violation: 400 con el motivo
    source: 'FR1.1, FR1.2, FR3.1, FR7.4, ADR-004, ADR-011, contrato «Cambios de estado»'
  - id: BR2.4
    statement: 'Retirada el 2026-10-25: no se borra una sala; «Reiniciar» (U6) borra el reto entero tras una copia.'
    category: policy
    applies_to: 'ninguna'
    trigger: no aplica
    logic: 'POST /api/admin/salas/borrar da 404 (BR1.1)'
    violation: no aplica
    source: 'FR11.6, NFR10.1'
  - id: BR2.5
    statement: 'El reto no se cierra solo.'
    category: policy
    applies_to: CicloDelReto
    trigger: vencimiento del reloj de un colegio
    logic: 'cada intento vence por hora_de_entrega con el arranque de su colegio; el reto sigue abierto hasta que el docente lo cierre, como hoy; un colegio puede arrancar mas tarde'
    violation: no aplica
    source: 'OQ8, ADR-W12, FR1.1'
  - id: BR3.1
    statement: 'Retirada el 2026-10-25: no hay catálogo del semillero (ADR-009).'
    category: policy
    applies_to: 'ninguna'
    trigger: no aplica
    logic: 'GET /api/admin/catalogo da 404 (BR1.1)'
    violation: no aplica
    source: 'ADR-009'
  - id: BR3.2
    statement: 'Retirada el 2026-10-25: la lista de colegios la carga el docente (BR4.2).'
    category: policy
    applies_to: 'ninguna'
    trigger: no aplica
    logic: 'POST /api/admin/catalogo da 404 (BR1.1)'
    violation: no aplica
    source: 'ADR-009'
  - id: BR4.1
    statement: 'Retirada el 2026-10-25: no hay colegios por sala ni provisionales.'
    category: policy
    applies_to: 'ninguna'
    trigger: no aplica
    logic: 'accion provisional o elegir da 400 «Acción no válida.» (BR4.2)'
    violation: no aplica
    source: 'ADR-009'
  - id: BR4.2
    statement: 'El docente agrega colegios a la lista, uno o varios a la vez, en inscripcion o abierto; si uno no sirve no se agrega ninguno.'
    category: validation
    applies_to: 'POST /api/admin/colegios con accion agregar'
    trigger: el docente pega la lista o agrega un colegio que falta
    logic: 'IF accion no es agregar, quitar ni arrancar THEN 400 «Acción no válida.»; IF estado no es inscripcion ni abierto THEN 400 «Los colegios se agregan o se quitan antes de cerrar el reto.»; preparado = preparar_colegios({nombres o nombre, existentes: colegios}); IF error THEN 400 con su mensaje (y existente {id_colegio, nombre} si es repetido); en una transaccion, por cada nombre: id_colegio = «c» + 8 del ALFABETO al azar (se repite si choca), arranque null, creado ahora; responde {ok, agregados: [{id_colegio, nombre}]}; un colegio agregado con el reto abierto nace sin arrancar'
    violation: 400 con el mensaje
    source: 'ADR-009, FR10.3, D3 del contrato, contrato «Lista de colegios y relojes»'
  - id: BR4.3
    statement: 'Un colegio se quita solo en inscripcion o abierto y solo si no tiene equipos.'
    category: validation
    applies_to: 'POST /api/admin/colegios con accion quitar'
    trigger: el docente quita un colegio
    logic: 'IF id_colegio no existe THEN 404 «No existe ese colegio.»; IF estado no es inscripcion ni abierto THEN 400 «Los colegios se agregan o se quitan antes de cerrar el reto.»; IF tiene algun participante (en cualquier estado) THEN 400 «Ese colegio ya tiene equipos inscritos; no se puede quitar.»; DELETE del colegio; responde {ok}'
    violation: '400 o 404'
    source: 'ADR-009, contrato «Lista de colegios y relojes»'
  - id: BR4.4
    statement: 'Arrancar el reloj de un colegio pone su arranque en la hora del servidor, una sola vez y solo con el reto abierto.'
    category: calculation
    applies_to: 'POST /api/admin/colegios con accion arrancar'
    trigger: el docente confirma «Arrancar reloj» de un colegio
    logic: 'IF id_colegio no existe THEN 404 «No existe ese colegio.»; decision = puede_arrancar_colegio(reto.estado, colegio.arranque); IF !ok THEN 400 con el mensaje («Abre el reto antes de arrancar un colegio.» o «Ese colegio ya arrancó.»); UPDATE colegios SET arranque = ahora WHERE id_colegio = ? AND arranque IS NULL en una transaccion; responde {ok, arranque}; se registra el arranque con el id_colegio, sin nombres; la confirmacion doble es del panel'
    violation: '400 o 404'
    source: 'FR3.1, FR11.5, ADR-011, BR4.5 de U4'
  - id: BR4.5
    statement: 'La lista de colegios con su reloj sale igual en el panel y en el resumen, y sin equipos ni datos personales en el tablero.'
    category: calculation
    applies_to: 'GET /api/admin/colegios, colegios[] de /api/admin/resumen, colegios[] de /api/publico, GET /api/colegios'
    trigger: cada lectura
    logic: 'panel y resumen: [{id_colegio, nombre, arranque, equipos, reloj: estado_reloj(arranque, duracion, ahora)}] ordenados por nombre sin tildes ni mayusculas, con equipos = participantes del colegio no descalificados; publico: [{id_colegio, nombre, arranque, restante_seg}] con restante_seg de estado_reloj; GET /api/colegios: [{id_colegio, nombre}] ordenados por nombre, sin parametros'
    violation: no aplica
    source: 'FR11.5, D10 del contrato, contrato (tabla de rutas)'
  - id: BR5.1
    statement: 'La inscripcion limpia y valida con LimpiezaEntrada, compara el codigo con el del reto, revisa el repetido por id de colegio y guarda los integrantes normalizados.'
    category: validation
    applies_to: 'POST /api/registro'
    trigger: un estudiante se inscribe
    logic: 'IF !admite_inscripciones(reto.estado) THEN 400 «Las inscripciones están cerradas.»; IF normalizar_texto(sala, 10) en mayusculas != reto.codigo THEN 400 «El código de sala no es correcto. Míralo en el tablero.»; campos = normalizar_texto por campo e integrantes = normalizar_integrantes; errores = validar_inscripcion(campos, ids de colegios); IF errores THEN 400 con el primero; repetido: lower(nombre) + id_colegio + grado (indice unico) da 400 «Ya hay alguien inscrito con ese nombre en ese colegio y grado. …» con el texto de hoy; grupo A/B, codigo, token y semilla como U1 BR3.3 y BR3.4; la inscripcion vale tambien con el reto abierto y el colegio sin arrancar; toda la peticion corre dentro del bloqueo del objeto'
    violation: 400 con el mensaje de hoy
    source: 'FR1.3, FR10.1, FR10.2, FR10.3, FR10.4, FR11.1, FR11.2, registrar() de servidor.py'
  - id: BR5.2
    statement: 'Eliminar borra al participante y sus eventos solo si esta en registrado o no_inicio.'
    category: policy
    applies_to: 'POST /api/admin/participante con accion eliminar'
    trigger: el docente elimina una inscripción
    logic: 'IF estado no es registrado ni no_inicio THEN 400 «Acción no válida para este participante.»; en una transaccion DELETE eventos y respuestas del participante (no deberia haber) y el participante'
    violation: '400; 404 «Participante no encontrado.» si el id no existe'
    source: 'ADR-007, accion_participante() de servidor.py'
  - id: BR6.1
    statement: 'Responder acepta los 10 tipos con las calculadoras de U4 y guarda la respuesta con ids del banco.'
    category: calculation
    applies_to: 'POST /api/responder'
    trigger: el estudiante responde
    logic: 'comprobaciones de U1 BR5.1 en el mismo orden; traducida = traducir_respuesta(semilla, cuerpo, respuesta); IF null THEN 400 «Respuesta incompleta o con formato no válido.»; revisada = validar_respuesta(cuerpo, traducida); IF error THEN el mismo 400; fraccion y puntos como hoy; INSERT y recalcular_puntos en una transaccion; con retro responde puntos, max y fraccion redondeados'
    violation: 400 con el mensaje de hoy
    source: 'FR2.1, FR2.4, FR6.2, BR1.1 y BR2.1 de U4'
  - id: BR6.2
    statement: 'Las acciones del docente sobre un participante siguen las reglas de hoy.'
    category: policy
    applies_to: 'POST /api/admin/participante'
    trigger: el docente pulsa Entregar, Anular, Reactivar o Eliminar
    logic: 'participante por id, si no 404 «Participante no encontrado.»; descalificar: estado = descalificado y motivo_fin = «descalificado (antes: <estado>)» en cualquier estado; reactivar: solo desde descalificado, vuelve al estado anterior del motivo o a finalizado; finalizar: cerrar(participante, ahora, docente) si esta en_curso (si no, ok sin cambio, como hoy); eliminar: BR5.2; otra cosa 400 «Acción no válida para este participante.»; cada accion en una transaccion'
    violation: 400 o 404
    source: 'FR1.2, ADR-007, accion_participante() de servidor.py'
  - id: BR6.3
    statement: 'Antes de cada peticion se entrega lo vencido de cada colegio y lo pendiente del cierre.'
    category: calculation
    applies_to: 'toda petición'
    trigger: antes de responder cualquier ruta
    logic: 'para cada participante en_curso (indice de estado): entrega = hora_de_entrega(ahora, inicio, duracion, reto.cerrado_en); IF entrega THEN cerrar(participante, entrega.hora, entrega.motivo); como inicio es el arranque de su colegio, cada colegio vence a su hora; ya no se une con salas'
    violation: no aplica
    source: 'FR3.1, FR3.2, FR3.3, ADR-004, contrato «Qué cambia respecto al corte»'
  - id: BR6.4
    statement: 'Comenzar exige el colegio arrancado y pone inicio igual al arranque del colegio.'
    category: calculation
    applies_to: 'POST /api/comenzar'
    trigger: el estudiante pulsa «Comenzar»
    logic: 'decision = puede_comenzar(reto.estado, participante.estado, colegio.arranque, duracion, ahora); sin_cambio: ok; rechazo: 400 con el mensaje («El reto todavía no ha empezado. Espera la señal del docente.», «Tu colegio todavía no ha empezado. Espera la señal del docente.» o «El tiempo del reto ya terminó.»); comenzar: UPDATE estado = en_curso, inicio = decision.inicio'
    violation: 400 con el mensaje
    source: 'FR3.1, FR11.3, BR4.6 de U4, contrato (/api/comenzar)'
  - id: BR6.5
    statement: '/api/estado agrega el reloj del colegio del estudiante sin revelar nada mas.'
    category: policy
    applies_to: 'GET /api/estado'
    trigger: el estudiante refresca su pantalla
    logic: 'como U1 y con ids opacos de los 10 tipos; participante.colegio = nombre del colegio; participante.colegio_arranque = arranque o null; participante.colegio_restante_seg = estado_reloj(...).restante_seg; restante_seg del intento con inicio = arranque; reto.reloj_global = true fijo (D1); puesto, puesto_grado, nota y revision los agrega U6 solo en resultados con el participante finalizado'
    violation: no aplica
    source: 'FR3.1, FR11.3, NFR8, D1 y D2 del contrato'
  - id: BR7.1
    statement: 'El resumen del panel trae lo mismo que hoy, mas la lista de colegios con su reloj y el puesto en el grado.'
    category: policy
    applies_to: 'GET /api/admin/resumen'
    trigger: el panel refresca cada 3 s
    logic: 'config = {estado, sala (reto.codigo), modo_sorpresa «1»/«0», retro «1»/«0», duracion_min como texto, evento, abierto_en, cerrado_en, reloj_global «1» fijo} (admin.js compara con «1», D1); urls = [origen de la peticion]; banco = {version, preguntas, puntos_totales, bono_max}; participantes = filas ordenadas por id con id, codigo, nombre, colegio (nombre), id_colegio, grado, integrantes, grupo, estado, respondidas, total_preguntas visibles, puntos, bono y total con redondear(x, 2), tiempo_usado, tiempo_respuestas, restante_seg (con inicio = arranque), salidas, puesto, puesto_grado y nota de puesto_de, motivo_fin; colegios = BR4.5; experimento = calcular completo, porque va con clave; servidor_ahora; el panel ve todo sin importar el modo sorpresa'
    violation: no aplica
    source: 'FR4.1, FR2.5, FR11.5, resumen_admin() de servidor.py, contrato «Resumen del panel», ADR-W11'
  - id: BR7.2
    statement: 'GET /api/publico sin parametros es el tablero y el chequeo de salud; U5 entrega todo menos clasificacion y experimento.'
    category: policy
    applies_to: 'GET /api/publico'
    trigger: el tablero sondea y el hosting revisa la salud
    logic: 'responde 200 con evento, titulo, estado, sala (reto.codigo), urls, duracion_min, abierto_en, cerrado_en, servidor_ahora, modo_sorpresa, reloj_global true fijo, conteo {inscritos (sin descalificados), en_curso, finalizados} y colegios[] (BR4.5); ?sala= se ignora; ya no responde {ok: true} solo; ranking, por_grado y experimento los agrega U6 (ADR-W11)'
    violation: no aplica
    source: 'FR11.4, contrato «Reglas comunes» (chequeo de salud), publico() de servidor.py'
  - id: BR8.1
    statement: 'El esquema se migra al arrancar con user_version y una lista ordenada; nunca se edita una migracion ya publicada.'
    category: constraint
    applies_to: arranque del objeto
    trigger: cada arranque
    logic: 'leer PRAGMA user_version; IF 0 THEN version 1 (ESQUEMA de U1, IF NOT EXISTS); version 2 = apartar las tablas del corte a v1_*, borrar sus dos indices y crear reto (con su fila unica), colegios, participantes, respuestas y eventos nuevos (ADR-W19); cada version en una transaccion que termina escribiendo user_version; si una migracion falla, el objeto registra el error y no atiende (500, como BR1.6)'
    violation: 'el servicio responde 500 «Error interno del servidor.» hasta que se corrija'
    source: 'NFR4, ADR-W10, ADR-W19'
  - id: BR9.1
    statement: 'Ninguna llamada de las pantallas de la copia de web/ queda sin ruta: al cerrar U5, cada llamada de su parte responde con la forma del contrato.'
    category: validation
    applies_to: 'despliegues/cloudflare/web/ (estudiante.js, admin.js, tablero.html)'
    trigger: antes del push de U5
    logic: 'la tabla «Pantallas completas» de ../../u6-cloudflare-resultados/functional-design/functional-spec.md lista cada llamada fetch o api(...) de la copia de web/ con su ruta, su unidad y su comprobacion; las filas de U5 tienen que pasar contra wrangler dev al cerrar U5; las de U6 pueden dar 404 hasta U6; U6 cierra la tabla (criterio del humano del 2026-10-26)'
    violation: 'U5 no se da por hecha'
    source: 'criterio de aceptación del humano (2026-10-26): «que ya todos los paneles funcionen, el dash, el de admin y el de los estudiantes»; FR4.1, FR4.2'
```

## Resumen

| Grupo | Reglas vigentes | Qué cubre |
|---|---|---|
| BR1 | BR1.1, BR1.3–BR1.6 | Acceso: tres niveles, clave docente en tiempo constante, sin `?clave=`, clave corta no arranca |
| BR2 | BR2.2, BR2.3, BR2.5 | Reto: configurar, estados con sus efectos, sin cierre automático |
| BR4 | BR4.2–BR4.5 | Colegios y relojes: agregar, quitar, arrancar, listar |
| BR5 | BR5.1, BR5.2 | Inscripción completa y eliminar |
| BR6 | BR6.1–BR6.5 | Examen: 10 tipos, acciones del docente, entrega por colegio, comenzar, reloj del estudiante |
| BR7 | BR7.1, BR7.2 | Resumen del panel y tablero sin clasificación |
| BR8 | BR8.1 | Migraciones del esquema |
| BR9 | BR9.1 | Pantallas sin llamadas huérfanas |
