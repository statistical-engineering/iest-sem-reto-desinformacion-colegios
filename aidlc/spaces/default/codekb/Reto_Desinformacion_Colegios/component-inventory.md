# Inventario de componentes

Cada encabezado de nivel 3 es el nombre de un componente tal como lo registra el bloque
`Scope of Analysis` de `reverse-engineering-timestamp.md`.

## Aplicación en ejecución (`2_Aplicacion_Reto/`)

### servidor.py

- **Responsabilidad**: proceso único que sirve las páginas, la API JSON, las exportaciones CSV, la
  persistencia SQLite y el vencimiento automático de tiempos. Hace cumplir las reglas del reto.
- **Entradas**: argumentos `--puerto`, `--clave`, `--db`, `--url-publica`; variables `PORT`,
  `RETO_CLAVE`, `RETO_DATOS`, `RETO_URL_PUBLICA`, `RENDER_EXTERNAL_URL`, `RETO_HOSTING`, `RENDER`.
- **Depende de**: `banco_preguntas.json`, `web/`, `reto.db`, `clave_docente.txt`.
- **Lo usan**: `estudiante.js`, `admin.js`, `tablero.html`, `simulacro.py` (como subproceso y como
  módulo importado), `modo_prueba.py`, `iniciar_internet.py`, lanzadores, `Dockerfile`.
- **Estado de proceso**: `LOCK` (RLock global), `DB` (conexión compartida), `CLAVE_ADMIN`, `URLS`,
  `BANCO`/`PREGUNTAS`, hilo `vigilante`.

### estudiante.js

- **Responsabilidad**: aplicación del estudiante: inscripción o ingreso con código, sala de espera,
  mapa de expedientes, misiones con un control por tipo de pregunta (`CONTROLES`), simulador de
  mezcla, entrega, resultados y revisión; registra salidas de pestaña.
- **Depende de**: `graficos.js` (`window.Graficos`), rutas de estudiante de la API, `localStorage`.
- **Lo usa**: `web/estudiante.html`.

### admin.js

- **Responsabilidad**: panel docente: login con clave, pasos del reto, botones de transición con doble
  confirmación, configuración, experimento, tabla de participantes con acciones, descarga de CSV y
  reinicio.
- **Depende de**: rutas `/api/admin/*`, `sessionStorage`.
- **Lo usa**: `web/admin.html`.

### tablero.html

- **Responsabilidad**: pantalla para proyectar: inscripción (URL y sala), reloj de referencia y
  ranking en vivo (si no hay modo sorpresa), aviso de cierre y diapositivas de resultados (podio,
  top 10, experimento en tres diapositivas). Atajos de teclado F, ←, →, espacio.
- **Depende de**: `GET /api/publico`.
- **Lo usa**: el docente lo abre en el proyector.

### graficos.js

- **Responsabilidad**: dibuja en SVG, sin librerías, las especificaciones de gráfico del banco
  (`barras_h`, `columnas` simples y agrupadas, `lineas`, `dispersion`, `intervalos`, `tabla`), con
  tooltip y «Ver tabla».
- **Depende de**: nada externo.
- **Lo usa**: `estudiante.js`.

### reto.css

- **Responsabilidad**: estilos compartidos (variables de color y tipografía, componentes).
- **Lo usan**: `estudiante.html`, `admin.html`.

### banco_preguntas.json

- **Responsabilidad**: banco de 10 misiones y 42 preguntas con respuestas, explicaciones, gráficos y
  configuración (`duracion_min`, `bono_tiempo_max`, `puntos_totales`, `version`).
- **Lo genera**: `construir_banco.py`. **Lo leen**: `servidor.py`, `simulacro.py`,
  `generar_clave_respuestas.py`.
- **Confidencial**: nunca se sirve como archivo; contiene todas las claves.

### reto.db

- **Responsabilidad**: base SQLite de la ejecución (tablas `config`, `participantes`, `respuestas`,
  `eventos`), en `datos/` o en `$RETO_DATOS`; copias `copia_reto_<fecha>.db` al reiniciar.
- **Lo crea y usa**: `servidor.py`. **Lo lee y altera en pruebas**: `simulacro.py` (BD temporal).
- **No se versiona** (`.gitignore`); no se abrió en este análisis.

## Pruebas y arranque

### simulacro.py

- **Responsabilidad**: prueba de aceptación de extremo a extremo con N estudiantes ficticios (40 por
  defecto) sobre una BD temporal y el puerto 8765; 29 comprobaciones; imprime «TODO BIEN» o la lista
  de fallas y sale con código 1.
