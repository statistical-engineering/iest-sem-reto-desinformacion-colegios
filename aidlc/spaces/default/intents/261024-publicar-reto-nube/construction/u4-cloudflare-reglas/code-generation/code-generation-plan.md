# Plan de código — U4 `u4-cloudflare-reglas`

> **Revisión 2026-10-27 (una sola sala).** Plan escrito para el reto de una sola sala, un solo docente con
> `CLAVE_DOCENTE` y un reloj por colegio (ADR-009 a ADR-011). U4 no toca claves ni rutas: `reto.js` y
> `worker.js` siguen como los dejó U1 hasta U5.

## Summary

- Builds: las seis «calculadoras» de ADR-001 en JavaScript con la forma del contrato C4: los 10 tipos de pregunta, bono, orden total con tiempos relativos al arranque del colegio, podio general, puesto por grado, nota, transiciones de estado, relojes y entrega por colegio, limpieza de entradas y experimento; más la tabla de casos compartida `casos_reglas.json`, generada desde `servidor.py`.
- Touches: `despliegues/cloudflare/src/reglas/` (nuevo), `despliegues/cloudflare/src/reglas.js` (pasa a fachada), `despliegues/cloudflare/pruebas/` (pruebas nuevas y copias de datos), `despliegues/cloudflare/herramientas/{copiar,verificar}.sh`, `despliegues/cloudflare/LEEME.md`, `despliegues/prueba_comun/{banco_prueba.json,casos_reglas.json,LEEME.md}` y `despliegues/prueba_comun/herramientas/{generar_casos.py,test_generar_casos.py}`. No toca `src/reto.js`, `src/worker.js`, `web/`, `wrangler.jsonc` ni `2_Aplicacion_Reto/`.
- Tests: un `pruebas/<componente>.test.js` por archivo de `src/reglas/` (5 a 8 pruebas o los mínimos de BR7.2), `pruebas/casos_reglas.test.js` con una prueba por fila de la tabla, las 23 pruebas de U1 sin cambios, `unittest` del generador, y al final `verificar.sh` (cobertura ≥ 80 % en `src/reglas/**`, prueba común en Workers y simulacro).

Fuentes: `../functional-design/` (F1 a F9, BR1.1 a BR7.3, entidades), `../nfr-requirements/`, `../nfr-design/`,
`../infrastructure-design/`, `../decisions.md` (ADR-W6 a ADR-W9, más ADR-W1 a ADR-W5 de U1),
`../../../inception/contract-design/contract-summary.md` («C4. Forma de las reglas») y `bolt-plan.md` (B4). Este
alcance no tiene historias de usuario: cada paso se traza a FR, BR y requisitos U4-*.

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

Rutas relativas a la raíz del repositorio. `CF` = `despliegues/cloudflare`, `PC` = `despliegues/prueba_comun`.
Cada archivo nuevo de `CF/src/reglas/` es un módulo ES (`export function …`), con JSDoc en cada función
exportada (qué hace, por qué existe: reutilización o paso aislado) y sin comentarios de línea; nombres en
español sin tildes; ninguna función con complejidad ciclomática mayor que 10 (`team.md`, «Code Style»,
revisada a mano). Prohibido en `CF/src/reglas/`: `Date`, `Math.random`, `getRandomValues`, `env.`,
`console.` (U4-S5, U4-O1). Ningún paquete npm nuevo; wrangler solo como `npx wrangler@4.148.0`. Nunca se copia
una respuesta, explicación ni veredicto de `2_Aplicacion_Reto/banco_preguntas.json` ni de `3_Guia_docente/`
a un archivo de prueba o a la tabla (U4-S1). `2_Aplicacion_Reto/` no se modifica (FR12.1).

### Estructura y runner

