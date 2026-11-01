# Entidades — U2 `u2-prueba-comun`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Este diseño ahora es para una sola sala, un
> solo docente y una sola clave docente, con un reloj por colegio (FR11, ADR-010, ADR-011, contrato C2).
> **SalaDePrueba** se retira y la reemplazan **RetoDePrueba** (el único reto, que se usa dos veces:
> calibración y reto principal, con «Reiniciar» entre las dos) y **ColegioDePrueba** (3 colegios con
> arranques a distinta hora, NFR1). **Corrida** pierde `salas` y gana `vencimiento`; `clave` es siempre
> la clave docente y `opcion` solo admite `local` o `cloudflare` (C3). Entra
> **ConfiguracionInicial**, que se guarda para dejar el reto como estaba. **ParticipanteFicticio**
> cambia `sala` por `colegio` y gana tres papeles. **Comprobacion** y **Medicion** siguen el C3
> revisado: la parte `salas` pasa a `relojes`, entra la parte `claves` y `nfr.salas` pasa a
> `nfr.colegios`.

Lo que maneja la prueba común completa. No son entidades del reto: esas están en `components.md` y en
`../../u5-cloudflare-salas/functional-design/entities.md`. Son los datos de una corrida de la prueba, que
vive en `despliegues/prueba_comun/` y corre desde la computadora de quien prueba (`unit-of-work.md`, U2).
Nada de esto se guarda en una base: vive en memoria mientras corre, y solo la Medicion se escribe en disco
(contrato C3). Las decisiones las tomó el asistente con la potestad que dio el humano (2026-10-25).

