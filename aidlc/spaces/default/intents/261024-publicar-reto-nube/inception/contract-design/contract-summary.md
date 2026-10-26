# Contratos del reto en la nube

Qué datos cruzan cada frontera, con qué forma y qué pasa si algo falla. Sale de las unidades y sus
dependencias (`unit-of-work.md`, `unit-of-work-dependency.md`), de los componentes (`components.md`) y de
los requisitos (`requirements.md`). Las respuestas de esta etapa están en
`contract-design-questions.md` (Q1 a Q6, todas A, 2026-10-25).

## Contratos

| # | Proveedor | Consumidor | Mecanismo | Dueño |
|---|---|---|---|---|
| C1 | Cada opción: Workers (U1, U4–U6), Apps Script (U7–U10), GitHub Pages (U11–U14) | External: navegador (`web/js/estudiante.js`, `web/js/admin.js`, `web/tablero.html`) | REST/HTTP, JSON | Prueba común (U1 lo crea, U2 lo completa) |
| C2 | Cada opción desplegada y la versión local (`2_Aplicacion_Reto/`) | Prueba común (U1, U2) | REST/HTTP, la misma API de C1 | Prueba común (U2) |
| C3 | Prueba común (U2) | Comparación (U17) | Esquema compartido: un JSON por corrida | U2 |
| C4 | Reglas de cada opción (U4, U8, U12) | Salas y resultados de la misma opción (U5, U6, U9, U10, U13, U14) | Llamada a función dentro del servicio, con la misma forma en las tres opciones | Cada unidad de reglas es dueña de su código; la forma y la tabla de casos, del contrato |
| C5 | Exportación de cada opción (U6, U10, U14) | External: carpeta privada del semillero (FR9.4) | Esquema compartido: paquete `.zip` | Contrato (U2); el diccionario de FR9.3 lo describe |

Las fronteras entre unidades de **una misma opción** son llamadas a funciones dentro del mismo servicio
(`unit-of-work-dependency.md`, «Puntos de integración»). Solo C4 fija su forma, porque es la única que se
repite en las tres opciones.

## C1 y C2. API HTTP

**Dónde vive.** `despliegues/prueba_comun/contrato_api.yaml` (Q1-A). El bloque de abajo es su contenido
inicial. Las 16 rutas de hoy (5 GET y 11 POST, `api-documentation.md`) se mantienen con sus claves JSON
(FR4.1). Aquí solo se escribe lo que cambia o se agrega; lo demás se copia tal cual de
`api-documentation.md` al crear el archivo.

**Reglas comunes.**

- Clave de docente y del semillero: las dos por la cabecera `X-Clave-Admin` (Q2-A, FR9.5). Si la clave
  empieza con `<código>-` es de esa sala; si no, se compara con la del semillero. El parámetro `?clave=`
  de hoy no se acepta en la nube, porque deja la clave en los registros del hosting.
- Con la clave de una sala, toda ruta `/api/admin/*` actúa sobre esa sala. Un `?sala=` distinto da 403
  (FR11.5). Con la clave del semillero, toda ruta de una sala exige `?sala=<código>`; sin él da 400.
- Errores (Q4-A): `{"error": "<mensaje en español>"}` con 400, 401, 403, 404 o 413, como hoy; 500 sin
  detalles; y **503** si la plataforma está sin cuota o no responde. El navegador no reintenta un POST
  por su cuenta.
- Responder dos veces la misma pregunta sigue dando 400 «ya respondida». Por eso un reintento de la
  persona nunca suma dos veces (invariante «una sola respuesta por pregunta»).
- Todas las respuestas llevan `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`, como hoy.
- La versión local ignora `?sala=`, porque tiene una sola sala. Así la prueba común manda siempre
  `?sala=` y corre igual contra las cuatro versiones (C2).

