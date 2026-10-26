# Reglas — U17 `u17-comparacion`

Reglas para llenar `despliegues/COMPARACION.md`, aplicar «pasa todo» (FR12.5), elegir con el orden de
FR12.6, escribir el ADR final y reescribir `PUBLICAR_EN_INTERNET.md` (FR8). Salen de `requirements.md`,
de `contract-summary.md` (C3), de `bolt-plan.md` (B13) y de `project.md` («Corrections»). Decisiones del
asistente con la potestad que dio el humano (2026-10-25); las de fondo están en `../decisions.md`.

```yaml
rules:
  - id: BR17.1
    statement: 'Cada casilla medida sale del JSON más reciente de la prueba común de esa opción (contrato C3), nunca de una corrida parcial ni de memoria.'
    category: validation
    applies_to: 'columnas Cloudflare y GitHub Pages de COMPARACION.md'
    trigger: al llenar la tabla
    logic: 'archivo = despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json con la fecha mayor; IF version_esquema no es 1 THEN se rechaza y la casilla dice «medición con esquema desconocido»; IF falta el archivo THEN la casilla dice «sin medir» y la opción no pasa; la casilla trae el valor, el nombre del archivo y la fecha'
    violation: 'la casilla queda «sin medir» y pasa_todo = false'
    source: 'FR12.4, contrato C3'
  - id: BR17.2
    statement: 'Una opción pasa todo solo con un «sí» con evidencia en cada fila de la tabla de FR12.5; «sin evidencia» cuenta como «no».'
    category: calculation
    applies_to: 'todas las opciones'
    trigger: al cerrar la fila de una opción
    logic: 'NFR1 = comprobaciones de la parte salas con 10 salas y 40 participantes en pasa = true; NFR2 = nfr.p95_responder_ms ≤ 1.000; NFR3 = nfr.p95_tablero_ms ≤ 1.500; NFR4 = nfr.sobrevive_reinicio = true; NFR5 = nfr.arranque_frio_ms ≤ 30.000 o null con cita oficial de que no duerme; NFR6 = costo US$ 0 con URL y nfr.peticiones ≤ 50 % de la cuota diaria o mensual citada; NFR7 = alguien del semillero que no la construyó la desplegó solo con su LEEME (nombre y fecha en la casilla); NFR8 = comprobaciones de la parte fugas en pasa = true; NFR9 = comprobaciones de 403 en pasa = true y revisión del código anotada; NFR10 y NFR10.1 = guía de cierre seguida una vez y comprobado que no quedan filas ni archivos (fecha en la casilla); NFR11 = comprobación de mismos puntos y misma clasificación en pasa = true; NFR12 = cobertura ≥ 80 % con la herramienta del ADR de la opción (comando y cifra en la casilla); pasa_todo = todos los doce en sí'
    violation: 'pasa_todo = false con la lista de NFR que fallan en motivo_no_pasa'
    source: 'FR12.5'
  - id: BR17.3
    statement: 'Las opciones sin despliegue entran en la tabla con sus cifras documentadas y «no pasa» con el motivo; nunca se borran de la tabla.'
    category: policy
    applies_to: 'Render (U15), Cloudflare Containers (U16), Apps Script (C-01)'
    trigger: al llenar la tabla
    logic: 'Render y Cloudflare Containers: se copian las columnas de functional-spec.md de U15 y U16 tal cual, con sus URL y fecha; Apps Script: todas las casillas dicen «no pasa por contrato: C-01» con enlace a contract-design/reviews/review-01.md y la frase de que su guía oficial no entrega cabeceras HTTP; IF una opción se saltó con aprobación del humano THEN su columna lleva «saltada el <fecha>: <motivo>»'
    violation: 'no aplica'
    source: 'FR12.2a, FR12.6, project.md («Corrections», Delivery Planning Q2-A), bolt-plan.md («Apps Script no se construye»)'
  - id: BR17.4
    statement: 'Un servicio externo es cada cuenta o producto que la persona del semillero crea o activa por separado y que tiene su propio panel o cuota.'
    category: calculation
    applies_to: 'fila «Piezas y servicios», criterio 1 de FR12.6'
    trigger: al contar
    logic: 'se cuenta 1 por proveedor en el que hay que abrir cuenta o activar un producto aparte del comando de despliegue de la opción; lo que se despliega junto con un solo comando en la misma cuenta cuenta como 1 (Workers: Worker + Durable Object + recursos estáticos con un solo wrangler deploy = 1); GitHub Pages = GitHub Pages + el servicio de la API (+ 1 si el almacén de datos es otro proveedor) ≥ 2; Apps Script = Apps Script + Google Sheets = 2; Render = 1; Cloudflare Containers = 1; el resultado y la lista de lo contado van en la casilla'
    violation: 'no aplica'
    source: 'FR12.6 (criterio 1), ADR-C1'
  - id: BR17.5
    statement: 'Una pieza propia es cada fila de la tabla «Piezas» de infrastructure-specification.md de la opción que alguien configura, sin contar el enlace fijo que asigna el proveedor.'
    category: calculation
    applies_to: 'fila «Piezas y servicios», criterio 2 de FR12.6'
    trigger: al contar
    logic: 'Workers (U1): Worker, recursos estáticos, Durable Object, secreto CLAVE_SEMILLERO = 4; GitHub Pages: lo que diga su infrastructure-specification.md; la casilla lista las piezas contadas'
    violation: 'no aplica'
    source: 'FR12.6 (criterio 2), ADR-C1'
  - id: BR17.6
    statement: 'Las líneas de código se cuentan con un solo comando sobre los archivos versionados de la carpeta de la opción, sin la copia de web/ ni el banco.'
    category: calculation
    applies_to: 'fila «Líneas de código», criterio 3 de FR12.6'
    trigger: al contar
    logic: 'comando: git ls-files despliegues/<opcion> | grep -v -E "^despliegues/<opcion>/(web/|src/banco\\.json|src/banco_huella\\.json|LEEME\\.md|\\.gitignore)$" | xargs wc -l | tail -1; cuentan src/, pruebas/, la configuración (wrangler.jsonc, Dockerfile) y herramientas/, incluido el parche de cambios a web/ (bolt-plan.md: la copia no cuenta, los cambios sí); el comando y el commit sobre el que se corrió van en la casilla'
    violation: 'no aplica'
    source: 'FR12.6 (criterio 3), bolt-plan.md («Reglas para todos los Bolts»), ADR-C1'
  - id: BR17.7
    statement: 'Entre las que pasan todo gana la de menos servicios externos; solo en empate se miran piezas y luego líneas; si persiste, decide el humano.'
    category: calculation
    applies_to: 'la elección'
    trigger: cuando todas las filas están cerradas
    logic: 'candidatas = filas con pasa_todo = true; IF ninguna THEN se aplica OQ2 y se pregunta al humano qué se relaja; ELSE ordenar por (servicios_externos, piezas_propias, lineas_codigo) ascendente; ganadora = primera; respaldo = segunda si existe; IF empate en los tres THEN el humano decide con la tabla; criterio_decisivo = el primero que separó a la ganadora de la segunda'
    violation: 'no aplica'
    source: 'FR12.6, project.md («Corrections», parsimonia)'
  - id: BR17.8
    statement: 'La tabla no se cierra a medias: U17 llena la tabla solo cuando cada opción gratuita terminó su unidad de resultados o fue saltada con aprobación.'
    category: constraint
    applies_to: 'U17 completa'
    trigger: al empezar U17
    logic: 'IF U6 no terminó THEN esperar; IF U14 no terminó y GitHub Pages no fue saltada THEN esperar; Apps Script ya está saltada por C-01 (bolt-plan.md); U15 y U16 ya entregaron sus columnas'
    violation: 'U17 no empieza'
    source: 'unit-of-work.md («U17», «Notas»)'
  - id: BR17.9
    statement: 'Las carpetas de las opciones que ni ganan ni son respaldo se borran en un commit propio, solo después de que el humano apruebe el ADR final; la tabla conserva su fila.'
    category: policy
    applies_to: 'despliegues/<opcion>/ de las perdedoras'
    trigger: tras la aprobación del ADR-C3
    logic: 'commit «chore: borrar las carpetas de las opciones descartadas» con solo esos borrados; el motivo de cada una queda en COMPARACION.md y en FR12.2 si el humano descartó una opción; el respaldo conserva carpeta, ADR y fila'
    violation: 'no se borra nada sin la aprobación'
    source: 'FR12.6, FR12.2'
  - id: BR17.10
    statement: 'PUBLICAR_EN_INTERNET.md se escribe para la ganadora y para personas que no programan: pasos numerados, frases de 30 palabras o menos y cada término técnico explicado la primera vez.'
    category: policy
    applies_to: 'PUBLICAR_EN_INTERNET.md'
    trigger: al reescribir la guía
    logic: 'secciones y orden en functional-spec.md («Forma de PUBLICAR_EN_INTERNET.md»); ningún paso pide escribir código: copiar y pegar un comando con sus valores ya puestos sí vale; incluye prueba de humo, volver atrás y cierre con respaldo antes de borrar; corrige la frase «reloj y clasificación en memoria» (FR8.3); costo US$ 0 con la cuota y su URL; nada de claves reales ni respuestas'
    violation: 'se corrige antes del push; se comprueba con un conteo de palabras por frase'
    source: 'FR8.1, FR8.2, FR8.3, NFR7, NFR10.1, .claude/rules/markdown-docs.md'
  - id: BR17.11
    statement: 'Ninguna casilla, ADR ni guía lleva claves, tokens, URL con clave, respuestas del banco ni datos de participantes.'
    category: policy
    applies_to: 'toda la unidad'
    trigger: siempre
    logic: 'el JSON de C3 ya no los trae; antes del push se revisa con grep -n -i -E "clave|token|KQMT-|\\?clave=" sobre COMPARACION.md, decisions.md y PUBLICAR_EN_INTERNET.md y solo se aceptan menciones genéricas'
    violation: 'se quita antes del push'
    source: 'project.md («Forbidden»), NFR9, contrato C3'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| Llenar la tabla | BR17.1, BR17.3, BR17.8 | De dónde sale cada casilla y cuándo se cierra |
| Pasa todo | BR17.2 | Los doce «sí» de FR12.5 con evidencia |
| Contar | BR17.4, BR17.5, BR17.6 | Servicios, piezas y líneas con un criterio fijo |
| Elegir | BR17.7, BR17.9 | Orden de FR12.6, respaldo y borrado de carpetas |
| Guía | BR17.10 | `PUBLICAR_EN_INTERNET.md` para la ganadora |
| Confidencialidad | BR17.11 | Sin claves ni respuestas |
