# Plan de código — U17 `u17-comparacion`

## Summary

- Builds: `despliegues/COMPARACION.md` con Cloudflare medida (dos corridas, ADR-C5) y las otras cuatro opciones con su motivo; el ADR final (ADR-C3) en `decisions.md`; `despliegues/cloudflare/LEEME.md` para una sala y Windows con Git Bash; `PUBLICAR_EN_INTERNET.md` reescrito para Cloudflare.
- Touches: `despliegues/COMPARACION.md`, `aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u17-comparacion/decisions.md`, `despliegues/cloudflare/LEEME.md`, `.gitattributes`, `PUBLICAR_EN_INTERNET.md` y, tras la aprobación, el borrado de cuatro carpetas de `despliegues/`.
- Tests: comprobaciones estructurales: `revisar_comparacion.py` sobre las cinco columnas, su suite `unittest`, conteo de palabras por frase, `grep` de claves y el simulacro local en «TODO BIEN». Sin código nuevo.

Fuentes: `../functional-design/` (F1 a F10, BR17.1 a BR17.13), `../nfr-requirements/`, `../nfr-design/`,
`../infrastructure-design/` (todas con la revisión del 2026-10-27, una sola sala) y `../decisions.md`
(ADR-C1 a ADR-C6). Este alcance no tiene historias de usuario: cada paso se traza a FR, NFR y BR.

