# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

- Trabajamos sobre un solo repositorio privado en GitHub con `main` como rama principal
  (`origin/main`). No usamos `develop` ni ramas de versión de larga vida. Las ramas llevan prefijo de
  tipo en inglés (`fix/`, `chore/`, `refactor/`, `feat/`; regla ya fijada en `project.md`).
- Estrategia: **GitHub Flow** con una rama de trabajo por intención (Q1). Primero terminamos todo el
  trabajo de la intención en su rama; al final abrimos **un solo pull request a `main`**, y solo
  cuando el reto ya está desplegado y verificado en el hosting elegido.
- Para la intención «publicar el reto en la nube», la rama de trabajo es `refactor/code-cleanup`:
  ya contiene, apiladas en línea, la normalización del `.bat` (`fix/normalizar-eol-bat`) y la
  configuración de AI-DLC (`chore/setup-aidlc`).
- Worktrees de Construcción: rama base `refactor/code-cleanup` y destino `refactor/code-cleanup`;
  cada Bolt se fusiona con **squash** (un commit por Bolt, con el nombre del Bolt). Ninguno sale de
  `main` ni vuelve a `main` directamente. La forma squash es una interpretación de Q1 (el humano no
  la nombró); vale mientras el equipo no indique otra.
- Llegada a `main` (Q2): siempre por pull request revisado por otra persona del semillero; nadie
  fusiona su propio PR sin esa revisión.
- Mensajes de commit (Q2): `tipo: descripción`, con el tipo en inglés y la descripción en español
  (por ejemplo, «fix: corregir fuga del veredicto antes de resultados»).
- Al refactorizar o migrar no cambiamos el diseño ni la lógica de negocio (Q1). Eso cubre la
  conducta visible (Q8): pantallas, preguntas, puntajes, desempates y flujo de estados quedan igual.
  Corregir una fuga de respuestas antes de «resultados» sí se permite, porque cumple un invariante
  que ya existe.
- `CLAUDE.md`, `.claude/` y `.worktreeinclude` son locales (excluidos en `.git/info/exclude`); el
  árbol `aidlc/` sí se versiona.
- Nadie cambia el banco ni el código con un reto en curso (regla ya en `project.md`, «Forbidden»).

## Walking Skeleton

- Sí construimos primero un corte delgado de extremo a extremo (Q3), aunque el alcance `classic`
  declara `skeleton: off`: el riesgo de esta intención (cambiar de hosting y separar el núcleo puro
  de la E/S a la vez) lo justifica.
- El primer corte es una versión mínima desplegada en el hosting elegido que deja inscribirse y
  responder una pregunta, antes de migrar todo lo demás.
- Lo damos por bueno cuando se cumplen las dos comprobaciones:
  - `python3 pruebas/simulacro.py 40`, corrido desde `2_Aplicacion_Reto/`, termina en «TODO BIEN».
  - El chequeo de salud `GET /api/publico` responde bien en el hosting elegido.
- Después del corte verificado, el humano aprueba el punto de control antes de seguir con las demás
  unidades.

## Testing Posture

- **Methodology**: test-after
- **Methodology evidence**: el humano eligió escribir las pruebas después del código (Q4-A); la única
  prueba existente, `2_Aplicacion_Reto/pruebas/simulacro.py` (29 comprobaciones de extremo a extremo
  por HTTP, según `code-quality-assessment.md`), se escribió sobre un servidor ya construido; no hay
  rastro de pruebas escritas antes del código.
- **Ordering**: implementamos cada capa que se pueda probar, luego escribimos y corremos sus pruebas
  `unittest`, y tras cada cambio en el servidor o en el banco corremos
  `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` hasta ver «TODO BIEN».
- Cobertura (Q5-D, Q7-A): mantenemos el piso de 80 % de cobertura de líneas del alcance `classic` y
  lo medimos en local con el módulo `trace` de la biblioteca estándar, sin paquetes nuevos. No hay
  CI: las pruebas corren en local antes de abrir el pull request. La falta de CI es una excepción
  explícita decidida por el humano; el 80 % no se baja para que una etapa pase.
- Prueba de aceptación y marco de pruebas: ya fijados en `project.md` («Testing Posture»:
  `simulacro.py` nunca se debilita; `unittest` sí, `pytest` no).
- Las pruebas nuevas verifican una conducta, sin `if` ni `try` dentro, entran por la interfaz pública
  y no usan *mocks* en la lógica pura (`.claude/rules/python-code.md`, «Pruebas»).
- Antes de cada reto en vivo, la persona que lo dirige corre `PROBAR_ANTES_DEL_RETO` (`.bat` o
  `.command`), que ejecuta el mismo simulacro (`2_Aplicacion_Reto/LEEME.md`, «Uso rápido»).

## Guard Policy

<!-- Affirmed by the team. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless project.md or the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

- Desplegamos **a mano** (Q6): el docente o el semillero lanza el despliegue solo cuando no hay un
  reto en curso. El hosting no despliega solo al fusionar ni al subir cambios.
- Volver atrás es redesplegar la versión anterior. No tenemos un entorno de ensayo en la nube aparte:
  ensayamos en local con el simulacro y con `modo_prueba.py`.
- Siempre corre una sola instancia, porque el reloj y la clasificación viven en memoria (ya en
  `project.md`, «Deployment»).

Entornos que existen hoy:

