# Visión de negocio

Reto «Detectives de la desinformación» — Semillero de investigación «Desinformación en redes
sociales (Colombia)», 2026. Repositorio analizado en el commit `99462c96268e29bde1738af0b4817d96df9a3989`.

## Propósito

Actividad de aula de **90 minutos** para estudiantes de **9.° a 11.°**. En un navegador, cada
estudiante o equipo resuelve **10 misiones** (3 expedientes sobre desinformación y lectura científica,
7 casos estadísticos) construidas con datos reales de Colombia: Colombiacheck, DANE ENTIC 2024 y
Banco Mundial, más el estudio de Arechar et al. (2023) en *Nature Human Behaviour* (`README.md`,
`construir_banco.py` docstring). La aplicación califica sola, entrega un podio sin empates y muestra
en el tablero un «experimento de la clase» que replica el estudio de Nature.

No es una librería ni un producto comercial: es una app web para usar en clase, un análisis de datos
y un conjunto de guías para docentes.

## Actores

| Actor | Qué hace | Dónde |
|---|---|---|
| Estudiante (o equipo) | Se inscribe con el código de sala, recibe un código de 5 caracteres, responde las misiones, entrega y, al final, revisa sus respuestas | `/` (`web/estudiante.html`, `web/js/estudiante.js`) |
| Docente | Abre, cierra y publica el reto; configura sala, duración y opciones; vigila salidas de pestaña; anula o fuerza entregas; exporta CSV; reinicia | `/admin` (`web/admin.html`, `web/js/admin.js`), con clave docente |
| Proyector / tablero | Muestra URL, código de sala, inscritos, reloj, ranking (si no hay modo sorpresa), podio y experimento | `/tablero` (`web/tablero.html`) |
| Semillero (autores) | Mantienen datos, preguntas y guías; regeneran el banco | `4_Codigo_y_datos/scripts/`, `REGENERAR_TODO.*` |

## Funcionalidad clave

- **Inscripción con código de sala** y recuperación de sesión con el código del participante
  (`servidor.py` `registrar`, `entrar`).
- **Ciclo del reto controlado por el docente**: `inscripcion` → `abierto` → `cerrado` → `resultados`
  (`servidor.py` `ESTADOS`, `cambiar_estado`).
- **Reloj medido por el servidor**: global por defecto (corre desde que el docente abre) o individual
  desde «Comenzar»; los intentos vencidos se entregan solos cada 3 segundos (`vigilante`).
- **Calificación automática con crédito parcial** para 10 tipos de pregunta: `opcion`, `multiple`,
  `clasificar`, `ordenar`, `construir`, `estimar`, `numero`, `texto`, `compartir`, `recordatorio`
  (`servidor.py` `fraccion`).
- **Bono de tiempo** de hasta 20 puntos, proporcional a lo acertado y medido con la última respuesta
  (`servidor.py` `finalizar`).
- **Clasificación en orden total**: total ↓, puntos ↓, momento de la última respuesta ↑, hora de
  entrega ↑, orden de inscripción ↑ (`servidor.py` `clasificacion`).
- **Experimento de clase A/B**: asignación alternada; solo el grupo B ve el «recordatorio de exactitud»;
  el tablero compara «compartir» frente a «creer» y la «sabiduría de la multitud» (`servidor.py` `experimento`).
- **Antitrampa**: las respuestas correctas solo se envían al publicar resultados; orden barajado por
  participante; 4 versiones del Exp. 02; registro de salidas de pestaña (`GUIA_DOCENTE.md` §6 «Contra la copia»).
- **Exportaciones CSV** de resultados y respuestas detalladas; **reinicio** con copia de seguridad.

## Contenido del banco (esquema, sin respuestas)

Conteo hecho por script sobre `2_Aplicacion_Reto/banco_preguntas.json` (versión `18f0f539fc`):

| Medida | Valor |
|---|---|
| Misiones | 10 (`m1`, `m2`, `c1` a `c7`, `m5`) |
| Preguntas | 42; 37 con puntos; 5 sin puntos (hipótesis y fases del experimento) |
| Puntos | 1.000 exactos + bono de hasta 20 |
| Duración por defecto | 90 minutos |
| Misiones con expediente de evidencia (`dossier`) | 6; 2 se desbloquean tras registrar la hipótesis |
| Pregunta solo para el grupo B | 1 (`m1_recordatorio`) |
| Pregunta con variantes | 1 (`m2_trampas`, 4 juegos equivalentes) |

## Reglas de negocio que no se rompen

Fuente: docstring de `servidor.py`, `construir_banco.py:validar` y `aidlc/spaces/default/memory/project.md`.

1. Las respuestas correctas nunca salen al navegador hasta que el docente publica resultados.
2. El banco suma exactamente 1.000 puntos y cada clave que depende de los datos se comprueba con `exigir(...)` (29 llamadas en `construir_banco.py`).
3. Cada pregunta se responde una sola vez; la fase «¿es verdad?» del Exp. 01 exige antes «¿lo compartirías?».
4. El tiempo lo mide el servidor y la clasificación nunca empata.
5. No se cambia el banco ni el código con un reto en curso.

Ver `code-quality-assessment.md` para dos hallazgos que hoy debilitan la regla 1.

## Contexto de despliegue actual

Tres modos documentados (`2_Aplicacion_Reto/LEEME.md`, `PUBLICAR_EN_INTERNET.md`):

| Modo | Enlace | Depende del computador del docente |
|---|---|---|
| Red local (`INICIAR_RETO`) | `http://<IP>:8000` | Sí |
| Túnel temporal de Cloudflare (`INICIAR_RETO_INTERNET`) | `https://….trycloudflare.com`, cambia cada vez | Sí |
| Render con Docker y disco persistente (`render.yaml`) | `https://….onrender.com`, fijo | No; plan de pago (≈ US$7/mes según `PUBLICAR_EN_INTERNET.md`) |

La intención activa (`261024-publicar-reto-nube`) busca un enlace fijo sin depender del computador
del docente y un refactor con núcleo puro separado de la E/S. Las implicaciones técnicas están en
`architecture.md` y `code-quality-assessment.md`.

## Datos personales

La app guarda nombre, colegio, grado, integrantes y respuestas de menores de edad (`GUIA_DOCENTE.md`
§10). El repositorio debe ser privado porque `3_Guia_docente/` contiene todas las respuestas.
