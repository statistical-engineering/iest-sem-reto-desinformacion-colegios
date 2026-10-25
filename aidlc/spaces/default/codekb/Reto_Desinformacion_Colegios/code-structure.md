# Estructura del código

Repositorio en la raíz del workspace, commit `99462c96268e29bde1738af0b4817d96df9a3989`. Se excluyen
los archivos de AI-DLC (`.claude/`, `aidlc/`, su bloque de `.gitignore`) y las carpetas ignoradas
(`2_Aplicacion_Reto/datos/`, `datos_prueba/`).

## Organización por carpetas

```text
Reto_Desinformacion_Colegios/
├── README.md, PUBLICAR_EN_INTERNET.md     documentación de entrada y de publicación en Render
├── render.yaml                            Blueprint de Render (servicio docker + disco /data)
├── .gitignore, .gitattributes             datos locales fuera de git; CRLF para .bat, LF para .command
├── ABRIR PARA HACER PRUEBA/               lanzadores de modo_prueba.py (.bat y .command)
├── 1_Analisis_de_datos/                   GENERADO por generar_analisis.py (6 carpetas + LEEME.md)
├── 2_Aplicacion_Reto/                     LA APLICACIÓN
│   ├── servidor.py                        servidor HTTP + API + SQLite + vigilante (913 líneas)
│   ├── banco_preguntas.json               GENERADO por construir_banco.py (≈ 110 KB)
│   ├── pruebas/simulacro.py               prueba de aceptación de extremo a extremo
│   ├── modo_prueba.py                     arranca un servidor de prueba en el puerto 8010 y abre el navegador
│   ├── iniciar_internet.py                túnel temporal de Cloudflare + servidor
│   ├── Dockerfile, .dockerignore          imagen python:3.12-slim para Render
│   ├── INICIAR_RETO*, PROBAR_ANTES_DEL_RETO*  lanzadores .bat (Windows) y .command (Mac)
│   ├── LEEME.md                           documentación técnica de la app
│   └── web/
│       ├── estudiante.html, admin.html, tablero.html
│       ├── css/reto.css
│       └── js/estudiante.js, admin.js, graficos.js
├── 3_Guia_docente/                        guías; CLAVE_DE_RESPUESTAS.md es GENERADA
├── 4_Codigo_y_datos/
│   ├── METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md
│   ├── REGENERAR_TODO.bat / .command      encadena los 4 pasos de regeneración
│   ├── datos_originales/                  FUENTE DE VERDAD (CSV y TXT, sin modificar)
│   └── scripts/                           generar_analisis.py, estilo_graficos.py,
│                                          construir_banco.py, generar_clave_respuestas.py
└── 5_Presentacion/Presentacion_10min.html presentación autónoma
```

## Clasificación de archivos

| Archivo | Categoría | Líneas | Notas |
|---|---|---|---|
| `2_Aplicacion_Reto/servidor.py` | Controlador + Servicio + Repositorio + Configuración (mezclados) | 913 | Ver mapa de secciones abajo |
| `2_Aplicacion_Reto/pruebas/simulacro.py` | Prueba | 262 | Importa `servidor` como módulo para resolver variantes; 29 comprobaciones |
| `2_Aplicacion_Reto/modo_prueba.py` | Utilidad (arranque local) | 97 | BD en `datos_prueba/`, clave y sala fijas de demostración |
| `2_Aplicacion_Reto/iniciar_internet.py` | Utilidad (arranque con túnel) | 169 | Descarga `cloudflared` a `.herramientas/` si falta |
| `2_Aplicacion_Reto/web/js/estudiante.js` | Estático (cliente SPA) | 652 | Estado `S`, enrutador por estado del participante, controles por tipo de pregunta |
| `2_Aplicacion_Reto/web/js/admin.js` | Estático (cliente SPA) | 278 | Estado `A`, panel, tabla, configuración, exportación |
| `2_Aplicacion_Reto/web/js/graficos.js` | Estático (biblioteca SVG) | 388 | `window.Graficos.dibujar`: barras horizontales, columnas, líneas, dispersión, intervalos, tabla |
| `2_Aplicacion_Reto/web/tablero.html` | Estático (HTML + CSS + JS incrustados) | 338 | Escenas por estado y diapositivas de resultados |
| `2_Aplicacion_Reto/web/estudiante.html`, `admin.html` | Estático (plantilla) | 36, 78 | Contenedor `#app`; `admin.html` trae CSS propio |
| `2_Aplicacion_Reto/web/css/reto.css` | Estático (estilos) | 404 | Variables de color y tipografía compartidas |
| `2_Aplicacion_Reto/banco_preguntas.json` | Modelo (datos generados) | — | Contiene respuestas y explicaciones |
| `2_Aplicacion_Reto/Dockerfile`, `render.yaml` | Configuración (despliegue) | 8, 17 | |
| Lanzadores `.bat` / `.command` (10 archivos) | Configuración (arranque) | 12-45 c/u | Buscan Python y llaman a un `.py` |
| `4_Codigo_y_datos/scripts/construir_banco.py` | Servicio (generador) | 1.190 | Una función por misión; `validar`; `main` |
| `4_Codigo_y_datos/scripts/generar_analisis.py` | Servicio (generador) | 1.190 | Una función `analizar_*` por dataset |
| `4_Codigo_y_datos/scripts/estilo_graficos.py` | Utilidad | 190 | Paleta y helpers de matplotlib |
| `4_Codigo_y_datos/scripts/generar_clave_respuestas.py` | Servicio (generador) | 72 | Banco → Markdown |
| `1_Analisis_de_datos/**` | Generado | — | No se analizó en profundidad |
| `4_Codigo_y_datos/datos_originales/**` | Datos fuente | 26-4.771 por archivo | Solo lectura |

