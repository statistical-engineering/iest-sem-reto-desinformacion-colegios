# Especificación funcional — U17 `u17-comparacion`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Cambia lo siguiente:
>
> - **Mediciones:** solo se mide Cloudflare, con dos corridas, la de la URL pública y la de
>   `wrangler dev` (ADR-C5).
> - **Opciones sin medir:** GitHub Pages entra como «no se construye» (FR12.2c).
> - **Elección:** gana Cloudflare si pasa todo, sin respaldo construido (ADR-C3).
> - **Flujos nuevos:** F9 (estimación de consumo) y F10 (`LEEME.md` de Cloudflare con Windows y Git
>   Bash).
> - **Guía:** `PUBLICAR_EN_INTERNET.md` queda para un docente, una clave y una sala.
>
> Los flujos F1 a F8 conservan su número.

Qué hace la comparación final, paso a paso (`unit-of-work.md`, «U17»; `bolt-plan.md`, B13). Los datos
están en `entities.md`, las reglas en `rules.md` y las decisiones en `../decisions.md` (ADR-C1 a ADR-C6).
Esta especificación no escribe el contenido final de `despliegues/COMPARACION.md`, de
`PUBLICAR_EN_INTERNET.md` ni del `LEEME.md` de Cloudflare. Eso le toca a Code Generation de U17, cuando ya
existan las mediciones de U2.

## Qué demuestra la unidad

La elección del hosting sale de la prueba común y de una regla escrita, no de una preferencia:

- la tabla muestra las cinco opciones lado a lado;
- el ADR final dice si Cloudflare queda elegida y por qué;
- la guía deja a una persona del semillero desplegarla sin escribir código, también desde Windows.

## Entradas

| Entrada | De dónde | Contrato |
|---|---|---|
| Medición de la URL pública de Cloudflare | `despliegues/prueba_comun/mediciones/cloudflare_<AAAA-MM-DD>.json` (U2) | C3, ADR-C5 |
| Medición de Cloudflare en `wrangler dev` | `despliegues/prueba_comun/mediciones/cloudflare-dev_<AAAA-MM-DD>.json` (U2) | C3, ADR-C5 |
| Columna Render | `u15-render-documentacion/functional-design/functional-spec.md`, «Columna Render, fila por fila» | BR17.3 |
| Columna Cloudflare Containers | `u16-cloudflare-containers-documentacion/functional-design/functional-spec.md`, «Columna Cloudflare Containers, fila por fila» | BR17.3 |
| Apps Script «no pasa por contrato» | `inception/contract-design/reviews/review-01.md`, hallazgo C-01 | BR17.3 |
| GitHub Pages «no se construye» | `requirements.md`, FR12.2c | BR17.3 |
| Piezas y pasos de Cloudflare | `infrastructure-design/infrastructure-specification.md` de U1 a U6 y `despliegues/cloudflare/LEEME.md` | BR17.5 |
| Refrescos de las pantallas | `despliegues/cloudflare/web/js/*.js` y `web/tablero.html` | BR17.12 |
| Evidencia de NFR7, NFR10.1 y NFR12 | Anotaciones del punto de control de Cloudflare: quién desplegó con el LEEME, cierre probado y cobertura | BR17.2 |

## Flujos

### F1. Comprobar que la tabla se puede cerrar (BR17.8)

1. U6 terminó: Cloudflare está completa y sus tres pantallas funcionan (criterio del humano del
   2026-10-26).
2. Existen las dos mediciones de Cloudflare, con `todo_bien: true`.
3. Las otras cuatro opciones ya tienen su motivo: U15 y U16 entregaron sus columnas, Apps Script está
   saltada por C-01 y GitHub Pages por FR12.2c.
4. Si falta algo, U17 espera: la tabla nunca se llena a medias.

### F2. Leer las mediciones (BR17.1, ADR-C5)

1. De cada corrida se toma el JSON con la fecha mayor y se rechaza un `version_esquema` distinto de 1.
2. De `publica.nfr` salen las filas de p95 al responder, p95 del tablero, arranque en frío y peticiones.
   De las dos sale el reinicio.
3. De `comprobaciones` salen «pasa la prueba común» y la evidencia de NFR1 (parte `relojes`, en dev),
   NFR8 (`fugas`), NFR9 (`claves`) y NFR11 (`mismas_fracciones_que_local`, `mismos_csv_que_local`), por
   el `id` de cada comprobación.
