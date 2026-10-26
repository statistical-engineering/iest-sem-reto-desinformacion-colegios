# Seguridad — U16

Requisitos no funcionales de U16, unidad de solo documentación sobre Cloudflare Containers. Salen de
`requirements.md` (NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Decisiones del asistente con la
potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U16-S1 | La columna y este diseño no llevan claves, tokens, respuestas del banco ni datos de participantes | NFR8, NFR9, BR16.7 |
| U16-S2 | No se activa Workers Paid ni se guarda tarjeta; no hay secreto que configurar | FR12.2a |
| U16-S3 | NFR10 y NFR10.1 no se evalúan: no hay datos en Containers. Si se aprobara, las instantáneas duran 30 días (https://developers.cloudflare.com/containers/platform-details/limits/) y el cierre tendría que borrarlas | NFR10.1 |
