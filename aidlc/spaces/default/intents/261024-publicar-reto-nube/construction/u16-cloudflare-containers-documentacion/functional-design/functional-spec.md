# Especificación funcional — U16 `u16-cloudflare-containers-documentacion`

Qué entrega U16: la columna **Cloudflare Containers** de `despliegues/COMPARACION.md`, llena con cifras
de la documentación oficial, cada una con su URL y su fecha de consulta, **sin desplegar ni gastar**
(`unit-of-work.md`, «U15 y U16»; `bolt-plan.md`, B6). Responde también las dos preguntas que dejó
`despliegues/cloudflare-containers/LEEME.md` («Pendiente de decidir en el ADR»): dónde quedan los datos
y si hay plan gratuito. Las entidades están en `entities.md` y las reglas en `rules.md`. El texto final de
la tabla lo escribe Code Generation copiando de aquí.

## Qué demuestra la unidad

Que Cloudflare Containers entra en la comparación con datos verificables y queda marcada «no pasa
todo» por dos motivos independientes: exige el plan de pago Workers Paid (NFR6) y su disco es efímero,
así que el `Dockerfile` actual con SQLite en `/data` pierde los datos al dormir o al parar (NFR4).

## Cifras oficiales (consultadas el 2026-10-25)

Todas las páginas son de `developers.cloudflare.com`. Las citas van en inglés, tal como están en la página.

| # | Cifra | Cita textual | URL |
|---|---|---|---|
| C1 | Containers está **solo en Workers Paid**; en el plan Free no hay memoria, CPU ni disco | «Available on Workers Paid plan»; columna Free de la tabla de precios: «N/A» en Memory, CPU y Disk | https://developers.cloudflare.com/containers/ y https://developers.cloudflare.com/containers/pricing/ |
| C2 | Workers Paid cuesta como mínimo **US$ 5 al mes** por cuenta | «a minimum charge of $5 USD per month for an account» | https://developers.cloudflare.com/workers/platform/pricing/ |
| C3 | Uso **incluido** en Workers Paid: 25 GiB-horas de memoria, 375 vCPU-minutos, 200 GB-horas de disco, 1 TB de salida (Norteamérica y Europa; 500 GB en el resto) | tabla «Included usage» | https://developers.cloudflare.com/containers/pricing/ |
| C4 | Tarifas **por encima** del incluido: US$ 0,0000025 por GiB-segundo, US$ 0,000020 por vCPU-segundo, US$ 0,00000007 por GB-segundo; salida US$ 0,025 por GB (NA y EU), US$ 0,04 en el resto | «$0.0000025 per additional GiB-second» / «$0.000020 per additional vCPU-second» / «$0.00000007 per additional GB-second» | https://developers.cloudflare.com/containers/pricing/ |
| C5 | Se cobra mientras la instancia está encendida; al dormir deja de cobrar | «Charges stop after the instance goes to sleep» | https://developers.cloudflare.com/containers/pricing/ |
| C6 | El disco es **efímero**: al dormir, la siguiente arrancada usa un disco nuevo de la imagen | «All disk is ephemeral by default» / «it uses a fresh disk from the container image» | https://developers.cloudflare.com/containers/platform-details/ |
| C7 | Alternativas documentadas para guardar datos: instantáneas **inmutables** (solo con la política `durable_object`; máximo 20 GB, 30 días) o un montaje FUSE a R2 u otro almacén de objetos, «sin rendimiento de SSD» | «Snapshots … are immutable» / «persist disk to R2 or other object storage backends» / «should not expect SSD-like performance» | https://developers.cloudflare.com/containers/faq/ y https://developers.cloudflare.com/containers/platform-details/limits/ |
| C8 | Duerme por defecto a los **10 minutos** sin peticiones (`sleepAfter`) | «sets sleepAfter to 10 minutes by default» | https://developers.cloudflare.com/containers/platform-details/ |
| C9 | La plataforma puede **detener un contenedor activo en cualquier momento**: `SIGTERM`, espera hasta 15 minutos y `SIGKILL` | «the platform can stop an active container at any time» / «sends SIGTERM, waits up to 15 minutes, then sends SIGKILL» | https://developers.cloudflare.com/containers/faq/ |
| C10 | Arranque en frío típico de **1 a 3 segundos**, según el tamaño de la imagen | «Container cold starts can often be in the 1-3 second range» | https://developers.cloudflare.com/containers/platform-details/ |
| C11 | Instancia más pequeña **`lite`**: 1/16 vCPU, 256 MiB de memoria, 2 GB de disco; `basic`: 1/4 vCPU, 1 GiB, 4 GB | tabla «Predefined instance types» | https://developers.cloudflare.com/containers/platform-details/limits/ |
| C12 | Límites de cuenta: 6 TiB de memoria y 1.500 vCPU concurrentes, 30 TB de disco, 50 GB de imágenes | tabla «Account limits» | https://developers.cloudflare.com/containers/platform-details/limits/ |
| C13 | Desplegar exige **Docker corriendo en el computador** y una imagen `linux/amd64`; el comando es `npx wrangler deploy` | «You must have Docker running locally when you run wrangler deploy» | https://developers.cloudflare.com/containers/get-started/ |
| C14 | **Sin autoescalado** por ahora; página actualizada el 2026-10-05 | «Not today, though Cloudflare plans to add built-in autoscaling in a future release» | https://developers.cloudflare.com/containers/beta-info/ |