| Entorno | Para qué | Cómo se levanta | Datos |
|---|---|---|---|
| Simulacro | Prueba automática | `pruebas/simulacro.py`, puerto 8765 | BD temporal |
| Modo prueba | Ensayo manual | `modo_prueba.py`, puerto 8010 | `datos_prueba/` |
| Red local | Reto en el aula, misma wifi | `INICIAR_RETO`, puerto 8000 | `datos/reto.db` |
| Túnel temporal | Reto desde otra red, solo por hoy | `INICIAR_RETO_INTERNET` (`cloudflared`) | `datos/reto.db` |
| Render | Reto con enlace fijo | Blueprint de `render.yaml`, Docker | Disco de 1 GB en `/data` |

- Prueba de humo tras cada despliegue (`PUBLICAR_EN_INTERNET.md`, «Antes del reto»): el hosting
  vigila `GET /api/publico` como chequeo de salud (`render.yaml`); luego abrimos el enlace con datos
  móviles, hacemos una inscripción de prueba y después «Reiniciar» (pide escribir BORRAR).
- Respaldo de datos: «Reiniciar» guarda una copia de la BD (`VACUUM INTO`) y al terminar se descargan
  los CSV desde el panel docente.

## Code Style

- Código, identificadores, docstrings, mensajes y `.md` en español; las reglas completas ya están en
  `project.md` («Code Style») y en `.claude/rules/python-code.md` y `.claude/rules/markdown-docs.md`.
- No adoptamos linter ni formateador (Q5-D): no se instala ningún paquete de desarrollo. La
  complejidad ciclomática máxima de 10 y el resto del estilo se revisan a mano en el pull request.
- JavaScript sin dependencias ni build: módulos IIFE con `"use strict"` y un helper `h()` que crea el
  DOM con `textContent` (`code-structure.md`, «Patrones de código»).
- Lanzadores: cada `.bat` tiene su gemelo `.command`; `.bat` en ASCII con fin de línea CRLF y
  `.command` con LF y ejecutable (`.gitattributes`, `.claude/rules/launchers.md`).
- Formato numérico de Colombia (`2.980`, `79,4 %`) y comillas «…» en toda la documentación
  (`.claude/rules/markdown-docs.md`).
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
- ALWAYS seguir el flujo de ramas refactor/code-cleanup → PR a develop (creada desde main; los despliegues de prueba salen de develop) → PR final revisado a main, de donde sale el despliegue definitivo; todo paso a develop va por PR para dejar trazabilidad y no se hace push a main hasta tener la versión final. Reemplaza la línea «No usamos develop» de Way of Working (fuente: decisión del humano en Requirements Analysis, 2026-10-24). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:requirements-analysis:c8031bdb84b40b38cf419324025d21c9a312eb43664f26da993f8e088a5e7d72 -->
- ALWAYS mantener cada PR en máximo 400 líneas de código cambiadas (añadidas + borradas); no cuentan archivos generados, documentación .md ni registros de aidlc/; si un cambio no cabe, se divide en varios PR (fuente: decisión del humano, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:requirements-analysis:557c11fcb22585998b4ba1b142243cfb25cf3bdefb5f8e244c02b438d8296dc2 -->
- ALWAYS escribir los commits como «tipo(alcance opcional): descripción», con tipo en inglés de la lista cerrada (feat, fix, refactor, chore, docs, test, perf, build, ci, style, revert), descripción en español que empieza en minúscula con un verbo en infinitivo, sin punto final y líneas de máximo 72 caracteres; lo revisan pre-commit y la revisión de PR en GitHub. Esa revisión (.github/workflows/revisar-pr.yml) es la única CI aprobada: corre los ganchos, el simulacro y el límite de 400 líneas, sin pruebas extra ni despliegue (fuente: decisión del humano, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:requirements-analysis:1fa0b16ba4e25d3a22055c29380e41f5dbfe8ef2f76934cd740b8777232678a3 -->
- ALWAYS, como regla general de ramas, hacer cada cambio en su propia rama de trabajo con prefijo de tipo (feat/, fix/, refactor/, chore/…) creada desde develop y llevarla a develop por PR; se repite rama por rama hasta la versión final, y solo entonces un PR revisado de develop a main. Generaliza la regla anterior que nombraba solo refactor/code-cleanup y reemplaza en Way of Working la rama única por intención y la base/destino refactor/code-cleanup de los worktrees, que pasan a ser develop (fuente: decisión del humano, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:requirements-analysis:eb6737f9cbe087cb17152d5e170a0d520e49b747576bc4b07bb3ba73e0ab8ff5 -->
- ALWAYS formatear y revisar el Python con ruff (versión fijada en el grupo dev de pyproject.toml y en .pre-commit-config.yaml, reglas en [tool.ruff]); reemplaza en «Code Style» la línea «No adoptamos linter ni formateador (Q5-D)»; el código anterior entra archivo por archivo al tocarse (fuente: decisión del humano, 2026-10-25, reabre Q5-D). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:domain-design:d924fbb2d154a9735e5ee2ed4b31314f21c117c2db699bfc7009981319318414 -->
- ALWAYS tratar como exento del límite de 400 líneas un PR o commit «style:» que solo toca archivos .py sin cambiar su árbol sintáctico (lo comprueba .github/workflows/revisar-pr.yml); se prueba con ruff format --check, la suite unittest y el simulacro en «TODO BIEN», y su commit se anota en .git-blame-ignore-revs (fuente: decisión del humano, 2026-10-25, ADR-008). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:domain-design:b6e90b094dd8ed7dd5487a444dcf933112afc1e3d5641be57fc976fbe149950b -->
