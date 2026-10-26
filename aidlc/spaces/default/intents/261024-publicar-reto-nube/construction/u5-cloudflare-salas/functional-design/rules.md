# Reglas — U5 `u5-cloudflare-salas`

Las reglas de Salas, Acceso, CatalogoColegios, Inscripcion y Examen completos. Salen de `requirements.md`
(FR1, FR2.4, FR3, FR7.2, FR7.4, FR10, FR11), de `components.md`, del contrato (`contract-summary.md`,
C1) y de `servidor.py`. Las reglas de U1 (`../../u1-cloudflare-corte/functional-design/rules.md`) siguen
vigentes; aquí van las que U5 agrega o completa, con ids propios. Las calculadoras son las de U4.
Decisiones en `../decisions.md` (ADR-W10 a ADR-W13).

```yaml
rules:
  - id: BR1.1
    statement: 'La tabla de rutas crece con las rutas del panel y cada una declara su nivel; lo que no esta sigue dando 404.'
    category: authorization
    applies_to: 'todas las rutas (tabla en functional-spec.md, «Rutas de U5»)'
    trigger: cada petición
    logic: 'niveles publico, token, clave (sala o semillero), sala (clave de sala, o del semillero con ?sala=), semillero; como U1 BR1.1 a BR1.3'
    violation: '401, 403, 404 o 400 «Falta la sala.»'
    source: 'FR7.2, FR11.5'
  - id: BR1.2
    statement: 'Regenerar la clave de una sala reemplaza su huella; la clave anterior deja de servir al instante y la nueva se muestra una sola vez.'
    category: policy
    applies_to: 'POST /api/admin/salas/clave'
    trigger: el semillero regenera
    logic: 'IF la clave no es la del semillero THEN 403; secreto nuevo de 16 caracteres del ALFABETO; UPDATE salas SET clave_huella; responde {sala, clave}; no se registra'
    violation: 403
    source: 'ADR-003, FR11.5'
  - id: BR1.3
    statement: 'Una clave incorrecta responde 403 tras la misma espera corta que un codigo inexistente; no hay bloqueo por intentos.'
    category: policy
    applies_to: 'rutas con clave'
    trigger: clave ausente, incorrecta o de otra sala
    logic: 'esperar_ms = 600 fuera del bloqueo del objeto, como entrar; sin contador de intentos (ADR-W12)'
    violation: '403 «Clave de docente incorrecta.» o «Esa clave no es de esta sala.»'
    source: 'NFR9, OQ6, ADR-W12'
  - id: BR2.1
    statement: 'El semillero lista todas las salas sin claves ni huellas.'
    category: policy
    applies_to: 'GET /api/admin/salas'
    trigger: el semillero abre su panel
    logic: '{salas: [{sala, estado, evento, creada, abierta, cerrada, inscritos}]} ordenadas por creada desc; inscritos = participantes no descalificados'
    violation: 403 con clave de sala
    source: 'contrato C1, FR11.5'
  - id: BR2.2
    statement: 'Configurar la sala sigue las reglas de hoy, salvo que el codigo no se cambia.'
    category: validation
    applies_to: 'POST /api/admin/config'
    trigger: el docente guarda un campo
    logic: 'modo_sorpresa y retro en cualquier estado; evento limpio a 80 y «Reto» si queda vacio; IF sala en el cuerpo THEN 400 «El código de sala no se puede cambiar.»; reloj_global y duracion_min solo en inscripcion, si no 400 «El tipo de reloj solo se cambia antes de abrir el reto.» o «La duración solo se cambia antes de abrir el reto.»; duracion_min = max(10, min(240, entero)); todo en una transaccion sin cruzarse con otra operacion de la sala'
    violation: 400 con el mensaje de hoy
    source: 'FR11.1, R-12, contrato C1 (/api/admin/config), review-05 (configurar solo antes de abrir)'
  - id: BR2.3
    statement: 'Cambiar el estado aplica transicion_permitida y, al cerrar, entrega y marca no_inicio con la hora del cierre.'
    category: calculation
    applies_to: 'POST /api/admin/estado'
    trigger: el docente o el semillero cambia el estado
    logic: 'IF estado no valido THEN 400 «Estado no válido.»; IF igual al actual THEN ok; IF !transicion_permitida THEN 400 «Ese cambio de estado no está permitido.»; abierto: abierta = COALESCE(abierta, ahora); cerrado: cerrada = COALESCE(cerrada, ahora), cada en_curso se cierra con cerrar(participante, ahora, cierre) y cada registrado pasa a no_inicio (estado_tras_cierre); resultados: nada mas que el estado; todo en una transaccion; se registra el cambio sin datos'
    violation: 400 con el motivo
    source: 'FR1.1, FR1.2, FR7.4, ADR-004, cambiar_estado() de servidor.py'
  - id: BR2.4
    statement: 'Borrar la sala es del semillero, solo con la sala cerrada o en resultados y escribiendo BORRAR; borra todo lo de esa sala y nada de otra.'
    category: policy
    applies_to: 'POST /api/admin/salas/borrar'
    trigger: el semillero cierra el reto
    logic: 'IF clave no es del semillero THEN 403; IF confirmar != BORRAR THEN 400 «Escribe BORRAR para confirmar.»; IF estado no es cerrado ni resultados THEN 400 «Cierra la sala antes de borrarla.»; en una transaccion: DELETE eventos y respuestas de sus participantes, participantes, sala_colegios y la sala (U6 agrega copias); los colegios del catalogo quedan'
    violation: 400 o 403
    source: 'NFR10.1, FR11.6, review-05 (Borrar solo con la sala cerrada)'
  - id: BR2.5
    statement: 'La sala no se cierra sola y no hay tope de salas en el codigo.'
    category: policy
    applies_to: Salas
    trigger: vencimiento del reloj global
    logic: 'cada intento vence por hora_de_entrega; la sala sigue abierta hasta que el docente la cierre, como hoy; la guia recomienda hasta 10 salas abiertas a la vez'
    violation: no aplica
    source: 'OQ8, ADR-W12, FR1.1'
  - id: BR3.1
    statement: 'El catalogo se lee con clave de sala o del semillero y nunca trae mas que id, nombre, provisional y unido_a.'
    category: policy
    applies_to: 'GET /api/admin/catalogo'
    trigger: el panel arma la lista para elegir
    logic: '{colegios: [Colegio]} ordenados por nombre sin mayusculas; incluye provisionales y unidos'
    violation: 403 sin clave
    source: 'ADR-002, contrato C1'
  - id: BR3.2
    statement: 'Solo el semillero mantiene el catalogo: agregar, corregir, confirmar y unir, sin nombres repetidos.'
    category: validation
    applies_to: 'POST /api/admin/catalogo'
    trigger: el semillero edita el catálogo
    logic: 'accion agregar: nombre limpio >= 3, normalizado unico, crea con provisional = 0; corregir: cambia nombre y normalizado de id_colegio, unico; confirmar: provisional = 0 en un provisional; unir: id_colegio provisional y unir_a un colegio existente ni provisional ni unido, pone unido_a y provisional = 0; IF el nombre normalizado ya existe THEN 400 «Ese colegio ya existe.» con la clave existente; IF accion desconocida THEN 400 «Acción no válida.»; cada accion en una transaccion'
    violation: '400 con el motivo; 403 con clave de sala'
    source: 'ADR-002, FR10.3, ADR-W13'
  - id: BR4.1
    statement: 'El docente elige y quita colegios del catalogo para su sala solo en inscripcion; el provisional vale en cualquier estado.'
    category: validation
    applies_to: 'POST /api/admin/colegios y GET /api/admin/colegios'
    trigger: el docente arma la lista de su sala
    logic: 'elegir: IF estado != inscripcion THEN 400 «Los colegios de la sala solo se eligen antes de abrir el reto.»; IF id_colegio no existe o esta unido THEN 400 «Ese colegio no está en el catálogo.»; INSERT OR IGNORE en sala_colegios; quitar: misma condicion de estado, IF ya hay un inscrito de ese colegio en la sala THEN 400 «Ya hay inscritos de ese colegio.», DELETE; provisional: como U1 BR2.3; GET: {elegidos: [Colegio]} con el nombre definitivo'
    violation: 400 con el motivo
    source: 'FR10.3, ADR-002, review-05'
  - id: BR5.1
    statement: 'La inscripcion limpia y valida con LimpiezaEntrada, revisa el repetido por id de colegio y guarda los integrantes normalizados.'
    category: validation
    applies_to: 'POST /api/registro'
    trigger: un estudiante se inscribe
    logic: 'sala por codigo (U1 BR3.1); IF !admite_inscripciones THEN 400 «Las inscripciones están cerradas.»; campos = normalizar_texto por campo e integrantes = normalizar_integrantes; errores = validar_inscripcion(campos, ids de sala_colegios); IF errores THEN 400 con el primero; repetido: lower(nombre) + id_colegio + grado en la sala (indice unico de U1); grupo, codigo, token y semilla como U1 BR3.3 y BR3.4; sin cruzarse: toda la peticion corre dentro del bloqueo del objeto'
    violation: 400 con el mensaje de hoy
    source: 'FR1.3, FR10.1, FR10.2, FR10.3, FR10.4, FR11.2'
  - id: BR5.2
    statement: 'Eliminar borra al participante y sus eventos solo si esta en registrado o no_inicio.'
    category: policy
    applies_to: 'POST /api/admin/participante con accion eliminar'
    trigger: el docente elimina una inscripción
    logic: 'IF estado no es registrado ni no_inicio THEN 400 «Acción no válida para este participante.»; en una transaccion DELETE eventos y respuestas del participante (no deberia haber) y el participante; el participante tiene que ser de la sala de la clave'
    violation: '400; 404 «Participante no encontrado.» si el id no es de esa sala'
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
    statement: 'Las acciones del docente sobre un participante siguen las reglas de hoy y solo sobre su sala.'
    category: policy
    applies_to: 'POST /api/admin/participante'
    trigger: el docente pulsa Entregar, Anular, Reactivar o Eliminar
    logic: 'participante = por id y por la sala de la clave, si no 404; descalificar: estado = descalificado y motivo_fin = «descalificado (antes: <estado>)» en cualquier estado; reactivar: solo desde descalificado, vuelve al estado anterior del motivo o a finalizado; finalizar: cerrar(participante, ahora, docente) si esta en_curso; eliminar: BR5.2; otra cosa 400 «Acción no válida para este participante.»; cada accion en una transaccion'
    violation: 400 o 404
    source: 'FR1.2, ADR-007, accion_participante() de servidor.py'
  - id: BR6.3
    statement: 'La entrega por tiempo y por cierre se aplica antes de cada peticion con la hora de cierre de la sala.'
    category: calculation
    applies_to: 'toda petición'
    trigger: antes de responder cualquier ruta
    logic: 'como U1 BR4.2, pero hora_de_entrega recibe sala.cerrada en vez de null; recorre solo los en_curso (indice de estado)'
    violation: no aplica
    source: 'FR3.2, FR3.3, ADR-004'
  - id: BR7.1
    statement: 'El resumen del panel trae lo mismo que hoy, de una sola sala, con config como texto.'
    category: policy
    applies_to: 'GET /api/admin/resumen'
    trigger: el panel refresca cada 3 s
    logic: 'config = {estado, sala, modo_sorpresa «1»/«0», retro «1»/«0», duracion_min como texto, evento, abierto_en, cerrado_en, reloj_global «1»/«0»} (admin.js compara con «1»); urls = [origen de la peticion]; banco = {version, preguntas, puntos_totales, bono_max}; participantes = filas de la sala ordenadas por id con respondidas, total_preguntas visibles, puntos, bono, total redondeados a 2, restante_seg, puesto y nota de ordenar(finalizados), colegio definitivo; experimento = calcular(banco, filas de la sala) completo, porque va con clave; servidor_ahora'
    violation: no aplica
    source: 'FR4.1, FR11.2, resumen_admin() de servidor.py, ADR-W11'
  - id: BR8.1
    statement: 'El esquema se migra al arrancar con user_version y una lista ordenada; nunca se edita una migracion ya publicada.'
    category: constraint
    applies_to: arranque del objeto
    trigger: cada arranque
    logic: 'leer PRAGMA user_version; para cada migracion con version mayor, en orden y en una transaccion, correr su SQL y escribir user_version; version 2 = ALTER TABLE colegios ADD COLUMN unido_a y la vista colegios_definitivos; si una migracion falla, el objeto registra el error y no atiende (como el error de arranque de U1)'
    violation: 'el servicio responde 500 con «Error interno» hasta que se corrija'
    source: 'NFR4, ADR-W10'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.3 | Acceso: tabla completa, regenerar clave, sin bloqueo por intentos |
| BR2 | BR2.1–BR2.5 | Salas: listar, configurar, estados completos, borrar, sin cierre automático |
| BR3 | BR3.1–BR3.2 | Catálogo único del semillero |
| BR4 | BR4.1 | Colegios de la sala |
| BR5 | BR5.1–BR5.2 | Inscripción completa y eliminar |
| BR6 | BR6.1–BR6.3 | Examen: 10 tipos, acciones del docente, entrega por cierre |
| BR7 | BR7.1 | Resumen del panel (ADR-W11) |
| BR8 | BR8.1 | Migraciones del esquema |
