# Infraestructura — U12 `u12-github-pages-reglas`

U12 no agrega infraestructura: `reglas.py` va dentro de la misma app WSGI de PythonAnywhere que creó
U11 (`../../u11-github-pages-corte/infrastructure-design/infrastructure-specification.md`). Nada de pago.

## Piezas

| Pieza | Configuración | Dónde |
|---|---|---|
| `src/reglas.py` | Módulo importado por `servicio.py`; sin configuración | Clon del repositorio en PythonAnywhere |
| `pruebas/casos_reglas.json` | Copia de datos de `despliegues/prueba_comun/casos_reglas.json` hecha por `herramientas/copiar.sh` | Repositorio |
| `.trace/` | Carpeta de salida de `trace`, ignorada por git | Solo en local |

## Pasos

1. `bash despliegues/github-pages/herramientas/copiar.sh` (copia también `casos_reglas.json`).
2. `bash despliegues/github-pages/herramientas/verificar.sh`: pruebas unitarias con cobertura, API y
   pantallas en local, prueba común.
3. Subir a `develop`; en PythonAnywhere, `git pull` y «Reload» (solo sin reto en curso).
4. Prueba común contra las dos URL.

Volver atrás: `git checkout <commit>` y «Reload». No toca datos.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
