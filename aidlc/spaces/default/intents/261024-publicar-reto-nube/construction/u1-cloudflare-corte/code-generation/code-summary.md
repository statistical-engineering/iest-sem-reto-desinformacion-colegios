# Resumen de código: U1 `u1-cloudflare-corte`

Corte delgado del reto en Cloudflare Workers, construido con el plan aprobado de 13 pasos
(`code-generation-plan.md`) y `unit-test-instructions.md`. Metodología test-after, estrategia standard,
alcance classic y piso de 80 % de cobertura de líneas.

## Qué se hizo

- Un Worker (`src/worker.js`) que no tiene lógica: pasa `/api/*` al único Durable Object `Reto` y
  responde 404 a lo demás. Si el objeto no responde, contesta 503 (contrato C1).
- El Durable Object `Reto` (`src/reto.js`) con SQLite: tablas `salas`, `colegios`, `sala_colegios`,
  `participantes`, `respuestas` y `eventos`, con `UNIQUE` en códigos, token, nombre normalizado del
  colegio, la inscripción (sala, nombre, colegio, grado) y (participante, pregunta). Cada petición se
  atiende dentro de `blockConcurrencyWhile`, como el bloqueo de `servidor.py`. Tiene la tabla de rutas del
  corte, los niveles público, token y clave, un tope de 65.536 bytes por cuerpo y una sola salida de
  errores.
- Las reglas sin E/S (`src/reglas.js`): validación del banco y su huella, examen público con lista blanca
  de claves, ids opacos HMAC-SHA256 con la semilla del participante, validación y calificación de
  `opcion`, bono, cierre del intento, transición de estado y hora de entrega.
- Las pantallas de `2_Aplicacion_Reto/web/` copiadas con `herramientas/copiar.sh` y los dos cambios del
  corte guardados en `herramientas/cambios_web.patch`: la lista de colegios en la inscripción
  (`/api/colegios?sala=`) y el `?sala=` del tablero, que sin sala muestra «Abre el tablero con el enlace
  de tu sala.».
- La prueba común mínima (`despliegues/prueba_comun/src/prueba.py`, solo biblioteca estándar): los 8
  pasos de `functional-spec.md`, la clave en la URL rechazada, las pantallas con 200 y el banco con 404,
  en `--modo nube` y `--modo local`.
- Los dos `LEEME.md`, con los pasos del semillero en palabras simples: cuenta gratuita, `login`,
  `secret put CLAVE_SEMILLERO`, `deploy`, prueba común y `rollback`.

## Archivos

Todos bajo `despliegues/`; el detalle está en `source-manifest.json`.

| Archivo | Qué es | Líneas |
|---|---|---|
| `cloudflare/wrangler.jsonc` | Worker, recursos estáticos en `./web` y Durable Object con `new_sqlite_classes` | 20 |
| `cloudflare/.gitignore` | deja fuera `.wrangler/` y `.dev.vars` | 4 |
| `cloudflare/herramientas/copiar.sh` | copia pantallas y banco, aplica el parche y escribe la huella | 45 |
| `cloudflare/herramientas/cambios_web.patch` | los dos cambios de pantalla de la nube | 88 |
| `cloudflare/src/worker.js` | entrada del Worker | 26 |
| `cloudflare/src/reto.js` | Durable Object: esquema, rutas y accesos | 754 |
| `cloudflare/src/reglas.js` | reglas puras | 495 |
| `cloudflare/src/banco.json`, `banco_huella.json` | copia generada del banco y su huella | generados |
| `cloudflare/web/` | pantallas copiadas y parchadas | generadas |
| `cloudflare/pruebas/reglas.test.js` | 23 pruebas unitarias (`node:test`) | 263 |
| `prueba_comun/src/prueba.py` | prueba común mínima | 368 |
| `cloudflare/LEEME.md`, `prueba_comun/LEEME.md` | pasos para el semillero y cómo correr la prueba | doc |

Se borró `despliegues/cloudflare/web/.gitkeep` (versionado), porque `copiar.sh` rehace `web/` entero.

## Resultados de las pruebas

Todas corridas en esta máquina el 2026-10-25.

| Verificación | Comando | Resultado |
|---|---|---|
| Pruebas unitarias | `node --test --experimental-test-coverage despliegues/cloudflare/pruebas/reglas.test.js` | 23 de 23 pasan en 3 grupos; `reglas.js` con 100 % de líneas, 96,75 % de ramas y 100 % de funciones (piso: 80 % de líneas) |
| Prueba común en la nube | `npx wrangler@4.148.0 dev --port 8787` y `prueba.py --url http://localhost:8787 --modo nube` | «TODO BIEN», 38 de 38 comprobaciones, código 0; repetida tras el último cambio de `reto.js` con el mismo resultado |
| Prueba común en local | `servidor.py --puerto 8790` con `RETO_DATOS` y `--db` en `cloudflare/.wrangler/local-ref/` (ignorado) y `prueba.py --modo local` | «TODO BIEN», 26 de 26 comprobaciones, código 0 |
| Simulacro de la versión local | `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` | «TODO BIEN: el reto está listo.», 30 comprobaciones, ninguna falla |
| Ruff | `uv run ruff format despliegues/prueba_comun` y `uv run ruff check despliegues/prueba_comun` | 1 archivo formateado; «All checks passed!» |
| Sintaxis de pantallas | `node --check` de `estudiante.js` y del script de `tablero.html` | sin errores |
| Parche reaplicable | `copiar.sh` dos veces y `sha256sum` de los archivos parchados | mismas huellas antes y después; `2_Aplicacion_Reto/` sin cambios |

