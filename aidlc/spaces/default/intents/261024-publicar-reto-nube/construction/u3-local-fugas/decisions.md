# ADR de la corrección de fugas en la versión local (U3)

**Estado:** aprobado por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). U3 es la única excepción a FR12.1 (OQ9, aprobada en Units Generation Q3-A): toca
solo `2_Aplicacion_Reto/servidor.py` y agrega una prueba `unittest`; no cambia pantallas, puntajes,
desempates ni flujo de estados (`project.md`, «Forbidden»), y `simulacro.py` sigue igual (FR6.3).

## ADR-L1: Ids opacos en Python con `hmac` de la semilla, traducción tolerante a la entrada

- **Context** — FR6.2 pide que los ids de opciones, ítems y partes que salen por `/api/estado` sean
  opacos, calculados en el servidor, sin tocar el banco ni lo que ve el estudiante, y que la base y
  `respuestas.csv` sigan con los ids del banco. ADR-006 fijó el mecanismo para toda versión: HMAC con la
  semilla secreta del participante, el id de la pregunta y el de la opción. Hoy `servidor.py` ya tiene
  la semilla (`secrets.token_hex(8)` en `registrar`) y ya baraja el orden con `rng_para`. La restricción
  propia de U3 es que `simulacro.py` no cambia y hoy envía a `/api/responder` los ids del banco que lee
  de `S.PREGUNTAS` (FR12.1, FR6.3). El código tiene que correr en Python 3.9 (`python-code.md`).

| | A. Traducir en los bordes de `version_publica`, `responder` y `estado_participante`, aceptando a la entrada el id opaco y el del banco | B. Igual que A, pero rechazar a la entrada todo id que no sea opaco | C. Reescribir `version_publica` como en `reglas.js` (orden por id opaco, lista blanca) |
|---|---|---|---|
| Cambio en `servidor.py` | Pequeño: 5 funciones nuevas (≈ 90 líneas) y 4 líneas tocadas | Igual que A | Grande: reescribe el armado del examen |
| `simulacro.py` sigue en «TODO BIEN» sin cambios | Sí: sus ids del banco pasan tal cual | No: `assert st == 200` falla en cada respuesta | Sí o no según se acepte la entrada |
| Cierra FR6.2 | Sí: a la salida todo es opaco | Sí | Sí |
| Orden que ve el estudiante | El de hoy (`rng_para`), ya distinto del banco | El de hoy | Cambia a orden por id opaco |
| Riesgo de conducta visible | Ninguno: mismas pantallas, mismos puntos | Ninguno | El orden cambia; `m1_compartir` y `m1_veracidad` deben seguir alineados |
| Python 3.9 | `hmac`, `hashlib` y `base64` de la biblioteca estándar | Igual | Igual |

- **Decision** — A. Mecanismo exacto:
  - `opaco_de(semilla, ambito, id)` = «o» + los primeros 11 caracteres de `base64.b32encode(HMAC-SHA256(
    clave = semilla, mensaje = f"{ambito}|{id}"))` en minúsculas. `opacos_de(semilla, ambito, ids)`
    devuelve el mapa id del banco → id opaco y, si dos de los 11 chocan dentro del grupo, usa 16 para
    todo el grupo. Es la forma de BR6.1 de U1 (`^o[a-z2-7]{11}([a-z2-7]{5})?$`), que la prueba común ya
    reconoce; no hace falta que dé el mismo valor que Workers (ADR-006).
  - Ámbitos: `opciones` → `pregunta_id`; `items` y `publicaciones` → `m1_posts` en la misión 1 y
    `pregunta_id` en las demás (así la misma publicación tiene el mismo id opaco en «¿lo compartirías?»,
    «¿es verdad?» y el recordatorio, como hoy comparten orden); `partes` → `pregunta_id|partes`; las
    opciones de una parte → `pregunta_id|parte_id`. Los ids de `categorias` siguen siendo del banco: son
    etiquetas (`V`/`F`, `S`/`N`, `IA`…) y no se correlacionan con la clave.
  - Salida: `version_publica` termina con `opacar_salida(pub, semilla, pregunta_id)`, que reemplaza los
    ids en los cuatro lugares; `estado_participante` pasa por `opacar_respuesta` cada
    `respuestas[qid].respuesta` y cada `revision[qid].respuesta`, porque `estudiante.js` compara esos
    valores con los ids que ve (hallazgo C-02 del contrato).
  - Entrada: `responder` aplica `traducir_entrada(respuesta, semilla, cuerpo)` antes de
    `validar_respuesta`: un id opaco conocido se vuelve el del banco; cualquier otro valor pasa igual.
    Así `simulacro.py` y cualquier cliente con ids del banco siguen funcionando, y un id opaco inventado
    cae en el 400 «Respuesta incompleta o con formato no válido.» de hoy.
  - El orden sigue siendo el de `rng_para` (ya es distinto del orden del banco, FR6.2) y el cuidado de
    «ordenar» (nunca mostrar el orden correcto) queda igual.
