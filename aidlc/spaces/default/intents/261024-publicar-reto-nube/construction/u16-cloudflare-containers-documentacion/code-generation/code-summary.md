# Resumen de código: U16 `u16-cloudflare-containers-documentacion`

Unidad de solo documentación: llena la columna Cloudflare Containers de la comparación sin desplegar ni
gastar (FR12.2a), con el plan de 6 pasos (`code-generation-plan.md`) y `unit-test-instructions.md`.

## Qué se hizo

- La columna Cloudflare Containers de `despliegues/COMPARACION.md`, copiada de
  `../functional-design/functional-spec.md`. Cada casilla con cifra trae su URL oficial de
  `developers.cloudflare.com`; las filas que exigen medir dicen «Sin medir». Debajo de la tabla, una nota
  con la fecha de consulta (2026-10-25) y el veredicto: «no pasa todo» por NFR6 (Workers Paid) y NFR4
  (disco efímero con el `Dockerfile` actual).
- `despliegues/cloudflare-containers/LEEME.md`: estado «no se despliega» y las dos respuestas a lo que
  quedaba pendiente (dónde quedan los datos, si hay plan gratuito), con sus URL.

## Archivos

| Archivo | Cambio |
|---|---|
| `despliegues/COMPARACION.md` | Columna Cloudflare Containers y nota de fuentes |
| `despliegues/cloudflare-containers/LEEME.md` | Estado y decisiones |

## Resultados de las pruebas

- `python3 despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion "cloudflare containers"`: «TODO BIEN».
- La misma comprobación con `--opcion render` sigue en «TODO BIEN».
- `python3 -m unittest test_revisar_comparacion`: 4 de 4.

## Desviaciones del plan y su motivo

- Igual que en U15, la cita textual en inglés queda en `functional-spec.md` y la tabla lleva la URL,
  para que la tabla siga siendo legible.
- La casilla de costo no repite el cálculo de excedentes paso a paso; el cálculo está en
  `functional-spec.md`.

## Notas para quien sigue

- U17 cierra la fila de esta opción como «no pasa» con estos dos motivos.
