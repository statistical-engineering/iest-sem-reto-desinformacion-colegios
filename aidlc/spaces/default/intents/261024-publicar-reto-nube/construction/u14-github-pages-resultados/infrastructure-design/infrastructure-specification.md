# Infraestructura — U14 `u14-github-pages-resultados`

U14 no agrega servicios: la misma app WSGI de PythonAnywhere y el mismo sitio de Pages de U11
(`../../u11-github-pages-corte/infrastructure-design/infrastructure-specification.md`). Nada de pago.

## Piezas

| Pieza | Qué cambia en U14 | Dónde |
|---|---|---|
| App WSGI | Resultados y Exportacion en `servicio.py`; rutas de CSV, paquete, reiniciar, copias; migración `user_version = 3` crea la tabla `copias` | Clon en PythonAnywhere, `git pull` + «Reload» |
| `reto.db` | Tabla `copias(id_copia, sala, creada, nombre_archivo, contenido BLOB)` | `~/reto_datos/` |
| Sitio de Pages | `admin/index.html`, `static/js/admin.js` y `tablero/index.html` cambian | «Run workflow» |
| `src/version.txt` | Escrito por `copiar.sh` con el commit corto; versionado para que PythonAnywhere lo tenga tras `git pull` | Repositorio |
| Diccionario | `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md` | Repositorio |

## Pasos

1. `copiar.sh` y `verificar.sh` en local (incluye abrir la copia con `sqlite3` en las pruebas).
2. Subir a `develop`.
3. Sin reto en curso: `git pull` y «Reload»; «Run workflow»; esperar la caché de Pages.
4. Prueba común completa (U2) contra las dos URL, en «TODO BIEN».
5. Ensayo de la guía de cierre contra una sala de prueba: paquete descargado, abierto y borrado de la
   sala con sus copias; `GET /api/admin/salas` sin esa sala.

Volver atrás: `git checkout <commit>` y «Reload»; «Run workflow» sobre la referencia anterior. La tabla
`copias` queda, el código anterior la ignora.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
