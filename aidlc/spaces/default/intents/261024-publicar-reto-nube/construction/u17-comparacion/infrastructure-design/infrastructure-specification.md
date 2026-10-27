# Infraestructura — U17 `u17-comparacion`

> **Revisión 2026-10-27 (una sola sala).** Solo Cloudflare (FR12.2c): el chequeo de salud devuelve los
> datos del tablero, entra el `LEEME.md` de Cloudflare como salida y no hay respaldo construido.

**No aplica: U17 no despliega nada.** Produce cuatro documentos, dos líneas de `.gitattributes` y un
commit de borrado. La infraestructura que describe es la de Cloudflare Workers, ya especificada en sus
unidades (U1 a U6; `u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`, «Piezas»
y «Pasos»).

## Lo que U17 toma de la infraestructura de Cloudflare

| Dato | De dónde | Para qué |
|---|---|---|
| Tabla «Piezas» | `infrastructure-specification.md` de U1 a U6 | contar piezas propias (BR17.5) |
| Pasos de despliegue | `despliegues/cloudflare/LEEME.md` | fila «Pasos para desplegar» y sección 2 de la guía |
| Comando de vuelta atrás | `infrastructure-specification.md` de U1 («Volver atrás») y ADR-W19 de U5 | sección 8 de la guía |
| Chequeo de salud | `GET /api/publico` sin parámetros → 200 con los datos del tablero (ADR-011) | sección 5 de la guía |
| Dónde se ven registros y consumo | `monitoring-design.md` de U1 | sección 5 de la guía, parte del semillero |
| Intervalos de refresco | `despliegues/cloudflare/web/static/js/*.js` y `web/tablero.html` | estimación de consumo (BR17.12) |

Render y Cloudflare Containers entran con las columnas de U15 y U16; Apps Script con C-01; GitHub Pages
con FR12.2c. Ninguna aporta infraestructura.

## Lo que U17 escribe

- `despliegues/COMPARACION.md` (tabla y cuatro bloques, `../functional-design/functional-spec.md`).
- `construction/u17-comparacion/decisions.md` (ADR-C3 completado y aprobado).
- `despliegues/cloudflare/LEEME.md` para una sala y Windows, y `*.sh` y `*.patch` con LF en
  `.gitattributes` (BR17.13, ADR-C6).
- `PUBLICAR_EN_INTERNET.md` (guía de Cloudflare).
- Commit propio de borrado de `apps-script/`, `render/`, `cloudflare-containers/` y `github-pages/` bajo
  `despliegues/` tras la aprobación (BR17.9).

## Lo que no toca

`2_Aplicacion_Reto/` (FR12.1), `render.yaml` de la raíz (sigue describiendo la versión local hasta que el
humano decida quitarlo; U17 lo anota en el ADR como pregunta de limpieza) y el código de
`despliegues/cloudflare/` (solo cambia su `LEEME.md`). No hay respaldo construido en la nube (FR12.2c).
