# Integración y despliegue — U13

- Sin despliegue automático (FR5.2). `revisar-pr.yml` no cambia.
- Antes de subir a `develop`: ruff, `python3 -m unittest discover -s despliegues/github-pages/pruebas -t .`,
  cobertura con `trace` ≥ 80 % en `src/`, `verificar.sh` y el simulacro local en «TODO BIEN».
- Si la unidad pasa de 400 líneas de código la sube el humano o el asistente directo a `develop`
  (`team.md`, «Corrections»); otra persona la parte en varios PR.
- Después de desplegar: prueba común contra las dos URL, incluida la parte de varias salas (FR11.7).
- `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1).
