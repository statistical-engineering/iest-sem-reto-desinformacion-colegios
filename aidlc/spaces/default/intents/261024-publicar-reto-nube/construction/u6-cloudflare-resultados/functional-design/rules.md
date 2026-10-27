# Reglas — U6 `u6-cloudflare-resultados`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Las reglas valen para el único reto, con la
> clave docente (ADR-010) y sin `?sala=`. **Cambian:** BR1.1 (gana `puesto_grado`), BR2.1 (gana
> `por_grado` y `nota`), BR2.2, BR3.1 a BR3.3, BR4.1 a BR4.5, BR5.1, BR5.2 (borra también los colegios),
> BR6.1 y BR6.2 (borrar una copia, ya no una sala). **Nuevas:** BR9.1 (migración 3) y BR10.1 a BR10.3
> (pantallas completas, criterio del humano del 2026-10-26).

Las reglas de Resultados y Exportacion. Salen de `requirements.md` (FR1.1, FR2.5, FR4.3, FR6.1, FR6.2,
FR9, FR11.4, FR11.6, NFR10.1), de `components.md` («Copias y "Reiniciar"»), del contrato
(`contract-summary.md`, C1 y C5) y de `servidor.py` (`publico`, `estado_participante`, `csv_resultados`,
`csv_respuestas`, `reiniciar`). Las de U1, U4 y U5 siguen vigentes. Decisiones en `../decisions.md`
(ADR-W14 a ADR-W18 y ADR-W21).

