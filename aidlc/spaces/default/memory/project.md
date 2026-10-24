# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

- Reto escolar de 90 minutos («Detectives de la desinformación»); fuente única de verdad de los datos: `4_Codigo_y_datos/datos_originales/` (fuente: `CLAUDE.md`, «Fuente de verdad»).
- Archivos generados (`2_Aplicacion_Reto/banco_preguntas.json`, `3_Guia_docente/CLAVE_DE_RESPUESTAS.md`, `1_Analisis_de_datos/**`) no se editan a mano: se cambia el script de `4_Codigo_y_datos/scripts/` y se regenera (fuente: `.claude/rules/generated-artifacts.md`).
- Ramas con prefijo de tipo en inglés (`refactor/`, `chore/`, `fix/`); `CLAUDE.md` y `.claude/` no se versionan (fuente: decisión del usuario, 2026-10-23).

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

- Prueba de aceptación: `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` debe terminar en «TODO BIEN»; nunca se debilita para que pase (fuente: `CLAUDE.md`, «Invariantes que no se rompen»).
- Pruebas nuevas con `unittest` de la biblioteca estándar; `pytest` no está aprobado (fuente: `.claude/rules/python-code.md`).

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

<!-- Project-specific specialisation. -->

- Hoy: red local (`servidor.py`), túnel temporal de Cloudflare (`iniciar_internet.py`) o Render con Docker y disco en `/data` (`render.yaml`). Una sola instancia: reloj y clasificación viven en memoria (fuente: `PUBLICAR_EN_INTERNET.md`).
- El repositorio debe ser privado: `3_Guia_docente/` contiene todas las respuestas.

## Code Style

<!-- Project-specific specialisation. -->

- Código, identificadores, docstrings y `.md` en español; sin tildes ni `ñ` en identificadores; no se renombran claves JSON ni rutas HTTP que usa `web/js/` (fuente: `.claude/rules/python-code.md`, decisión del usuario 2026-10-23).
- Reglas completas: `.claude/rules/python-code.md` (núcleo funcional con E/S en los bordes, sin abstracción prematura, docstrings estilo Google en vez de `#`, excepciones concretas con `from`) y `.claude/rules/markdown-docs.md` (formato numérico 2.980 y 79,4 %).

## Tech Stack

<!-- Technology choices locked for this project. -->

- App: solo biblioteca estándar de Python 3.9+ y SQLite, HTML/CSS/JS sin frameworks ni build (fuente: `2_Aplicacion_Reto/LEEME.md`, `servidor.py`).
- Scripts de datos: pandas, numpy, matplotlib. Agregar dependencias requiere aprobación del usuario.

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

NEVER enviar las respuestas correctas al navegador antes de que el docente publique resultados (fuente: docstring de `servidor.py`).
NEVER cambiar el banco ni el código con un reto en curso (fuente: `2_Aplicacion_Reto/LEEME.md`).
NEVER escribir claves docentes reales ni datos de `2_Aplicacion_Reto/datos/` en archivos versionados.

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

ALWAYS mantener el banco en exactamente 1.000 puntos y cada clave de datos comprobada con `exigir(...)` (fuente: `construir_banco.py`).
ALWAYS medir el tiempo en el servidor y mantener la clasificación como orden total sin empates (fuente: docstring de `servidor.py`).

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
