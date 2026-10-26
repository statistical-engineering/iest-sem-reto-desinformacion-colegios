# Especificación funcional — U17 `u17-comparacion`

Qué hace la comparación final, paso a paso (`unit-of-work.md`, «U17»; `bolt-plan.md`, B13). Los datos
están en `entities.md`, las reglas en `rules.md` y las decisiones en `../decisions.md` (ADR-C1 a ADR-C4).
Esta especificación no escribe el contenido final de `despliegues/COMPARACION.md` ni de
`PUBLICAR_EN_INTERNET.md`: eso es Code Generation de U17, cuando ya existan las mediciones de U2.

## Qué demuestra la unidad

Que la elección del hosting sale de la misma prueba para todas las opciones y de un orden fijo, no de una
preferencia: la tabla muestra las cinco opciones lado a lado, el ADR final dice quién gana y por qué, y la
guía deja a una persona del semillero desplegar la ganadora sin escribir código.

## Entradas

| Entrada | De dónde | Contrato |
|---|---|---|
| Mediciones de Cloudflare Workers y de GitHub Pages | `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` (U2) | C3 |
| Columna Render | `u15-render-documentacion/functional-design/functional-spec.md`, «Columna Render, fila por fila» | BR17.3 |
| Columna Cloudflare Containers | `u16-cloudflare-containers-documentacion/functional-design/functional-spec.md`, «Columna Cloudflare Containers, fila por fila» | BR17.3 |
| Apps Script «no pasa por contrato» | `inception/contract-design/reviews/review-01.md`, hallazgo C-01 | BR17.3 |
| Piezas y pasos de cada opción desplegada | `infrastructure-design/infrastructure-specification.md` y `despliegues/<opcion>/LEEME.md` | BR17.5 |
| Evidencia de NFR7, NFR10.1 y NFR12 | Anotaciones del punto de control de cada opción (quién desplegó con el LEEME, cierre probado, cobertura) | BR17.2 |

## Flujos

### F1. Comprobar que la tabla se puede cerrar (BR17.8)

1. U6 terminó (Workers completa) y existe `mediciones/cloudflare_<fecha>.json` con `todo_bien: true`.
2. U14 terminó (GitHub Pages completa) con su JSON, **o** el humano aprobó saltar U11 a U14; en ese caso
   su columna dice «saltada» con el motivo.
3. Apps Script ya está saltada por C-01 (`bolt-plan.md`). U15 y U16 entregaron sus columnas.
4. Si falta algo, U17 espera: la tabla nunca se llena a medias.

### F2. Leer las mediciones (BR17.1)

1. Por opción medida, tomar el JSON con la fecha mayor; rechazar `version_esquema` distinto de 1.
2. De `nfr` salen las filas p95 al responder, p95 del tablero, reinicio, arranque en frío y peticiones.
3. De `comprobaciones` salen «pasa la prueba común» (`todo_bien`) y las evidencias de NFR1, NFR8, NFR9 y
   NFR11 por el `id` de cada comprobación.
4. Cada casilla trae el valor y el nombre del archivo: «812 ms (cloudflare_2026-11-02.json)».

### F3. Contar servicios, piezas y líneas (BR17.4 a BR17.6)

1. Servicios externos: por opción, la lista de cuentas o productos aparte y su número.
2. Piezas propias: las filas de la tabla «Piezas» de su `infrastructure-specification.md`, sin el enlace.
3. Líneas de código: el comando de BR17.6, corrido sobre el commit que se anota en la casilla.

### F4. Dar el veredicto por opción (BR17.2, BR17.3)

1. Para cada opción desplegada, un «sí / no / sin evidencia» por NFR de FR12.5, con su evidencia.
2. Render, Cloudflare Containers y Apps Script quedan «no pasa» con los motivos de sus unidades o del
   hallazgo C-01 (tabla «Estado conocido» más abajo).
