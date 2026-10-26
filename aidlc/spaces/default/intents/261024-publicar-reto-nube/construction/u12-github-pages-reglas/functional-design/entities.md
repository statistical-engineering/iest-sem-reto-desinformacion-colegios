# Entidades — U12 `u12-github-pages-reglas`

U12 son las «calculadoras» de ADR-001 para la opción GitHub Pages, en `despliegues/github-pages/src/reglas.py`
(Python, `../../u11-github-pages-corte/decisions.md`, ADR-G3). No guardan nada: reciben datos y la hora y
devuelven datos. Por eso sus entidades son **objetos de valor** que entran y salen de las funciones, con la
forma del contrato C4 (`contract-summary.md`). Las entidades guardadas (Sala, Participante, Respuesta…)
son las de U11 y no cambian.

```yaml
entities:
  - name: PreguntaResuelta
    description: Una pregunta del banco con la variante que le toca a un participante ya aplicada; es lo que reciben Calificacion y examen_publico.
    owner: Banco
    attributes:
      - {name: id, type: texto, required: true}
      - {name: tipo, type: enum, required: true, allowed: [opcion, multiple, verdadero_falso, numero, orden, emparejar, clasificar, escala, partes, abierta], constraints: "los 10 tipos de hoy; los nombres exactos salen de banco_preguntas.json al construir"}
      - {name: puntos, type: número, required: true, min: 0}
      - {name: variante, type: entero, required: true}
      - {name: respuesta, type: json, required: true, constraints: "la respuesta correcta de la variante; nunca sale de reglas.py hacia el navegador"}
      - {name: opciones, type: lista, required: false, constraints: "ids del banco; el orden público lo da examen_publico"}
      - {name: items, type: lista, required: false}
      - {name: partes, type: lista, required: false}
      - {name: tolerancia, type: número, required: false}
      - {name: requiere, type: texto, required: false}
      - {name: solo_grupo, type: enum, required: false, allowed: [A, B]}
  - name: RespuestaNormalizada
    description: La respuesta de un estudiante ya validada por tipo y traducida a ids del banco; es lo que se guarda en Respuesta.respuesta.
    owner: Calificacion
    attributes:
      - {name: valor, type: json, required: true, constraints: "texto, número, id, lista de ids o pares, según el tipo"}
  - name: Calificacion
    description: Resultado de calificar una respuesta.
    owner: Calificacion
    attributes:
      - {name: fraccion, type: número, required: true, min: 0, max: 1}
      - {name: puntos, type: número, required: true}
      - {name: max_puntos, type: número, required: true}
  - name: ParticipanteFinalizado
    description: Lo que Clasificacion necesita de cada participante finalizado de una sala.
    owner: Clasificacion
    attributes:
      - {name: id, type: entero, required: true, constraints: "último desempate (orden de inscripción)"}
      - {name: total, type: número, required: true}
      - {name: puntos, type: número, required: true}
      - {name: tiempo_respuestas, type: número, required: true, constraints: "segundos, con tope en la duración"}
      - {name: fin, type: fecha-hora, required: true}
      - {name: nombre, type: texto, required: true}
      - {name: colegio, type: texto, required: true, constraints: "nombre definitivo del catálogo (C-11)"}
      - {name: grado, type: texto, required: true}
      - {name: estado, type: enum, required: true, allowed: [finalizado, descalificado]}
  - name: Puesto
    description: Una fila del ranking de la sala.
    owner: Clasificacion
    attributes:
      - {name: puesto, type: entero, required: true, min: 1, constraints: "sin repetir (NFR11)"}
      - {name: id, type: entero, required: true}
      - {name: nota, type: número, required: true, constraints: "sobre 5, con la fórmula de hoy"}
  - name: HoraDeEntrega
    description: Lo que devuelve CicloDeSala.hora_de_entrega cuando un intento ya venció.
    owner: CicloDeSala
    attributes:
      - {name: hora, type: fecha-hora, required: true, constraints: "la menor entre ahora, inicio + duración y el cierre de la sala"}
      - {name: motivo, type: enum, required: true, allowed: [tiempo, cierre]}
  - name: CasoDeRegla
    description: Una fila de despliegues/prueba_comun/casos_reglas.json, copiada a pruebas/casos_reglas.json de esta opción (contrato C4).
    owner: Banco
    attributes:
      - {name: regla, type: enum, required: true, allowed: [Banco, Calificacion, Clasificacion, CicloDeSala, LimpiezaEntrada, Experimento]}
      - {name: funcion, type: texto, required: true}
      - {name: entrada, type: json, required: true, constraints: "objeto con los nombres de C4"}
      - {name: salida_esperada, type: json, required: true, constraints: "calculada con la versión local, nunca escrita a mano; los casos de Calificacion usan un banco de prueba propio, sin respuestas del banco real"}
relationships:
  - {from: PreguntaResuelta, to: Calificacion, cardinality: "1 a muchos", note: "una pregunta se califica una vez por participante"}
  - {from: ParticipanteFinalizado, to: Puesto, cardinality: "1 a 1"}
```

## Resumen

- Nada de U12 se guarda en SQLite: U13 y U14 convierten filas en estos objetos, llaman a las reglas y
  guardan lo que devuelven.
- `PreguntaResuelta` lleva la respuesta correcta porque la calificación la necesita; `examen_publico` la
  quita antes de que nada salga al navegador (NFR8).
- `CasoDeRegla` es el puente con las otras opciones: la misma tabla de casos, copiada (nunca código,
  `project.md` «Corrections»).
