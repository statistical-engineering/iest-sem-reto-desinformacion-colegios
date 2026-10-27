# Entidades — U17 `u17-comparacion`

> **Revisión 2026-10-25 (una sola sala, solo Cloudflare).** Cambia lo siguiente:
>
> - **Medicion** sigue el C3 revisado: `opcion` es `local` o `cloudflare`, la parte `salas` pasa a
>   `relojes`, entra la parte `claves`, `nfr.salas` pasa a `nfr.colegios` y se leen las claves agregadas
>   `no_aplica` y `vencimiento`. Gana `corrida` (`publica` o `dev`, ADR-C5).
> - **FilaDeOpcion** gana el origen `no_se_construye` para GitHub Pages (FR12.2c).
> - **Eleccion** pierde el respaldo construido: el respaldo es la versión local (ADR-C3).
> - **GuiaDeDespliegue** gana el paso de Windows (ADR-C6).
> - Entra **EstimacionDeConsumo** (NFR6, BR17.12).

Las entidades de la comparación final (`unit-of-work.md`, «U17»). Son datos de documentación, no de una
base. Viven en:

- `despliegues/prueba_comun/mediciones/*.json` (contrato C3);
- `despliegues/COMPARACION.md`;
- `decisions.md` de esta unidad;
- `PUBLICAR_EN_INTERNET.md` y `despliegues/cloudflare/LEEME.md`.

Su dueño es el componente **Comparacion** (`components.md`, domain-design/).

