# Entidades — U5 `u5-cloudflare-salas`

Las entidades guardadas de la opción, completas. Son las de U1
(`../../u1-cloudflare-corte/functional-design/entities.md`) con lo que U5 agrega, marcado con **(U5)**. Cómo se
guardan lo fijan ADR-W1 (un Durable Object con SQLite) y ADR-W10 (migraciones). CopiaDeSala llega con U6.

```yaml
entities:
  - name: Sala
    description: Una sala del reto; un docente la maneja con su clave y el semillero la crea, regenera y borra.
    owner: Salas
    attributes:
      - {name: id_sala, type: identificador, required: true, unique: true}
      - {name: codigo, type: texto, required: true, unique: true, constraints: '4 letras del alfabeto sin 0, O, 1 ni I; lo genera el servidor y no cambia (R-12)'}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados], default: inscripcion}
      - {name: clave_huella, type: texto, required: true, constraints: 'SHA-256 del secreto; regenerar la reemplaza (U5)'}
      - {name: evento, type: texto, required: false, max: 80, default: 'Sala de verificación'}
      - {name: duracion_min, type: número, required: true, default: 'la del banco', min: 10, max: 240}
      - {name: reloj_global, type: booleano, required: true, default: true, constraints: 'solo cambia en inscripcion'}
      - {name: retro, type: booleano, required: true, default: true}
      - {name: modo_sorpresa, type: booleano, required: true, default: true}
      - {name: creada, type: fecha-hora, required: true}
      - {name: abierta, type: fecha-hora, required: false, constraints: 'se fija la primera vez que pasa a abierto'}
      - {name: cerrada, type: fecha-hora, required: false, constraints: 'se fija la primera vez que pasa a cerrado (U5); es el cierre de hora_de_entrega'}
  - name: Colegio
    description: Un colegio del catalogo unico del semillero; los provisionales los agrega un docente el dia del reto.
    owner: CatalogoColegios
    attributes:
      - {name: id_colegio, type: texto, required: true, unique: true, constraints: 'c + 8 caracteres del alfabeto; estable entre retos y años'}
      - {name: nombre, type: texto, required: true, min: 3, max: 80}
      - {name: nombre_normalizado, type: texto, required: true, unique: true, constraints: 'unico en todo el servicio (FR10.3)'}
      - {name: provisional, type: booleano, required: true, default: true, constraints: 'el semillero lo confirma (false) o lo une'}
      - {name: unido_a, type: referencia, references: Colegio, required: false, constraints: 'un solo salto: apunta a un colegio ni provisional ni unido (U5, ADR-W13)'}
      - {name: creado, type: fecha-hora, required: true}
  - name: Participante
    description: Una persona o un equipo inscrito en una sala; Inscripcion escribe quien es y Examen lo que pasa en el reto (ADR-007).
    owner: 'Inscripcion (datos de inscripción) y Examen (estado, tiempos y puntos)'
    attributes:
      - {name: id, type: entero, required: true, unique: true, constraints: 'crece con el orden de inscripción en todo el servicio; último desempate'}
      - {name: sala, type: referencia, references: Sala, required: true}
      - {name: codigo, type: texto, required: true, unique: true, constraints: '5 caracteres, único en todo el servicio'}
      - {name: token, type: texto, required: true, unique: true, constraints: 'secreto de sesión; nunca se registra ni se exporta'}
      - {name: semilla, type: texto, required: true, constraints: 'secreta (ADR-006)'}
      - {name: nombre, type: texto, required: true, min: 3, max: 60, constraints: 'normalizado con FR10.2 (U5)'}
      - {name: id_colegio, type: referencia, references: Colegio, required: true, constraints: 'el elegido al inscribirse; se muestra el definitivo (ADR-W13)'}
      - {name: grado, type: enum, required: true, allowed: ['9', '10', '11']}
      - {name: integrantes, type: texto, required: false, max: 200, constraints: 'separados por coma y espacio (FR10.4, U5)'}
      - {name: grupo, type: enum, required: true, allowed: [A, B]}
      - {name: estado, type: enum, required: true, allowed: [registrado, en_curso, finalizado, descalificado, no_inicio], default: registrado}
      - {name: creado, type: fecha-hora, required: true}
      - {name: inicio, type: fecha-hora, required: false}
      - {name: fin, type: fecha-hora, required: false}
      - {name: motivo_fin, type: texto, required: false, constraints: 'entrega, tiempo, cierre, docente o «descalificado (antes: <estado>)», como hoy'}
      - {name: puntos, type: número, required: true, default: 0}
      - {name: bono, type: número, required: true, default: 0}
      - {name: total, type: número, required: true, default: 0}
      - {name: tiempo_usado, type: número, required: false}
      - {name: tiempo_respuestas, type: número, required: false}
      - {name: salidas, type: entero, required: true, default: 0}
    constraints:
      - 'nombre en minúsculas + id_colegio + grado no se repite dentro de la sala (FR10.3)'
  - name: Respuesta
    description: La respuesta de un participante a una pregunta; una sola por pregunta; de los 10 tipos (U5).
    owner: Examen
    attributes:
      - {name: participante, type: referencia, references: Participante, required: true}
      - {name: pregunta_id, type: texto, required: true, constraints: 'id del banco'}
      - {name: variante, type: entero, required: true}
      - {name: respuesta, type: json, required: true, constraints: 'ids del banco, forma de RespuestaValidada (U4)'}
      - {name: fraccion, type: número, required: true, min: 0, max: 1}
      - {name: puntos, type: número, required: true}
      - {name: max_puntos, type: número, required: true}
      - {name: momento, type: fecha-hora, required: true}
    constraints:
      - 'participante + pregunta_id es único (FR2.4)'
  - name: Evento
    description: Una salida de pantalla del participante en curso.
    owner: Examen
    attributes:
      - {name: id_evento, type: identificador, required: true, unique: true}
      - {name: participante, type: referencia, references: Participante, required: true}
      - {name: tipo, type: enum, required: true, allowed: [salida]}
      - {name: momento, type: fecha-hora, required: true}
  - name: Esquema
    description: La version del esquema SQLite del objeto (ADR-W10).
    owner: Persistencia
    attributes:
      - {name: user_version, type: entero, required: true, constraints: '1 en U1; 2 en U5 (unido_a); U6 agrega la 3'}
relationships:
  - {from: Sala, to: Participante, cardinality: '1 a muchos'}
  - {from: Sala, to: Colegio, cardinality: 'muchos a muchos', note: 'colegios que ofrece la sala (sala_colegios)'}
  - {from: Colegio, to: Colegio, cardinality: 'muchos a 1', note: 'unido_a, un solo salto'}
  - {from: Colegio, to: Participante, cardinality: '1 a muchos'}
  - {from: Participante, to: Respuesta, cardinality: '1 a muchos'}
  - {from: Participante, to: Evento, cardinality: '1 a muchos'}
```

## Resumen

- **Sala** gana `cerrada` en uso (U1 solo la declaraba) y la clave regenerable.
- **Colegio** gana `unido_a` (migración a la versión 2 del esquema).
- **Participante** guarda nombre e integrantes ya normalizados (FR10.2, FR10.4); `n_integrantes` no se
  guarda, lo cuenta U6 al exportar.
- **Respuesta** acepta los 10 tipos con la forma de U4.
- Nada se borra en U5 salvo con «Eliminar» (participante) y «Borrar la sala» (semillero).