3. `pasa_todo` solo con doce «sí».

### F5. Elegir (BR17.7)

1. Ordenar las que pasan todo por (servicios externos, piezas propias, líneas), ascendente.
2. Ganadora: la primera. Respaldo: la segunda, si existe.
3. Si ninguna pasa todo, se aplica OQ2: se pregunta al humano qué se relaja; no se elige a ciegas.
4. Si hay empate completo, decide el humano con la tabla.

### F6. Escribir el ADR final (`../decisions.md`, ADR-C3)

1. Contexto: la tabla cerrada. Decisión: ganadora, respaldo y criterio decisivo. Alternativas: cada
   opción que no ganó, con su motivo.
2. Estado «Proposed» hasta que el humano apruebe; después «Accepted» con la fecha.

### F7. Reescribir `PUBLICAR_EN_INTERNET.md` (BR17.10)

Con la forma de la sección «Forma de PUBLICAR_EN_INTERNET.md». Se reemplaza entero: la guía de hoy es de
Render y de GitHub Desktop con repositorio privado, y las dos cosas cambiaron (Render no cumple NFR6; el
repositorio es público por decisión del humano).

### F8. Borrar las carpetas descartadas (BR17.9)

Solo después de la aprobación del ADR, en un commit propio. Se conservan la ganadora, el respaldo,
`prueba_comun/`, `LEEME.md` y `COMPARACION.md`.

## Estado conocido al diseñar (2026-10-25)

Lo que ya se sabe antes de las mediciones. Code Generation lo confirma o corrige con los JSON.

