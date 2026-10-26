# Entidades — U15 `u15-render-documentacion`

Unidad de solo documentación (`unit-of-work.md`, «U15 y U16»): no despliega nada ni escribe código. Sus
«entidades» son las cifras que llena en la columna Render de `despliegues/COMPARACION.md`. No se guardan
en ninguna base: viven en el Markdown de la tabla y en `functional-spec.md` de esta unidad.

```yaml
entities:
  - name: CifraDocumentada
    description: 'Un dato de la documentación oficial de Render que responde a una fila de la tabla de comparación.'
    owner: Comparacion
    attributes:
      - {name: criterio, type: enum, required: true, allowed: [corte_delgado, prueba_comun, p95_responder, p95_tablero, sobrevive_reinicio, arranque_frio, consumo_cuota, costo_usd, piezas_servicios, lineas_codigo, pasos_despliegue]}
      - {name: valor, type: texto, required: true, constraints: 'formato numérico de Colombia (2.980, 79,4 %); US$ con coma decimal'}
      - {name: cita, type: texto, required: true, constraints: 'frase textual de la página oficial, en su idioma original, entre comillas «…»'}
      - {name: url, type: texto, required: true, constraints: 'página oficial de render.com; nunca un foro ni una captura de memoria'}
      - {name: fecha_consulta, type: fecha, required: true, default: '2026-10-25'}
      - {name: veredicto, type: enum, required: true, allowed: [cumple, no_cumple, sin_medir, no_aplica]}
      - {name: motivo, type: texto, required: false, constraints: 'obligatorio cuando el veredicto es no_cumple o sin_medir'}
  - name: ColumnaDeOpcion
    description: 'La columna Render de COMPARACION.md: una CifraDocumentada por fila de FR12.4.'
    owner: Comparacion
    attributes:
      - {name: opcion, type: enum, required: true, allowed: [render]}
      - {name: cifras, type: lista, required: true, constraints: 'exactamente una por criterio; ninguna casilla queda en «pendiente»'}
      - {name: pasa_todo, type: booleano, required: true, default: false, constraints: 'false mientras NFR6 no se cumpla (FR12.2a)'}
relationships:
  - {from: ColumnaDeOpcion, to: CifraDocumentada, cardinality: '1 a 11'}
```

## Resumen

- **CifraDocumentada** es la unidad mínima: valor, cita textual, URL oficial y fecha. Sin URL no entra en
  la tabla (FR12.4, «con la URL oficial»).
- **ColumnaDeOpcion** es lo que U15 entrega a U17: la columna completa, sin «pendiente». U17 la copia
  tal cual a `COMPARACION.md` cuando llena la tabla (FR12.4).
- Las cifras verificadas el 2026-10-25 están en `functional-spec.md`, «Cifras oficiales».
