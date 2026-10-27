# Infraestructura — U6 `u6-cloudflare-resultados`

> **Revisión 2026-10-27 (una sola sala).** Sin `GET /api/admin/salas`, sin «Borrar la sala» y sin
> `?sala=`: el reto se comprueba con el panel (clave docente en `X-Clave-Admin`) y el cierre es
> «Reiniciar» y borrar cada copia (D7). La migración 3 ya no crea el índice por sala.

Sale de `../nfr-design/` y de `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21). Mismas piezas que U1 y U5;
U6 agrega la migración 3 del esquema, un archivo generado (`src/version.json`) y las descargas. Todo en el
plan gratuito; sin servicios nuevos (se rechazó R2/KV para las copias, ADR-W17).

## Piezas

| Pieza | Cambio en U6 | Dónde |
|---|---|---|
| Worker `reto-desinformacion` | Sin cambio en `wrangler.jsonc` | `despliegues/cloudflare/wrangler.jsonc` |
| Durable Object `Reto` | Esquema SQL versión 3: `copias`, `copia_trozos`; guarda y borra las `v1_*` (ADR-W10, BR9.1) | `src/reto.js` |
| Secreto | `CLAVE_DOCENTE` sin cambio (U5); en local, `.dev.vars` | Cloudflare |
| Almacenamiento | ≈ 0,5 MB por copia; ≈ 5 MB con 10 copias sin borrar, frente a 5 GB del plan gratuito (U6-E1) | SQLite del objeto |
| `src/version.json` | Generado por `copiar.sh` con `git rev-parse --short HEAD` y la fecha; en `.gitignore` | `despliegues/cloudflare/src/` |
| Recursos estáticos | `web/` rehecho con el parche ampliado (paquete, copias, texto de reiniciar, por grado, puesto en el grado) | `herramientas/cambios_web.patch` |
| Diccionario | `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`, versionado | repositorio |

## Pasos (los pone en palabras simples `despliegues/cloudflare/LEEME.md`)

1. Confirmar en el panel que el reto no está en «abierto».
2. `bash despliegues/cloudflare/herramientas/copiar.sh` (escribe `version.json`) y
   `bash despliegues/cloudflare/herramientas/verificar.sh`.
3. `npx wrangler@4.148.0 deploy`.
4. En `npx wrangler@4.148.0 tail`: «Migración v3 aplicada.» una vez y el commit en la línea de arranque.
5. Prueba común completa contra el enlace, que ahora descarga un paquete y lo abre.

## Cierre de un reto (NFR10.1; la guía final es de U17)

1. El docente descarga el paquete `.zip` y los dos CSV desde el panel y los guarda en el Drive del
   semillero, carpeta del año (FR9.4).
2. Abre el paquete y comprueba que `participantes.csv` tiene una fila por participante.
3. Pulsa «Reiniciar todo el reto» y escribe BORRAR (queda una copia nueva).
4. En la tarjeta «Copias», descarga las que falten y pulsa «Borrar» en cada una, incluida la recién
   creada.
5. Comprueba que la tarjeta «Copias» está vacía (`GET /api/admin/copias` → `copias: []`) y que el panel
   no muestra participantes ni colegios: no queda ninguna fila del reto en Cloudflare.

Volver atrás: `npx wrangler@4.148.0 rollback`. El código de U5 ignora las tablas de copias; no hay que
deshacer la migración (las `v1_*` ya quedaron guardadas en `migracion_v1.sql`).

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
