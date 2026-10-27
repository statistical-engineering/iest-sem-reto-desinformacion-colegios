# Publicar el reto en Render creando el servicio a mano (Docker)

Esta guía documenta el despliegue que se hizo en Render sin usar `render.yaml`: el servicio se crea
desde el panel con «New → Web Service». Documenta la creación con el plan **Compute** más económico
(`0.5c-512mb`); la sección 6 explica también el plan gratis, que solo sirve para ensayar.

Resultado: tres enlaces fijos que funcionan desde cualquier computador y red, sin que ningún
computador del equipo haga de servidor.

| Para quién | Enlace |
|---|---|
| Estudiantes | `https://<nombre-del-servicio>.onrender.com` |
| Tablero (proyector) | `https://<nombre-del-servicio>.onrender.com/tablero` |
| Panel docente | `https://<nombre-del-servicio>.onrender.com/admin` |

`<nombre-del-servicio>` es el «Name» que se escribe al crear el servicio. Si el nombre ya está
tomado, Render agrega un sufijo; el enlace real aparece arriba en la página del servicio.

> **La clave docente no se escribe en el repositorio.** En esta guía aparece como `<TU_CLAVE>`.
> Usa 12 o más caracteres: es una recomendación, el servidor no exige un mínimo. El servidor la pasa
> a mayúsculas, así que no distingue mayúsculas de minúsculas. Compártela solo con quien dirige el
> reto.
>
> **La clave se escribe solo en el formulario de `/admin`, nunca en la URL.** El servidor todavía
> acepta `?clave=` en la dirección, y en Render esa URL queda en los registros.

## 1. Antes de empezar

- El repositorio es público por decisión del 2026-10-25, con el riesgo aceptado. La imagen que
  construye Render solo lleva la carpeta `2_Aplicacion_Reto/`.
- Prueba el servidor en tu computador. Desde `2_Aplicacion_Reto/`:

  ```powershell
  uv run python pruebas/simulacro.py 40
  ```

  Debe terminar con «TODO BIEN».
- El reto real se despliega desde `main`. A `develop` se sube directo, y un push ahí reiniciaría el
  servicio en pleno reto (sección 7).

## 2. Crear el servicio

En render.com, «New → Web Service». Render detecta Python y rellena campos como si fuera una app
de Python; hay que cambiar el lenguaje a Docker.

| Campo | Valor |
|---|---|
| Source Code | El repositorio del reto. Si no aparece en la lista, autoriza a Render en GitHub; al ser público, también se puede pegar su URL |
| Name | Un nombre corto, por ejemplo `reto-desinformacion`. Forma parte del enlace |
| Language | **Docker** (no Python 3) |
| Branch | `main` |
| Region | La más cercana disponible |
| Root Directory | Vacío |
| Dockerfile Path | `./2_Aplicacion_Reto/Dockerfile` |
| Docker Build Context Directory | `./2_Aplicacion_Reto` |
| Docker Command | Vacío (se usa el `CMD` del Dockerfile) |
| Pre-Deploy Command | Vacío (el servidor crea su base de datos al iniciar) |
| Health Check Path | `/api/publico` |
| Auto-Deploy | Off (Settings → Auto-Deploy) |
| Instance Type | **Compute**, el plan más económico: 0,5 CPU, 512 MB de RAM (`0.5c-512mb`). Ver sección 6 |
| Disk (en Advanced) | Name `datos`, Mount Path `/data`, Size 1 GB. Los planes Compute admiten discos persistentes |

Los nombres exactos de los campos pueden variar con el tiempo en el panel de Render. Lo que importa
es que el lenguaje sea Docker y que el contexto de construcción sea `./2_Aplicacion_Reto`, para que
la imagen no incluya las guías con respuestas.

### Variable de entorno

| Nombre | Valor |
|---|---|
| `RETO_CLAVE` | `<TU_CLAVE>` |

No hace falta agregar nada más. Render define el puerto (`PORT`) y la URL pública
(`RENDER_EXTERNAL_URL`), y `servidor.py` los lee. El Dockerfile ya define `RETO_HOSTING=1` y
`RETO_DATOS=/data`.

Pulsa «Create Web Service», abre la pestaña «Logs» y espera de 3 a 5 minutos hasta que el estado
diga «Live».

## 3. Comprobar que funcionó

En los logs debe aparecer un recuadro con el título del reto, el número de preguntas, las
direcciones de estudiantes y tablero, el **código de sala** y la clave docente.

Abre en el navegador:

1. El enlace del servicio (pantalla de estudiantes).
2. El enlace más `/tablero` (debe mostrar el código de sala).
3. El enlace más `/admin` (pide la clave docente en un formulario).

### Cosas que parecen errores y no lo son

- **El log imprime `http://localhost:10000/admin` para el panel docente.** Es un texto fijo del
  servidor, pensado para cuando corre en un computador. En Render el panel se abre con el enlace
  público más `/admin`.
- **El panel docente no aparece enlazado en ninguna pantalla.** Se abre escribiendo `/admin` al final
  del enlace.
- **El log muestra la clave docente.** Cualquier persona con acceso al panel de Render del servicio
  puede leerla. Limita ese acceso.