- [ ] Paso 1. Estructura (ADR-W6, U4-R4). Crear `CF/src/reglas/` con `comun.js`, `banco.js`,
  `calificacion.js`, `clasificacion.js`, `ciclo_del_reto.js`, `limpieza_entrada.js` y `experimento.js`, y
  **mover sin cambiar su cuerpo** cada función que hoy está en `CF/src/reglas.js`:
  - a `comun.js`: `ALFABETO`, `PUNTOS_TOTALES`, `sha256_hex`, `iguales_en_tiempo_constante` y la constante
    `ESTADOS_SALA` renombrada `ESTADOS_RETO` (mismo contenido);
  - a `banco.js`: `validar_banco`, `huella_banco`, `opaco_de`, `opacos_de`, `traducir_opaco`, `resolver`,
    `visible_para`, `armar_misiones`, `aplicar_bloqueos`, `examen_publico` y sus auxiliares privados;
  - a `calificacion.js`: `validar_respuesta`, `fraccion`, `bono`, `cerrar_intento`;
  - a `ciclo_del_reto.js`: `transicion_permitida`, `hora_de_entrega`;
  - a `limpieza_entrada.js`: `limpiar` renombrada `normalizar_texto`, `normalizar_codigo`, `normalizar_nombre`
    renombrada `normalizar_nombre_colegio`.

  `CF/src/reglas.js` queda como fachada: un `export * from "./reglas/<archivo>.js";` por módulo y los tres alias
  que `CF/src/reto.js` de U1 todavía usa: `export const limpiar = normalizar_texto;`,
  `export const normalizar_nombre = normalizar_nombre_colegio;`, `export const ESTADOS_SALA = ESTADOS_RETO;`.
  `CF/src/reto.js`, `CF/src/worker.js` y `CF/pruebas/reglas.test.js` no se tocan. Los módulos solo importan de
  `./comun.js`, nunca entre sí (U4-E2: sin `let` ni `Map` a nivel de módulo).
- [ ] Paso 2. Runner. Comprobar `node --version` ≥ 24 y correr
  `node --test despliegues/cloudflare/pruebas/reglas.test.js`: las 23 pruebas de U1 pasan sin cambios
  (U4-R4). Anotar el comando por archivo y el de cobertura en `unit-test-instructions.md` (ya escrito con este
  plan; corregirlo solo si el comando real difiere).
- [ ] Paso 3. Banco de prueba (ADR-W7, U4-S1, C4 `no_lleva`). Crear `PC/banco_prueba.json` a mano, **inventado**:
  misma forma que `banco_preguntas.json` (`version`, `puntos_totales: 1000`, `bono_tiempo_max: 20`, `misiones[]`
  con `preguntas[]`), con al menos una pregunta de cada uno de los 10 tipos (`opcion`, `multiple`, `clasificar`,
  `compartir`, `recordatorio`, `ordenar`, `construir`, `texto`, `estimar`, `numero`), una con `variantes`, una con
  `solo_grupo`, una con `requiere`, y un Expediente 01 propio con ids `m1_posts`, `m1_compartir`,
  `m1_veracidad` y publicaciones con veredicto inventado, para que `experimento()` funcione. Ids, textos y claves
  propios (prefijo `prueba_` salvo los `m1_*` que `experimento()` exige). Los puntos suman exactamente 1.000.
  Comprobar con `node -e` que `validar_banco` de `CF/src/reglas.js` devuelve `[]` sobre ese archivo. En
  `CF/herramientas/copiar.sh`, después de copiar el banco, agregar la copia de `PC/banco_prueba.json` a
  `CF/pruebas/banco_prueba.json` (y su línea en el encabezado del script); correr el script y confirmar con
  `git status --short despliegues/cloudflare/web` que la copia de `web/` no cambió.

### Lógica pura, un componente por paso, con sus pruebas después

- [ ] Paso 4. `CF/src/reglas/comun.js`: `redondear(x, d)` (BR2.5, ADR-W8): `r = Number(x.toFixed(d))`; si
  `x × 10^d` es exactamente un entero más 0,5 (comprobado sin error descomponiendo el doble con `DataView`
  en mantisa y exponente y comparando con `BigInt`), devolver el vecino cuyo último dígito es par; `d` de 0 a 9;
  `x` no finito se devuelve igual. Agregar `BONO_MAX = 20` y `GRADOS = Object.freeze(["9", "10", "11"])`.
- [ ] Paso 5. `CF/pruebas/comun.test.js` (5 a 8 pruebas): `redondear` con un empate exacto por cada número de
  decimales usado (1, 2, 3, 4 y 9, por ejemplo `redondear(2.25, 1)` da 2,2 y `redondear(1.125, 2)` da 1,12, como
  `round` de Python), dos sin empate, y `iguales_en_tiempo_constante` (igual, distinto, largo distinto). Correr
  `node --test despliegues/cloudflare/pruebas/comun.test.js`.
