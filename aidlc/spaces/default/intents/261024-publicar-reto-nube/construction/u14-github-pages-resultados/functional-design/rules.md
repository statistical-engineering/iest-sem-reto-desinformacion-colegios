# Reglas — U14 `u14-github-pages-resultados`

Resultados y exportación de la opción GitHub Pages: vista del participante, tablero por sala, resumen
con ranking, los dos CSV de hoy, el paquete, la copia de «Reiniciar» y el borrado con copias. Salen de
`requirements.md` (FR3.2, FR4.3, FR6.1, FR9, FR11.4, FR11.6, NFR10.1), `components.md` (Resultados,
Exportacion, «Copias y borrado de una sala»), los contratos C1 y C5 y los hallazgos C-06, C-08, C-11 y
C-13. Usan Clasificacion y Experimento de U12 y las salas de U13.

```yaml
rules:
  - id: BR22.1
    statement: 'El tablero de una sala trae las claves de hoy y, antes de resultados, el experimento sin veredicto.'
    category: policy
    applies_to: 'GET /api/publico?sala='
    trigger: el tablero sondea cada 2 s
    logic: 'antes, hora de entrega de la sala (ADR-004); completa BR7.1 de U11 con ranking = ordenar(finalizados de la sala) con nombre, colegio definitivo, grado, total y puesto, y experimento = calcular(filas de la sala, estado); IF estado != resultados THEN por_publicacion[] no trae verdad ni multitud_acierta; sin ?sala= sigue siendo {ok: true}; sala inexistente → 404 «No existe esa sala.»'
    violation: 'no aplica; lo comprueba la prueba común (fuga_verdad_cerrado)'
    source: 'FR6.1, FR11.4, FR3.2, contrato C1'
  - id: BR22.2
    statement: 'La vista del participante trae la revisión solo en resultados y con ids opacos.'
    category: policy
    applies_to: 'GET /api/estado'
    trigger: el estudiante sondea
    logic: 'completa F7 de U11: IF estado de la sala es resultados y el participante está finalizado THEN revision = por pregunta {respuesta correcta, explicacion, respuesta propia} con los ids traducidos por opaco_de_respuesta; además puesto, podio y nota de ordenar; ELSE sin revision; respuestas[].respuesta siempre opaca (C-02)'
    violation: no aplica
    source: 'FR4.1, NFR8, BR9.3 de U12, hallazgo C-02'
  - id: BR22.3
    statement: 'El resumen del panel agrega el ranking y el experimento de la sala.'
    category: policy
    applies_to: 'GET /api/admin/resumen'
    trigger: el panel sondea
    logic: 'completa BR19.3 de U13 con ranking (ordenar) y experimento completo (el docente sí puede ver el veredicto, como hoy), solo de su sala'
    violation: no aplica
    source: 'FR4.1, FR11.2'
  - id: BR22.4
    statement: 'El tablero avisa cuando falta la sala o no existe.'
    category: policy
    applies_to: 'tablero/index.html'
    trigger: abrir el tablero
    logic: 'sin ?sala= muestra «Abre el tablero con el enlace de tu sala.» (ya en U11); con 404 muestra «No existe la sala <código>. Revisa el enlace.»; con 5xx muestra «Sin conexión con el servidor…» y sigue sondeando'
    violation: no aplica
    source: 'hallazgo C-08, contrato C1'
  - id: BR23.1
    statement: 'Los dos CSV de hoy salen con las mismas columnas y el mismo formato, solo de la sala de la clave.'
    category: policy
    applies_to: 'GET /api/admin/resultados.csv, GET /api/admin/respuestas.csv'
    trigger: descarga del panel
    logic: 'antes, hora de entrega; mismas columnas, separador y BOM que api-documentation.md; colegio = nombre definitivo (C-11); respuestas con ids del banco; Content-Disposition con el nombre de hoy'
    violation: 403 sin clave
    source: 'FR4.3, FR3.2, hallazgo C-11'
  - id: BR23.2
    statement: 'El paquete es un .zip con los cuatro CSV, la copia y metadatos.json, con el nombre AAAA-MM-DD_<sala>_reto.zip.'
    category: policy
    applies_to: 'GET /api/admin/paquete.zip?sala='
    trigger: descarga del panel
    logic: 'antes, hora de entrega; archivos participantes.csv, respuestas.csv, eventos.csv, colegios.csv, <copia>.db y metadatos.json (contrato C5); la fecha del nombre es la de abierta (o creada si nunca abrió) en la zona horaria de Colombia; application/zip; Content-Disposition con el nombre'
    violation: 403 sin clave
    source: 'FR9.1, FR9.5, FR11.6, contrato C5'
  - id: BR23.3
    statement: 'Los CSV del paquete van en UTF-8 con encabezado, coma como separador, sin BOM, fechas ISO 8601 con zona horaria y decimales con punto; el respuestas.csv del paquete no es el de hoy.'
    category: policy
    applies_to: 'los cuatro CSV del paquete'
    trigger: armar el paquete
    logic: 'csv.writer con delimiter «,», lineterminator «\n», encoding utf-8 sin BOM; fechas con datetime.isoformat() en America/Bogota (-05:00); participantes.csv con id, sala, nombre, id_colegio, colegio, grado, integrantes, n_integrantes, grupo, estado, creado, inicio, fin, motivo_fin, puntos, bono, total, tiempo_usado, tiempo_respuestas, salidas; respuestas.csv con participante_id, pregunta_id, variante, respuesta (JSON), fraccion, puntos, max_puntos, momento; eventos.csv con id_evento, participante_id, tipo, momento; colegios.csv con id_colegio, nombre, provisional; las columnas se describen en el diccionario de FR9.3'
    violation: no aplica
    source: 'FR9.2, hallazgo C-13'
  - id: BR23.4
    statement: 'metadatos.json dice de qué reto, banco y versión salió el paquete.'
    category: policy
    applies_to: 'metadatos.json'
    trigger: armar el paquete
    logic: 'inicio, fin, sala, evento, duracion_min, participantes, version_banco (huella sha256 de src/banco.json), version_app (src/version.txt), opcion = «github_pages»'
    violation: no aplica
    source: 'FR9.1'
  - id: BR23.5
    statement: 'La copia de una sala es un reto.db con el mismo esquema y solo sus filas, sin token, semilla, codigo personal ni clave_huella.'
    category: policy
    applies_to: 'CopiaDeSala (reiniciar y paquete)'
    trigger: reiniciar o pedir el paquete
    logic: 'se crea un archivo SQLite temporal, se le aplica el esquema, se ATTACH y se hace INSERT … SELECT … WHERE sala = ? para salas, sala_colegios, colegios (solo los de la sala), participantes (con token, semilla y codigo vacíos), respuestas y eventos; salas se copia con clave_huella vacía; nunca VACUUM INTO de la base entera (R-05); el archivo se lee a bytes y se borra'
    violation: 'no aplica; la prueba común abre la copia y confirma que esas columnas están vacías (C-06)'
    source: 'FR4.3, FR9.1, FR9.5, ADR-005, ADR-G5, hallazgo C-06'
  - id: BR23.6
    statement: 'El diccionario de datos describe cada archivo y cada columna del paquete, sin datos de participantes.'
    category: policy
    applies_to: '4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md'
    trigger: cada cambio de columnas
    logic: 'una sección por archivo del paquete con tabla columna, tipo, unidades, valores posibles y de dónde sale; cambiar una columna obliga a cambiar el diccionario en el mismo push (contrato C5); es un .md en español con el formato de .claude/rules/markdown-docs.md'
    violation: 'el push no sale'
    source: 'FR9.3, contrato C5'
  - id: BR24.1
    statement: 'Reiniciar guarda la copia y después vacía la sala, como una sola operación; conserva la sala, su clave, sus colegios y sus copias.'
    category: policy
    applies_to: 'POST /api/admin/reiniciar?sala='
    trigger: el docente reinicia con BORRAR
    logic: 'IF confirmar != «BORRAR» THEN 400; en una transacción: copia = CopiaDeSala (BR23.5) insertada en copias; DELETE respuestas, eventos y participantes de la sala; abierta y cerrada a NULL; estado = inscripcion; responde {ok: true, copia: id_copia} (contrato C1)'
    violation: '400'
    source: 'FR1.1, FR11.6, R-17, contrato C1'
  - id: BR24.2
    statement: 'El docente lista y descarga las copias de su sala.'
    category: policy
    applies_to: 'GET /api/admin/copias?sala=, GET /api/admin/copia?sala=&id='
    trigger: desde el panel
    logic: 'copias → {copias: [{id_copia, creada, nombre_archivo}]} de esa sala; copia → el blob con application/vnd.sqlite3 y Content-Disposition con nombre_archivo; una copia de otra sala → 404'
    violation: '404'
    source: 'R-17, contrato C1'
  - id: BR24.3
    statement: 'Borrar la sala borra también sus copias; al final no queda ninguna fila de esa sala.'
    category: policy
    applies_to: 'POST /api/admin/salas/borrar?sala='
    trigger: guía de cierre
    logic: 'completa BR16.6 de U13 con DELETE FROM copias WHERE sala = ?; después del borrado, una consulta de comprobación por tabla devuelve 0 filas para esa sala'
    violation: no aplica
    source: 'NFR10.1, FR8.2'
  - id: BR25.1
    statement: 'Las descargas desde el panel de Pages exponen el nombre del archivo al navegador.'
    category: policy
    applies_to: 'CSV, paquete y copia'
    trigger: descarga con fetch desde otro dominio
    logic: 'la respuesta lleva Access-Control-Expose-Headers: Content-Disposition además de las cabeceras CORS de BR8.1; admin.js lee el nombre de esa cabecera y, si falta, usa el nombre de hoy'
    violation: 'el navegador descarga con el nombre de hoy'
    source: 'ADR-G4, contrato C1 (hallazgo C-04)'
  - id: BR25.2
    statement: 'El panel muestra la copia de «Reiniciar» como una fila descargable, no como una ruta de carpeta.'
    category: policy
    applies_to: 'admin/index.html, static/js/admin.js'
    trigger: después de reiniciar
    logic: 'el texto «Copia de seguridad: datos/…» de hoy pasa a «Copia guardada: <nombre_archivo> (descárgala en la lista de copias)»; la lista de copias tiene un botón por fila y el botón del paquete .zip'
    violation: no aplica
    source: 'hallazgo C-08, R-17, FR9.1'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR22 | BR22.1–BR22.4 | Tablero por sala, vista del participante, resumen, mensajes del tablero |
| BR23 | BR23.1–BR23.6 | CSV de hoy, paquete, formato, metadatos, copia, diccionario |
| BR24 | BR24.1–BR24.3 | Reiniciar, copias, borrar con copias |
| BR25 | BR25.1–BR25.2 | Lo propio de dos dominios en las descargas y el panel |
