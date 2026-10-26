# Integración y despliegue — U12

- Sin despliegue automático (FR5.2). La única CI es `revisar-pr.yml`, que no cambia.
- Antes de subir a `develop`: ruff, `python3 -m unittest despliegues/github-pages/pruebas/test_reglas.py`,
  cobertura con `trace` ≥ 80 % en `reglas.py`, `verificar.sh` y el simulacro local en «TODO BIEN».
- Si U12 agrega casos a `despliegues/prueba_comun/casos_reglas.json`, van en el mismo push (contrato C4).
- Después de desplegar: prueba común contra las dos URL.
- `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1); copiar funciones de `servidor.py`
  no lo modifica.
