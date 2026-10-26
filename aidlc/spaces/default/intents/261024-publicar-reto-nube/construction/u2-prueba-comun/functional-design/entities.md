# Entidades — U2 `u2-prueba-comun`

Lo que maneja la prueba común completa. No son entidades del reto (esas están en `components.md` y en
`u1-cloudflare-corte/functional-design/entities.md`): son los datos de una corrida de la prueba, que vive en
`despliegues/prueba_comun/` y corre desde la computadora de quien prueba (`unit-of-work.md`, U2). Nada
de esto se guarda en una base: vive en memoria mientras corre y solo la Medicion se escribe en disco
(contrato C3). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

```yaml
entities:
  - name: Corrida
    description: Una ejecución de la prueba contra una URL, en un modo y con una opción nombrada.
    owner: Prueba
    attributes:
      - {name: url, type: texto, required: true, constraints: 'sin barra final; nunca lleva la clave (NFR9)'}
      - {name: clave, type: texto, required: true, constraints: 'clave del semillero (nube) o docente (local); llega por argumento o PRUEBA_CLAVE y nunca se imprime ni se escribe'}
      - {name: modo, type: enum, required: true, allowed: [nube, local]}
      - {name: opcion, type: enum, required: true, allowed: [local, cloudflare, apps_script, github_pages], constraints: 'la del esquema C3; en modo local es local'}
      - {name: duracion_min, type: entero, required: true, default: 10, min: 10, max: 240, constraints: 'duración de cada sala del reto; 10 es el mínimo que acepta el servidor (C-09)'}
      - {name: reinicio, type: enum, required: true, allowed: [ninguno, manual, comando], default: ninguno}
      - {name: comando_reinicio, type: texto, required: false, constraints: 'solo con reinicio = comando'}
      - {name: medir_frio, type: booleano, required: true, default: false, constraints: 'si la primera petición cuenta como arranque en frío (NFR5)'}
      - {name: semilla_guion, type: entero, required: true, default: 7, constraints: 'semilla del generador de azar del guion, como random.seed(7) en simulacro.py'}
      - {name: participantes, type: entero, required: true, default: 40, min: 2}
      - {name: salas, type: entero, required: true, default: 10, constraints: 'en modo local siempre 1'}
      - {name: fallas, type: lista, required: true, default: '[]', constraints: 'mensajes de las comprobaciones que fallaron, en orden'}
      - {name: peticiones, type: entero, required: true, default: 0, constraints: 'cuenta cada petición HTTP que hace la prueba (NFR6)'}
  - name: Comprobacion
    description: Una verificación con nombre fijo, su parte y si pasó.
    owner: Prueba
    attributes:
      - {name: id, type: texto, required: true, unique: true, constraints: 'nombre fijo en snake_case, por ejemplo fuga_verdad_cerrado; es la clave que U17 lee (C3)'}
      - {name: parte, type: enum, required: true, allowed: [base, fugas, salas, nfr]}
      - {name: pasa, type: booleano, required: true}
      - {name: detalle, type: texto, required: false, constraints: 'nunca una clave, un token ni una respuesta correcta'}
      - {name: esencial, type: booleano, required: true, default: false, constraints: 'si falla, la corrida se detiene porque lo demás depende de ella'}
  - name: SalaDePrueba
    description: Una sala que la prueba crea (nube) o la única sala del servidor (local).
    owner: Prueba
    attributes:
      - {name: codigo, type: texto, required: true, constraints: 'lo da el servicio; en local sale de /api/publico'}
      - {name: clave_sala, type: texto, required: true, constraints: 'en nube la devuelve /api/admin/salas/crear; en local es la clave docente; nunca se imprime'}
      - {name: papel, type: enum, required: true, allowed: [calibracion, reto]}
      - {name: tamano, type: entero, required: true, min: 1, max: 10, constraints: 'participantes planeados; las 10 salas del reto miden 10, 7, 6, 5, 4, 3, 2, 1, 1 y 1 (suman 40, NFR1)'}
      - {name: id_colegio, type: texto, required: false, constraints: 'colegio provisional con nombre único por corrida (nube); en local el colegio va como texto'}
      - {name: abierto_en, type: número, required: false, constraints: 'hora del servidor al abrir, leída de /api/publico?sala='}
  - name: ParticipanteFicticio
    description: Un participante inventado del guion, con su papel y lo que la prueba sabe de él.
    owner: Guion
    attributes:
      - {name: k, type: entero, required: true, unique: true, constraints: 'índice global 0 a participantes - 1; fija el papel y el azar del guion'}
      - {name: sala, type: referencia, references: SalaDePrueba, required: true}
      - {name: papel, type: enum, required: true, allowed: [perfecto, cero, parcial, vencido_sin_respuestas, vencido_al_final, llega_tarde, normal, calibrador]}
      - {name: nivel, type: número, required: true, min: 0, max: 1, constraints: 'k / (participantes - 1), como en simulacro.py'}
      - {name: nombre, type: texto, required: true, constraints: 'inventado: «Detective <k> <sufijo de corrida>»'}
      - {name: grado, type: enum, required: true, allowed: ['9', '10', '11']}
      - {name: token, type: texto, required: false, constraints: 'secreto; nunca se imprime ni se escribe'}
      - {name: codigo, type: texto, required: false, constraints: '5 caracteres que devuelve /api/registro'}
      - {name: grupo, type: enum, required: false, allowed: [A, B], constraints: 'se lee de /api/admin/resumen, no de la base'}
      - {name: misiones, type: lista, required: false, constraints: 'el examen público que recibió, con ids opacos; vive en memoria'}
      - {name: fracciones, type: mapa, required: true, default: '{}', constraints: 'pregunta_id -> fracción que devolvió /api/responder; va al JSON (no es una respuesta)'}
      - {name: puntos_esperados, type: número, required: true, default: 0, constraints: 'suma de puntos de las preguntas que el guion decidió acertar'}
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
      - 'se obtiene solo de revision de /api/estado con la sala en resultados (BR2.3); nunca del banco ni de otro archivo'
      - 'vive en memoria durante la corrida; nunca se imprime ni se escribe en disco'
  - name: Medicion
    description: El archivo JSON de una corrida, con el esquema del contrato C3.
    owner: Prueba
    attributes:
      - {name: version_esquema, type: entero, required: true, constraints: 'siempre 1'}
      - {name: opcion, type: enum, required: true, allowed: [local, cloudflare, apps_script, github_pages]}
      - {name: url, type: texto, required: true}
      - {name: inicio, type: fecha-hora, required: true}
      - {name: fin, type: fecha-hora, required: true}
      - {name: todo_bien, type: booleano, required: true}
      - {name: comprobaciones, type: lista, required: true, constraints: 'una Comprobacion por fila: id, parte, pasa, detalle'}
      - {name: nfr, type: json, required: true, constraints: 'p95_responder_ms, p95_tablero_ms, sobrevive_reinicio, arranque_frio_ms, salas, participantes, peticiones, y además duracion_min y fracciones (lista de {k, pregunta_id, fraccion}), que son claves agregadas (C3 permite agregar)'}
    constraints:
      - 'se escribe en despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json'
      - 'nunca lleva la URL con clave, claves, tokens, nombres reales ni respuestas correctas'
relationships:
  - {from: Corrida, to: Comprobacion, cardinality: '1 a muchos'}
  - {from: Corrida, to: SalaDePrueba, cardinality: '1 a muchos', note: 'una de calibración y hasta 10 del reto; en local una sola sala cumple los dos papeles en orden'}
  - {from: SalaDePrueba, to: ParticipanteFicticio, cardinality: '1 a muchos'}
  - {from: ParticipanteFicticio, to: HuellaDePregunta, cardinality: 'muchos a muchos', note: 'cada participante ve una huella por pregunta'}
  - {from: HuellaDePregunta, to: ClavePorTexto, cardinality: '1 a 1'}
  - {from: Corrida, to: Medicion, cardinality: '1 a 1'}
```

## Resumen

- **Corrida** y **Comprobacion** ya existen en la prueba mínima de U1 (`Prueba`, `comprobar`); aquí
  ganan la opción, la duración, el reinicio, el conteo de peticiones y la marca `esencial`.
- **SalaDePrueba** y **ParticipanteFicticio** son el plan de carga de NFR1: 10 salas de tamaños
  desiguales que suman 40, con un papel por participante que reproduce los casos de `simulacro.py`.
- **HuellaDePregunta** y **ClavePorTexto** son la pieza nueva: permiten responder bien sin que la prueba
  conozca el banco, con la clave leída de `revision` después de publicar resultados.
- **Medicion** es el contrato C3; `fracciones` y `duracion_min` son claves agregadas para que U17 compare
  la calificación entre opciones (NFR11) sin mover `version_esquema`.
