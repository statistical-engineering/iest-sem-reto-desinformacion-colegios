# Infraestructura — U17 `u17-comparacion`

**No aplica: U17 no despliega nada.** Produce tres documentos y un commit de borrado. La infraestructura
que describe es la de la ganadora, y ya está especificada en su propia unidad (para Workers,
`u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`, «Piezas» y «Pasos»).

## Lo que U17 toma de la infraestructura de cada opción

| Dato | De dónde | Para qué |
|---|---|---|
| Tabla «Piezas» | `infrastructure-specification.md` de la opción | contar piezas propias (BR17.5) |
| Pasos de despliegue | `despliegues/<opcion>/LEEME.md` | fila «Pasos para desplegar» y sección 2 de la guía |
| Comando de vuelta atrás | `infrastructure-specification.md` de la opción («Volver atrás») | sección 7 de la guía |
| Chequeo de salud | `GET /api/publico` → `{"ok": true}` (igual en todas) | sección 4 de la guía |
| Dónde se ven registros y consumo | `monitoring-design.md` de la opción | sección 4 de la guía, parte del semillero |

## Lo que U17 escribe

- `despliegues/COMPARACION.md` (tabla y tres bloques, `../functional-design/functional-spec.md`).
- `construction/u17-comparacion/decisions.md` (ADR-C3 completado y aprobado).
- `PUBLICAR_EN_INTERNET.md` (guía de la ganadora).
- Commit propio de borrado de `despliegues/<perdedoras>/` tras la aprobación (BR17.9).

## Lo que no toca

`2_Aplicacion_Reto/` (FR12.1), `render.yaml` de la raíz (sigue describiendo la versión local hasta que el
humano decida quitarlo; U17 lo anota en el ADR como pregunta de limpieza), las carpetas de la ganadora y
del respaldo.
