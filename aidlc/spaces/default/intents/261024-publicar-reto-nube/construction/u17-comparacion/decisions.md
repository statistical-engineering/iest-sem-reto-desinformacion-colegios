# ADR de la comparación final (U17)

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Solo se construye y se mide Cloudflare
> Workers (FR12.2c).
>
> - **ADR-C1:** cuenta el secreto `CLAVE_DOCENTE` en vez de `CLAVE_SEMILLERO`.
> - **ADR-C2:** pasa a cuatro opciones sin medir. GitHub Pages entra como «no se construye».
> - **ADR-C3:** Cloudflare es la única candidata. Si pasa todo, gana sin respaldo construido y la versión
>   local queda como respaldo de aula.
> - **ADR-C4:** la guía es para un docente, una clave y una sala, con colegios y «Arrancar reloj».
> - **Nuevos:** ADR-C5 (dos mediciones de Cloudflare: `wrangler dev` y la URL pública) y ADR-C6 (pasos
>   para Windows con Git Bash).

Decisiones de `u17-comparacion`: cómo se cuenta, cómo entra cada opción, quién gana, cómo se lee la
medición de Cloudflare y cómo se escribe la guía. Salen de FR12.2c, FR12.4 a FR12.6, FR8 y de `project.md`
(«Corrections», parsimonia). Son decisiones del asistente con la potestad que dio el humano (2026-10-25).
El ADR-C3 queda «Proposed» hasta que el humano lo apruebe con la tabla cerrada, como exige FR12.6.

## ADR-C1: Cómo se cuentan servicios externos, piezas propias y líneas de código

**Estado:** Accepted (2026-10-25); revisado el 2026-10-25 para una sola sala.

**Contexto.** FR12.6 ordena las opciones que pasan todo por tres criterios: «menos servicios externos»,
«menos piezas propias que desplegar» y «menos líneas de código». Pero no dice cómo contar. Sin una regla
fija, dos personas contarían distinto: ¿un Durable Object es un servicio aparte? ¿Cuenta la copia de
`web/`? Con una sola candidata construida, el conteo ya no decide, pero queda en la tabla como evidencia
de parsimonia.

**Decisión.**

- **Servicio externo:** cada cuenta o producto que la persona del semillero crea o activa por separado y
  que tiene su propio panel o cuota. Lo que se despliega junto, con un solo comando y en la misma cuenta,
  cuenta como 1. Conteos:
  - Workers (Worker + Durable Object + recursos estáticos con un solo `wrangler deploy`) = 1;
  - GitHub Pages = Pages + el servicio de la API (+ 1 si el almacén de datos es otro proveedor) ≥ 2;
  - Apps Script + Google Sheets = 2;
  - Render = 1;
  - Cloudflare Containers = 1.
- **Pieza propia:** cada fila de la tabla «Piezas» de `infrastructure-specification.md` de la opción que
  alguien configura, sin contar el enlace fijo que asigna el proveedor. Workers = 4: Worker, recursos
  estáticos, Durable Object y secreto `CLAVE_DOCENTE`. `DURACION_MINIMA_MIN` no cuenta, porque solo va
  en `.dev.vars` de `wrangler dev` y nunca en el despliegue (D9).
- **Líneas de código:** se cuentan con `git ls-files despliegues/<opcion> | grep -v -E
  "^despliegues/<opcion>/(web/|src/banco\.json|src/banco_huella\.json|LEEME\.md|\.gitignore)$" | xargs wc
  -l | tail -1`, corrido sobre un commit que se anota.
  - **Cuentan:** `src/`, `pruebas/`, la configuración y `herramientas/`, incluido el parche de cambios a
    `web/`.
  - **No cuentan:** la copia de `web/` ni el banco (`bolt-plan.md`: la copia no cuenta, los cambios sí).

**Consecuencias.**

- **Positivas:** cualquiera repite el conteo y obtiene lo mismo, porque la casilla trae el comando y el
  commit.
