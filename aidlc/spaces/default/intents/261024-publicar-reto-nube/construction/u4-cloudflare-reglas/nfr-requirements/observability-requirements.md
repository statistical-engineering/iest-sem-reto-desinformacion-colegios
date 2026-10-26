# Observación — U4

Requisitos no funcionales de U4, las reglas puras de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C4. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U4-O1 | Las reglas no escriben en el registro (`console.*`): un error de regla sube como excepción y lo registra la única salida de errores de `reto.js` (U1-O1) | `.claude/rules/python-code.md` («Logs», aplicado igual a JS), ADR-001 |
| U4-O2 | Cada prueba con la tabla nombra en su título la regla, la función y el índice del caso (`Calificacion.fraccion caso 12`), para que un fallo diga qué caso falló sin abrir el JSON | NFR12 |
| U4-O3 | La cobertura de líneas de `src/reglas/` se imprime en cada corrida (`--experimental-test-coverage`) y `verificar.sh` falla si baja de 80 % | NFR12, `team.md` («Testing Posture») |