```yaml
openapi: 3.0.3
info:
  title: API del reto «Detectives de la desinformación» en la nube
  version: "1.0"
  description: >
    Cambios y agregados sobre las 16 rutas de hoy (api-documentation.md). Las rutas que no aparecen
    aquí se mantienen igual. Sin versión en la ruta (Q3-A).
components:
  securitySchemes:
    token:
      type: http
      scheme: bearer
    claveAdmin:
      type: apiKey
      in: header
      name: X-Clave-Admin
      description: Clave de sala (<código>-…) o clave del semillero.
  parameters:
    sala:
      name: sala
      in: query
      required: false
      schema: {type: string, pattern: "^[A-Z0-9]{3,8}$"}
      description: Obligatorio con la clave del semillero; con la clave de sala debe coincidir o faltar.
  schemas:
    Error:
      type: object
      required: [error]
      properties:
        error: {type: string}
    Ok:
      type: object
      required: [ok]
      properties:
        ok: {type: boolean}
    Colegio:
      type: object
      required: [id_colegio, nombre, provisional]
      properties:
        id_colegio: {type: string}
        nombre: {type: string}
        provisional: {type: boolean}
  responses:
    Error400: {description: Petición inválida, content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
    Error403: {description: Clave incorrecta o de otra sala, content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
    Error503: {description: Plataforma sin cuota o sin respuesta, content: {application/json: {schema: {$ref: "#/components/schemas/Error"}}}}
paths:
  /api/publico:
    get:
      summary: Tablero de una sala (cambia, FR6.1 y FR11.4)
      parameters:
        - $ref: "#/components/parameters/sala"
      responses:
        "200":
          description: >
            Con ?sala= trae las mismas claves de hoy para esa sala. Mientras el estado no sea
            «resultados», experimento.por_publicacion[] no trae «verdad» ni «multitud_acierta» (FR6.1).
            Sin ?sala= responde solo {"ok": true}: sirve de chequeo de salud y no muestra ninguna sala.
        "404": {description: No existe una sala con ese código}
        "503": {$ref: "#/components/responses/Error503"}
  /api/colegios:
    get:
      summary: Colegios de una sala para el formulario de inscripción (nueva, FR10.3)
      parameters:
        - {name: sala, in: query, required: true, schema: {type: string}}
      responses:
        "200":
          description: Solo los colegios que eligió el docente; nada más de la sala.
          content:
            application/json:
              schema:
                type: object
                required: [colegios]
                properties:
                  colegios:
                    type: array
                    items:
                      type: object
                      required: [id_colegio, nombre]
                      properties:
                        id_colegio: {type: string}
                        nombre: {type: string}
        "404": {description: No existe una sala con ese código}
  /api/registro:
    post:
      summary: Inscripción (cambia una clave, FR10.3)
      description: >
        Mismas claves que hoy. «colegio» pasa a ser el id_colegio de la lista de /api/colegios; un
        valor fuera de la lista da 400. «sala» es el código de la sala, que se busca en todo el servicio.
      responses:
        "200": {description: "{token, codigo}, como hoy"}
        "400": {$ref: "#/components/responses/Error400"}
  /api/estado:
    get:
      summary: Estado del participante (misma forma, ids opacos, FR6.2)
      description: >
        Mismas claves. Los ids de opciones, ítems y partes son opacos (HMAC, ADR-006) y su orden no es el
        del banco. /api/responder los recibe opacos y el servidor los traduce.
      security: [{token: []}]
      responses:
        "200": {description: Mismas claves que hoy}
        "401": {description: Sesión no encontrada}
  /api/admin/login:
    post:
      summary: Entrar al panel (agrega claves)
      security: [{claveAdmin: []}]
      responses:
        "200":
          description: >
            {ok: true, rol: "sala" | "semillero", sala: <código> solo si rol es "sala"}. Las claves
            «rol» y «sala» son nuevas.
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/config:
    post:
      summary: Configurar la sala (cambia, R-12)
      description: >
        Mismas claves que hoy, salvo «sala»: el código ya no se cambia y mandarlo da 400 «El código de
        sala no se puede cambiar.». Solo en «inscripción» se puede cambiar duracion_min y reloj_global,
        como hoy.
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{ok: true}"}
        "400": {$ref: "#/components/responses/Error400"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/reiniciar:
    post:
      summary: Reiniciar la sala (cambia el valor de «copia»)
      description: >
        Pide confirmar = "BORRAR", como hoy. «copia» ahora es el id_copia de la CopiaDeSala guardada,
        que se descarga con /api/admin/copia. Conserva la sala, su clave, sus colegios y sus copias.
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{ok: true, copia: <id_copia>}"}
  /api/admin/salas:
    get:
      summary: Lista de salas (nueva, solo semillero)
      security: [{claveAdmin: []}]
      responses:
        "200":
          description: >
            {salas: [{sala, estado, evento, creada, abierta, cerrada, inscritos}]}. Nunca trae claves
            ni huellas.
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/salas/crear:
    post:
      summary: Crear una sala (nueva, solo semillero, ADR-003)
      description: El servidor genera el código y la clave. La clave se muestra solo en esta respuesta.
      security: [{claveAdmin: []}]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                evento: {type: string}
      responses:
        "200": {description: "{sala: <código>, clave: <código>-…}"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/salas/clave:
    post:
      summary: Regenerar la clave de una sala (nueva, solo semillero, ADR-003)
      description: La clave anterior deja de servir en ese momento.
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{sala, clave}"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/salas/borrar:
    post:
      summary: Borrar una sala con sus copias (nueva, solo semillero, NFR10.1)
      description: Solo con la sala en «cerrado» o «resultados» y confirmar = "BORRAR"; si no, 400.
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{ok: true}"}
        "400": {$ref: "#/components/responses/Error400"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/catalogo:
    get:
      summary: Catálogo único de colegios (nueva, ADR-002)
      security: [{claveAdmin: []}]
      responses:
        "200": {description: "{colegios: [Colegio]} con todos los del catálogo"}
    post:
      summary: Mantener el catálogo (nueva, solo semillero, ADR-002)
      description: >
        accion ∈ {agregar, corregir, confirmar, unir}. agregar usa «nombre»; corregir usa «id_colegio» y
        «nombre»; confirmar usa «id_colegio» de un provisional; unir usa «id_colegio» del provisional y
        «unir_a». Un nombre normalizado que ya existe da 400 con la clave «existente» (un Colegio).
      security: [{claveAdmin: []}]
      responses:
        "200": {description: "{ok: true, id_colegio}"}
        "400": {$ref: "#/components/responses/Error400"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/colegios:
    get:
      summary: Colegios elegidos para la sala (nueva, FR10.3)
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{elegidos: [Colegio]}"}
    post:
      summary: Elegir colegios de la sala (nueva, FR10.3)
      description: >
        accion ∈ {elegir, quitar, provisional}. elegir y quitar usan «id_colegio»; provisional usa
        «nombre» y agrega a la sala un colegio marcado provisional. Elegir y quitar solo en «inscripción»;
        provisional también el día del reto. Un nombre que ya existe da 400 con la clave «existente».
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{ok: true, id_colegio}"}
        "400": {$ref: "#/components/responses/Error400"}
        "403": {$ref: "#/components/responses/Error403"}
  /api/admin/copias:
    get:
      summary: Copias de «Reiniciar» de la sala (nueva, R-17)
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "{copias: [{id_copia, creada, nombre_archivo}]}"}
  /api/admin/copia:
    get:
      summary: Descargar una copia (nueva)
      description: El formato de la copia lo fija el ADR de cada opción (FR4.3).
      security: [{claveAdmin: []}]
      parameters:
        - $ref: "#/components/parameters/sala"
        - {name: id, in: query, required: true, schema: {type: string}}
      responses:
        "200": {description: Archivo de la copia}
        "404": {description: No existe esa copia en la sala}
  /api/admin/paquete.zip:
    get:
      summary: Paquete de datos de la sala (nueva, FR9.1, FR9.5)
      security: [{claveAdmin: []}]
      parameters: [{$ref: "#/components/parameters/sala"}]
      responses:
        "200": {description: "application/zip, nombre AAAA-MM-DD_<sala>_reto.zip, contenido en C5"}
        "403": {$ref: "#/components/responses/Error403"}
```

