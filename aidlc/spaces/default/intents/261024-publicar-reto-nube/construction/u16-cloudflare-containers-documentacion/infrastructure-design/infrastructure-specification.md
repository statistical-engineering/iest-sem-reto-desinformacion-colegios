# Infraestructura — U16 `u16-cloudflare-containers-documentacion`

**No aplica: no se despliega nada.** Cloudflare Containers está «Available on Workers Paid plan»
(https://developers.cloudflare.com/containers/), con un mínimo de US$ 5 al mes
(https://developers.cloudflare.com/workers/platform/pricing/), y su disco es efímero
(https://developers.cloudflare.com/containers/platform-details/). Mientras el humano no apruebe un monto y
un tope (FR12.2a), esta unidad solo documenta.

## Lo que existiría si se aprobara el costo (referencia, no se crea)

| Pieza | Configuración | Dónde |
|---|---|---|
| Worker con clase `Container` | `wrangler.jsonc` con `containers` e instancia `lite` (1/16 vCPU, 256 MiB, 2 GB) | `despliegues/cloudflare-containers/` |
| Imagen Docker | copia del `Dockerfile` de hoy, `linux/amd64`; Docker corriendo en el computador al desplegar | idem |
| Almacén de datos fuera del contenedor | obligatorio: instantáneas inmutables o FUSE a R2 según la documentación, o mover SQLite a un Durable Object, que es lo que ya hace Workers (U1) | cambia la aplicación |
| Secreto de la clave del semillero | `npx wrangler secret put` | cuenta de Cloudflare del semillero, plan Workers Paid |
| Enlace fijo | `https://<nombre>.<subdominio>.workers.dev` | lo asigna Cloudflare |

Volver atrás sería `npx wrangler rollback`, como en Workers; los datos del disco efímero no sobreviven
a ningún despliegue.

## Lo que esta unidad sí toca

- `despliegues/COMPARACION.md`, columna Cloudflare Containers (Code Generation).
- `despliegues/cloudflare-containers/LEEME.md`: responde lo «Pendiente de decidir» con las URL y cambia
  el «Estado» a «no se despliega: de pago y sin disco persistente (FR12.2a, NFR4)».
