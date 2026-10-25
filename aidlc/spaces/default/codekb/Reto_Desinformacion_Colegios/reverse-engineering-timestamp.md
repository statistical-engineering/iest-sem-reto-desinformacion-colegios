# Reverse Engineering Timestamp

## Run Record

- Date: 2026-10-24T04:42:18Z
- Commit: 99462c96268e29bde1738af0b4817d96df9a3989

Escaneo completo del repositorio en la raíz del workspace (repo sin registrar), profundidad
Standard, ejecución solo del desarrollador (colaboradores desactivados). Se leyó el código; no se
ejecutaron pruebas, builds ni programas del proyecto. El árbol de trabajo tenía un cambio sin
confirmar en `2_Aplicacion_Reto/INICIAR_RETO_INTERNET.bat` (solo finales de línea).

## Cobertura del análisis

- **Analizado en profundidad**: `2_Aplicacion_Reto/` (servidor, frontend, pruebas, arranque,
  Docker), `render.yaml`, lanzadores, `4_Codigo_y_datos/scripts/construir_banco.py` y
  `generar_clave_respuestas.py`, esquema de `banco_preguntas.json` por script, documentación viva.
- **Hojeado**: `generar_analisis.py`, `estilo_graficos.py`, `reto.css`, `1_Analisis_de_datos/`
  (generado), `datos_originales/` (fuente de verdad), `METODOLOGIA…md`, guías docentes sin
  respuestas, `5_Presentacion/`.
- **Dejado fuera**: `2_Aplicacion_Reto/datos/`, `datos_prueba/`, `.herramientas/`, las dos guías
  con respuestas de `3_Guia_docente/`, cachés y todo lo de AI-DLC.

## Scope of Analysis

```yaml
scope_version: 1
kind: full
intent: publicar-reto-nube
fingerprint: 1ec2f05f2ec95c4365eabbe517c0c757518c76ae
analyzed:
  paths:
    - ./
  components:
    - servidor.py
    - estudiante.js
    - admin.js
    - tablero.html
    - graficos.js
    - reto.css
    - banco_preguntas.json
    - reto.db
    - simulacro.py
    - modo_prueba.py
    - iniciar_internet.py
    - Lanzadores
    - Dockerfile y render.yaml
    - construir_banco.py
    - generar_analisis.py
    - estilo_graficos.py
    - generar_clave_respuestas.py
shallow:
  paths:
    - 1_Analisis_de_datos/
    - 4_Codigo_y_datos/datos_originales/
    - 4_Codigo_y_datos/METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md
    - 3_Guia_docente/
    - 5_Presentacion/
    - 2_Aplicacion_Reto/web/css/reto.css
    - 4_Codigo_y_datos/scripts/generar_analisis.py
    - 4_Codigo_y_datos/scripts/estilo_graficos.py
```
