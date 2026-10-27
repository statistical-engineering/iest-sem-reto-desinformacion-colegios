# Preguntas de Contract Design

Un contrato es el acuerdo en una frontera: qué datos pasan, con qué forma y qué pasa si algo falla. En
este reto hay cuatro fronteras:

- el navegador (`web/js/`) y el servidor de cada opción: la API HTTP (FR4.1, `api-documentation.md`);
- la prueba común (U1, U2) y cada opción desplegada, por la misma API;
- U2 y U17: el archivo de mediciones;
- dentro de cada opción, las reglas («calculadoras», ADR-001) y quien las usa.

Ya está fijado: se mantienen las rutas y las claves JSON que usa `web/js/` (FR4.1), y ninguna carpeta
de opción comparte código con otra (FR12.2).

## Q1. [Arquitectura] ¿Un contrato de API para todas o uno por opción?

A. Uno solo, `despliegues/prueba_comun/contrato_api.yaml` (OpenAPI), que cumplen las tres opciones. Su
   dueño es la prueba común (U1 lo crea, U2 lo completa): si la prueba pasa, la opción cumple el
   contrato.
B. Uno por opción, dentro de su carpeta, cada uno con su dueño.
X. Other (please specify)

[Answer]: A

## Q2. [Arquitectura] ¿Cómo entran las rutas nuevas de salas y la clave del semillero?

Las rutas nuevas son: crear, listar, cerrar y borrar salas; catálogo de colegios; copias y paquete
`.zip` (FR9, FR10, FR11).

A. Bajo `/api/admin/…`, con la misma cabecera `X-Clave-Admin` de hoy. El servidor distingue la clave:
   si empieza con `KQMT-` es de esa sala; si no, se compara con la del semillero. El panel no cambia
   de cabecera.
B. Bajo `/api/semillero/…`, con una cabecera aparte `X-Clave-Semillero`.
X. Other (please specify)

[Answer]: A

## Q3. [Arquitectura] ¿Cómo se cambia el contrato después?

A. Sin versión en la ruta. Agregar una clave o una ruta se puede, porque el cliente ignora lo que no
   conoce. Quitar o renombrar exige un ADR, tu aprobación y cambiar en el mismo push `web/js/`, el
   contrato y la prueba común.
B. Con prefijo de versión (`/api/v2/…`) y la versión vieja viva un tiempo.
X. Other (please specify)

[Answer]: A

## Q4. [Desarrollo] ¿Qué responde el servidor cuando algo falla?

Hoy: `{"error": "<mensaje en español>"}` con 400, 401, 403, 404 o 413, y 500 sin detalles. Responder
dos veces la misma pregunta da 400 «ya respondida».

A. Igual que hoy en las tres opciones, más 503 `{"error": …}` si la plataforma está sin cuota o no
   responde. El navegador no reintenta un POST solo; la persona vuelve a intentar.
B. Igual que hoy, más un campo `codigo` fijo (por ejemplo `ya_respondida`) para que la prueba común no
   dependa del texto del mensaje.
X. Other (please specify)

[Answer]: A

## Q5. [Calidad] ¿Qué forma tiene el archivo de mediciones que U2 le pasa a U17?

A. Un JSON por corrida en `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json`, con un
   campo `version_esquema`, el resultado de cada comprobación y las cifras de NFR2 a NFR5.
B. Un CSV con una fila por corrida.
X. Other (please specify)

[Answer]: A

## Q6. [Arquitectura] ¿Las reglas («calculadoras») tienen la misma forma en las tres opciones?

A. Sí: mismos nombres de funciones y mismos datos de entrada y salida, descritos una vez en el
   contrato, con una tabla de casos («estos datos y esta hora dan este resultado») que cada opción
   copia como prueba. Cada unidad de reglas (U4, U8, U12) es dueña de su código.
B. No: cada opción nombra y arma sus reglas como quiera; solo la API tiene que coincidir.
X. Other (please specify)

[Answer]: A

## Revisión 2026-10-25 (una sola sala, solo Cloudflare)

Q1 a Q6 siguen valiendo con un ajuste: Q2 queda sin efecto en lo que decía de la clave del semillero y el
prefijo de sala, porque hay una sola clave docente (ADR-010). `contract-summary.md` se reescribió para
una sola sala y solo Cloudflare (FR11, FR12.2c, ADR-009 a ADR-011). Lo que no salió del humano ni de los
ADR son decisiones del asistente, con la potestad que el humano dio en la revisión de los requisitos:

- **D1.** `reto.reloj_global` (`/api/estado`, `/api/publico`) y `config.reloj_global` (`/api/admin/resumen`)
  se mantienen en el JSON con valor fijo (`true` / `"1"`) porque `web/js/` las lee (FR4.1); mandar
  `reloj_global` a `/api/admin/config` da 400. Las copias de las pantallas dejan de usarlas.
- **D2.** El estudiante recibe `participante.colegio_arranque` y `participante.colegio_restante_seg`;
  `participante.puesto_grado` solo en «resultados» y «finalizado». Nada más cambia en `/api/estado`.
- **D3.** La lista de colegios y «Arrancar reloj» van en una sola ruta, `POST /api/admin/colegios`, con
  `accion` ∈ {`agregar`, `quitar`, `arrancar`}, como `/api/admin/participante`. `agregar` acepta
  `nombres` (un nombre por línea) o `nombre`; si un nombre ya existe no se agrega ninguno (400 con
  `existente`).
- **D4.** En `/api/publico`, el podio son los tres primeros de `ranking` (no hay clave `podio`); se
  agrega `por_grado` y, en cada fila, `nota` y `puesto_grado`. Con modo sorpresa, `ranking` y `por_grado`
  se ocultan juntos hasta publicar. `colegios[]` sale en todo estado.
- **D5.** `experimento` en «cerrado» se recorta a `{n, listo}` (lo único que el tablero usa en ese estado)
  y sale completo solo en «resultados» (FR6.1).
- **D6.** Una petición a `/api/admin/*` con `clave` en la URL recibe 403 aunque la cabecera sea correcta.
  La copia de `admin.js` deja de pasar la clave a mayúsculas, porque la clave docente se compara tal cual
  (ADR-010).
- **D7.** `/api/admin/reiniciar` devuelve `copia` como `id_copia`; se agregan `GET /api/admin/copias`,
  `GET /api/admin/copia?id=` y `POST /api/admin/copia/borrar`.
- **D8.** El esquema de mediciones (C3) sigue en la versión 1 porque aún no existe ninguna medición;
  `salas` pasa a `colegios` y la parte `salas` pasa a `relojes`, y se agrega la parte `claves`.
- **D9** (decisión del asistente, con la potestad del humano). En producción `duracion_min` sigue con
  mínimo 10. Solo para probar el vencimiento por colegio, la variable `DURACION_MINIMA_MIN` puede bajar
  ese mínimo; va en `.dev.vars` (ignorado por git) para `wrangler dev` y nunca en `wrangler.jsonc` ni
  como secreto del despliegue. La prueba común contra la URL pública no prueba el vencimiento real:
  lo prueba contra `wrangler dev` con 1 minuto. Así no hay ninguna ruta ni opción pública que mueva el
  reloj (OQ3).
- **D10** (decisión del asistente). `colegios[]` en `GET /api/publico` sí sale: el nombre de un colegio
  no es un dato personal de un menor y ya aparece hoy en el tablero. OQ5 (nombres de equipos) no cambia
  con esto.
