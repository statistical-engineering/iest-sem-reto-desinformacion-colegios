# Opción: Cloudflare Containers con el Dockerfile actual

El servidor en Python corre en un contenedor de Cloudflare, armado igual que la imagen de hoy
(`2_Aplicacion_Reto/Dockerfile`). Es la opción b del pedido inicial.

**Estado:** no se despliega: es de pago y no tiene disco persistente (FR12.2a, NFR4). Las cifras, con su
URL oficial y la fecha de consulta, están en la columna Cloudflare Containers de
[`../COMPARACION.md`](../COMPARACION.md).

## Estructura

```text
cloudflare-containers/
├── LEEME.md
├── src/        servidor en Python 3.12 (la API)
├── web/        pantallas copiadas de 2_Aplicacion_Reto/web/
└── pruebas/    pruebas unitarias con unittest (test_<modulo>.py)
```

Cuando el ADR lo apruebe, aquí van también el `Dockerfile` propio de esta opción y su configuración de
Cloudflare. La versión de hoy no se toca: el `Dockerfile` se copia, no se mueve.

## Decidido (U16, 2026-10-25)

- Dónde quedan los datos: en disco efímero; al dormir (10 minutos sin peticiones) o si la plataforma lo
  para, arranca con un disco nuevo y la base SQLite de `/data` se pierde
  (https://developers.cloudflare.com/containers/platform-details/,
  https://developers.cloudflare.com/containers/faq/).
- Plan gratuito: no hay. Containers exige Workers Paid, como mínimo US$ 5 al mes
  (https://developers.cloudflare.com/containers/pricing/,
  https://developers.cloudflare.com/workers/platform/pricing/).
- No se pide aprobar el costo: aun pagando, no cumpliría NFR4 con el `Dockerfile` actual. La opción
  Cloudflare Workers (`../cloudflare/`) ya guarda los datos gratis en un Durable Object.
