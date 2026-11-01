# Comparación de las opciones de hosting

Tabla que se llena con lo que mide la prueba común (`prueba_comun/`) contra el enlace de cada opción
(requisito FR12.4). Cada cifra lleva al lado el comando o la URL oficial de donde salió; una casilla sin
medir dice «pendiente».

| Criterio | Render | Cloudflare | Cloudflare Containers | Apps Script | GitHub Pages | PythonAnywhere |
|---|---|---|---|---|---|---|
| Pasa el corte delgado | Sin medir: no se despliega mientras no se apruebe el costo (FR12.2a) | pendiente | Sin medir: exige Workers Paid y no se aprobó el costo (https://developers.cloudflare.com/containers/pricing/) | pendiente | pendiente | pendiente |
| Pasa la prueba común («TODO BIEN») | Sin medir (FR12.2a) | pendiente | Sin medir (FR12.2a) | pendiente | pendiente | pendiente |
| Latencia p95 al responder (meta ≤ 1 s) | Sin medir (FR12.2a) | pendiente | Sin medir (FR12.2a) | pendiente | pendiente | pendiente |
| Latencia p95 del tablero (meta ≤ 1,5 s) | Sin medir (FR12.2a) | pendiente | Sin medir (FR12.2a) | pendiente | pendiente | pendiente |
| Sobrevive a un reinicio sin perder puntajes | Gratuito: **no**, sistema de archivos efímero y sin disco (https://render.com/docs/free). De pago con disco: sí según la documentación, sin medir; cada despliegue corta el servicio unos segundos (https://render.com/docs/disks) | pendiente | **No con el `Dockerfile` actual**: el disco es efímero y al dormir o parar arranca con disco nuevo (https://developers.cloudflare.com/containers/platform-details/); SQLite en `/data` se pierde. **No cumple NFR4** | pendiente | pendiente | pendiente |
| Arranque en frío | Gratuito: duerme a los 15 min y despierta en «about one minute» (https://render.com/docs/free): **no cumple NFR5** (≤ 30 s). De pago: no duerme | pendiente | 1 a 3 s según la documentación, sin medir (https://developers.cloudflare.com/containers/platform-details/). Duerme a los 10 min y la plataforma puede pararlo en cualquier momento (https://developers.cloudflare.com/containers/faq/) | pendiente | pendiente | pendiente |
| Consumo frente a la cuota gratuita (con URL oficial) | Gratuito: 750 h-instancia al mes (https://render.com/docs/free); un enlace fijo siempre encendido gasta 720 a 744 h (96 a 99 %): **supera el 50 %**. Ancho de banda: ≈ 0,3 GB por sesión frente a 100 GB al mes (https://render.com/pricing): 0,3 % | pendiente | No hay cuota gratuita (https://developers.cloudflare.com/containers/pricing/). Frente al uso incluido en Workers Paid, una sesión de 90 min en `lite`: 1,5 % de memoria, CPU y disco; ≈ 0,3 GB de 1 TB de salida (0,03 %) | pendiente | pendiente | pendiente |
| Costo en US$ | Plan con disco `0.5c-512mb`: US$ 7 al mes + US$ 0,25 por GB, prorrateado por segundo (https://render.com/pricing): ≈ US$ 7,25 al mes encendido. **No cumple NFR6** (US$ 0) | pendiente | US$ 5 al mes fijos (https://developers.cloudflare.com/workers/platform/pricing/) + excedentes: ≈ US$ 1,77 al mes más si queda siempre encendido en `lite`. **No cumple NFR6** (US$ 0) | pendiente | pendiente | pendiente |
| Piezas y servicios | 1 servicio externo (Render, con tarjeta). Piezas: servicio web Docker, disco de 1 GB, secreto `RETO_CLAVE`, `render.yaml` (https://render.com/docs/disks) | pendiente | 1 servicio externo (Cloudflare, plan Workers Paid). Piezas: Worker, clase Container, imagen Docker (Docker local obligatorio, https://developers.cloudflare.com/containers/get-started/), secreto, `wrangler.jsonc` | pendiente | pendiente | pendiente |
| Líneas de código | Sin escribir: `despliegues/render/` queda sin código porque no se aprobó el costo (FR12.2a) | pendiente | Sin escribir: `despliegues/cloudflare-containers/` queda sin código (de pago y sin disco persistente, FR12.2a) | pendiente | pendiente | pendiente |
| Pasos para desplegar (persona del semillero) | 5 pasos de la «Parte 2» de `PUBLICAR_EN_INTERNET.md` (Blueprint de `render.yaml`), más tarjeta de crédito | pendiente | Instalar Docker, `npx wrangler login`, secreto, `npx wrangler deploy` (https://developers.cloudflare.com/containers/get-started/): uno más que Workers (Docker) | pendiente | pendiente | pendiente |

«PythonAnywhere» es el servidor que hoy corre el reto (`despliegues/github-pages/LEEME.md`); «GitHub Pages» solo redirige a él.

**Render** (U15): cifras de la documentación oficial de `render.com`, consultadas el 2026-10-25.
Veredicto: **no pasa todo** (NFR6 en el plan con disco; NFR4 y NFR5 en el gratuito). `render.com/pricing`
carga la tabla con JavaScript: para repetir la comprobación, descargarla con `curl` y buscar
«0.5c-512mb», «$7/month» y «$0.25 per GB per month». Detalle y citas textuales:
`aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u15-render-documentacion/functional-design/functional-spec.md`.

**Cloudflare Containers** (U16): cifras de `developers.cloudflare.com`, consultadas el 2026-10-25.
Veredicto: **no pasa todo** (NFR6: solo Workers Paid, US$ 5 al mes; NFR4: disco efímero con el `Dockerfile`
actual). Detalle y citas textuales:
`aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u16-cloudflare-containers-documentacion/functional-design/functional-spec.md`.

«Pasa todo» y el orden para elegir la más simple están en FR12.5 y FR12.6 de los requisitos. La
elección y la alternativa de respaldo las aprueba el humano en un ADR.
