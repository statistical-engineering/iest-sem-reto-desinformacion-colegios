# Seguridad — U5

> **Revisión 2026-10-27 (una sola sala).** Una sola sala, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`) y un reloj por colegio (ADR-009 a ADR-011, `../functional-design/`, D1 a D10 de
> `contract-design-questions.md`). Se quitan la clave del semillero, las claves de sala, crear o borrar
> salas y el catálogo. Los ids retirados no se reutilizan. Retirados: U5-S2 (rutas del semillero), U5-S3 (regenerar clave de sala) y U5-S7 (borrar sala).
> Nuevos: U5-S9 a U5-S12.

Requisitos no funcionales de U5, reto, colegios y relojes en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Decisiones tomadas por el asistente con la potestad que dio el humano. Los de U1 (U1-S1 a U1-S9) siguen vigentes salvo lo que hablaba de la clave del semillero.

| Id | Requisito | Origen |
|---|---|---|
| U5-S1 | Toda ruta `/api/admin/*` exige `X-Clave-Admin` igual a `CLAVE_DOCENTE`, comparada en tiempo constante, sin espacios en los extremos y sin cambiar mayúsculas; un `id` de participante o colegio que no existe da 404 | BR1.3, BR1.4, NFR9 |
| U5-S2 | Retirado el 2026-10-27: no hay rutas del semillero | — |
| U5-S3 | Retirado el 2026-10-27: no hay claves de sala que regenerar | — |
| U5-S4 | No hay bloqueo por intentos fallidos; la espera de 600 ms ante clave ausente o incorrecta corre fuera del bloqueo del objeto para que no frene a los equipos | ADR-010, ADR-W12, BR1.3 |
| U5-S5 | `resumen`, `colegios` y `publico` nunca traen `token` ni `semilla`; `colegios[]` de `/api/publico` lleva nombre y reloj, sin equipos ni datos personales | NFR9, NFR10, BR4.5, D10 |
| U5-S6 | Las respuestas de los 10 tipos se validan en el servidor antes de guardarse (tipo, tamaño, ids), aunque la petición no venga de `web/js/`; las guardadas salen al navegador solo con ids opacos | FR10.1, BR6.1, `phases/construction.md` («Security») |
| U5-S7 | Retirado el 2026-10-27: no se borra una sala («Reiniciar» es de U6) | — |
| U5-S8 | El resumen del panel trae el experimento completo solo porque va con clave; nada del experimento ni respuestas correctas salen sin clave antes de resultados | FR6.1, NFR8, `project.md` («Forbidden») |
| U5-S9 | Una petición a `/api/admin/*` con `clave` en la URL recibe 403 aunque la cabecera sea correcta | BR1.5, D6, `project.md` («Corrections») |
| U5-S10 | El servicio no atiende si `CLAVE_DOCENTE` falta o tiene menos de 12 caracteres; la clave nunca va en un archivo versionado: `.dev.vars` (ignorado) en local y `wrangler secret put` en la nube | BR1.6, NFR9, `project.md` («Forbidden») |
| U5-S11 | Ninguna ruta ni opción pública mueve un reloj: el arranque es la hora del servidor (BR4.4) y `DURACION_MINIMA_MIN` solo existe en `.dev.vars` para `wrangler dev`, nunca en `wrangler.jsonc` ni como secreto del despliegue | D9, BR4.4, OQ3 |
| U5-S12 | Las tablas `v1_*` que deja la migración no salen por ninguna ruta | ADR-W19, NFR10 |
