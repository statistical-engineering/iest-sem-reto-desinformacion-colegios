# Escaneo de código del desarrollador — Reto «Detectives de la desinformación»

Escaneo completo del repositorio en la raíz del workspace (repo sin registrar), commit
`99462c96268e29bde1738af0b4817d96df9a3989`, profundidad Standard, 2026-10-24. Solo lectura: no se
ejecutaron pruebas, builds ni programas del proyecto. Se respetó la confidencialidad: no se copian
respuestas ni claves del banco ni de `3_Guia_docente/`.

## Developer Code Scan Results

### Scan Coverage
- **Analyzed deeply**:
  - `2_Aplicacion_Reto/servidor.py` (913 líneas, leído completo)
  - `2_Aplicacion_Reto/pruebas/simulacro.py` (leído completo)
  - `2_Aplicacion_Reto/web/js/estudiante.js`, `web/js/admin.js`, `web/js/graficos.js` (leídos completos)
  - `2_Aplicacion_Reto/web/estudiante.html`, `web/admin.html`, `web/tablero.html` (con su JS incrustado; leídos completos)
  - `2_Aplicacion_Reto/iniciar_internet.py`, `2_Aplicacion_Reto/modo_prueba.py` (leídos completos)
  - `2_Aplicacion_Reto/Dockerfile`, `2_Aplicacion_Reto/.dockerignore`, `render.yaml`
  - Lanzadores: `2_Aplicacion_Reto/*.bat`, `2_Aplicacion_Reto/*.command`, `ABRIR PARA HACER PRUEBA/*`, `4_Codigo_y_datos/REGENERAR_TODO.*`
  - `4_Codigo_y_datos/scripts/construir_banco.py` (estructura, utilidades, `validar`, `main`, misiones 01-02 y caso 1; resto por funciones y conteos)
  - `4_Codigo_y_datos/scripts/generar_clave_respuestas.py` (completo)
  - `2_Aplicacion_Reto/banco_preguntas.json` (esquema procesado por script: claves, tipos, conteos; sin volcar contenidos)
  - Documentación viva: `README.md`, `PUBLICAR_EN_INTERNET.md`, `2_Aplicacion_Reto/LEEME.md`, `.gitignore`, `.gitattributes`
- **Skimmed only**:
  - `4_Codigo_y_datos/scripts/generar_analisis.py` y `estilo_graficos.py` (cabecera, funciones, `main`)
  - `2_Aplicacion_Reto/web/css/reto.css` (404 líneas, estilos)
  - `1_Analisis_de_datos/` (GENERADO por `generar_analisis.py`; solo `LEEME.md` y listado)
  - `4_Codigo_y_datos/datos_originales/` (fuente de verdad; solo conteo de líneas)
  - `4_Codigo_y_datos/METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md` (encabezados y §4.4-§5)
  - `3_Guia_docente/GUIA_DOCENTE.md`, `REGLAMENTO_ESTUDIANTES.md`, `ACTA_DE_PREMIACION.md` (encabezados y secciones operativas)
  - `5_Presentacion/Presentacion_10min.html` (cabecera)
- **Left out**:
  - `2_Aplicacion_Reto/datos/` (ignorado por git; datos reales del reto, prohibido abrirlo)
  - `2_Aplicacion_Reto/datos_prueba/` (ignorado por git)
  - `2_Aplicacion_Reto/.herramientas/` (binario de cloudflared; no existe en este checkout)
  - `3_Guia_docente/CLAVE_DE_RESPUESTAS.md` y `GUIA_ACTIVIDADES_Y_RESPUESTAS.md` (contienen respuestas; no se abrieron)
  - `__pycache__/` (caché)
  - AI-DLC: `.claude/`, `aidlc/`, bloque AI-DLC de `.gitignore`, `.worktreeinclude`, `aidlc.settings.local.json`, `CLAUDE.md` (no versionado)

### Packages Found
- `2_Aplicacion_Reto/` — aplicación web (servidor + frontend estático) — Python 3.9+ biblioteca estándar, HTML/CSS/JS sin build — el reto en el aula
- `4_Codigo_y_datos/scripts/` — scripts de datos — Python con pandas, numpy, matplotlib — análisis, banco de preguntas y clave
- `1_Analisis_de_datos/` — salida generada (CSV, PNG, `ANALISIS.md`) — insumo de `construir_banco.py`
- `3_Guia_docente/` — documentación para docentes (una parte generada)
- `5_Presentacion/` — presentación HTML autónoma

### Build System
- **Type**: ninguno. Sin `requirements.txt`, `pyproject.toml`, `package.json` ni Makefile. Imagen Docker para Render.
- **Config Files**: `2_Aplicacion_Reto/Dockerfile` (`python:3.12-slim`, `RETO_HOSTING=1`, `RETO_DATOS=/data`), `2_Aplicacion_Reto/.dockerignore`, `render.yaml` (servicio `docker`, plan `0.5c-512mb`, disco 1 GB en `/data`, `healthCheckPath: /api/publico`, `RETO_CLAVE` con `sync: false`), `.gitattributes`.
- **Build Dependencies**: `datos_originales/` → `generar_analisis.py` → `1_Analisis_de_datos/**` → `construir_banco.py` → `banco_preguntas.json` → (`generar_clave_respuestas.py` → `CLAVE_DE_RESPUESTAS.md`) y (`servidor.py` lo carga al importar) → `simulacro.py`. `REGENERAR_TODO.*` encadena los 4 pasos.

### APIs Discovered
- REST/JSON propia — `2_Aplicacion_Reto/servidor.py` clase `Manejador` (`do_GET` líneas 702-735, `do_POST` 737-802) — 4 rutas de páginas/estáticos + 5 rutas GET de API + 11 rutas POST de API, todas despachadas con cadenas de `if` sobre `url.path`.

