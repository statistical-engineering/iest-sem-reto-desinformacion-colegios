# ADR de la comparación final (U17)

Decisiones de `u17-comparacion`: cómo se cuenta, cómo se cierra cada opción, quién gana y cómo se escribe
la guía. Salen de FR12.4 a FR12.6, FR8 y de `project.md` («Corrections», parsimonia). Decisiones del
asistente con la potestad que dio el humano (2026-10-25); el ADR-C3 queda «Proposed» hasta que el humano
lo apruebe con la tabla cerrada, como exige FR12.6.

## ADR-C1: Cómo se cuentan servicios externos, piezas propias y líneas de código

**Estado:** Accepted (2026-10-25).

**Contexto.** FR12.6 ordena las opciones que pasan todo por «menos servicios externos», «menos piezas
propias que desplegar» y «menos líneas de código», pero no dice cómo contar. Sin una regla fija, dos
personas contarían distinto (¿un Durable Object es un servicio aparte? ¿cuenta la copia de `web/`?).

**Decisión.**
- **Servicio externo:** cada cuenta o producto que la persona del semillero crea o activa por separado y
  que tiene su propio panel o cuota. Lo que se despliega junto, con un solo comando y en la misma cuenta,
  cuenta como 1. Workers (Worker + Durable Object + recursos estáticos con un `wrangler deploy`) = 1.
  GitHub Pages = Pages + el servicio de la API (+ 1 si el almacén de datos es otro proveedor) ≥ 2. Apps
  Script + Google Sheets = 2. Render = 1. Cloudflare Containers = 1.
- **Pieza propia:** cada fila de la tabla «Piezas» de `infrastructure-specification.md` de la opción que
  alguien configura, sin contar el enlace fijo que asigna el proveedor. Workers = 4 (Worker, recursos
  estáticos, Durable Object, secreto `CLAVE_SEMILLERO`).
- **Líneas de código:** `git ls-files despliegues/<opcion> | grep -v -E
  "^despliegues/<opcion>/(web/|src/banco\.json|src/banco_huella\.json|LEEME\.md|\.gitignore)$" | xargs wc
  -l | tail -1`, corrido sobre un commit que se anota. Cuentan `src/`, `pruebas/`, la configuración y
  `herramientas/`, incluido el parche de cambios a `web/`; no cuenta la copia de `web/` ni el banco
  (`bolt-plan.md`: la copia no cuenta, los cambios sí).

**Consecuencias.** Positivas: cualquiera repite el conteo y obtiene lo mismo; la casilla trae el comando
y el commit. Negativas: el conteo de líneas premia opciones con menos pruebas, por eso es el tercer
criterio y NFR12 (80 % de cobertura) se exige antes. Neutras: si una opción comparte proveedor con
otra (Workers y Containers), eso no las acerca en el conteo; se cuenta por opción.

**Alternativas.**
- *Contar cada producto del proveedor como servicio (Worker, Durable Object, Assets = 3):* castiga a
  Workers por detalles internos de un solo despliegue, cuando lo que pide `project.md` es «menos piezas,
  servicios y cambios de código» desde el punto de vista de quien despliega. Rechazada.
- *Contar líneas con un paquete (cloc, tokei):* exige aprobar un paquete para una cifra que `wc -l` da
  igual de bien. Rechazada (`project.md`: cada paquete nuevo requiere aprobación).

## ADR-C2: Cómo entran las opciones que no se despliegan ni se miden

**Estado:** Accepted (2026-10-25).

