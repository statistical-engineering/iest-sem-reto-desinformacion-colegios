# Instrucciones de pruebas — U1

- Marco: `node:test` de Node 24, sin paquetes (ADR-W2). Prueba común: Python 3.12 sin paquetes.
- Comando de la unidad (desde la raíz del repo):
  `node --test --experimental-test-coverage despliegues/cloudflare/pruebas/reglas.test.js`
- Prueba común contra el corte en local (dos terminales):
  1. `cd despliegues/cloudflare && npx wrangler@4.148.0 dev --port 8787`
  2. `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8787 --clave "$CLAVE_SEMILLERO" --modo nube`
- Contra la versión local: `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8000 --clave <clave docente> --modo local`.
- Cobertura objetivo: 80 % de líneas de `src/reglas.js` (piso del alcance `classic`).
- Sin mocks en las reglas puras: reciben datos y la hora. Datos de prueba: un banco mínimo armado en la
  prueba y el banco real para `validar_banco`; nunca se copian respuestas del banco a las pruebas.
