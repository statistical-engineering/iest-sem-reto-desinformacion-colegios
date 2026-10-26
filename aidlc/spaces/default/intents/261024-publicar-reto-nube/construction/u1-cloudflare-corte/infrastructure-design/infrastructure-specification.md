# Infraestructura — U1 `u1-cloudflare-corte`

Sale de `../nfr-design/` y de `../decisions.md` (ADR-W1 a ADR-W5). Todo en el plan gratuito de
Cloudflare Workers; nada de pago (regla de `project.md`).

## Piezas

| Pieza | Configuración | Dónde |
|---|---|---|
| Worker `reto-desinformacion` | `main: src/worker.js`, `compatibility_date: 2026-10-01` | `despliegues/cloudflare/wrangler.jsonc` |
| Recursos estáticos | `assets.directory: ./web`, `run_worker_first: ["/api/*"]` | idem |
| Durable Object `Reto` | enlace `RETO`, migración `new_sqlite_classes: ["Reto"]` (el plan gratuito solo admite objetos con SQLite) | idem |
| Secreto `CLAVE_SEMILLERO` | `npx wrangler@4.148.0 secret put CLAVE_SEMILLERO` | cuenta de Cloudflare del semillero |
| Enlace fijo | `https://reto-desinformacion.<subdominio>.workers.dev` | lo asigna Cloudflare |

## Pasos (los pone en palabras simples `despliegues/cloudflare/LEEME.md`)

1. `herramientas/copiar.sh` copia `web/` y el banco desde `2_Aplicacion_Reto/`.
2. `npx wrangler@4.148.0 login` con la cuenta del semillero.
3. `npx wrangler@4.148.0 secret put CLAVE_SEMILLERO`.
4. `npx wrangler@4.148.0 deploy`.
5. Prueba común contra el enlace (`despliegues/prueba_comun/src/prueba.py`).

Volver atrás: `npx wrangler@4.148.0 rollback` a la versión anterior. Los datos del objeto no se
pierden al desplegar ni al volver atrás.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
