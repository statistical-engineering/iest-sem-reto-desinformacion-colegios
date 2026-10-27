# Seguridad — diseño U5

> **Revisión 2026-10-27 (una sola sala).** Una sola clave, `CLAVE_DOCENTE`, solo por `X-Clave-Admin`
> (ADR-010, D6). Retirados U5-S2, U5-S3 y U5-S7 (semillero, claves de sala, borrar sala); nuevos U5-S9
> a U5-S12.

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U5-S1 | `acceso_admin` lee `X-Clave-Admin`, quita espacios de los extremos y la compara con `env.CLAVE_DOCENTE` con `iguales_en_tiempo_constante` (U1), sin pasar a mayúsculas; desaparecen `clave_semillero`, `sala_de_acceso` y los niveles `semillero` y `sala`. `participante` y `colegios` buscan por id y responden 404 si no está |
| U5-S4 | `ErrorAPI` con `esperar_ms = 600` cuando la clave falta o no coincide; `Reto.fetch` ya espera fuera del bloqueo |
| U5-S5 | Las consultas de `resumen`, `colegios` y `publico` nombran columnas, nunca `SELECT *`; `colegios[]` público lleva solo el nombre y el reloj de `estado_reloj` |
| U5-S6 | `responder` pasa por `traducir_respuesta` → `validar_respuesta` → `fraccion` de U4; la respuesta guardada sale con `respuesta_opaca` para todos los tipos |
| U5-S8 | `resumen` llama a `calcular` (completo); `publico` no trae experimento en U5 (lo agrega U6 con `experimento_publico`) |
| U5-S9 | Antes de mirar la cabecera, `dar_acceso` responde 403 si la URL de una ruta `/api/admin/*` trae el parámetro `clave` |
| U5-S10 | En el constructor, si `env.CLAVE_DOCENTE` falta o, sin espacios, mide menos de 12 caracteres, se fija `error_arranque` y toda ruta responde 500. `verificar.sh` crea `.dev.vars` (ignorado) con una clave al azar de 24 caracteres; en la nube, `npx wrangler@4.148.0 secret put CLAVE_DOCENTE` |
| U5-S11 | El mínimo de `duracion_min` es 10 salvo que `env.DURACION_MINIMA_MIN` diga otro número; esa variable solo se escribe en `.dev.vars`. Ninguna ruta recibe una hora: `arrancar` usa la hora del servidor |
| U5-S12 | Ninguna consulta de las rutas nombra una tabla `v1_*`; solo la migración 2 las crea y la 3 (U6) las lee |

OQ5 (nombres de menores en el tablero público): se conserva como hoy, porque cambiarlo altera la
conducta visible (`project.md`, «Forbidden»); la guía del docente recomienda proyectar el tablero
solo en el aula. La alternativa de mostrar solo el código personal queda anotada y rechazada por ese
motivo (A2 de `requirements.md`).