- **Consequences** — A favor: diff pequeño en una versión congelada, pantallas y puntos idénticos,
  `simulacro.py` intacto y la parte de fugas de la prueba común pasa. En contra: la entrada acepta dos
  alfabetos de ids; no es una fuga, porque aceptar un id del banco no revela nada que el estudiante no
  sepa ya (con `retro` recibe la fracción de su propia respuesta, como hoy), y queda escrito en el
  docstring de `traducir_entrada` por qué existe. Cada `/api/estado` calcula unos 250 HMAC (≤ 3 ms);
  no se agrega caché (ver `nfr-design/performance-design.md`).
- **Alternatives Rejected** — B: rompe `simulacro.py`, que no se puede cambiar (FR6.3, FR12.1). C:
  reescribe el armado del examen en una versión congelada, con riesgo de cambiar el orden que ve el
  estudiante sin ganancia frente a A.

## ADR-L2: En «cerrado», el experimento sale solo con `n` y `listo`

- **Context** — FR6.1 pide que `/api/publico` no entregue en «cerrado» ningún campo «que revele o
  permita deducir el veredicto de cada publicación», y nombra `verdad` y `multitud_acierta`. El contrato
  C1 escribe solo esos dos. Pero `experimento()` también devuelve `clase.cree_falsas`,
  `comparte_falsas` y sus pares para «verdaderas», `multitud.aciertos_multitud` y, por publicación,
  `pct_cree_verdadera`: con los porcentajes de 10 publicaciones y la media sobre el subconjunto de las
  falsas, un estudiante con calculadora puede resolver qué subconjunto es, que es la clave de
  `m1_veracidad`. `tablero.html` en «cerrado» muestra solo «Expediente cerrado» y usa del experimento
  únicamente `n` (en la firma de cambios, línea 144); los tres diapositivas del experimento se dibujan
  solo en «resultados» (líneas 221–330; hallazgo del revisor del contrato).

| | A. Quitar solo `verdad` y `multitud_acierta` en cerrado | B. En cerrado devolver `{n, listo}` y nada más | C. No devolver `experimento` en cerrado |
|---|---|---|---|
| Cumple la letra de FR6.1 y el contrato | Sí | Sí (más estricto; C1 solo exige que no traiga esos dos) | Sí |
| Cierra la deducción por agregados | No | Sí | Sí |
| El tablero en cerrado se ve igual | Sí | Sí: usa solo `n` | Casi: `d.experimento && d.experimento.n` da `undefined` y la firma cambia una vez; se ve igual |
| Cambio | 6 líneas | 4 líneas | 2 líneas |

- **Decision** — B. `publico()` devuelve en «cerrado» `{"n": n, "listo": listo}` del experimento, y en
  «resultados» el experimento completo, igual que hoy. `resumen_admin` sigue devolviendo el experimento
  completo en cualquier estado: va con clave docente.
- **Consequences** — A favor: ningún número derivado de la clave sale sin clave antes de «resultados»;
  el tablero no cambia. En contra: es más estricto que el contrato; la prueba común solo exige la ausencia
  de los dos campos, así que las opciones de la nube pueden elegir A o B. Se anota en `contract-summary.md`
  como recomendación cuando se toque el contrato.
- **Alternatives Rejected** — A: deja la deducción abierta. C: cambia una clave que el tablero lee,
  aunque sea inofensivo; B lo evita por el mismo costo.

## ADR-L3: Pruebas `unittest` de las funciones nuevas, sin tocar `simulacro.py`

- **Decision** — Las cinco funciones nuevas son puras (reciben datos y devuelven datos) y se prueban en
  `2_Aplicacion_Reto/pruebas/test_servidor.py` con preguntas inventadas (sin respuestas del banco):
  forma del id opaco, dependencia de la semilla y del ámbito, regla de choque, ida y vuelta de cada tipo
  de respuesta, valores no opacos que pasan igual, y el experimento recortado en «cerrado». La
  aceptación sigue siendo `python3 pruebas/simulacro.py 40` en «TODO BIEN» y la parte de fugas de la prueba
  común en modo local.
- **Alternatives Rejected** — Probar solo por HTTP con la prueba común: deja sin prueba unitaria la
  regla de choque y la traducción por tipo, que son las que más fallan.