Al arrancar, Wrangler registró «Arranque: banco 18f0f539fc, 42 preguntas.»: el banco se valida y su
huella coincide.

## Pruebas escritas sin correr y lo que queda sin medir

- No se publicó en `workers.dev`: lo hace el semillero a mano (FR5.1, FR5.2). Por eso no se midieron
  contra la URL publicada el p95 (U1-P1 y U1-P2), el arranque en frío (U1-R3) ni el consumo de cuota
  (U1-E2 y U1-E3); quedan para Build and Test.
- No hay CI aprobada que corra estas pruebas: `revisar-pr.yml` corre los ganchos, el simulacro y el
  límite de líneas. Las pruebas de esta unidad se corren a mano.
- Las pantallas no se probaron en un navegador: Chrome no arranca en esta máquina sin desactivar su
  sandbox, y no se desactivó. Se revisaron la sintaxis y las rutas que piden.

## Desviaciones del plan y su motivo

1. **Forma de `web/`.** `estudiante.html` queda como `web/index.html`, y `css/` y `js/` dentro de
   `web/static/`. Así los recursos estáticos de Workers sirven `/`, `/admin`, `/tablero` y `/static/...`
   sin lógica en el Worker. El contenido se copia sin cambios.
2. **«Commit aparte» del Paso 9.** El brief prohíbe hacer commits. La separación entre la copia sin
   cambios y los cambios del corte queda en `cambios_web.patch`, que `copiar.sh` aplica después de copiar.
3. **Huella del banco en vez de su `version`.** El `version` de Python no se puede recalcular en JS:
   cambia el formato de los decimales (salió 862860fc9c frente a 18f0f539fc). `copiar.sh` guarda
   sha256 de `JSON.stringify` del banco y el Worker la compara al arrancar.
4. **`casos_reglas.json` no se creó.** No está en el plan de U1; la tabla compartida de casos queda para
   U4.
5. **Panel docente limitado.** `admin.js` pide `/api/admin/resumen`, que llega con U5. Hoy da 404 y el
   panel se queda en el ingreso tras entrar, como prevé `functional-spec.md` («Pantallas»).
6. **`revelar_tras` sale al navegador.** Es solo el id de la pregunta que abre el dossier, y la versión
   local también lo envía; no es una respuesta.
7. **Comando de pruebas.** `node --test despliegues/cloudflare/pruebas/` (con la carpeta) falla en Node
   24; hay que nombrar el archivo. `infrastructure-design/cicd-pipeline.md` nombra la carpeta.
8. **Riesgo de pre-commit sobre `src/banco.json`.** `end-of-file-fixer` y `trailing-whitespace` pueden
   tocarlo. La huella resiste porque se calcula sobre el JSON leído y vuelto a escribir.
9. **Nombres snake_case en JS.** Siguen la forma del contrato C4 en vez de camelCase.
10. **`reto.js` pasa de 300 líneas.** Lo pide ADR-W3: un solo objeto con todas las rutas del corte.
11. **`copiar.sh` ejecutable.** Se le dio permiso de ejecución con `chmod +x`.
12. **`/api/publico?sala=` trae más campos.** Incluye `urls`, `cerrado_en` y `modo_sorpresa`, que el
    tablero copiado ya lee.
13. **Caché del examen por semilla.** Se agregó para no rehacer los HMAC en cada `/api/estado` y cuidar
    el límite de CPU.
14. **Orden de publicaciones.** Fuera de la misión 1, las publicaciones se ordenan por id opaco, igual
    que las opciones.
15. **Errores 500 con traza.** Se registra `error.stack` para cumplir U1-O1; el mensaje al navegador
    sigue sin detalles (U1-S9).
16. **Prueba común con más casos.** Además de los 8 pasos, revisa la clave en la URL, la clave de una
    sala sobre otra, el colegio fuera de la lista, el código que no existe y el banco con 404.

## Notas para quien sigue

- `.dev.vars` tiene una clave de prueba inventada, ignorada por git; nunca va una clave real.
- `2_Aplicacion_Reto/INICIAR_RETO_INTERNET.bat` ya figuraba modificado antes de esta unidad; no se tocó.
- Esta unidad suma más de 400 líneas de código. El humano y el asistente suben directo a `develop` sin
  PR (`team.md`, «Corrections»: regla del 2026-10-25 que exime solo al humano y al asistente); si
  la sube otra persona del equipo, hay que partirla en varios PR.
