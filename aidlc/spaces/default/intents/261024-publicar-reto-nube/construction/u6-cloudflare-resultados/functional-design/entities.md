# Entidades — U6 `u6-cloudflare-resultados`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** **CopiaDeSala** pasa a **Copia** (del reto,
> sin `sala`); **Metadatos** sigue los campos de C5; **VistaResultados** gana `puesto_grado`;
> **VistaTablero** gana `por_grado` y `nota`; las columnas del paquete pierden `sala`, `provisional` y
> `unido_a` y ganan `puesto_grado`, `arranque` y `equipos`.

Lo que U6 agrega a las entidades de U5 (`../../u5-cloudflare-salas/functional-design/entities.md`): la
copia del reto, el paquete de datos y las formas de exportación y de resultados. Las decisiones de formato
están en `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21).

```yaml
entities:
  - name: Copia
    description: Una copia completa de los datos del reto, hecha al reiniciar o en la migracion; se conserva hasta que el docente la borra (D7).
    owner: Exportacion
    attributes:
      - {name: id_copia, type: texto, required: true, unique: true, constraints: 'k + 8 caracteres del ALFABETO'}
      - {name: creada, type: fecha-hora, required: true}
      - {name: nombre_archivo, type: texto, required: true, constraints: 'copia_<sala>_<AAAA-MM-DD_HHMM>.sql, o migracion_v1.sql la de la version 3'}
      - {name: bytes, type: entero, required: true}
      - {name: sha256, type: texto, required: true, constraints: 'huella del contenido; se comprueba al descargar'}
      - {name: contenido, type: texto, required: true, constraints: 'guion SQL (ADR-W14) guardado en trozos de 512 KiB (ADR-W17); sin token, semilla ni codigo personal'}
  - name: Paquete
    description: El .zip que el docente descarga; no se guarda, se arma en cada descarga.
    owner: Exportacion
    attributes:
      - {name: nombre, type: texto, required: true, constraints: 'AAAA-MM-DD_<sala>_reto.zip, fecha de apertura en hora de Colombia (ADR-W18)'}
      - {name: participantes_csv, type: texto, required: true}
      - {name: respuestas_csv, type: texto, required: true}
      - {name: eventos_csv, type: texto, required: true}
      - {name: colegios_csv, type: texto, required: true}
      - {name: copia_sql, type: texto, required: true, constraints: 'misma forma que Copia.contenido'}
      - {name: metadatos_json, type: json, required: true}
  - name: Metadatos
    description: metadatos.json del paquete (FR9.1, C5).
    owner: Exportacion
    attributes:
      - {name: inicio, type: texto, required: false, constraints: 'ISO 8601 con -05:00 de abierto_en; null si no se abrio'}
      - {name: fin, type: texto, required: false, constraints: 'ISO 8601 de cerrado_en; null si no se cerro'}
      - {name: sala, type: texto, required: true, constraints: 'codigo de sala del reto'}
      - {name: evento, type: texto, required: true}
      - {name: duracion_min, type: número, required: true}
      - {name: participantes, type: entero, required: true, constraints: 'filas de participantes.csv'}
      - {name: colegios, type: entero, required: true, constraints: 'filas de colegios.csv'}
      - {name: version_banco, type: texto, required: true, constraints: 'version del banco (la de construir_banco.py)'}
      - {name: huella_banco, type: texto, required: true, constraints: 'sha256 del banco.json copiado (project.md, «Corrections»)'}
      - {name: version_app, type: json, required: true, constraints: 'objeto con commit y fecha, de src/version.json'}
      - {name: version_esquema, type: entero, required: true}
      - {name: estado, type: enum, required: true, allowed: [inscripcion, abierto, cerrado, resultados]}
      - {name: generado, type: texto, required: true, constraints: 'ISO 8601 del momento de la descarga'}
  - name: VistaResultados
    description: Lo que /api/estado agrega al participante finalizado con el reto en resultados.
    owner: Resultados
    attributes:
      - {name: puesto, type: entero, required: true, constraints: 'puesto general entre todos los colegios'}
      - {name: puesto_grado, type: entero, required: true}
      - {name: nota, type: número, required: true}
      - {name: revision, type: json, required: true, constraints: 'por pregunta visible, respuesta con ids opacos y explicacion (U4 BR1.2)'}
  - name: VistaTablero
    description: Lo que GET /api/publico agrega a lo de U5.
    owner: Resultados
    attributes:
      - {name: ranking, type: lista, required: false, constraints: 'top 10 del orden general con puesto, puesto_grado, nombre, colegio, grado, total, puntos y nota; solo en resultados o con modo sorpresa apagado; el podio son los tres primeros'}
      - {name: por_grado, type: json, required: false, constraints: '{"9", "10", "11"}: top 10 de cada grado con las mismas claves; sale y se oculta junto con ranking'}
      - {name: experimento, type: json, required: false, constraints: 'experimento_publico (U4 BR6.2): nada en inscripcion y abierto, {n, listo} en cerrado, completo en resultados'}
relationships:
  - {from: Copia, to: Paquete, cardinality: 'independientes', note: 'el paquete arma su propia copia en cada descarga; no lee la tabla copias'}
```

## Tablas (versión 3 del esquema)

| Tabla | Columnas | Notas |
|---|---|---|
| `copias` | `id_copia`, `creada`, `nombre_archivo`, `bytes`, `sha256` | Una fila por copia |
| `copia_trozos` | `id_copia`, `n`, `contenido` | Clave (`id_copia`, `n`); trozos de 524.288 bytes |

## Columnas de los CSV del paquete (fuente del diccionario de FR9.3)

| Archivo | Columnas |
|---|---|
| `participantes.csv` | `id`, `nombre`, `id_colegio`, `colegio`, `grado`, `integrantes`, `n_integrantes`, `grupo`, `estado`, `creado`, `inicio`, `fin`, `motivo_fin`, `puntos`, `bono`, `total`, `tiempo_usado`, `tiempo_respuestas`, `salidas`, `puesto`, `puesto_grado`, `nota` |
| `respuestas.csv` | `participante_id`, `pregunta_id`, `variante`, `respuesta`, `fraccion`, `puntos`, `max_puntos`, `momento` |
| `eventos.csv` | `id_evento`, `participante_id`, `tipo`, `momento` |
| `colegios.csv` | `id_colegio`, `nombre`, `arranque`, `equipos` |

- El orden de columnas es el de C5 (`contract-summary.md`, «C5. Paquete de datos»).
- Sin `codigo`, `token` ni `semilla` en ningún archivo (FR9.5, R-11).
- `colegio` es el nombre de la lista del docente; `id_colegio` no se conserva entre retos: varios años se
  unen por el nombre normalizado de `colegios.csv` (C5, ADR-009).
- `respuesta` lleva los ids del banco como JSON compacto (FR9.2); `pregunta_id` es el id del banco.
- Fechas (`creado`, `inicio`, `fin`, `momento`, `arranque`) en ISO 8601 con `-05:00`; `tiempo_usado` y
  `tiempo_respuestas` en segundos con punto decimal, relativos al arranque del colegio (FR2.6); `puesto`,
  `puesto_grado` y `nota` vacíos si no está finalizado.

## Resumen

- **Copia** es la única entidad nueva guardada (migración a la versión 3 del esquema: tablas `copias` y
  `copia_trozos`).
- **Paquete**, **Metadatos**, **VistaResultados** y **VistaTablero** son formas de salida; no se
  guardan.
- Los dos CSV de hoy no son entidades nuevas: son las mismas filas de siempre con el formato de
  `servidor.py` (ADR-W16).
