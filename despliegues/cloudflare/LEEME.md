# Opción: Cloudflare Workers con un Durable Object

La API corre como un Worker de Cloudflare. Todos los datos (salas, colegios, participantes y respuestas)
viven en un solo Durable Object llamado `Reto`, con su propia base SQLite. Las pantallas se sirven como
archivos estáticos desde `web/`. Las decisiones están en los ADR-W1 a W5 de la unidad
(`aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u1-cloudflare-corte/`).

**Estado:** corte delgado (unidad U1). Ya se puede crear una sala, agregar un colegio, inscribirse,
comenzar, responder preguntas de opción y entregar. Las demás preguntas, el panel docente completo, el
tablero completo y los CSV llegan con U2 a U6. El panel docente entra, pero sus secciones todavía muestran
un error porque piden rutas que aún no existen.

## Qué hay aquí

```text
cloudflare/
├── LEEME.md
├── wrangler.jsonc          configuración del Worker y del Durable Object
├── .gitignore              deja fuera .wrangler/ y .dev.vars
├── herramientas/
│   ├── copiar.sh           copia pantallas y banco desde 2_Aplicacion_Reto/
│   └── cambios_web.patch   los dos cambios de pantalla de la nube
├── src/
│   ├── worker.js           pasa /api/* al Durable Object
│   ├── reto.js             el Durable Object: tablas, rutas y accesos
│   ├── reglas.js           reglas del reto sin E/S (las que se prueban)
│   ├── banco.json          copia del banco (generada, no se edita)
│   └── banco_huella.json   huella del banco (generada)
├── web/                    pantallas copiadas (generadas, no se editan)
└── pruebas/
    └── reglas.test.js      pruebas unitarias de reglas.js
```

No hay `package.json` ni paquetes: solo Node 24 y `npx wrangler@4.148.0`, siempre con esa versión exacta.

## Lo que se necesita

- Node 24 (trae `npx` y el ejecutor de pruebas).
- Python 3.12, para la prueba común.
- Una cuenta gratuita de Cloudflare (solo para publicar; para probar en tu computador no hace falta).

## Si cambian las pantallas o el banco de la versión local

`web/`, `src/banco.json` y `src/banco_huella.json` no se editan a mano. Desde la raíz del repositorio:

```bash
bash despliegues/cloudflare/herramientas/copiar.sh
```

El script copia de nuevo las pantallas, les aplica `cambios_web.patch` (la lista de colegios en la
inscripción y el `?sala=` del tablero) y copia el banco con su huella. Si el parche ya no aplica porque
la versión local cambió, el script se detiene: hay que rehacer el parche. El Worker no arranca si el
banco no suma 1.000 puntos o si su huella no coincide.

## Probar en tu computador

1. Crea el archivo `despliegues/cloudflare/.dev.vars` con una clave de prueba inventada, de 12
   caracteres o más y sin guion:

   ```text
   CLAVE_SEMILLERO=UNACLAVEDEPRUEBA
   ```

   Ese archivo no se sube a GitHub (lo ignora `.gitignore`). Nunca pongas allí la clave real.
2. Desde `despliegues/cloudflare/`, arranca el Worker:

   ```bash
   npx wrangler@4.148.0 dev --port 8787
   ```

3. En otra terminal, desde la raíz del repositorio, corre la prueba común (ver
   `despliegues/prueba_comun/LEEME.md`):

   ```bash
   python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8787 --clave UNACLAVEDEPRUEBA --modo nube
   ```

   Debe terminar en «TODO BIEN».
4. Las pruebas unitarias, desde la raíz del repositorio:

   ```bash
   node --test --experimental-test-coverage despliegues/cloudflare/pruebas/reglas.test.js
   ```

   Hay que nombrar el archivo: si se pasa solo la carpeta, Node 24 no encuentra las pruebas.

## Publicar en internet (lo hace el semillero, a mano)

Solo cuando no haya un reto en curso.

1. Crea una cuenta gratuita en <https://dash.cloudflare.com/sign-up> y confirma el correo.
2. Desde `despliegues/cloudflare/`, entra con tu cuenta. Se abre el navegador para autorizar:

   ```bash
   npx wrangler@4.148.0 login
   ```

3. Guarda la clave del semillero como secreto. La pide en la terminal y no queda en ningún archivo.
   Debe tener 12 caracteres o más y ningún guion; si no, las rutas de administración responden error 500.

   ```bash
   npx wrangler@4.148.0 secret put CLAVE_SEMILLERO
   ```

4. Publica:

   ```bash
   npx wrangler@4.148.0 deploy
   ```

   Al terminar muestra la dirección pública, del tipo `https://reto-desinformacion.<tu-cuenta>.workers.dev`.
5. Comprueba la publicación con la prueba común contra esa dirección:

   ```bash
   python3 despliegues/prueba_comun/src/prueba.py --url https://reto-desinformacion.<tu-cuenta>.workers.dev --clave <la clave del semillero> --modo nube
   ```

   La prueba crea una sala propia de ensayo; no toca las salas de los docentes.

## Volver a la versión anterior

Si la nueva versión falla, desde `despliegues/cloudflare/`:

```bash
npx wrangler@4.148.0 deployments list
npx wrangler@4.148.0 rollback
```

`rollback` sin más datos ofrece volver a la versión publicada justo antes y pide confirmar; también
acepta el id de una versión de las que muestra `deployments list` (`rollback <id-de-versión>`). Volver
atrás cambia el código, no los datos: las salas y respuestas guardadas en el Durable Object se quedan.

## Cómo se usa el día del reto

- El semillero crea la sala con su clave y le da al docente la clave de la sala (`CÓDIGO-SECRETO`).
- El docente agrega su colegio y abre la sala desde el panel.
- Los estudiantes entran a la dirección pública, escriben el código de sala y eligen su colegio de la
  lista.
- El tablero se abre con el enlace de la sala: `/tablero?sala=<CÓDIGO>`. Sin `?sala=` muestra «Abre el
  tablero con el enlace de tu sala.».
- Las claves van siempre en el campo de clave del panel, nunca en la dirección (`?clave=` no funciona en
  la nube).
