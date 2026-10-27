# Terminar la versión de Cloudflare — instrucciones para el agente

Este archivo se le da a un agente de código (o a una persona) para que termine la versión de
Cloudflare del reto. Las especificaciones ya están escritas; falta el código. Léelo completo antes de
empezar.

## Qué hay que lograr

La versión de Cloudflare (Worker con un Durable Object y SQLite) queda lista para el aula con las reglas
de negocio del 2026-10-25:

- **una sola sala**, un solo docente y un solo panel;
- una sola clave, `CLAVE_DOCENTE`, que entra solo por la cabecera `X-Clave-Admin` (nunca por `?clave=`);
- **un reloj por colegio**: el docente carga la lista de colegios y pulsa «Arrancar reloj» para cada
  uno, así cada colegio tiene sus 90 minutos completos;
- podio general (1.°, 2.° y 3.° entre todos los equipos), puesto por grado y nota de 1,0 a 5,0;
- las tres pantallas funcionan completas: estudiante (`/`), panel docente (`/admin`) y tablero
  (`/tablero`).

Hoy el código de `despliegues/cloudflare/` es el **corte delgado** (U1): funciona de punta a punta, pero
todavía tiene varias salas, la clave del semillero y solo el tipo de pregunta `opcion`.

## Qué leer, en este orden

`R` = `aidlc/spaces/default/intents/261024-publicar-reto-nube`.

1. Reglas del proyecto: `aidlc/spaces/default/memory/team.md` y `aidlc/spaces/default/memory/project.md`
   (secciones «Forbidden», «Mandated» y «Corrections»).
2. Reglas de negocio originales: `R/inception/requirements-analysis/reglas-de-negocio-2026-10-25.md`.
3. Requisitos: `R/inception/requirements-analysis/requirements.md` (FR2.5, FR2.6, FR3.1, FR11, FR12).
4. Decisiones de arquitectura: `R/inception/domain-design/decisions.md` (ADR-009, ADR-010 y ADR-011).
5. Contrato de la API: `R/inception/contract-design/contract-summary.md` y las decisiones D1 a D10 de
   `R/inception/contract-design/contract-design-questions.md`.
6. Orden de trabajo: `R/inception/delivery-planning/bolt-plan.md`.
7. Para cada unidad, en `R/construction/<unidad>/`: `functional-design/`, `decisions.md`,
   `nfr-requirements/`, `nfr-design/`, `infrastructure-design/` y, sobre todo,
   `code-generation/code-generation-plan.md` y `code-generation/unit-test-instructions.md`.
8. Como modelo de un plan ya terminado: `R/construction/u1-cloudflare-corte/code-generation/`.
9. El código actual: `despliegues/cloudflare/` y `despliegues/prueba_comun/`. La versión local de
   referencia, que **no se toca**, está en `2_Aplicacion_Reto/` (`servidor.py`, `web/`).

## Qué hacer: 5 unidades, en este orden

Cada unidad tiene un plan con pasos sin marcar (`- [ ] Paso N.`). Haz los pasos en orden y marca cada
uno con `- [x]` solo cuando su prueba pasó de verdad.

| Orden | Unidad | Plan | Pasos | Qué deja |
|---|---|---|---|---|
| 1 | `u4-cloudflare-reglas` | `R/construction/u4-cloudflare-reglas/code-generation/code-generation-plan.md` | 25 | Las reglas en JS: 10 tipos de pregunta, bono, desempate, podio, nota, transiciones; `casos_reglas.json` |
| 2 | `u5-cloudflare-salas` | `R/construction/u5-cloudflare-salas/code-generation/code-generation-plan.md` | 15 | Una sala, `CLAVE_DOCENTE`, colegios y «Arrancar reloj», vencimiento por colegio, `/api/admin/resumen` |
| 3 | `u6-cloudflare-resultados` | `R/construction/u6-cloudflare-resultados/code-generation/code-generation-plan.md` | 17 | Podio general y por grado, CSV, paquete `.zip`, «Reiniciar» con BORRAR y copias; las tres pantallas completas |
| 4 | `u2-prueba-comun` | `R/construction/u2-prueba-comun/code-generation/code-generation-plan.md` | 21 | La prueba común completa y el JSON de mediciones |
| 5 | `u17-comparacion` | `R/construction/u17-comparacion/code-generation/code-generation-plan.md` | 16 | `despliegues/COMPARACION.md`, el ADR final y las guías de despliegue (también Windows con Git Bash) |

Cada unidad depende de la anterior: no empieces U5 sin que U4 pase sus pruebas.

## Cómo se prueba

- Pruebas de reglas: `node --test despliegues/cloudflare/pruebas/<archivo>.test.js`, nombrando cada
  archivo (con una carpeta falla en Node 24). Cobertura mínima de 80 % de líneas
  (`--test-coverage-lines=80`).
