# Plan de código — U2 `u2-prueba-comun`

## Summary

- Builds: la prueba común completa para una sola sala (FR12.3, las dos partes): la parte base (las 30 comprobaciones de `simulacro.py` por HTTP y los 27 `pantalla_*`) y la parte nueva (fugas, relojes por colegio, claves y NFR), con el JSON de mediciones del contrato C3.
- Touches: `despliegues/prueba_comun/` (src, pruebas, mediciones, `contrato_api.yaml`, LEEME) y `despliegues/cloudflare/herramientas/verificar.sh`.
- Tests: 5 a 8 pruebas `unittest` por módulo (`guion`, `pantallas`, `mediciones`, `cliente`, `carga`, contrato y sin secretos), más la prueba común contra la versión local, contra `wrangler dev` y contra la URL de Workers.

Fuentes: `../functional-design/` (F1 a F12, BR1.1 a BR8.3), `../nfr-requirements/`, `../nfr-design/` y
`../infrastructure-design/` (revisados el 2026-10-27 para una sola sala), `contract-summary.md` (C1, C2,
C3), `contract-design-questions.md` (D1 a D10) y `bolt-plan.md` (B2). Este alcance no tiene historias de
usuario: cada paso se traza a FR, NFR y BR.

**Requisito previo.** La prueba completa mide la versión terminada: B4 (U4), B9 (U5) y B11 (U6) deben
estar hechos antes de los pasos 18 a 20. Hoy (2026-10-27) `despliegues/prueba_comun/src/prueba.py` y
`verificar.sh` siguen en la versión de varias salas de U1 (`CLAVE_SEMILLERO`, `/api/admin/salas/crear`):
U2 los reescribe para la clave docente. Los pasos 1 a 17 no dependen del servicio y se pueden hacer antes.

**La clave docente nunca se escribe ni se imprime.** La prueba la lee de la variable de entorno
`PRUEBA_CLAVE` (forma documentada; `--clave` queda solo por compatibilidad, porque en la línea de comandos
se ve en la lista de procesos). Viaja solo en `X-Clave-Admin`, tal cual; ningún `print`, `detalle`, JSON ni
mensaje de error la lleva, y `validar_medicion` rechaza un JSON que la contenga. Quien prueba la escribe
sin eco (`read -rs PRUEBA_CLAVE && export PRUEBA_CLAVE`); `verificar.sh` la lee de `.dev.vars` (ignorado
por git, generado al azar, D9) y la exporta sin pasarla como argumento; la versión local la recibe por
`RETO_CLAVE`, variable que ya lee `servidor.py`.

## Testing Contract

