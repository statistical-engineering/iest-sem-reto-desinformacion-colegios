# Plan de código — U1 `u1-cloudflare-corte`

## Summary

- Builds: el corte delgado en Cloudflare Workers (salud, salas, inscripción, comenzar, responder `opcion`, entregar) y la prueba común mínima.
- Touches: `despliegues/cloudflare/` (src, web, pruebas, wrangler.jsonc, herramientas, LEEME) y `despliegues/prueba_comun/src/prueba.py`.
- Tests: unas 20 pruebas `node:test` de las reglas, más la prueba común de 8 pasos contra `wrangler dev` y contra la versión local.

Fuentes: `../functional-design/`, `../nfr-design/`, `../infrastructure-design/`, `../decisions.md`
(ADR-W1 a ADR-W5). Este alcance no tiene historias de usuario: cada paso se traza a FR y BR.

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "team",
  "ordering": "implementamos cada capa que se pueda probar, luego escribimos y corremos sus pruebas `unittest`, y tras cada cambio en el servidor o en el banco corremos `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` hasta ver «TODO BIEN».",
  "scope": "classic",
  "test_strategy": "standard",
  "project_type": "brownfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra`, `classic` add an 80% line-coverage\n  floor and CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `express` uses the Minimal strategy: requirement-driven unit tests (one per\n  requirement, with a happy-path floor per component); existing tests remain\n  green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nBuild and Test verifies defined coverage floors and affirmed quality targets;\nthey may not be weakened to make a step pass.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Methodology evidence**: el humano eligió escribir las pruebas después del código (Q4-A); la única\n  prueba existente, `2_Aplicacion_Reto/pruebas/simulacro.py` (29 comprobaciones de extremo a extremo\n  por HTTP, según `code-quality-assessment.md`), se escribió sobre un servidor ya construido; no hay\n  rastro de pruebas escritas antes del código.\n- **Ordering**: implementamos cada capa que se pueda probar, luego escribimos y corremos sus pruebas\n  `unittest`, y tras cada cambio en el servidor o en el banco corremos\n  `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` hasta ver «TODO BIEN».\n- Cobertura (Q5-D, Q7-A): mantenemos el piso de 80 % de cobertura de líneas del alcance `classic` y\n  lo medimos en local con el módulo `trace` de la biblioteca estándar, sin paquetes nuevos. No hay\n  CI: las pruebas corren en local antes de abrir el pull request. La falta de CI es una excepción\n  explícita decidida por el humano; el 80 % no se baja para que una etapa pase.\n- Prueba de aceptación y marco de pruebas: ya fijados en `project.md` («Testing Posture»:\n  `simulacro.py` nunca se debilita; `unittest` sí, `pytest` no).\n- Las pruebas nuevas verifican una conducta, sin `if` ni `try` dentro, entran por la interfaz pública\n  y no usan *mocks* en la lógica pura (`.claude/rules/python-code.md`, «Pruebas»).\n- Antes de cada reto en vivo, la persona que lo dirige corre `PROBAR_ANTES_DEL_RETO` (`.bat` o\n  `.command`), que ejecuta el mismo simulacro (`2_Aplicacion_Reto/LEEME.md`, «Uso rápido»)."
    },
    {
      "layer": "project",
      "text": "- Prueba de aceptación: `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` debe terminar en «TODO BIEN»; nunca se debilita para que pase (fuente: `CLAUDE.md`, «Invariantes que no se rompen»).\n- Pruebas nuevas con `unittest` de la biblioteca estándar; `pytest` no está aprobado (fuente: `.claude/rules/python-code.md`)."
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:37b735ead6553d8409a9cf403032562d4ec986d949150d9eefe66703da816a1d",
  "contract_sha256": "sha256:b878c67134b15ac4e91c11d52701c7a846b04d32cfe493850f88118d378d22d8"
}
```

## Pasos

- [x] Paso 1. Estructura: `despliegues/cloudflare/wrangler.jsonc` (Worker, `assets` en `./web`, Durable Object `Reto` con `new_sqlite_classes`), `herramientas/copiar.sh` (copia `web/` y el banco a `src/banco.json`), `.gitignore` local (`.wrangler/`, `.dev.vars`). FR12.2, FR5.2.
- [x] Paso 2. Runner: comprobar `node --test` (Node 24) y anotar el comando en `unit-test-instructions.md`.
- [x] Paso 3. Datos: esquema SQLite del objeto con tablas `salas`, `colegios`, `sala_colegios`, `participantes`, `respuestas`, `eventos`, con `UNIQUE` en códigos, nombre normalizado de colegio y (participante, pregunta). Entidades de `entities.md`.
- [x] Paso 4. Pruebas de datos: unicidad de respuesta por pregunta y de inscripción repetida, desde la prueba común (pasos 4 y 6). FR2.4.
- [x] Paso 5. Lógica pura `src/reglas.js`: `validar_banco`, `examen_publico`, `opaco_de`, `traducir_opaco`, `validar_respuesta`, `fraccion` (`opcion`), `bono`, `transicion_permitida`, `hora_de_entrega`, `limpiar`, `normalizar_nombre`. BR2.2, BR4.2, BR4.3, BR5.2, BR6.1 a BR6.3.
- [x] Paso 6. Pruebas `despliegues/cloudflare/pruebas/reglas.test.js`: 5 a 8 por grupo (banco, calificación, ciclo), incluida la prueba de que `examen_publico` no trae ninguna clave secreta. U1-S1, U1-S2.
- [x] Paso 7. Acceso a datos y rutas: `src/reto.js` (clase `Reto`) y `src/worker.js`, con la tabla de rutas de `functional-spec.md` («Rutas del corte»), niveles público/token/clave, cuerpo con tope de 65.536 bytes y una sola salida de errores. BR1.1 a BR1.4, BR2.1, BR2.3, BR3.1 a BR3.4, BR4.1, BR4.4, BR5.1, BR7.1.
- [x] Paso 8. Pruebas de rutas: `despliegues/prueba_comun/src/prueba.py` (Python sin paquetes), los 8 pasos de `functional-spec.md`, contra `npx wrangler@4.148.0 dev` y contra la versión local. FR12.3.
- [x] Paso 9. Pantallas: copiar `2_Aplicacion_Reto/web/` sin cambios (commit aparte) y luego los dos cambios del corte: lista de colegios en `estudiante.js` y `?sala=` en `tablero.html`. FR4.1, FR4.2.
- [x] Paso 10. Prueba de pantallas: la prueba común pide `/`, `/tablero` y un archivo de `/static/` y comprueba 200.
- [x] Paso 11. Configuración: `CLAVE_SEMILLERO` en `.dev.vars` local (ignorado) y como secreto en la nube; el banco se comprueba al arrancar. U1-S4.
- [x] Paso 12. Documentación: `despliegues/cloudflare/LEEME.md` con los pasos para el semillero en palabras simples y `despliegues/prueba_comun/LEEME.md` con cómo correrla. FR8.0.
- [x] Paso 13. Simulacro local `python3 pruebas/simulacro.py 40` en «TODO BIEN» (la versión local no cambia).
