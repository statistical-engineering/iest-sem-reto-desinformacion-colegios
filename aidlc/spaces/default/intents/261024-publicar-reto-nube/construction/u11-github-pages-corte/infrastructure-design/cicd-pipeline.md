# Integración y despliegue — U11

- No hay despliegue automático: la API se actualiza con `git pull` y «Reload» a mano, y las pantallas con
  «Run workflow» a mano, solo sin reto en curso (`project.md`, «Mandated»; FR5.2).
- `publicar-pages.yml` solo se dispara con `workflow_dispatch`: no corre al subir cambios ni al fusionar,
  así que no es CI. Es un archivo de workflow nuevo y el humano lo aprueba con el ADR-G2; la revisión de
  PR (`.github/workflows/revisar-pr.yml`) no cambia.
- Antes de subir a `develop`: `uv run ruff format` y `uv run ruff check` sobre `despliegues/github-pages`,
  `python3 -m unittest discover -s despliegues/github-pages/pruebas -t .`, la cobertura con `trace`
  (≥ 80 % de líneas en `src/`), `bash despliegues/github-pages/herramientas/verificar.sh` (API y pantallas
  en local con la prueba común) y el simulacro local en «TODO BIEN».
- Después de desplegar: la prueba común contra las dos URL (`--url` y `--url-web`) y la prueba de humo.
- Comprobación de FR12.1 antes de cada push: `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío.
