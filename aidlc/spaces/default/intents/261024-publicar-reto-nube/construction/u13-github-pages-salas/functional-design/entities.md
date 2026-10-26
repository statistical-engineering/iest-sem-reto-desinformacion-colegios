# Entidades — U13 `u13-github-pages-salas`

U13 completa Salas, Acceso, CatalogoColegios, Inscripcion y Examen en la opción GitHub Pages (API en
PythonAnywhere, `../../u11-github-pages-corte/decisions.md`). Las entidades son las de U11 con los
atributos que el corte dejó fuera; aquí se listan completas para que el esquema SQLite de `servicio.py`
tenga una sola fuente. Cómo se guardan lo fija el ADR-G5 (un archivo SQLite con `UNIQUE`).

```yaml
entities:
  - name: Sala
    description: Una sala del reto con su estado, su clave, su configuración y sus colegios.
    owner: Salas
    attributes:
      - {name: id_sala, type: identificador, required: true, unique: true}
      - {name: codigo, type: texto, required: true, unique: true, constraints: "4 caracteres del ALFABETO de hoy; lo genera el servidor y no cambia (R-12)"}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados], default: inscripcion}
      - {name: clave_huella, type: texto, required: true, constraints: "SHA-256 del secreto vigente; cambia al regenerar (ADR-003)"}
      - {name: evento, type: texto, required: false, max: 80}
      - {name: duracion_min, type: número, required: true, min: 10, max: 240, constraints: "solo cambia en inscripción (R-12, revisión 05 de Domain Design)"}
      - {name: reloj_global, type: booleano, required: true, default: true, constraints: "solo cambia en inscripción"}
      - {name: retro, type: booleano, required: true, default: true}
      - {name: modo_sorpresa, type: booleano, required: true, default: true}
      - {name: creada, type: fecha-hora, required: true}
      - {name: abierta, type: fecha-hora, required: false}
      - {name: cerrada, type: fecha-hora, required: false, constraints: "hora del servidor al pasar a cerrado; es el «cierre» de hora_de_entrega"}
  - name: Colegio
    description: Un colegio del catálogo único del semillero (ADR-002).
    owner: CatalogoColegios
    attributes:
      - {name: id_colegio, type: identificador, required: true, unique: true, constraints: "estable entre retos y años"}
      - {name: nombre, type: texto, required: true, max: 80, constraints: "como lo escribió el semillero o el docente; es lo que se muestra"}
      - {name: nombre_normalizado, type: texto, required: true, unique: true, constraints: "LimpiezaEntrada.nombre_normalizado_colegio (BR13.4 de U12)"}
      - {name: provisional, type: booleano, required: true, default: false, constraints: "true si lo agregó un docente el día del reto"}
      - {name: unido_a, type: referencia, references: Colegio, required: false, constraints: "si el semillero unió este provisional con uno existente; desde entonces el definitivo es unido_a"}
      - {name: creado, type: fecha-hora, required: true}
  - name: SalaColegio
    description: Qué colegios ofrece una sala en su inscripción.
    owner: Salas
    attributes:
      - {name: sala, type: referencia, references: Sala, required: true}
      - {name: id_colegio, type: referencia, references: Colegio, required: true}
    constraints:
      - "sala + id_colegio es único"
  - name: Participante
    description: Igual que en U11; U13 agrega n_integrantes y las acciones del docente.
    owner: "Inscripcion (datos de la persona) y Examen (estado y datos del reto), ADR-007"
    attributes:
      - {name: id, type: entero, required: true, unique: true}
      - {name: sala, type: referencia, references: Sala, required: true}
      - {name: codigo, type: texto, required: true, unique: true}
      - {name: token, type: texto, required: true, unique: true}
      - {name: semilla, type: texto, required: true}
      - {name: nombre, type: texto, required: true, min: 3, max: 60}
      - {name: id_colegio, type: referencia, references: Colegio, required: true}
      - {name: grado, type: enum, required: true, allowed: ["9", "10", "11"]}
      - {name: integrantes, type: texto, required: false, max: 200, constraints: "normalizados con «, » (FR10.4)"}
      - {name: n_integrantes, type: entero, required: true, default: 0}
      - {name: grupo, type: enum, required: true, allowed: [A, B]}
      - {name: estado, type: enum, required: true, allowed: [registrado, en_curso, finalizado, descalificado, no_inicio], default: registrado}
      - {name: creado, type: fecha-hora, required: true}
      - {name: inicio, type: fecha-hora, required: false}
      - {name: fin, type: fecha-hora, required: false}
      - {name: motivo_fin, type: enum, required: false, allowed: [entrega, tiempo, cierre, docente]}
      - {name: puntos, type: número, required: true, default: 0}
      - {name: bono, type: número, required: true, default: 0}
      - {name: total, type: número, required: true, default: 0}
      - {name: tiempo_usado, type: número, required: false}
      - {name: tiempo_respuestas, type: número, required: false}
      - {name: salidas, type: entero, required: true, default: 0}
    constraints:
      - "sala + nombre normalizado + id_colegio + grado es único (FR10.3)"
  - name: Respuesta
    description: Igual que en U11; con U12 acepta los 10 tipos.
    owner: Examen
    attributes:
      - {name: participante, type: referencia, references: Participante, required: true}
      - {name: pregunta_id, type: texto, required: true}
      - {name: variante, type: entero, required: true}
      - {name: respuesta, type: json, required: true, constraints: "ids del banco"}
      - {name: fraccion, type: número, required: true, min: 0, max: 1}
      - {name: puntos, type: número, required: true}
      - {name: max_puntos, type: número, required: true}
      - {name: momento, type: fecha-hora, required: true}
    constraints:
      - "participante + pregunta_id es único (FR2.4)"
  - name: Evento
    description: Igual que en U11.
    owner: Examen
    attributes:
      - {name: id_evento, type: identificador, required: true, unique: true}
      - {name: participante, type: referencia, references: Participante, required: true}
      - {name: tipo, type: enum, required: true, allowed: [salida]}
      - {name: momento, type: fecha-hora, required: true}
relationships:
  - {from: Sala, to: SalaColegio, cardinality: "1 a muchos"}
  - {from: Colegio, to: SalaColegio, cardinality: "1 a muchos"}
  - {from: Colegio, to: Colegio, cardinality: "muchos a 1", note: "unido_a: un provisional apunta a su definitivo"}
  - {from: Sala, to: Participante, cardinality: "1 a muchos"}
  - {from: Colegio, to: Participante, cardinality: "1 a muchos"}
  - {from: Participante, to: Respuesta, cardinality: "1 a muchos"}
  - {from: Participante, to: Evento, cardinality: "1 a muchos"}
```

## Resumen

- **Colegio** gana `unido_a` y deja de ser solo provisional: ahora existe el catálogo del semillero.
- **SalaColegio** se hace explícita (en U11 vivía como tabla `sala_colegios` sin entidad).
- **Sala** gana `cerrada`, que es el «cierre» de `hora_de_entrega` (ADR-004).
- **Participante** gana `n_integrantes` (FR10.4) y las acciones del docente cambian su `estado`.
- CopiaDeSala llega con U14.
