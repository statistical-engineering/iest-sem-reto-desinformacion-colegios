#!/usr/bin/env bash
# Copia las pantallas y el banco de la versión local (2_Aplicacion_Reto/) a la opción Cloudflare Workers.
#
# Uso, desde cualquier carpeta:   bash despliegues/cloudflare/herramientas/copiar.sh
# Requiere: bash, git y node (los mismos que pide wrangler).
#
# Qué hace, en orden, y se detiene al primer error:
#   1. Borra despliegues/cloudflare/web/ y vuelve a copiar 2_Aplicacion_Reto/web/ sin cambiar su
#      contenido, con la forma que piden los recursos estáticos de Workers: estudiante.html queda como
#      index.html (la página de «/») y css/ y js/ quedan dentro de static/ (las páginas los piden en
#      /static/...).
#   2. Aplica los dos cambios del corte, guardados en herramientas/cambios_web.patch: la lista de
#      colegios en static/js/estudiante.js y el ?sala= de tablero.html. Si la versión local cambió y
#      el parche ya no aplica, se detiene y hay que rehacer el parche.
#   3. Copia 2_Aplicacion_Reto/banco_preguntas.json a src/banco.json (fuera de web/: nunca se sirve) y
#      guarda su huella en src/banco_huella.json. El Worker no arranca si src/banco.json cambia sin
#      volver a correr este script, o si el banco no suma 1.000 puntos.
#
# Nunca modifica 2_Aplicacion_Reto/.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPCION="$(dirname "$AQUI")"
RAIZ="$(cd "$OPCION/../.." && pwd)"
ORIGEN="$RAIZ/2_Aplicacion_Reto"
WEB="$OPCION/web"

rm -rf "$WEB"
mkdir -p "$WEB/static"
cp "$ORIGEN/web/estudiante.html" "$WEB/index.html"
cp "$ORIGEN/web/admin.html" "$ORIGEN/web/tablero.html" "$WEB/"
cp -R "$ORIGEN/web/css" "$ORIGEN/web/js" "$WEB/static/"

git -C "$RAIZ" apply --whitespace=nowarn "despliegues/cloudflare/herramientas/cambios_web.patch"

cp "$ORIGEN/banco_preguntas.json" "$OPCION/src/banco.json"
HUELLA="$(node -e '
const fs = require("fs");
const crypto = require("crypto");
const banco = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
process.stdout.write(crypto.createHash("sha256").update(JSON.stringify(banco)).digest("hex"));
' "$OPCION/src/banco.json")"
printf '{"sha256": "%s"}\n' "$HUELLA" > "$OPCION/src/banco_huella.json"

echo "Listo: pantallas en despliegues/cloudflare/web/ y banco en despliegues/cloudflare/src/banco.json."