- **Depende de**: `servidor.py` (subproceso y `import servidor as S`), `sqlite3` para adelantar
  relojes, `urllib`.
- **Lo usan**: `PROBAR_ANTES_DEL_RETO.*`, `REGENERAR_TODO.*` (con 30 estudiantes).

### modo_prueba.py

- **Responsabilidad**: abre una sesión de prueba (puerto 8010, BD en `datos_prueba/`, sala y clave
  de demostración fijas), abre el reto y lanza tres pestañas del navegador.
- **Lo usan**: `ABRIR PARA HACER PRUEBA/ABRIR LA PRUEBA.*`.

### iniciar_internet.py

- **Responsabilidad**: crea un túnel temporal `trycloudflare.com`, mantiene despierto el equipo y
  arranca `servidor.py` con `--url-publica`. Descarga `cloudflared` a `.herramientas/` si no está.
- **Lo usa**: `INICIAR_RETO_INTERNET.bat` (el `.command` hace lo mismo en bash con Homebrew).

### Lanzadores

- **Responsabilidad**: doble clic para docentes sin consola. `INICIAR_RETO.*`,
  `INICIAR_RETO_INTERNET.*`, `PROBAR_ANTES_DEL_RETO.*`, `ABRIR PARA HACER PRUEBA/ABRIR LA PRUEBA.*`,
  `4_Codigo_y_datos/REGENERAR_TODO.*`. Los `.bat` buscan `py -3` o `python` (el de internet también
  un `python\python.exe` embebido y exige 3.9+); los `.command` buscan `python3`.
- **Formato**: `.bat` con CRLF, `.command` con LF (`.gitattributes`).

### Dockerfile y render.yaml

- **Responsabilidad**: imagen `python:3.12-slim` con `RETO_HOSTING=1` y `RETO_DATOS=/data`, `CMD
  python servidor.py`; Blueprint de Render con plan `0.5c-512mb`, disco de 1 GB en `/data`,
  `healthCheckPath: /api/publico`, `RETO_CLAVE` pedida al crear el servicio.
- **Contexto de build**: solo `2_Aplicacion_Reto/` (la imagen no lleva las guías).

## Pipeline de datos (`4_Codigo_y_datos/scripts/`)

### construir_banco.py

- **Responsabilidad**: arma las 10 misiones a partir de los CSV limpios, calcula cada clave que
  depende de los datos, la comprueba con `exigir(...)` (29 llamadas), valida el banco (`validar`:
  ids únicos, claves coherentes con opciones e ítems, `requiere` y `revelar_tras` existentes, total
  1.000) y escribe `banco_preguntas.json` con una versión SHA-256 de 10 caracteres.
- **Depende de**: pandas; `1_Analisis_de_datos/01_*/datos/`, `02_*/datos/`, `03_*/datos/`.

### generar_analisis.py

- **Responsabilidad**: limpia los datos originales y escribe, por dataset, `datos/`, `tablas/`,
  `figuras/` y `ANALISIS.md`, más `1_Analisis_de_datos/LEEME.md`.
- **Depende de**: pandas, numpy, matplotlib, `estilo_graficos.py`; `4_Codigo_y_datos/datos_originales/`.

### estilo_graficos.py

- **Responsabilidad**: paleta (apta para daltonismo según su docstring) y helpers de matplotlib
  (`apply`, `hbar`, `stacked`, `heatmap`, `save`, formatos).
- **Lo usa**: `generar_analisis.py`.

### generar_clave_respuestas.py

- **Responsabilidad**: convierte el banco en `3_Guia_docente/CLAVE_DE_RESPUESTAS.md`.
- **Depende de**: `banco_preguntas.json`.

## Matriz de dependencias

| Componente | Depende de |
|---|---|
| servidor.py | banco_preguntas.json, reto.db, web/ |
| estudiante.js | servidor.py (API), graficos.js |
| admin.js | servidor.py (API) |
| tablero.html | servidor.py (API) |
| simulacro.py | servidor.py, banco_preguntas.json |
| modo_prueba.py | servidor.py |
| iniciar_internet.py | servidor.py, cloudflared |
| Lanzadores | servidor.py, simulacro.py, modo_prueba.py, iniciar_internet.py, scripts de datos |
| Dockerfile y render.yaml | servidor.py y todo `2_Aplicacion_Reto/` |
| construir_banco.py | salida de generar_analisis.py |
| generar_analisis.py | datos_originales/, estilo_graficos.py |
| generar_clave_respuestas.py | banco_preguntas.json |
