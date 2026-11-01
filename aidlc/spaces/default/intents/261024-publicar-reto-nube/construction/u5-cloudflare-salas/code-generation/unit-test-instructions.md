# Instrucciones de pruebas — U5

- Marco: `node:test` de Node 24, sin paquetes (ADR-W2). Prueba común: Python 3.12 sin paquetes.
- Reglas puras (de U4, deben seguir verdes), desde la raíz del repo y nombrando cada archivo, porque
  `node --test` con una carpeta falla en Node 24 (`project.md`, «Corrections»):
  - `node --test --experimental-test-coverage despliegues/cloudflare/pruebas/reglas.test.js`
  - `node --test --experimental-test-coverage despliegues/cloudflare/pruebas/casos_reglas.test.js`
- Clave de prueba: `despliegues/cloudflare/.dev.vars` (ignorado por git) con la línea
  `CLAVE_DOCENTE=<24 caracteres al azar>`; `verificar.sh` la crea si falta. Nunca se copia a otro archivo
  ni se escribe una clave real. Para probar a mano el vencimiento se puede agregar
  `DURACION_MINIMA_MIN=1` en ese mismo archivo (D9); nunca en `wrangler.jsonc`.
- Prueba común mínima contra U5 en local (dos terminales):
  1. `cd despliegues/cloudflare && npx wrangler@4.148.0 dev --port 8787`
  2. `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8787 --clave "$(sed -n 's/^CLAVE_DOCENTE=//p' despliegues/cloudflare/.dev.vars)" --modo nube`
  Debe terminar en «TODO BIEN». Cubre: 403 con clave ausente, incorrecta y con `?clave=` (BR1.3, BR1.5);
  404 en las rutas quitadas (BR1.1); colegios y relojes (BR4.2 a BR4.4); el aviso de espera al comenzar
  sin arranque (BR6.4); una respuesta aceptada y una repetida rechazada (BR6.1); cierre (BR2.3);
  resumen y tablero sin `token` ni `semilla` (BR7.1, BR7.2).
- Contra la versión local: `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8000 --clave <clave docente> --modo local`
  (la parte base no cambia, FR11.7).
- Migración F8, a mano y una vez antes de desplegar:
  1. Con el código del corte (U1, commit `9ed6b4c`) en una copia aparte, `wrangler dev` y su prueba común
     mínima para dejar datos en `.wrangler/`.
  2. Con el código de U5 sobre ese mismo estado local, `wrangler dev`.
  3. Comprobar: «Migración v2 aplicada.» en el registro; `user_version` = 2; `v1_salas` y
     `v1_participantes` con las filas de antes; `reto` con una fila en «inscripción»; `colegios` y
     `participantes` vacías; el panel entra con la clave docente. Anotar el resultado en `code-summary.md`.
- Todo junto: `bash despliegues/cloudflare/herramientas/verificar.sh` debe terminar con código de salida
  0, y `python3 pruebas/simulacro.py 40`, desde `2_Aplicacion_Reto/`, en «TODO BIEN».
- Cobertura objetivo: 80 % de líneas del código nuevo (piso del alcance `classic`). Las reglas puras se
  miden con `--experimental-test-coverage`; `src/reto.js` y `src/servicios/` corren dentro de
  `wrangler dev` y no tienen medida automática (ver pregunta abierta en el informe de la etapa).
- Sin mocks en las reglas puras; las rutas se prueban por HTTP. Datos de prueba: nombres inventados con
  sufijo al azar; nunca se copian respuestas correctas del banco a las pruebas: la prueba común solo
  comprueba que una respuesta se acepta una vez y se rechaza la segunda, no si es correcta.
