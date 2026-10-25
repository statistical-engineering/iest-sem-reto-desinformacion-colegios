# Evidencia de Practices Discovery

- Proyecto: brownfield, alcance `classic`, profundidad Standard, colaboradores desactivados (ejecución
  solo con el lead `aidlc-pipeline-deploy-agent`; no hay archivos de contribución).
- Commit inspeccionado: `99462c96268e29bde1738af0b4817d96df9a3989` (rama `refactor/code-cleanup`).
- No se ejecutó ninguna prueba, build ni programa del proyecto; solo lecturas y comandos de git de
  consulta.
- Participantes: el lead redactó el borrador (Paso 2) y lo integró (Paso 5); el humano respondió la
  entrevista de 8 preguntas en `practices-discovery-questions.md` (Paso 4). No hubo revisión de
  colaboradores (Paso 3 omitido por `collaborators: off`).

## Qué se inspeccionó

### Historial y configuración de git

| Fuente | Qué se miró | Qué dice |
|---|---|---|
| `git log --all` (5 commits) | Autores, mensajes, fechas | 3 commits de `MarcoCardenas2807` directos en `main` («Primera version», 2 × «Add files via upload», 19 y 22 de octubre); 2 de Juan Sebastian Ramirez Ayala en ramas locales («Normalizar fin de línea de INICIAR_RETO_INTERNET.bat», «chore: set up AI-DLC», 23 de octubre) |
| `git branch -a -vv` | Ramas | `main` sigue a `origin/main` en `92393dc`; `fix/normalizar-eol-bat` (`d32d228`), `chore/setup-aidlc` y `refactor/code-cleanup` (ambas en `99462c9`) son locales, apiladas en línea y sin subir; no hay ramas remotas aparte de `main` |
| `git show --stat` de los 4 últimos commits | Alcance de cada commit | Commits pequeños de un solo tema; sin commits de fusión |
| `git ls-files` sobre `CLAUDE.md`, `.claude`, `aidlc`, `.github` | Qué se versiona | Se versiona solo `aidlc/spaces/default/memory/**`; no hay `.github/` (sin CI) |
| `.git/info/exclude` | Exclusiones locales | `/CLAUDE.md`, `/CLAUDE.local.md`, `/.claude`, `/.worktreeinclude` excluidos solo en esta copia |
| `git status` y `git diff --stat` | Árbol de trabajo | `2_Aplicacion_Reto/INICIAR_RETO_INTERNET.bat` modificado (26 líneas cambiadas, mismo texto) pese al commit `d32d228` que normalizó su fin de línea |

### Archivos del repositorio

| Archivo | Para qué se leyó |
|---|---|
| `.gitignore` | Datos locales (`datos/`, `datos_prueba/`) fuera de git; bloque de AI-DLC; `.herramientas/` no aparece |
| `.gitattributes` | `*.bat` CRLF, `*.command` LF, `*.png` y `*.db` binarios |
| `.worktreeinclude` | Archivos locales que se copian a los worktrees de Claude Code |
| `render.yaml` | Servicio `docker`, plan `0.5c-512mb`, `healthCheckPath: /api/publico`, disco de 1 GB en `/data`, `RETO_CLAVE` con `sync: false`; no fija rama ni despliegue automático |
| `2_Aplicacion_Reto/Dockerfile` y `.dockerignore` | Imagen `python:3.12-slim`, `RETO_HOSTING=1`, `RETO_DATOS=/data`; la imagen excluye lanzadores y datos |
| `PUBLICAR_EN_INTERNET.md` | Flujo de publicación con GitHub Desktop y Render Blueprint; prueba de humo «Antes del reto»; eliminar el servicio «Después del reto» |
| `2_Aplicacion_Reto/LEEME.md` | `PROBAR_ANTES_DEL_RETO` y `simulacro.py 40`; prueba de carga de 60 estudiantes documentada; pasos para modificar preguntas |
| `CLAUDE.md` | Invariantes, fuente de verdad, dependencias, publicación, reglas para asistentes y gotchas |
| `.claude/rules/python-code.md` | Estilo de Python, `unittest` sí y `pytest` no, sin linter instalado |
| `.claude/rules/markdown-docs.md` | Idioma, formato numérico, confidencialidad de respuestas |
| `.claude/rules/generated-artifacts.md` | Archivos generados y orden de regeneración |
| `.claude/rules/launchers.md` | Gemelos `.bat`/`.command`, CRLF/LF, `.bat` en ASCII |
| `.claude/rules/document-review.md` | Fuente de verdad y estándar de revisión de documentos |
| `.claude/scopes/aidlc-classic.md` | `skeleton: off`, `collaborators: off` |
| `aidlc/spaces/default/intents/261024-publicar-reto-nube/aidlc-state.md` | Brownfield, alcance `classic`, `ci-pipeline` y toda la fase de Operación en SKIP |

### Base de conocimiento del código (reverse engineering)

