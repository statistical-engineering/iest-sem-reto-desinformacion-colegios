# Entidades — U3 `u3-local-fugas`

U3 no agrega ni cambia tablas de `2_Aplicacion_Reto/datos/reto.db`: `participantes`, `respuestas`,
`eventos` y `config` siguen iguales (FR6.2: «la base de datos y `respuestas.csv` siguen guardando los
identificadores del banco»). Lo que aparece son valores calculados en memoria para la respuesta HTTP.
Decisiones en `../decisions.md` (ADR-L1, ADR-L2); tomadas por el asistente con la potestad que dio el
humano (2026-10-25).

```yaml
entities:
  - name: Participante
    description: La fila de participantes de hoy; U3 solo usa su semilla, que ya existe.
    owner: 'servidor.py (registrar, participante_por_token); sin cambios'
    attributes:
      - {name: id, type: entero, required: true, unique: true}
      - {name: semilla, type: texto, required: true, constraints: 'secrets.token_hex(8), 16 caracteres hexadecimales; nunca sale al navegador; es la clave del HMAC (ADR-006, ADR-L1)'}
      - {name: grupo, type: enum, required: true, allowed: [A, B]}
  - name: Respuesta
    description: La fila de respuestas de hoy; sigue con ids del banco.
    owner: 'servidor.py (responder); sin cambios'
    attributes:
      - {name: participante_id, type: entero, required: true}
      - {name: pregunta_id, type: texto, required: true}
      - {name: respuesta, type: json, required: true, constraints: 'con los ids del banco, nunca opacos (FR6.2, FR9.2)'}
      - {name: fraccion, type: número, required: true}
      - {name: puntos, type: número, required: true}
    constraints:
      - 'participante_id + pregunta_id es único (FR2.4)'
  - name: IdOpaco
    description: El id que ve el navegador para una opción, ítem, publicación o parte; se calcula, no se guarda.
    owner: 'servidor.py (opaco_de, opacos_de); nuevo'
    attributes:
      - {name: semilla, type: texto, required: true, constraints: 'la del participante'}
      - {name: ambito, type: texto, required: true, constraints: 'pregunta_id para opciones; m1_posts para ítems y publicaciones de la misión 1 y pregunta_id en las demás; pregunta_id|partes para partes; pregunta_id|parte_id para las opciones de una parte'}
      - {name: id_banco, type: texto, required: true}
      - {name: valor, type: texto, required: true, constraints: 'o + 11 caracteres base32 en minúsculas de HMAC-SHA256(semilla, ambito|id_banco); 16 si dos del mismo grupo chocan'}
    constraints:
      - 'dentro de un grupo (misma semilla y ámbito), valor es único'
      - 'la función es la misma mientras haya un reto en curso: no se despliega con un reto en curso (project.md, Forbidden)'
  - name: PreguntaPublica
    description: Lo que ve el navegador de una pregunta; igual que hoy, con ids opacos en sus listas.
    owner: 'servidor.py (version_publica + opacar_salida); tocada'
    attributes:
      - {name: id, type: texto, required: true, constraints: 'id de la pregunta del banco, público como hoy (no es opción ni ítem)'}
      - {name: opciones, type: lista, required: false, constraints: '[{id opaco, texto}] en el orden de rng_para de hoy'}
      - {name: items, type: lista, required: false, constraints: 'ids opacos; orden de hoy'}
      - {name: publicaciones, type: lista, required: false, constraints: 'ids opacos con ámbito m1_posts; orden de hoy'}
      - {name: partes, type: lista, required: false, constraints: '[{id opaco, etiqueta, opciones con ids opacos}]'}
      - {name: categorias, type: lista, required: false, constraints: 'ids del banco (V, F, S, N, IA…): etiquetas sin correlación con la clave'}
    constraints:
      - 'nunca trae respuesta, explicacion ni tolerancia (sin cambios)'
  - name: ExperimentoPublico
    description: Lo que /api/publico entrega del experimento según el estado de la sala.
    owner: 'servidor.py (publico + sin_veredicto); tocada'
    attributes:
      - {name: n, type: entero, required: true}
      - {name: listo, type: booleano, required: true}
      - {name: resto, type: json, required: false, constraints: 'clase, grupos, multitud y por_publicacion (con verdad y multitud_acierta) solo en resultados (ADR-L2)'}
relationships:
  - {from: Participante, to: IdOpaco, cardinality: '1 a muchos', note: 'uno por id del banco visible, calculado con su semilla'}
  - {from: Participante, to: Respuesta, cardinality: '1 a muchos'}
  - {from: PreguntaPublica, to: IdOpaco, cardinality: '1 a muchos'}
```

## Resumen

- Nada nuevo en la base: **IdOpaco** es un valor calculado por petición a partir de la semilla que ya
  existe (ADR-006, alternativa A: «sin datos nuevos que guardar, respaldar ni borrar»).
- **PreguntaPublica** cambia solo en los ids de sus listas; el orden, las claves y los textos son los de
  hoy, así las pantallas no cambian.
- **ExperimentoPublico** se recorta en «cerrado» y es el de hoy en «resultados».
