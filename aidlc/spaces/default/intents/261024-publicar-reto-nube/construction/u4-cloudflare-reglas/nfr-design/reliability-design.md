# Confiabilidad — diseño U4

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
  `export const limpiar = normalizar_texto`; `pruebas/reglas.test.js` de U1 se conserva tal cual hasta
  que sus casos se repartan en los archivos nuevos, y en ese momento se borra en el mismo push.
- Copia al día (U4-R5): `verificar.sh` calcula `sha256sum` de `despliegues/prueba_comun/casos_reglas.json`
  y de `despliegues/cloudflare/pruebas/casos_reglas.json` y se detiene si difieren, antes de correr
  `node --test`.
