# Especificación funcional — U15 `u15-render-documentacion`

Qué entrega U15: la columna **Render** de `despliegues/COMPARACION.md`, llena con cifras de la
documentación oficial, cada una con su URL y su fecha de consulta, **sin desplegar ni gastar**
(`unit-of-work.md`, «U15 y U16»; `bolt-plan.md`, B5). Las entidades están en `entities.md` y las reglas en
`rules.md`. El texto final de la tabla lo escribe Code Generation copiando de aquí.

## Qué demuestra la unidad

Que Render entra en la comparación con datos verificables y queda marcada «no cumple NFR6» mientras el
plan con disco sea de pago (FR12.2a), y que el plan gratuito tampoco cumple NFR4 ni NFR5. Así U17 puede
cerrar su fila sin esperar un despliegue.

## Cifras oficiales (consultadas el 2026-10-25)

Todas las páginas son de `render.com`. Las citas van en inglés, tal como están en la página.

| # | Cifra | Cita textual | URL |
|---|---|---|---|
| R1 | El plan gratuito duerme a los **15 minutos** sin tráfico | «spins down a Free web service that goes 15 minutes without receiving any inbound traffic» | https://render.com/docs/free |
| R2 | Despertar tarda **alrededor de un minuto** | «takes about one minute» | https://render.com/docs/free |
| R3 | **750 horas-instancia** gratis por espacio de trabajo y mes; no se acumulan | «750 free instance hours per workspace per calendar month» | https://render.com/docs/free |
| R4 | El plan gratuito **no admite disco persistente** | «Free web services cannot attach a persistent disk» | https://render.com/docs/free |
| R5 | El sistema de archivos es **efímero**: se pierde al redesplegar, reiniciar o dormir | «Like all Render services, Free web services have an ephemeral filesystem» / «lost every time the service redeploys, restarts, or spins down» | https://render.com/docs/free |
| R6 | Render puede **reiniciar** un servicio gratuito en cualquier momento | «Render may also restart a Free web service at any time» | https://render.com/docs/free |
| R7 | El disco persistente solo va en un servicio **de pago** | «You can attach a persistent disk to a paid Render web service, private service, or background worker» | https://render.com/docs/disks |
| R8 | Con disco **no hay despliegue sin corte**: unos segundos sin servicio en cada despliegue | «Adding a disk to a service prevents zero-downtime deploys» / «This instance swap takes a few seconds, during which your service is unavailable» | https://render.com/docs/disks y https://render.com/docs/deploys |
| R9 | Con disco **no se puede escalar** a más de una instancia (coincide con «una sola instancia» de `project.md`) | «You can't scale a service to multiple instances if it has a disk attached» | https://render.com/docs/disks |
| R10 | Copia del disco cada **24 h**, guardada **7 días** | «Render takes a disk snapshot every 24 hours» / «available for seven days after they're created» | https://render.com/docs/disks |
| R11 | Plan de cómputo más barato con disco: **`0.5c-512mb`** (antes «Starter»), 0,5 CPU y 512 MB, **US$ 7 al mes** | fila «0.5c-512mb … 512 MB RAM … $7/month» | https://render.com/pricing (sección Compute); ids en https://render.com/docs/compute-plans |
| R12 | Disco: **US$ 0,25 por GB al mes** | «$0.25 per GB per month» | https://render.com/pricing |
| R13 | El cómputo se **prorratea por segundo** | «Prorated by the second» | https://render.com/pricing |
| R14 | Plan de espacio de trabajo Hobby: **US$ 0 al mes + cómputo**, con **100 GB** de ancho de banda incluidos | «Hobby … $ 0 /mo + compute»; fila «Included bandwidth: 100 GB / month» | https://render.com/pricing |
| R15 | El 2026-08-26 Render renombró los planes; «no hay cambios de precio» | «On August 26, 2026, Render introduced a new naming convention for compute plans» / «There are no changes to pricing» | https://render.com/docs/compute-plans-update |
| R16 | Los despliegues sin disco sí son sin corte; con disco, no | «All service types redeploy with zero downtime, unless they attach a persistent disk» | https://render.com/docs/deploys |

