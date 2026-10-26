# Reglas — U13 `u13-github-pages-salas`

Salas, claves, catálogo, inscripción y examen completos en la opción GitHub Pages. Completan BR2 y BR3
de U11 y usan las «calculadoras» de U12 (BR12, BR13). Salen de `requirements.md` (FR1, FR7.4, FR10,
FR11), `components.md` (Salas, CatalogoColegios, Acceso, Inscripcion, Examen), `decisions.md` de Domain
Design (ADR-002, ADR-003, ADR-004, ADR-007), el contrato C1 y las dos reglas que dejó la revisión 05 de
Domain Design (configurar solo antes de abrir; borrar solo cerrada y con BORRAR). «Sin cruzarse» es el
candado del proceso más `BEGIN IMMEDIATE` (ADR-G5).

```yaml
rules:
  - id: BR16.1
    statement: 'El semillero regenera la clave de una sala; la anterior deja de servir en ese momento.'
    category: policy
    applies_to: 'POST /api/admin/salas/clave?sala='
    trigger: el semillero pide otra clave
    logic: 'IF la clave no es la del semillero THEN 403; ELSE nuevo secreto de 16 caracteres del ALFABETO, nueva huella guardada en la misma transacción y respuesta {sala, clave} una sola vez'
    violation: 403
    source: 'ADR-003, FR11.5'
  - id: BR16.2
    statement: 'La sala se configura solo en «inscripción» y sin cruzarse con otra operación de la sala; el código no se cambia.'
    category: constraint
    applies_to: 'POST /api/admin/config'
    trigger: el docente guarda la configuración
    logic: 'IF el cuerpo trae sala THEN 400 «El código de sala no se puede cambiar.»; IF estado != inscripcion y cambian duracion_min o reloj_global THEN 400 «La duración y el reloj solo se cambian antes de abrir.»; evento, retro y modo_sorpresa se cambian como hoy; duracion_min entre 10 y 240; todo dentro de la misma transacción que revisa el estado'
    violation: '400 con el motivo'
    source: 'R-12, revisión 05 de Domain Design, contrato C1 (/api/admin/config)'
  - id: BR16.3
    statement: 'Cerrar la sala entrega a quien sigue en curso con la hora del cierre y pasa a no_inicio a quien nunca empezó.'
    category: calculation
    applies_to: 'POST /api/admin/estado con estado cerrado'
    trigger: el docente o el semillero cierra
    logic: 'IF transicion_permitida(actual, cerrado) THEN cerrada = ahora; para cada participante en_curso: entregar con hora_de_entrega(ahora, inicio, duracion, cerrada) (motivo tiempo o cierre, idempotente, BR4.3); registrado → no_inicio; todo en una transacción (ADR-004, R-09)'
    violation: '400 «Ese cambio de estado no está permitido.» si la transición no está en la tabla'
    source: 'FR1.1, FR7.4, ADR-004, BR12.1 y BR12.3 de U12'
  - id: BR16.4
    statement: 'Las demás transiciones (abrir, publicar y las que ofrezca el panel) pasan por la misma tabla; publicar no cambia datos, solo el estado.'
    category: constraint
    applies_to: 'POST /api/admin/estado'
    trigger: cambio de estado
    logic: 'IF nuevo == actual THEN ok sin cambio; IF not transicion_permitida THEN 400; abierto fija abierta si no estaba; resultados solo desde cerrado; resultados → abierto nunca (S5)'
    violation: '400'
    source: 'FR7.4, FR1.1 (reemplaza BR2.2 de U11)'
  - id: BR16.5
    statement: 'El semillero lista las salas sin ver claves ni huellas.'
    category: policy
    applies_to: 'GET /api/admin/salas'
    trigger: el semillero abre su panel
    logic: 'IF clave != semillero THEN 403; ELSE {salas: [{sala, estado, evento, creada, abierta, cerrada, inscritos}]}'
    violation: 403
    source: 'FR11.5, contrato C1'
  - id: BR16.6
    statement: 'Borrar una sala es solo del semillero, solo con la sala en cerrado o resultados y escribiendo BORRAR.'
    category: constraint
    applies_to: 'POST /api/admin/salas/borrar?sala='
    trigger: el semillero cierra el reto (guía de cierre)
    logic: 'IF clave != semillero THEN 403; IF estado not in {cerrado, resultados} THEN 400 «Cierra la sala antes de borrarla.»; IF confirmar != «BORRAR» THEN 400 «Escribe BORRAR para confirmar.»; borra en bloque participantes, respuestas, eventos, sala_colegios y la sala; las copias las agrega U14; nunca toca otra sala'
    violation: '403 o 400'
    source: 'NFR10.1, FR11.6, revisión 05 de Domain Design'
  - id: BR17.1
    statement: 'El semillero agrega y corrige colegios del catálogo; un nombre normalizado que ya existe se rechaza y se devuelve el existente.'
    category: validation
    applies_to: 'POST /api/admin/catalogo con accion agregar o corregir'
    trigger: mantenimiento del catálogo
    logic: 'IF clave != semillero THEN 403; nombre = normalizar_texto(nombre, 80), al menos 3 caracteres; IF nombre_normalizado_colegio(nombre) ya existe en otro colegio THEN 400 {error, existente: Colegio}; agregar crea con provisional = false; corregir cambia nombre y nombre_normalizado del id_colegio dado'
    violation: '400 con «existente»'
    source: 'FR10.3, ADR-002, contrato C1'
  - id: BR17.2
    statement: 'El semillero confirma un provisional o lo une con uno existente; desde entonces el definitivo es el destino.'
    category: policy
    applies_to: 'POST /api/admin/catalogo con accion confirmar o unir'
    trigger: después del reto
    logic: 'confirmar: provisional = false; unir: unido_a = unir_a (que no puede ser provisional ni estar unido), provisional = false; los participantes conservan su id_colegio y toda vista y exportación resuelven el definitivo siguiendo unido_a (una sola vez: no hay cadenas)'
    violation: '400 si unir_a no existe o también es provisional'
    source: 'ADR-002, FR9.2'
  - id: BR17.3
    statement: 'GET /api/admin/catalogo devuelve todo el catálogo a cualquier clave de administración.'
    category: policy
    applies_to: 'GET /api/admin/catalogo'
    trigger: el docente elige colegios
    logic: '{colegios: [{id_colegio, nombre, provisional}]}, sin los unidos (se muestran por su definitivo)'
    violation: 403 sin clave
    source: 'ADR-002, contrato C1'
  - id: BR17.4
    statement: 'El docente elige y quita colegios de su sala solo en «inscripción»; agrega provisionales también el día del reto.'
    category: constraint
    applies_to: 'POST /api/admin/colegios?sala= con accion elegir, quitar o provisional'
    trigger: el docente arma la lista de su sala
    logic: 'elegir y quitar: IF estado != inscripcion THEN 400 «Los colegios de la sala solo se cambian antes de abrir.»; quitar: IF algún participante de la sala tiene ese id_colegio THEN 400; provisional: en inscripcion o abierto, crea el colegio provisional (BR2.3 de U11) y lo agrega a la sala; un nombre existente devuelve 400 con «existente» y no lo agrega solo'
    violation: '400 con el motivo'
    source: 'FR10.3, ADR-002, contrato C1'
  - id: BR17.5
    statement: 'En toda respuesta y en los dos CSV de hoy, «colegio» es el nombre definitivo del catálogo; el id solo viaja en /api/registro, /api/colegios y el paquete.'
    category: policy
    applies_to: '/api/estado, /api/publico, /api/admin/resumen, CSV'
    trigger: cada lectura
    logic: 'colegio = nombre del colegio definitivo (siguiendo unido_a); /api/colegios?sala= devuelve {id_colegio, nombre} de los elegidos de la sala, resolviendo unidos a su definitivo sin repetir'
    violation: no aplica
    source: 'FR10.3, R-18, hallazgo C-11'
  - id: BR18.1
    statement: 'La inscripción valida todo en el servidor con las reglas de U12 y guarda los integrantes normalizados y contados.'
    category: validation
    applies_to: 'POST /api/registro'
    trigger: un estudiante se inscribe
    logic: 'reemplaza BR3.1 de U11: campos = validar_inscripcion(cuerpo, ids de sala_colegios resueltos); IF error THEN 400 con su mensaje; integrantes, n_integrantes = normalizar_integrantes; repetido por (sala, nombre normalizado, id_colegio, grado) → 400 de hoy; lo demás como BR3.2 a BR3.4'
    violation: '400 con el mensaje de hoy'
    source: 'FR10.1, FR10.2, FR10.3, FR10.4'
  - id: BR18.2
    statement: 'Eliminar a un participante solo vale en registrado o no_inicio y borra también sus eventos.'
    category: constraint
    applies_to: 'POST /api/admin/participante con accion eliminar'
    trigger: el docente limpia la lista
    logic: 'IF estado not in {registrado, no_inicio} THEN 400 «Solo se puede eliminar a quien no ha empezado.»; DELETE eventos y participante en una transacción; nunca toca otra sala'
    violation: '400'
    source: 'ADR-007, FR1.2'
  - id: BR19.1
    statement: 'Responder acepta los 10 tipos de pregunta con la calificación de U12.'
    category: calculation
    applies_to: 'POST /api/responder'
    trigger: el estudiante responde
    logic: 'reemplaza BR5.2 de U11: pregunta = resolver(pregunta, variante_de(semilla, pregunta)); respuesta = traducir_opaco (None → 400); validar_respuesta (error → 400); fraccion; puntos = fraccion × puntos; se guarda con ids del banco y se suma a participante.puntos en la misma transacción'
    violation: '400 «Respuesta incompleta o con formato no válido.»'
    source: 'FR2.1, FR2.4, BR10.1 y BR10.2 de U12'
  - id: BR19.2
    statement: 'El docente finaliza, descalifica o reactiva a un participante con las reglas de hoy, sin cruzarse.'
    category: constraint
    applies_to: 'POST /api/admin/participante con accion finalizar, descalificar o reactivar'
    trigger: acción del docente
    logic: 'antes, hora de entrega de la sala (ADR-004); finalizar: solo en_curso, entrega con motivo docente (BR4.3); descalificar: desde registrado o en_curso, estado descalificado y fin = ahora; reactivar: solo desde descalificado, vuelve a en_curso (o registrado si nunca empezó); otra combinación → 400 con el mensaje de hoy; una transacción por acción'
    violation: '400'
    source: 'FR1.2, ADR-007, BR12.3 de U12'
  - id: BR19.3
    statement: 'El resumen del panel trae lo que el panel de hoy necesita para funcionar, solo de su sala.'
    category: policy
    applies_to: 'GET /api/admin/resumen'
    trigger: el panel sondea cada 3 s
    logic: 'antes, hora de entrega; {estado, sala, evento, duracion_min, reloj_global, retro, modo_sorpresa, abierto_en, cerrado_en, servidor_ahora, participantes: [{id, codigo, nombre, colegio (definitivo), grado, integrantes, grupo, estado, puntos, bono, total, salidas, inicio, fin}]}, con las claves de hoy; ranking y experimento los agrega U14'
    violation: 403 sin clave
    source: 'FR4.1, FR11.5'
  - id: BR20.1
    statement: 'Con la clave del semillero, toda ruta de sala exige ?sala=; el panel lo agrega solo cuando entra con rol semillero.'
    category: authorization
    applies_to: '/api/admin/* de una sala'
    trigger: el semillero usa el panel de una sala
    logic: 'la API aplica BR1.3 de U11; admin.js guarda rol y, con rol semillero, su helper api() agrega ?sala=<sala elegida> a cada llamada de sala; cerrar o abrir una sala desde el semillero es POST /api/admin/estado?sala='
    violation: '400 «Falta la sala.»'
    source: 'FR11.5, hallazgo C-07'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR16 | BR16.1–BR16.6 | Salas: regenerar clave, configurar, cerrar, transiciones, listar, borrar |
| BR17 | BR17.1–BR17.5 | Catálogo único, colegios de la sala, nombre definitivo |
| BR18 | BR18.1–BR18.2 | Inscripción completa y eliminar |
| BR19 | BR19.1–BR19.3 | Examen completo, acciones del docente, resumen |
| BR20 | BR20.1 | El semillero en el panel de una sala |

BR16.4 reemplaza a BR2.2 de U11, BR18.1 a BR3.1 y BR19.1 a BR5.2. Las copias y el borrado con copias
los completa U14.
