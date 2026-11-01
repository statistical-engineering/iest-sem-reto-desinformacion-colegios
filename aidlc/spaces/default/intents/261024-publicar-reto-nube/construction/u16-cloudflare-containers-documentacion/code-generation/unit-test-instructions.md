# Instrucciones de pruebas — `u16-cloudflare-containers-documentacion`

- Marco: Python 3 sin paquetes (`unittest`).
- Comando de la unidad: `python3 despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion "cloudflare containers"`
- Suite: `cd despliegues/prueba_comun/herramientas && python3 -m unittest -v test_revisar_comparacion`
- Cobertura: no aplica a una tabla; la comprobación revisa cada celda de la columna.
- Sin mocks; datos: el propio `COMPARACION.md`.