- **Negativas:** el conteo de líneas premia opciones con menos pruebas. Por eso es el tercer criterio, y
  NFR12 (80 % de cobertura) se exige antes.
- **Neutras:** con una sola candidata, los tres números se anotan pero no deciden.

**Alternativas.**

- *Contar cada producto del proveedor como servicio (Worker, Durable Object y Assets = 3):* castiga a
  Workers por detalles internos de un solo despliegue. Lo que pide `project.md` es «menos piezas,
  servicios y cambios de código» desde el punto de vista de quien despliega. Rechazada.
- *Contar líneas con un paquete (cloc, tokei):* exige aprobar un paquete para una cifra que `wc -l` da
  igual de bien. Rechazada (`project.md`: cada paquete nuevo requiere aprobación).

## ADR-C2: Cómo entran las opciones que no se construyen ni se miden

**Estado:** Accepted (2026-10-25); revisado el 2026-10-25 por FR12.2c.

**Contexto.** Cuatro de las cinco opciones no llegan a la prueba común:

- **Apps Script** no puede cumplir el contrato (C-01, `contract-design/reviews/review-01.md`): `doGet` y
  `doPost` no entregan cabeceras, así que no lee `X-Clave-Admin`.
- **Render con disco** es de pago: US$ 7 al mes + US$ 0,25 por GB (https://render.com/pricing). Su plan
  gratuito no tiene disco, se duerme a los 15 minutos y despierta en «about one minute»
  (https://render.com/docs/free).
- **Cloudflare Containers** solo existe en Workers Paid, US$ 5 al mes
  (https://developers.cloudflare.com/containers/pricing/), y su disco es efímero
  (https://developers.cloudflare.com/containers/platform-details/).
- **GitHub Pages** no se construye por decisión del humano: «lo referente solo a cloudflare» (FR12.2c).

FR12.2a, FR12.2c y la regla de Delivery Planning (Q2-A) piden que estas opciones entren en la tabla con su
motivo, no que desaparezcan.

**Decisión.** Las cuatro quedan en `COMPARACION.md` con todas sus casillas llenas:

- **Render y Cloudflare Containers:** con las columnas documentadas de U15 y U16 (URL y fecha 2026-10-25).
- **Apps Script:** «no pasa por contrato: C-01» en cada casilla, con el enlace a la revisión.
- **GitHub Pages:** «no se construye (FR12.2c)» en cada casilla medida. En «Piezas y servicios» se anota
  el mínimo documentado (≥ 2 servicios), sin desplegar.

Ninguna cuenta como candidata en ADR-C3. No se pide al humano aprobar un costo para Render ni para
Containers. Containers tampoco cumpliría NFR4 con el `Dockerfile` actual aunque se pagara. Render exige
tarjeta para un problema que Workers ya resuelve gratis (U1, ADR-W1).

**Consecuencias.**

- **Positivas:** la tabla muestra las cinco opciones lado a lado (FR12.4) y queda escrito por qué no se
  gastó dinero ni tiempo en ellas.
- **Negativas:** Render, la línea base de hoy, no se mide. Si algún día se quiere medir, hay que aprobar
  un monto y un tope y agregar unidades. Lo mismo vale para reabrir GitHub Pages.
- **Neutras:** `render.yaml` de la raíz sigue describiendo la versión local. Quitarlo o no es una
  pregunta de limpieza para el humano al aprobar ADR-C3.

**Alternativas.**

- *Pagar un día de Render (≈ US$ 0,24) para medirla:* rompe NFR6 (US$ 0) y FR12.2a sin ganar nada
  decisivo, porque no cumple NFR6 de todas formas. Rechazada; el humano puede reabrirla.
- *Construir GitHub Pages como respaldo:* contradice FR12.2c. Rechazada.
- *Borrar ahora las carpetas de las cuatro:* FR12.6 dice que se borran después de la aprobación del ADR
  final, en un commit propio. Rechazada.

## ADR-C3: Elección de la opción ganadora

**Estado:** Proposed (2026-10-25). Pasa a Accepted cuando el humano lo apruebe con la tabla cerrada (U6
terminada y las dos mediciones de U2 escritas, ADR-C5).

**Contexto.** Lo conocido al diseñar está en `functional-design/functional-spec.md` («Estado conocido»).
Cloudflare Workers pasó su corte delgado (U1) y es la única opción que se construye (FR12.2c). Las otras
cuatro no pasan o no se construyen (ADR-C2). «Pasa todo» exige doce «sí» con evidencia (BR17.2). FR12.2c
dice: «si Cloudflare pasa todo, es la elegida sin respaldo construido».

**Decisión (condicional; se completa con los JSON de U2).**

1. Si Workers pasa todo, **gana Cloudflare Workers**. No hay respaldo en la nube. La versión local
   (`2_Aplicacion_Reto/`, red local o túnel temporal) es el respaldo de aula, y la guía lo dice
   (sección 9 de `PUBLICAR_EN_INTERNET.md`).
2. Si Workers no pasa todo, no se elige. Se aplica OQ2: se pregunta al humano qué NFR se relaja o si se
   reabre otra opción (FR12.2c). Nunca se elige a ciegas.
3. Carpetas que se borran tras la aprobación (BR17.9): `despliegues/apps-script/`, `despliegues/render/`,
   `despliegues/cloudflare-containers/` y `despliegues/github-pages/`. Se conservan `cloudflare/`,
   `prueba_comun/`, `LEEME.md` y `COMPARACION.md`. La fila de cada opción borrada se queda en la tabla.

Code Generation de U17 llena aquí, con la tabla cerrada, los doce veredictos de Cloudflare, sus tres
números de FR12.6 y la fecha. El humano firma la aprobación en este mismo archivo.

**Consecuencias.**

- **Positivas:** la decisión no depende de gustos, porque sale de la tabla y de la regla escrita en
  FR12.2c.
- **Negativas:** si Cloudflare deja de servir (cuota, cambio de plan), no hay otra versión de la nube lista.
  El respaldo es el de hoy: red local o túnel temporal. Hay que avisarlo en la guía.
- **Neutras:** la elección se puede reabrir con una medición nueva (U17-R3).

**Alternativas.**

- *Elegir ya a Workers sin esperar la prueba común completa:* contradice FR12.5 («pasa todo» con la
  prueba común) y «la tabla nunca se llena a medias» (`unit-of-work.md`). Rechazada.
- *Construir un respaldo en la nube antes de elegir:* contradice FR12.2c y la parsimonia de
  `project.md`. Rechazada.

## ADR-C4: Forma de `PUBLICAR_EN_INTERNET.md` para la ganadora

**Estado:** Accepted (2026-10-25); revisado el 2026-10-25 para una sola sala.

**Contexto.** La guía de hoy describe Render con tarjeta y GitHub Desktop con repositorio privado, y dice
que el reloj y la clasificación viven en memoria. Las tres cosas cambiaron:

- Render no cumple NFR6.
- El repositorio es público por decisión del humano.
- El estado sale de SQLite (FR8.3).

Con la revisión, además, hay un solo docente con una sola clave, un solo panel, una lista de colegios con
«Arrancar reloj» y un tablero sin `?sala=` (FR11, ADR-009 a ADR-011). La guía la leen docentes y personas
del semillero que no programan (FR8.1, NFR7). `.claude/rules/markdown-docs.md` exige frases de
30 palabras o menos y explicar cada término técnico la primera vez.

**Decisión.** Se reemplaza entera con las diez secciones de `functional-design/functional-spec.md`
(«Forma de PUBLICAR_EN_INTERNET.md»):

- resumen y costo US$ 0, con la cuota y su URL;
- qué se necesita;
- crear el servicio con los pasos del `LEEME.md` de Cloudflare (también desde Windows, ADR-C6);
- entregar al docente el enlace y su clave;
- preparar el reto (código de sala, colegios);
- prueba de humo;
- el día del reto, con «Arrancar reloj» para el colegio que llega tarde;
- cierre con respaldo antes de borrar (NFR10.1): paquete, «Reiniciar» y borrar copias;
- volver atrás y qué hacer si aparece la página de error 1027;
- dónde viven los datos (corrige FR8.3) y ensayar gratis sin publicar.

La guía no lleva claves reales ni respuestas. Se comprueba con un conteo de palabras por frase y con la
lectura de alguien del semillero ajeno al diseño (FR8.1). Se escribe solo después de aprobar ADR-C3.

**Consecuencias.**

- **Positivas:** hay una sola guía, para una sola opción, en el lenguaje de quien la usa.
- **Negativas:** las guías de las opciones descartadas desaparecen con sus carpetas. Su memoria queda en
  `COMPARACION.md` y en los ADR de cada unidad.
- **Neutras:** `2_Aplicacion_Reto/LEEME.md` sigue cubriendo el uso en red local y el túnel; la guía solo
  remite a él.

**Alternativas.**

- *Mantener la guía de Render como anexo:* confunde al docente con una opción que no se usa y cuesta
  dinero. Rechazada.
- *Dejar los pasos técnicos solo en el `LEEME.md` de Cloudflare y que la guía remita a él:* obliga a quien
  no programa a leer un documento para desarrolladores. Rechazada: la guía copia los pasos con palabras
  simples y el `LEEME.md` los conserva para el semillero.

## ADR-C5: Cloudflare se mide dos veces y cada NFR sale de una medición fija

**Estado:** Accepted (2026-10-25).

**Contexto.** La prueba común no puede probar el vencimiento real contra la URL pública. En producción,
`duracion_min` tiene mínimo 10, y no hay ninguna ruta pública que mueva el reloj (D9, OQ3). Contra
`wrangler dev`, con `DURACION_MINIMA_MIN=1`, sí lo prueba. Pero `wrangler dev` corre en la computadora
de quien prueba, así que sus latencias, su arranque en frío y su consumo no dicen nada del servicio real.
Las dos corridas escribirían el mismo nombre de archivo (`cloudflare_<fecha>.json`, C3).

**Decisión.**

- Hay dos corridas, con el mismo esquema C3 y `opcion: cloudflare`:
  - **URL pública:** `cloudflare_<AAAA-MM-DD>.json`, con `--vencimiento omitir`, `--frio` y
    `--reinicio manual` (un `wrangler deploy` a mitad de la prueba es el reinicio de NFR4);
  - **`wrangler dev`:** `cloudflare-dev_<AAAA-MM-DD>.json` (con `--salida`), con `--vencimiento esperar`,
    `--duracion-min 2` y `--reinicio comando`.
- De qué corrida sale cada NFR:
  - **solo de la URL pública:** NFR2, NFR3, NFR5 y NFR6;
  - **de la que más prueba:** NFR1, NFR8, NFR9 y NFR11 salen de las comprobaciones de la URL pública, y
    cada id que esa corrida dejó en `nfr.no_aplica` tiene que estar en `pasa: true` en la de
    `wrangler dev`;
  - **de las dos:** NFR4, con `sobrevive_reinicio` igual a `true` en las dos.
- Si alguna de las dos falta o está a medias, la casilla dice «sin medir» y Cloudflare no pasa (BR17.1).

**Consecuencias.**

- **Positivas:** ninguna comprobación queda sin hacer en ninguna parte, y las cifras de rapidez y costo
  son las del servicio real.
- **Negativas:** hay dos archivos que mantener al día; U17 tiene que cruzar los `no_aplica`.
- **Neutras:** el esquema C3 no cambia; el nombre `cloudflare-dev_…` sale de `--salida`.

**Alternativas.**

- *Una sola corrida contra la URL pública, esperando 10 minutos reales:* deja en el servicio real un reto
  de prueba largo, que consume cuota y bloquea el panel. Además no prueba los relojes con 1 minuto como
  pidió D9. Rechazada.
- *Un modo de prueba en producción que acorte el reloj:* abre una puerta pública para mover el reloj,
  justo lo que D9 y OQ3 prohíben. Rechazada.

## ADR-C6: Los pasos de Cloudflare también funcionan desde Windows con Git Bash

**Estado:** Accepted (2026-10-25).

**Contexto.** El `LEEME.md` de Cloudflare usa `bash` para `herramientas/copiar.sh` y
`herramientas/verificar.sh`, `python3` para la prueba común y `npx wrangler` para publicar. Varias
personas del semillero usan Windows (los lanzadores `.bat` existen por eso). Git para Windows trae Git
Bash, que corre esos scripts. Pero hay tres detalles:

- con `core.autocrlf` encendido, Git puede guardar los `.sh` con fin de línea CRLF y `bash` falla;
- el lanzador de Python en Windows suele llamarse `py` y no `python3`;
- `.gitattributes` hoy solo fija `*.bat` (CRLF) y `*.command` (LF).

**Decisión.**

- **Fin de línea:** Code Generation de U17 agrega a `.gitattributes` `*.sh text eol=lf` y
  `*.patch text eol=lf`. Sin eso, `copiar.sh` y `cambios_web.patch` se rompen en Windows.
- **Una sección del `LEEME.md` de Cloudflare para Windows:**
  - instalar Git para Windows (trae Git Bash), Node 24 y Python 3.12;
  - abrir Git Bash en la carpeta del repositorio;
  - usar `py -3` donde dice `python3`;
  - los comandos `npx wrangler@4.148.0 …` son los mismos.
- **Si Git Bash no muestra la pregunta de `wrangler secret put CLAVE_DOCENTE`:** el mismo comando se
  corre en PowerShell, desde `despliegues/cloudflare/`.
- **Paso único para quien venga del corte:** `npx wrangler@4.148.0 secret delete CLAVE_SEMILLERO`, porque
  la versión de una sala ya no la usa.
- **Volver atrás:** solo hasta la primera versión publicada de una sala (U5). Un `rollback` a la versión
  del corte (U1) dejaría código de varias salas sobre la base ya migrada a la versión 2 (ADR-W19 de U5).

**Consecuencias.**

- **Positivas:** los mismos comandos, copiados del `LEEME.md`, sirven en Linux, Mac y Windows.
- **Negativas:** quien use Windows instala Git para Windows, aunque ya use GitHub Desktop.
- **Neutras:** los lanzadores `.bat` de `2_Aplicacion_Reto/` no cambian.

**Alternativas.**

- *Escribir `copiar.ps1` y `verificar.ps1` para PowerShell:* duplica la lógica en dos lenguajes y hay que
  mantener las dos copias iguales. Rechazada.
- *Pedir WSL:* es una instalación más pesada y más difícil de explicar a quien no programa. Rechazada.

## Referencias

- `requirements.md` (FR8, FR12.2 a FR12.6, NFR1 a NFR12) y `project.md` («Corrections»).
- `contract-summary.md` (C3) y `contract-design-questions.md` (D8 y D9: esquema de mediciones y
  vencimiento con `DURACION_MINIMA_MIN`).
- `contract-design/reviews/review-01.md` (C-01: Apps Script no entrega cabeceras).
- `u15-render-documentacion/functional-design/functional-spec.md` y
  `u16-cloudflare-containers-documentacion/functional-design/functional-spec.md` («Cifras oficiales»).
- `u1-cloudflare-corte/decisions.md` (ADR-W1 a ADR-W5) y `u5-cloudflare-salas/decisions.md` (ADR-W19:
  migración a una sala; ADR-W20: respuesta ante la cuota).
- `u2-prueba-comun/functional-design/` (las dos corridas y `nfr.no_aplica`).
- `bolt-plan.md` (B5, B6, B13) y `unit-of-work.md` («U15 y U16», «U17»).
