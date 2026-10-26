# Confiabilidad — U16

Requisitos no funcionales de U16, unidad de solo documentación sobre Cloudflare Containers. Salen de
`requirements.md` (NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Cifras de la documentación
oficial consultada el 2026-10-25. Decisiones del asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U16-R1 | NFR4 queda «no cumple» con el `Dockerfile` actual: «All disk is ephemeral by default» y al dormir arranca con disco nuevo (https://developers.cloudflare.com/containers/platform-details/) | NFR4, FR12.2 |
| U16-R2 | La columna anota las dos alternativas documentadas (instantáneas inmutables con `durable_object`; FUSE a R2, https://developers.cloudflare.com/containers/faq/) y que las dos cambian la aplicación | NFR4 |
| U16-R3 | NFR5 queda «cumple según documentación, sin medir»: «1-3 second range» | NFR5 |
| U16-R4 | La columna anota el apagado a mitad del reto: `sleepAfter` de 10 min por defecto y «the platform can stop an active container at any time» con `SIGTERM`, hasta 15 min y `SIGKILL` (https://developers.cloudflare.com/containers/faq/) | NFR4, `project.md` («no cambiar nada con un reto en curso») |
| U16-R5 | NFR11 no se evalúa: no hay código desplegado | NFR11 |