### Frameworks & Libraries
- Python biblioteca estándar — 3.9+ declarado, 3.12 en Docker — `http.server.ThreadingHTTPServer`, `sqlite3`, `threading`, `secrets`, `hashlib`, `csv`, `argparse`
- SQLite — la del intérprete — requiere ≥ 3.24 (UPSERT en `set_cfg`) y ≥ 3.27 (`VACUUM INTO` en `reiniciar`); WAL activado
- pandas, numpy, matplotlib — sin versión fijada — solo scripts de `4_Codigo_y_datos/scripts/`
- Google Fonts (Lexend, Bricolage Grotesque, Special Elite) — CDN — opcional, hay tipografías de respaldo
- cloudflared — última versión de GitHub Releases — túnel temporal (`iniciar_internet.py`) o Homebrew (`.command`)

### Test Coverage
- **Test Directories**: `2_Aplicacion_Reto/pruebas/`
- **Test Frameworks**: script propio `simulacro.py` (prueba de aceptación de extremo a extremo por HTTP contra un servidor real con BD temporal en el puerto 8765); 29 llamadas a `comprobar(...)` (la documentación dice 27). Sin `unittest` ni pruebas unitarias.
- **Coverage Config**: absent

### Code Quality Indicators
- **Linting**: no hay configuración; solo directivas `# noqa: BLE001` y `# noqa: E731` en el código.
- **CI/CD**: no hay pipeline; Render construye desde el repositorio (Blueprint).
- **Documentation**: buena para usuarios (README, LEEME, guías, metodología); docstrings de módulo en todos los `.py`; funciones mayormente sin docstring ni tipos (reconocido en `.claude/rules/python-code.md`).

### Technical Debt Signals
- `servidor.py` es un archivo «dios» de 913 líneas que mezcla carga del banco al importar (líneas 45-48), lógica pura (calificación 177-257, clasificación 300-314, experimento 325-374, examen público 103-173), persistencia SQLite (58-99, 261-298), HTTP (662-808) y arranque (812-913).
- Estado global de módulo mutable: `DB`, `CLAVE_ADMIN`, `URLS`, `RUTA_DB` reasignados con `global` en `main()` (línea 853); `LOCK` global serializa todas las peticiones de API.
- Enrutamiento por cadenas de `if` en `do_GET`/`do_POST`; la ruta `/api/admin/config` tiene la lógica de configuración en línea dentro del manejador (755-773).
- `validar_respuesta` (196-225) valida entradas con `assert`; con `python -O` la validación desaparece.
- `entrar` duerme 0,6 s (`time.sleep`, línea 550) dentro de `with LOCK` (línea 742): cada código incorrecto congela todo el servidor 0,6 s.
- `cambiar_estado` (607-619) no valida transiciones: cualquier estado puede pasar a cualquier otro.
- Varios `ValueError` no controlados devuelven 500: `int(d["duracion_min"])` (773), `int(d.get("id", 0))` (623), `Content-Length` no numérico (685).
- Ids de opciones e ítems asignados por posición en la lista de autoría (`construir_banco.py` `opciones` línea 130, `mision_compartir` línea 234, `q_evaluar` línea 171): el orden de autoría se correlaciona con la clave (verificado por script; no se reproducen conteos), y esos ids viajan al navegador.
- `/api/publico` (sin autenticación) incluye `experimento.por_publicacion[].verdad` desde el estado `cerrado` (líneas 433-434, 359), antes de publicar resultados.
- `es_admin` acepta la clave también por `?clave=` en la URL (698); no la usa `web/js/`.
- `.herramientas/` y `python/` (Python embebido de `INICIAR_RETO_INTERNET.bat`) no están en `.gitignore` ni en `.dockerignore`.
- `INICIAR_RETO_INTERNET.bat` modificado en el árbol de trabajo: perdió los finales de línea CRLF (diff de 26 líneas, mismo texto).
- Duplicación: `h()`/`num()` en `estudiante.js` y `admin.js`; `aNumero` (JS) replica `a_numero` (Python); `num()` en tres scripts Python; `ELECCIONES` en dos scripts.
- `version_publica` lista `"max"` dos veces en la tupla de claves públicas (130-131).

## Handoff Summary
- **Intent-relevant finding**: el estado del reto NO vive en memoria como dice `PUBLICAR_EN_INTERNET.md` («lleva el reloj y la clasificación en memoria»): reloj (`config.abierto_en`, `participantes.inicio`) y clasificación (calculada en cada petición desde `participantes`) se guardan/derivan de SQLite (`servidor.py` 555-569, 300-314). Lo que ata a una sola instancia es el `threading.RLock` global de proceso (línea 50), el hilo `vigilante` que vence tiempos cada 3 s (842-849) y el archivo SQLite en disco local (`RETO_DATOS`). Para la nube: Workers/D1 exigiría reescribir el servidor (no hay Python stdlib HTTP), un Durable Object reemplazaría lock + vigilante (alarmas), y Apps Script + Sheets perdería las garantías transaccionales de SQLite.
- **Risks / follow-up**: (1) fuga estructural de respuestas por ids de opciones/ítems correlacionados con la clave (rompe el invariante «las respuestas nunca salen al navegador»); (2) `/api/publico` expone `verdad` del Exp. 01 en `cerrado`; (3) `sleep` dentro del lock; (4) `assert` como validación; (5) sin validación de transiciones de estado; (6) en internet, `/api/publico` publica nombres y colegios de menores en el ranking sin autenticación y el panel no está limitado a localhost; (7) ninguna prueba unitaria: el refactor del núcleo puro necesita pruebas `unittest` nuevas además de `simulacro.py`. El refactor no debe renombrar claves JSON ni rutas que usa `web/js/`.
