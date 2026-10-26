# Infraestructura — U15 `u15-render-documentacion`

**No aplica: no se despliega nada.** Render es de pago en el plan con disco (US$ 7 al mes + US$ 0,25 por
GB, https://render.com/pricing) y el plan gratuito no cumple NFR4 ni NFR5 (https://render.com/docs/free).
Mientras el humano no apruebe un monto y un tope (FR12.2a), esta unidad solo documenta.

## Lo que existiría si se aprobara el costo (referencia, no se crea)

| Pieza | Configuración | Dónde |
|---|---|---|
| Servicio web Docker | plan `0.5c-512mb`, `healthCheckPath: /api/publico`, una sola instancia | Blueprint en `despliegues/render/render.yaml` (copia, no el de la raíz) |
| Disco persistente | `mountPath: /data`, 1 GB, copia cada 24 h guardada 7 días | mismo Blueprint |
| Secreto `RETO_CLAVE` / clave del semillero | `sync: false`; se escribe en el panel de Render | cuenta de Render del semillero, con tarjeta |
| Enlace fijo | `https://<nombre>.onrender.com` | lo asigna Render |

Los pasos serían los 5 de la «Parte 2» de `PUBLICAR_EN_INTERNET.md` de hoy. Volver atrás es redesplegar
el commit anterior desde el panel; con disco, cada despliegue corta el servicio unos segundos
(https://render.com/docs/deploys).

## Lo que esta unidad sí toca

- `despliegues/COMPARACION.md`, columna Render (Code Generation).
- `despliegues/render/LEEME.md`, campo «Estado»: pasa a decir que no se despliega por costo, con enlace
  a la columna.
