# Plan de código — U5 `u5-cloudflare-salas` (reto, colegios y relojes)

## Summary

- Builds: el reto de una sola sala en Cloudflare Workers: clave docente única (`CLAVE_DOCENTE`, solo por `X-Clave-Admin`), migración 2 del esquema (tablas del corte a `v1_*`), lista de colegios del docente con «Arrancar reloj», vencimiento por colegio, las tres transiciones del reto, las acciones del docente, inscripción y examen completos con los 10 tipos, y el resumen del panel.
- Touches: `despliegues/cloudflare/` (`src/reto.js`, `src/servicios/`, `src/worker.js`, `wrangler.jsonc` solo el comentario, `herramientas/cambios_web.patch`, `herramientas/verificar.sh`, `LEEME.md`, `web/` regenerada) y `despliegues/prueba_comun/src/prueba.py` (la prueba común mínima pasa a la clave docente).
- Tests: las pruebas `node:test` de U4 siguen verdes; la prueba común mínima, ampliada a la clave docente, los colegios y el reloj, contra `wrangler dev`; la migración F8 a mano sobre datos del corte; el simulacro local en «TODO BIEN».

Fuentes: `../functional-design/` (flujos F1 a F8, reglas BR1.1 a BR9.1, entidades de la versión 2),
`../nfr-requirements/`, `../nfr-design/`, `../infrastructure-design/` (revisados el 2026-10-27, una sola
sala), `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19, ADR-W20) y `contract-design-questions.md` (D1 a
D10). Este alcance no tiene historias de usuario: cada paso se traza a FR, BR y NFR de la unidad.

**Requisito previo:** U4 terminada. U5 llama a la fachada `src/reglas.js` y a los módulos
`src/reglas/{banco,calificacion,clasificacion,ciclo_del_reto,limpieza_entrada,experimento}.js` de U4
(ADR-W6): `traducir_respuesta`, `validar_respuesta`, `fraccion`, `respuesta_opaca`, `ordenar`,
`por_grado`, `calcular`, `transicion_permitida`, `hora_de_entrega`, `estado_tras_cierre`,
`puede_arrancar_colegio`, `puede_comenzar`, `estado_reloj`, `colegios_al_abrir`, `validar_inscripcion`,
`normalizar_integrantes` y `preparar_colegios`. Si alguna falta, el paso que la usa se detiene y se
anota; U5 no la reescribe por su cuenta.

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
  }
}
```

## Pasos

