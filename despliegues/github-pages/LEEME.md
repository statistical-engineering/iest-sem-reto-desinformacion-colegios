# Opción: GitHub Pages con la API en otro servicio

GitHub Pages solo sirve archivos estáticos: las pantallas van en Pages, y la API, que califica y guarda
los datos, corre en otro servicio.

**Estado:** publicado como **página de entrada**: GitHub Pages solo lleva al servidor del reto, que corre
completo (pantallas y API) en PythonAnywhere con una cuenta gratuita. El código que corre allá está en
esta carpeta (`src/` y `web/`). Hay **una sala por colegio**, cada una con su clave, su reloj, su tablero
y su podio (FR11). GitHub Pages todavía no está activado en el repositorio (ver [Pendiente](#pendiente)).

| Para qué | Enlace |
|---|---|
| Estudiantes | https://angels16384.pythonanywhere.com (o con la sala puesta: `/?sala=KQMT`) |
| Panel docente y del semillero | https://angels16384.pythonanywhere.com/admin |
| Tablero y reloj de una sala | https://angels16384.pythonanywhere.com/tablero?sala=KQMT |
| Entrada por GitHub Pages (cuando se active) | https://statistical-engineering.github.io/iest-sem-reto-desinformacion-colegios/ |

Ninguna clave está en este repositorio. La del semillero vive solo en el archivo WSGI de PythonAnywhere
(ver [Paso 5](#paso-5-archivo-wsgi-y-clave-del-semillero)); la de cada sala la genera el servidor y se
muestra una sola vez.

## Cómo quedó armado

```text
navegador
   │
   ├─▶ statistical-engineering.github.io/iest-sem-reto-desinformacion-colegios/   (rama gh-pages)
   │      index.html · admin.html · tablero.html · destino.js
   │      no tiene preguntas ni respuestas: solo redirige
   │
   └─▶ angels16384.pythonanywhere.com            (cuenta gratuita de PythonAnywhere)
          src/servidor.py (WSGI) + web/ + banco_preguntas.json
          base SQLite en ~/reto_datos/reto.db: salas, colegios, participantes, respuestas
          califica y lleva el reloj y la clasificación de cada sala
```

### Por qué así y no solo con Pages

- **Pages no ejecuta código del servidor.** Las pantallas solas abren, pero muestran «Sin conexión con
  el servidor»: nadie califica, nadie guarda puntajes y no hay reloj. Se probó y se descartó.
- **La API va en PythonAnywhere** porque ya existía una versión del reto preparada para ese servicio,
  con todos los tipos de pregunta. La versión de `despliegues/cloudflare/` todavía es un corte
  delgado: solo atiende las preguntas de tipo `opcion` (`despliegues/cloudflare/LEEME.md`, «Estado»).
  Elegir entre esta opción y Cloudflare como despliegue oficial lo decide el equipo (FR12).
- **Pages redirige en vez de llamar a la API por CORS.** Así las cookies y el token quedan en un solo
  dominio, y si el servidor cambia de dirección solo se edita una línea (`destino.js`).
- **Las respuestas no salen del servidor.** `banco_preguntas.json` está solo en PythonAnywhere, que es
  quien califica. Los archivos de la rama `gh-pages` no las tienen.
- **Costo: US$ 0.** PythonAnywhere gratis no pide tarjeta; la condición es renovar cada mes (ver
  [Mantenimiento](#mantenimiento)).

### Qué hace cumplir el servidor

| Regla | Cómo |
|---|---|
| Una sala por colegio (FR11) | Tabla `salas`: cada sala tiene código, estado, reloj (apertura, pausas, minutos extra), configuración y colegios. Abrir, pausar o cerrar una sala no toca a las demás. No hay ranking general |
| Clave de cada sala | `<código>-` y 10 caracteres al azar. Solo se guarda su huella (SHA-256). Con ella se maneja solo esa sala: un `?sala=` distinto da 403 |
| Clave del semillero | La de `CLAVE_ADMIN` en el WSGI. Crea salas, ve todas, entra al panel de cualquiera (con `?sala=`), cambia la clave de una sala y borra salas cerradas |
| La clave nunca en la URL | Solo por la cabecera `X-Clave-Admin`; `?clave=` da 403 |
| Un estudiante no bloquea al docente | Tras 8 claves malas en 5 minutos se bloquea **ese navegador** (cookie `reto_nav`), no toda la IP del colegio. Un segundo freno de 40 fallos por red detiene a quien borra la cookie para seguir probando, pero no a un navegador donde el docente ya entró |
| Ids opacos (ADR-006) | El navegador ve un HMAC por participante en vez de los ids del banco; el servidor traduce la respuesta antes de calificar |
| La verdad de cada publicación del Exp. 01 | Sale en el tablero solo con los resultados publicados (FR6.1) |
| Lista cerrada de colegios | El estudiante elige de la lista de su sala (`/api/colegios?sala=`); un nombre repetido con otras mayúsculas o tildes da 400 |
| Copia al reiniciar | «Reiniciar» guarda una base SQLite solo con los datos de esa sala (sin su clave) en `~/reto_datos/copias/<sala>_<fecha>.db` |

## Cómo se desplegó, paso a paso

Para repetirlo en otra cuenta, cambia `Angels16384` por el usuario nuevo (el dominio siempre va en
minúsculas: `angels16384.pythonanywhere.com`). El servidor solo usa la biblioteca estándar de Python: no
hay que instalar paquetes ni crear un virtualenv.

### Paso 1. Cuenta

Cuenta **Beginner** (gratuita) en https://www.pythonanywhere.com/registration/register/beginner/.
Usuario: `Angels16384`. El usuario es parte del enlace, así que conviene uno corto.

### Paso 2. Web app

Pestaña **Web** → **Add a new web app**:

1. Dominio: el gratuito, `Angels16384.pythonanywhere.com` → **Next**.
2. Framework: **Manual configuration** (no Django ni Flask).
3. Python: **3.12**, la misma de `.python-version`.
4. **Next**. PythonAnywhere crea `/var/www/angels16384_pythonanywhere_com_wsgi.py` con un «Hello World».

### Paso 3. Armar y subir el paquete

Desde la raíz del repositorio, en tu computador:

```bash
python despliegues/github-pages/herramientas/empaquetar.py
```

Crea `despliegues/github-pages/dist/reto_para_internet.zip` con `src/servidor.py`, `src/wsgi_pythonanywhere.py`,
las pantallas de `web/` y el banco de `2_Aplicacion_Reto/`, todo dentro de `2_Aplicacion_Reto/` (como lo
espera el WSGI) y lista lo que quedó adentro. El `.zip` lleva el banco con las respuestas: `dist/` está en
`.gitignore` y el paquete solo se sube a PythonAnywhere.

En PythonAnywhere: pestaña **Files** → carpeta `/home/Angels16384` → **Upload a file** → ese `.zip`.

### Paso 4. Descomprimir

Pestaña **Consoles** → **Bash**:

```bash
mkdir -p ~/reto ~/reto_datos
unzip -o ~/reto_para_internet.zip -d ~/reto
```

- `~/reto/2_Aplicacion_Reto/` queda con el código.
- `~/reto_datos/` es para la base de datos y sus copias. Va **fuera** de la carpeta del código para que
  actualizar el paquete nunca borre los datos de los estudiantes.

### Paso 5. Archivo WSGI y clave del semillero

Se reemplaza el WSGI de ejemplo por `wsgi_pythonanywhere.py` del paquete, con el usuario ya puesto:

```bash
sed 's/^USUARIO = "TU_USUARIO"/USUARIO = "Angels16384"/' \
  ~/reto/2_Aplicacion_Reto/wsgi_pythonanywhere.py > /var/www/angels16384_pythonanywhere_com_wsgi.py
```

Lo que hace ese archivo:

| Variable | Valor | Para qué |
|---|---|---|
| `CLAVE_ADMIN` | la línea `CLAVE = "..."` | Clave del semillero. El servidor no arranca si tiene menos de 10 caracteres |
| `RETO_DB` | `/home/Angels16384/reto_datos/reto.db` | Base de datos fuera del código |
| `RETO_JOURNAL` | `DELETE` | El disco de PythonAnywhere es de red: SQLite en modo clásico, sin WAL |
| `RETO_URL_PUBLICA` | `https://angels16384.pythonanywhere.com` | El enlace que muestra el panel (en minúsculas, con `USUARIO.lower()`) |

Luego `from servidor import crear_app` y `application = crear_app()`.

**La clave la escribe a mano el responsable** en el editor de PythonAnywhere (Files → el archivo WSGI
→ línea `CLAVE = "..."` → **Save**). No se escribe en ningún chat, commit ni documento. Se comprueba,
sin mostrarla, que ya no sea la de ejemplo y que tenga al menos 10 caracteres:

```bash
W=/var/www/angels16384_pythonanywhere_com_wsgi.py
grep -c 'CAMBIA-ESTA-CLAVE' $W        # debe dar 0
python3.12 -c "import re; m = re.search(r'^CLAVE = \"(.*)\"', open('$W').read(), re.M); print(len(m.group(1).strip()))"
```

El segundo comando lee solo la línea `CLAVE = "..."` e imprime cuántos caracteres tiene (debe dar 10 o
más), sin ejecutar el archivo y sin mostrar la clave.

> No se recarga la web app antes de cambiar la clave: si arranca con la de ejemplo, cualquiera que la
> conozca administra todas las salas.

### Paso 6. HTTPS y recarga

Pestaña **Web**:

1. **Security → Force HTTPS → Enabled** (el certificado de `*.pythonanywhere.com` viene incluido).
2. Botón verde **Reload Angels16384.pythonanywhere.com**.

No se configuró el mapeo de **Static files** (`/static/` → `.../web/`): es solo una mejora de velocidad,
y el servidor ya entrega esos archivos.

Si en `~/reto_datos/` había una base de la versión anterior (una sola sala, sin columna `sala`), al
arrancar el servidor la renombra a `reto_antes_de_salas_<fecha>.db` sin tocar sus datos y empieza una
base nueva.

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

En tu computador, desde la raíz del repositorio:

```bash
python -m unittest discover -s despliegues/github-pages/pruebas -v
```

Son 10 pruebas: la clave solo por cabecera y el freno por navegador (`test_clave_admin.py`), los ids
opacos con la respuesta correcta de cada tipo de pregunta (`test_ids_opacos.py`), y dos salas a la vez
sin mezclar relojes, clasificaciones ni claves (`test_salas.py`, FR11.7).

Contra el servidor publicado (crea una sala de prueba propia; después se puede borrar desde el panel del
semillero):

```bash
python despliegues/prueba_comun/src/prueba.py --url https://angels16384.pythonanywhere.com --clave <clave del semillero> --modo nube
```

Debe terminar en «TODO BIEN». La clave va por la cabecera, nunca en la URL, y la prueba no la imprime.

## Pendiente

1. **Activar GitHub Pages** (lo hace un admin del repositorio): **Settings → Pages → Build and
   deployment → Source: Deploy from a branch → `gh-pages` / `(root)` → Save**. Mientras tanto, se
   comparte directo el enlace de PythonAnywhere.
2. **Elegir el despliegue oficial** entre esta opción y Cloudflare (FR12), y llenar la columna
   «GitHub Pages» de `despliegues/COMPARACION.md` con la prueba común contra el enlace publicado.
3. **Las respuestas siguen visibles en el repositorio público**: `2_Aplicacion_Reto/banco_preguntas.json`,
   `despliegues/cloudflare/src/banco.json`, `3_Guia_docente/CLAVE_DE_RESPUESTAS.md`,
   `3_Guia_docente/GUIA_ACTIVIDADES_Y_RESPUESTAS.md` y `4_Codigo_y_datos/scripts/construir_banco.py`.
   Quitarlas o volver privado el repositorio es una decisión del equipo; aun así quedan en el historial.
4. **Partes del contrato de la nube que esta opción todavía no tiene**: el catálogo único de colegios
   (ADR-002), la lista y descarga de copias (`/api/admin/copias`, `/api/admin/copia`) y el paquete de
   datos `.zip` (FR9). Hoy las copias quedan en `~/reto_datos/copias/` y se bajan desde **Files**.

## Mantenimiento

### Cada mes (obligatorio en la cuenta gratuita)

Pestaña **Web** → **Run until 1 month from today**. Si no se hace, el sitio se apaga; la primera fecha
es el **26 de noviembre de 2026**. PythonAnywhere avisa por correo una semana antes. Si se apaga, los
datos no se pierden: se renueva y vuelve con los mismos enlaces. Conviene renovar siempre la semana
antes de cada reto.

### Antes de cada reto

1. Renovar la cuenta (paso anterior).
2. El semillero entra a `/admin` con su clave → **Crear sala**, una por colegio. La clave de cada sala
   aparece **una sola vez**: anotarla y entregársela al docente de ese colegio con el código de sala.
   Si se pierde, **Nueva clave** genera otra y la anterior deja de servir.
3. Cada docente entra a `/admin` con la clave de su sala → **Configuración**: la lista de colegios (al
   menos uno, uno por línea), el nombre del evento y la duración.
4. Ensayar con 2 o 3 celulares, mejor con datos móviles y desde la red de la institución: algunas redes
   bloquean dominios de alojamiento.
5. Descargar los CSV si se quieren conservar y luego **Zona de peligro → Reiniciar esta sala** (escribir
   `BORRAR`). Borra participantes, respuestas y ranking de esa sala, guarda una copia en
   `~/reto_datos/copias/` y conserva colegios y configuración.

### Durante y después

Cada docente maneja su sala desde `/admin`: abrir el reto (el reloj de 90 minutos corre solo para esa
sala), pausar, ajustar el tiempo, cerrar y publicar resultados. El tablero de la sala se proyecta con
`/tablero?sala=<código>`. Al terminar, descargar los CSV.

**Para no quedar bloqueado:** abrir el panel en el navegador del docente **antes** de dar el enlace a los
estudiantes. Un estudiante que prueba claves solo se bloquea a sí mismo, y un navegador donde el docente
ya entró sigue funcionando aunque alguien insista desde la misma red. Si aun así aparece «Demasiados
intentos fallidos desde esta red», entrar con datos móviles o esperar 5 minutos.

Cuando una sala termina, el semillero la puede **Borrar** (solo cerrada o con resultados): se van sus
datos y sus copias.

### Actualizar preguntas o pantallas

No hacerlo con un reto en curso.

1. Si cambian las preguntas: `4_Codigo_y_datos/REGENERAR_TODO.bat` (o `.command`) regenera el banco de
   `2_Aplicacion_Reto/`. No crea el `.zip`.
2. `python despliegues/github-pages/herramientas/empaquetar.py` arma el paquete nuevo.
3. Subirlo en **Files**, reemplazando el anterior.
4. En la consola **Bash**: `unzip -o ~/reto_para_internet.zip -d ~/reto`.
5. Revisar que el WSGI conserve la clave (el `unzip` no lo toca, vive en `/var/www/`) y pulsar **Reload**.

Los datos de los estudiantes no se borran: están en `~/reto_datos/`.

### Si cambia la dirección del servidor

Editar `destino.js` en la rama `gh-pages` como dice el [Paso 7](#paso-7-página-de-entrada-en-la-rama-gh-pages),
con `push` normal. Nada más cambia.

### Si algo falla

Pestaña **Web** → **Log files → Error log**. La última línea dice qué falta; casi siempre es el usuario
mal escrito en el WSGI o una clave de menos de 10 caracteres.

## Estructura de esta carpeta

```text
github-pages/
├── LEEME.md            este archivo
├── src/
│   ├── servidor.py     el servidor del reto (local y WSGI), con salas
│   └── wsgi_pythonanywhere.py
├── web/                pantallas: estudiante, panel docente y tablero
├── herramientas/
│   └── empaquetar.py   arma dist/reto_para_internet.zip para PythonAnywhere
├── pruebas/            pruebas unitarias (python -m unittest discover -s despliegues/github-pages/pruebas)
└── dist/               el .zip (no se versiona: lleva las respuestas)
```

`src/servidor.py` sale de la copia local `Reto_Desinformacion_Colegios` (commit `e57d13a`, la versión
con WSGI para PythonAnywhere), importada sin cambios de conducta y luego modificada en PR aparte: clave
por cabecera y freno por navegador, ids opacos, salas y pantallas. No toca `2_Aplicacion_Reto/` (FR12.1).
