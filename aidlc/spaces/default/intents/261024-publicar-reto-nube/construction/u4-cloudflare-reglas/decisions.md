# ADR de la opción Cloudflare Workers (U4, reglas)

**Estado:** aprobado por el asistente con la potestad que dio el humano («potestad absoluta para
decidir», 2026-10-25). Continúa la numeración de `../u1-cloudflare-corte/decisions.md` (ADR-W1 a ADR-W5),
que siguen vigentes: un solo Durable Object con SQLite, JavaScript sin build, pruebas con `node:test`,
tabla de rutas, claves e ids opacos, banco dentro del código.

## ADR-W6: Un módulo por «calculadora» bajo `src/reglas/`, con `src/reglas.js` como fachada

- **Context** — U1 dejó `src/reglas.js` con 495 líneas y solo la parte mínima de Banco y Calificacion.
  U4 agrega los otros 9 tipos de pregunta, Clasificacion, CicloDeSala completo, LimpiezaEntrada y
  Experimento (`unit-of-work.md`, «U4, U8, U12»). En un solo archivo pasaría de 1.000 líneas, y el resto
  del equipo entrega por PR de máximo 400 líneas (`team.md`).

| | A. Un solo `src/reglas.js` | B. Un archivo por componente en `src/reglas/` y una fachada `src/reglas.js` | C. Un archivo por función |
|---|---|---|---|
| Archivos | 1 | 7 (6 componentes + fachada) | Más de 30 |
| Cambio en `reto.js` | Ninguno | Ninguno: sigue importando `./reglas.js` | Cada import cambia |
| Revisión por PR | Un archivo de 1.000 líneas | Cada componente cabe en un PR | Demasiados archivos pequeños |
| Coincide con `components.md` | No se ve | Sí: un archivo por bloque de la capa Reglas | No |

- **Decision** — B. `src/reglas/{banco,calificacion,clasificacion,ciclo_de_sala,limpieza_entrada,experimento}.js`
  y `src/reglas.js` que reexporta todo (`export * from "./reglas/banco.js"`, etc.), así `reto.js` no cambia
  su import y las pruebas de U1 siguen pasando. Las pruebas van en `pruebas/<componente>.test.js`, una por
  archivo, y se corren nombrando cada archivo (`project.md`, «Corrections»: `node --test <archivo>`).
- **Consequences** — A favor: cada bloque de `components.md` tiene un archivo con el mismo nombre y su
  prueba al lado; los PR del equipo caben en 400 líneas. En contra: 7 archivos donde había 1, y un
  `import` relativo entre reglas (por ejemplo, `calificacion.js` usa `a_numero` propio y nada más; solo
  `banco.js` comparte `sha256_hex` con `calificacion.js` a través de `comun.js`).
- **Alternatives Rejected** — A: no cabe en los PR del equipo y mezcla seis responsabilidades. C:
  fragmenta sin ganancia.

## ADR-W7: La tabla de casos se genera con la versión local y vive en `despliegues/prueba_comun/`

- **Context** — El contrato C4 fija `despliegues/prueba_comun/casos_reglas.json` con la regla de oro
  «la salida esperada se calcula con el servidor local, nunca se escribe a mano», y `project.md` manda
  compartir entre opciones solo datos, que cada opción copia a sus pruebas. U1 no creó la tabla
  (`code-summary.md`, desviación 4). Hay reglas que `servidor.py` **no tiene** (FR10.2 forma NFC y
  caracteres invisibles, FR10.4 integrantes, FR7.4 transiciones, hora de entrega con cierre).

| | A. Un generador en Python que importa `servidor.py` y, para lo que no existe allí, trae su propia referencia | B. Escribir los casos a mano a partir de leer `servidor.py` | C. Correr `servidor.py` por HTTP y capturar las respuestas |
|---|---|---|---|
| Cumple la regla de oro | Sí para todo lo que `servidor.py` calcula; lo demás se calcula, no se transcribe | No | Sí, pero solo lo que sale por la API (puntos redondeados a 2 decimales, sin fracciones exactas) |
| Toca `2_Aplicacion_Reto/` | No: solo lo importa en modo lectura | No | No |
| Cubre desempates y vencimiento | Sí, con una base SQLite en memoria (`conectar(":memory:")`) y filas fabricadas | A mano | Exige esperar el reloj |
| Costo | Medio: un script de unas 200 líneas | Bajo, pero sin garantía | Alto |

- **Decision** — A. `despliegues/prueba_comun/herramientas/generar_casos.py` (Python 3.12, biblioteca
  estándar) importa `2_Aplicacion_Reto/servidor.py` como módulo, reemplaza `BANCO` y `PREGUNTAS` por un
  banco de prueba inventado (`despliegues/prueba_comun/banco_prueba.json`, 1.000 puntos, con un
  Expediente 01 propio) y calcula con `fraccion`, `validar_respuesta`, `a_numero`, `finalizar`,
  `clasificacion`, `experimento`, `cambiar_estado` y `vencer_tiempos` sobre una base en memoria. Para
  FR10.2, FR10.4 y FR7.4 el generador lleva una referencia en Python escrita según `requirements.md`, y
  cada caso de esas reglas lleva `fuente: "referencia FR10.2"` en vez de `fuente: "servidor.py"`. El
  JSON se escribe con `sort_keys` y sangría fija para que un cambio se vea en el diff. `copiar.sh` copia
  la tabla a `despliegues/cloudflare/pruebas/casos_reglas.json`, y `verificar.sh` compara las dos huellas
  SHA-256 y se detiene si la copia está vieja (misma lección que la copia del banco, `project.md`).
