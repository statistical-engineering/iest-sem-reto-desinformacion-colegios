# Resumen de código: U15 `u15-render-documentacion`

Unidad de solo documentación: llena la columna Render de la comparación sin desplegar ni gastar
(FR12.2a), con el plan de 6 pasos (`code-generation-plan.md`) y `unit-test-instructions.md`.

## Qué se hizo

- La columna Render de `despliegues/COMPARACION.md`, fila por fila, copiada de
  `../functional-design/functional-spec.md`. Cada casilla con cifra trae su URL oficial de `render.com`;
  las filas que exigen medir dicen «Sin medir (FR12.2a)». Debajo de la tabla, una nota con la fecha de
  consulta (2026-10-25), el veredicto («no pasa todo»: NFR6 con disco; NFR4 y NFR5 en el gratuito) y
  cómo repetir la comprobación de `render.com/pricing` con `curl`.
- La comprobación `despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion <columna>`:
  falla si una casilla con cifra no trae URL `https://` ni comando. Sirve también para las demás columnas
  (U17).
- `despliegues/render/LEEME.md`: estado «documentada, no se despliega», enlace a la comparación y lo
  decidido.

## Archivos

| Archivo | Cambio |
|---|---|
| `despliegues/COMPARACION.md` | Columna Render y nota de fuentes |
| `despliegues/prueba_comun/herramientas/revisar_comparacion.py` | Nuevo |
| `despliegues/prueba_comun/herramientas/test_revisar_comparacion.py` | Nuevo, 4 pruebas `unittest` |
| `despliegues/render/LEEME.md` | Estado y decisiones |

## Resultados de las pruebas

- `python3 -m unittest -v test_revisar_comparacion` (desde `despliegues/prueba_comun/herramientas/`): 4 de 4.
- `python3 despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion render`: «TODO BIEN».
- `uv run ruff check` y `uv run ruff format --check` sobre la carpeta: sin faltas.

## Desviaciones del plan y su motivo

- BR15.1 pide la cita textual junto a cada cifra. La tabla lleva la URL en cada casilla y la nota remite a
  `functional-spec.md`, donde están las 16 citas: copiar las citas en inglés dentro de cada casilla haría
  la tabla ilegible para el semillero.
- Se agregó `test_revisar_comparacion.py` (no estaba en el plan) porque la regla de Python exige una
  prueba propia para cada función de paso aislado.

## Notas para quien sigue

- U17 usa la misma comprobación con `--opcion cloudflare`, `--opcion "github pages"`, etc.
- No se tocó `render.yaml` de la raíz.