## Columna Cloudflare Containers, fila por fila (FR12.4)

Lo que Code Generation copia a `COMPARACION.md`. Cada casilla trae el valor y la fuente entre paréntesis.

| Fila | Casilla Cloudflare Containers |
|---|---|
| Pasa el corte delgado | Sin medir: exige Workers Paid y no se aprobó el costo (C1, C2; FR12.2a). |
| Pasa la prueba común («TODO BIEN») | Sin medir (FR12.2a). |
| Latencia p95 al responder (meta ≤ 1 s) | Sin medir (FR12.2a). |
| Latencia p95 del tablero (meta ≤ 1,5 s) | Sin medir (FR12.2a). |
| Sobrevive a un reinicio sin perder puntajes | **No con el `Dockerfile` actual**: el disco es efímero y al dormir o parar arranca con disco nuevo (C6); SQLite en `/data` se pierde. Guardar datos exige cambiar la aplicación: instantáneas inmutables o FUSE a R2 (C7). **No cumple NFR4** como opción b (FR12.2, «con el Dockerfile actual»). |
| Arranque en frío | 1 a 3 s según documentación (C10): dentro de los 30 s de NFR5, sin medir. Duerme a los 10 min (C8) y la plataforma puede pararlo en cualquier momento (C9): cada parada pierde los datos (fila anterior). |
| Consumo frente a la cuota gratuita (con URL oficial) | No hay cuota gratuita (C1). Frente al uso incluido en Workers Paid (C3), una sesión de 90 min en `lite` (C11): 0,375 GiB-h de 25 (1,5 %), ≤ 5,6 vCPU-min de 375 (1,5 %), 3 GB-h de 200 (1,5 %), ≈ 0,3 GB de salida de 1 TB (0,03 %). Siempre encendido (744 h, para no perder SQLite): 186 GiB-h y 1.488 GB-h, por encima del incluido. |
| Costo en US$ | US$ 5 al mes fijos (C2) + excedentes (C4): ≈ US$ 0 si solo se enciende para el reto; ≈ US$ 1,77 al mes adicionales siempre encendido en `lite` (161 GiB-h × 3.600 s × 0,0000025 + 1.288 GB-h × 3.600 s × 0,00000007). **No cumple NFR6** (US$ 0). |
| Piezas y servicios | 1 servicio externo (Cloudflare, plan Workers Paid). Piezas propias: Worker, clase Container, imagen Docker (Docker local obligatorio, C13), secreto de la clave del semillero, `wrangler.jsonc`. |
| Líneas de código | Sin escribir: la carpeta `despliegues/cloudflare-containers/` queda vacía porque no se aprobó el costo y la opción no cumple NFR4 sin cambiar la aplicación. |
| Pasos para desplegar (persona del semillero) | Según `get-started`: instalar Docker, `npx wrangler login`, secreto, `npx wrangler deploy` (C13). Más que Workers (U1): exige Docker en el computador de quien despliega. |

Veredicto de la columna: **no pasa todo**. Motivos: NFR6 (Workers Paid, US$ 5 al mes) y NFR4 (disco
efímero con el `Dockerfile` actual).

## Respuestas a lo «pendiente de decidir» del LEEME de la opción

| Pregunta del LEEME | Respuesta |
|---|---|
| ¿Dónde quedan los datos? ¿Se apaga a mitad del reto? | En disco efímero (C6); duerme a los 10 min (C8) y la plataforma puede parar en cualquier momento (C9). SQLite en `/data` se pierde en cada parada. |
| ¿Hay plan gratuito? | No: solo Workers Paid, US$ 5 al mes (C1, C2). |

Code Generation deja estas dos respuestas en `despliegues/cloudflare-containers/LEEME.md`, con las URL,
y cambia el «Estado» a «no se despliega: de pago y sin disco persistente (FR12.2a, NFR4)».

## Comparación con la opción Cloudflare Workers (U1)

Workers ya corre en el plan gratuito con un Durable Object con SQLite que persiste entre reinicios
(`u1-cloudflare-corte/decisions.md`, ADR-W1). Containers agregaría un contenedor de pago para correr el
mismo Python de hoy y, aun así, tendría que mover los datos fuera del contenedor. Por eso no se propone
pedir aprobación de costo para esta opción: aunque se pagara, no cumpliría NFR4 con el `Dockerfile`
actual.

## Qué no hace la unidad

- No activa Workers Paid ni crea un contenedor.
- No escribe código ni copia el `Dockerfile` a `despliegues/cloudflare-containers/`.
- No decide la ganadora: eso es U17.
