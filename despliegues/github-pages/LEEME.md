# Opción: GitHub Pages con la API en otro servicio

GitHub Pages solo sirve archivos estáticos: las pantallas van en Pages, y la API, que califica y guarda
los datos, corre en otro servicio.

**Estado:** publicado el 25 y 26 de octubre de 2026 como **página de entrada**: GitHub Pages solo lleva
al servidor del reto, que corre completo (pantallas y API) en PythonAnywhere con una cuenta gratuita.
Se puede jugar de punta a punta. GitHub Pages todavía no está activado en el repositorio (ver
[Pendiente](#pendiente)).

| Para qué | Enlace |
|---|---|
| Estudiantes | https://angels16384.pythonanywhere.com |
| Panel docente | https://angels16384.pythonanywhere.com/admin |
| Tablero y reloj para proyectar | https://angels16384.pythonanywhere.com/tablero |
| Entrada por GitHub Pages (cuando se active) | https://statistical-engineering.github.io/iest-sem-reto-desinformacion-colegios/ |

La clave del panel docente **no** está en este repositorio: vive solo en el archivo WSGI de
PythonAnywhere (ver [Paso 5](#paso-5-archivo-wsgi-y-clave-docente)).

## Cómo quedó armado

```text
navegador del estudiante
   │
   ├─▶ statistical-engineering.github.io/iest-sem-reto-desinformacion-colegios/   (rama gh-pages)
   │      index.html · admin.html · tablero.html · destino.js
   │      no tiene preguntas ni respuestas: solo redirige
   │
   └─▶ angels16384.pythonanywhere.com            (cuenta gratuita de PythonAnywhere)
          servidor.py (WSGI) + web/ + banco_preguntas.json
          base de datos SQLite en ~/reto_datos/reto.db
          califica, lleva el reloj común y el ranking único
```

### Por qué así y no solo con Pages

- **Pages no ejecuta código del servidor.** Las pantallas solas abren, pero muestran «Sin conexión con
  el servidor»: nadie califica, nadie guarda puntajes y no hay reloj. Se probó y se descartó.
- **La API va en PythonAnywhere** porque ya existía una versión del reto preparada para ese servicio,
  con todos los tipos de pregunta. La versión de `despliegues/cloudflare/` todavía es un corte
  delgado: solo atiende las preguntas de tipo `opcion` (`despliegues/cloudflare/LEEME.md`, «Estado»).
- **Pages redirige en vez de llamar a la API por CORS.** Así no se cambia ninguna pantalla ni el
  servidor, las cookies y el token quedan en un solo dominio, y si el servidor cambia de dirección
  solo se edita una línea (`destino.js`).
- **Las respuestas no llegan al navegador.** En PythonAnywhere el banco solo lo lee el servidor, que es
  quien califica, y la rama `gh-pages` no lo tiene. Pero el banco y las guías con respuestas siguen
  públicos en este repositorio (ver [Pendiente](#pendiente)).
- **Costo: US$ 0.** PythonAnywhere gratis no pide tarjeta; la condición es renovar cada mes (ver
  [Mantenimiento](#mantenimiento)).

### De dónde sale el código que corre en PythonAnywhere

El servidor publicado **no sale de `develop`**. Sale de la copia local del proyecto
`Reto_Desinformacion_Colegios` (commit `e57d13a`, 19 de octubre de 2026: «reloj común controlado por la
organización, varios colegios con un solo ranking, WSGI para PythonAnywhere gratis, prueba de carga»),
empaquetada en `PUBLICAR EN INTERNET/reto_para_internet.zip`.

Esa versión tiene `crear_app()` (punto de entrada WSGI) y el manejo de varios colegios, que el
`2_Aplicacion_Reto/servidor.py` de `develop` todavía no tiene. Llevar esos cambios a este repositorio
queda pendiente.

Contenido del paquete (10 archivos, 82 KB):

```text
2_Aplicacion_Reto/servidor.py
2_Aplicacion_Reto/banco_preguntas.json
2_Aplicacion_Reto/wsgi_pythonanywhere.py
2_Aplicacion_Reto/web/admin.html
2_Aplicacion_Reto/web/estudiante.html
2_Aplicacion_Reto/web/tablero.html
2_Aplicacion_Reto/web/css/reto.css
2_Aplicacion_Reto/web/js/admin.js
2_Aplicacion_Reto/web/js/estudiante.js
2_Aplicacion_Reto/web/js/graficos.js
```

El servidor solo usa la biblioteca estándar de Python (`http.server`, `sqlite3`, `csv`…): no hay que
instalar paquetes ni crear un virtualenv.

## Cómo se desplegó, paso a paso

Así se hizo la primera vez. Para repetirlo en otra cuenta, cambia `Angels16384` por el usuario nuevo
(el dominio siempre va en minúsculas: `angels16384.pythonanywhere.com`).

### Paso 1. Cuenta

Cuenta **Beginner** (gratuita) en https://www.pythonanywhere.com/registration/register/beginner/.
Usuario: `Angels16384`. El usuario es parte del enlace, así que conviene uno corto.

### Paso 2. Web app

Pestaña **Web** → **Add a new web app**:

1. Dominio: el gratuito, `Angels16384.pythonanywhere.com` → **Next**.
2. Framework: **Manual configuration** (no Django ni Flask).
3. Python: **3.12**, la misma de `.python-version`.
4. **Next**. PythonAnywhere crea `/var/www/angels16384_pythonanywhere_com_wsgi.py` con un «Hello World».

### Paso 3. Subir el paquete

Pestaña **Files** → carpeta `/home/Angels16384` → **Upload a file** → `reto_para_internet.zip`.

### Paso 4. Descomprimir

Pestaña **Consoles** → **Bash**:

```bash
mkdir -p ~/reto ~/reto_datos
unzip -o ~/reto_para_internet.zip -d ~/reto
```

- `~/reto/2_Aplicacion_Reto/` queda con el código.
- `~/reto_datos/` es para la base de datos. Va **fuera** de la carpeta del código para que actualizar el
  paquete nunca borre los datos de los estudiantes.

### Paso 5. Archivo WSGI y clave docente

Se reemplazó el WSGI de ejemplo por `wsgi_pythonanywhere.py` del paquete, con el usuario ya puesto:

```bash
sed 's/^USUARIO = "TU_USUARIO"/USUARIO = "Angels16384"/' \
  ~/reto/2_Aplicacion_Reto/wsgi_pythonanywhere.py > /var/www/angels16384_pythonanywhere_com_wsgi.py
```

Lo que hace ese archivo:

| Variable | Valor | Para qué |
|---|---|---|
| `CLAVE_ADMIN` | la línea `CLAVE = "..."` | Clave del panel docente. El servidor no arranca si tiene menos de 10 caracteres |
| `RETO_DB` | `/home/Angels16384/reto_datos/reto.db` | Base de datos fuera del código |
| `RETO_JOURNAL` | `DELETE` | El disco de PythonAnywhere es de red: SQLite en modo clásico, sin WAL |
| `RETO_URL_PUBLICA` | `https://angels16384.pythonanywhere.com` | El enlace que muestra el panel (en minúsculas) |

Luego `from servidor import crear_app` y `application = crear_app()`.

El `wsgi_pythonanywhere.py` del paquete arma esa URL con el usuario tal cual (`Angels16384`). Para que
quede en minúsculas se ajustó esa línea en el WSGI publicado:

```bash
sed -i 's|^os.environ\["RETO_URL_PUBLICA"\] = .*|os.environ["RETO_URL_PUBLICA"] = "https://angels16384.pythonanywhere.com"|' \
  /var/www/angels16384_pythonanywhere_com_wsgi.py
```

**La clave la escribió a mano el responsable** en el editor de PythonAnywhere (Files → el archivo WSGI
→ línea `CLAVE = "..."` → **Save**). No se escribió en ningún chat, commit ni documento. Se comprobó,
sin mostrarla, que ya no fuera la de ejemplo y que tuviera al menos 10 caracteres:

```bash
W=/var/www/angels16384_pythonanywhere_com_wsgi.py
grep -c 'CAMBIA-ESTA-CLAVE' $W        # debe dar 0
python3.12 -c "import re; m = re.search(r'^CLAVE\s*=\s*[\"\x27](.*?)[\"\x27]', open('$W').read(), re.M); print(len(m.group(1).strip()) if m else 'AVISO: no se encontro la linea CLAVE = ...')"
```

El segundo comando lee solo la línea `CLAVE = "..."` (con comillas dobles o simples, con o sin espacios
alrededor del `=`) e imprime cuántos caracteres tiene: debe dar 10 o más. Si no encuentra la línea, imprime
un aviso. No ejecuta el archivo ni muestra la clave.

> No se recarga la web app antes de cambiar la clave: si arranca con la de ejemplo, cualquiera que la
> conozca entra al panel.

### Paso 6. HTTPS y recarga

Pestaña **Web**:

1. **Security → Force HTTPS → Enabled** (el certificado de `*.pythonanywhere.com` viene incluido).
2. Botón verde **Reload Angels16384.pythonanywhere.com**.

No se configuró el mapeo de **Static files** (`/static/` → `.../web/`) que sugiere la guía del paquete:
es solo una mejora de velocidad, y el servidor ya entrega esos archivos.

### Paso 7. Página de entrada en la rama `gh-pages`

Rama huérfana (sin historial en común con `develop`, no se fusiona) con 5 archivos:

| Archivo | Qué hace |
|---|---|
| `destino.js` | Única línea que se edita: `window.RETO_SERVIDOR = "https://angels16384.pythonanywhere.com";` |
| `index.html` | Lleva a `/` del servidor (inscripción de estudiantes) |
| `admin.html` | Lleva a `/admin` (panel docente) |
| `tablero.html` | Lleva a `/tablero` (reloj y tablero) |
| `.nojekyll` | Pages sirve los archivos tal cual, sin procesarlos con Jekyll |

Las tres páginas conservan `?sala=...` y el `#...` del enlace, y muestran un botón «Entrar al reto» por si
el navegador bloquea la redirección. Si `destino.js` todavía dice `TU_USUARIO`, no redirigen.

La rama se creó una sola vez, desde una carpeta aparte con esos archivos (`git init -b gh-pages`,
commit y push). Para cambiarla después **no se usa `push -f`**, que borra lo que otra persona haya
subido: se clona solo esa rama, se cambia el archivo y se hace un `push` normal.

```bash
git clone --branch gh-pages --single-branch \
  git@github.com:statistical-engineering/iest-sem-reto-desinformacion-colegios.git reto-gh-pages
cd reto-gh-pages
# editar destino.js (o la página que haga falta)
git add destino.js
git commit -m "chore(pages): cambiar la direccion del servidor"
git push
```

Si `git push` responde que la rama remota tiene cambios nuevos, primero `git pull` y luego `git push`.

### Paso 8. Verificación

| Comprobación | Resultado |
|---|---|
| `curl -s -o /dev/null -w "%{http_code}" https://angels16384.pythonanywhere.com/` | `200`, título «Detectives de la desinformación» |
| Lo mismo con `/admin` y `/tablero` | `200` |
| `/api/estado` sin sesión | `401` (la API no responde a quien no se inscribió) |
| Abrir el enlace en el navegador | Sale la inscripción: «¿Lo compartirías?» |
| Entrar a `/admin` con la clave | Funciona |
| Reto de práctica completo (inscribirse, responder, entregar) | Funciona |
| Redirección de `destino.js` (probada con Node) | `/admin?sala=ABC` → `https://angels16384.pythonanywhere.com/admin?sala=ABC` |
| https://statistical-engineering.github.io/iest-sem-reto-desinformacion-colegios/ | `404` hasta que se active Pages |

## Pendiente

1. **Activar GitHub Pages** (lo hace un admin del repositorio): **Settings → Pages → Build and
   deployment → Source: Deploy from a branch → `gh-pages` / `(root)` → Save**. Mientras tanto, se
   comparte directo el enlace de PythonAnywhere.
2. **Las respuestas siguen visibles en el repositorio público**: `2_Aplicacion_Reto/banco_preguntas.json`,
   `despliegues/cloudflare/src/banco.json`, `3_Guia_docente/CLAVE_DE_RESPUESTAS.md`,
   `3_Guia_docente/GUIA_ACTIVIDADES_Y_RESPUESTAS.md` y `4_Codigo_y_datos/scripts/construir_banco.py`.
   Quitarlas o volver privado el repositorio es una decisión del equipo; aun así quedan en el historial.
3. **Llevar a `develop` la versión del servidor que corre en PythonAnywhere** (`crear_app()`, varios
   colegios, reloj común), para que este repositorio y lo publicado coincidan.
4. **Llenar la columna «PythonAnywhere» de `despliegues/COMPARACION.md`** con la prueba común
   (`despliegues/prueba_comun/`) contra el enlace de PythonAnywhere. Es una opción aparte de «GitHub
   Pages»: Pages solo redirige, y lo que se mide (latencia, reinicios, cuota) es el servidor.

## Mantenimiento

### Cada mes (obligatorio en la cuenta gratuita)

Pestaña **Web** → **Run until 1 month from today**. Si no se hace, el sitio se apaga; la primera fecha
es el **26 de noviembre de 2026**. PythonAnywhere avisa por correo una semana antes. Si se apaga, los
datos no se pierden: se renueva y vuelve con los mismos enlaces. Conviene renovar siempre la semana
antes de cada reto.

### Antes de cada reto

1. Renovar la cuenta (paso anterior).
2. En `/admin` → **Configuración**: lista de colegios (uno por línea) y código de sala.
3. Ensayar con 2 o 3 celulares, mejor con datos móviles y desde la red de la institución: algunas redes
   bloquean dominios de alojamiento.
4. Descargar los CSV si se quieren conservar y luego **Zona de peligro → Reiniciar** (escribir
   `BORRAR`). Borra participantes, respuestas y ranking, guarda una copia de seguridad en
   `~/reto_datos/` y conserva preguntas, colegios y código de sala.

### Durante y después

Todo se maneja desde `/admin`: abrir el reto (un solo reloj de 90 minutos para todos los colegios),
pausar, ajustar el tiempo, cerrar y publicar resultados. Al terminar, descargar los CSV.

Cuidado con la clave en redes compartidas: tras **8 intentos fallidos en 5 minutos** el servidor
bloquea el panel 5 minutos para toda esa IP, y en una institución todos salen por la misma IP. Los
códigos de estudiante se bloquean después de 40 fallos por minuto por IP.

### Actualizar preguntas o pantallas

No hacerlo con un reto en curso.

1. En la copia local, ejecutar `4_Codigo_y_datos/REGENERAR_TODO.bat`. Regenera el banco y las guías,
   pero **no** crea el `.zip`.
2. Armar el paquete a mano. En PowerShell, desde la carpeta `Reto_Desinformacion_Colegios` de la copia
   local (`tar` viene con Windows 10 y 11):

   ```powershell
   tar -a -cf reto_para_internet.zip 2_Aplicacion_Reto/servidor.py 2_Aplicacion_Reto/banco_preguntas.json 2_Aplicacion_Reto/wsgi_pythonanywhere.py 2_Aplicacion_Reto/web
   tar -tf reto_para_internet.zip
   ```

   El segundo comando lista lo que quedó adentro: 13 líneas, los 10 archivos de la lista de arriba más
   las carpetas `2_Aplicacion_Reto/web/`, `web/css/` y `web/js/`.
3. Subirlo en **Files**, reemplazando el anterior.
4. En la consola **Bash**: `unzip -o ~/reto_para_internet.zip -d ~/reto`.
5. Revisar que el WSGI conserve la clave (el `unzip` no lo toca, vive en `/var/www/`) y pulsar **Reload**.

Los datos de los estudiantes no se borran: están en `~/reto_datos/`.

### Si cambia la dirección del servidor

Editar `destino.js` en la rama `gh-pages` como dice el [Paso 7](#paso-7-página-de-entrada-en-la-rama-gh-pages), con `push` normal. Nada más cambia.

### Si algo falla

Pestaña **Web** → **Log files → Error log**. La última línea dice qué falta; casi siempre es el usuario
mal escrito en el WSGI o una clave de menos de 10 caracteres.

## Estructura de esta carpeta

```text
github-pages/
├── LEEME.md    este archivo: cómo quedó publicado y cómo se mantiene
├── web/        vacío: la página de entrada vive en la rama gh-pages
├── src/        vacío: la API corre en PythonAnywhere
└── pruebas/    vacío
```
