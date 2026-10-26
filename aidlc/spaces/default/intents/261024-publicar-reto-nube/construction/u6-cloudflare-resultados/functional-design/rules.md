# Reglas — U6 `u6-cloudflare-resultados`

Las reglas de Resultados y Exportacion. Salen de `requirements.md` (FR1.1, FR4.3, FR6.1, FR6.2, FR9,
FR11.4, FR11.6, NFR10.1), de `components.md` («Copias y borrado de una sala»), del contrato
(`contract-summary.md`, C1 y C5) y de `servidor.py` (`publico`, `estado_participante`, `csv_resultados`,
`csv_respuestas`, `reiniciar`). Las de U1, U4 y U5 siguen vigentes. Decisiones en `../decisions.md`
(ADR-W14 a ADR-W18).

```yaml
rules:
  - id: BR1.1
    statement: 'Con la sala en resultados, el participante finalizado recibe puesto, nota y revision con ids opacos; antes, nada de eso.'
    category: policy
    applies_to: 'GET /api/estado'
    trigger: cada consulta del estudiante
    logic: 'IF sala.estado es resultados AND participante.estado es finalizado THEN puesto = puesto_de(id, finalizados de la sala), nota = nota(puntos), revision = revision_publica(banco, semilla, grupo); ELSE las tres claves no existen en la respuesta'
    violation: 'la comprobacion de fugas de la prueba comun falla'
    source: 'FR6.2, NFR8, estado_participante() de servidor.py, C-02'
  - id: BR2.1
    statement: 'El tablero trae el ranking (top 10) solo en resultados o con el modo sorpresa apagado.'
    category: policy
    applies_to: 'GET /api/publico?sala='
    trigger: sondeo del tablero cada 2 s
    logic: 'IF estado es resultados OR !modo_sorpresa THEN ranking = las 10 primeras filas de ordenar(finalizados de la sala) con puesto, nombre, colegio (definitivo), grado, total, puntos; ELSE sin la clave ranking'
    violation: no aplica
    source: 'FR11.4, publico() de servidor.py'
  - id: BR2.2
    statement: 'El tablero trae el experimento solo en cerrado y resultados, y en cerrado reducido a n y listo.'
    category: policy
    applies_to: 'GET /api/publico?sala='
    trigger: sondeo del tablero
    logic: 'IF estado es cerrado o resultados THEN experimento = experimento_publico(calcular(banco, filas de la sala), estado); ELSE sin la clave'
    violation: 'la comprobacion fuga_verdad_cerrado de la prueba comun falla'
    source: 'FR6.1, ADR-W9, BR6.2 de U4'
  - id: BR3.1
    statement: 'resultados.csv sale byte a byte como hoy para los mismos datos: separador punto y coma, BOM, CRLF, decimales con coma a 4 cifras y una columna por pregunta.'
    category: policy
    applies_to: 'GET /api/admin/resultados.csv'
    trigger: descarga del panel
    logic: 'cabecera de csv_resultados() de servidor.py; filas de la sala ordenadas por puesto y luego id; colegio definitivo; flotantes con 4 decimales y coma, enteros tal cual, nota vacia si no esta clasificado; Content-Disposition attachment con resultados_reto.csv'
    violation: 'la comparacion con la version local en la prueba comun falla'
    source: 'FR4.3, ADR-W16, csv_resultados() de servidor.py'
  - id: BR3.2
    statement: 'respuestas.csv sale como hoy, con la respuesta serializada como json.dumps de Python.'
    category: policy
    applies_to: 'GET /api/admin/respuestas.csv'
    trigger: descarga del panel
    logic: 'cabecera de csv_respuestas(); filas de la sala ordenadas por participante y momento; respuesta = json_como_python(valor); fraccion y puntos con 4 decimales y coma; segundos_desde_inicio = round(momento - (inicio o momento)) con redondeo a par como Python; Content-Disposition respuestas_detalle.csv'
    violation: 'la comparacion con la version local falla'
    source: 'FR4.3, FR6.2 (ids del banco), ADR-W16, csv_respuestas() de servidor.py'
  - id: BR3.3
    statement: 'Todas las descargas son de nivel sala: clave de esa sala, o del semillero con ?sala=; nunca traen datos de otra sala.'
    category: authorization
    applies_to: 'GET /api/admin/resultados.csv, respuestas.csv, paquete.zip, copias, copia'
    trigger: cada descarga
    logic: 'nivel sala de la tabla de rutas (U1 BR1.3); toda consulta lleva id_sala'
    violation: '403 sin datos'
    source: 'FR9.5, FR11.6, NFR9'
  - id: BR4.1
    statement: 'El paquete se llama AAAA-MM-DD_<sala>_reto.zip y trae los cuatro CSV, la copia y metadatos.json.'
    category: policy
    applies_to: 'GET /api/admin/paquete.zip'
    trigger: descarga del panel
    logic: 'fecha = abierta o creada en hora de Colombia (ADR-W18); entradas: participantes.csv, respuestas.csv, eventos.csv, colegios.csv, copia_<sala>_<fecha>.sql, metadatos.json; zip stored con CRC-32 (ADR-W15); Content-Type application/zip y Content-Disposition con el nombre; se arma en cada descarga, no se guarda; antes de leer se aplica la entrega (vencer_tiempos, que ya corre en toda peticion)'
    violation: no aplica
    source: 'FR9.1, FR3.2, C5'
  - id: BR4.2
    statement: 'Los CSV del paquete van en UTF-8 sin BOM, separados por coma, con encabezado, fechas ISO 8601 con -05:00 y decimales con punto.'
    category: policy
    applies_to: 'los cuatro CSV del paquete'
    trigger: armar el paquete
    logic: 'columnas de entities.md («Columnas de los CSV del paquete»); comillas solo cuando el valor lleva coma, comilla o salto de linea, con la comilla doblada (RFC 4180); salto de linea LF; null como celda vacia'
    violation: no aplica
    source: 'FR9.2, C-13, ADR-W16'
  - id: BR4.3
    statement: 'metadatos.json lleva inicio, fin, sala, evento, duracion, numero de participantes, huella del banco, version de la app, version del esquema, estado y fecha de generacion.'
    category: policy
    applies_to: 'metadatos.json del paquete'
    trigger: armar el paquete
    logic: 'forma de Metadatos en entities.md; version_banco = {version: banco.version, sha256: huella de copiar.sh}; version_app = src/version.json'
    violation: no aplica
    source: 'FR9.1, FR9.2'
  - id: BR4.4
    statement: 'Ni el paquete ni la copia llevan token, semilla, codigo personal ni clave_huella, y la prueba lo comprueba abriendo los archivos.'
    category: policy
    applies_to: 'paquete.zip y CopiaDeSala'
    trigger: armar el paquete o la copia
    logic: 'las consultas de exportacion nombran columnas y nunca usan SELECT *; una prueba unitaria busca esas cuatro palabras en los encabezados de los CSV y en los CREATE TABLE del guion; la prueba comun descomprime el paquete y repite la busqueda'
    violation: 'prueba unitaria y prueba comun fallan'
    source: 'FR9.5, R-11, C-06'
  - id: BR4.5
    statement: 'En el paquete y en la copia, respuesta y pregunta_id llevan los ids del banco, y el colegio el id y el nombre definitivos.'
    category: policy
    applies_to: 'respuestas.csv, participantes.csv, colegios.csv y la copia'
    trigger: armar el paquete o la copia
    logic: 'respuesta = JSON compacto de la base (ids del banco); colegio y id_definitivo con la vista colegios_definitivos (ADR-W13); colegios.csv lista los colegios ofrecidos por la sala mas los de sus participantes'
    violation: no aplica
    source: 'FR9.2, FR6.2, FR10.3'
  - id: BR5.1
    statement: 'La copia de una sala es un guion SQL con las tablas sin columnas secretas y solo las filas de esa sala.'
    category: policy
    applies_to: 'Exportacion: armar_copia'
    trigger: reiniciar y paquete
    logic: 'cabecera comentada con sala, evento, fecha, version_banco y version_app; CREATE TABLE de salas (sin clave_huella), colegios, sala_colegios, participantes (sin codigo, token, semilla), respuestas y eventos; INSERT por fila con comillas simples dobladas y numeros con punto; termina con un comentario con el numero de filas por tabla'
    violation: no aplica
    source: 'FR4.3, R-05, R-11, ADR-W14'
  - id: BR5.2
    statement: 'Reiniciar pide BORRAR y, como una sola operacion, guarda la copia y despues vacia la sala sin tocar sus copias, su clave ni sus colegios.'
    category: policy
    applies_to: 'POST /api/admin/reiniciar'
    trigger: el docente reinicia
    logic: 'IF confirmar != BORRAR THEN 400 «Escribe BORRAR para confirmar.»; en una transaccion: contenido = armar_copia(sala); INSERT en copias y copia_trozos; DELETE eventos, respuestas y participantes de la sala; UPDATE salas SET estado = inscripcion, abierta = NULL, cerrada = NULL; responde {ok, copia: id_copia}; registra «Sala <codigo> reiniciada»'
    violation: 400
    source: 'FR1.1, FR11.6, R-17, reiniciar() de servidor.py, contrato C1'
  - id: BR5.3
    statement: 'El contenido de una copia se guarda en trozos de 512 KiB y se devuelve entero con su huella comprobada.'
    category: constraint
    applies_to: 'copias y copia_trozos'
    trigger: guardar y descargar una copia
    logic: 'trozos de 524.288 bytes numerados desde 0; al descargar se concatenan por n y se comprueba sha256; IF no coincide THEN 500 y registro «copia dañada <id_copia>»'
    violation: 500
    source: 'ADR-W17, limite de 2 MB por fila'
  - id: BR6.1
    statement: 'El docente ve la lista de copias de su sala con id, fecha y nombre, y descarga cada una.'
    category: policy
    applies_to: 'GET /api/admin/copias y GET /api/admin/copia?id='
    trigger: el panel abre la lista
    logic: 'copias: {copias: [{id_copia, creada, nombre_archivo, bytes}]} ordenadas por creada desc; copia: IF id no es de esa sala THEN 404 «No existe esa copia en la sala.»; ELSE el guion con Content-Type application/sql; charset=utf-8 y Content-Disposition attachment'
    violation: 404
    source: 'R-17, contrato C1'
  - id: BR6.2
    statement: 'Borrar la sala borra tambien sus copias y trozos en la misma transaccion.'
    category: policy
    applies_to: 'POST /api/admin/salas/borrar'
    trigger: el semillero borra
    logic: 'se agregan DELETE copia_trozos y DELETE copias a la transaccion de U5 BR2.4; despues no queda ninguna fila con ese id_sala en ninguna tabla'
    violation: 'la prueba de conteo por id_sala falla'
    source: 'NFR10.1, FR8.2, FR11.6'
  - id: BR7.1
    statement: 'La version de la app viene de src/version.json, que escribe copiar.sh; sin ese archivo el Worker no se construye.'
    category: constraint
    applies_to: arranque y metadatos
    trigger: cada despliegue
    logic: 'copiar.sh escribe {commit: git rev-parse --short HEAD, fecha: ISO} en src/version.json (ignorado por git); reto.js lo importa; el registro de arranque incluye el commit'
    violation: 'wrangler falla al construir: no se despliega'
    source: 'FR9.1, ADR-W17'
  - id: BR8.1
    statement: 'El diccionario de datos describe cada archivo y cada columna del paquete, sin datos de participantes.'
    category: policy
    applies_to: '4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md'
    trigger: cada cambio de columna
    logic: 'una tabla por archivo con columna, tipo, unidad, valores posibles y de donde sale; incluye metadatos.json y la copia; una prueba unitaria compara los encabezados que produce csv.js con los nombres del diccionario'
    violation: 'prueba unitaria falla'
    source: 'FR9.3, C5 («cambiar una columna obliga a cambiar el diccionario en el mismo push»)'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1 | Vista del participante en resultados |
| BR2 | BR2.1–BR2.2 | Tablero completo por sala |
| BR3 | BR3.1–BR3.3 | Los dos CSV de hoy y el nivel de acceso de las descargas |
| BR4 | BR4.1–BR4.5 | Paquete `.zip` |
| BR5 | BR5.1–BR5.3 | Copia de la sala y reiniciar |
| BR6 | BR6.1–BR6.2 | Copias: listar, descargar, borrar con la sala |
| BR7 | BR7.1 | Versión de la app |
| BR8 | BR8.1 | Diccionario de datos |