- [ ] Paso 6. `CF/src/reglas/banco.js` (BR1.1, BR1.2, BR1.3, U4-P3, U4-S2): extender `examen_publico` y
  `armar_misiones` a los 10 tipos con la lista blanca de BR1.3 (`opciones`, `publicaciones`, `items`, `partes`
  con ids opacos; nunca `respuesta`, `explicacion`, `tolerancia`, `solo_grupo`, `variantes`); agregar
  `traducir_respuesta(semilla, pregunta, respuesta_opaca)` y `respuesta_opaca(semilla, pregunta, valor)` según
  la tabla por tipo de BR1.1 (ámbito `m1_posts` para ítems y publicaciones de `m1_*`; `null` si un id opaco
  no corresponde), llamando a `opacos_de` solo con los ids de esa pregunta o parte; agregar
  `revision_publica(banco, semilla, grupo)` → `{<pregunta_id>: {respuesta, explicacion}}` con ids opacos, sin
  decidir cuándo se llama.
- [ ] Paso 7. `CF/pruebas/banco.test.js` (5 a 8 pruebas, con la copia `CF/pruebas/banco_prueba.json`): ida y vuelta
  `respuesta_opaca` → `traducir_respuesta` para cada tipo que traduce; `null` con un id opaco ajeno; los ids opacos de
  `revision_publica` coinciden con los de `examen_publico`; y con `CF/src/banco.json` (banco real, solo
  estructura) ninguna pregunta de `examen_publico` trae `respuesta`, `explicacion`, `tolerancia`, `solo_grupo` ni
  `variantes` en los 10 tipos. Correr el archivo.
- [ ] Paso 8. `CF/src/reglas/calificacion.js` (BR2.1 a BR2.5, U4-S4): `validar_respuesta` para los 10 tipos
  según BR2.1 (comprobar tipo JS y tamaño antes de recorrer; `texto` hasta `max + 50`, 700 si falta `max`);
  `a_numero(texto, entero)` según BR2.2, recortando a 64 caracteres y aceptando solo dígitos ASCII; `fraccion` para
  los 10 tipos según BR2.3, con el mismo orden de operaciones que `fraccion()` de `servidor.py` y `RangeError` para un
  tipo desconocido; `bono` y `cerrar_intento` según BR2.4 (`inicio` = arranque del colegio;
  `bono_max * (puntos / puntos_totales) * (1 - t / dur)`, sin reordenar).
- [ ] Paso 9. `CF/pruebas/calificacion.test.js`: por tipo, un caso válido y dos inválidos de `validar_respuesta`;
  acierto, parcial y cero de `fraccion` con preguntas armadas en la prueba; los 5 casos de `a_numero` de BR7.2;
  `RangeError` con tipo desconocido; `cerrar_intento` con colegio arrancado tarde (mismo bono que uno arrancado a
  tiempo con la misma última respuesta relativa). Correr el archivo.
- [ ] Paso 10. `CF/src/reglas/clasificacion.js` (BR3.1 a BR3.4, U4-P1): `ordenar(finalizados)` con la clave
  `-redondear(total, 9)`, `-redondear(puntos, 9)`, `tiempo_respuestas` ↑, `tiempo_usado` ↑, `id` ↑, devolviendo
  FilaClasificada (`entities.md`) con `puesto` 1..n y los redondeos de `clasificacion()` (puntos, bono y total a
  4; nota a 2; `tiempo_usado` a 1; `tiempo_respuestas` a 3); `por_grado(ordenadas)` →
  `{lista, por_grado: {"9", "10", "11"}}` con `puesto_grado`, sin reordenar; `nota(puntos, puntos_totales = 1000)` =
  `redondear(1 + 4 * puntos / puntos_totales, 2)`; `puesto_de(id, finalizados)` → `{puesto, puesto_grado, nota}`
  o `null`.
- [ ] Paso 11. `CF/pruebas/clasificacion.test.js`: empate en total, en total y puntos, hasta `tiempo_usado` y hasta
  `id`; lista vacía; un grado vacío; `nota(0)` = 1, `nota(1000)` = 5 y `nota(31.25)` = 1,12; `puesto_de` de un id
  ausente da `null`; con 40 filas fabricadas, `ordenar` + `por_grado` informa su tiempo con `performance.now()`
  sin fallar por él (U4-P1). Correr el archivo.
- [ ] Paso 12. `CF/src/reglas/ciclo_del_reto.js` (BR4.1 a BR4.8, FR3.1, FR11.5, ADR-011):
  `transicion_permitida` (solo inscripción→abierto, abierto→cerrado, cerrado→resultados); `hora_de_entrega` según
  BR4.2; `estado_tras_cierre(estado)` según BR4.3; `admite_inscripciones(estado)` (BR4.4);
  `puede_arrancar_colegio(estado_reto, arranque)`, `puede_comenzar(estado_reto, estado_participante, arranque,
  duracion, ahora)`, `estado_reloj(arranque, duracion, ahora)` y `colegios_al_abrir(colegios)` con la lógica y
  los mensajes exactos de BR4.5 a BR4.8 en `../functional-design/rules.md`.