```yaml
rules:
  - id: BR1.1
    statement: 'Con el reto en resultados, el participante finalizado recibe puesto, puesto en el grado, nota y revision con ids opacos; antes, nada de eso.'
    category: policy
    applies_to: 'GET /api/estado'
    trigger: cada consulta del estudiante
    logic: 'IF reto.estado es resultados AND participante.estado es finalizado THEN {puesto, puesto_grado, nota} = puesto_de(id, finalizados del reto) y revision = revision_publica(banco, semilla, grupo); ELSE las cuatro claves no existen en la respuesta'
    violation: 'la comprobacion de fugas de la prueba comun falla'
    source: 'FR2.5, FR6.2, NFR8, estado_participante() de servidor.py, C-02, D2 del contrato'
  - id: BR2.1
    statement: 'El tablero trae el top 10 general y el de cada grado solo en resultados o con el modo sorpresa apagado, siempre juntos.'
    category: policy
    applies_to: 'GET /api/publico'
    trigger: sondeo del tablero cada 2 s
    logic: 'IF estado es resultados OR !modo_sorpresa THEN lista = por_grado(ordenar(finalizados del reto)); ranking = las 10 primeras filas de lista con puesto, puesto_grado, nombre, colegio, grado, total, puntos y nota; por_grado = {"9", "10", "11"}: las 10 primeras de cada grado con las mismas claves; ELSE sin las claves ranking ni por_grado; el podio son los tres primeros de ranking (no hay clave podio)'
    violation: no aplica
    source: 'FR2.5, FR11.4, D4 del contrato, publico() de servidor.py'
  - id: BR2.2
    statement: 'El tablero trae el experimento solo en cerrado y resultados, y en cerrado reducido a n y listo.'
    category: policy
    applies_to: 'GET /api/publico'
    trigger: sondeo del tablero
    logic: 'e = experimento_publico(calcular(banco, filas del reto), estado); IF e no es null THEN experimento = e; ELSE sin la clave'
    violation: 'la comprobacion fuga_verdad_cerrado de la prueba comun falla'
    source: 'FR6.1, ADR-W9, BR6.2 de U4, D5 del contrato'
  - id: BR3.1
    statement: 'resultados.csv sale byte a byte como hoy para los mismos datos: separador punto y coma, BOM, CRLF, decimales con coma a 4 cifras y una columna por pregunta.'
    category: policy
    applies_to: 'GET /api/admin/resultados.csv'
    trigger: descarga del panel
    logic: 'cabecera de csv_resultados() de servidor.py; filas ordenadas por puesto y luego id; colegio = nombre de la lista; flotantes con 4 decimales y coma, enteros tal cual, nota vacia si no esta clasificado; Content-Disposition attachment con resultados_reto.csv'
    violation: 'la comparacion con la version local en la prueba comun falla'
    source: 'FR4.3, ADR-W16, csv_resultados() de servidor.py'
  - id: BR3.2
    statement: 'respuestas.csv sale como hoy, con la respuesta serializada como json.dumps de Python.'
    category: policy
    applies_to: 'GET /api/admin/respuestas.csv'
    trigger: descarga del panel
    logic: 'cabecera de csv_respuestas(); filas ordenadas por participante y momento; respuesta = json_como_python(valor); fraccion y puntos con 4 decimales y coma; segundos_desde_inicio = round(momento - (inicio o momento)) con redondeo a par como Python (redondear de U4); Content-Disposition respuestas_detalle.csv'
    violation: 'la comparacion con la version local falla'
    source: 'FR4.3, FR6.2 (ids del banco), ADR-W16, csv_respuestas() de servidor.py'
  - id: BR3.3
    statement: 'Todas las descargas y las rutas de copias son de nivel clave: solo con la clave docente en X-Clave-Admin, nunca en la URL.'
    category: authorization
    applies_to: 'GET /api/admin/resultados.csv, respuestas.csv, paquete.zip, copias, copia; POST /api/admin/reiniciar, copia/borrar'
    trigger: cada descarga
    logic: 'nivel clave de la tabla de rutas (BR1.1, BR1.4 y BR1.5 de U5); sin clave, con una incorrecta o con ?clave=, 403 «Clave de docente incorrecta.» sin datos; admin.js descarga con fetch y la cabecera, como hoy'
    violation: '403 sin datos'
    source: 'FR9.5, NFR9, ADR-010'
  - id: BR4.1
    statement: 'El paquete se llama AAAA-MM-DD_<sala>_reto.zip y trae los cuatro CSV, la copia y metadatos.json.'
    category: policy
    applies_to: 'GET /api/admin/paquete.zip'
    trigger: descarga del panel
    logic: 'fecha = abierto_en, o ahora si nunca se abrio, en hora de Colombia (ADR-W18); sala = reto.codigo; entradas: participantes.csv, respuestas.csv, eventos.csv, colegios.csv, copia_<sala>_<fecha>.sql, metadatos.json; zip stored con CRC-32 (ADR-W15); Content-Type application/zip y Content-Disposition con el nombre; se arma en cada descarga, no se guarda; antes de leer se aplica la entrega de lo vencido (U5 BR6.3, que ya corre en toda peticion)'
    violation: no aplica
    source: 'FR9.1, FR11.6, FR3.2, C5'
  - id: BR4.2
    statement: 'Los CSV del paquete van en UTF-8 sin BOM, separados por coma, con encabezado, fechas ISO 8601 con -05:00 y decimales con punto.'
    category: policy
    applies_to: 'los cuatro CSV del paquete'
    trigger: armar el paquete
    logic: 'columnas de entities.md («Columnas de los CSV del paquete»), en el orden de C5; comillas solo cuando el valor lleva coma, comilla o salto de linea, con la comilla doblada (RFC 4180); salto de linea LF; null como celda vacia'
    violation: no aplica
    source: 'FR9.2, C-13, ADR-W16'
  - id: BR4.3
    statement: 'metadatos.json lleva los campos de C5 mas la version del esquema, el estado y la fecha de generacion.'
    category: policy
    applies_to: 'metadatos.json del paquete'
    trigger: armar el paquete
    logic: 'forma de Metadatos en entities.md: inicio, fin, sala, evento, duracion_min, participantes, colegios, version_banco, huella_banco, version_app, version_esquema, estado, generado'
    violation: no aplica
    source: 'FR9.1, FR9.2, C5'
  - id: BR4.4
    statement: 'Ni el paquete ni la copia llevan token, semilla ni codigo personal, y la prueba lo comprueba abriendo los archivos.'
    category: policy
    applies_to: 'paquete.zip y Copia'
    trigger: armar el paquete o la copia
    logic: 'las consultas de exportacion nombran columnas y nunca usan SELECT *; una prueba unitaria busca token, semilla y codigo (como columna) en los encabezados de los CSV y en los CREATE TABLE del guion, y busca la clave docente de prueba en todo el zip; la prueba comun descomprime el paquete y repite la busqueda'
    violation: 'prueba unitaria y prueba comun fallan'
    source: 'FR9.5, R-11, C-06, C5 («nunca»)'
  - id: BR4.5
    statement: 'En el paquete y en la copia, respuesta y pregunta_id llevan los ids del banco, y el colegio su id y su nombre de la lista.'
    category: policy
    applies_to: 'respuestas.csv, participantes.csv, colegios.csv y la copia'
    trigger: armar el paquete o la copia
    logic: 'respuesta = JSON compacto de la base (ids del banco); colegio = nombre por JOIN con colegios; colegios.csv = todos los colegios de la lista con arranque y equipos (participantes no descalificados)'
    violation: no aplica
    source: 'FR9.2, FR6.2, FR10.3, C5'
  - id: BR5.1
    statement: 'La copia del reto es un guion SQL con las tablas sin columnas secretas y todas sus filas.'
    category: policy
    applies_to: 'Exportacion: armar_copia'
    trigger: reiniciar, paquete y migracion 3
    logic: 'cabecera comentada con codigo de sala, evento, fecha, version_banco, huella_banco y version_app; CREATE TABLE de reto, colegios, participantes (sin codigo, token ni semilla), respuestas y eventos; INSERT por fila con comillas simples dobladas y numeros con punto; termina con un comentario con el numero de filas por tabla; la misma funcion recibe la lista de tablas y columnas, asi la migracion 3 la usa con las v1_*'
    violation: no aplica
    source: 'FR4.3, R-11, ADR-W14'
  - id: BR5.2
    statement: 'Reiniciar pide BORRAR y, como una sola operacion, guarda la copia y despues vacia el reto sin tocar sus copias ni su configuracion.'
    category: policy
    applies_to: 'POST /api/admin/reiniciar'
    trigger: el docente reinicia
    logic: 'IF confirmar != BORRAR THEN 400 «Escribe BORRAR para confirmar.»; en una transaccion: contenido = armar_copia(); INSERT en copias y copia_trozos; DELETE eventos, respuestas, participantes y colegios; DELETE FROM sqlite_sequence WHERE name = participantes (los ids vuelven a empezar en 1, como hoy); UPDATE reto SET estado = inscripcion, abierto_en = NULL, cerrado_en = NULL; codigo, evento, duracion_min, retro y modo_sorpresa quedan; responde {ok, copia: id_copia}; registra «Reto reiniciado» con el id_copia y sin datos'
    violation: 400
    source: 'FR1.1, FR11.6, R-17, reiniciar() de servidor.py, components.md («Copias y "Reiniciar"»), D7 del contrato'
  - id: BR5.3
    statement: 'El contenido de una copia se guarda en trozos de 512 KiB y se devuelve entero con su huella comprobada.'
    category: constraint
    applies_to: 'copias y copia_trozos'
    trigger: guardar y descargar una copia
    logic: 'trozos de 524.288 bytes numerados desde 0; al descargar se concatenan por n y se comprueba sha256; IF no coincide THEN 500 y registro «copia dañada <id_copia>»'
    violation: 500
    source: 'ADR-W17, limite de 2 MB por fila'
  - id: BR6.1
    statement: 'El docente ve la lista de copias con id, fecha, nombre y tamaño, y descarga cada una.'
    category: policy
    applies_to: 'GET /api/admin/copias y GET /api/admin/copia?id='
    trigger: el panel abre la lista
    logic: 'copias: {copias: [{id_copia, creada, nombre_archivo, bytes}]} ordenadas por creada desc; copia: IF id no existe THEN 404 «No existe esa copia.»; ELSE el guion con Content-Type application/sql; charset=utf-8 y Content-Disposition attachment con nombre_archivo'
    violation: 404
    source: 'R-17, D7 del contrato'
  - id: BR6.2
    statement: 'Borrar una copia borra la copia y sus trozos en una transaccion; no hay otra forma de borrar copias.'
    category: policy
    applies_to: 'POST /api/admin/copia/borrar'
    trigger: el docente borra una copia ya guardada en el lugar privado del semillero
    logic: 'IF id_copia no existe THEN 404 «No existe esa copia.»; DELETE copia_trozos y copias de ese id en una transaccion; responde {ok}; registra «Copia borrada» con el id; el panel pide confirmacion antes'
    violation: 404
    source: 'NFR10.1, FR8.2, D7 del contrato'
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
    logic: 'una tabla por archivo con columna, tipo, unidad, valores posibles y de donde sale; incluye metadatos.json y la copia; advierte que id_colegio no se conserva entre retos y que los años se unen por el nombre normalizado; una prueba unitaria compara los encabezados que produce csv.js con los nombres del diccionario'
    violation: 'prueba unitaria falla'
    source: 'FR9.3, C5 («cambiar una columna obliga a cambiar el diccionario en el mismo push»)'
  - id: BR9.1
    statement: 'La version 3 del esquema crea las copias y guarda lo que aparto la migracion de U5 antes de borrarlo.'
    category: constraint
    applies_to: 'arranque del objeto (ADR-W10)'
    trigger: primer arranque con el codigo de U6
    logic: 'en una transaccion: CREATE TABLE copias y copia_trozos; IF alguna tabla v1_* tiene filas THEN contenido = armar_copia(tablas v1_* sin clave_huella, token, semilla ni codigo) guardado como migracion_v1.sql; DROP de las seis tablas v1_*; user_version = 3'
    violation: 'el objeto no atiende (500) hasta que se corrija, como BR8.1 de U5'
    source: 'NFR4, ADR-W10, ADR-W19 de U5, ADR-W14'
  - id: BR10.1
    statement: 'Ninguna pantalla de la copia de web/ llama una ruta que no exista.'
    category: validation
    applies_to: 'pruebas/pantallas.test.js'
    trigger: cada node --test
    logic: 'saca de web/static/js/*.js y web/tablero.html cada literal que empieza con /api/; cada uno tiene que estar en RUTAS de reto.js y, en cuanto exista, en contrato_api.yaml; IF una pantalla escribe ?sala= o ?clave= THEN falla'
    violation: 'node --test falla'
    source: 'criterio de aceptación del humano (2026-10-26), ADR-W21, FR4.1'
  - id: BR10.2
    statement: 'Cada llamada de las pantallas tiene su comprobacion en la prueba comun con la forma que la pantalla usa y las claves que lee.'
    category: validation
    applies_to: 'prueba común (U2), comprobaciones pantalla_*'
    trigger: cada corrida de la prueba común
    logic: 'una comprobacion por fila de la tabla «Pantallas completas» de functional-spec.md: metodo, ruta, cuerpo como lo arma la pantalla, codigo 200 y presencia de las claves JSON que lee la pantalla'
    violation: 'la prueba común no da «TODO BIEN»'
    source: 'criterio de aceptación del humano (2026-10-26), ADR-W21, FR12.3'
  - id: BR10.3
    statement: 'U6 no se da por hecha hasta que las tres pantallas se recorren completas en wrangler dev sin errores en la consola.'
    category: validation
    applies_to: 'cierre de U6'
    trigger: antes del punto de control de U6
    logic: 'una persona sigue la lista «Recorrido de las pantallas» de functional-spec.md (estudiante, panel docente y tablero), con dos colegios y un reto completo de inscripcion a resultados y Reiniciar; anota fecha, persona y resultado en code-summary.md de U6; cualquier vista que no se dibuja, boton sin efecto o error en la consola deja la unidad abierta'
    violation: 'U6 no se cierra'
    source: 'criterio de aceptación del humano (2026-10-26): «que ya todos los paneles funcionen, el dash, el de admin y el de los estudiantes»'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| BR1 | BR1.1 | Vista del participante en resultados |
| BR2 | BR2.1–BR2.2 | Tablero completo: podio general, por grado, nota y experimento |
| BR3 | BR3.1–BR3.3 | Los dos CSV de hoy y el nivel de acceso de las descargas |
| BR4 | BR4.1–BR4.5 | Paquete `.zip` |
| BR5 | BR5.1–BR5.3 | Copia del reto y reiniciar |
| BR6 | BR6.1–BR6.2 | Copias: listar, descargar, borrar |
| BR7 | BR7.1 | Versión de la app |
| BR8 | BR8.1 | Diccionario de datos |
| BR9 | BR9.1 | Migración 3 del esquema |
| BR10 | BR10.1–BR10.3 | Pantallas completas (criterio de cierre) |
