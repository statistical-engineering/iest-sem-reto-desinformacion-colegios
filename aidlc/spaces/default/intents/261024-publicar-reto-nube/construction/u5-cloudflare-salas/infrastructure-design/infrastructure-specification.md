# Infraestructura — U5 `u5-cloudflare-salas`

> **Revisión 2026-10-27 (una sola sala).** El secreto pasa de `CLAVE_SEMILLERO` a `CLAVE_DOCENTE`
> (ADR-010); el paso 1 ya no consulta salas sino el estado del reto; la vuelta atrás es redesplegar U5,
> no U1, porque el código del corte no conoce el esquema v2 (ADR-W10, «Consequences»).

Sale de `../nfr-design/` y de `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20). Mismas piezas que
U1 (`../../u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`); U5 cambia el
esquema de datos, el secreto y las pantallas, no la plataforma. Todo en el plan gratuito.

## Piezas

| Pieza | Cambio en U5 | Dónde |
|---|---|---|
| Worker `reto-desinformacion` | Solo el comentario de cabecera de `wrangler.jsonc` (nombra `CLAVE_DOCENTE`); sin `vars` nuevas | `despliegues/cloudflare/wrangler.jsonc` |
| Durable Object `Reto` | Sin migración de clase (`migrations` se queda en `v1`); el **esquema SQL** pasa a la versión 2 con `PRAGMA user_version` al primer arranque después del despliegue (ADR-W10, ADR-W19) | `src/reto.js` |
| Secreto `CLAVE_DOCENTE` | Nuevo: 12 caracteres o más (BR1.6). En local va en `.dev.vars` (ignorado por git); en la nube con `npx wrangler@4.148.0 secret put CLAVE_DOCENTE`. Nunca en un archivo versionado | cuenta de Cloudflare |
| Secreto `CLAVE_SEMILLERO` | Se borra después del despliegue de U5 (`npx wrangler@4.148.0 secret delete CLAVE_SEMILLERO`); el código ya no lo lee | cuenta de Cloudflare |
| `DURACION_MINIMA_MIN` | Solo en `.dev.vars` para `wrangler dev` (D9); nunca en `wrangler.jsonc` ni como secreto | máquina local |
| Recursos estáticos | `web/` se rehace con `copiar.sh` y el parche ampliado | `herramientas/cambios_web.patch` |

## Pasos (los pone en palabras simples `despliegues/cloudflare/LEEME.md`)

1. Confirmar que no hay un reto en curso: `GET /api/publico` no debe estar en «abierto» (`project.md`,
   «Mandated»).
2. `bash despliegues/cloudflare/herramientas/copiar.sh` y `bash despliegues/cloudflare/herramientas/verificar.sh`
   (código de salida 0).
3. `npx wrangler@4.148.0 secret put CLAVE_DOCENTE` (la escribe el semillero; no queda en ningún archivo).
4. `npx wrangler@4.148.0 deploy`.
5. Abrir `/api/publico` y después el panel con la clave docente: en `wrangler tail` debe verse «Migración
   v2 aplicada.» una sola vez.
6. Prueba común mínima contra el enlace y luego `npx wrangler@4.148.0 secret delete CLAVE_SEMILLERO`.

Volver atrás: `npx wrangler@4.148.0 rollback` solo a otra versión de U5 o posterior. Volver al código del
corte (U1) no sirve: no conoce las tablas del esquema v2 (ADR-W10). Si U5 falla tras migrar, se corrige
y se redespliega U5; los datos del corte siguen en `v1_*`.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
