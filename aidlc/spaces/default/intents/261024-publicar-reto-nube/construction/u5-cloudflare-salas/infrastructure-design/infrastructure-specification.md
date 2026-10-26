# Infraestructura — U5 `u5-cloudflare-salas`

Sale de `../nfr-design/` y de `../decisions.md` (ADR-W10 a ADR-W13). Mismas piezas que U1
(`../../u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`); U5 cambia el esquema
de datos y las pantallas, no la plataforma. Todo en el plan gratuito.

## Piezas

| Pieza | Cambio en U5 | Dónde |
|---|---|---|
| Worker `reto-desinformacion` | Sin cambio en `wrangler.jsonc` | `despliegues/cloudflare/wrangler.jsonc` |
| Durable Object `Reto` | Sin migración de clase (`migrations` de `wrangler.jsonc` se queda en `v1`); el **esquema SQL** pasa a la versión 2 con `PRAGMA user_version` al primer arranque después del despliegue (ADR-W10) | `src/reto.js` |
| Secreto `CLAVE_SEMILLERO` | Sin cambio | cuenta de Cloudflare |
| Recursos estáticos | `web/` se rehace con `copiar.sh` y el parche ampliado del panel | `herramientas/cambios_web.patch` |

## Pasos (los pone en palabras simples `despliegues/cloudflare/LEEME.md`)

1. Confirmar en el panel del semillero que ninguna sala está en «abierto» (`GET /api/admin/salas`):
   no se despliega con un reto en curso.
2. `bash despliegues/cloudflare/herramientas/copiar.sh` y `bash despliegues/cloudflare/herramientas/verificar.sh`.
3. `npx wrangler@4.148.0 deploy`.
4. Abrir `/api/publico` y después el panel: en `wrangler tail` debe verse «Migración v2 aplicada.» una
   sola vez.
5. Prueba común contra el enlace.

Volver atrás: `npx wrangler@4.148.0 rollback`. El código anterior (U1) ignora la columna `unido_a` y
sigue funcionando con el esquema v2; no hay que deshacer la migración.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