## 4. Antes del día del reto

1. Abre los tres enlaces desde un celular con **datos móviles**, no con el wifi, para confirmar que
   entran desde otra red.
2. Haz una inscripción de prueba con el código de sala que muestra el tablero.
3. En `/admin`, usa «Reiniciar» (pide escribir `BORRAR`) para dejar el reto limpio.
4. Cambia la clave de ensayo por la definitiva: en el servicio, abre «Environment», edita
   `RETO_CLAVE` y elige «Save and deploy». Hazlo antes de inscribir a nadie.

La clave queda guardada en `/data/clave_docente.txt`. Quitar `RETO_CLAVE` de «Environment» **no la
borra**: el servidor sigue usando la guardada. Para cambiarla, cambia el valor de `RETO_CLAVE`.

El código de sala se genera al crear la base de datos. Si el servicio se reinicia en el plan gratis,
la base se crea de nuevo y el código **cambia**. No lo anuncies antes del día.

## 5. El día del reto

El flujo es el de `3_Guia_docente/GUIA_DOCENTE.md`, sin el paso de iniciar el servidor en un
computador:

1. Unos 30 minutos antes, abre los tres enlaces. Deja `/tablero` abierto en el computador del
   proyector y `/admin` abierto en el del docente. El tablero consulta al servidor cada 2 segundos.
2. Los estudiantes abren el enlace, se inscriben con el código de sala y anotan su código de detective.
3. En `/admin`, «Abrir el reto». Los 90 minutos los controla el servidor.
4. Al terminar, «Cerrar el reto» y luego «Publicar resultados».
5. Descarga `resultados_reto.csv` y `respuestas_detalle.csv` desde el panel.

Diferencias con la guía docente:

- **Todos los dispositivos necesitan internet** (wifi del colegio o datos móviles). La guía dice que
  no hace falta porque asume la red local.
- El panel docente se puede abrir desde cualquier computador con el enlace y la clave.

Durante el reto:

- No cambies código, preguntas, rama ni variables de entorno: cada despliegue corta el servicio cerca
  de un minuto.
- Descarga los CSV a media sesión (por ejemplo a los 45 minutos) como respaldo.

## 6. Plan Compute y plan gratis

El plan que se usa es el más económico de **Compute**, el grupo de planes de pago de Render:

| Plan | CPU | RAM | Identificador |
|---|---|---|---|
| Compute, el más económico | 0,5 | 512 MB | `0.5c-512mb` |

Es el mismo `plan: 0.5c-512mb` que declara `render.yaml` en la raíz del repositorio. De lo que ofrece
Compute, para este reto importa el **disco persistente**.

Precios: ver [`../COMPARACION.md`](../COMPARACION.md) y https://render.com/pricing. Render cobra por
uso, así que conviene crear el servicio unos días antes del reto y eliminarlo después (sección 8).

| | Free | Compute `0.5c-512mb` con disco |
|---|---|---|
| Se duerme sin tráfico | Sí, a los 15 minutos; despertar tarda cerca de 1 minuto | No |
| Disco persistente | No | Sí, montado en `/data` |
| Datos tras un reinicio | **Se pierden** (inscripciones, respuestas y código de sala) | Se conservan en el disco |

El plan gratis solo sirve para ensayar el despliegue. Para un reto con premios, usa Compute.

Con un disco adjunto, Render detiene la instancia anterior antes de iniciar la nueva, así que cada
despliegue corta el servicio cerca de un minuto. Verifica en el panel que el disco se puede agregar
al crear el servicio (campo «Disk» en «Advanced») o después, desde la configuración del servicio.

## 7. Rama y Auto-Deploy

El reto real se despliega desde `main`, con Auto-Deploy en Off (Settings → Auto-Deploy). A `develop`
se sube directo: con Auto-Deploy activo, un push ahí reiniciaría el servicio en pleno reto y cortaría
a los estudiantes que estén respondiendo.

Con disco, los datos guardados se conservan tras el despliegue; sin disco, se pierden.

## 8. Después del reto

1. Descarga los CSV de resultados desde `/admin`.
2. Elimina el servicio («Settings → Delete Web Service») para dejar de pagar. Al eliminarlo, los tres
   enlaces dejan de funcionar.

## 9. Si algo falla

| Síntoma | Causa probable |
|---|---|
| Error de `pip` o de `requirements.txt` | «Language» quedó en Python 3. Cámbialo a Docker |
| «Dockerfile not found» | Revisa que las dos rutas empiecen con `./2_Aplicacion_Reto` |
| La primera visita tarda o muestra una pantalla de Render | El servicio gratis estaba dormido; espera 1 minuto y recarga |
| El código de sala cambió | El servicio se reinició y creó una base nueva |
| `/admin` pide la clave y no la acepta | Revisa `RETO_CLAVE` en «Environment» y que el servicio se haya desplegado con el valor nuevo («Save and deploy») |
| Los estudiantes no entran | Confirma que usan el enlace público y que tienen internet |

Si el error no está en la tabla, copia las últimas 20 líneas de la pestaña «Logs» del servicio.