**Cambios que exige el navegador** (FR4.1 pide listarlos con motivo y archivo):

| Archivo de `web/` | Cambio | Motivo |
|---|---|---|
| `web/tablero.html` | Lee `sala` de su propia URL (`/tablero?sala=KQMT`) y la pasa a `/api/publico` | Tablero por sala (FR11.4) |
| `web/js/estudiante.js` | El campo «Colegio» pasa a ser una lista que llena `/api/colegios?sala=` | Lista cerrada (FR10.3) |
| `web/js/admin.js` | El código de sala se muestra sin poder editarse | El código no cambia (R-12) |
| `web/js/admin.js` | Lista de copias con un botón de descarga cada una, y botón del paquete `.zip` | R-17, FR9.1 |
| `web/js/admin.js` | Con `rol: "semillero"`: salas, crear, regenerar clave, borrar, catálogo | FR11.5, ADR-002, ADR-003 |
| `web/js/admin.js` | Elegir colegios de la sala y agregar uno provisional | FR10.3 |

El estudiante no ve otro cambio (FR11.3). Son las excepciones aprobadas en Domain Design
(`components.md`, «Cambios que el docente ve en el panel»).

## C3. Archivo de mediciones

Un JSON por corrida en `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` (Q5-A). U17 lo lee
para llenar `despliegues/COMPARACION.md` (FR12.4).