**Contexto.** Tres de las cinco opciones no llegan a la prueba común: Apps Script no puede cumplir el
contrato (C-01, `contract-design/reviews/review-01.md`: `doGet`/`doPost` no entregan cabeceras, así que
no lee `X-Clave-Admin`); Render con disco es de pago (US$ 7 al mes + US$ 0,25 por GB,
https://render.com/pricing) y su plan gratuito no tiene disco, duerme a los 15 minutos y despierta en
«about one minute» (https://render.com/docs/free); Cloudflare Containers solo existe en Workers Paid
(US$ 5 al mes, https://developers.cloudflare.com/containers/pricing/) y su disco es efímero
(https://developers.cloudflare.com/containers/platform-details/). FR12.2a y la regla de Delivery
Planning (Q2-A) piden que entren en la tabla como «no pasa», con el motivo, no que desaparezcan.

**Decisión.** Las tres quedan en `COMPARACION.md` con todas sus casillas llenas: Render y Cloudflare
Containers con las columnas documentadas de U15 y U16 (URL y fecha 2026-10-25); Apps Script con «no pasa
por contrato: C-01» en cada casilla y el enlace a la revisión. Ninguna cuenta como candidata en ADR-C3.
No se pide al humano aprobar un costo para Render ni para Containers, porque Containers tampoco
cumpliría NFR4 con el `Dockerfile` actual aunque se pagara, y Render exige tarjeta para un problema que
Workers ya resuelve gratis (U1, ADR-W1).

**Consecuencias.** Positivas: la tabla muestra las cinco opciones lado a lado (FR12.4) y queda escrito
por qué no se gastó dinero. Negativas: Render, la línea base de hoy, no se mide; si algún día se quiere
medir, hay que aprobar un monto y un tope y agregar unidades. Neutras: `render.yaml` de la raíz sigue
describiendo la versión local; quitarlo o no es una pregunta de limpieza para el humano al aprobar
ADR-C3.

**Alternativas.**
- *Pagar un día de Render (≈ US$ 0,24) para medirla:* rompe NFR6 (US$ 0) y FR12.2a sin ganar nada
  decisivo, porque no cumple NFR6 de todas formas. Rechazada; el humano puede reabrirla.
- *Borrar las carpetas de las tres ahora:* FR12.6 dice que se borran después de la aprobación del ADR
  final, en un commit propio. Rechazada.

## ADR-C3: Elección de la opción ganadora y de la de respaldo

**Estado:** Proposed (2026-10-25). Pasa a Accepted cuando el humano lo apruebe con la tabla cerrada
(U2, U6 y U14 terminadas o saltadas).

**Contexto.** Lo conocido al diseñar (`../functional-design/functional-spec.md`, «Estado conocido»):
Cloudflare Workers pasó su corte delgado (U1) y es la candidata principal; GitHub Pages depende de U11 a
U14 y, por definición, tiene al menos 2 servicios externos (pantallas en Pages, API en otro servicio);
Render, Cloudflare Containers y Apps Script no pasan (ADR-C2). «Pasa todo» exige doce «sí» con evidencia
(BR17.2); el orden es el de FR12.6 (BR17.7).

**Decisión (condicional, se completa con los JSON de U2).**
1. Si Workers pasa todo, **gana Cloudflare Workers** por el criterio 1 de FR12.6: 1 servicio externo
   frente a 2 o más de GitHub Pages. No hace falta mirar piezas ni líneas. **Respaldo:** GitHub Pages si
   pasa todo; si no, no hay respaldo en la nube y la versión local sigue siendo el respaldo de aula
   (`despliegues/LEEME.md`).
2. Si Workers no pasa todo y GitHub Pages sí, **gana GitHub Pages**, sin respaldo en la nube.
3. Si ninguna pasa todo, no se elige: se aplica OQ2 y se pregunta al humano qué NFR se relaja.
4. Carpetas que se borran tras la aprobación (BR17.9): `despliegues/apps-script/`, `despliegues/render/`,
   `despliegues/cloudflare-containers/` y la de la perdedora si no es respaldo. Se conservan la ganadora,
   el respaldo, `prueba_comun/`, `LEEME.md` y `COMPARACION.md`.

Code Generation de U17 llena aquí, con la tabla cerrada: la fila elegida, los tres números de FR12.6 de
cada candidata, el criterio decisivo y la fecha; el humano firma la aprobación en este mismo archivo.

**Consecuencias.** Positivas: la decisión no depende de gustos; cualquiera puede recorrer la tabla y
llegar al mismo resultado. Negativas: GitHub Pages solo puede ganar si Workers falla, lo que puede
desanimar a quien la construye; por eso se dice desde ahora y se mantiene su valor como respaldo.
Neutras: la elección se puede reabrir con una medición nueva (U17-R3).

**Alternativas.**
- *Elegir ya a Workers sin esperar la prueba común completa:* contradice FR12.5 («pasa todo» con la
  prueba común) y «la tabla nunca se llena a medias» (`unit-of-work.md`). Rechazada.
- *Ponderar criterios con puntajes:* `project.md` pide el orden estricto (parsimonia) y Delivery Planning
  rechazó puntajes formales (Q1-A). Rechazada.

## ADR-C4: Forma de `PUBLICAR_EN_INTERNET.md` para la ganadora

**Estado:** Accepted (2026-10-25).

**Contexto.** La guía de hoy describe Render con tarjeta y GitHub Desktop con repositorio privado, y dice
que el reloj y la clasificación viven en memoria. Las tres cosas cambiaron: Render no cumple NFR6, el
repositorio es público por decisión del humano, y hoy el estado sale de SQLite (FR8.3). La leen docentes
y personas del semillero que no programan (FR8.1, NFR7). `.claude/rules/markdown-docs.md` exige frases de
30 palabras o menos y cada término técnico explicado la primera vez.

**Decisión.** Se reemplaza entera con las nueve secciones de `../functional-design/functional-spec.md`
(«Forma de PUBLICAR_EN_INTERNET.md»): resumen y costo US$ 0 con la cuota y su URL; qué se necesita;
crear el servicio con los pasos del `LEEME.md` de la ganadora, numerados y con comandos listos para
copiar; crear una sala y entregar la clave; prueba de humo; el día del reto; cierre con respaldo antes de
borrar (NFR10.1); volver atrás; dónde viven los datos (corrige FR8.3); ensayar gratis sin publicar. Nada
de claves reales ni respuestas. Se comprueba con un conteo de palabras por frase y con la lectura de
alguien del semillero ajeno al diseño (FR8.1). Se escribe solo después de aprobar ADR-C3.

**Consecuencias.** Positivas: una sola guía, para una sola opción, en el lenguaje de quien la usa.
Negativas: las guías de las opciones perdedoras desaparecen con sus carpetas; su memoria queda en
`COMPARACION.md` y en los ADR de cada unidad. Neutras: `2_Aplicacion_Reto/LEEME.md` sigue cubriendo el
uso en red local y el túnel; la guía solo remite a él.

**Alternativas.**
- *Mantener la guía de Render como anexo:* confunde al docente con una opción que no se usa y cuesta
  dinero. Rechazada.
- *Escribir la guía para las dos (ganadora y respaldo):* duplica pasos y claves que entregar; el respaldo
  conserva su propio `LEEME.md` para el semillero. Rechazada.

## Referencias

- `requirements.md` (FR8, FR12.2 a FR12.6, NFR1 a NFR12) y `project.md` («Corrections»).
- `contract-summary.md` (C3) y `contract-design/reviews/review-01.md` (C-01).
- `u15-render-documentacion/functional-design/functional-spec.md` y
  `u16-cloudflare-containers-documentacion/functional-design/functional-spec.md` («Cifras oficiales»).
- `u1-cloudflare-corte/decisions.md` (ADR-W1 a ADR-W5) y su `infrastructure-design/`.
- `bolt-plan.md` (B5, B6, B13) y `unit-of-work.md` («U15 y U16», «U17»).
