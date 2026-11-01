# Instrucciones de pruebas — U6

- Marco: `node:test` de Node 24, sin paquetes (ADR-W2). Prueba común: Python 3.12 sin paquetes. Cada
  archivo se nombra: `node --test` con una carpeta falla en Node 24 (`project.md`, «Corrections»).
- Comandos de la unidad (desde la raíz del repo):
  - `node --test despliegues/cloudflare/pruebas/exportacion.test.js` (csv, zip, copia, fechas, columnas
    secretas, clave de prueba fuera del `.zip`, encabezados contra el diccionario);
  - `node --test despliegues/cloudflare/pruebas/resultados.test.js` (vista del estudiante y tablero);
  - `node --test despliegues/cloudflare/pruebas/pantallas.test.js` (ninguna pantalla llama una ruta que
    no exista ni escribe `?sala=` o `?clave=`, BR10.1);
  - las de U4 y U5 siguen: `node --test despliegues/cloudflare/pruebas/reglas.test.js`.
- Cobertura: `node --test --experimental-test-coverage despliegues/cloudflare/pruebas/exportacion.test.js despliegues/cloudflare/pruebas/resultados.test.js`;
  objetivo 80 % de líneas de `src/servicios/csv.js`, `zip.js`, `copia.js` y `resultados.js` (piso del
  alcance `classic`; no se baja para que pase).
- Prueba común contra `wrangler dev` (dos terminales):
  1. `.dev.vars` con `CLAVE_DOCENTE` (12 o más caracteres, solo de prueba, nunca versionada) y
     `DURACION_MINIMA_MIN=1` (D9);
  2. `cd despliegues/cloudflare && npx wrangler@4.148.0 dev --port 8787`;
  3. `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8787 --clave "$PRUEBA_CLAVE" --modo nube --opcion cloudflare`
     (opciones completas en `../../u2-prueba-comun/functional-design/functional-spec.md`). La clave va
     solo en la cabecera `X-Clave-Admin`.
- Contra la versión local (para comparar los dos CSV byte a byte): desde `2_Aplicacion_Reto/`,
  `python3 servidor.py --puerto 8790 --clave <clave de ensayo> --db <carpeta temporal>/reto.db` y
  `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8790 --clave "$PRUEBA_CLAVE" --modo local --opcion local`.
  Nunca contra `datos/reto.db`.
- Todo junto: `bash despliegues/cloudflare/herramientas/verificar.sh` (código 0) y, desde
  `2_Aplicacion_Reto/`, `python3 pruebas/simulacro.py 40` en «TODO BIEN».
- Recorrido manual de `/`, `/admin` y `/tablero` en `wrangler dev`: lista de `../functional-design/functional-spec.md`
  («Recorrido de las pantallas»), consola del navegador abierta, resultado en `code-summary.md`.
- Reglas de las pruebas: una conducta por prueba, sin `if` ni `try` dentro, por la interfaz pública, sin
  mocks en la lógica pura (reciben datos y la hora). Datos de prueba inventados en la prueba; nunca se
  copian respuestas de `banco_preguntas.json` ni de `3_Guia_docente/`.