- **Consequences** — A favor: ningún número de la tabla sale de la mano de una persona; los casos de
  Calificacion no llevan respuestas del banco real (C4, `no_lleva`). En contra: el generador depende de
  nombres internos de `servidor.py`; como esa versión está congelada (FR12.1), no cambian.
- **Alternatives Rejected** — B: viola la regla de oro. C: pierde precisión y exige esperar el reloj.

## ADR-W8: Igualdad numérica entre Python y JavaScript

- **Context** — Los dos lenguajes usan el mismo doble IEEE 754, así que la misma secuencia de
  operaciones da el mismo resultado. Difieren en tres puntos: `round(x, 9)` de Python redondea el valor
  binario exacto a par; `\d` de Python acepta dígitos Unicode y `float()` los lee; y `json.dumps` separa
  con `", "` y `": "`.

| | A. Reproducir la operación de Python donde cambia el resultado y aceptar lo demás con prueba | B. Portar `round` y `float` de Python al detalle | C. Comparar con tolerancia en todas partes |
|---|---|---|---|
| Mismos puntos y orden (NFR11) | Sí: las operaciones de `fraccion`, bono y desempates se escriben en el mismo orden | Sí | No garantiza el orden en empates cercanos |
| Costo | Bajo | Alto, sin caso real que lo pida | Bajo |

- **Decision** — A. Reglas exactas:
  - `fraccion`, `bono` y `cerrar_intento` hacen las operaciones en el mismo orden que `servidor.py`
    (por ejemplo, `20 * (puntos / 1000) * (1 - t / dur)`, no reordenado), así el resultado es idéntico bit
    a bit y las pruebas comparan con `assert.equal`, salvo los casos marcados `tolerancia: 1e-9` en la
    tabla (porcentajes del experimento que dividen por `n`).
  - La clave de orden usa `redondear9(x) = Number(x.toFixed(9))`. Difiere de Python solo cuando el
    décimo decimal es exactamente 5 en binario, lo que no ocurre con sumas de puntos del banco (múltiplos
    de 1/12 como máximo) ni con bonos reales; la tabla de casos lleva los empates que importan (mismo
    total y puntos con tiempos distintos; mismo todo salvo `id`).
  - `a_numero` acepta solo dígitos ASCII: un dígito arábigo-índico no es un caso del aula. Se documenta
    como diferencia aceptada y no entra en la tabla.
  - El valor de `respuesta` que sale en `respuestas.csv` se serializa como `json.dumps(ensure_ascii=False)`
    (separadores `", "` y `": "`): lo hace U6 al exportar, no la regla; en la base queda compacto como U1.
- **Consequences** — A favor: comparación exacta donde cuenta. En contra: quien toque una fórmula debe
  conservar el orden de operaciones; las pruebas con la tabla lo detectan.
- **Alternatives Rejected** — B: código extra para casos que no existen. C: oculta diferencias reales.

## ADR-W9: Qué sale del experimento antes de «resultados»

- **Context** — FR6.1 prohíbe en `/api/publico`, mientras la sala no esté en `resultados`, «ningún campo
  del experimento que revele o permita deducir el veredicto de cada publicación». Hoy el tablero en
  «cerrado» no usa ningún campo del experimento salvo `experimento.n` para su firma de redibujo
  (`tablero.html`, `sondear()`); el panel docente sí usa el experimento completo, con clave.

| | A. En «cerrado», `/api/publico` trae solo `{n, listo}` | B. Quitar solo `verdad` y `multitud_acierta` (lo mínimo que nombra FR6.1) | C. No traer `experimento` en «cerrado» |
|---|---|---|---|
| Cierra la fuga | Sí | No del todo: `clase.cree_falsas`, `cree_verdaderas` y `por_publicacion[].pct_cree_verdadera` permiten deducir con pocos participantes cuáles son las falsas | Sí |
| Conducta visible | Igual: el tablero no muestra nada del experimento en «cerrado» | Igual | Cambia la firma de redibujo del tablero (`experimento && experimento.n`): redibuja una vez más, sin efecto visible |
| Costo | Una función pura `experimento_publico(experimento, estado)` | Igual | Igual |

- **Decision** — A. `Experimento.calcular` devuelve siempre el objeto completo (lo usa el panel con
  clave); `Experimento.experimento_publico` lo reduce a `{n, listo}` salvo en `resultados`. Es la
  lectura más estricta de FR6.1 sin cambiar nada visible.
- **Consequences** — A favor: ningún porcentaje por publicación sale sin clave antes de publicar. En
  contra: ninguna.
- **Alternatives Rejected** — B: deja deducible el veredicto. C: cambia la firma del tablero sin motivo.