```yaml
# esquema compartido (JSON Schema escrito en YAML)
$schema: "https://json-schema.org/draft/2020-12/schema"
title: Medición de una corrida de la prueba común
type: object
required: [version_esquema, opcion, url, inicio, fin, todo_bien, comprobaciones, nfr]
properties:
  version_esquema: {const: 1}
  opcion: {enum: [local, cloudflare, apps_script, github_pages]}
  url: {type: string}
  inicio: {type: string, format: date-time}
  fin: {type: string, format: date-time}
  todo_bien: {type: boolean}
  comprobaciones:
    type: array
    items:
      type: object
      required: [id, parte, pasa]
      properties:
        id: {type: string}          # nombre fijo de la comprobación, por ejemplo «fuga_verdad_cerrado»
        parte: {enum: [base, fugas, salas, nfr]}
        pasa: {type: boolean}
        detalle: {type: string}     # nunca una clave ni una respuesta correcta
  nfr:
    type: object
    required: [p95_responder_ms, p95_tablero_ms, sobrevive_reinicio, arranque_frio_ms, salas, participantes]
    properties:
      p95_responder_ms: {type: number}
      p95_tablero_ms: {type: number}
      sobrevive_reinicio: {type: [boolean, "null"]}   # null cuando no aplica
      arranque_frio_ms: {type: [number, "null"]}
      salas: {type: integer}
      participantes: {type: integer}
      peticiones: {type: integer}                       # para comparar con la cuota (NFR6)
```

El archivo nunca lleva la URL con clave, ninguna clave ni datos de participantes de un reto real.

## C4. Forma de las reglas

Mismos nombres, entradas y salidas en las tres opciones (Q6-A). Cada opción las escribe en su lenguaje y
no comparte código con otra (FR12.2). Una tabla de casos, `despliegues/prueba_comun/casos_reglas.json`
(«estos datos y esta hora dan este resultado», ADR-001), se copia a las pruebas unitarias de cada opción.
Ninguna regla lee la base ni el reloj: la hora llega como argumento.

```yaml
# forma de las «calculadoras» (ADR-001); tipos en notación neutral
reglas:
  Banco:
    validar_banco: {entrada: [banco], salida: "lista de errores (vacía si está bien)"}
    examen_publico: {entrada: [banco, semilla, grupo, respondidas], salida: "misiones[] con ids opacos (FR6.2)"}
    traducir_opaco: {entrada: [banco, semilla, pregunta_id, respuesta_opaca], salida: "respuesta con ids del banco"}
  Calificacion:
    validar_respuesta: {entrada: [pregunta, respuesta], salida: "respuesta normalizada o error"}
    fraccion: {entrada: [pregunta, respuesta], salida: "número entre 0 y 1"}
    bono: {entrada: [puntos, t_ultima_seg, duracion_seg], salida: "número"}
  Clasificacion:
    ordenar: {entrada: ["participantes finalizados"], salida: "lista con puesto, sin empates (NFR11)"}
    nota: {entrada: [total], salida: "nota sobre 5"}
  CicloDeSala:
    transicion_permitida: {entrada: [estado_actual, estado_nuevo], salida: booleano}
    hora_de_entrega: {entrada: [ahora, inicio, duracion_seg, cierre], salida: "{hora, motivo: tiempo | cierre} o nada"}
  LimpiezaEntrada:
    normalizar_texto: {entrada: [texto], salida: texto}
    normalizar_integrantes: {entrada: [texto], salida: texto}
  Experimento:
    calcular: {entrada: ["participantes y respuestas de la sala", estado_sala], salida: "objeto «experimento» sin veredicto antes de resultados"}
casos_reglas:
  formato: "[{regla, funcion, entrada, salida_esperada}]"
  regla_de_oro: "la salida esperada se calcula con el servidor local, nunca se escribe a mano"
  no_lleva: "respuestas correctas del banco: los casos de Calificacion usan un banco de prueba propio"
```

