# Entidades — U14 `u14-github-pages-resultados`

U14 completa Resultados y Exportacion en la opción GitHub Pages (API en PythonAnywhere,
`../../u11-github-pages-corte/decisions.md`, ADR-G5 para el formato de la copia). Las entidades
guardadas son las de U13; U14 agrega la copia de una sala y define los objetos de salida (paquete,
metadatos) con la forma del contrato C5.

```yaml
entities:
  - name: CopiaDeSala
    description: Una copia completa de los datos de una sala, que se puede volver a abrir (FR4.3); la hace «Reiniciar» y la lleva el paquete.
    owner: Exportacion
    attributes:
      - {name: id_copia, type: identificador, required: true, unique: true}
      - {name: sala, type: referencia, references: Sala, required: true}
      - {name: creada, type: fecha-hora, required: true}
      - {name: nombre_archivo, type: texto, required: true, constraints: "AAAA-MM-DD_HHMM_<sala>_reto.db"}
      - {name: contenido, type: binario, required: true, constraints: "un archivo SQLite con el mismo esquema y solo las filas de esa sala; sin las columnas token, semilla, codigo personal ni clave_huella (C-06, R-11)"}
  - name: Paquete
    description: El .zip que descarga el docente (FR9.1); no se guarda, se arma al pedirlo.
    owner: Exportacion
    attributes:
      - {name: nombre, type: texto, required: true, constraints: "AAAA-MM-DD_<sala>_reto.zip"}
      - {name: participantes_csv, type: archivo, required: true, constraints: "una fila por participante; sin token, semilla, codigo ni clave_huella; con n_integrantes"}
      - {name: respuestas_csv, type: archivo, required: true, constraints: "una fila por respuesta con el id del banco; distinto del respuestas.csv de hoy (C-13)"}
      - {name: eventos_csv, type: archivo, required: true, constraints: "una fila por evento con id_evento"}
      - {name: colegios_csv, type: archivo, required: true, constraints: "colegios de la sala con su id_colegio definitivo"}
      - {name: copia, type: archivo, required: true, constraints: "la CopiaDeSala en formato reto.db"}
      - {name: metadatos_json, type: archivo, required: true}
  - name: Metadatos
    description: metadatos.json del paquete (FR9.1).
    owner: Exportacion
    attributes:
      - {name: inicio, type: fecha-hora, required: true, constraints: "ISO 8601 con zona horaria (abierta de la sala)"}
      - {name: fin, type: fecha-hora, required: false, constraints: "cerrada de la sala"}
      - {name: sala, type: texto, required: true}
      - {name: evento, type: texto, required: false}
      - {name: duracion_min, type: número, required: true}
      - {name: participantes, type: entero, required: true}
      - {name: version_banco, type: texto, required: true, constraints: "huella sha256 de src/banco.json"}
      - {name: version_app, type: texto, required: true, constraints: "commit corto de la API, leído de src/version.txt que escribe copiar.sh"}
      - {name: opcion, type: texto, required: true, constraints: "«github_pages»"}
  - name: VistaPublica
    description: Lo que devuelve GET /api/publico?sala= al tablero (FR11.4).
    owner: Resultados
    attributes:
      - {name: claves_de_hoy, type: json, required: true, constraints: "las de api-documentation.md: evento, titulo, estado, sala, duracion_min, abierto_en, cerrado_en, servidor_ahora, reloj_global, modo_sorpresa, conteo, ranking, experimento, urls"}
      - {name: experimento, type: json, required: true, constraints: "por_publicacion[] sin verdad ni multitud_acierta mientras el estado no sea resultados (FR6.1)"}
relationships:
  - {from: Sala, to: CopiaDeSala, cardinality: "1 a muchos", note: "reiniciar conserva las copias; borrar la sala las borra"}
```

## Resumen

- **CopiaDeSala** se guarda en la tabla `copias` como blob: un `reto.db` pequeño con las filas de esa
  sala. Así `/api/admin/copia` la descarga y «Borrar la sala» la borra con la sala (NFR10.1).
- **Paquete** y **Metadatos** no se guardan: se arman al pedirlos con `zipfile` y `csv` de la biblioteca
  estándar.
- **VistaPublica** es la forma del tablero; el navegador la recibe desde otro dominio con las cabeceras
  CORS de U11.