- [ ] Paso 13. `CF/pruebas/ciclo_del_reto.test.js`: las 3 transiciones permitidas y 4 prohibidas; cada motivo de
  `puede_arrancar_colegio` y de `puede_comenzar` (incluido «Tu colegio todavía no ha empezado. Espera la señal
  del docente.»); `estado_reloj` sin arrancar, corriendo, justo al vencer y vencido; `hora_de_entrega` con cierre
  antes y después del vencimiento; `colegios_al_abrir` con un colegio sin equipos y uno ya arrancado. Correr el
  archivo.
- [ ] Paso 14. `CF/src/reglas/limpieza_entrada.js` (BR5.1 a BR5.5, FR10): `normalizar_texto` según BR5.1 (NFC,
  control a espacio, sin caracteres de formato, espacios juntados, recorte en caracteres), sin regex con
  cuantificadores anidados; `normalizar_integrantes(texto)` → `{texto, n_integrantes}` (BR5.2);
  `validar_inscripcion(campos, ids_colegios)` con los tres mensajes de BR5.3 en su orden;
  `normalizar_nombre_colegio` (BR5.4); `preparar_colegios({nombres, nombre, existentes})` según BR5.5 (todo o
  nada, `existente` en el error de repetido, repetidos dentro del texto cuentan una vez).
- [ ] Paso 15. `CF/pruebas/limpieza_entrada.test.js`: NFC, ancho cero, control, espacios, largo y vacío;
  integrantes vacíos, uno, varios y comas sobrantes; inscripción válida, nombre corto, grado y colegio fuera de la
  lista; `preparar_colegios` con lista válida, línea vacía, nombre corto, repetido con la lista, repetido dentro del
  texto y solo `nombre`. Correr el archivo.
- [ ] Paso 16. `CF/src/reglas/experimento.js` (BR6.1, BR6.2, ADR-W9, U4-S3): `calcular(banco, filas)` que
  reproduce `experimento()` de `servidor.py` con el mismo orden de operaciones sobre las filas
  `{participante_id, grupo, estado, pregunta_id, respuesta}` de todos los colegios, sin descalificados;
  `experimento_publico(experimento, estado)`: `null` en «inscripción» y «abierto», un objeto nuevo `{n, listo}` en
  «cerrado» (construido desde cero, no borrando claves) y el objeto completo en «resultados».
- [ ] Paso 17. `CF/pruebas/experimento.test.js` (con `banco_prueba.json`): n < 2, solo grupo A, los dos grupos, con
  un descalificado; `experimento_publico` en los cuatro estados, comprobando que fuera de «resultados» no sale
  `verdad`, `multitud_acierta`, `clase`, `por_publicacion` ni `multitud`. Correr el archivo.

### Tabla de casos compartida (contrato C4)

- [ ] Paso 18. Generador `PC/herramientas/generar_casos.py` (ADR-W7, BR7.1, BR7.3, U4-S6), Python 3.12 sin paquetes,
  con docstring de módulo y formato ruff (`uv run ruff format` y `uv run ruff check`): agrega
  `2_Aplicacion_Reto/` a `sys.path`, importa `servidor` (no llama a `main()`), reemplaza `servidor.BANCO`,
  `servidor.PREGUNTAS`, `servidor.PUNTOS_TOTALES` y `servidor.BONO_MAX` con `PC/banco_prueba.json`, pone
  `servidor.DB = servidor.conectar(":memory:")` y llama a `servidor.inicializar_config()`; nunca abre
  `2_Aplicacion_Reto/datos/`. Calcula cada caso con la fuente de la tabla de ADR-W7 (`servidor.py` o
  `referencia FR2.5`, `FR2.6`, `ADR-011`, `FR10.2`, `FR10.4`, `FR7.4`, `ADR-004`), con horas fabricadas (arranque
  en 1.000 s) y los mínimos por función de `../functional-design/functional-spec.md` («Forma de la tabla de
  casos»), incluidos los casos A y B de BR7.3; se detiene con código 1 si el caso B no coincide con
  `clasificacion()`. Escribe `PC/casos_reglas.json` con `json.dumps(…, ensure_ascii=False, indent=1,
  sort_keys=True)`, filas `{regla, funcion, fuente, entrada, salida_esperada[, tolerancia]}`, con
  `entrada.banco: "banco_prueba"` en vez de repetir el banco. Prueba `PC/herramientas/test_generar_casos.py`
  (`unittest`, sin `if` ni `try`): el caso B coincide, toda fila tiene `fuente` permitida, los mínimos por función
  se cumplen y el archivo se escribe igual dos veces seguidas (determinista). Correr el generador y su prueba.
