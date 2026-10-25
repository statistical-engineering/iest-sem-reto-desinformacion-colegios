# Reto «Detectives de la desinformación»

Reto interactivo de **90 minutos** para estudiantes de **9.° a 11.°**: 3 expedientes sobre
**desinformación** y 7 **casos estadísticos** con datos reales de Colombia, calificación automática,
puntajes sin empates y podio para premiar el 1.°, 2.° y 3.° puesto.

Semillero de investigación — Desinformación en redes sociales (Colombia), 2026.

## Mapa de la carpeta

```
Reto_Desinformacion_Colegios/
├── README.md                        ← este archivo
├── PUBLICAR_EN_INTERNET.md          subir a GitHub y publicar con enlace fijo (cualquier red)
├── ABRIR PARA HACER PRUEBA/         doble clic en «ABRIR LA PRUEBA» (.bat Windows / .command Mac):
│                                    abre el reto como estudiante, panel docente y tablero
├── 1_Analisis_de_datos/             RESULTADOS del análisis: un ANALISIS.md por dataset,
│                                    con datos limpios, tablas y gráficas
├── 2_Aplicacion_Reto/               LA APLICACIÓN: servidor, páginas web, banco de preguntas,
│                                    simulacro y los lanzadores (.bat Windows / .command Mac)
├── 3_Guia_docente/                  PARA QUIEN DIRIGE EL RETO
│   ├── GUIA_DOCENTE.md                  logística del día, calificación, premiación
│   ├── GUIA_ACTIVIDADES_Y_RESPUESTAS.md cómo se dividen las actividades, dudas de los
│   │                                    estudiantes y respuestas esperadas
│   ├── CLAVE_DE_RESPUESTAS.md           todas las respuestas (generada desde la app)
│   ├── REGLAMENTO_ESTUDIANTES.md         para imprimir
│   └── ACTA_DE_PREMIACION.md
├── 4_Codigo_y_datos/                CÓMO SE HIZO
│   ├── METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md  fuentes, limpieza, análisis y diseño
│   ├── REGENERAR_TODO (.bat / .command)         repite todo el proceso
│   ├── datos_originales/                       copia de los datasets usados
│   └── scripts/                                código Python (análisis, gráficas, preguntas)
└── 5_Presentacion/                  Presentacion_10min.html: resumen del proyecto (flechas para avanzar, F = pantalla completa)
```

## ¿Qué leer según lo que necesites?

| Necesito… | Abre |
|---|---|
| Probar la actividad como docente y como estudiante | `ABRIR PARA HACER PRUEBA/` → «ABRIR LA PRUEBA» |
| Hacer el reto con un grupo | `3_Guia_docente/GUIA_DOCENTE.md` y luego `2_Aplicacion_Reto/INICIAR_RETO` |
| Que los estudiantes entren desde cualquier red | `PUBLICAR_EN_INTERNET.md` (y `2_Aplicacion_Reto/LEEME.md`) |
| Entender cada actividad y qué deben responder | `3_Guia_docente/GUIA_ACTIVIDADES_Y_RESPUESTAS.md` |
| Ver todas las respuestas correctas | `3_Guia_docente/CLAVE_DE_RESPUESTAS.md` |
| Saber de dónde salen los datos y qué se hizo | `4_Codigo_y_datos/METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md` |
| Ver cómo se comportan los datos | `1_Analisis_de_datos/LEEME.md` |
| Presentar el proyecto en 10 minutos | `5_Presentacion/Presentacion_10min.html` |

## Empezar en 3 pasos

1. Instalar **Python 3.9+** en el computador del docente (python.org; en Windows marcar «Add python.exe to PATH»).
2. Doble clic en `2_Aplicacion_Reto/PROBAR_ANTES_DEL_RETO` (`.bat` en Windows, `.command` en Mac) → debe decir **«TODO BIEN»**.
   En Mac, si no abre: clic derecho → **Abrir** (solo la primera vez).
3. El día del reto: doble clic en `2_Aplicacion_Reto/INICIAR_RETO`, proyectar el tablero y seguir la guía docente.

## Para quien desarrolla (semillero)

Las dependencias se manejan con [uv](https://docs.astral.sh/uv/): `pyproject.toml` las declara y
`uv.lock` fija las versiones exactas, para que todos trabajen con lo mismo.

| Grupo | Para qué | Paquetes |
|---|---|---|
| (base) | Aplicación del reto | Ninguno hoy: solo la biblioteca estándar |
| `datos` | Scripts de `4_Codigo_y_datos/scripts/` | `pandas`, `numpy`, `matplotlib` |
| `dev` | Herramientas del repositorio | `pre-commit` |

1. Instalar uv: <https://docs.astral.sh/uv/getting-started/installation/>.
2. En la raíz del repositorio: `uv sync --all-groups` (crea `.venv/` con Python 3.12 y todo lo anterior).
3. Activar las revisiones antes del primer commit: `uv run pre-commit install`.
4. Correr cualquier script con `uv run`, por ejemplo `uv run --group datos python 4_Codigo_y_datos/scripts/construir_banco.py`.

Para agregar un paquete: `uv add <paquete>` (app) o `uv add --group datos <paquete>`; el cambio en
`pyproject.toml` y `uv.lock` va en el mismo PR y necesita aprobación del responsable del repositorio.

## Si cambian los datos o las preguntas

Con uv instalado, doble clic en `4_Codigo_y_datos/REGENERAR_TODO` (`.bat` / `.command`): regenera el análisis, el banco de preguntas
(comprobando cada respuesta contra los datos), la clave de respuestas y corre el simulacro.