> Copiado del de U1 (mismo alcance `classic`, estrategia `standard` y postura del equipo); las huellas
> `input_sha256` y `contract_sha256` las pone el motor al reportar la etapa.

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
      "layer": "team",
      "text": "- **Methodology**: test-after\n- **Ordering**: implementamos cada capa que se pueda probar, luego escribimos y corremos sus pruebas\n  `unittest`, y tras cada cambio en el servidor o en el banco corremos\n  `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` hasta ver «TODO BIEN».\n- Cobertura (Q5-D, Q7-A): mantenemos el piso de 80 % de cobertura de líneas del alcance `classic` y\n  lo medimos en local con el módulo `trace` de la biblioteca estándar, sin paquetes nuevos.\n- Las pruebas nuevas verifican una conducta, sin `if` ni `try` dentro, entran por la interfaz pública\n  y no usan *mocks* en la lógica pura (`.claude/rules/python-code.md`, «Pruebas»)."
    },
    {
      "layer": "project",
      "text": "- Prueba de aceptación: `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` debe terminar en «TODO BIEN»; nunca se debilita para que pase.\n- Pruebas nuevas con `unittest` de la biblioteca estándar; `pytest` no está aprobado."
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
      "Business logic",
      "API / endpoint"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Verify the existing test runner/configuration and record the exact unit-scoped command.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  }
}
```

La prueba común no tiene base de datos, acceso a datos ni pantallas propias: sus capas son la lógica pura
(`guion`, `pantallas`, `mediciones`) y la frontera HTTP (`cliente`, `carga`, `prueba`). Las notas `org`
completas están en el plan de U1.

## Pasos

- [ ] Paso 1. Estructura: crear `despliegues/prueba_comun/pruebas/`, `despliegues/prueba_comun/mediciones/` (con `.gitkeep`) y `despliegues/prueba_comun/contrato_api.yaml`, copiado sin editar del bloque «Contenido inicial de `contrato_api.yaml`» de `contract-summary.md`. FR12.3, FR12.4, C1, C2, BR8.3.
- [ ] Paso 2. Runner: comprobar con Python 3.12 `PYTHONPATH=despliegues/prueba_comun/src python3 -m unittest discover -s despliegues/prueba_comun/pruebas -p 'test_*.py'` y la cobertura con `python3 -m trace --count --missing --summary --coverdir=<carpeta temporal> --module unittest discover …`; anotar los comandos exactos en `unit-test-instructions.md`. NFR12.
- [ ] Paso 3. Lógica pura `despliegues/prueba_comun/src/guion.py`: `huella` (BR2.2); `elegir_representantes` y `clave_por_texto` desde `revision` (BR2.3, BR2.4); `reparto_colegios` y `Guion` con colegio, papel, grado y decisiones por semilla (BR3.1, BR6.1); `respuesta_para` por tipo y decisión, incluida la inválida de cada uno de los 10 tipos (BR3.2, BR4.8); `puntos_esperados` y fracciones (BR3.3); `claves_de`, `es_opaco`, `ordenes_distintos` y `csv_sin_opacos` (BR5.1, BR5.3, BR5.4); y las revisiones de orden de BR4.5 y BR4.10. Sin red, reloj ni archivos. FR2.1, FR2.3, FR2.5, FR6.2, FR6.3, FR11.7, NFR11.
- [ ] Paso 4. Pruebas `despliegues/prueba_comun/pruebas/test_guion.py` con preguntas inventadas (nunca del banco): huella estable ante ids y orden; clave por texto completa e incompleta; reparto 40 → (20, 12, 8) y otro tamaño; mismo guion con la misma semilla; inválida por tipo; puntos esperados del perfecto y del cero; opacos y CSV. BR2.2 a BR3.3, BR5.3, BR5.4, BR6.1.
- [ ] Paso 5. Lógica pura `despliegues/prueba_comun/src/pantallas.py`: la tabla de los 27 ids `pantalla_*` (ruta, método, estado del reto, código esperado y claves de la columna «Qué usa la pantalla» de U6; Content-Type para CSV, zip y copia), las 6 que no aplican en local y `revisar(id, codigo, cuerpo, cabeceras)`. BR4.7, FR4.1.
- [ ] Paso 6. Pruebas `despliegues/prueba_comun/pruebas/test_pantallas.py`: hay exactamente 27 ids con los nombres de `functional-spec.md`; un cuerpo completo pasa; una clave que falta falla y la nombra; un archivo vacío o con otro Content-Type falla; las 6 de local están marcadas. BR4.7.
- [ ] Paso 7. Lógica pura `despliegues/prueba_comun/src/mediciones.py`: `armar` (C3 con `version_esquema` 1, partes `base`, `fugas`, `relojes`, `claves` y `nfr`, `nfr.colegios`, y las claves agregadas `duracion_min`, `vencimiento`, `no_aplica`, `p95_resumen_ms`, `fracciones`, `encabezados_csv`); `validar_medicion(medicion, clave)` (obligatorias, tipos, partes, sin secretos, sin la clave y sin `url` con `?`); `comparar_referencia` (BR8.2); `ruta_por_defecto(opcion, fecha)` → `mediciones/<opcion>_<AAAA-MM-DD>.json`; y las dos funciones de archivo, `escribir` y `leer_referencia`. FR12.4, C3, D8, BR8.1, BR8.2, NFR11.
- [ ] Paso 8. Pruebas `despliegues/prueba_comun/pruebas/test_mediciones.py`: una medición válida pasa y se escribe en una carpeta temporal; se rechazan `version_esquema` distinto de 1, una parte desconocida, un `detalle` con `veredicto` y un `detalle` o `url` con la clave docente; `no_aplica` no entra en `comprobaciones`; la comparación detecta una fracción y una columna distintas. BR8.1, BR8.2, U2-S4.
- [ ] Paso 9. Red `despliegues/prueba_comun/src/cliente.py`: `Cliente(url, clave)` con `pedir` (GET/POST, tope de 20 s, `X-Clave-Admin` solo cuando se pide, conteo de peticiones y latencia), lectura tolerante de JSON (BR1.4), `descargar` (cuerpo y Content-Type) y `__repr__` sin la clave. BR1.1, BR1.4, BR7.4, NFR9.
- [ ] Paso 10. Pruebas `despliegues/prueba_comun/pruebas/servidor_falso.py` (`http.server` en un puerto libre, respuestas fijas, guarda cabeceras y cuenta peticiones) y `test_cliente.py`: la clave llega en la cabecera sin cambios y nunca en la URL; un 500 sin JSON da `{"error": "la respuesta no es JSON"}`; sin conexión da 0; el conteo y la descarga son correctos; `repr` no muestra la clave. BR1.4, U2-S1.
- [ ] Paso 11. Carga `despliegues/prueba_comun/src/carga.py`: hilos de participantes que esperan el `Event` del arranque de su colegio, hilo de tablero cada 2 s (10 s en la espera) y de panel cada 3 s, `percentil` por vecino más cercano y `esperar_hasta(cliente, objetivo)` con `servidor_ahora`. BR6.1, BR6.2, BR7.1, NFR2, NFR3.
- [ ] Paso 12. Pruebas `despliegues/prueba_comun/pruebas/test_carga.py` con el servidor falso: percentil de listas conocidas; un hilo no empieza antes de su `Event`; el tablero se detiene con el `Event` de fin; `esperar_hasta` termina cuando `servidor_ahora` alcanza el objetivo. BR7.1, U2-R7.
- [ ] Paso 13. Pruebas `despliegues/prueba_comun/pruebas/test_contrato.py`: un lector mínimo de rutas (sin paquetes) lee `contrato_api.yaml` y exige que cada (método, ruta) que usa la prueba esté en `paths`. BR8.3.
- [ ] Paso 14. Pruebas `despliegues/prueba_comun/pruebas/test_sin_secretos.py`: `src/` no contiene `banco_preguntas` ni `open(` fuera de `mediciones.py`, y ningún `print` de `prueba.py` recibe la clave. NFR8, U2-S3, U2-S8.
- [ ] Paso 15. Orquestación `despliegues/prueba_comun/src/prueba.py` (reescrita): argumentos de `functional-spec.md` («Cómo se corre»), con la clave de `PRUEBA_CLAVE` (o `--clave`) y código 2 si falta URL, clave u opción; pasos F1 a F12 con las 30 comprobaciones base, los 27 `pantalla_*`, `tipos_respuesta`, `acciones_docente`, `cierre_no_inicio`, `resultados_por_grado`, `resultados_nota`, `paquete_completo` y las partes fugas, relojes, claves y nfr; esenciales que detienen (BR1.3); reto vacío (BR1.5); restauración en `finally`, también con Ctrl+C (BR1.6); `no_aplica` por modo y por `--vencimiento omitir`; impresión de BR1.2; JSON con `mediciones.py`. FR12.3, FR12.5, FR6.1 a FR6.3, FR11.5 a FR11.7, FR2.1 a FR2.6, FR3.1 a FR3.3, FR9.1, FR9.5, NFR1 a NFR6, NFR9, NFR11, D1 a D9.
- [ ] Paso 16. Configuración `despliegues/cloudflare/herramientas/verificar.sh`: si falta `.dev.vars`, lo crea con `CLAVE_DOCENTE` al azar y `DURACION_MINIMA_MIN=1`; si existe sin `DURACION_MINIMA_MIN`, lo agrega; exporta `PRUEBA_CLAVE` leída de `CLAVE_DOCENTE` y corre la prueba sin `--clave`, con `--modo nube --opcion cloudflare --duracion-min 2 --reinicio comando` (un comando que detiene y relanza `wrangler dev` en el mismo puerto y con el mismo estado de `.wrangler/`) y `--salida despliegues/prueba_comun/mediciones/cloudflare-dev_<AAAA-MM-DD>.json`. D9, NFR4, U2-S8.
- [ ] Paso 17. Documentación: reescribir `despliegues/prueba_comun/LEEME.md` (qué revisa cada parte, los tres comandos con la clave por el entorno, el reto vacío, qué no aplica en cada caso, la duración de cada corrida y el JSON de `mediciones/`) y ajustar en `despliegues/cloudflare/LEEME.md` la línea de `verificar.sh`. FR8.0, FR12.3.
- [ ] Paso 18. Corrida contra la versión local: `servidor.py` en el puerto 8790 con `RETO_CLAVE` y `--db`/`RETO_DATOS` en `despliegues/cloudflare/.wrangler/local-ref/`; `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8790 --modo local --opcion local` bajo `trace`. Se exige que pasen todas las comprobaciones de la parte `base` (las de fugas fallan mientras U3 siga saltada y los relojes van a `no_aplica`) y que se escriba `mediciones/local_<AAAA-MM-DD>.json`. FR12.3, NFR11.
- [ ] Paso 19. Corrida contra `wrangler dev`: `bash despliegues/cloudflare/herramientas/verificar.sh` termina en «TODO BIEN», con el vencimiento real de cada colegio, el reinicio por comando y `--referencia` al JSON local; la cobertura de `src/` sumando la suite y las corridas 18 y 19 es ≥ 80 %. FR11.7, NFR4, NFR11, NFR12, D9.
- [ ] Paso 20. Corrida contra la URL de Workers (la ejecuta el humano, sin reto en curso y con el reto vacío): `python3 despliegues/prueba_comun/src/prueba.py --url https://<nombre>.workers.dev --modo nube --opcion cloudflare --vencimiento omitir --reinicio manual --frio --referencia despliegues/prueba_comun/mediciones/local_<AAAA-MM-DD>.json`, con la clave en `PRUEBA_CLAVE`, termina en «TODO BIEN» y escribe `mediciones/cloudflare_<AAAA-MM-DD>.json`. NFR2 a NFR6, FR12.4.
- [ ] Paso 21. Cierre: `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` en «TODO BIEN»; `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío; `uv run ruff format --check` y `uv run ruff check` sobre `despliegues/prueba_comun`; ningún JSON de `mediciones/` contiene la clave, un token ni una respuesta correcta. FR12.1, NFR9.