Regla de toda la unidad: cada cifra sale de un archivo de `despliegues/prueba_comun/mediciones/`, de una
URL oficial con su fecha de consulta o de un comando anotado con su commit. Si falta la fuente, la casilla
dice «sin medir» o «sin evidencia» y Cloudflare no pasa (BR17.1, BR17.2). Ningún archivo lleva claves
reales, respuestas del banco ni datos de participantes (BR17.11).

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
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default.",
    "unit_adaptation": [
      "Unidad de tipo spec: no agrega código de producción ni pruebas nuevas; las capas de datos, acceso, lógica, API y pantallas no aplican.",
      "Las pruebas de la unidad son comprobaciones estructurales repetibles: cada casilla con cifra trae un archivo de mediciones entre comillas invertidas, una URL oficial o un comando (revisar_comparacion.py y su suite unittest).",
      "Toda cifra de COMPARACION.md, del ADR final y de las guías se traza a despliegues/prueba_comun/mediciones/*.json o a una URL oficial con fecha de consulta; nunca se escribe de memoria.",
      "La suite existente sigue verde: simulacro.py 40 en «TODO BIEN» y git diff vacío sobre 2_Aplicacion_Reto/ (FR12.1)."
    ]
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Verify the existing test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Documentation structure (tabla, ADR, guías)"
    ],
    "steps": [
      "Verify the inputs exist (U6 done, two Cloudflare measurements) and record the exact check commands.",
      "Documentation structure - write the comparison table and verdict blocks.",
      "Documentation structure - run the structural checks after writing.",
      "Final ADR, Cloudflare LEEME and publishing guide after human approval.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:37b735ead6553d8409a9cf403032562d4ec986d949150d9eefe66703da816a1d",
  "contract_sha256": "sha256:b878c67134b15ac4e91c11d52701c7a846b04d32cfe493850f88118d378d22d8"
}
```

## Pasos

- [ ] Paso 1. Entradas (F1, BR17.8): confirmar que U6 está terminada y que existen `despliegues/prueba_comun/mediciones/cloudflare_<AAAA-MM-DD>.json` y `cloudflare-dev_<AAAA-MM-DD>.json`, cada uno con `version_esquema: 1` y `todo_bien: true`. Si falta algo, U17 se detiene: la tabla nunca se llena a medias.
- [ ] Paso 2. Runner: anotar en `unit-test-instructions.md` los comandos de comprobación y correr la línea base: `python3 -m unittest -v test_revisar_comparacion` (desde `despliegues/prueba_comun/herramientas/`) y `python3 pruebas/simulacro.py 40` (desde `2_Aplicacion_Reto/`) en «TODO BIEN».
- [ ] Paso 3. Mediciones (F2, BR17.1, ADR-C5): en `despliegues/COMPARACION.md`, llenar la columna Cloudflare. NFR2, NFR3, NFR5 y NFR6 salen de la corrida pública; NFR4 de las dos; cada id de `publica.nfr.no_aplica` se busca en dev con `pasa: true`. Cada casilla trae el valor y el archivo entre comillas invertidas, por ejemplo «812 ms (`cloudflare_2026-11-02.json`)».
- [ ] Paso 4. Conteos (F3, BR17.4 a BR17.6): fila «Piezas y servicios» de Cloudflare con 1 servicio y 4 piezas (Worker, recursos estáticos, Durable Object, secreto `CLAVE_DOCENTE`); fila «Líneas de código» con el comando de BR17.6 y el commit sobre el que se corrió.
- [ ] Paso 5. Consumo (F9, BR17.12): leer los intervalos de `despliegues/cloudflare/web/static/js/*.js` y `despliegues/cloudflare/web/tablero.html`; calcular las peticiones de 90 minutos con un tablero, un panel y 40 estudiantes; dividir por 100.000 tras volver a consultar https://developers.cloudflare.com/workers/platform/limits/ y la página oficial de precios de Durable Objects. Escribir el bloque «Consumo de un reto real» con fórmula, cada número, URL y fecha.
- [ ] Paso 6. Otras opciones (F4, BR17.3, ADR-C2): columna GitHub Pages con «no se construye (FR12.2c, `requirements.md`)» en cada casilla medida y «≥ 2 servicios, sin desplegar» en «Piezas y servicios»; columna Apps Script con «no pasa por contrato: C-01 (`contract-design/reviews/review-01.md`)»; columnas Render y Cloudflare Containers sin cambios (U15, U16).
- [ ] Paso 7. Bloques de veredicto (F4, BR17.2, «Forma de `COMPARACION.md`»): «Veredicto por NFR» como tabla con primera columna «Criterio» y las cinco columnas en el mismo orden de la tabla principal (así la lee `revisar_comparacion.py`); «Qué salió de cada corrida», «Consumo de un reto real» y «Resultado» como listas, no tablas. Pie con las fechas de las mediciones y de la documentación consultada.
- [ ] Paso 8. Comprobación de la tabla: correr `revisar_comparacion.py --opcion` para `cloudflare`, `render`, `"cloudflare containers"`, `"apps script"` y `"github pages"`; las cinco en «TODO BIEN». Correr el `grep` de U17-S1 sobre `COMPARACION.md`.
- [ ] Paso 9. ADR final (F5, F6, BR17.7): completar ADR-C3 en `aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u17-comparacion/decisions.md` con los doce veredictos de Cloudflare, sus tres números de FR12.6, el criterio «única que pasa», el respaldo de aula (versión local) y la pregunta de limpieza de `render.yaml`. Estado «Proposed». Si Cloudflare no pasa todo, el ADR lista los NFR que fallan y se detiene en OQ2. Commit 1 de `../infrastructure-design/cicd-pipeline.md`.
- [ ] Paso 10. `LEEME.md` de Cloudflare (F10, BR17.13, ADR-C6): en `despliegues/cloudflare/LEEME.md`, `CLAVE_SEMILLERO` pasa a `CLAVE_DOCENTE` (en `.dev.vars` y en `npx wrangler@4.148.0 secret put CLAVE_DOCENTE`); paso único `npx wrangler@4.148.0 secret delete CLAVE_SEMILLERO`; `.dev.vars` de ejemplo con `DURACION_MINIMA_MIN=1` y la advertencia D9; las dos corridas de ADR-C5; «Cómo se usa el día del reto» para un docente, con el tablero en `/tablero` sin `?sala=`; «Volver a la versión anterior» con la advertencia de ADR-W19; sección «Desde Windows» (Git para Windows con Git Bash, Node 24, Python 3.12, `py -3`, PowerShell si Git Bash no muestra la pregunta del secreto). Decir que el despliegue es a mano, solo sin un reto en curso, y con una sola instancia.
- [ ] Paso 11. Fin de línea (ADR-C6): agregar a `.gitattributes` las líneas `*.sh text eol=lf` y `*.patch text eol=lf`. Commit 2 de `cicd-pipeline.md`.
- [ ] Paso 12. Aprobación: el humano lee la tabla y el ADR-C3 y lo pasa a «Accepted» con la fecha. Sin esa aprobación no se hacen los pasos 13 y 15.
- [ ] Paso 13. Guía (F7, BR17.10, ADR-C4): reemplazar entero `PUBLICAR_EN_INTERNET.md` con las once secciones (0 a 10) de «Forma de `PUBLICAR_EN_INTERNET.md`». Incluye `wrangler login`, `wrangler secret put CLAVE_DOCENTE`, `wrangler deploy`, el recuadro «Desde Windows», la regla de desplegar a mano solo cuando no hay un reto en curso, una sola instancia, la página 1027 y la corrección de FR8.3. Quitar GitHub Desktop, Render, «solo Mac», salas, clave del semillero y `?sala=`. Costo US$ 0 con la cuota y su URL.
- [ ] Paso 14. Comprobación de las guías: conteo de palabras por frase sobre `PUBLICAR_EN_INTERNET.md` (ninguna con más de 30); `grep` de U17-S1 sobre las dos guías y el ADR; lectura de la guía por alguien del semillero ajeno al diseño (FR8.1); `LEEME.md` seguido en Windows con Git Bash, con `copiar.sh` y `verificar.sh` sin error de fin de línea. Anotar quién y cuándo en la casilla NFR7. Commit 4.
- [ ] Paso 15. Borrado (F8, BR17.9): commit propio «chore: borrar las carpetas de las opciones descartadas» con `despliegues/apps-script/`, `despliegues/render/`, `despliegues/cloudflare-containers/` y `despliegues/github-pages/`. Se conservan `cloudflare/`, `prueba_comun/`, `LEEME.md` y `COMPARACION.md`; las filas de la tabla quedan.
- [ ] Paso 16. Cierre: `python3 pruebas/simulacro.py 40` en «TODO BIEN», `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1), ganchos de pre-commit, y trazabilidad y resumen de la unidad.
