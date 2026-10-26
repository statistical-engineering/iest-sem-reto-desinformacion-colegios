# Reglas — U12 `u12-github-pages-reglas`

Las «calculadoras» de ADR-001 para la opción GitHub Pages, con la forma del contrato C4. Reemplazan la
versión mínima de Banco, Calificacion y CicloDeSala que trajo el corte (U11, BR4.3, BR5.2, BR6.1, BR2.2)
y agregan Clasificacion, LimpiezaEntrada y Experimento. Ninguna lee la base ni el reloj: la hora llega
como argumento (ADR-004). Dan exactamente los mismos puntos, orden y vencimientos que `servidor.py`
(NFR11, FR5.5): las nueve funciones que ya son puras en `servidor.py` (`fraccion`, `validar_respuesta`,
`version_publica`, `examen_publico`, `variante_de`, `resolver`, `rng_para`, `a_numero`, `puesto_de`) se
copian a `reglas.py` sin cambiar su lógica, porque la versión local está congelada y copiar no es
depender (FR12.1, FR12.2). Las seis mezcladas se separan de su SQL y de la hora.

```yaml
rules:
  - id: BR9.1
    statement: 'validar_banco devuelve la lista de errores de un banco: debe sumar 1.000 puntos, no repetir ids y traer versión.'
    category: validation
    applies_to: 'Banco.validar_banco(banco)'
    trigger: al arrancar la API y en las pruebas
    logic: 'errores = []; IF suma de puntos != 1000 THEN agrega «suma <n>, no 1.000»; IF hay ids repetidos de misión o pregunta THEN agrega cada uno; IF falta version THEN agrega «sin versión»; devuelve errores (vacía si está bien)'
    violation: 'la API no arranca si la lista no está vacía (BR6.3 de U11)'
    source: 'project.md («Mandated», 1.000 puntos), contrato C4'
  - id: BR9.2
    statement: 'examen_publico arma las misiones que ve un participante: su variante, sus preguntas visibles, ids opacos en orden barajado y sin ninguna clave secreta.'
    category: policy
    applies_to: 'Banco.examen_publico(banco, semilla, grupo, respondidas)'
    trigger: GET /api/estado
    logic: 'para cada misión y pregunta: variante = variante_de(semilla, pregunta); IF solo_grupo existe y no es el grupo THEN se omite; se copia solo la lista blanca de claves de version_publica de hoy (nunca respuesta, explicacion, tolerancia, verdad ni multitud_acierta); opciones, items y partes salen con opaco_de y ordenados por el id opaco; el dossier sale bloqueado hasta que revelar_tras esté en respondidas'
    violation: 'no aplica; lo comprueban la prueba común (fugas) y los casos de C4'
    source: 'FR6.2, NFR8, ADR-006, BR6.1 y BR6.2 de U11'
  - id: BR9.3
    statement: 'opaco_de y traducir_opaco son inversas para una misma semilla y pregunta; opaco_de_respuesta traduce una respuesta guardada (ids del banco) a la forma que ve el navegador.'
    category: calculation
    applies_to: 'Banco.opaco_de(semilla, pregunta_id, id), Banco.traducir_opaco(banco, semilla, pregunta_id, respuesta_opaca), Banco.opaco_de_respuesta(banco, semilla, pregunta_id, respuesta)'
    trigger: al armar el examen, al recibir una respuesta y al devolver respuestas y revision
    logic: 'opaco = «o» + primeros 11 caracteres base32 minúsculas de HMAC-SHA256(semilla, pregunta_id + «|» + id); IF dos ids de la misma pregunta chocan THEN 16 caracteres para esa pregunta; traducir_opaco busca el id del banco cuyo opaco coincide y devuelve la respuesta con ids del banco (listas y pares incluidos); IF algún opaco no corresponde THEN devuelve None; opaco_de_respuesta hace lo contrario campo a campo'
    violation: 'None → 400 «Respuesta incompleta o con formato no válido.» en Examen'
    source: 'FR6.2, ADR-006, ADR-G6, hallazgos C-02 y C-05'
  - id: BR10.1
    statement: 'validar_respuesta normaliza la forma de una respuesta según el tipo de pregunta y rechaza lo que no cabe.'
    category: validation
    applies_to: 'Calificacion.validar_respuesta(pregunta_resuelta, respuesta)'
    trigger: POST /api/responder
    logic: 'copia de validar_respuesta de servidor.py: por tipo exige id de la lista, lista de ids sin repetir, número dentro de min y max (entero si entero), orden completo, pares válidos, escala en rango, partes completas o texto no vacío; devuelve la respuesta normalizada o error'
    violation: '400 «Respuesta incompleta o con formato no válido.»'
    source: 'FR2.1, FR2.4, contrato C4'
  - id: BR10.2
    statement: 'fraccion da el crédito parcial de los 10 tipos con la misma regla que hoy.'
    category: calculation
    applies_to: 'Calificacion.fraccion(pregunta_resuelta, respuesta_normalizada)'
    trigger: POST /api/responder
    logic: 'copia de fraccion de servidor.py; número entre 0 y 1; puntos = fraccion x puntos de la pregunta; IF la pregunta no tiene puntos THEN 0'
    violation: no aplica
    source: 'FR2.1, NFR11'
  - id: BR10.3
    statement: 'bono = 20 × (puntos / 1.000) × (1 − tiempo_respuestas / duración), nunca negativo.'
    category: calculation
    applies_to: 'Calificacion.bono(puntos, t_ultima_seg, duracion_seg)'
    trigger: al entregar
    logic: 'IF duracion_seg <= 0 THEN 0; t = min(max(t_ultima_seg, 0), duracion_seg); bono = 20 * (puntos / 1000) * (1 - t / duracion_seg); mismo redondeo que hoy'
    violation: no aplica
    source: FR2.2
  - id: BR11.1
    statement: 'ordenar devuelve los participantes finalizados de una sala en orden total, sin empates, con puesto y nota.'
    category: calculation
    applies_to: 'Clasificacion.ordenar(participantes_finalizados)'
    trigger: tablero, resumen y CSV
    logic: 'clave de orden: total desc y puntos desc (los dos redondeados a 9 decimales), tiempo_respuestas asc, fin asc, id asc; excluye descalificados del ranking como hoy; puesto = posición desde 1; nota = Clasificacion.nota(total)'
    violation: 'no aplica; una prueba exige que no haya dos puestos iguales'
    source: 'FR2.3, NFR11, components.md (Clasificacion)'
  - id: BR11.2
    statement: 'nota da la nota sobre 5 con la fórmula de hoy; podio y top10 salen de ordenar.'
    category: calculation
    applies_to: 'Clasificacion.nota(total), Clasificacion.podio(orden), Clasificacion.top10(orden)'
    trigger: tablero y vista del participante
    logic: 'copia de la fórmula de servidor.py; podio = 3 primeros; top10 = 10 primeros; puesto_de(id, orden) devuelve el puesto del participante'
    violation: no aplica
    source: 'FR2.3, contrato C4 (hallazgo C-05)'
  - id: BR12.1
    statement: 'transicion_permitida solo acepta los cambios de estado de la sala que ofrece el panel.'
    category: constraint
    applies_to: 'CicloDeSala.transicion_permitida(estado_actual, estado_nuevo)'
    trigger: POST /api/admin/estado
    logic: 'tabla cerrada tomada de los botones de admin.js al construir: inscripcion→abierto, abierto→cerrado, cerrado→resultados, cerrado→abierto (reabrir, si el panel lo ofrece) y resultados→cerrado (si lo ofrece); mismo estado → permitido sin cambio; resultados→abierto nunca (hallazgo S5); «Reiniciar» no es una transición: es la acción de U14'
    violation: '400 «Ese cambio de estado no está permitido.»'
    source: 'FR7.4, FR1.1'
  - id: BR12.2
    statement: 'hora_de_entrega dice si un intento en curso ya venció y con qué hora y motivo.'
    category: calculation
    applies_to: 'CicloDeSala.hora_de_entrega(ahora, inicio, duracion_seg, cierre)'
    trigger: antes de cualquier operación sobre una sala (ADR-004)
    logic: 'vencimiento = inicio + duracion_seg; candidatos = [vencimiento] + [cierre si no es None]; hora = min(candidatos); IF ahora < hora THEN None; ELSE {hora, motivo: tiempo si hora == vencimiento y (cierre es None o vencimiento <= cierre), si no cierre}'
    violation: no aplica
    source: 'FR3.1, FR3.2, ADR-004'
  - id: BR12.3
    statement: 'estado_participante y admite_inscripciones aplican las reglas de estado de hoy.'
    category: constraint
    applies_to: 'CicloDeSala.estado_participante(estado_sala, participante, ahora), CicloDeSala.admite_inscripciones(estado_sala)'
    trigger: inscripción, cierre de sala y vistas
    logic: 'admite_inscripciones = estado en {inscripcion, abierto}; al cerrar la sala, registrado → no_inicio y en_curso → finalizado con motivo cierre; descalificado y finalizado no cambian; reactivar vuelve a en_curso solo desde descalificado, como hoy'
    violation: no aplica
    source: 'FR1.2, ADR-004, ADR-007'
  - id: BR13.1
    statement: 'normalizar_texto deja el texto como lo escribió la persona, pero limpio: NFC, sin caracteres de control ni invisibles, con un solo espacio entre palabras y recortado al largo.'
    category: validation
    applies_to: 'LimpiezaEntrada.normalizar_texto(texto, largo)'
    trigger: antes de validar y guardar cualquier texto del navegador
    logic: 'IF no es texto THEN «»; unicodedata.normalize(«NFC»); quita los caracteres de categoría Cc y Cf (control y formato, incluido el ancho cero) y los espacios raros de categoría Zs distintos del espacio; junta espacios repetidos; strip; recorta a largo (60 nombre, 200 integrantes, 80 colegio y evento); no cambia mayúsculas ni tildes'
    violation: no aplica
    source: 'FR10.2'
  - id: BR13.2
    statement: 'validar_inscripcion aplica en el servidor todas las reglas de los campos de inscripción, en el orden y con los mensajes de hoy.'
    category: validation
    applies_to: 'LimpiezaEntrada.validar_inscripcion(campos, ids_colegios_de_la_sala)'
    trigger: POST /api/registro
    logic: 'nombre normalizado con al menos 3 caracteres, si no «Escribe tu nombre (o el del equipo).»; grado en {9, 10, 11}, si no «Elige el grado: 9, 10 u 11.»; colegio obligatorio y dentro de la lista, si no «Elige tu colegio de la lista.»; integrantes con normalizar_integrantes; devuelve los campos limpios o el primer error'
    violation: '400 con el mensaje'
    source: 'FR10.1, FR10.3'
  - id: BR13.3
    statement: 'normalizar_integrantes separa por comas, limpia cada nombre, quita los vacíos y los une con «, »; n_integrantes es cuántos quedaron.'
    category: calculation
    applies_to: 'LimpiezaEntrada.normalizar_integrantes(texto)'
    trigger: POST /api/registro
    logic: 'partes = texto.split(«,»); cada una con normalizar_texto(parte, 60); sin vacías; devuelve (unidos con «, » recortado a 200, cantidad)'
    violation: no aplica
    source: FR10.4
  - id: BR13.4
    statement: 'nombre_normalizado_colegio es la forma con la que se detectan duplicados del catálogo.'
    category: calculation
    applies_to: 'LimpiezaEntrada.nombre_normalizado_colegio(nombre)'
    trigger: alta de colegios y provisionales
    logic: 'normalizar_texto(nombre, 80) → NFD → quitar marcas diacríticas (categoría Mn) → minúsculas (casefold) → dejar solo letras, dígitos y espacios → juntar espacios → strip; «IE San José» y «ie san jose» dan lo mismo; no se quitan palabras como «colegio» para no unir colegios distintos'
    violation: no aplica
    source: 'FR10.3, ADR-002'
  - id: BR14.1
    statement: 'calcular arma el experimento A/B de una sala igual que hoy y, antes de resultados, sin veredicto.'
    category: policy
    applies_to: 'Experimento.calcular(participantes, respuestas, estado_sala)'
    trigger: GET /api/publico?sala=
    logic: 'copia de la lógica de experimento de servidor.py sobre las filas de una sola sala; excluye descalificados; IF estado_sala != resultados THEN por_publicacion[] sale sin verdad ni multitud_acierta; ELSE completo'
    violation: 'no aplica; lo comprueba la prueba común (fuga_verdad_cerrado)'
    source: 'FR6.1, FR11.2'
  - id: BR15.1
    statement: 'Cada regla pasa todos los casos de casos_reglas.json y, además, un caso válido y al menos dos inválidos escritos en la prueba.'
    category: policy
    applies_to: 'pruebas/test_reglas.py'
    trigger: antes de cada push
    logic: 'test_reglas.py carga pruebas/casos_reglas.json (copia de despliegues/prueba_comun/casos_reglas.json) y genera una prueba por fila con subTest; los casos de Calificacion usan un banco de prueba propio incluido en el JSON, nunca el banco real; la cobertura de reglas.py con trace es ≥ 80 % de líneas'
    violation: 'el push no sale'
    source: 'FR7.1, FR10.5, NFR12, contrato C4'
```

## Resumen

| Grupo | Reglas | Regla de C4 |
|---|---|---|
| BR9 | BR9.1–BR9.3 | Banco |
| BR10 | BR10.1–BR10.3 | Calificacion |
| BR11 | BR11.1–BR11.2 | Clasificacion |
| BR12 | BR12.1–BR12.3 | CicloDeSala |
| BR13 | BR13.1–BR13.4 | LimpiezaEntrada |
| BR14 | BR14.1 | Experimento |
| BR15 | BR15.1 | Cómo se prueban |
