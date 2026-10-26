# Entidades — U16 `u16-cloudflare-containers-documentacion`

Unidad de solo documentación (`unit-of-work.md`, «U15 y U16»): no despliega nada ni escribe código. Sus
«entidades» son las cifras que llena en la columna Cloudflare Containers de `despliegues/COMPARACION.md`.
Tienen la misma forma que las de U15, para que U17 trate las dos columnas igual.

```yaml
entities:
  - name: CifraDocumentada
    description: 'Un dato de la documentación oficial de Cloudflare Containers que responde a una fila de la tabla de comparación.'
    owner: Comparacion
    attributes:
      - {name: criterio, type: enum, required: true, allowed: [corte_delgado, prueba_comun, p95_responder, p95_tablero, sobrevive_reinicio, arranque_frio, consumo_cuota, costo_usd, piezas_servicios, lineas_codigo, pasos_despliegue]}
      - {name: valor, type: texto, required: true, constraints: 'formato numérico de Colombia; US$ con coma decimal'}
      - {name: cita, type: texto, required: true, constraints: 'frase textual de la página oficial, en inglés, entre comillas «…»'}
      - {name: url, type: texto, required: true, constraints: 'página de developers.cloudflare.com; nunca un foro ni una cifra de memoria'}
      - {name: fecha_consulta, type: fecha, required: true, default: '2026-10-25'}
      - {name: veredicto, type: enum, required: true, allowed: [cumple, no_cumple, sin_medir, no_aplica]}
      - {name: motivo, type: texto, required: false, constraints: 'obligatorio cuando el veredicto es no_cumple o sin_medir'}
  - name: ColumnaDeOpcion
    description: 'La columna Cloudflare Containers de COMPARACION.md: una CifraDocumentada por fila de FR12.4.'
    owner: Comparacion
    attributes:
      - {name: opcion, type: enum, required: true, allowed: [cloudflare_containers]}
      - {name: cifras, type: lista, required: true, constraints: 'exactamente una por criterio; ninguna casilla queda en «pendiente»'}
      - {name: pasa_todo, type: booleano, required: true, default: false, constraints: 'false: exige Workers Paid (NFR6) y el disco es efímero (NFR4)'}
relationships:
  - {from: ColumnaDeOpcion, to: CifraDocumentada, cardinality: '1 a 11'}
```

## Resumen

- Misma forma que U15: valor, cita, URL oficial, fecha y veredicto por fila.
- La diferencia de fondo con Render: aquí el problema no es solo el costo (NFR6) sino que **el disco es
  efímero** y el `Dockerfile` actual guarda SQLite en `/data`, así que NFR4 no se cumple sin cambiar la
  aplicación (`functional-spec.md`, «Cifras oficiales», C4 a C7).