- [ ] Paso 1. Estructura: crear `despliegues/cloudflare/src/servicios/` con `ciclo.js`, `colegios.js`, `inscripcion.js` y `examen.js` (funciones `nombre(reto, contexto)`, `nfr-design/logical-components.md`); cambiar solo el comentario de cabecera de `wrangler.jsonc` para nombrar `CLAVE_DOCENTE` (sin `vars` nuevas: `DURACION_MINIMA_MIN` nunca va ahí, D9). Comprobar que `.gitignore` de la opción sigue ignorando `.wrangler/` y `.dev.vars`. FR12.2, U5-S10, U5-S11.
- [ ] Paso 2. Runner: comprobar `node --version` (24) y que `node --test despliegues/cloudflare/pruebas/reglas.test.js` y `node --test despliegues/cloudflare/pruebas/casos_reglas.test.js` (U4) pasan antes de tocar nada; anotar los comandos exactos en `unit-test-instructions.md`. `project.md` («Corrections»: `node --test` nombrando el archivo).
- [ ] Paso 3. Datos: en `src/reto.js`, `MIGRACIONES[]` con `PRAGMA user_version` (ADR-W10): versión 1 = el `ESQUEMA` del corte tal cual; versión 2 en una sola `transactionSync` = renombrar `salas`, `sala_colegios`, `colegios`, `participantes`, `respuestas`, `eventos` a `v1_*`, `DROP INDEX participante_unico` y `participantes_estado`, crear `reto` (`CHECK (id = 1)`), `colegios` (`nombre_normalizado` único, `arranque`), `participantes` sin `id_sala` con `participante_unico`, `participantes_estado` y `participantes_colegio`, `respuestas` y `eventos` iguales a U1, e insertar la fila de `reto` con los valores por defecto (`entities.md`, «Tablas (versión 2)»). Un fallo deja `error_arranque` (500 en toda ruta). BR8.1, ADR-W19, U5-R1, U5-R6.
- [ ] Paso 4. Arranque y acceso: en el constructor, revisar `env.CLAVE_DOCENTE` (sin espacios, 12 caracteres o más) antes de migrar; `acceso_admin` compara `X-Clave-Admin` con `iguales_en_tiempo_constante`, sin pasar a mayúsculas, con espera de 600 ms fuera del bloqueo si falta o no coincide; `dar_acceso` responde 403 si una ruta `/api/admin/*` trae `?clave=` aunque la cabecera sea correcta; tres niveles (público, token, clave) y todo lo demás 404. Quitar `clave_semillero`, `sala_de_acceso`, `sala_por_codigo`, `sala_de`, `crear_sala` y los niveles `semillero` y `sala`. BR1.1, BR1.3, BR1.4, BR1.5, BR1.6, U5-S1, U5-S4, U5-S9, U5-S10.
- [ ] Paso 5. Pruebas de datos y acceso: en `despliegues/prueba_comun/src/prueba.py`, cambiar el modo nube a la clave docente (sin crear sala) y agregar: 403 con clave ausente, incorrecta y con `?clave=` más cabecera correcta; 404 en `POST /api/admin/salas/crear`; `GET /api/publico` responde 200 sin parámetros. Correr contra `npx wrangler@4.148.0 dev` y hacer a mano la comprobación F8 (estado local del corte → código de U5: `user_version` = 2, `v1_salas` y `v1_participantes` con sus filas, `reto` en «inscripción», `colegios` y `participantes` vacías). BR1.3, BR1.5, BR8.1, FR12.3, U5-R1.
- [ ] Paso 6. Lógica de colegios y ciclo: `src/servicios/colegios.js` con `GET /api/admin/colegios`, `POST /api/admin/colegios` (`accion` ∈ `agregar`, `quitar`, `arrancar`; `agregar` acepta `nombres` o `nombre`, valida todo con `preparar_colegios` y no agrega ninguno si uno falla, 400 «Ese colegio ya existe.» con `existente`; `quitar` solo sin equipos; `arrancar` con `puede_arrancar_colegio`, hora del servidor y `WHERE arranque IS NULL`) y `GET /api/colegios` público sin `?sala=`. `src/servicios/ciclo.js` con `login` (`{ok: true}`), `config` (código, evento, duración solo en «inscripción» con mínimo 10 o `DURACION_MINIMA_MIN`, modo sorpresa, retro; `reloj_global` da 400, D1) y `estado` del docente con `transicion_permitida`: abrir arranca en la misma transacción los colegios de `colegios_al_abrir`; cerrar fija `cerrado_en`, entrega los `en_curso` y pasa los `registrado` a `no_inicio` en una transacción; publicar pasa a «resultados»; el reto nunca se cierra solo. BR2.2, BR2.3, BR2.5, BR4.2, BR4.3, BR4.4, D3, D9, U5-R2, U5-R3, U5-R7, U5-S11, U5-E4.
- [ ] Paso 7. Lógica de inscripción y examen: `src/servicios/inscripcion.js` (`registro` con `validar_inscripcion`, código del reto, colegio de la lista por `id_colegio`, integrantes normalizados; `entrar`; «Eliminar» solo en `registrado` o `no_inicio`, borrando también sus eventos) y `src/servicios/examen.js` (`comenzar` con `puede_comenzar`: 400 «Tu colegio todavía no ha empezado. Espera la señal del docente.» si el colegio no arrancó, `inicio` = `arranque` del colegio; `responder` de los 10 tipos con `traducir_respuesta` → `validar_respuesta` → `fraccion` y la guardada con `respuesta_opaca`; `finalizar`; `evento`; acciones del docente Entregar, Anular, Reactivar como hoy; entrega de lo vencido antes de cada petición con `hora_de_entrega` sobre el `arranque` de cada colegio y `cerrado_en`). `GET /api/estado` agrega `participante.colegio_arranque` y `participante.colegio_restante_seg` (D2) y mantiene `reto.reloj_global` fijo (D1). BR5.1, BR5.2, BR6.1, BR6.2, BR6.3, BR6.4, BR6.5, FR3.1, FR10.1 a FR10.4, U5-S6, U5-R4, U5-P3.
- [ ] Paso 8. Pruebas de la lógica: ampliar la prueba común mínima (`prueba.py`, modo nube) con: agregar dos colegios (uno repetido da 400 y no agrega ninguno), inscribir un equipo en cada uno, abrir (arranca solo el colegio con equipos), comenzar en un colegio sin arrancar da 400 con el mensaje de espera, «Arrancar reloj» del segundo y comenzar, responder una pregunta (aceptada) y la misma otra vez (rechazada), «Eliminar» de un inscrito sin empezar, cerrar (entrega a todos y deja «No inició» a quien no empezó). Las reglas puras siguen en `node:test` de U4 sin cambios. Correr contra `wrangler dev` hasta «TODO BIEN». El caso de vencimiento real (`DURACION_MINIMA_MIN` en `.dev.vars`) y una respuesta de cada uno de los 10 tipos son de U2 (`functional-spec.md`, «Prueba común»). BR2.3, BR4.2 a BR4.4, BR5.2, BR6.1, BR6.4, FR11.7.
- [ ] Paso 9. API del panel y tablero: rutas `GET /api/admin/resumen` (lo de hoy más la tarjeta de colegios con `estado_reloj` y el número de equipos, el «Puesto en el grado» con `por_grado` y el experimento completo con `calcular`, ADR-W11), `POST /api/admin/participante` y `GET /api/publico` sin parámetros (tablero y salud: conteo y `colegios[]` con nombre y reloj, sin `ranking`, `por_grado` ni `experimento`, que son de U6; ninguna consulta nombra `v1_*` ni trae `token` o `semilla`). `src/worker.js`: 503 con el mensaje del contrato si `stub.fetch` lanza un error (ADR-W20). Registro solo de arranque, migración, cambio de estado y reloj arrancado. Las rutas de U6 responden 404. BR1.1, BR4.5, BR7.1, BR7.2, D10, U5-S5, U5-S8, U5-S12, U5-O1, U5-O2, U5-O4.
- [ ] Paso 10. Pruebas de la API: en `prueba.py`, `GET /api/admin/resumen` con clave trae la tarjeta de colegios y ningún `token` ni `semilla`; `GET /api/publico` trae `colegios[]` sin equipos y sin clasificación antes de resultados; cada llamada de la parte de U5 de las tres pantallas responde con la forma del contrato (no 404). Correr contra `wrangler dev`. BR7.1, BR7.2, BR9.1, U5-S5, U5-S8.
- [ ] Paso 11. Pantallas: rehacer `herramientas/cambios_web.patch` sobre una copia limpia de `2_Aplicacion_Reto/web/` con los cambios de `functional-spec.md` («Pantallas»): `admin.js` sin mayúsculas en la clave, aviso «La clave docente la guarda el semillero en Cloudflare», sin «Reloj global», tarjeta «Colegios» (lista con reloj, «Agregar colegios» con un nombre por línea, «Quitar», «Arrancar reloj» con las dos confirmaciones «¿Arrancar el reloj de <colegio>? Tendrá <n> minutos desde ahora.» y «No se puede deshacer.»), columna «Puesto en el grado»; `estudiante.js` con la lista de colegios sin `?sala=`, el aviso «Tu colegio todavía no ha empezado. Espera la señal del docente.» y «Comenzar» habilitado solo con `colegio_arranque`; `tablero.html` sin `?sala=` y con el reloj de cada colegio. Forma IIFE con `h()` y `textContent`. Regenerar `web/` con `copiar.sh`. FR10.3, FR11.3, FR11.4, FR11.5, FR2.5, D1, D6.
- [ ] Paso 12. Prueba de pantallas: `copiar.sh` dos veces desde cero da la misma huella de `web/`; la prueba común pide `/`, `/admin`, `/tablero` y un archivo de `/static/` (200); revisión a mano en `wrangler dev` del flujo completo: el panel entra con la clave docente y se dibuja entero, el estudiante se inscribe, ve el aviso de espera, comienza tras «Arrancar reloj», responde y entrega, y el tablero muestra los relojes. BR9.1, FR11.3.
- [ ] Paso 13. Configuración y secretos: `herramientas/verificar.sh` pasa a `CLAVE_DOCENTE` (crea `.dev.vars` con una clave al azar de 24 caracteres si no existe, o le agrega la línea si solo trae la `CLAVE_SEMILLERO` de U1) y corre cada archivo de pruebas `node --test` por nombre. La clave nunca se escribe en un archivo versionado: en local va en `.dev.vars` (ignorado) y en la nube con `npx wrangler@4.148.0 secret put CLAVE_DOCENTE`; después del despliegue, `npx wrangler@4.148.0 secret delete CLAVE_SEMILLERO`. `DURACION_MINIMA_MIN` solo en `.dev.vars`. Ningún paquete npm nuevo. BR1.6, U5-S10, U5-S11, NFR9.
- [ ] Paso 14. Documentación y trazabilidad: `despliegues/cloudflare/LEEME.md` en palabras simples (la clave docente, cómo cargar colegios y arrancar relojes, los pasos de despliegue de `infrastructure-specification.md` y que la vuelta atrás es redesplegar U5, no U1); `despliegues/prueba_comun/LEEME.md` con el cambio a `--clave` docente; `code-summary.md`, `source-manifest.json` y `traceability.json` de esta etapa con el resultado de F8. FR8.0, ADR-W10.
- [ ] Paso 15. Cierre: `bash despliegues/cloudflare/herramientas/verificar.sh` termina con código de salida 0 (reglas, prueba común mínima con la clave docente contra `wrangler dev` en «TODO BIEN» y simulacro) y `python3 pruebas/simulacro.py 40`, desde `2_Aplicacion_Reto/`, termina en «TODO BIEN»; `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` sale vacío (FR12.1); ningún archivo lleva una clave, una respuesta correcta ni datos de un reto real. `bolt-plan.md` («Reglas para todos los Bolts»).
