# Metodología: fuentes, tratamiento de los datos y construcción de la actividad

Este documento explica **de dónde salen los datos, qué se hizo con ellos y cómo se convirtieron en el
reto**. Todo el trabajo se hizo en **Python** (no se usó R). Los scripts y los datos están en esta
misma carpeta, así que cualquier persona del semillero puede repetirlo.

---

## 1. Qué hay en esta carpeta

```
4_Codigo_y_datos/
├── METODOLOGIA_Y_TRABAJO_CON_LOS_DATOS.md   ← este documento
├── REGENERAR_TODO.bat                        ← repite todo el proceso con doble clic
├── datos_originales/                         ← copia de los datos de entrada (sin modificar)
│   ├── colombiacheck/
│   │   ├── colombiacheck_verificado.csv            2.980 chequeos verificados
│   │   ├── colombiacheck_verificado_resumen.txt    trazabilidad del filtro
│   │   └── colombiacheck_tipo_de_chequeo.csv       url + tipo (redes / discurso público)
│   ├── dane_entic_2024/
│   │   ├── dane_entic2024_horas_uso_internet.csv
│   │   ├── dane_entic2024_actividades_internet.csv
│   │   └── dane_entic2024_actividades_redes_sociales.csv
│   └── banco_mundial/
│       └── banco_mundial_conectividad_colombia.csv
└── scripts/
    ├── estilo_graficos.py          estilo común de las gráficas (paleta accesible)
    ├── generar_analisis.py         limpieza, estadísticas, tablas, gráficas y ANALISIS.md
    ├── construir_banco.py          preguntas, respuestas calculadas y comprobaciones
    └── generar_clave_respuestas.py clave de respuestas para el docente
```

