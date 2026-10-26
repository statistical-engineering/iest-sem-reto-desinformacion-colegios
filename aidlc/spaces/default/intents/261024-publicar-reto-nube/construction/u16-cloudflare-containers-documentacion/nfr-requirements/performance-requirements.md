# Rapidez — U16

Requisitos no funcionales de U16, unidad de solo documentación sobre Cloudflare Containers. Salen de
`requirements.md` (NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Cifras de la documentación
oficial consultada el 2026-10-25. Decisiones del asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U16-P1 | NFR2 y NFR3 no se miden: la opción no se despliega (FR12.2a). La tabla dice «sin medir» y el motivo | Lectura de la columna | NFR2, NFR3, FR12.2a |
| U16-P2 | El arranque en frío se anota con la cifra oficial («1-3 second range», https://developers.cloudflare.com/containers/platform-details/) y se compara con los 30 s de NFR5 | Lectura de la columna | NFR5 |
