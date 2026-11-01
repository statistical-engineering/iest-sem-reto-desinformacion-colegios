# Entidades — U5 `u5-cloudflare-salas` (reto, colegios y relojes)

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** **Sala** pasa a **Reto**, una fila única sin
> clave ni `reloj_global` (ADR-010, ADR-011); **Colegio** gana `arranque` y pierde `provisional` y
> `unido_a` (ADR-009); **Participante** pierde `sala`; **Esquema** cambia de versiones (ADR-W10, ADR-W19).
> Respuesta y Evento no cambian. La Copia es de U6.

Las entidades guardadas de la opción, completas, en la versión 2 del esquema. Sustituyen a las de U1
(`../../u1-cloudflare-corte/functional-design/entities.md`) en lo que es de varias salas. Cómo se guardan
lo fijan ADR-W1 (un Durable Object con SQLite), ADR-W10 (migraciones) y ADR-W19 (migración desde el corte).
Los nombres siguen `components.md` (domain-design/, catálogo YAML).

```yaml
entities:
  - name: Reto
    description: El unico reto del servicio; una fila que guarda la configuracion y el estado (FR11.1).
    owner: CicloDelReto
    attributes:
      - {name: id, type: entero, required: true, unique: true, constraints: 'siempre 1 (CHECK id = 1)'}
      - {name: codigo, type: texto, required: true, constraints: 'codigo de sala que escriben los estudiantes; 3 a 8 letras o numeros; lo fija el docente en config; nace con 4 letras al azar del ALFABETO'}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados], default: inscripcion}
      - {name: evento, type: texto, required: true, max: 80, default: 'Reto'}
      - {name: duracion_min, type: número, required: true, default: 'la del banco', min: 10, max: 240, constraints: 'solo cambia en inscripcion; el minimo baja solo con DURACION_MINIMA_MIN en wrangler dev (D9)'}
      - {name: retro, type: booleano, required: true, default: true}
      - {name: modo_sorpresa, type: booleano, required: true, default: true}
      - {name: abierto_en, type: fecha-hora, required: false, constraints: 'se fija la primera vez que pasa a abierto'}
      - {name: cerrado_en, type: fecha-hora, required: false, constraints: 'se fija la primera vez que pasa a cerrado; es el cierre de hora_de_entrega'}
  - name: Colegio
    description: Un colegio de la lista que carga el docente; cada uno tiene su reloj (ADR-009, ADR-011).
    owner: Colegios
    attributes:
      - {name: id_colegio, type: texto, required: true, unique: true, constraints: 'c + 8 caracteres del ALFABETO; lo genera el servidor; no se conserva entre retos'}
      - {name: nombre, type: texto, required: true, min: 3, max: 80, constraints: 'como lo escribio el docente, limpio con FR10.2'}
      - {name: nombre_normalizado, type: texto, required: true, unique: true, constraints: 'normalizar_nombre_colegio de U4; no se repite en la lista'}
      - {name: arranque, type: fecha-hora, required: false, constraints: 'null hasta que arranca; se fija una vez y no se deshace'}
      - {name: creado, type: fecha-hora, required: true}
  - name: Participante
    description: Una persona o un equipo inscrito; Inscripcion escribe quien es y Examen lo que pasa en el reto (ADR-007).
    owner: 'Inscripcion (datos de inscripción) y Examen (estado, tiempos y puntos)'
    attributes:
      - {name: id, type: entero, required: true, unique: true, constraints: 'crece con el orden de inscripción; último desempate'}
      - {name: codigo, type: texto, required: true, unique: true, constraints: '5 caracteres'}
      - {name: token, type: texto, required: true, unique: true, constraints: 'secreto de sesión; nunca se registra ni se exporta'}
      - {name: semilla, type: texto, required: true, constraints: 'secreta (ADR-006)'}
      - {name: nombre, type: texto, required: true, min: 3, max: 60, constraints: 'normalizado con FR10.2'}
      - {name: id_colegio, type: referencia, references: Colegio, required: true}
      - {name: grado, type: enum, required: true, allowed: ['9', '10', '11']}
      - {name: integrantes, type: texto, required: false, max: 200, constraints: 'separados por coma y espacio (FR10.4)'}
      - {name: grupo, type: enum, required: true, allowed: [A, B]}
      - {name: estado, type: enum, required: true, allowed: [registrado, en_curso, finalizado, descalificado, no_inicio], default: registrado}
      - {name: creado, type: fecha-hora, required: true}
      - {name: inicio, type: fecha-hora, required: false, constraints: 'igual al arranque de su colegio, aunque pulse Comenzar despues (FR3.1)'}
      - {name: fin, type: fecha-hora, required: false}
      - {name: motivo_fin, type: texto, required: false, constraints: 'entrega, tiempo, cierre, docente o «descalificado (antes: <estado>)», como hoy'}
      - {name: puntos, type: número, required: true, default: 0}
      - {name: bono, type: número, required: true, default: 0}
      - {name: total, type: número, required: true, default: 0}
      - {name: tiempo_usado, type: número, required: false}
      - {name: tiempo_respuestas, type: número, required: false}
      - {name: salidas, type: entero, required: true, default: 0}
    constraints:
      - 'nombre en minúsculas + id_colegio + grado no se repite (FR10.3, índice único participante_unico)'
  - name: Respuesta
    description: La respuesta de un participante a una pregunta; una sola por pregunta; de los 10 tipos.
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
      - {name: user_version, type: entero, required: true, constraints: '0 en el corte desplegado; 1 = esquema de U1; 2 = una sala (U5, ADR-W19); 3 = copias (U6)'}
relationships:
  - {from: Colegio, to: Participante, cardinality: '1 a muchos'}
  - {from: Participante, to: Respuesta, cardinality: '1 a muchos'}
  - {from: Participante, to: Evento, cardinality: '1 a muchos'}
```

## Tablas (versión 2)

| Tabla | Columnas | Índices y restricciones |
|---|---|---|
| `reto` | `id`, `codigo`, `estado`, `evento`, `duracion_min`, `retro`, `modo_sorpresa`, `abierto_en`, `cerrado_en` | `CHECK (id = 1)`; `CHECK (estado IN (...))` |
| `colegios` | `id_colegio`, `nombre`, `nombre_normalizado`, `arranque`, `creado` | `nombre_normalizado` único |
| `participantes` | las de U1 sin `id_sala` | `participante_unico` (`lower(nombre)`, `id_colegio`, `grado`); `participantes_estado` (`estado`); `participantes_colegio` (`id_colegio`) |
| `respuestas`, `eventos` | iguales a U1 | iguales a U1 |
| `v1_*` | las seis tablas del corte, apartadas (ADR-W19) | sin índices propios; las borra la versión 3 (U6) |

## Resumen

- **Reto** es una fila: no hay salas, ni clave guardada (la clave docente es el secreto `CLAVE_DOCENTE`,
  nunca una columna), ni `reloj_global` (en el JSON sale fijo, D1).
- **Colegio** es la lista del docente y lleva el reloj: `arranque` es la única hora de inicio de sus
  equipos (FR3.1, FR2.6).
- **Participante** guarda nombre e integrantes ya normalizados (FR10.2, FR10.4); `n_integrantes` no se
  guarda, lo cuenta U6 al exportar.
- Nada se borra en U5 salvo con «Eliminar» (participante) y «Quitar» (colegio sin equipos); «Reiniciar»
  es de U6.