Nota: `https://render.com/pricing` carga la tabla con JavaScript; el texto se verificó descargando la
página completa (`curl`) y buscando las cadenas «0.5c-512mb», «$7/month» y «$0.25 per GB per month».
Code Generation deja esa nota en la tabla para que cualquiera pueda repetir la comprobación.

## Columna Render, fila por fila (FR12.4)

Lo que Code Generation copia a `COMPARACION.md`. Cada casilla trae el valor y la fuente entre paréntesis.

| Fila | Casilla Render |
|---|---|
| Pasa el corte delgado | Sin medir: no se despliega mientras no se apruebe el costo (FR12.2a). |
| Pasa la prueba común («TODO BIEN») | Sin medir (FR12.2a). |
| Latencia p95 al responder (meta ≤ 1 s) | Sin medir (FR12.2a). |
| Latencia p95 del tablero (meta ≤ 1,5 s) | Sin medir (FR12.2a). |
| Sobrevive a un reinicio sin perder puntajes | Gratuito: **no** (sistema de archivos efímero, R5; sin disco, R4). De pago con disco: sí según documentación (R7, R10), sin medir; cada despliegue corta el servicio unos segundos (R8). |
| Arranque en frío | Gratuito: duerme a los 15 min (R1) y despierta en «about one minute» (R2): **no cumple NFR5** (≤ 30 s). De pago: no duerme. |
| Consumo frente a la cuota gratuita (con URL oficial) | Gratuito: 750 h-instancia al mes (R3); un enlace fijo siempre encendido gasta 720 a 744 h (96 a 99 %), y al agotarse el servicio se suspende el resto del mes: **supera el 50 %**. Ancho de banda: ≈ 0,3 GB por sesión frente a 100 GB al mes (R14): 0,3 %. |
| Costo en US$ | Plan con disco: US$ 7 al mes (R11) + US$ 0,25 por GB (R12), prorrateado por segundo (R13): ≈ US$ 7,25 al mes encendido, o ≈ US$ 0,24 si se crea el día del reto y se borra después. **No cumple NFR6** (US$ 0). |
| Piezas y servicios | 1 servicio externo (Render, con tarjeta). Piezas propias: servicio web Docker, disco de 1 GB, secreto `RETO_CLAVE`, `render.yaml`. |
| Líneas de código | Sin escribir: la carpeta `despliegues/render/` queda vacía porque no se aprobó el costo. La versión local de hoy (`2_Aplicacion_Reto/`) no tiene salas (FR11), así que no serviría tal cual. |
| Pasos para desplegar (persona del semillero) | 5 pasos de la «Parte 2» de `PUBLICAR_EN_INTERNET.md` de hoy (Blueprint de `render.yaml`), más tarjeta de crédito. |

Veredicto de la columna: **no pasa todo**. Motivo: NFR6 (de pago) en el plan con disco; NFR4 y NFR5 en el
plan gratuito.

## Estimación de consumo de una sesión (NFR6)

Sale de `u1-cloudflare-corte/nfr-design/scalability-design.md`: ≈ 60.600 peticiones en 90 minutos con 40
personas y 10 salas. A unos 5 KB por respuesta JSON, son ≈ 0,3 GB de salida. En Render el límite que
manda no es ese sino las horas-instancia del plan gratuito: un servicio con enlace fijo que no se apaga
consume el mes entero. Si la cuota se agota a mitad del reto, Render suspende los servicios gratuitos
hasta el mes siguiente (R3, «suspended»); con el plan de pago no hay cuota de horas.

## Qué no hace la unidad

- No crea cuenta, servicio ni Blueprint en Render.
- No cambia `render.yaml` de la raíz (sigue describiendo la versión local, `despliegues/render/LEEME.md`).
- No escribe código en `despliegues/render/`.
- No decide la ganadora: eso es U17.

## Si el humano aprueba un costo más adelante

Se agregan unidades para construir la opción (`unit-of-work.md`, «U15 y U16», «Notas»): corte delgado,
reglas, salas y catálogo, resultados y exportación, como las de Workers. El monto y el tope aprobados se
anotan en el ADR de esa opción (FR12.2a).
