# Observación — diseño U4

> **Revisión 2026-10-27 (una sola sala).** El piso de 80 % lo exige la opción de Node `--test-coverage-lines=80` en vez de leer el resumen.

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

- Ningún `console.*` en `src/reglas/` (U4-O1); `verificar.sh` lo comprueba con `grep`.
- `casos_reglas.test.js` genera una prueba por caso con `test(`${regla}.${funcion} caso ${i}`)`, así el
  informe de `node --test` nombra el caso que falló (U4-O2).
- La cobertura se pide con `--experimental-test-coverage` y `--test-coverage-include` limitado a
  `src/reglas/**`, más `--test-coverage-lines=80`: `node --test` termina con error por debajo de 80 % de
  líneas y `verificar.sh` se detiene (U4-O3).