```yaml
entities:
  - name: Corrida
    description: Una ejecución de la prueba contra una URL, en un modo y con una opción nombrada.
    owner: Prueba
    attributes:
      - {name: url, type: texto, required: true, constraints: 'sin barra final; nunca lleva la clave (NFR9)'}
      - {name: clave, type: texto, required: true, constraints: 'siempre la clave docente, en la nube y en local (C2); llega por argumento o PRUEBA_CLAVE; viaja solo en X-Clave-Admin; nunca se imprime ni se escribe'}
      - {name: modo, type: enum, required: true, allowed: [nube, local], constraints: 'nube = la versión de Cloudflare (wrangler dev o URL de Workers); local = 2_Aplicacion_Reto/servidor.py, que no cambia (FR12.1)'}
      - {name: opcion, type: enum, required: true, allowed: [local, cloudflare], constraints: 'la del esquema C3; en modo local es local'}
      - {name: duracion_min, type: entero, required: true, default: 10, min: 1, max: 240, constraints: 'duración del reto principal y de la calibración; el servidor decide el mínimo: 10 en producción y en local, y el de DURACION_MINIMA_MIN en wrangler dev (D9); si el servidor guarda otro valor, la prueba usa el que lee del resumen'}
      - {name: vencimiento, type: enum, required: true, allowed: [esperar, omitir], default: esperar, constraints: 'esperar = la prueba espera el fin real de cada reloj; omitir = contra la URL pública, las comprobaciones que necesitan el vencimiento van a no_aplica (D9)'}
      - {name: reinicio, type: enum, required: true, allowed: [ninguno, manual, comando], default: ninguno}
      - {name: comando_reinicio, type: texto, required: false, constraints: 'solo con reinicio = comando'}
      - {name: medir_frio, type: booleano, required: true, default: false, constraints: 'si la primera petición cuenta como arranque en frío (NFR5)'}
      - {name: semilla_guion, type: entero, required: true, default: 7, constraints: 'semilla del generador de azar del guion, como random.seed(7) en simulacro.py'}
      - {name: participantes, type: entero, required: true, default: 40, min: 12, constraints: 'con menos de 40, el reparto entre colegios es proporcional (BR6.1)'}
      - {name: fallas, type: lista, required: true, default: '[]', constraints: 'mensajes de las comprobaciones que fallaron, en orden'}
      - {name: no_aplica, type: lista, required: true, default: '[]', constraints: 'ids de las comprobaciones que no aplican en esta corrida, cada una con su motivo (BR8.1)'}
      - {name: peticiones, type: entero, required: true, default: 0, constraints: 'cuenta cada petición HTTP que hace la prueba (NFR6)'}
      - {name: copias_creadas, type: lista, required: true, default: '[]', constraints: 'id_copia de cada «Reiniciar» que hizo la prueba; son las únicas que la prueba borra (BR1.6)'}
  - name: ConfiguracionInicial
    description: Lo que el reto tenía antes de la corrida, para dejarlo igual al terminar.
    owner: Prueba
    attributes:
      - {name: duracion_min, type: entero, required: true, constraints: 'de config en /api/admin/resumen'}
      - {name: modo_sorpresa, type: booleano, required: true}
      - {name: retro, type: booleano, required: true}
      - {name: colegios, type: lista, required: true, constraints: 'nombres de la lista del docente, en orden; vacía en local, que no tiene lista'}
      - {name: copias, type: lista, required: true, constraints: 'id_copia de las copias que ya existían; la prueba nunca las borra'}
    constraints:
      - 'se lee en el paso 2, solo si el reto está en inscripcion y sin inscritos (BR1.5)'
      - 'vive en memoria; nunca se escribe en el JSON'
  - name: Comprobacion
    description: Una verificación con nombre fijo, su parte y si pasó.
    owner: Prueba
    attributes:
      - {name: id, type: texto, required: true, unique: true, constraints: 'nombre fijo en snake_case, por ejemplo fuga_verdad_cerrado; es la clave que U17 lee (C3)'}
      - {name: parte, type: enum, required: true, allowed: [base, fugas, relojes, claves, nfr], constraints: 'las partes del C3 revisado'}
      - {name: pasa, type: booleano, required: true}
      - {name: detalle, type: texto, required: false, constraints: 'nunca una clave, un token ni una respuesta correcta'}
      - {name: esencial, type: booleano, required: true, default: false, constraints: 'si falla, la corrida se detiene porque lo demás depende de ella'}
  - name: RetoDePrueba
    description: El único reto del servicio, tal como lo usa la prueba en cada uno de sus dos papeles.
    owner: Prueba
    attributes:
      - {name: papel, type: enum, required: true, allowed: [calibracion, principal], constraints: 'primero la calibración; «Reiniciar» la borra y empieza el principal (BR2.1)'}
      - {name: codigo_sala, type: texto, required: true, constraints: 'se lee de config.sala en /api/admin/resumen (nube) o de /api/publico (local); la prueba no lo cambia'}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados]}
      - {name: abierto_en, type: número, required: false, constraints: 'hora del servidor al abrir, leída de /api/publico'}
      - {name: id_copia, type: texto, required: false, constraints: 'la copia que dejó «Reiniciar» al terminar este papel'}
  - name: ColegioDePrueba
    description: Un colegio que la prueba agrega a la lista del docente para el reto principal.
    owner: Prueba
    attributes:
      - {name: letra, type: enum, required: true, allowed: [A, B, C], constraints: 'en la calibración hay un solo colegio, sin letra'}
      - {name: nombre, type: texto, required: true, unique: true, constraints: '«Colegio Prueba <letra> <sufijo de corrida>»; inventado, nunca un colegio real'}
      - {name: id_colegio, type: texto, required: false, constraints: 'lo devuelve POST /api/admin/colegios (agregar); en local no existe y el colegio va como texto'}
      - {name: tamano, type: entero, required: true, constraints: 'equipos planeados: A 20, B 12 y C 8 (suman 40, NFR1)'}
      - {name: desfase_seg, type: entero, required: true, constraints: 'A 0 (arranca al abrir), B 20 y C 40 (se arrancan con «Arrancar reloj» a esos segundos de abierto_en)'}
      - {name: arranque, type: número, required: false, constraints: 'hora del servidor, leída de colegios[] en /api/admin/resumen'}
  - name: ParticipanteFicticio
    description: Un participante inventado del guion, con su papel y lo que la prueba sabe de él.
    owner: Guion
    attributes:
      - {name: k, type: entero, required: true, unique: true, constraints: 'índice global de 0 a participantes - 1; fija el papel, el colegio y el azar del guion'}
      - {name: colegio, type: referencia, references: ColegioDePrueba, required: true}
      - {name: papel, type: enum, required: true, allowed: [perfecto, cero, parcial, vencido_sin_respuestas, vencido_al_final, llega_tarde, no_inicia, vencido_colegio, entregado_docente, normal, calibrador]}
      - {name: nivel, type: número, required: true, min: 0, max: 1, constraints: 'k / (participantes - 1), como en simulacro.py'}
      - {name: nombre, type: texto, required: true, constraints: 'inventado: «Detective <k> <sufijo de corrida>»'}
      - {name: grado, type: enum, required: true, allowed: ['9', '10', '11'], constraints: 'k mod 3: 9, 10 u 11, para que cada grado tenga clasificación propia (FR2.5)'}
      - {name: token, type: texto, required: false, constraints: 'secreto; nunca se imprime ni se escribe'}
      - {name: codigo, type: texto, required: false, constraints: '5 caracteres que devuelve /api/registro'}
      - {name: id, type: entero, required: false, constraints: 'id del participante, leído de /api/admin/resumen; lo usan las acciones del docente'}
      - {name: grupo, type: enum, required: false, allowed: [A, B], constraints: 'se lee de /api/admin/resumen, no de la base'}
      - {name: misiones, type: lista, required: false, constraints: 'el examen público que recibió, con ids opacos; vive en memoria'}
      - {name: fracciones, type: mapa, required: true, default: '{}', constraints: 'pregunta_id -> fracción que devolvió /api/responder; va al JSON (no es una respuesta)'}
      - {name: puntos_esperados, type: número, required: true, default: 0, constraints: 'suma de puntos de las preguntas que el guion decidió acertar y alcanzó a enviar'}
  - name: HuellaDePregunta
    description: Identidad de una pregunta tal como la ve un participante, sin ids, para reconocer su variante.
    owner: Guion
    attributes:
      - {name: pregunta_id, type: texto, required: true}
      - {name: huella, type: texto, required: true, constraints: 'sha256 del JSON ordenado de los textos visibles (enunciado, textos de opciones, ítems, publicaciones, categorías, etiquetas de partes, min, max); sin ids ni orden'}
    constraints:
      - 'pregunta_id + huella es único; m2_trampas produce hasta 4 huellas (sus variantes cambian solo los ítems)'
  - name: ClavePorTexto
    description: La respuesta correcta de una pregunta en una variante, expresada con textos y no con ids.
    owner: Guion
    attributes:
      - {name: pregunta_id, type: texto, required: true}
      - {name: huella, type: texto, required: true}
      - {name: tipo, type: enum, required: true, allowed: [opcion, multiple, clasificar, compartir, recordatorio, ordenar, construir, texto, estimar, numero]}
      - {name: correcta, type: json, required: false, constraints: 'texto de la opción; lista de textos; mapa texto de ítem -> id de categoría; lista de textos en orden; mapa etiqueta de parte -> texto de opción; número; o nada si la pregunta no tiene clave'}
    constraints:
      - 'se obtiene solo de revision de /api/estado con el reto de calibración en resultados (BR2.3); nunca del banco ni de otro archivo'
      - 'vive en memoria durante la corrida; nunca se imprime ni se escribe en disco'
  - name: Medicion
    description: El archivo JSON de una corrida, con el esquema del contrato C3 revisado.
    owner: Prueba
    attributes:
      - {name: version_esquema, type: entero, required: true, constraints: 'siempre 1 (D8)'}
      - {name: opcion, type: enum, required: true, allowed: [local, cloudflare]}
      - {name: url, type: texto, required: true}
      - {name: inicio, type: fecha-hora, required: true}
      - {name: fin, type: fecha-hora, required: true}
      - {name: todo_bien, type: booleano, required: true}
      - {name: comprobaciones, type: lista, required: true, constraints: 'una Comprobacion por fila: id, parte, pasa, detalle; las de no_aplica no van aquí'}
      - {name: nfr, type: json, required: true, constraints: 'obligatorias: p95_responder_ms, p95_tablero_ms, sobrevive_reinicio, arranque_frio_ms, colegios, participantes, peticiones; agregadas (C3 permite agregar): duracion_min, vencimiento, no_aplica (lista de {id, motivo}), p95_resumen_ms, fracciones (lista de {k, pregunta_id, fraccion}) y encabezados_csv ({resultados, respuestas})'}
    constraints:
      - 'se escribe en despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json'
      - 'nunca lleva la URL con clave, claves, tokens, nombres de la corrida, nombres de colegios ni respuestas correctas'
relationships:
  - {from: Corrida, to: Comprobacion, cardinality: '1 a muchos'}
  - {from: Corrida, to: ConfiguracionInicial, cardinality: '1 a 1', note: 'solo en modo nube; en local guarda solo duracion_min, modo_sorpresa y retro'}
  - {from: Corrida, to: RetoDePrueba, cardinality: '1 a 2', note: 'el mismo reto del servicio, primero de calibración y después principal'}
  - {from: RetoDePrueba, to: ColegioDePrueba, cardinality: '1 a muchos', note: 'calibración: 1 colegio; principal: 3 colegios'}
  - {from: ColegioDePrueba, to: ParticipanteFicticio, cardinality: '1 a muchos'}
  - {from: ParticipanteFicticio, to: HuellaDePregunta, cardinality: 'muchos a muchos', note: 'cada participante ve una huella por pregunta'}
  - {from: HuellaDePregunta, to: ClavePorTexto, cardinality: '1 a 1'}
  - {from: Corrida, to: Medicion, cardinality: '1 a 1'}
```

