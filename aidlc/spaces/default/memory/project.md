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

NEVER cambiar la conducta visible del reto (pantallas, preguntas, puntajes, desempates ni flujo de estados) al refactorizar o migrar; corregir fugas de respuestas antes de «resultados» sí se permite (fuente: entrevista Q1 y Q8). (affirmed 2026-10-24)

NEVER editar `4_Codigo_y_datos/datos_originales/`, la única fuente de verdad de los datos (fuente: `CLAUDE.md`, «Fuente de verdad»). (affirmed 2026-10-24)

NEVER poner respuestas del reto en material para estudiantes (fuente: `CLAUDE.md`, «Convenciones de idioma y código»; `.claude/rules/markdown-docs.md`, «Confidencialidad»). (affirmed 2026-10-24)

NEVER versionar `2_Aplicacion_Reto/.herramientas/`, donde queda el binario de `cloudflared` (fuente: `CLAUDE.md`, «Gotchas»). (affirmed 2026-10-24)

## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

ALWAYS mantener el banco en exactamente 1.000 puntos y cada clave de datos comprobada con `exigir(...)` (fuente: `construir_banco.py`).
ALWAYS medir el tiempo en el servidor y mantener la clasificación como orden total sin empates (fuente: docstring de `servidor.py`).

ALWAYS abrir el pull request a `main` solo cuando todo el trabajo esté terminado y el reto esté desplegado y verificado en el hosting elegido (fuente: entrevista Q1). (affirmed 2026-10-24)

ALWAYS fusionar a `main` por pull request revisado por otra persona del semillero (fuente: entrevista Q2). (affirmed 2026-10-24)

ALWAYS desplegar a mano y solo cuando no haya un reto en curso (fuente: entrevista Q6). (affirmed 2026-10-24)

ALWAYS aceptar una sola respuesta por pregunta y participante (fuente: `CLAUDE.md`, «Invariantes que no se rompen»). (affirmed 2026-10-24)

ALWAYS reiniciar el servidor después de regenerar el banco (fuente: `CLAUDE.md`, «Invariantes que no se rompen»). (affirmed 2026-10-24)

## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
- ALWAYS al elegir cómo publicar el reto, evaluar todas las opciones razonables, incluidas las que proponga el equipo (por ejemplo GitHub Pages), y entre las que cumplen todos los requisitos elegir la más parsimoniosa: menos piezas, servicios y cambios de código (fuente: nota del humano en Requirements Analysis, Tradeoff). (learned 2026-10-24) <!-- cid:261024-publicar-reto-nube:requirements-analysis:b8492e53143eb8c77bf3f5d03bc43a0e4447da12a7218f17e45a4cd823968727 -->
- ALWAYS manejar las dependencias con uv (pyproject.toml declara, uv.lock fija versiones, Python 3.12); la app puede tener dependencias y esto reemplaza en «Tech Stack» la línea «App: solo biblioteca estándar de Python 3.9+»; cada paquete nuevo requiere aprobación del humano; los scripts de datos usan el grupo datos con pandas<3 porque pandas 3 rompe generar_analisis.py (fuente: decisión del humano, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:requirements-analysis:ccb892a2d2ef34ca50d05696616e8e8621a6229c4111983817d49e7ce536b61f -->
- ALWAYS tratar el repositorio como público (decisión del humano, 2026-10-25, riesgo aceptado): reemplaza en «Deployment» la regla «El repositorio debe ser privado»; 3_Guia_docente/ y banco_preguntas.json quedan visibles en internet, así que nunca se versionan claves docentes ni datos de participantes. (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:requirements-analysis:0bcf47213f839a50d767faed53a1d8818e2fe6d63c9c6ea3ced38a517d162859 -->
- ALWAYS dejar la arquitectura y los patrones de diseño en los ADR de cada intención (aidlc/spaces/default/intents/<intención>/…/decisions.md); las reglas .claude/rules/<lenguaje>-code.md solo fijan convenciones del lenguaje comprobables con herramienta o leyendo el archivo. Reemplaza en «Code Style» el paréntesis «(núcleo funcional con E/S en los bordes, sin abstracción prematura, …)» (fuente: decisión del humano, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:domain-design:85e55c9776c50b9d1e792ea30c22090ca560e224ec98f03409073426c1d2ae06 -->
- ALWAYS partir cada opción gratuita de hosting en 4 unidades por capa (corte delgado, reglas, salas y catálogo, resultados y exportación) y dejar las opciones de pago como unidades de solo documentación mientras no se apruebe su costo (fuente: decisión del humano en Units Generation, Q1-A y Q2-A, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:units-generation:da710df59993543186488a198560a4e17a9600965dcd7c600ba54af8d39775fa -->
- NEVER aceptar la clave docente ni la del semillero en la URL (?clave=) en las versiones de la nube; solo por la cabecera X-Clave-Admin, porque la URL queda en los registros del hosting (fuente: Contract Design, ADR-005 y FR9.5, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:contract-design:67c24e2c16fa20f8d52c840a4652b88f8b8a15e269b1126da4126431a4f8b5a0 -->
- ALWAYS, en las versiones de la nube, responder GET /api/publico sin ?sala= solo con {"ok": true}: es el chequeo de salud y no muestra ninguna sala; el tablero pasa la sala que lee de su URL (fuente: Contract Design, FR11.4, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:contract-design:af7e2db207d3d87bb13677257d146d6be163886aaa1d1317a912790779828c04 -->
- ALWAYS compartir entre opciones de hosting solo datos, como la tabla despliegues/prueba_comun/casos_reglas.json que cada opción copia a sus pruebas, nunca código, para cumplir FR12.2 (fuente: Contract Design, Q6-A, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:contract-design:7e97faaeddb4c1121e94d40aaa06516f5355466dda3b81392ff77eacfa7a9304 -->
- ALWAYS, cuando una opción de hosting no pasa (por contrato o por su corte), saltar sus unidades con aprobación del humano en vez de borrarlas, para que la comparación (U17) la anote como «no pasa» con el motivo (fuente: Delivery Planning, Q2-A, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:delivery-planning:48ba38595aac117910d0cfba304cd2ecad1f850ed4160ca29211bc940c9d588f -->
- ALWAYS elegir el comando de verificación de Construcción en el punto de control del corte delgado, cuando la prueba común que lo hace real ya existe (fuente: Delivery Planning, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:delivery-planning:42e1515c401378845370d1aa7b19ede55b0a55a27624afc9978b225a3d4ac2cb -->
- ALWAYS ordenar los Bolts por riesgo, sin puntaje formal tipo WSJF, mientras la meta sea elegir la opción de hosting que pasa todo (fuente: Delivery Planning, Q1-A, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:delivery-planning:3bd7875d86564c06c5a193f490c03bc82817581d5fe4a49559dd3b5a873bcd5f -->
- ALWAYS, en las opciones de hosting con Node, correr las pruebas nombrando el archivo (node --test <archivo>), porque node --test con una carpeta falla en Node 24 (fuente: Code Generation de U1, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:code-generation:894a31893516d1b8c1749d1b2be8f8590c492ad4936e4a24e715f9060a86fd32 -->
- ALWAYS comprobar en cada opción de hosting la copia del banco con una huella propia (sha256 del JSON), porque la version de Python no se puede recalcular en JS (fuente: Code Generation de U1, 2026-10-25). (learned 2026-10-25) <!-- cid:261024-publicar-reto-nube:code-generation:e29485c12804a561530e4e5aae2a88c4d098709bbf8cf72da47a0a1269093093 -->
- ALWAYS, con una sola sala, responder GET /api/publico sin parámetros con lo que necesita el tablero; esa misma ruta es el chequeo de salud. Reemplaza la regla «GET /api/publico sin ?sala= solo con {"ok": true}», que era para varias salas (fuente: revisión a una sola sala, ADR-011, 2026-10-25). (learned 2026-10-26) <!-- cid:261024-publicar-reto-nube:domain-design:57f1cde7235a47ef57b4fdb7fbaa526fd34b19197a18135cb13b62857afc48f7 -->
