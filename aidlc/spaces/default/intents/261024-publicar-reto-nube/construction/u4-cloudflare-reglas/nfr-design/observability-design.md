# Observación — diseño U4

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

- Ningún `console.*` en `src/reglas/` (U4-O1); `verificar.sh` lo comprueba con `grep`.
- `casos_reglas.test.js` genera una prueba por caso con `test(`${regla}.${funcion} caso ${i}`)`, así el
  informe de `node --test` nombra el caso que falló (U4-O2).
- La cobertura se pide con `--experimental-test-coverage` y `--test-coverage-include` limitado a
  `src/reglas/`; `verificar.sh` lee el resumen y falla por debajo de 80 % de líneas (U4-O3).