**Programas usados:** Python 3.12 con `pandas` (datos), `numpy` (cálculos) y `matplotlib`
(gráficas del análisis). Las versiones exactas quedan fijas en `uv.lock`, en la raíz del repositorio,
y las instala [uv](https://docs.astral.sh/uv/): así todos regeneran con las mismas versiones. Con
pandas 2.3.3, numpy 2.5.4 y matplotlib 3.11.2 el banco sale idéntico al versionado (misma
«version» del banco). Con pandas 3 el análisis falla, por eso `pyproject.toml` pide `pandas<3`.
La aplicación del reto declara sus dependencias en el mismo `pyproject.toml` (hoy no tiene: usa solo
la biblioteca estándar) y, en el navegador, HTML, CSS y JavaScript sin librerías externas (sus
gráficos se dibujan en SVG).

**Para repetir todo:** instalar uv una vez y hacer doble clic en `REGENERAR_TODO.bat` (o `.command`). Corre, en orden: análisis → banco de
preguntas → clave de respuestas → simulacro de la aplicación.

---

## 2. Fuentes de datos

| Fuente | Qué es | Quién lo produce | Cómo se obtuvo | Uso en el reto |
|---|---|---|---|---|
| **Colombiacheck** | Verificaciones (*fact-checks*) publicadas, 2020–2026 | Colombiacheck, medio de verificación del Consejo de Redacción | *Web scraping* propio del semillero de `colombiacheck.com/chequeos`, quedándose solo con los artículos que traen el marcado **ClaimReview** (schema.org) completo | **Núcleo**: Exp. 01, 02 y Casos 1, 2, 3, 5 y 7 |
| **DANE · ENTIC Hogares 2024** | Encuesta oficial de uso de tecnologías en los hogares (53.570 hogares, personas de 5 años y más) | DANE | Anexo oficial en Excel (cuadros Mod. 4-3, 4-7 y 4-8), extraído a CSV por el semillero | Casos 4, 6 y 7 |
| **Banco Mundial / UIT** | % de personas que usan internet y suscripciones móviles, Colombia 2000–2024 | Banco Mundial con datos de la UIT | Descarga del indicador `IT.NET.USER.ZS` | Análisis de contexto (sin preguntas en esta versión) |
| **Arechar et al. (2023)** | Experimento sobre desinformación en 16 países (*Nature Human Behaviour*, 7, 1502–1513) | Investigadores de MIT, Regina y otras | Resumen publicado y versión preliminar de acceso abierto (PsyArXiv) | Marco del reto, Exp. 01 (experimento) y Exp. 10 |

Los pasos previos de recolección (scraping y extracción del Excel del DANE) están en el proyecto
del semillero: `scripts/01_scrape_colombiacheck.py`, `scripts/02_build_dataset.py`,
`scripts/03_dataset_verificado.py` y `Datasets - Tiempo en redes sociales Colombia/scripts/`.
Esta carpeta parte de sus resultados ya limpios. Las fichas de procedencia completas están en
`reports/FUENTES.md` y `reports/DATOS_Y_FUENTES.md` del proyecto.

### Por qué estas fuentes son confiables y qué NO miden

- **Colombiacheck**: la afirmación, el veredicto y la fecha con hora los declara el propio medio en
  un estándar internacional (ClaimReview); no los interpretamos nosotros. **Pero describe lo que el
  medio decidió verificar, no toda la desinformación que circuló** (sesgo de selección). Esta
  advertencia atraviesa todo el reto y es, de hecho, una de sus lecciones.
- **DANE**: es la estadística oficial, con intervalos de confianza y coeficientes de variación
  (todas las horas tienen CVE menor a 6 %: alta precisión). **Mide horas de internet, no horas en
  redes**, y mide uso, no creencias.
- **Estudio de Nature**: revisado por pares, con datos y código abiertos. Colombia no participó.

---

## 3. Qué se hizo con los datos (`generar_analisis.py`)

### 3.1 Limpieza

| Dataset | Tratamiento |
|---|---|
| Colombiacheck | Se tradujo el día de la semana al español. Se unió el campo **tipo** (la sección del medio: «Desinformación en redes» / «Discurso público»), que el medio declara en su listado, usando la URL como llave. La sección «Desinformación en redes» se renombró **«Contenido viral en redes»**: indica dónde circuló el contenido, no su veredicto (algunos resultan Verdaderos), y el nombre original confundía a los estudiantes. Se marcó el **tema electoral** (palabras en título o afirmación: elección, voto, candidato, registraduría, jurado, escrutinio, tarjetón, consulta). |
| DANE (3 archivos) | Se quitaron las filas de notas al pie que venían en los CSV. Se convirtieron las cifras de texto a números. Se normalizaron los nombres de territorios (por ejemplo, «VALLE DEL CAUCA» → «Valle del Cauca»). Los nombres larguísimos de las actividades se acortaron y se guardó un diccionario con el nombre oficial. |
| Banco Mundial | Sin cambios (ya venía limpio). |

Los archivos limpios quedan en `1_Analisis_de_datos/<dataset>/datos/`.

### 3.2 Variables derivadas (y su honestidad)

Algunas variables son **conteos de palabras** en los títulos (IA, COVID/vacunas, video, foto,
estafas, plataformas, tema electoral). No son clasificaciones validadas: un chequeo sobre IA cuyo
título no diga «IA» no se cuenta. Por eso, en el reto siempre se presentan como «títulos que
mencionan…» y esa limitación aparece como respuesta correcta en el Caso 3.

### 3.3 Análisis realizados

| Análisis | Resultado principal |
|---|---|
| Distribución de veredictos | 76,6 % Falso · 20,3 % Cuestionable · 3 % verdaderos |
| Serie por año y por mes | 420–480 chequeos por año (estable); 2026 incompleto (hasta 17-sep) |
| Día y hora de publicación | 95 % en días hábiles; pico a las 15:00 → horario de la redacción |
| Temas en títulos por año | COVID/vacunas: 173 (2020) → 1 (2026). IA: 0 (2022) → 56 (2025) |
| Tipo × veredicto | Discurso público: 46,8 % Cuestionable vs. 18,2 % en redes → **efecto de composición** al desaparecer el discurso público desde 2024 |
| Elecciones | Meses con votación: +15 % de chequeos, pero 24,7 % sobre elecciones vs. 4,6 % en el resto |
| Tabla IA × Falso | P(Falso \| IA) = 98,4 %; P(IA \| Falso) = 5,4 % |
| Periodistas | 261 firmas; mediana 1 chequeo, promedio 11,4 (distribución muy sesgada) |
| DANE horas | 4,90 h/día (IC ± 0,07); urbano 5,17 vs. rural 3,28; correlación % diario–horas por departamento r = 0,17 |
| DANE actividades | 80,2 % de usuarios de internet usa redes; 16,0 % lee periódicos digitales; en lo rural, redes ≈ ciudad pero correo y periódicos mucho menores |
| Banco Mundial | 2,2 % (2000) → 79,4 % (2024); más de la mitad desde 2013 |

Cada dataset tiene su `ANALISIS.md` con tablas y gráficas en `1_Analisis_de_datos/`. Las gráficas
siguen una paleta probada para daltonismo, eje en cero, rejilla tenue y sin doble eje.

---

## 4. Cómo se construyó la actividad (`construir_banco.py`)

### 4.1 Principio: las respuestas se calculan, no se escriben

Cada pregunta con datos toma su respuesta **directamente de los archivos limpios**. Además, cada
afirmación que el reto marca como «respaldada» o «contradicha» tiene una **comprobación automática**
(`exigir(...)`): si los datos cambiaran y la clave dejara de ser cierta, el banco **no se genera** y
el script dice cuál comprobación falló. Ejemplos:

- Caso 1: «la proporción electoral en meses de votación es más de 3 veces la del resto» y «el
  volumen no sube un 50 %».
- Caso 2: «el contenido de redes es más Falso que el discurso público todos los años».
- Caso 5: «P(Falso | IA) > 95 % y P(IA | Falso) < 10 %».
- Caso 6: cada pareja se clasifica comparando los extremos de los intervalos de confianza.

### 4.2 Selección de los chequeos de las misiones de desinformación

- Se revisaron a mano los títulos y afirmaciones del corpus y se eligieron casos **aptos para
  estudiantes**: salud, ciencia, estafas, fotos y videos fuera de contexto, IA. Se excluyó contenido
  violento y de campaña electoral.
- Cada chequeo se busca por su URL y se **verifica su calificación oficial**; si no coincide, el
  script se detiene.
- La afirmación verificada llega recortada a 75 caracteres en ClaimReview: se revisaron una por
  una y solo dos estaban cortadas a mitad de palabra (se marcan con «…»).

### 4.3 Diseño pedagógico

- **3 expedientes de desinformación y lectura + 7 casos estadísticos**, cada caso con un encargo y
  una mecánica distinta (hipótesis previa, simulador, proyección, tabla de doble entrada,
  intervalos, taller de gráficos).
- **Distractores igual de elaborados que la respuesta correcta**, construidos con los errores
  típicos (saltos causales, generalizaciones, leer mal un año incompleto), para que no se adivine
  por la longitud.
- **Experimento de clase** basado en Arechar et al. (2023): fase de «compartir» sin puntos, fase de
  veracidad con puntos, recordatorio de exactitud asignado al azar (alternado) a la mitad del grupo
  y cálculo de la «sabiduría de la multitud».
- Nivel 9.°–11.°: porcentajes, divisiones, tablas y razonamiento; glosario en cada caso.

### 4.4 Calificación (en la aplicación)

- Puntaje parcial por ítem, pares ordenados, cercanía (estimaciones) o tolerancia (números).
- Bono de tiempo pequeño (máx. 20) proporcional a lo acertado y medido con la última respuesta.
- Clasificación sin empates: total → puntos → momento de la última respuesta → hora de entrega.
- Las respuestas correctas nunca llegan al navegador durante el reto; la evidencia de los Casos 1 y
  5 no se envía hasta registrar la hipótesis.

### 4.5 Verificación

- **Simulacro automático** (`2_Aplicacion_Reto/pruebas/simulacro.py`, 27 comprobaciones): todo
  correcto = 1.000 puntos, todo incorrecto = 0, puestos únicos, bloqueos, vencimiento del tiempo,
  exportaciones.
- **Prueba de carga**: 60 estudiantes simultáneos, 4.320 peticiones, 0 errores.
- **Revisión visual** de cada tipo de pregunta en computador y celular.

---

## 5. Limitaciones que conviene declarar si se presenta el trabajo

1. Colombiacheck es una **muestra editorial**, no aleatoria: no mide cuánta desinformación circula.
2. Las variables por palabras clave son **aproximaciones** sin validación manual.
3. 2026 está **incompleto** (datos hasta el 17 de septiembre de 2026).
4. Fuente única de verificación (no se contrastó con La Silla Vacía ni AFP Factual).
5. Entre los financiadores de Colombiacheck figura Meta (lo declara el propio medio).
6. El experimento de clase es una **demostración educativa**: para usarlo como investigación se
   necesita consentimiento de acudientes, asentimiento de los estudiantes y aval ético.

## 6. Cómo citar las fuentes

- Colombiacheck (Consejo de Redacción). *Chequeos*. https://colombiacheck.com/chequeos — datos del
  marcado ClaimReview, recolectados en septiembre de 2026.
- DANE. *Encuesta de Tecnologías de la Información y las Comunicaciones en Hogares (ENTIC
  Hogares) 2024*. Anexos estadísticos.
- Banco Mundial. *Personas que usan Internet (% de la población)*, indicador IT.NET.USER.ZS.
- Arechar, A. A., Allen, J., Berinsky, A. J., et al. (2023). Understanding and combatting
  misinformation across 16 countries on six continents. *Nature Human Behaviour*, 7, 1502–1513.
  https://doi.org/10.1038/s41562-023-01641-6
