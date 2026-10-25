# Dependencias

## Dependencias externas

### Aplicación (`2_Aplicacion_Reto/`)

| Dependencia | Tipo | Versión | Riesgo |
|---|---|---|---|
| Intérprete Python | Entorno | ≥ 3.9 | Bajo; la imagen fija `python:3.12-slim` (etiqueta móvil dentro de 3.12) |
| SQLite embebido en Python | Biblioteca del sistema | ≥ 3.27 por `VACUUM INTO` | Bajo; Python 3.9+ oficial trae versiones más nuevas, pero un Python de sistema antiguo fallaría solo al reiniciar el reto |
| Google Fonts | CDN | — | Bajo; solo estética, con respaldo |
| cloudflared | Binario externo | `latest` de GitHub Releases sin suma de verificación | Medio: se descarga y ejecuta sin verificar integridad (`iniciar_internet.py` `buscar_cloudflared`); solo en modo túnel |
| Render | Plataforma | Plan `0.5c-512mb`, disco 1 GB | Costo y una sola instancia |

No hay paquetes de PyPI ni de npm en la aplicación.

### Scripts de datos (`4_Codigo_y_datos/scripts/`)

| Paquete | Versión | Usado en |
|---|---|---|
| pandas | sin fijar | `generar_analisis.py`, `construir_banco.py` |
| numpy | sin fijar | `generar_analisis.py`, `estilo_graficos.py` |
| matplotlib | sin fijar | `generar_analisis.py`, `estilo_graficos.py` |

Sin archivo de dependencias, la regeneración depende de lo que tenga instalado cada máquina.
Agregar o fijar paquetes requiere aprobación del usuario (`CLAUDE.md`, «Dependencias»).

## Dependencias internas

```text
datos_originales/ ──generar_analisis.py──> 1_Analisis_de_datos/**/datos/*_limpio.csv
1_Analisis_de_datos/{01,02,03}/datos ──construir_banco.py──> 2_Aplicacion_Reto/banco_preguntas.json
banco_preguntas.json ──generar_clave_respuestas.py──> 3_Guia_docente/CLAVE_DE_RESPUESTAS.md
banco_preguntas.json ──(import)──> servidor.py ──(import)──> pruebas/simulacro.py
servidor.py <──(subproceso)── simulacro.py, modo_prueba.py, iniciar_internet.py, lanzadores
web/estudiante.html -> web/js/graficos.js + web/js/estudiante.js + web/css/reto.css
web/admin.html -> web/js/admin.js + web/css/reto.css
web/js/*.js, web/tablero.html -> API HTTP de servidor.py (contrato de claves JSON y rutas)
```

### Contratos que no se pueden romper sin tocar a otros

| Productor | Consumidor | Contrato |
|---|---|---|
| `construir_banco.py` | `servidor.py` | Esquema del banco: claves de raíz (`titulo`, `duracion_min`, `bono_tiempo_max`, `puntos_totales`, `misiones`, `version`), de misión y de pregunta (`id`, `tipo`, `puntos`, `respuesta`, `variantes`, `solo_grupo`, `requiere`, `tolerancia`, …) |
| `construir_banco.py` | `graficos.js` | Especificación de gráficos (`tipo`, `etiquetas`, `series`, `unidad`, `decimales`, `destacar`, `letra`, `margenes`, `puntos`, …) |
| `servidor.py` | `estudiante.js`, `admin.js`, `tablero.html` | Rutas y claves JSON de `api-documentation.md` |
| `servidor.py` | `simulacro.py` | Símbolos importados `PREGUNTAS` y `resolver`; argumentos `--puerto`, `--clave`, `--db`; esquema SQLite (`participantes.inicio`, `config.abierto_en`) que la prueba altera directamente |
| `servidor.py` | `modo_prueba.py`, `iniciar_internet.py`, lanzadores | Argumentos de línea de comandos y variable `PORT` |
| `servidor.py` | `render.yaml` | `GET /api/publico` responde 200 como chequeo de salud; `PORT`, `RETO_CLAVE`, `RETO_DATOS` |
| `servidor.py` (`a_numero`) | `estudiante.js` (`aNumero`) | Misma regla de lectura de números con coma o punto; duplicada en dos lenguajes |

### Acoplamientos relevantes para el refactor

- `simulacro.py` escribe en la BD SQLite de la prueba para adelantar relojes; si la persistencia cambia
  de motor o de esquema, la prueba de aceptación también cambia.
- `servidor.py` lee el banco **al importar**: importar el módulo para pruebas unitarias exige que
  exista `banco_preguntas.json` junto al archivo.
- La experiencia del estudiante depende del orden de barajado determinista (`rng_para` con
  `semilla|clave`); cambiar la función de semilla cambia lo que ve un participante a mitad de reto.
