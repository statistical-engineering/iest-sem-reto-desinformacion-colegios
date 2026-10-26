# Infraestructura — U11 `u11-github-pages-corte`

Sale de `../nfr-design/` y de `../decisions.md` (ADR-G1 a ADR-G7). Todo en los planes gratuitos de
GitHub y de PythonAnywhere; nada de pago (regla de `project.md`). Dos servicios externos.

## Piezas

| Pieza | Configuración | Dónde |
|---|---|---|
| Sitio de Pages | Settings → Pages → Source: «GitHub Actions»; URL `https://<cuenta>.github.io/<repositorio>/` | Repositorio público en GitHub |
| Flujo `Publicar pantallas` | `.github/workflows/publicar-pages.yml`: `on: workflow_dispatch`; `permissions: pages: write, id-token: write, contents: read`; `actions/configure-pages@v5`, `actions/upload-pages-artifact@v4` con `path: despliegues/github-pages/web`, `actions/deploy-pages@v4`; `environment: github-pages` | Raíz del repositorio (archivo nuevo, aprobación del humano según ADR-G2) |
| App web de PythonAnywhere | «Manual configuration», Python 3.10 o más reciente de la imagen de la cuenta; archivo WSGI de la pestaña Web según `herramientas/wsgi_pythonanywhere.ejemplo.py`; sin mapeo de estáticos (las sirve Pages) | Cuenta gratuita del semillero, `https://<usuario>.pythonanywhere.com` |
| Clon del repositorio | `~/Reto_Desinformacion_Colegios`, rama `develop`, actualizado con `git pull` desde una consola Bash | Disco de PythonAnywhere |
| Datos | `~/reto_datos/reto.db` (`RETO_DATOS`) | Disco de PythonAnywhere, fuera del clon |
| Secretos | `~/.reto_secretos/clave_semillero.txt` (permisos 600), leído por el archivo WSGI; `RETO_ORIGENES=https://<cuenta>.github.io` | Disco de PythonAnywhere, fuera del clon |
| URL de la API para las pantallas | `herramientas/config.js` → `web/static/js/config.js` | Repositorio (es pública) |

## Pasos (los pone en palabras simples `despliegues/github-pages/LEEME.md`)

1. `herramientas/copiar.sh` copia `web/` con su parche, `config.js` y el banco con su huella.
2. Pruebas en local: `herramientas/verificar.sh` (unitarias, `servidor_local.py` y la prueba común con
   `--url http://localhost:8791 --url-web http://localhost:8792`).
3. Subir a `develop`.
4. PythonAnywhere: crear la cuenta gratuita; en una consola Bash, `git clone` del repositorio y
   `mkdir -p ~/reto_datos ~/.reto_secretos`; escribir la clave del semillero en
   `~/.reto_secretos/clave_semillero.txt` y `chmod 600`; en la pestaña Web, «Add a new web app» →
   «Manual configuration»; pegar la plantilla WSGI con la ruta del clon y el origen de Pages; «Reload».
5. GitHub: Settings → Pages → Source «GitHub Actions»; Actions → «Publicar pantallas» → «Run workflow»
   sobre `develop`. Esperar la URL que muestra el entorno `github-pages`.
6. Prueba común contra las dos URL:
   `python3 despliegues/prueba_comun/src/prueba.py --url https://<usuario>.pythonanywhere.com --url-web https://<cuenta>.github.io/<repositorio> --clave <clave del semillero> --modo nube`.
7. Prueba de humo del `LEEME.md`: abrir el enlace de Pages desde datos móviles, inscribirse y responder.

Actualizar: `git pull` y «Reload» para la API; «Run workflow» para las pantallas. Volver atrás:
`git checkout <commit>` y «Reload»; «Run workflow» sobre la referencia anterior. Los datos no se tocan
en ningún caso. Antes de cada reto: prorrogar la app en la pestaña Web (vence al mes sin uso, U11-R5).

## Monitoreo y despliegue

Ver `monitoring-design.md` y `cicd-pipeline.md`.
