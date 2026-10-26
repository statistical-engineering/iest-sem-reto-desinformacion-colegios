# Integración y despliegue — U2

- No hay despliegue: la prueba corre desde la computadora de quien prueba.
- La única CI aprobada es la revisión de PR (`.github/workflows/revisar-pr.yml`: ganchos, simulacro y
  límite de 400 líneas) y no cambia (`team.md`, «Corrections»). Las pruebas de esta unidad corren en
  local.
- Antes de cada push a `develop` (el humano y el asistente suben directo; el resto por PR):
  1. `uv run ruff format --check despliegues/prueba_comun` y `uv run ruff check despliegues/prueba_comun`;
  2. `python3 -m unittest discover -s despliegues/prueba_comun/pruebas -t despliegues/prueba_comun`;
  3. cobertura: `python3 -m trace --count --coverdir=/tmp/cobertura_prueba --missing -m unittest discover
     -s despliegues/prueba_comun/pruebas -t despliegues/prueba_comun`, y la corrida en modo local bajo
     `trace` para `prueba.py`; se exige el 80 % de líneas de `src/` (U2-M1);
  4. `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` en «TODO BIEN» (no cambia nada ahí,
     pero es regla de todo Bolt);
  5. `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1; después de U3, contra su commit);
  6. la prueba común en modo local (parte base en «TODO BIEN») y en modo nube contra `wrangler dev`
     (`verificar.sh`).
- Esta unidad pasa de 400 líneas de código: si la sube alguien distinto del humano o el asistente, se
  parte en PR por módulo (`guion.py` con sus pruebas, `cliente.py` y `carga.py`, `mediciones.py`,
  `prueba.py`).
