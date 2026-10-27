# Confiabilidad — diseño U4

> **Revisión 2026-10-27 (una sola sala).** Se agrega U4-R6 (relojes por colegio); `pruebas/reglas.test.js` de U1 se conserva sin cambios durante U4 como prueba de que la fachada no rompe nada.

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

- Determinismo (U4-R1): sin reloj ni azar dentro de las reglas; la hora y la semilla llegan como
  argumentos. `variante_de` usa `BigInt` sobre el SHA-256 completo, como `int(hexdigest, 16)` en Python.
- Igualdad numérica (U4-R2): cada fórmula se escribe con el orden de operaciones de `servidor.py`
  (ADR-W8). La prueba con la tabla compara con `assert.deepEqual` salvo cuando el caso trae
  `tolerancia`, y entonces compara número a número recorriendo el objeto.
- Errores controlados (U4-R3): las funciones de validación devuelven valores, no lanzan; el único
  `throw` de `src/reglas/` es el `RangeError` de `fraccion` para un tipo desconocido, que
  `validar_banco` hace imposible en producción porque rechaza tipos fuera de la lista de 10.
- Compatibilidad con U1 (U4-R4): `src/reglas.js` reexporta cada archivo y define
  `export const limpiar = normalizar_texto`, `export const normalizar_nombre = normalizar_nombre_colegio`
  y `export const ESTADOS_SALA = ESTADOS_RETO`; `pruebas/reglas.test.js` de U1 se conserva sin cambios
  durante U4 (sus 23 pruebas prueban la fachada). Los alias se quitan cuando U5 deje de usarlos.
- Copia al día (U4-R5): `verificar.sh` calcula `sha256sum` de `despliegues/prueba_comun/casos_reglas.json`
  y de `despliegues/cloudflare/pruebas/casos_reglas.json` y se detiene si difieren, antes de correr
  `node --test`.
- Relojes por colegio (U4-R6): `estado_reloj`, `puede_comenzar` y `hora_de_entrega` reciben el `arranque`
  del colegio como dato y nunca la hora de otro colegio; `cerrar_intento` recibe `inicio = arranque`. El caso
  B de BR7.3 lo comprueba el propio generador contra `clasificacion()` antes de escribir la tabla.
