# Entidades — U1 `u1-cloudflare-corte`

Las entidades que usa el corte delgado. Son las de `components.md` (domain-design/), recortadas a lo que
el corte necesita; las unidades U4 a U6 agregan lo demás sin cambiar estos nombres. Sin tecnología: cómo
se guardan lo decide el ADR de la opción (`construction/u1-cloudflare-corte/decisions.md`).

```yaml
entities:
  - name: Sala
    description: Una sala del reto; un docente la maneja con su clave.
    owner: Salas
    attributes:
      - {name: id_sala, type: identificador, required: true, unique: true}
      - {name: codigo, type: texto, required: true, unique: true, constraints: "3 a 8 letras o números en mayúsculas; lo genera el servidor y no cambia (R-12)"}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados], default: inscripcion}
      - {name: clave_huella, type: texto, required: true, constraints: "huella de la parte secreta de la clave; la clave nunca se guarda"}
      - {name: evento, type: texto, required: false, max: 80}
      - {name: duracion_min, type: número, required: true, default: "la del banco", min: 10, max: 240}
      - {name: reloj_global, type: booleano, required: true, default: true}
      - {name: retro, type: booleano, required: true, default: true}
      - {name: modo_sorpresa, type: booleano, required: true, default: true}
      - {name: creada, type: fecha-hora, required: true}
      - {name: abierta, type: fecha-hora, required: false, constraints: "se fija al pasar a abierto"}
      - {name: cerrada, type: fecha-hora, required: false, constraints: "la fija U5 al cerrar"}
  - name: Colegio
    description: Un colegio que la sala ofrece en la inscripción. En el corte solo existen provisionales.
    owner: CatalogoColegios
    attributes:
      - {name: id_colegio, type: identificador, required: true, unique: true}
      - {name: nombre, type: texto, required: true, max: 80}
      - {name: nombre_normalizado, type: texto, required: true, unique: true, constraints: "único en todo el servicio (FR10.3)"}
      - {name: provisional, type: booleano, required: true, default: true}
      - {name: creado, type: fecha-hora, required: true}
  - name: Participante
    description: Una persona o un equipo inscrito en una sala.
    owner: "Inscripcion (datos de inscripción) y Examen (estado, tiempos y puntos), ADR-007"
    attributes:
      - {name: id, type: entero, required: true, unique: true, constraints: "crece con el orden de inscripción; último desempate"}
      - {name: sala, type: referencia, references: Sala, required: true}
      - {name: codigo, type: texto, required: true, unique: true, constraints: "5 caracteres, único en todo el servicio; credencial para volver a entrar"}
      - {name: token, type: texto, required: true, unique: true, constraints: "secreto de sesión; nunca se registra ni se exporta"}
      - {name: semilla, type: texto, required: true, constraints: "secreta; da la variante, el orden y los ids opacos (ADR-006)"}
      - {name: nombre, type: texto, required: true, min: 3, max: 60}
      - {name: id_colegio, type: referencia, references: Colegio, required: true}
      - {name: grado, type: enum, required: true, allowed: ["9", "10", "11"]}
      - {name: integrantes, type: texto, required: false, max: 200}
      - {name: grupo, type: enum, required: true, allowed: [A, B]}
      - {name: estado, type: enum, required: true, allowed: [registrado, en_curso, finalizado, descalificado, no_inicio], default: registrado}
      - {name: creado, type: fecha-hora, required: true}
      - {name: inicio, type: fecha-hora, required: false, constraints: "hora del servidor al comenzar"}
      - {name: fin, type: fecha-hora, required: false}
      - {name: motivo_fin, type: enum, required: false, allowed: [entrega, tiempo, cierre, docente]}
      - {name: puntos, type: número, required: true, default: 0}
      - {name: bono, type: número, required: true, default: 0}
      - {name: total, type: número, required: true, default: 0}
      - {name: tiempo_usado, type: número, required: false, constraints: "segundos de inicio a fin"}
      - {name: tiempo_respuestas, type: número, required: false, constraints: "segundos de inicio a la última respuesta, con tope en la duración"}
      - {name: salidas, type: entero, required: true, default: 0}
    constraints:
      - "nombre normalizado + id_colegio + grado no se repite dentro de la sala (FR10.3, «repetido por clave»)"
  - name: Respuesta
    description: La respuesta de un participante a una pregunta; una sola por pregunta.
    owner: Examen
    attributes:
      - {name: participante, type: referencia, references: Participante, required: true}
      - {name: pregunta_id, type: texto, required: true, constraints: "id del banco, nunca el opaco"}
      - {name: variante, type: entero, required: true}
      - {name: respuesta, type: json, required: true, constraints: "con los ids del banco (FR6.2, FR9.2)"}
      - {name: fraccion, type: número, required: true, min: 0, max: 1}
      - {name: puntos, type: número, required: true}
      - {name: max_puntos, type: número, required: true}
      - {name: momento, type: fecha-hora, required: true, constraints: "hora del servidor"}
    constraints:
      - "participante + pregunta_id es único (FR2.4)"
  - name: Evento
    description: Una salida de pantalla del participante en curso.
    owner: Examen
    attributes:
      - {name: id_evento, type: identificador, required: true, unique: true}
      - {name: participante, type: referencia, references: Participante, required: true}
      - {name: tipo, type: enum, required: true, allowed: [salida]}
      - {name: momento, type: fecha-hora, required: true, constraints: "hora del servidor"}
  - name: Banco
    description: El banco de preguntas, leído de una copia sin cambios de 2_Aplicacion_Reto/banco_preguntas.json.
    owner: Banco
    attributes:
      - {name: version, type: texto, required: true, constraints: "huella del banco; la copia se rechaza si no coincide"}
      - {name: misiones, type: lista, required: true}
      - {name: puntos_totales, type: número, required: true, constraints: "exactamente 1.000"}
relationships:
  - {from: Sala, to: Participante, cardinality: "1 a muchos"}
  - {from: Sala, to: Colegio, cardinality: "muchos a muchos", note: "colegios que ofrece la sala"}
  - {from: Colegio, to: Participante, cardinality: "1 a muchos"}
  - {from: Participante, to: Respuesta, cardinality: "1 a muchos"}
  - {from: Participante, to: Evento, cardinality: "1 a muchos"}
```

## Resumen

- **Sala** y **Colegio** son nuevas frente a la versión local, que tiene una sola sala en su
  configuración y el colegio como texto libre.
- **Participante** y **Respuesta** guardan lo mismo que hoy, más la sala y el `id_colegio`.
- **Banco** no se guarda: es una copia del archivo generado, comprobada con su versión.
- **Evento** guarda las salidas de pantalla, como hoy.
- CopiaDeSala y el catálogo único llegan con U5 y U6.
