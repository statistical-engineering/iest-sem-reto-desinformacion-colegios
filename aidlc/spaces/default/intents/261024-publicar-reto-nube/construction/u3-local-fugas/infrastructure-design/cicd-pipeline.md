# Integración y despliegue — U3

- No hay despliegue automático: el docente actualiza y reinicia a mano, sin reto en curso
  (`project.md`, «Mandated»).
- La única CI es la revisión de PR (`.github/workflows/revisar-pr.yml`): ganchos de pre-commit (ruff y
  mensaje de commit), `simulacro.py` y el límite de 400 líneas. U3 cabe en un solo PR (unas 120 líneas de
  código con sus pruebas).
- Antes de cada push a `develop`:
  1. `uv run ruff format --check 2_Aplicacion_Reto` y `uv run ruff check 2_Aplicacion_Reto`;
  2. `python3 -m unittest discover -s 2_Aplicacion_Reto/pruebas -t 2_Aplicacion_Reto` (nuevo
     `test_servidor.py`);
  3. `python3 -m trace --count --coverdir=/tmp/cobertura_u3 --missing -m unittest discover -s
     2_Aplicacion_Reto/pruebas -t 2_Aplicacion_Reto` y revisar que las seis funciones nuevas pasen del
     80 % de líneas (U3-M1);
  4. `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` en «TODO BIEN», sin tocar
     `simulacro.py` (FR6.3);
  5. la prueba común en modo local contra `servidor.py` con `--db` aparte: parte base y parte de fugas en
     «TODO BIEN» (B7 de `bolt-plan.md`);
  6. `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` solo muestra `servidor.py` y
     `pruebas/test_servidor.py`.
- Mensaje de commit: `fix: corregir las fugas de respuestas antes de resultados` (tipo en inglés,
  descripción en español, `team.md`).