- [ ] Paso 19. `CF/pruebas/casos_reglas.test.js` (BR7.1, U4-O2, U4-R2): lee `CF/pruebas/casos_reglas.json` y
  `CF/pruebas/banco_prueba.json`, sustituye `"banco_prueba"` por el banco cargado y genera una prueba por fila
  con el título `` `${regla}.${funcion} caso ${i}` ``; llama a la función de la fachada con los argumentos de
  `entrada` en el orden de las firmas de C4 (una tabla `funcion → argumentos` en el archivo de prueba; las
  `async` con `await`) y compara con `assert.deepStrictEqual`, o número a número con `|a − b| ≤ tolerancia`
  cuando la fila la trae. Una prueba más cuenta los mínimos por función de la spec y otra comprueba que ninguna
  pregunta de `banco_prueba.json` cuyo id también existe en `CF/src/banco.json` (los `m1_*`) tiene la misma
  `respuesta` que la del banco real, comparando en memoria sin escribir nada (U4-S1).
- [ ] Paso 20. `CF/herramientas/copiar.sh` (U4-R5): agregar la copia de `PC/casos_reglas.json` a
  `CF/pruebas/casos_reglas.json` junto a la de `banco_prueba.json` del paso 3, con su línea en el encabezado.
  Correr el script y confirmar otra vez que `despliegues/cloudflare/web` no cambió.
- [ ] Paso 21. Correr `node --test` de cada archivo de `CF/pruebas/*.test.js`, uno por uno, y la cobertura del
  conjunto (comando de `unit-test-instructions.md`): todo en verde y ≥ 80 % de líneas en `CF/src/reglas/**`
  (NFR12, U4-O3). Si una fila de la tabla falla, se corrige la regla JS, nunca la tabla a mano.

### Configuración, documentación y cierre

- [ ] Paso 22. `CF/herramientas/verificar.sh` (U4-R5, U4-S5, U4-O3, U4-P4): antes de las pruebas, comparar
  `sha256sum` de `PC/casos_reglas.json` y `CF/pruebas/casos_reglas.json` (y lo mismo con `banco_prueba.json`) y
  detenerse con «la copia de casos_reglas.json está vieja: corre copiar.sh»; `grep -rnE
  'Date|Math\.random|getRandomValues|env\.|console\.' despliegues/cloudflare/src/reglas/` debe salir vacío;
  reemplazar la línea `node --test "$OPCION/pruebas/reglas.test.js"` por una sola corrida
  `node --test --experimental-test-coverage --test-coverage-include='despliegues/cloudflare/src/reglas/**'
  --test-coverage-lines=80 <cada archivo de pruebas/*.test.js expandido por bash>`, ejecutada desde la raíz del
  repo. Lo demás (wrangler dev, prueba común con `CLAVE_SEMILLERO`, simulacro) no cambia: la clave pasa a
  `CLAVE_DOCENTE` en U5.
- [ ] Paso 23. Documentación (FR8.0): en `CF/LEEME.md`, una sección corta «Reglas y tabla de casos» con los
  archivos de `src/reglas/`, cuándo correr el generador y `copiar.sh`, y qué significa el mensaje de copia vieja;
  en `PC/LEEME.md`, qué es `casos_reglas.json`, que nunca se edita a mano y cómo se regenera. Español, formato
  numérico de Colombia y comillas «…».
- [ ] Paso 24. Trazabilidad: `code-summary.md`, `source-manifest.json` y `traceability.json` de esta carpeta, con
  cada BR1.1 a BR7.3 apuntando a su archivo y su prueba, y las desviaciones si las hubo.
- [ ] Paso 25. Verificación final: `bash despliegues/cloudflare/herramientas/verificar.sh` termina con código 0 y
  «VERIFICACION COMPLETA…»; `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` termina en «TODO BIEN»;
  `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` sale vacío (FR12.1, `bolt-plan.md`, «Reglas para todos
  los Bolts»).
