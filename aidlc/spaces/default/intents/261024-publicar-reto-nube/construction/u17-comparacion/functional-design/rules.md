# Reglas — U17 `u17-comparacion`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Cambia lo siguiente:
>
> - **Revisadas:**
>   - BR17.1: dos corridas de Cloudflare (ADR-C5);
>   - BR17.2: NFR1 con 3 colegios y la parte `relojes`, NFR9 con la parte `claves` y los `no_aplica`;
>   - BR17.3: GitHub Pages «no se construye»;
>   - BR17.5: secreto `CLAVE_DOCENTE`;
>   - BR17.7: con una sola candidata, gana si pasa todo;
>   - BR17.8: espera solo a U6 y U2;
>   - BR17.9: se borran las cuatro carpetas;
>   - BR17.10: guía para una sala.
> - **Nuevas:** BR17.12 (estimación de consumo y página 1027) y BR17.13 (`LEEME.md` de Cloudflare con
>   Windows y Git Bash).

Reglas para llenar `despliegues/COMPARACION.md`, aplicar «pasa todo» (FR12.5), elegir con FR12.2c y
FR12.6, escribir el ADR final y reescribir `PUBLICAR_EN_INTERNET.md` (FR8) y el `LEEME.md` de Cloudflare.
Fuentes:

- `requirements.md`;
- `contract-summary.md`: C3;
- `contract-design-questions.md`: D8 y D9;
- `bolt-plan.md`: B13;
- `project.md`: «Corrections».

Son decisiones del asistente con la potestad que dio el humano (2026-10-25). Las de fondo están en
`../decisions.md`.