## Resumen

- **Corrida** y **Comprobacion** ya existen en la prueba mínima de U1 (`Prueba`, `comprobar`). Aquí
  ganan la opción, la duración, el modo de vencimiento, el reinicio, el conteo de peticiones, la lista
  `no_aplica` y la marca `esencial`.
- **ConfiguracionInicial** existe porque la prueba usa el único reto del servicio: al terminar, lo deja
  con la misma duración, los mismos interruptores, la misma lista de colegios y sin copias nuevas
  (BR1.6).
- **RetoDePrueba** y **ColegioDePrueba** son el plan de carga de NFR1: un reto con 40 equipos de
  3 colegios, cuyos relojes arrancan a 0, 20 y 40 segundos de la apertura.
- **ParticipanteFicticio** reproduce los casos de `simulacro.py` y agrega tres papeles: `no_inicia`
  (cerrar lo deja en «No inició»), `vencido_colegio` (vence a la hora de su colegio, no a la del
  primero) y `entregado_docente` (lo entrega el panel).
- **HuellaDePregunta** y **ClavePorTexto** permiten responder bien sin que la prueba conozca el banco:
  la clave sale de `revision` después de publicar los resultados de la calibración.
- **Medicion** es el contrato C3 revisado. `no_aplica`, `vencimiento`, `fracciones` y
  `encabezados_csv` son claves agregadas para que U17 sepa qué no se midió y compare la calificación con
  la versión local (NFR11) sin cambiar `version_esquema`.