| Artefacto | Ruta | Qué aportó a las prácticas |
|---|---|---|
| code-structure | `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/code-structure.md` | Patrones de código (Python con estado global, JS IIFE sin build, despacho por tabla en el cliente), idioma de identificadores |
| technology-stack | `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/technology-stack.md` | Modos de ejecución (red local, túnel, Render, simulacro, modo prueba); sin formateador, linter, tipos ni CI |
| dependencies | `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/dependencies.md` | App sin paquetes de terceros; pandas, numpy y matplotlib sin fijar; contratos que el simulacro y `render.yaml` esperan del servidor |
| code-quality-assessment | `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/code-quality-assessment.md` | Simulacro con 29 comprobaciones y ninguna prueba unitaria; sin cobertura ni CI; el piso de 80 % y CI del alcance `classic` no tiene hoy infraestructura |
| architecture | `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/architecture.md` | Una sola instancia por `RLock`, vigilante y SQLite de proceso; estado que sobrevive a un reinicio |
| business-overview | `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/business-overview.md` | Tres modos de despliegue y su dependencia del computador del docente; datos de menores; repositorio privado |

### Memoria del espacio

| Archivo | Estado | Uso en el borrador |
|---|---|---|
| `aidlc/spaces/default/memory/team.md` | Todas las secciones vacías | No hay línea base afirmada: no es una re-ejecución |
| `aidlc/spaces/default/memory/project.md` | Reglas del proyecto sembradas el 2026-10-23 | Se refieren en `team-practices.md`; no se duplican ni contradicen en `discovered-rules.md` |
| `aidlc/spaces/default/memory/org.md` | Valores por defecto del framework | Respaldo para rama base `main` con squash, test-after y piso de 80 % con CI del alcance `classic` |

## Qué se infirió (borrador, antes de la entrevista)

| Área | Inferencia | Base | Certeza |
|---|---|---|---|
| Ramas | Trunk-based / GitHub Flow sobre `main`, con ramas cortas de prefijo en inglés; aún sin fusionar las tres ramas locales | `git branch`, `project.md` | Media: el patrón de fusión no se ha observado nunca |
| Colaboración | Al menos dos personas: una sube directo a `main` por la web; otra trabaja en ramas locales | `git log` | Alta para los hechos; la intención futura no se sabe |
| Revisión | No hay evidencia de pull requests ni de revisión antes de fusionar | Historia sin commits de fusión | Baja (solo se miró la historia local) |
| Mensajes de commit | Sin convención única | `git log` | Alta |
| Esqueleto | Por defecto no (`skeleton: off` del alcance) | `aidlc-classic.md` | Alta para el valor por defecto; la conveniencia para esta intención es juicio del equipo |
| Metodología de pruebas | test-after | Solo existe una prueba de aceptación escrita sobre código hecho; `org.md` | Media |
| Cobertura y CI | No existen; el alcance `classic` los exige antes de fusionar | `technology-stack.md`, `code-quality-assessment.md`, `org.md` | Alta |
| Despliegue | Manual y por evento (crear antes del reto, borrar después); producción sin entorno de ensayo en la nube; ensayo local con simulacro y modo prueba | `PUBLICAR_EN_INTERNET.md`, `render.yaml` | Alta |
| Vuelta atrás | No documentada; los datos se respaldan con `VACUUM INTO` al reiniciar y con los CSV | `PUBLICAR_EN_INTERNET.md`, `architecture.md` | Alta para la ausencia |
| Estilo | Español en todo, sin herramienta de formato ni lint; reglas escritas en `.claude/rules/` | `technology-stack.md`, reglas | Alta |

### Tensiones del borrador y cómo quedaron

| Tensión | Resolución | Pregunta |
|---|---|---|
| Rama base de los worktrees: `main` no contiene la normalización del `.bat` ni la configuración de AI-DLC | Los worktrees salen de `refactor/code-cleanup` y vuelven a ella; `main` solo recibe el PR final | Q1 |
| Piso de 80 % de cobertura y CI del alcance `classic` sin herramienta ni CI | Se mantiene el 80 %, medido en local con `trace`; la falta de CI queda como excepción explícita del humano | Q5, Q7 |
| Despliegue automático frente a «no cambiar el código con un reto en curso» | Despliegue a mano, solo sin reto en curso; volver atrás = redesplegar la versión anterior | Q6 |
| Subidas directas a `main` durante una rama larga | Todo llega a `main` por un PR revisado por otra persona del semillero | Q2 |
| Fuga de `por_publicacion[].verdad` en `/api/publico` en estado «cerrado» (`servidor.py:433-434`) frente a «no cambiar la lógica de negocio» | La regla cubre la conducta visible; corregir la fuga sí se permite porque cumple un invariante existente | Q8 |

## Decisiones de la entrevista

Fuente: `practices-discovery-questions.md` (misma carpeta), respuestas en las líneas `[Answer]:`.

