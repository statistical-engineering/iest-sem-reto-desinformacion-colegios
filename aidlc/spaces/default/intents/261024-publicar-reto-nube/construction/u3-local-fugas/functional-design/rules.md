# Reglas — U3 `u3-local-fugas`

Las reglas de la corrección de fugas en `2_Aplicacion_Reto/servidor.py`. Salen de `requirements.md`
(FR6.1, FR6.2, FR6.3), de ADR-006 (`domain-design/decisions.md`), de `unit-of-work.md` (U3) y de los ADR
de esta unidad (`../decisions.md`, ADR-L1 a ADR-L3). Decisiones tomadas por el asistente con la potestad
que dio el humano (2026-10-25).

```yaml
rules:
  - id: BR1.1
    statement: 'El id opaco de un id del banco es «o» más los primeros 11 caracteres base32 en minúsculas de HMAC-SHA256 con clave la semilla del participante y mensaje ambito|id.'
    category: calculation
    applies_to: 'opaco_de(semilla, ambito, id)'
    trigger: 'al armar la salida y al traducir la entrada'
    logic: 'hmac.new(semilla.encode(), f"{ambito}|{id}".encode(), hashlib.sha256).digest() → base64.b32encode → minúsculas → [:11]; prefijo «o»; mismo id y misma semilla dan siempre el mismo valor; otra semilla da otro valor'
    violation: no aplica
    source: 'FR6.2, ADR-006, ADR-L1'
  - id: BR1.2
    statement: 'Dentro de un grupo de ids del mismo ámbito, si dos valores de 11 caracteres coinciden, todo el grupo usa 16.'
    category: calculation
    applies_to: 'opacos_de(semilla, ambito, ids)'
    trigger: 'cada grupo de opciones, ítems, publicaciones, partes u opciones de una parte'
    logic: 'IF len(set(cortos)) < len(ids) THEN valores de 16 caracteres (los primeros 16 del mismo base32) ELSE 11; devuelve el mapa id del banco → opaco'
    violation: no aplica
    source: 'BR6.1 de U1 (misma forma ^o[a-z2-7]{11}([a-z2-7]{5})?$ que reconoce la prueba común)'
  - id: BR1.3
    statement: 'El ámbito de cada lista es fijo: opciones por pregunta; ítems y publicaciones de la misión 1 comparten m1_posts; partes por pregunta|partes; opciones de una parte por pregunta|parte.'
    category: policy
    applies_to: 'opacar_salida, opacar_respuesta, traducir_entrada'
    trigger: 'cada pregunta'
    logic: 'ambito_items(pregunta_id) = «m1_posts» si empieza con «m1_», si no pregunta_id; igual que la clave de rng_para de hoy para que la misma publicación tenga el mismo id opaco en las tres preguntas de la misión 1'
    violation: no aplica
    source: 'servidor.py (version_publica, clave m1_posts), ADR-L1'
  - id: BR2.1
    statement: 'La versión pública de cada pregunta sale con ids opacos en opciones, items, publicaciones, partes y las opciones de cada parte; todo lo demás queda como hoy.'
    category: policy
    applies_to: 'version_publica'
    trigger: 'GET /api/estado con misiones'
    logic: 'después de armar pub como hoy (lista blanca de claves y orden de rng_para), opacar_salida(pub, semilla, pregunta_id) reemplaza cada id de las cuatro listas con opacos_de; categorias no cambia; el orden de cada lista no cambia; el id de la pregunta no cambia'
    violation: no aplica
    source: 'FR6.2, ADR-L1'
  - id: BR2.2
    statement: 'Las respuestas guardadas y la revisión salen con ids opacos, con la misma función y los mismos ámbitos.'
    category: policy
    applies_to: 'estado_participante'
    trigger: 'GET /api/estado'
    logic: 'respuestas[qid].respuesta = opacar_respuesta(respuesta guardada, semilla, cuerpo resuelto); en resultados revision[qid].respuesta = opacar_respuesta(c.get("respuesta"), ...); None queda None; estudiante.js compara esos valores con los ids opacos que recibió (C-02)'
    violation: no aplica
    source: 'FR6.2, contrato C-02, ADR-L1'
  - id: BR2.3
    statement: 'La traducción de una respuesta sigue la forma de su tipo: opcion texto; multiple lista; clasificar, compartir y recordatorio claves del mapa; ordenar lista; construir claves y valores del mapa; estimar, numero y texto no cambian.'
    category: calculation
    applies_to: 'opacar_respuesta y traducir_entrada'
    trigger: 'cada respuesta que entra o sale'
    logic: 'una tabla tipo → función; opcion: mapa[opciones]; multiple: lista con mapa[opciones]; clasificar/compartir/recordatorio: claves con mapa[items o publicaciones], valores (categorías) iguales; ordenar: lista con mapa[items]; construir: claves con mapa[partes] y cada valor con mapa[opciones de esa parte]; estimar, numero, texto: sin cambio'
    violation: no aplica
    source: 'api-documentation.md («forma de cada tipo»), FR6.2'
  - id: BR3.1
    statement: 'A la entrada, un id opaco conocido se traduce al id del banco y cualquier otro valor pasa igual; validar_respuesta decide después, como hoy.'
    category: validation
    applies_to: 'responder'
    trigger: 'POST /api/responder'
    logic: 'r = traducir_entrada(d.get("respuesta"), semilla, cuerpo); luego validar_respuesta(cuerpo, r) y fraccion como hoy; un id opaco inventado no está en el mapa, pasa igual y validar_respuesta lo rechaza con 400 «Respuesta incompleta o con formato no válido.»; un id del banco pasa igual y sigue válido (simulacro.py, FR6.3); una respuesta que no es str, list ni dict pasa igual'
    violation: '400 con el mensaje de hoy'
    source: 'ADR-L1 (entrada tolerante), FR12.1, FR6.3'
  - id: BR3.2
    statement: 'La base, los CSV y la calificación siguen con ids del banco: nada cambia después de traducir.'
    category: constraint
    applies_to: 'responder, csv_respuestas, csv_resultados, experimento'
    trigger: 'cada respuesta guardada'
    logic: 'INSERT INTO respuestas con r traducido (ids del banco); fraccion(cuerpo, r) como hoy; experimento() lee las respuestas de la base con ids del banco; respuestas.csv no cambia'
    violation: no aplica
    source: 'FR6.2, FR4.3, FR9.2'
  - id: BR4.1
    statement: 'En «cerrado», /api/publico entrega del experimento solo n y listo; en «resultados», el experimento completo; en los demás estados, nada, como hoy.'
    category: policy
    applies_to: 'publico'
    trigger: 'GET /api/publico'
    logic: 'IF estado == "cerrado" THEN experimento = sin_veredicto(experimento()) = {"n": ..., "listo": ...}; IF estado == "resultados" THEN experimento() completo; ELSE sin la clave experimento'
    violation: no aplica
    source: 'FR6.1, ADR-L2'
  - id: BR4.2
    statement: 'El resumen del docente no cambia: experimento completo en cualquier estado, con clave.'
    category: policy
    applies_to: 'resumen_admin'
    trigger: 'GET /api/admin/resumen'
    logic: 'sin cambios; va con X-Clave-Admin'
    violation: no aplica
    source: 'FR6.1 (solo nombra /api/publico), api-documentation.md'
  - id: BR5.1
    statement: 'Nada visible cambia: mismas pantallas, mismos textos, mismo orden de opciones, mismos puntos, mismos desempates y mismo flujo de estados.'
    category: constraint
    applies_to: 'toda la unidad'
    trigger: 'cada cambio en servidor.py'
    logic: 'el diff toca solo opaco_de, opacos_de, opacar_salida, opacar_respuesta, traducir_entrada, sin_veredicto (nuevas), el final de version_publica, dos líneas de estado_participante, una de responder y una de publico; simulacro.py 40 termina en «TODO BIEN» sin cambios y la prueba común en modo local pasa la parte base y la de fugas'
    violation: 'la unidad no se da por hecha'
    source: 'project.md («Forbidden»), unit-of-work.md (U3, notas), FR6.3'
  - id: BR5.2
    statement: 'La corrección no se aplica con un reto en curso, y el servidor se reinicia después de actualizar.'
    category: policy
    applies_to: 'despliegue en la computadora del docente'
    trigger: 'actualizar 2_Aplicacion_Reto/'
    logic: 'el docente actualiza solo con la sala en inscripción sin participantes o en resultados; después reinicia el servidor; la función opaca es la misma durante todo un reto'
    violation: no aplica
    source: 'project.md («Forbidden», «Mandated»), ADR-006 (consecuencias)'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1–BR1.3 | Cómo se calcula un id opaco y sus ámbitos |
| BR2 | BR2.1–BR2.3 | Salida opaca: examen, respuestas guardadas y revisión |
| BR3 | BR3.1–BR3.2 | Entrada tolerante y base con ids del banco |
| BR4 | BR4.1–BR4.2 | Veredicto solo en resultados (FR6.1) |
| BR5 | BR5.1–BR5.2 | Nada visible cambia; no se aplica con un reto en curso |
