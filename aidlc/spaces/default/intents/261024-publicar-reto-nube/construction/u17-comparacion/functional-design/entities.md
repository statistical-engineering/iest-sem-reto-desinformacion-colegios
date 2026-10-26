# Entidades — U17 `u17-comparacion`

Las entidades de la comparación final (`unit-of-work.md`, «U17»). Son datos de documentación, no de una
base: viven en `despliegues/prueba_comun/mediciones/*.json` (contrato C3), en `despliegues/COMPARACION.md`,
en `decisions.md` de esta unidad y en `PUBLICAR_EN_INTERNET.md`. Dueño: el componente **Comparacion**
(`components.md`, domain-design/).

```yaml
entities:
  - name: Medicion
    description: 'Una corrida de la prueba común contra una opción, en el JSON del contrato C3.'
    owner: Comparacion
    attributes:
      - {name: version_esquema, type: entero, required: true, constraints: 'solo se acepta 1; otra versión se rechaza (C3)'}
      - {name: opcion, type: enum, required: true, allowed: [local, cloudflare, apps_script, github_pages]}
      - {name: url, type: texto, required: true, constraints: 'sin clave ni ?clave='}
      - {name: inicio, type: fecha-hora, required: true}
      - {name: fin, type: fecha-hora, required: true}
      - {name: todo_bien, type: booleano, required: true}
      - {name: comprobaciones, type: lista, required: true, constraints: 'cada una con id, parte (base | fugas | salas | nfr) y pasa'}
      - {name: nfr, type: objeto, required: true, constraints: 'p95_responder_ms, p95_tablero_ms, sobrevive_reinicio, arranque_frio_ms, salas, participantes, peticiones'}
  - name: CifraDocumentada
    description: 'Una cifra de documentación oficial que llenaron U15 o U16 (misma forma que en sus entities.md).'
    owner: Comparacion
    attributes:
      - {name: criterio, type: enum, required: true, allowed: [corte_delgado, prueba_comun, p95_responder, p95_tablero, sobrevive_reinicio, arranque_frio, consumo_cuota, costo_usd, piezas_servicios, lineas_codigo, pasos_despliegue]}
      - {name: valor, type: texto, required: true}
      - {name: url, type: texto, required: true}
      - {name: fecha_consulta, type: fecha, required: true}
  - name: VeredictoNfr
    description: 'Si una opción cumple un NFR según la tabla de FR12.5, con su evidencia.'
    owner: Comparacion
    attributes:
      - {name: opcion, type: enum, required: true, allowed: [render, cloudflare, cloudflare_containers, apps_script, github_pages]}
      - {name: nfr, type: enum, required: true, allowed: [NFR1, NFR2, NFR3, NFR4, NFR5, NFR6, NFR7, NFR8, NFR9, NFR10, NFR11, NFR12]}
      - {name: cumple, type: enum, required: true, allowed: [si, no, sin_evidencia], constraints: 'sin_evidencia cuenta como no para «pasa todo» (BR17.2)'}
      - {name: evidencia, type: texto, required: true, constraints: 'id de comprobación del JSON, URL oficial, comando o nombre de la persona que desplegó con el LEEME (NFR7)'}
  - name: FilaDeOpcion
    description: 'La columna completa de una opción en COMPARACION.md, con su veredicto «pasa todo» y los tres números de FR12.6.'
    owner: Comparacion
    attributes:
      - {name: opcion, type: enum, required: true, allowed: [render, cloudflare, cloudflare_containers, apps_script, github_pages]}
      - {name: origen, type: enum, required: true, allowed: [medida, documentada, no_pasa_por_contrato]}
      - {name: pasa_todo, type: booleano, required: true}
      - {name: motivo_no_pasa, type: texto, required: false, constraints: 'obligatorio cuando pasa_todo es false; nombra los NFR o el hallazgo (por ejemplo C-01)'}
      - {name: servicios_externos, type: entero, required: true, min: 0, constraints: 'contados con BR17.4'}
      - {name: piezas_propias, type: entero, required: true, min: 0, constraints: 'contadas con BR17.5'}
      - {name: lineas_codigo, type: entero, required: true, min: 0, constraints: 'contadas con BR17.6; 0 si no se escribió código'}
      - {name: veredictos, type: lista, required: true, constraints: 'un VeredictoNfr por NFR de FR12.5'}
  - name: Eleccion
    description: 'El resultado de aplicar FR12.5 y FR12.6: ganadora, respaldo y qué carpetas se borran.'
    owner: Comparacion
    attributes:
      - {name: ganadora, type: referencia, references: FilaDeOpcion, required: false, constraints: 'vacía si ninguna pasa todo (OQ2)'}
      - {name: respaldo, type: referencia, references: FilaDeOpcion, required: false, constraints: 'la segunda que pasa todo; conserva carpeta, ADR y fila'}
      - {name: criterio_decisivo, type: enum, required: false, allowed: [servicios_externos, piezas_propias, lineas_codigo, humano]}
      - {name: carpetas_a_borrar, type: lista, required: true, constraints: 'las de las opciones que ni ganan ni son respaldo; se borran en un commit propio tras la aprobación (FR12.6)'}
      - {name: aprobada_por_humano, type: booleano, required: true, default: false}
  - name: GuiaDeDespliegue
    description: 'PUBLICAR_EN_INTERNET.md reescrito para la ganadora (FR8.1, FR8.2, FR8.3).'
    owner: Comparacion
    attributes:
      - {name: opcion, type: referencia, references: FilaDeOpcion, required: true, constraints: 'la ganadora'}
      - {name: secciones, type: lista, required: true, constraints: 'las de functional-spec.md, «Forma de PUBLICAR_EN_INTERNET.md»'}
      - {name: max_palabras_por_frase, type: entero, required: true, default: 30}
      - {name: terminos_explicados, type: lista, required: true, constraints: 'cada término técnico se explica la primera vez (markdown-docs.md)'}
relationships:
  - {from: FilaDeOpcion, to: Medicion, cardinality: '1 a 0 o 1', note: 'solo las opciones medidas'}
  - {from: FilaDeOpcion, to: CifraDocumentada, cardinality: '1 a muchos', note: 'Render y Cloudflare Containers'}
  - {from: FilaDeOpcion, to: VeredictoNfr, cardinality: '1 a 12'}
  - {from: Eleccion, to: FilaDeOpcion, cardinality: '1 a 5'}
  - {from: GuiaDeDespliegue, to: Eleccion, cardinality: '1 a 1'}
```

## Resumen

- **Medicion** es lo que U2 entrega (C3); **CifraDocumentada** lo que entregan U15 y U16. Las dos
  alimentan una **FilaDeOpcion** por opción.
- **VeredictoNfr** hace explícito cada «sí / no / sin evidencia» de la tabla de FR12.5; la fila pasa todo
  solo con doce «sí».
- **Eleccion** aplica el orden de FR12.6 y nombra ganadora, respaldo y carpetas que se borran; la aprueba
  el humano en `decisions.md` (ADR-C3).
- **GuiaDeDespliegue** es `PUBLICAR_EN_INTERNET.md` para la ganadora.