- Servidor local: `npx wrangler@4.148.0 dev`, desde `despliegues/cloudflare/`. La clave va en
  `despliegues/cloudflare/.dev.vars` (ignorado por git), con `CLAVE_DOCENTE=` y `DURACION_MINIMA_MIN=1`.
- Prueba común: `python3 despliegues/prueba_comun/src/prueba.py ...`, con la clave solo en la variable
  de entorno `PRUEBA_CLAVE` (nunca como argumento, porque se vería en la lista de procesos).
- Al cerrar cada unidad: `bash despliegues/cloudflare/herramientas/verificar.sh` termina con código 0, y
  `python3 pruebas/simulacro.py 40`, desde `2_Aplicacion_Reto/`, termina en «TODO BIEN».

## Lo que nunca se hace

- Mandar respuestas correctas o explicaciones al navegador antes de que el docente publique resultados.
- Aceptar la clave en la URL (`?clave=`): da 403 aunque la cabecera sea correcta (D6).
- Escribir una clave real, datos de participantes o respuestas del banco en un archivo versionado. El
  repositorio es **público**.
- Tocar `2_Aplicacion_Reto/` (la versión local queda congelada), `4_Codigo_y_datos/datos_originales/` o
  los archivos generados (`banco_preguntas.json`, `3_Guia_docente/CLAVE_DE_RESPUESTAS.md`).
- Abrir `2_Aplicacion_Reto/datos/`, `datos_prueba/` o `.herramientas/`.
- Agregar paquetes de npm o de Python sin aprobación. El `.zip` se arma en JS puro.
- Desplegar (`wrangler deploy`) o cargar el secreto en la nube: eso lo hace el docente, a mano y sin un
  reto en curso.

## Cómo se entrega

- Una rama por unidad, creada desde `develop`, con prefijo en inglés: por ejemplo
  `feat/cloudflare-reglas`.
- Commits `tipo(alcance): descripción`, en español, con verbo en infinitivo y en minúscula, sin punto
  final y con máximo 72 caracteres. Ejemplo: `feat(cloudflare): calcular el podio por grado`.
- Pull request a `develop` de máximo 400 líneas cambiadas (sin contar `.md` ni `aidlc/`). Si no cabe,
  se parte en varios.
- Ni el commit ni el PR mencionan herramientas de IA.

## Decisiones ya tomadas sobre puntos que quedaron abiertos

Las especificaciones dejaron estos puntos en duda. Así se resuelven:

1. **Duración mínima para probar el vencimiento.** Vale lo del diseño funcional de U2:
   `DURACION_MINIMA_MIN=1` en `.dev.vars` y `--duracion-min 2` en la prueba. El «2» de `bolt-plan.md`
   está desactualizado.
2. **`/api/admin/resumen`.** Lo construye U5 (ADR-W11 de U5). U6 lo da por hecho.
3. **Comprobaciones `pantalla_*`.** Son de U2. Si U6 las necesita antes, las agrega en `prueba.py`, y
   U2 las completa después.
4. **`verificar.sh`.** U5 lo cambia a `CLAVE_DOCENTE` y quita la creación de salas. U2 lo amplía con la
   prueba completa.
5. **Fachada de reglas.** `reglas.js` conserva el alias `ESTADOS_SALA` mientras `reto.js` lo use
   (plan de U4).
6. **Tabla `copias`.** Se sigue ADR-W17 (`copias` más `copia_trozos`), no la columna `contenido` del
   contrato.
7. **Respaldo construido (FR12.6).** Manda FR12.2c: solo se construye Cloudflare.
8. **Ruta de los JS de las pantallas.** Es `web/static/js/*.js`, no `web/js/*.js`.
9. **`despliegues/prueba_comun/herramientas/revisar_comparacion.py` y su prueba.** Hoy no están en git;
   se versionan con U17, que los usa.
10. **Huellas `input_sha256` y `contract_sha256` del Testing Contract.** Se dejan como están: no las
    escribe una persona.
11. **Comandos con `--clave "$PRUEBA_CLAVE"` en el diseño funcional de U2.** No se usan así: la clave va
    solo por la variable de entorno `PRUEBA_CLAVE`.

## Cuándo está terminado

- Los 94 pasos de los cinco planes quedan marcados con `- [x]`.
- `verificar.sh` termina con código 0 y el simulacro local da «TODO BIEN».
- Probado a mano en el navegador con `wrangler dev`, con dos colegios arrancados en momentos distintos:
  inscripción, responder, vencimiento por colegio, cerrar, publicar resultados, podio y CSV.
- Queda listo para que el docente despliegue a mano siguiendo `despliegues/cloudflare/LEEME.md`.
