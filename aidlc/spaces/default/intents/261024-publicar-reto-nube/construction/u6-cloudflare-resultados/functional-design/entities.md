# Entidades — U6 `u6-cloudflare-resultados`

Lo que U6 agrega a las entidades de U5 (`../../u5-cloudflare-salas/functional-design/entities.md`): la
copia de una sala, el paquete de datos y las formas de exportación. Las decisiones de formato están en
`../decisions.md` (ADR-W14 a ADR-W18).

```yaml
entities:
  - name: CopiaDeSala
    description: Una copia completa de los datos de una sala, hecha al reiniciar; se conserva hasta que el semillero borra la sala.
    owner: Exportacion
    attributes:
      - {name: id_copia, type: texto, required: true, unique: true, constraints: 'k + 8 caracteres del alfabeto'}
      - {name: sala, type: referencia, references: Sala, required: true}
      - {name: creada, type: fecha-hora, required: true}
      - {name: nombre_archivo, type: texto, required: true, constraints: 'copia_<sala>_<AAAA-MM-DD_HHMM>.sql'}
      - {name: bytes, type: entero, required: true}
      - {name: sha256, type: texto, required: true, constraints: 'huella del contenido; se comprueba al descargar'}
      - {name: contenido, type: texto, required: true, constraints: 'guion SQL (ADR-W14) guardado en trozos de 512 KiB (ADR-W17); sin token, semilla, codigo personal ni clave_huella'}
  - name: Paquete
    description: El .zip que el docente descarga; no se guarda, se arma en cada descarga.
    owner: Exportacion
    attributes:
      - {name: nombre, type: texto, required: true, constraints: 'AAAA-MM-DD_<sala>_reto.zip, fecha de apertura en hora de Colombia (ADR-W18)'}
      - {name: participantes_csv, type: texto, required: true}
      - {name: respuestas_csv, type: texto, required: true}
      - {name: eventos_csv, type: texto, required: true}
      - {name: colegios_csv, type: texto, required: true}
      - {name: copia_sql, type: texto, required: true, constraints: 'misma forma que CopiaDeSala.contenido'}
      - {name: metadatos_json, type: json, required: true}
  - name: Metadatos
    description: metadatos.json del paquete (FR9.1, C5).
    owner: Exportacion
    attributes:
      - {name: inicio, type: texto, required: false, constraints: 'ISO 8601 con -05:00 de la apertura; null si no se abrio'}
      - {name: fin, type: texto, required: false, constraints: 'ISO 8601 del cierre; null si no se cerro'}
      - {name: sala, type: texto, required: true}
      - {name: evento, type: texto, required: true}
      - {name: duracion_min, type: número, required: true}
      - {name: participantes, type: entero, required: true, constraints: 'filas de participantes.csv'}
      - {name: version_banco, type: json, required: true, constraints: 'objeto con version (la de Python) y sha256 (la huella de copiar.sh)'}
      - {name: version_app, type: json, required: true, constraints: 'objeto con commit y fecha, de src/version.json'}
      - {name: version_esquema, type: entero, required: true}
      - {name: generado, type: texto, required: true, constraints: 'ISO 8601 del momento de la descarga'}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados]}
  - name: VistaResultados
    description: Lo que /api/estado agrega al participante finalizado con la sala en resultados.
    owner: Resultados
    attributes:
      - {name: puesto, type: entero, required: true}
      - {name: nota, type: número, required: true}
      - {name: revision, type: json, required: true, constraints: 'por pregunta visible, respuesta con ids opacos y explicacion (U4 BR1.2)'}
  - name: VistaTablero
    description: Lo que /api/publico?sala= agrega a lo de U1.
    owner: Resultados
    attributes:
      - {name: ranking, type: lista, required: false, constraints: 'top 10 con puesto, nombre, colegio, grado, total, puntos; solo en resultados o con modo sorpresa apagado'}
      - {name: experimento, type: json, required: false, constraints: 'experimento_publico (U4 BR6.2); en cerrado solo n y listo; solo en cerrado y resultados'}
relationships:
  - {from: Sala, to: CopiaDeSala, cardinality: '1 a muchos', note: 'borrar la sala borra sus copias'}
  - {from: Sala, to: Paquete, cardinality: '1 a 1', note: 'se arma por descarga, nunca se guarda'}
```

## Columnas de los CSV del paquete (fuente del diccionario de FR9.3)

| Archivo | Columnas |
|---|---|
| `participantes.csv` | `id`, `sala`, `nombre`, `id_colegio`, `colegio`, `grado`, `integrantes`, `n_integrantes`, `grupo`, `estado`, `creado`, `inicio`, `fin`, `motivo_fin`, `puntos`, `bono`, `total`, `nota`, `puesto`, `tiempo_usado_seg`, `tiempo_respuestas_seg`, `salidas` |
| `respuestas.csv` | `participante_id`, `pregunta_id`, `variante`, `respuesta`, `fraccion`, `puntos`, `max_puntos`, `momento`, `segundos_desde_inicio` |
| `eventos.csv` | `id_evento`, `participante_id`, `tipo`, `momento` |
| `colegios.csv` | `id_colegio`, `nombre`, `provisional`, `unido_a`, `id_definitivo`, `nombre_definitivo` |

- Sin `codigo`, `token`, `semilla` ni `clave_huella` en ningún archivo (FR9.5, R-11).
- `id_colegio` es el elegido al inscribirse; `colegio` es el nombre definitivo (ADR-W13).
- `respuesta` lleva los ids del banco como JSON compacto (FR9.2); `pregunta_id` es el id del banco.
- Fechas en ISO 8601 con `-05:00`; `tiempo_*_seg` y `segundos_desde_inicio` en segundos con punto
  decimal; `puesto` y `nota` vacíos si no está finalizado.

## Resumen

- **CopiaDeSala** es la única entidad nueva guardada (migración a la versión 3 del esquema: tablas
  `copias` y `copia_trozos`).
- **Paquete**, **Metadatos**, **VistaResultados** y **VistaTablero** son formas de salida; no se
  guardan.
- Los dos CSV de hoy no son entidades nuevas: son las mismas filas de siempre con el formato de
  `servidor.py` (ADR-W16).
