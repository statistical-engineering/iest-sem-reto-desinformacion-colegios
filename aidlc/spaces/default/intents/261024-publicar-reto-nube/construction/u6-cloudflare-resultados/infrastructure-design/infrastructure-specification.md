# Infraestructura — U6 `u6-cloudflare-resultados`

Sale de `../nfr-design/` y de `../decisions.md` (ADR-W14 a ADR-W18). Mismas piezas que U1 y U5; U6 agrega
la migración 3 del esquema, un archivo generado (`src/version.json`) y las descargas. Todo en el plan
gratuito; sin servicios nuevos (se rechazó R2/KV para las copias, ADR-W17).

## Piezas

| Pieza | Cambio en U6 | Dónde |
|---|---|---|
| Worker `reto-desinformacion` | Sin cambio en `wrangler.jsonc` | `despliegues/cloudflare/wrangler.jsonc` |
| Durable Object `Reto` | Esquema SQL versión 3: `copias`, `copia_trozos`, índice `participantes_sala_estado` (ADR-W10) | `src/reto.js` |
| Almacenamiento | ≈ 0,5 MB por copia; ≈ 25 MB en el peor caso previsto, frente a 5 GB del plan gratuito (`scalability-requirements.md`, U6-E1) | SQLite del objeto |
| `src/version.json` | Generado por `copiar.sh` con `git rev-parse --short HEAD` y la fecha; en `.gitignore` | `despliegues/cloudflare/src/` |
| Recursos estáticos | `web/` rehecho con el parche ampliado (paquete, copias, texto de reiniciar) | `herramientas/cambios_web.patch` |
| Diccionario | `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`, versionado | repositorio |

## Pasos (los pone en palabras simples `despliegues/cloudflare/LEEME.md`)

1. Confirmar que ninguna sala está en «abierto» (`GET /api/admin/salas`).
2. `bash despliegues/cloudflare/herramientas/copiar.sh` (escribe `version.json`) y
   `bash despliegues/cloudflare/herramientas/verificar.sh`.
3. `npx wrangler@4.148.0 deploy`.
4. En `wrangler tail`: «Migración v3 aplicada.» una vez y el commit en la línea de arranque.
5. Prueba común completa contra el enlace, que ahora descarga un paquete y lo abre.

## Cierre de un reto (NFR10.1; la guía final es de U17)

1. El docente descarga el paquete `.zip` y los dos CSV desde el panel y los guarda en el Drive del
   semillero, carpeta del año (FR9.4).
2. Abre el paquete y comprueba que `participantes.csv` tiene una fila por participante.
3. El semillero, con su clave, pulsa «Borrar la sala» y escribe BORRAR.
4. Comprueba `/api/publico?sala=<código>` → 404 y que `GET /api/admin/salas` ya no la lista: no queda
   ninguna fila ni copia de esa sala en Cloudflare.

Volver atrás: `npx wrangler@4.148.0 rollback`. El código de U5 ignora las tablas de copias; no hay que
deshacer la migración.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
