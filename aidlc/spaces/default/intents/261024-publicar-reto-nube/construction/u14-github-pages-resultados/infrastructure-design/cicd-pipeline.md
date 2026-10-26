# Integración y despliegue — U14

- Sin despliegue automático (FR5.2). `revisar-pr.yml` no cambia.
- Antes de subir a `develop`: ruff, `python3 -m unittest discover -s despliegues/github-pages/pruebas -t .`
  (incluidas `test_exportacion.py` y `test_resultados.py`), cobertura con `trace` ≥ 80 % en `src/`,
  `verificar.sh` y el simulacro local en «TODO BIEN».
- Cambiar una columna del paquete obliga a cambiar `DICCIONARIO_DATOS_RETO.md` en el mismo push
  (contrato C5); toda clave nueva que llegue al navegador sin clave lleva su comprobación de fugas en la
  prueba común en el mismo push (C-14).
- Después de desplegar: prueba común completa contra las dos URL; es la que U17 usa para la tabla.
- `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1).