| Pregunta | Tema | Respuesta | Dónde quedó |
|---|---|---|---|
| Q1 | Rama base y forma de fusión | `X` (texto libre, citado abajo) | `team-practices.md`, «Way of Working»; `discovered-rules.md`, primera regla de «Mandated» y la de «Forbidden» |
| Q2 | Revisión y mensajes de commit | `A`: PR revisado por otra persona del semillero; mensajes `tipo: descripción` (tipo en inglés, descripción en español) | «Way of Working»; segunda regla de «Mandated» |
| Q3 | Corte delgado primero | `A`: sí, desplegado y verificado con `simulacro.py 40` y el chequeo de salud | «Walking Skeleton» |
| Q4 | Orden de las pruebas | `A`: después del código (test-after), simulacro tras cada cambio del servidor | «Testing Posture» (`Methodology`, `Ordering`) |
| Q5 | Cobertura, lint y CI | `D`: sin CI; pruebas en local antes de fusionar | «Testing Posture», «Code Style» |
| Q6 | Disparador del despliegue | `A`: a mano y sin reto en curso; volver atrás = redesplegar la versión anterior | «Deployment»; tercera regla de «Mandated» |
| Q7 | Seguimiento de Q5 frente al piso del alcance | `A`: sin CI, pero el 80 % se mide en local con `trace`; la falta de CI queda como excepción del humano | «Testing Posture» |
| Q8 | Alcance de «no cambiar el diseño ni la lógica de negocio» | `A`: cubre la conducta visible; corregir fugas de respuestas antes de «resultados» sí se permite | «Way of Working»; regla de «Forbidden» |

Respuesta literal de Q1:

> X. primero terminamos todo, y después hacemos un PR a main, pero la condicion es que debe de estar desplegado, regla importante es que no debemos de cambiar nada del diseñño o logica de negocio.

Cómo se interpretó Q1 (interpretación del lead, no palabras del humano):

- «Primero terminamos todo»: el trabajo de la intención se hace entero en la rama actual
  `refactor/code-cleanup`, que ya contiene `fix/normalizar-eol-bat` y `chore/setup-aidlc`.
- «Después hacemos un PR a main»: un único pull request de `refactor/code-cleanup` a `main` al final.
- «Debe de estar desplegado»: el PR se abre solo con el reto desplegado y verificado en el hosting
  elegido.
- Worktrees de Construcción: base y destino `refactor/code-cleanup`. La forma de fusión por Bolt
  (**squash**, un commit por Bolt) no la dijo el humano: es el valor por defecto de `org.md` aplicado
  a la nueva rama destino y puede cambiarse en la aprobación.
- «No debemos de cambiar nada del diseño o lógica de negocio»: se precisó con Q8.

### Reglas candidatas del borrador

Las 5 candidatas del borrador se conservan en `discovered-rules.md`: las cinco son restricciones que
el humano escribió como obligatorias en `CLAUDE.md` («Invariantes que no se rompen», «Fuente de
verdad», «Convenciones de idioma y código», «Gotchas») y ninguna está todavía en `project.md`.

## Incertidumbre que queda

- **Desplegar antes de fusionar.** Como el PR a `main` se abre solo con el reto desplegado, el
  hosting tiene que desplegar desde `refactor/code-cleanup` (o desde una copia local), no desde
  `main`. Falta decidir en etapas posteriores desde qué rama despliega el hosting antes y después del
  PR, y cómo se apaga el despliegue automático para cumplir «a mano».
- **Comprobación del corte delgado en el hosting.** `simulacro.py` levanta su propio servidor
  temporal en el puerto 8765 con una BD aparte: comprueba el código, no la instancia desplegada. En
  el hosting la comprobación es `GET /api/publico` más la prueba de humo de `PUBLICAR_EN_INTERNET.md`.
  Si se quiere correr el simulacro contra la URL desplegada, hace falta decidirlo en el diseño.
- **Alcance de la medición con `trace`.** No se fijó sobre qué módulos se mide el 80 % (núcleo puro
  nuevo, `servidor.py` entero o todo `2_Aplicacion_Reto/`) ni el comando exacto; lo concreta Code
  Generation o Build and Test, sin bajar el 80 %.
- **`skeleton: off` del alcance frente a Q3.** El alcance `classic` declara `skeleton: off`; el
  equipo eligió el corte delgado. El orquestador tiene que reflejar esa elección al entrar a
  Construcción.
- **Hosting elegido.** Todavía no está decidido (puede seguir siendo Render u otro); las prácticas
  de despliegue valen para cualquiera de ellos.
- No se consultó GitHub (`gh`), así que no se sabe si hay pull requests, protección de rama o
  colaboradores configurados en el repositorio remoto. La revisión por otra persona del semillero
  (Q2) es una práctica acordada; no se comprobó si está forzada en GitHub.
- No se verificó en la documentación oficial de Render qué rama despliega un Blueprint ni si despliega
  solo al subir cambios cuando `render.yaml` no lo dice; eso corresponde a etapas posteriores.
- No se sabe por qué `INICIAR_RETO_INTERNET.bat` vuelve a aparecer modificado en el árbol de trabajo
  después de `d32d228`.
