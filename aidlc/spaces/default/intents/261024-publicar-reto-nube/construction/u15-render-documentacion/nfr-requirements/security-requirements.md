# Seguridad — U15

Requisitos no funcionales de U15, unidad de solo documentación sobre Render. Salen de `requirements.md`
(NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Decisiones del asistente con la potestad que dio
el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U15-S1 | La columna y este diseño no llevan claves, tokens, respuestas del banco ni datos de participantes | NFR8, NFR9, BR15.6 |
| U15-S2 | No se crea cuenta ni se guarda tarjeta en Render para esta unidad; no hay secreto que configurar | FR12.2a |
| U15-S3 | NFR10 y NFR10.1 no se evalúan: no hay datos en Render. Si se aprueba el costo, el ADR de esa opción fija el borrado del disco y de sus copias de 7 días (https://render.com/docs/disks) | NFR10.1 |