## C5. Paquete de datos

```yaml
# esquema compartido del .zip (FR9.1, FR9.2, FR9.5)
nombre: "AAAA-MM-DD_<sala>_reto.zip"
archivos:
  participantes.csv: "una fila por participante; sin token, semilla, codigo personal ni clave_huella"
  respuestas.csv: "una fila por respuesta, con el id del banco (nunca el opaco)"
  eventos.csv: "una fila por evento, con id_evento"
  colegios.csv: "los colegios de la sala con su id_colegio definitivo"
  copia: "la copia completa de la sala en el formato del ADR de cada opción (FR4.3)"
  metadatos.json:
    campos: [inicio, fin, sala, evento, duracion_min, participantes, version_banco, version_app]
formato:
  codificacion: UTF-8 con encabezado
  fechas: "ISO 8601 con zona horaria, por ejemplo 2026-11-03T08:15:00-05:00"
  decimales: punto
  nunca: [claves, token, "datos de otra sala"]
```

Los dos CSV de hoy (`resultados.csv`, `respuestas.csv` de `/api/admin/*.csv`) no cambian de columnas ni
de formato (FR4.3). El diccionario de FR9.3 describe cada columna del paquete.

## Reglas de dueño y de cambio

- **C1 y C2:** el dueño es la prueba común. Una opción cumple el contrato cuando la prueba común da
  «TODO BIEN» contra su URL.
- **Agregar** una clave, una ruta o una comprobación es seguro: el cliente ignora lo que no conoce (Q3-A).
- **Quitar o renombrar** exige un ADR, la aprobación del humano y cambiar en el mismo push `web/js/`,
  `contrato_api.yaml` y la prueba común.
- **C3:** `version_esquema` sube con cualquier cambio que no sea agregar; U17 rechaza una versión que no
  conoce.
- **C4:** la tabla de casos solo crece. Una unidad de reglas que agrega casos los agrega a
  `casos_reglas.json` en el mismo push, y las demás opciones los pasan antes de U17.
- **C5:** igual que C1; además, cambiar una columna obliga a cambiar el diccionario de FR9.3 en el mismo
  push.
- Push directo a `develop` para el humano y el asistente; el resto del equipo por PR (`team.md`,
  «Corrections»). Antes de cada push: el simulacro y, si se tocó una opción o el contrato, la prueba
  común.

## Preguntas abiertas

| Contrato | Pregunta | Bloquea |
|---|---|---|
| C1 | `/api/publico` sin `?sala=` responde solo `{"ok": true}` en la nube. Hay que confirmar que el chequeo de salud de cada plataforma acepta esa ruta | U1 |
| C1 | El 503 por cuota: cada ADR de opción dice cómo detecta la plataforma que se quedó sin cuota | U1, U7, U11 |
| C4 | `casos_reglas.json` lo empieza U1 con las reglas mínimas, pero U4, U8 y U12 corren en paralelo. Delivery Planning fija el orden de los push a ese archivo | U4, U8, U12 |
| C5 | Formato de la copia en las opciones sin SQLite (FR4.3) | U6, U10, U14 |

## Sources

- `unit-of-work.md` y `unit-of-work-dependency.md` (units-generation/): unidades, dueños y «Puntos de
  integración».
- `components.md` (domain-design/): Acceso, ApiHttp, Salas, CatalogoColegios, reglas de ADR-001,
  «Cómo se sabe la sala en cada petición» y «Cambios que el docente ve en el panel».
- `requirements.md` (requirements-analysis/): FR4.1, FR4.3, FR6.1, FR6.2, FR9.1–FR9.5, FR10.3, FR11.3–FR11.7,
  FR12.2–FR12.4.
- `aidlc/spaces/default/codekb/Reto_Desinformacion_Colegios/api-documentation.md`: las 16 rutas de hoy.
- `contract-design-questions.md`: Q1 a Q6.