4. Cada id de `publica.nfr.no_aplica` se busca en dev con `pasa: true`. Si falta, la casilla dice «sin
   medir: <id>».
5. Cada casilla trae el valor y el archivo, por ejemplo «812 ms (cloudflare_2026-11-02.json)».

### F3. Contar servicios, piezas y líneas (BR17.4 a BR17.6)

1. Servicios externos: por opción, la lista de cuentas o productos aparte y su número.
2. Piezas propias: las filas de la tabla «Piezas» de su `infrastructure-specification.md`, sin el
   enlace. Workers suma 4, con el secreto `CLAVE_DOCENTE`.
3. Líneas de código: el comando de BR17.6, corrido sobre el commit que se anota en la casilla.

### F4. Dar el veredicto por opción (BR17.2, BR17.3)

1. Cloudflare recibe un «sí», «no» o «sin evidencia» por cada NFR de FR12.5, con su evidencia.
2. Render, Cloudflare Containers, Apps Script y GitHub Pages quedan en «no pasa» o «no se construye», con
   los motivos de la tabla «Estado conocido».
3. `pasa_todo` solo con doce «sí».

### F5. Elegir (BR17.7)

1. Si Cloudflare pasa todo, gana con el criterio «única que pasa» (FR12.2c). El respaldo es la versión
   local.
2. Si no pasa, se aplica OQ2: se pregunta al humano qué se relaja o qué opción se reabre. No se elige a
   ciegas.

### F6. Escribir el ADR final (`../decisions.md`, ADR-C3)

1. **Contexto:** la tabla cerrada. **Decisión:** la ganadora y el respaldo de aula. **Alternativas:**
   cada opción que no ganó, con su motivo.
2. El estado es «Proposed» hasta que el humano aprueba; después pasa a «Accepted» con la fecha.

### F7. Reescribir `PUBLICAR_EN_INTERNET.md` (BR17.10)

Se usa la forma de la sección «Forma de `PUBLICAR_EN_INTERNET.md`». La guía se reemplaza entera: la de
hoy es de Render y de GitHub Desktop con repositorio privado, para varias salas. Esas cosas cambiaron:

- Render no cumple NFR6;
- el repositorio es público;
- hay una sola sala (FR11).

### F8. Borrar las carpetas descartadas (BR17.9)

Solo después de la aprobación del ADR, en un commit propio. Se borran `apps-script/`, `render/`,
`cloudflare-containers/` y `github-pages/`. Se conservan `cloudflare/`, `prueba_comun/`, `LEEME.md` y
`COMPARACION.md`.

### F9. Estimar el consumo de un reto real (BR17.12)

1. Se leen de la copia de `web/` los intervalos de refresco: el tablero cada 2 s, el panel cada 3 s y el
   que diga `estudiante.js`.
2. Se suman las peticiones de 90 minutos con un tablero, un panel y 40 estudiantes abiertos, más
   40 × preguntas × 2 y las inscripciones.
3. Se divide por la cuota diaria de la página oficial (hoy, 100.000 peticiones) y se anota el porcentaje.
   NFR6 pide ≤ 50 %.
4. En la misma casilla van la fórmula, cada número, la URL y la fecha de consulta.

### F10. Dejar el `LEEME.md` de Cloudflare para una sala y para Windows (BR17.13, ADR-C6)

1. Se cambia `CLAVE_SEMILLERO` por `CLAVE_DOCENTE` en todo el archivo. Se agrega el paso único
   `npx wrangler@4.148.0 secret delete CLAVE_SEMILLERO` para quien venga del corte.
2. «Probar en tu computador» queda así:
   - `.dev.vars` con `CLAVE_DOCENTE=UNACLAVEDEPRUEBA` y `DURACION_MINIMA_MIN=1`, más la advertencia de
     que esa línea nunca va al despliegue (D9);
   - las dos corridas de ADR-C5, con sus comandos completos.
3. «Cómo se usa el día del reto» queda para un docente:
   - fijar el código de sala;
   - pegar la lista de colegios;
   - abrir el reto;
   - «Arrancar reloj» del colegio que llega tarde;
   - el tablero en `/tablero`, sin `?sala=`.
