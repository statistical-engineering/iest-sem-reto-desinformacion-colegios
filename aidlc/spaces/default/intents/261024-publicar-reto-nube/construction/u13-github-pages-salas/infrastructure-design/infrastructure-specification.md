# Infraestructura — U13 `u13-github-pages-salas`

U13 no agrega infraestructura: corre en la misma app WSGI de PythonAnywhere y el mismo sitio de Pages
de U11 (`../../u11-github-pages-corte/infrastructure-design/infrastructure-specification.md`). Nada de
pago.

## Piezas

| Pieza | Qué cambia en U13 | Dónde |
|---|---|---|
| App WSGI | `servicio.py` y la tabla de rutas crecen; la migración `user_version = 2` corre sola al arrancar | Clon en PythonAnywhere, `git pull` + «Reload» |
| `reto.db` | Dos columnas nuevas (`colegios.unido_a`, `participantes.n_integrantes`) por `ALTER TABLE`; los datos del corte se conservan | `~/reto_datos/` |
| Sitio de Pages | `admin/index.html` y `static/js/admin.js` cambian (panel de salas, catálogo, colegios) | «Run workflow» de `publicar-pages.yml` |

## Pasos

1. `copiar.sh` (reaplica el parche con los cambios del panel) y `verificar.sh` en local.
2. Subir a `develop`.
3. Sin reto en curso: `git pull` y «Reload» en PythonAnywhere; «Run workflow» para las pantallas;
   esperar los 10 minutos de la caché de Pages.
4. Prueba común contra las dos URL, ahora con la parte de varias salas.

Volver atrás: `git checkout <commit>` y «Reload»; «Run workflow» sobre la referencia anterior. La
migración no se deshace, pero el código anterior ignora las columnas nuevas.

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