| Opción | Origen | Estado | Motivo |
|---|---|---|---|
| Cloudflare Workers | medida | candidata principal: pasó su corte (U1) | falta la prueba común completa de U2 y las unidades U4 a U6 |
| GitHub Pages | medida | pendiente de U11 a U14 | su ADR lo escribe otro agente en `u11-github-pages-corte/decisions.md`; tiene al menos 2 servicios externos por definición (pantallas en Pages, API en otro servicio) |
| Render | documentada (U15) | no pasa | NFR6: plan con disco US$ 7 al mes + US$ 0,25 por GB (https://render.com/pricing); gratuito sin disco, duerme a los 15 min y despierta en «about one minute» (https://render.com/docs/free): NFR4 y NFR5 |
| Cloudflare Containers | documentada (U16) | no pasa | NFR6: solo Workers Paid, US$ 5 al mes (https://developers.cloudflare.com/containers/pricing/); NFR4: disco efímero con el `Dockerfile` actual (https://developers.cloudflare.com/containers/platform-details/) |
| Apps Script | no pasa por contrato | no pasa | C-01: `doGet`/`doPost` no entregan cabeceras, así que no lee `X-Clave-Admin` (NFR9); no fija códigos de estado ni `Cache-Control` (`review-01.md`) |

Consecuencia (ADR-C3): si Workers pasa la prueba común completa, gana por el criterio 1 de FR12.6 (1
servicio externo frente a 2 o más de GitHub Pages) sin mirar piezas ni líneas; GitHub Pages queda de
respaldo si pasa todo. Si Workers no pasa y GitHub Pages sí, gana GitHub Pages sin respaldo en la nube; la
versión local sigue siendo el respaldo de aula (`despliegues/LEEME.md`). Si ninguna pasa, OQ2.

## Forma de `COMPARACION.md`

Se conserva la tabla de hoy (11 filas, 5 columnas) y se agregan, debajo, tres bloques:

1. **Veredicto por NFR**: una tabla con las doce filas de FR12.5 y una columna por opción («sí», «no»,
   «sin evidencia», «no se despliega»), con la evidencia entre paréntesis.
2. **Orden de FR12.6**: una tabla con servicios externos, piezas propias y líneas de cada opción que pasa
   todo, y el criterio decisivo.
3. **Resultado**: ganadora, respaldo, enlace al ADR y fecha de aprobación; las opciones saltadas con su
   motivo y fecha.

Al pie: «Mediciones: archivos de `prueba_comun/mediciones/`; documentación consultada el 2026-10-25 (U15 y
U16)».

## Forma de `PUBLICAR_EN_INTERNET.md`

La leen docentes y personas del semillero que no programan. Reglas de escritura: frases de 30 palabras o
menos; cada término técnico explicado en palabras simples la primera vez («servidor: el computador de la
empresa que atiende el enlace»); números en formato de Colombia; comillas «…» para botones y textos; sin
claves reales ni respuestas. Secciones, en este orden:

| # | Sección | Qué lleva | Requisito |
|---|---|---|---|
| 0 | Título y resumen | Qué se obtiene: un enlace fijo que funciona desde cualquier red, sin depender del computador del docente; costo US$ 0 con la cuota y su URL | FR5.1, NFR6 |
| 1 | Qué necesitas | Una cuenta en el proveedor ganador, el repositorio (público) y la clave del semillero de 12 caracteres o más guardada en el lugar privado | NFR9, NFR10 |
| 2 | Crear el servicio (persona del semillero) | Los pasos del `LEEME.md` de la ganadora en pasos numerados con comandos listos para copiar; nada se escribe a mano salvo la clave | FR8.1, NFR7 |
| 3 | Crear una sala y entregar la clave | Cómo el semillero crea una sala, cómo entrega al docente el código y la clave de sala, y que la clave se muestra una sola vez | FR11.5, ADR-003 |
| 4 | Prueba de humo antes del reto | Abrir el enlace con datos móviles, `…/api/publico` responde «ok», inscripción de prueba y «Reiniciar» (escribir BORRAR); abrir el enlace unos minutos antes si el hosting duerme | FR8.2, NFR5 |
| 5 | El día del reto (docente) | Abrir el enlace, entrar al panel con su clave, abrir la sala, proyectar el tablero con su `?sala=`; no cambiar nada con un reto en curso | NFR7, `project.md` («Mandated») |
| 6 | Después del reto: cerrar | Primero descargar los CSV y el paquete al lugar privado del semillero; comprobar que abren y tienen una fila por participante; solo entonces «Borrar la sala» (escribir BORRAR), que borra también las copias de «Reiniciar»; nada de eso va al repositorio | FR8.2, NFR10.1, FR9.4 |
| 7 | Volver a la versión anterior | El comando de vuelta atrás de la ganadora, en palabras simples, y que los datos no se pierden | FR8.2 |
| 8 | Dónde viven los datos | Corrige la frase de hoy: el reloj y la clasificación no viven solo en memoria; salen de la base de datos del servicio y sobreviven a un reinicio | FR8.3, NFR4 |
| 9 | Ensayar gratis sin publicar | Misma red wifi (`INICIAR_RETO`) o enlace temporal (`INICIAR_RETO_INTERNET`, Windows y Mac) | `2_Aplicacion_Reto/LEEME.md` |

Lo que desaparece de la guía de hoy: la «Parte 1» de GitHub Desktop con repositorio privado (el
repositorio es público por decisión del humano; lo que no se sube son claves ni datos), la «Parte 2» de
Render, el costo de US$ 7 y la nota de «solo Mac» del túnel (`CLAUDE.md`, «Gotchas»).

Cómo se comprueba BR17.10 antes del push: un conteo de palabras por frase sobre el archivo (por ejemplo
`python3 -c` con `re.split` por `.`, `?` y `!`) que no deje ninguna frase con más de 30 palabras, y una
lectura por alguien del semillero que no participó en el diseño (FR8.1).

## Fuera de la unidad

- No mide nada: las mediciones son de U2.
- No construye ninguna opción nueva; si el humano aprobara un costo, se agregarían unidades.
- No cambia `2_Aplicacion_Reto/` (FR12.1).