4. «Volver a la versión anterior» advierte que no se vuelve a una versión anterior a la de una sala
   (ADR-W19 de U5).
5. Sección nueva «Desde Windows»:
   - instalar Git para Windows (trae Git Bash), Node 24 y Python 3.12;
   - abrir Git Bash en la carpeta del repositorio;
   - usar `py -3` donde dice `python3`;
   - si Git Bash no muestra la pregunta de `wrangler secret put`, correr ese comando en PowerShell.
6. `.gitattributes` gana `*.sh text eol=lf` y `*.patch text eol=lf`.
7. Se comprueba siguiendo el `LEEME.md` en un computador con Windows: `copiar.sh` y `verificar.sh` corren
   sin error de fin de línea.

## Estado conocido al diseñar (2026-10-25)

Lo que ya se sabe antes de las mediciones. Code Generation lo confirma o lo corrige con los JSON.

| Opción | Origen | Estado | Motivo |
|---|---|---|---|
| Cloudflare Workers | medida (dos corridas) | única candidata: pasó su corte (U1) | faltan U4 a U6 y la prueba común completa de U2 |
| GitHub Pages | no se construye | no se construye | FR12.2c: «lo referente solo a cloudflare»; además tendría al menos 2 servicios externos (pantallas en Pages, API en otro servicio) |
| Render | documentada (U15) | no pasa | NFR6: el plan con disco cuesta US$ 7 al mes + US$ 0,25 por GB (https://render.com/pricing). El gratuito no tiene disco, se duerme a los 15 min y despierta en «about one minute» (https://render.com/docs/free), así que falla NFR4 y NFR5 |
| Cloudflare Containers | documentada (U16) | no pasa | NFR6: solo existe en Workers Paid, a US$ 5 al mes (https://developers.cloudflare.com/containers/pricing/). NFR4: el disco es efímero con el `Dockerfile` actual (https://developers.cloudflare.com/containers/platform-details/) |
| Apps Script | no pasa por contrato | no pasa | C-01: `doGet` y `doPost` no entregan cabeceras, así que no lee `X-Clave-Admin` (NFR9); tampoco fija códigos de estado ni `Cache-Control` (`review-01.md`) |

Consecuencia (ADR-C3):

- Si Workers pasa la prueba común completa en las dos corridas, gana sin respaldo construido. La versión
  local sigue siendo el respaldo de aula (`despliegues/LEEME.md`).
- Si no pasa, se aplica OQ2.

## Forma de `COMPARACION.md`

Se conserva la tabla de hoy (11 filas y 5 columnas). La columna GitHub Pages pasa a «no se construye
(FR12.2c)». Debajo se agregan cuatro bloques:

1. **Veredicto por NFR:** una tabla con las doce filas de FR12.5 y una columna por opción («sí», «no»,
   «sin evidencia», «no se despliega», «no se construye»), con la evidencia entre paréntesis.
2. **Qué salió de cada corrida:** las dos mediciones de Cloudflare, con su fecha y su `vencimiento`.
   Cada id de `no_aplica` de la corrida pública aparece con el archivo donde sí pasó (ADR-C5).
3. **Consumo de un reto real:** la estimación de F9 frente a la cuota diaria, con la fórmula y la URL.
4. **Resultado:** ganadora, respaldo de aula, enlace al ADR y fecha de aprobación; las opciones que no se
   construyeron, con su motivo.

Al pie va: «Mediciones: archivos de `prueba_comun/mediciones/`; documentación consultada el 2026-10-25
(U15 y U16) y el <fecha> (cuota de Cloudflare)».

## Forma de `PUBLICAR_EN_INTERNET.md`

La leen docentes y personas del semillero que no programan. Reglas de escritura:

- frases de 30 palabras o menos;
- cada término técnico explicado en palabras simples la primera vez («servidor: el computador de la
  empresa que atiende el enlace»);
- números en formato de Colombia;
- comillas «…» para botones y textos;
- sin claves reales ni respuestas.

Secciones, en este orden:

| # | Sección | Qué lleva | Requisito |
|---|---|---|---|
| 0 | Título y resumen | Qué se obtiene: un enlace fijo que funciona desde cualquier red, sin depender del computador del docente. Costo US$ 0, con la cuota y su URL | FR5.1, NFR6 |
| 1 | Qué necesitas | Una cuenta gratuita de Cloudflare; el repositorio (público); Node 24, Python 3.12 y, en Windows, Git para Windows con Git Bash; la clave docente, de 12 caracteres o más, guardada en el lugar privado del semillero | NFR9, NFR10, ADR-C6 |
| 2 | Crear el servicio (persona del semillero) | Los pasos del `LEEME.md` de Cloudflare, numerados y con comandos listos para copiar: entrar con `wrangler login`, guardar el secreto `CLAVE_DOCENTE`, publicar con `wrangler deploy`. Nada se escribe a mano salvo la clave. Un recuadro «Desde Windows» | FR8.1, NFR7, ADR-C6 |
| 3 | Entregar el enlace y la clave al docente | La persona del semillero le da al docente el enlace y la clave docente por un canal privado. Hay una sola clave y un solo panel | FR11.5, ADR-010 |
| 4 | Preparar el reto (docente) | En el panel: fijar el código de sala, el nombre del evento y la duración, y pegar la lista de colegios (un nombre por línea). Qué significa «Ese colegio ya existe.» | FR10.3, FR11.1, ADR-009 |
| 5 | Prueba de humo antes del reto | Abrir el enlace con datos móviles; `…/api/publico` responde; hacer una inscripción de prueba y luego «Reiniciar» (escribir BORRAR). Abrir el enlace unos minutos antes, por si el servicio estaba dormido | FR8.2, NFR5 |
| 6 | El día del reto (docente) | Abrir el panel con la clave y abrir el reto: arrancan solos los colegios que ya tienen equipos. Para un colegio que llega tarde, agregarlo si falta y pulsar «Arrancar reloj» (pide confirmar dos veces). Proyectar el tablero en `…/tablero`. No cambiar nada con un reto en curso | NFR7, FR11.5, ADR-011, `project.md` («Mandated») |
| 7 | Después del reto: cerrar | Primero descargar el paquete (`.zip`) y los CSV al lugar privado del semillero, y comprobar que abren y tienen una fila por participante. Solo entonces «Reiniciar» (escribir BORRAR) y, en la tarjeta «Copias», borrar cada copia después de guardarla. Al final, el panel no muestra participantes ni copias. Nada de eso va al repositorio | FR8.2, FR9.4, NFR10.1, D7 |
| 8 | Si algo falla | Volver a la versión anterior con `wrangler rollback`, en palabras simples: los datos no se pierden y no se vuelve a una versión anterior a la de una sala. Si aparece la página de error 1027 de Cloudflare, se acabó la cuota del día: vuelve a la medianoche UTC (las 19:00 en Colombia); mientras tanto, el reto sigue en red local o con el túnel temporal | FR8.2, NFR6, BR17.12 |
| 9 | Dónde viven los datos | Corrige la frase de hoy: el reloj de cada colegio y la clasificación no viven solo en memoria; salen de la base de datos del servicio y sobreviven a un reinicio | FR8.3, NFR4 |
| 10 | Ensayar gratis sin publicar | Misma red wifi (`INICIAR_RETO`) o enlace temporal (`INICIAR_RETO_INTERNET`, en Windows y Mac). Es también el respaldo de aula si la nube falla | `2_Aplicacion_Reto/LEEME.md`, ADR-C3 |

Lo que desaparece de la guía de hoy:

- la «Parte 1» de GitHub Desktop con repositorio privado: el repositorio es público por decisión del
  humano, y lo que no se sube son claves ni datos;
- la «Parte 2» de Render y el costo de US$ 7;
- la nota de «solo Mac» del túnel (`CLAUDE.md`, «Gotchas»);
- cualquier mención a crear salas, a la clave del semillero o a `?sala=`.

Cómo se comprueba BR17.10 antes del push:

- un conteo de palabras por frase sobre el archivo (por ejemplo, `python3 -c` con `re.split` por `.`,
  `?` y `!`) que no deje ninguna frase con más de 30 palabras;
- la lectura de alguien del semillero que no participó en el diseño (FR8.1).

## Fuera de la unidad

- No mide nada: las mediciones son de U2.
- No construye ninguna opción nueva. Si el humano reabre una o aprueba un costo, se agregan unidades.
- No cambia `2_Aplicacion_Reto/` (FR12.1).
- No cambia el código de Cloudflare. Solo toca su `LEEME.md` y `.gitattributes` (ADR-C6).
