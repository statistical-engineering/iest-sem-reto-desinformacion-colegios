# Entidades — U4 `u4-cloudflare-reglas`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** `CicloDeSala` pasa a `CicloDelReto`; la
> clasificación es de todo el reto (todos los colegios) y suma `puesto_grado`; entran
> **ParticipanteParaOrden**, **EstadoReloj** y **ResultadoDeComenzar** para el reloj por colegio
> (ADR-011); `CamposDeInscripcion.colegio` es el `id_colegio` de la lista del docente (ADR-009); la fuente
> de **CasoDeRegla** suma las referencias de FR2.5, FR2.6 y ADR-011 (ADR-W7).

U4 no guarda nada: son las «calculadoras» de ADR-001, que reciben datos y la hora y devuelven datos
(contrato C4). Las entidades de abajo son las **formas de entrada y salida** que cruzan la frontera C4
entre `src/reglas/` y `src/reto.js`, con los nombres que ya usa U1 (`../u1-cloudflare-corte/functional-design/entities.md`)
y que U5 y U6 consumen sin cambiarlos. No hay almacenamiento: nada de aquí tiene tabla.

```yaml
entities:
  - name: PreguntaResuelta
    description: Una pregunta del banco ya resuelta a la variante del participante; la unica forma que Calificacion acepta.
    owner: Banco
    attributes:
      - {name: id, type: texto, required: true, constraints: 'id del banco'}
      - {name: tipo, type: enum, required: true, allowed: [opcion, multiple, clasificar, compartir, recordatorio, ordenar, construir, texto, estimar, numero]}
      - {name: puntos, type: número, required: true, min: 0}
      - {name: respuesta, type: json, required: false, constraints: 'clave de la variante; nunca sale de src/'}
      - {name: tolerancia, type: número, required: false}
      - {name: min, type: número, required: false}
      - {name: max, type: número, required: false}
      - {name: entero, type: booleano, required: false}
      - {name: opciones, type: lista, required: false}
      - {name: items, type: lista, required: false}
      - {name: publicaciones, type: lista, required: false}
      - {name: categorias, type: lista, required: false}
      - {name: partes, type: lista, required: false}
      - {name: requiere, type: texto, required: false}
      - {name: solo_grupo, type: enum, required: false, allowed: [A, B]}
  - name: RespuestaValidada
    description: Salida de validar_respuesta; la forma exacta por tipo que servidor.py guarda hoy.
    owner: Calificacion
    attributes:
      - {name: valor, type: json, required: true, constraints: 'opcion texto; multiple lista ordenada; clasificar, compartir y recordatorio objeto item a categoria; ordenar lista; construir objeto parte a opcion; texto cadena recortada; estimar y numero número'}
  - name: ResultadoDeCierre
    description: Lo que cerrar_intento devuelve para escribir la entrega; todos los tiempos se miden desde inicio, que es el arranque del colegio (FR2.6).
    owner: Calificacion
    attributes:
      - {name: fin, type: fecha-hora, required: true, constraints: 'min(ahora, inicio + duracion)'}
      - {name: tiempo_usado, type: número, required: true, constraints: 'fin - inicio, minimo 0'}
      - {name: tiempo_respuestas, type: número, required: true, constraints: 'desde inicio hasta la ultima respuesta; tope en la duración'}
      - {name: bono, type: número, required: true}
      - {name: total, type: número, required: true}
  - name: ParticipanteParaOrden
    description: Lo que ordenar recibe por cada participante finalizado del reto; reto.js lo arma desde la fila guardada, sin redondear.
    owner: Clasificacion
    attributes:
      - {name: id, type: entero, required: true, unique: true, constraints: 'orden de inscripcion (FR2.3)'}
      - {name: codigo, type: texto, required: true}
      - {name: nombre, type: texto, required: true}
      - {name: colegio, type: texto, required: true, constraints: 'nombre del colegio de la lista, como lo escribio el docente'}
      - {name: grado, type: enum, required: true, allowed: ['9', '10', '11']}
      - {name: puntos, type: número, required: true}
      - {name: bono, type: número, required: true}
      - {name: total, type: número, required: true}
      - {name: tiempo_usado, type: número, required: true, constraints: 'relativo al arranque del colegio'}
      - {name: tiempo_respuestas, type: número, required: true, constraints: 'relativo al arranque del colegio'}
      - {name: salidas, type: entero, required: true}
      - {name: motivo_fin, type: texto, required: false}
  - name: FilaClasificada
    description: Una fila del orden total del reto entre todos los colegios; misma forma que clasificacion() de servidor.py mas puesto_grado.
    owner: Clasificacion
    attributes:
      - {name: puesto, type: entero, required: true, min: 1, unique: true}
      - {name: puesto_grado, type: entero, required: false, min: 1, constraints: 'lo agrega por_grado; unico dentro del grado'}
      - {name: id, type: entero, required: true}
      - {name: codigo, type: texto, required: true}
      - {name: nombre, type: texto, required: true}
      - {name: colegio, type: texto, required: true}
      - {name: grado, type: texto, required: true}
      - {name: puntos, type: número, required: true, constraints: 'redondeado a 4'}
      - {name: bono, type: número, required: true, constraints: 'redondeado a 4'}
      - {name: total, type: número, required: true, constraints: 'redondeado a 4'}
      - {name: nota, type: número, required: true, constraints: '1 + 4 x puntos / 1.000, redondeado a 2, sin bono (FR2.5)'}
      - {name: tiempo_usado, type: número, required: true, constraints: 'redondeado a 1'}
      - {name: tiempo_respuestas, type: número, required: true, constraints: 'redondeado a 3'}
      - {name: salidas, type: entero, required: true}
      - {name: motivo_fin, type: texto, required: false}
  - name: Entrega
    description: Salida de hora_de_entrega; nada si el intento sigue.
    owner: CicloDelReto
    attributes:
      - {name: hora, type: fecha-hora, required: true}
      - {name: motivo, type: enum, required: true, allowed: [tiempo, cierre]}
  - name: EstadoReloj
    description: El reloj de un colegio visto en un instante; lo leen el panel, el tablero y el estudiante (ADR-011).
    owner: CicloDelReto
    attributes:
      - {name: estado, type: enum, required: true, allowed: [sin_arrancar, corriendo, vencido]}
      - {name: restante_seg, type: número, required: false, constraints: 'null si sin_arrancar; 0 si vencido; arranque + duracion - ahora si corriendo, sin redondear'}
  - name: ResultadoDeComenzar
    description: Lo que puede_comenzar decide cuando un equipo pulsa «Comenzar».
    owner: CicloDelReto
    attributes:
      - {name: resultado, type: enum, required: true, allowed: [comenzar, sin_cambio, rechazo]}
      - {name: inicio, type: fecha-hora, required: false, constraints: 'solo con comenzar; igual al arranque del colegio'}
      - {name: mensaje, type: texto, required: false, constraints: 'solo con rechazo; uno de los tres mensajes del contrato'}
  - name: CamposDeInscripcion
    description: Lo que llega de POST /api/registro ya limpio, listo para guardar.
    owner: LimpiezaEntrada
    attributes:
      - {name: nombre, type: texto, required: true, min: 3, max: 60}
      - {name: colegio, type: texto, required: true, constraints: 'id_colegio de la lista del docente (ADR-009)'}
      - {name: grado, type: enum, required: true, allowed: ['9', '10', '11']}
      - {name: integrantes, type: texto, required: false, max: 200, constraints: 'separados por coma y espacio (FR10.4)'}
      - {name: n_integrantes, type: entero, required: true, min: 0}
  - name: ResumenExperimento
    description: La salida de experimento() de hoy, de todo el reto; la version publica se reduce antes de resultados (ADR-W9).
    owner: Experimento
    attributes:
      - {name: n, type: entero, required: true}
      - {name: listo, type: booleano, required: true}
      - {name: total_posts, type: entero, required: false}
      - {name: clase, type: json, required: false}
      - {name: grupo_sin_recordatorio, type: json, required: false}
      - {name: grupo_con_recordatorio, type: json, required: false}
      - {name: multitud, type: json, required: false}
      - {name: por_publicacion, type: lista, required: false, constraints: 'con verdad y multitud_acierta solo en resultados'}
  - name: CasoDeRegla
    description: Una fila de despliegues/prueba_comun/casos_reglas.json (contrato C4).
    owner: Banco
    attributes:
      - {name: regla, type: enum, required: true, allowed: [Banco, Calificacion, Clasificacion, CicloDelReto, LimpiezaEntrada, Experimento]}
      - {name: funcion, type: texto, required: true}
      - {name: entrada, type: json, required: true, constraints: 'objeto con los nombres de C4'}
      - {name: salida_esperada, type: json, required: true}
      - {name: fuente, type: enum, required: true, allowed: [servidor.py, referencia FR2.5, referencia FR2.6, referencia ADR-011, referencia FR10.2, referencia FR10.4, referencia FR7.4, referencia ADR-004]}
      - {name: tolerancia, type: número, required: false, constraints: 'solo en divisiones del experimento (ADR-W8)'}
relationships:
  - {from: PreguntaResuelta, to: RespuestaValidada, cardinality: '1 a 1', note: 'validar_respuesta y fraccion reciben las dos'}
  - {from: ParticipanteParaOrden, to: FilaClasificada, cardinality: '1 a 1', note: 'ordenar y por_grado'}
  - {from: CasoDeRegla, to: PreguntaResuelta, cardinality: 'muchos a 1', note: 'los casos de Calificacion usan el banco de prueba, nunca el real'}
```

## Resumen

- Ninguna entidad se guarda: son contratos de llamada dentro del mismo servicio (C4).
- **FilaClasificada** y **ResumenExperimento** copian la forma exacta de `clasificacion()` y
  `experimento()` de `servidor.py`, porque `admin.js` y `tablero.html` las leen tal cual (FR4.1);
  `puesto_grado` es la única clave nueva (FR2.5).
- **EstadoReloj** y **ResultadoDeComenzar** son el reloj por colegio de ADR-011: el arranque lo guarda U5
  en la tabla `colegios`, y estas reglas solo lo leen como dato.
- **CasoDeRegla** es la única forma compartida entre opciones de hosting, y es solo datos
  (`project.md`, «Corrections», Q6-A).
- Las entidades guardadas (Reto, Colegio, Participante, Respuesta, Evento, Copia) son de U5 y U6.
