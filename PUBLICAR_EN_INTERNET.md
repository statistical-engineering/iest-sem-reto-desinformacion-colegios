# Publicar el reto en internet (enlace fijo, funciona desde cualquier red)

Resultado: un enlace como `https://reto-desinformacion.onrender.com` que los estudiantes abren desde
cualquier celular o computador, en cualquier red. Tu computador puede estar apagado.

Costo aproximado: unos US$7 al mes por el servidor + US$0,25 por GB de disco, **cobrado por segundo**
(precios de render.com, pueden cambiar). Si lo creas unos días antes del reto y lo eliminas después,
pagas centavos o pocos dólares. El plan gratis NO sirve: se duerme y borra la base de datos al reiniciar.

> **El repositorio debe ser PRIVADO.** `3_Guia_docente/CLAVE_DE_RESPUESTAS.md` y
> `GUIA_ACTIVIDADES_Y_RESPUESTAS.md` traen todas las respuestas; en un repositorio público los
> estudiantes podrían encontrarlas. Para que otras personas del semillero lo modifiquen, agrégalas como
> colaboradoras (Settings → Collaborators). La imagen que se publica en Render solo lleva la aplicación,
> no las guías.

## Parte 1 — Subir esta carpeta a GitHub (GitHub Desktop, sin comandos)
1. Instala **GitHub Desktop** (https://desktop.github.com) e inicia sesión con tu cuenta de GitHub.
2. Menú **File → Add Local Repository…** y elige **esta carpeta completa** (`Reto_Desinformacion_Colegios`).
3. Si dice que no es un repositorio, pulsa **create a repository** → **Create Repository**.
4. Abajo a la izquierda escribe `Primera version` y pulsa **Commit to main**.
5. Arriba pulsa **Publish repository**, deja marcada **Keep this code private** y pulsa **Publish**.

(`.gitignore` ya deja fuera las bases de datos y claves locales, y `.gitattributes` cuida que los
`.bat` de Windows y los `.command` de Mac no se dañen.)

## Parte 2 — Publicarlo en Render
1. Entra a https://render.com → **Get Started** → **Sign up with GitHub** y autoriza el acceso.
2. **New +** → **Blueprint** → elige el repositorio → **Connect**. (Usa el archivo `render.yaml` de esta carpeta.)
3. Te pide `RETO_CLAVE`: escribe la clave del panel docente (8 o más letras/números, sin espacios).
4. **Apply** (te pedirá una tarjeta). Espera 3–5 minutos hasta que diga **Live**.
5. Arriba verás el enlace `https://….onrender.com`:
   - Estudiantes: ese enlace · Panel docente: ese enlace + `/admin` · Tablero: ese enlace + `/tablero`

Notas: el servidor debe correr en **una sola instancia** (lleva el reloj y la clasificación en memoria);
cambiar preguntas o código reinicia el servicio, **no lo hagas con un reto en curso**.

## Antes del reto
- Abre el enlace desde un celular **con datos móviles** (no con el wifi) para confirmar que entra desde otra red.
- Haz una inscripción de prueba y luego, en el panel docente, **Reiniciar** (pide escribir BORRAR).
- Si cambiaste preguntas o datos: `4_Codigo_y_datos/REGENERAR_TODO` (`.bat` en Windows, `.command` en Mac)
  y vuelve a subir los cambios desde GitHub Desktop (Commit + Push).

## Después del reto
- En el panel docente descarga los CSV de resultados.
- En Render: el servicio → **Settings** → **Delete Web Service** para dejar de pagar.

## Opciones gratis para ensayar (sin publicar)
Detalle en `2_Aplicacion_Reto/LEEME.md`: misma red wifi (`INICIAR_RETO`) o un enlace temporal desde tu
computador (`INICIAR_RETO_INTERNET.command`, solo Mac; el computador debe quedar encendido).
