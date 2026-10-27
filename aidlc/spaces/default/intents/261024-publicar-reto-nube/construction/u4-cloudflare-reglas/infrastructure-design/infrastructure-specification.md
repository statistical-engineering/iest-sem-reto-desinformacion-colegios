# Infraestructura — U4 `u4-cloudflare-reglas`

> **Revisión 2026-10-27 (una sola sala).** El Durable Object `Reto` sigue igual en U4; el esquema de una sola sala (tabla `colegios` con `arranque`) es de U5. Los archivos de prueba se cuentan por patrón, no por número.

Sale de `../nfr-design/` y de `../decisions.md` (ADR-W6 a ADR-W9). U4 no agrega ninguna pieza de
Cloudflare: las reglas van dentro del mismo Worker y del mismo Durable Object de U1
(`../../u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`). Todo sigue en el plan
gratuito.

## Piezas

| Pieza | Cambio en U4 | Dónde |
|---|---|---|
| Worker `reto-desinformacion` | Ninguno en `wrangler.jsonc`; el bundle crece con `src/reglas/` (unos 60 KB más, muy por debajo del límite de tamaño del Worker en el plan gratuito, «Worker size 64 MiB», https://developers.cloudflare.com/workers/platform/limits/, consultado el 2026-10-25) | `despliegues/cloudflare/` |
| Durable Object `Reto` | Ninguno en U4: esquema y migración `v1` sin cambios; la tabla `colegios` con `arranque` la agrega U5 | idem |
| Herramientas | `herramientas/copiar.sh` copia además `despliegues/prueba_comun/casos_reglas.json` a `pruebas/`; `herramientas/verificar.sh` compara las huellas, corre cada archivo de `pruebas/*.test.js` por nombre, exige 80 % de cobertura con `--test-coverage-lines=80` y comprueba que `src/reglas/` no usa reloj, azar ni `env` | `despliegues/cloudflare/herramientas/` |
| Datos compartidos | `despliegues/prueba_comun/casos_reglas.json`, `banco_prueba.json` y `herramientas/generar_casos.py`, versionados | `despliegues/prueba_comun/` |

## Pasos (los pone en palabras simples `despliegues/cloudflare/LEEME.md`)

1. `python3 despliegues/prueba_comun/herramientas/generar_casos.py` cuando cambie el generador o el
   banco de prueba (no hace falta para desplegar).
2. `bash despliegues/cloudflare/herramientas/copiar.sh`.
3. `bash despliegues/cloudflare/herramientas/verificar.sh` (es el comando de verificación de la
   intención, `verification-command.txt`).
4. Despliegue igual que U1: `npx wrangler@4.148.0 deploy`, solo sin reto en curso.

Volver atrás: `npx wrangler@4.148.0 rollback`, como U1. Los datos no cambian porque U4 no toca el
esquema.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