```yaml
entities:
  - name: Medicion
    description: 'Una corrida de la prueba común contra Cloudflare, en el JSON del contrato C3.'
    owner: Comparacion
    attributes:
      - {name: version_esquema, type: entero, required: true, constraints: 'solo se acepta 1; otra versión se rechaza (C3)'}
      - {name: opcion, type: enum, required: true, allowed: [local, cloudflare]}
      - {name: corrida, type: enum, required: true, allowed: [publica, dev], constraints: 'sale del nombre del archivo: cloudflare_<fecha>.json es publica y cloudflare-dev_<fecha>.json es dev (ADR-C5)'}
      - {name: url, type: texto, required: true, constraints: 'sin clave ni ?clave='}
      - {name: inicio, type: fecha-hora, required: true}
      - {name: fin, type: fecha-hora, required: true}
      - {name: todo_bien, type: booleano, required: true}
      - {name: comprobaciones, type: lista, required: true, constraints: 'cada una con id, parte (base | fugas | relojes | claves | nfr) y pasa'}
      - {name: nfr, type: objeto, required: true, constraints: 'p95_responder_ms, p95_tablero_ms, sobrevive_reinicio, arranque_frio_ms, colegios, participantes, peticiones; agregadas: duracion_min, vencimiento, no_aplica, p95_resumen_ms, fracciones, encabezados_csv'}
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
      - {name: cumple, type: enum, required: true, allowed: [si, no, sin_evidencia, no_se_construye], constraints: 'sin_evidencia y no_se_construye cuentan como no para «pasa todo» (BR17.2)'}
      - {name: evidencia, type: texto, required: true, constraints: 'id de comprobación y archivo JSON (publica o dev, ADR-C5), URL oficial, comando o nombre de la persona que desplegó con el LEEME (NFR7)'}
  - name: EstimacionDeConsumo
    description: 'Peticiones que pide un reto real de 90 minutos, frente a la cuota diaria del plan gratuito.'
    owner: Comparacion
    attributes:
      - {name: equipos, type: entero, required: true, default: 40, constraints: 'NFR1'}
      - {name: minutos, type: entero, required: true, default: 90}
      - {name: intervalos, type: lista, required: true, constraints: 'cada refresco automático de las pantallas con su intervalo en segundos, leído de web/js/*.js y tablero.html de la copia de Cloudflare (tablero cada 2 s, panel cada 3 s, estudiante el que diga estudiante.js)'}
      - {name: respuestas, type: entero, required: true, constraints: 'equipos × preguntas × 2 (responder + estado), como en NFR2'}
      - {name: total, type: entero, required: true, constraints: 'Σ (minutos × 60 / intervalo) por pantalla abierta + respuestas + inscripciones; la fórmula y cada número van en la casilla'}
      - {name: cuota_diaria, type: entero, required: true, constraints: '100.000 peticiones por día del plan gratuito de Workers (https://developers.cloudflare.com/workers/platform/limits/); se vuelve a consultar el día que se llena la tabla'}
      - {name: porcentaje, type: número, required: true, constraints: 'total / cuota_diaria × 100, con una cifra decimal; NFR6 exige ≤ 50 %'}
  - name: FilaDeOpcion
    description: 'La columna completa de una opción en COMPARACION.md, con su veredicto «pasa todo» y los tres números de FR12.6.'
    owner: Comparacion
    attributes:
      - {name: opcion, type: enum, required: true, allowed: [render, cloudflare, cloudflare_containers, apps_script, github_pages]}
      - {name: origen, type: enum, required: true, allowed: [medida, documentada, no_pasa_por_contrato, no_se_construye]}
      - {name: pasa_todo, type: booleano, required: true}
      - {name: motivo_no_pasa, type: texto, required: false, constraints: 'obligatorio cuando pasa_todo es false; nombra los NFR, el hallazgo (por ejemplo C-01) o FR12.2c'}
      - {name: servicios_externos, type: entero, required: true, min: 0, constraints: 'contados con BR17.4'}
      - {name: piezas_propias, type: entero, required: true, min: 0, constraints: 'contadas con BR17.5'}
      - {name: lineas_codigo, type: entero, required: true, min: 0, constraints: 'contadas con BR17.6; 0 si no se escribió código'}
      - {name: veredictos, type: lista, required: true, constraints: 'un VeredictoNfr por NFR de FR12.5'}
  - name: Eleccion
    description: 'El resultado de aplicar FR12.5, FR12.6 y FR12.2c: ganadora y qué carpetas se borran.'
    owner: Comparacion
    attributes:
      - {name: ganadora, type: referencia, references: FilaDeOpcion, required: false, constraints: 'Cloudflare si pasa todo; vacía si no (OQ2)'}
      - {name: respaldo, type: texto, required: true, default: 'versión local (red local o túnel temporal)', constraints: 'no hay respaldo construido en la nube (FR12.2c, ADR-C3)'}
      - {name: criterio_decisivo, type: enum, required: false, allowed: [unica_que_pasa, servicios_externos, piezas_propias, lineas_codigo, humano]}
      - {name: carpetas_a_borrar, type: lista, required: true, constraints: 'apps-script, render, cloudflare-containers y github-pages; se borran en un commit propio tras la aprobación (FR12.6)'}
      - {name: aprobada_por_humano, type: booleano, required: true, default: false}
  - name: GuiaDeDespliegue
    description: 'PUBLICAR_EN_INTERNET.md reescrito para Cloudflare y una sola sala (FR8.1, FR8.2, FR8.3), con el LEEME.md de Cloudflare como fuente de los comandos.'
    owner: Comparacion
    attributes:
      - {name: opcion, type: referencia, references: FilaDeOpcion, required: true, constraints: 'la ganadora'}
      - {name: secciones, type: lista, required: true, constraints: 'las de functional-spec.md, «Forma de PUBLICAR_EN_INTERNET.md»'}
      - {name: sistemas, type: lista, required: true, default: '[Linux, Mac, Windows con Git Bash]', constraints: 'ADR-C6'}
      - {name: max_palabras_por_frase, type: entero, required: true, default: 30}
      - {name: terminos_explicados, type: lista, required: true, constraints: 'cada término técnico se explica la primera vez (markdown-docs.md)'}
relationships:
  - {from: FilaDeOpcion, to: Medicion, cardinality: '1 a 0 o 2', note: 'solo Cloudflare: una corrida publica y una dev (ADR-C5)'}
  - {from: FilaDeOpcion, to: CifraDocumentada, cardinality: '1 a muchos', note: 'Render y Cloudflare Containers'}
  - {from: FilaDeOpcion, to: VeredictoNfr, cardinality: '1 a 12'}
  - {from: FilaDeOpcion, to: EstimacionDeConsumo, cardinality: '1 a 0 o 1', note: 'solo Cloudflare'}
  - {from: Eleccion, to: FilaDeOpcion, cardinality: '1 a 5'}
  - {from: GuiaDeDespliegue, to: Eleccion, cardinality: '1 a 1'}
```

## Resumen

- **Medicion** es lo que entrega U2 (C3), en dos corridas de Cloudflare. **CifraDocumentada** es lo que
  entregan U15 y U16. Las dos alimentan una **FilaDeOpcion** por opción.
- **VeredictoNfr** deja explícito cada «sí», «no», «sin evidencia» o «no se construye» de la tabla de
  FR12.5. La fila pasa todo solo con doce «sí».
- **EstimacionDeConsumo** traduce las peticiones de la prueba a las de un reto real de 90 minutos y las
  compara con la cuota diaria. Es la evidencia de NFR6 y de lo que pasa si aparece la página de error 1027.
- **Eleccion** aplica FR12.2c: Cloudflare gana si pasa todo, y el respaldo es la versión local. La aprueba
  el humano en `decisions.md` (ADR-C3).
- **GuiaDeDespliegue** es `PUBLICAR_EN_INTERNET.md` para Cloudflare. Sus comandos salen del `LEEME.md`
  de Cloudflare, que también cubre Windows con Git Bash.