## Mapa de secciones de `servidor.py`

| Líneas | Sección | Funciones | Naturaleza |
|---|---|---|---|
| 1-54 | Constantes y globales | `AQUI`, `WEB`, `DATOS`, `BANCO`, `PREGUNTAS`, `PUNTOS_TOTALES`, `BONO_MAX`, `LOCK`, `DB`, `CLAVE_ADMIN`, `URLS`, `RUTA_DB` | E/S al importar (lee el banco y `RETO_DATOS`) |
| 57-99 | Base de datos | `conectar`, `cfg`, `set_cfg`, `inicializar_config`, `duracion_seg` | E/S (SQLite) |
| 102-173 | Examen por participante | `rng_para`, `variante_de`, `resolver`, `visible_para`, `version_publica`, `examen_publico` | Pura (depende de `BANCO` global) |
| 176-257 | Calificación | `a_numero`, `validar_respuesta`, `fraccion` | Pura |
| 260-321 | Participantes | `participante_por_token`, `recalcular_puntos`, `finalizar`, `vencer_tiempos`, `clasificacion`, `puesto_de` | Mezcla: reglas de bono y orden + SQL + `time.time()` |
| 324-374 | Experimento | `experimento` | Mezcla: SQL + estadística pura |
| 377-499 | Vistas | `estado_participante`, `publico`, `resumen_admin`, `csv_resultados`, `csv_respuestas` | Mezcla: lectura SQL + armado de JSON/CSV |
| 502-652 | Acciones | `ErrorAPI`, `limpiar`, `nuevo_codigo`, `registrar`, `entrar`, `comenzar`, `responder`, `cambiar_estado`, `accion_participante`, `reiniciar` | Mezcla: reglas + SQL + reloj |
| 655-808 | HTTP | `TIPOS`, `PAGINAS`, `Manejador` (`enviar`, `cuerpo_json`, `token`, `es_admin`, `do_GET`, `do_POST`, `archivo`) | E/S (HTTP) con lógica de configuración en línea |
| 811-913 | Arranque | `ips_locales`, `ServidorDual`, `vigilante`, `main` | E/S (red, archivos, hilos, argumentos) |

## Grafo de dependencias

```text
servidor.py            -> stdlib (argparse, csv, hashlib, io, json, os, random, re, secrets, socket,
                          sqlite3, sys, threading, time, http.server, pathlib, urllib.parse)
                       -> banco_preguntas.json (lectura al importar), web/** (lectura por petición)
pruebas/simulacro.py   -> servidor (import como módulo: PREGUNTAS, resolver)
                       -> servidor.py (subproceso), sqlite3 (lee y altera la BD temporal), urllib
modo_prueba.py         -> servidor.py (subproceso), urllib, webbrowser
iniciar_internet.py    -> servidor.py (subproceso), cloudflared (subproceso), GitHub Releases (descarga)
web/estudiante.html    -> /static/js/graficos.js, /static/js/estudiante.js, /static/css/reto.css
web/admin.html         -> /static/js/admin.js, /static/css/reto.css
web/js/estudiante.js   -> window.Graficos (graficos.js), API /api/*
construir_banco.py     -> pandas; 1_Analisis_de_datos/*/datos/*_limpio.csv -> banco_preguntas.json
generar_analisis.py    -> pandas, numpy, matplotlib, estilo_graficos; datos_originales/ -> 1_Analisis_de_datos/
generar_clave_respuestas.py -> banco_preguntas.json -> 3_Guia_docente/CLAVE_DE_RESPUESTAS.md
```

No hay referencias circulares. `simulacro.py` depende de la API pública del módulo `servidor`
(`PREGUNTAS`, `resolver`): un refactor que mueva esas funciones debe mantener su importación o
actualizar la prueba.

## Patrones de código

- **Python**: funciones de módulo con estado global; una sola clase de dominio (`ErrorAPI`); clases
  solo para la infraestructura (`Manejador`, `ServidorDual`). Docstrings de módulo en todos los
  archivos; pocas funciones con docstring; sin anotaciones de tipo. Comentarios con `#` para
  explicar decisiones. SQL parametrizado con `?` (salvo el `IN (...)` armado con `?` en `simulacro.py`).
- **Enrutamiento**: cadenas de `if url.path == ...` en `do_GET` y `do_POST`; diccionario solo para
  las páginas (`PAGINAS`) y los tipos MIME (`TIPOS`).
- **Despacho por tipo**: `validar_respuesta` y `fraccion` usan cadenas `if t == ...` por tipo de
  pregunta; en el cliente, `CONTROLES` es un diccionario de tipo a función (patrón tabla).
- **JS**: módulos IIFE con `"use strict"`, sin dependencias ni build; helper `h(tag, attrs, ...hijos)`
  para crear DOM con `textContent` (evita inyección); `tablero.html` usa plantillas con `innerHTML` y
  una función `esc()`.
- **Determinismo**: barajado y variantes con `random.Random(sha256(semilla|clave))`.
- **Generadores de datos**: funciones constructoras (`q_opcion`, `q_evaluar`, `q_construir`, `caso`,
  `grafico`) y comprobaciones `exigir(...)` que detienen la construcción con `sys.exit`.
- **Idioma**: identificadores, mensajes y documentación en español sin tildes en identificadores.