```yaml
rules:
  - id: BR17.1
    statement: 'Cada casilla medida sale de las dos mediciones más recientes de Cloudflare (contrato C3): la de la URL pública y la de wrangler dev; nunca de una corrida parcial ni de memoria.'
    category: validation
    applies_to: 'columna Cloudflare de COMPARACION.md'
    trigger: al llenar la tabla
    logic: 'publica = mediciones/cloudflare_<AAAA-MM-DD>.json y dev = mediciones/cloudflare-dev_<AAAA-MM-DD>.json, cada una la de fecha mayor; IF version_esquema no es 1 THEN se rechaza y la casilla dice «medición con esquema desconocido»; IF falta una de las dos THEN las casillas que dependen de ella dicen «sin medir» y la opción no pasa; cada casilla trae el valor, el archivo y la fecha; qué NFR sale de cuál está en ADR-C5'
    violation: 'la casilla queda «sin medir» y pasa_todo = false'
    source: 'FR12.4, contrato C3, ADR-C5'
  - id: BR17.2
    statement: 'Una opción pasa todo solo con un «sí» con evidencia en cada fila de la tabla de FR12.5; «sin evidencia» y «no se construye» cuentan como «no».'
    category: calculation
    applies_to: 'todas las opciones'
    trigger: al cerrar la fila de una opción
    logic: 'NFR1 = en dev, nfr.colegios = 3, nfr.participantes = 40 y todas las comprobaciones de la parte relojes en pasa = true; NFR2 = publica.nfr.p95_responder_ms ≤ 1.000; NFR3 = publica.nfr.p95_tablero_ms ≤ 1.500; NFR4 = sobrevive_reinicio = true en las dos; NFR5 = publica.nfr.arranque_frio_ms ≤ 30.000; NFR6 = costo US$ 0 con URL y EstimacionDeConsumo ≤ 50 % de la cuota diaria (BR17.12); NFR7 = alguien del semillero que no la construyó la desplegó solo con su LEEME (nombre y fecha en la casilla); NFR8 = comprobaciones de la parte fugas en pasa = true en publica; NFR9 = comprobaciones de la parte claves en pasa = true en publica y revisión del código anotada; NFR10 y NFR10.1 = guía de cierre seguida una vez (paquete guardado, «Reiniciar», copias borradas) y comprobado con /api/admin/resumen y /api/admin/copias que no quedan filas ni copias (fecha en la casilla); NFR11 = mismas_fracciones_que_local y mismos_csv_que_local en pasa = true; NFR12 = cobertura ≥ 80 % con node --test --experimental-test-coverage nombrando cada archivo (comando y cifra en la casilla); en todos, cada id de publica.nfr.no_aplica tiene que estar en pasa = true en dev; pasa_todo = todos los doce en sí'
    violation: 'pasa_todo = false con la lista de NFR que fallan en motivo_no_pasa'
    source: 'FR12.5, ADR-C5, project.md («Corrections»: node --test nombrando el archivo)'
  - id: BR17.3
    statement: 'Las opciones que no se construyen entran en la tabla con su motivo y, si las hay, sus cifras documentadas; nunca se borran de la tabla.'
    category: policy
    applies_to: 'Render (U15), Cloudflare Containers (U16), Apps Script (C-01), GitHub Pages (FR12.2c)'
    trigger: al llenar la tabla
    logic: 'Render y Cloudflare Containers: se copian las columnas de functional-spec.md de U15 y U16 tal cual, con sus URL y fecha; Apps Script: todas las casillas dicen «no pasa por contrato: C-01», con enlace a contract-design/reviews/review-01.md y la frase de que su guía oficial no entrega cabeceras HTTP; GitHub Pages: las casillas medidas dicen «no se construye (FR12.2c)» y «Piezas y servicios» dice «≥ 2 servicios, sin desplegar»; IF una opción se saltó con aprobación del humano THEN su columna lleva «saltada el <fecha>: <motivo>»'
    violation: 'no aplica'
    source: 'FR12.2a, FR12.2c, FR12.6, project.md («Corrections», Delivery Planning Q2-A)'
  - id: BR17.4
    statement: 'Un servicio externo es cada cuenta o producto que la persona del semillero crea o activa por separado y que tiene su propio panel o cuota.'
    category: calculation
    applies_to: 'fila «Piezas y servicios», criterio 1 de FR12.6'
    trigger: al contar
    logic: 'se cuenta 1 por proveedor en el que hay que abrir cuenta o activar un producto aparte del comando de despliegue de la opción; lo que se despliega junto con un solo comando en la misma cuenta cuenta como 1 (Workers: Worker + Durable Object + recursos estáticos con un solo wrangler deploy = 1); GitHub Pages ≥ 2; Apps Script = 2; Render = 1; Cloudflare Containers = 1; el resultado y la lista de lo contado van en la casilla'
    violation: 'no aplica'
    source: 'FR12.6 (criterio 1), ADR-C1'
  - id: BR17.5
    statement: 'Una pieza propia es cada fila de la tabla «Piezas» de infrastructure-specification.md de la opción que alguien configura, sin contar el enlace fijo que asigna el proveedor.'
    category: calculation
    applies_to: 'fila «Piezas y servicios», criterio 2 de FR12.6'
    trigger: al contar
    logic: 'Workers: Worker, recursos estáticos, Durable Object y secreto CLAVE_DOCENTE = 4; DURACION_MINIMA_MIN no cuenta (solo .dev.vars, D9); la casilla lista las piezas contadas'
    violation: 'no aplica'
    source: 'FR12.6 (criterio 2), ADR-C1, ADR-010'
  - id: BR17.6
    statement: 'Las líneas de código se cuentan con un solo comando sobre los archivos versionados de la carpeta de la opción, sin la copia de web/ ni el banco.'
    category: calculation
    applies_to: 'fila «Líneas de código», criterio 3 de FR12.6'
    trigger: al contar
    logic: 'comando: git ls-files despliegues/<opcion> | grep -v -E "^despliegues/<opcion>/(web/|src/banco\\.json|src/banco_huella\\.json|LEEME\\.md|\\.gitignore)$" | xargs wc -l | tail -1; cuentan src/, pruebas/, la configuración (wrangler.jsonc) y herramientas/, incluido el parche de cambios a web/; el comando y el commit sobre el que se corrió van en la casilla'
    violation: 'no aplica'
    source: 'FR12.6 (criterio 3), bolt-plan.md («Reglas para todos los Bolts»), ADR-C1'
  - id: BR17.7
    statement: 'Cloudflare, la única candidata construida, gana si pasa todo; si no pasa, no se elige y se pregunta al humano.'
    category: calculation
    applies_to: 'la elección'
    trigger: cuando todas las filas están cerradas
    logic: 'candidatas = filas con pasa_todo = true; IF candidatas = [cloudflare] THEN ganadora = cloudflare y criterio_decisivo = unica_que_pasa; IF ninguna THEN se aplica OQ2 y se pregunta al humano qué se relaja o qué opción se reabre; IF el humano reabre otra opción y pasa todo THEN se ordena por (servicios_externos, piezas_propias, lineas_codigo) ascendente, como dice FR12.6; respaldo = la versión local, siempre'
    violation: 'no aplica'
    source: 'FR12.2c («si Cloudflare pasa todo, es la elegida sin respaldo construido»), FR12.6, project.md («Corrections», parsimonia)'
  - id: BR17.8
    statement: 'La tabla no se cierra a medias: U17 la llena solo cuando U6 terminó y existen las dos mediciones de Cloudflare.'
    category: constraint
    applies_to: 'U17 completa'
    trigger: al empezar U17
    logic: 'IF U6 no terminó THEN esperar; IF falta cloudflare_<fecha>.json o cloudflare-dev_<fecha>.json THEN esperar; Apps Script, GitHub Pages, Render y Cloudflare Containers ya tienen su motivo (FR12.2c, U15, U16)'
    violation: 'U17 no empieza'
    source: 'unit-of-work.md («U17», «Notas»: empieza cuando U6 terminó y U2 midió Cloudflare)'
  - id: BR17.9
    statement: 'Las carpetas de las opciones descartadas se borran en un commit propio, solo después de que el humano apruebe el ADR final; la tabla conserva su fila.'
    category: policy
    applies_to: 'despliegues/apps-script/, despliegues/render/, despliegues/cloudflare-containers/ y despliegues/github-pages/'
    trigger: tras la aprobación del ADR-C3
    logic: 'commit «chore: borrar las carpetas de las opciones descartadas» con solo esos borrados; el motivo de cada una queda en COMPARACION.md; se conservan cloudflare/, prueba_comun/, LEEME.md y COMPARACION.md'
    violation: 'no se borra nada sin la aprobación'
    source: 'FR12.6, FR12.2, FR12.2c'
  - id: BR17.10
    statement: 'PUBLICAR_EN_INTERNET.md se escribe para Cloudflare, una sola sala y personas que no programan: pasos numerados, frases de 30 palabras o menos y cada término técnico explicado la primera vez.'
    category: policy
    applies_to: 'PUBLICAR_EN_INTERNET.md'
    trigger: al reescribir la guía
    logic: 'secciones y orden en functional-spec.md («Forma de PUBLICAR_EN_INTERNET.md»); ningún paso pide escribir código: copiar y pegar un comando con sus valores ya puestos sí vale; un solo docente con la clave docente, sin crear salas ni claves de sala; el tablero se abre en /tablero sin ?sala=; incluye la lista de colegios, «Arrancar reloj», prueba de humo, volver atrás, la página 1027 y el cierre con respaldo antes de borrar (paquete, «Reiniciar», borrar copias); corrige la frase «reloj y clasificación en memoria» (FR8.3); costo US$ 0 con la cuota y su URL; nada de claves reales ni respuestas'
    violation: 'se corrige antes del push; se comprueba con un conteo de palabras por frase'
    source: 'FR8.1, FR8.2, FR8.3, FR11, NFR7, NFR10.1, ADR-009 a ADR-011, .claude/rules/markdown-docs.md'
  - id: BR17.11
    statement: 'Ninguna casilla, ADR, guía ni LEEME lleva claves, tokens, URL con clave, respuestas del banco ni datos de participantes.'
    category: policy
    applies_to: 'toda la unidad'
    trigger: siempre
    logic: 'el JSON de C3 ya no los trae; antes del push se revisa con grep -n -i -E "clave|token|\\?clave=" sobre COMPARACION.md, decisions.md, PUBLICAR_EN_INTERNET.md y despliegues/cloudflare/LEEME.md, y solo se aceptan menciones genéricas («tu clave», «UNACLAVEDEPRUEBA» de ejemplo en .dev.vars)'
    violation: 'se quita antes del push'
    source: 'project.md («Forbidden»), NFR9, contrato C3'
  - id: BR17.12
    statement: 'El consumo de un reto real se estima con las peticiones medidas y los refrescos de las pantallas, y se compara con las 100.000 peticiones diarias del plan gratuito; la guía explica qué hacer si se pasa.'
    category: calculation
    applies_to: 'fila «Consumo de la cuota» y sección 8 de la guía'
    trigger: al llenar la tabla
    logic: 'EstimacionDeConsumo.total = Σ por pantalla abierta (90 × 60 / intervalo en segundos) + 40 × preguntas × 2 + inscripciones, con los intervalos leídos de la copia de web/ de Cloudflare y un tablero, un panel y 40 estudiantes abiertos; porcentaje = total / 100.000 × 100; NFR6 exige ≤ 50 %; se anota también publica.nfr.peticiones de la prueba; la cuota se vuelve a consultar en https://developers.cloudflare.com/workers/platform/limits/ y los límites del plan gratuito de Durable Objects en su página oficial de precios, con la fecha; la guía dice que al pasarse la cuota Cloudflare muestra su página de error 1027 hasta la medianoche UTC (las 19:00 en Colombia) y que entonces el reto sigue en red local o con el túnel temporal'
    violation: 'NFR6 = no, con el porcentaje'
    source: 'NFR6, ADR-W20 de U5, https://developers.cloudflare.com/workers/platform/limits/ («100,000 requests, resetting at midnight UTC»; al pasarse, «Returns a Cloudflare 1027 error page»)'
  - id: BR17.13
    statement: 'El LEEME.md de Cloudflare queda para una sola sala y explica cada paso también para Windows con Git Bash.'
    category: policy
    applies_to: 'despliegues/cloudflare/LEEME.md'
    trigger: al cerrar U17, antes de la guía
    logic: 'se reemplaza CLAVE_SEMILLERO por CLAVE_DOCENTE en .dev.vars y en wrangler secret put; .dev.vars de ejemplo con DURACION_MINIMA_MIN=1 y la advertencia de que nunca va al despliegue (D9); se agrega el paso único wrangler secret delete CLAVE_SEMILLERO; «Probar en tu computador» corre las dos corridas de ADR-C5 con sus comandos completos; «Cómo se usa el día del reto» queda para un docente (código de sala, colegios, abrir, Arrancar reloj, tablero sin ?sala=); «Volver a la versión anterior» advierte que no se vuelve a una versión anterior a la de una sala (ADR-W19 de U5); se agrega la sección «Desde Windows» de ADR-C6 (Git para Windows con Git Bash, py -3 en vez de python3, PowerShell si Git Bash no muestra la pregunta del secreto); .gitattributes gana *.sh text eol=lf y *.patch text eol=lf'
    violation: 'se corrige antes del push'
    source: 'ADR-C6, ADR-010, D9, bolt-plan.md (B13: «también desde Windows con Git Bash»), ADR-W19 de U5'
```

## Resumen

| Grupo | Reglas | Qué cubre |
|---|---|---|
| Llenar la tabla | BR17.1, BR17.3, BR17.8 | De dónde sale cada casilla y cuándo se cierra |
| Pasa todo | BR17.2, BR17.12 | Los doce «sí» de FR12.5 con evidencia y el consumo frente a la cuota |
| Contar | BR17.4, BR17.5, BR17.6 | Servicios, piezas y líneas con un criterio fijo |
| Elegir | BR17.7, BR17.9 | FR12.2c, FR12.6 y borrado de carpetas |
| Guías | BR17.10, BR17.13 | `PUBLICAR_EN_INTERNET.md` y el `LEEME.md` de Cloudflare, también para Windows |
| Confidencialidad | BR17.11 | Sin claves ni respuestas |
