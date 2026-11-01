# Unidades de trabajo

Una unidad es un pedazo de trabajo que se construye, se prueba y se entrega por su cuenta. Las unidades
salen del plan aprobado por el humano (2026-10-25, `units-generation-questions.md`):

- Q1-A: cada opción tiene 4 unidades por capa, y la prueba común es otra unidad;
- Q2-A: solo se construyen las opciones gratuitas. Render y Cloudflare Containers entran con datos de su
  documentación oficial;
- Q3-A: una unidad corrige solo las fugas de respuestas en la versión local (OQ9 aprobada).

**Revisión del 2026-10-25 (una sola sala, solo Cloudflare).** Con los requisitos revisados (FR11, FR12.2c)
y los ADR-009 a ADR-011, las unidades se quedan con los mismos ids y carpetas, pero:

- solo se construyen las de Cloudflare (U1, U4, U5, U6), la prueba común (U2) y la comparación (U17);
- U5 pasa de «salas y catálogo» a **reto, colegios y relojes**: quita el multi-sala que dejó U1 (clave
  del semillero, claves de sala, crear sala) y agrega la clave docente única y el reloj por colegio;
- U3 (fugas locales) y las cadenas de Apps Script (U7 a U10) y GitHub Pages (U11 a U14) se saltan con
  la aprobación del humano («lo referente solo a cloudflare»), sin borrarlas (`project.md`,
  «Corrections»); en la tabla de comparación quedan como «no pasa» o «no se construye»;
- U15 y U16 ya están hechas.

Los componentes son los de `../domain-design/components.md` y las decisiones las de
`../domain-design/decisions.md`. Aquí no se decide qué se construye primero: eso va en Delivery Planning.

## Tabla de unidades

| Unit ID | Directorio | Opción | Qué entrega | Tipo | Tamaño |
|---|---|---|---|---|---|
| U1 | `u1-cloudflare-corte` | Cloudflare Workers | Corte delgado inicial del proyecto: crear y abrir una sala, inscribirse y responder una pregunta, más la prueba común mínima | service | L |
| U2 | `u2-prueba-comun` | todas | La prueba común completa contra la URL de cualquier versión (FR12.3) | library | L |
| U3 | `u3-local-fugas` | local | Corrige solo las fugas de FR6 en `2_Aplicacion_Reto/` (se salta) | service | S |
| U4 | `u4-cloudflare-reglas` | Cloudflare Workers | Las «calculadoras» de ADR-001 en JS, con sus pruebas | library | M |
| U5 | `u5-cloudflare-salas` | Cloudflare Workers | Reto de una sala, clave docente, lista de colegios con su reloj, inscripción y examen completos | service | L |
| U6 | `u6-cloudflare-resultados` | Cloudflare Workers | Resultados, podio general y por grado, panel, CSV, paquete y copias | service | M |
| U7 | `u7-apps-script-corte` | Apps Script | Corte delgado desplegado (se salta) | service | M |
| U8 | `u8-apps-script-reglas` | Apps Script | Las «calculadoras» en Apps Script, con sus pruebas (se salta) | library | M |
| U9 | `u9-apps-script-salas` | Apps Script | Salas, claves, catálogo, inscripción y examen completos (se salta) | service | L |
| U10 | `u10-apps-script-resultados` | Apps Script | Resultados, tablero, CSV, paquete y copias (se salta) | service | M |
| U11 | `u11-github-pages-corte` | GitHub Pages | Corte delgado desplegado: pantallas en Pages y API en otro servicio (se salta) | service | M |
| U12 | `u12-github-pages-reglas` | GitHub Pages | Las «calculadoras» en el lenguaje de su API, con sus pruebas (se salta) | library | M |
| U13 | `u13-github-pages-salas` | GitHub Pages | Salas, claves, catálogo, inscripción y examen completos (se salta) | service | L |
| U14 | `u14-github-pages-resultados` | GitHub Pages | Resultados, tablero, CSV, paquete y copias (se salta) | service | M |
| U15 | `u15-render-documentacion` | Render | Cifras de la documentación oficial para la comparación, sin desplegar | spec | S |
| U16 | `u16-cloudflare-containers-documentacion` | Cloudflare Containers | Igual que U15 | spec | S |
| U17 | `u17-comparacion` | todas | `despliegues/COMPARACION.md`, ADR final de elección y guía del ganador | spec | M |

## Qué hace cada unidad

### U2 `u2-prueba-comun`

- **Responsabilidad:** completa la prueba común mínima que dejó U1 en `despliegues/prueba_comun/`. Es
  una sola prueba que recibe la URL y la **clave docente** por argumento o variable de entorno, igual
  contra la nube y contra la versión local (revisión del 2026-10-25: ya no hay clave del semillero). Tiene dos partes (FR12.3):
  - **base:** las 29 comprobaciones de `simulacro.py 40`, sin debilitar ninguna;
  - **nueva:** todo lo que FR12.5 pone en la prueba común:
    - las fugas (FR6.3);
    - los relojes por colegio (FR11.7): dos colegios arrancados a distinta hora, cada uno con sus
      90 minutos y su bono medido desde su arranque; 40 equipos de 3 colegios (NFR1);
    - 403 con clave ausente, incorrecta o enviada en la URL (NFR9);
    - los mismos puntos y la misma clasificación que la versión local con las mismas respuestas (NFR11);
    - la latencia (NFR2, NFR3), un reinicio a mitad de la prueba (NFR4) y el arranque en frío (NFR5);
    - el consumo medido frente a la cuota gratuita (NFR6).
- **Despliegue:** no se despliega; corre desde la computadora de quien prueba.
- **Notas:**
  - no abre la base de datos ni pide una ruta para mover el reloj: el vencimiento se prueba esperando
    con una duración corta (`despliegues/prueba_comun/LEEME.md`, «Pendiente de decidir»);
  - contra la versión local, la parte base da «TODO BIEN»; las de fugas fallan mientras U3 siga saltada, y
    las de relojes por colegio no aplican;
  - `simulacro.py` no se copia ni se cambia;
  - **salida:** termina en «TODO BIEN» o con la lista de comprobaciones que fallaron, y escribe un archivo
    JSON con cada medición (latencias, consumo, arranque en frío). U17 llena `COMPARACION.md` con ese
    archivo. El tipo `library` se mantiene: no es un servicio desplegado, y su interfaz es ese JSON.

### U3 `u3-local-fugas`

- **Responsabilidad:** corregir en `2_Aplicacion_Reto/servidor.py` solo las fugas de FR6.1 y FR6.2. Es
  la única excepción a FR12.1 (OQ9, aprobada en Q3-A). Para FR6.2 aplica el mismo mecanismo de ADR-006
  (HMAC de la semilla, con `hmac` de Python 3.9+), y la base y `respuestas.csv` siguen con los ids del
  banco.
- **Despliegue:** la versión local de hoy (red local, túnel, modo prueba).
- **Notas:**
  - `python3 pruebas/simulacro.py 40` termina en «TODO BIEN», y la parte de fugas de U2 pasa;
  - no cambia ninguna pantalla, puntaje ni desempate (`project.md`, «Forbidden»);
  - no se aplica con un reto en curso.

### U1, U7, U11: corte delgado de cada opción

- **Responsabilidad:** la versión mínima desplegada de esa opción, con enlace fijo. Con la clave del
  semillero se crea y se abre una sala; después un estudiante se inscribe con el código de sala, comienza
  y responde una pregunta. Es el primer punto de control de la opción.
- **U1 es el corte inicial del proyecto** (elección del humano, 2026-10-25: Cloudflare Workers). Además
  de su corte, crea la **prueba común mínima** en `despliegues/prueba_comun/`: chequeo de salud, crear y
  abrir una sala, inscribirse, comenzar y responder. U7 y U11 dependen de U1 solo para usar esa prueba;
  no usan nada de la carpeta `despliegues/cloudflare/` (FR12.2). U2 la completa.
- **Componentes:** ApiHttp, Persistencia y Arranque de la opción, completos desde el corte, y la copia de
  AppEstudiante, PanelDocente, Tablero y Graficos de `2_Aplicacion_Reto/web/` a su carpeta `web/`. Trae
  una versión mínima de Banco y Calificacion que ya sale con los ids opacos de ADR-006, así que la opción
  nace sin la fuga de FR6.2; la unidad de reglas la completa. Trae también lo mínimo de Salas, Acceso y
  CicloDeSala: crear una sala con la clave del semillero, su clave de sala y pasarla de «inscripción» a
  «abierto». La unidad de salas lo completa. Incluye `GET /api/publico` para el chequeo
  de salud, y el banco nunca se sirve como archivo estático (NFR8).
- **Antes del código:** el ADR de esa opción, aprobado por el humano (FR12.2b). Va en
  `aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/<directorio del corte>/decisions.md`
  (por ejemplo `construction/u1-cloudflare-corte/decisions.md`). Fija el lenguaje, el runner de pruebas,
  el almacén, cómo se despachan las rutas, el mecanismo para «no cruzarse» y la huella de la clave. Los
  límites de cuota se citan con la URL oficial.
- **Cómo se verifica:** con la prueba común mínima contra su URL, que termina en «TODO BIEN», y con
  `GET /api/publico` en el hosting (requisitos, «Constraints»; `team.md`, «Walking Skeleton»). Es un
  comando que se repite igual en las tres opciones. Cuando U2 está lista, la parte base completa lo
  vuelve a comprobar.
- **Despliegue:** en el plan gratuito de la opción, a mano (FR5.2).
- **Notas:**
  - el `LEEME.md` de la carpeta tiene los pasos para desplegarla (FR8.0);
  - en GitHub Pages (U11), el ADR elige el servicio gratuito de la API.

### U4, U8, U12: reglas de cada opción

- **Responsabilidad:** los componentes Banco, Calificacion, Clasificacion, CicloDeSala, LimpiezaEntrada y
  Experimento como «calculadoras»: reciben datos y la hora, y devuelven datos (ADR-001, ADR-006). Cada
  regla lleva sus pruebas, que corren sin servidor ni base (FR7.1, FR10.5, NFR12).
- **Despliegue:** va dentro del servicio de su opción. Depende del corte porque usa la carpeta, el
  lenguaje y el runner que fijó el ADR del corte, y reemplaza la versión mínima de Banco y Calificacion.
- **Notas:**
  - las mismas tablas de casos en todas las opciones, para que dos versiones que difieran fallen en las
    pruebas y no el día del reto;
  - el desempate exacto: `tiempo_respuestas` relativo a `inicio` con tope en la duración, redondeo a 9
    decimales e `id` creciente (`components.md`, Clasificacion);
  - las transiciones de la sala solo permiten lo que ofrece el panel (FR7.4).

### U5 `u5-cloudflare-salas`: reto, colegios y relojes (U9 y U13 se saltan)

- **Responsabilidad:** los componentes Reto, CicloDelReto, Acceso, Inscripcion y Examen completos
  (ADR-004, ADR-007, ADR-009, ADR-010, ADR-011):
  - una sola fila de reto con estado, configuración y código de sala que fija el docente;
  - la clave docente única como secreto del hosting, solo por `X-Clave-Admin` (quita la clave del
    semillero, las claves de sala y «crear sala» que dejó U1);
  - la lista de colegios que carga el docente (pegar un nombre por línea o uno a uno);
  - el reloj de cada colegio: «Abrir el reto» arranca los colegios con equipos, «Arrancar reloj» arranca
    uno, el inicio del equipo es el arranque de su colegio y el vencimiento se aplica por colegio;
  - las acciones del docente: forzar entrega, anular y reactivar, eliminar inscripciones sin empezar;
  - todos los cambios de estado (inscripción → abierto → cerrado → resultados), cada uno confirmado.
- **Despliegue:** el mismo servicio del corte.
- **Pantallas:** cambia la copia de `web/` para:
  - la inscripción con colegio de la lista (FR10.3);
  - el aviso «Tu colegio todavía no ha empezado. Espera la señal del docente.» (FR3.1);
  - el panel con la lista de colegios, el estado de su reloj y «Arrancar reloj» (FR11.5).
- **Notas:** configurar el reto (duración, colegios) se permite antes de cerrar; agregar un colegio
  también con el reto abierto (ADR-009).

### U6 `u6-cloudflare-resultados` (U10 y U14 se saltan)

- **Responsabilidad:** los componentes Resultados y Exportacion: vista del participante, tablero con
  podio general y clasificación por grado (FR2.5), resumen del panel (`/api/admin/resumen`), los dos CSV
  de hoy, el paquete de datos, «Reiniciar» con BORRAR y su copia previa, y la descarga (FR4.3, FR9,
  FR11.4, FR11.6).
- **Pantallas:** cambia la copia de `web/` para el podio general y por grado del tablero y la descarga
  del paquete (`components.md`, «Cambios que el docente y el estudiante ven»).
- **Despliegue:** el mismo servicio del corte.
- **Notas:**
  - la copia lleva todas las filas del reto, pero no `token`, `semilla` ni `codigo` personal;
  - al terminar, la opción pasa la prueba común completa (U2) en «TODO BIEN».

### U15 `u15-render-documentacion` y U16 `u16-cloudflare-containers-documentacion`

- **Responsabilidad:** llenar la columna de la opción en `despliegues/COMPARACION.md` con cifras de la
  documentación oficial (cuota, costo, persistencia, arranque en frío), cada una con su URL.
- **Despliegue:** ninguno. No se gasta dinero sin aprobar antes el monto y un tope (FR12.2a).
- **Notas:** si el humano aprueba un costo más adelante, se agregan unidades para construirla.

### U17 `u17-comparacion`

- **Responsabilidad:**
  - llenar `despliegues/COMPARACION.md` con lo que midió U2 (FR12.4);
  - aplicar «pasa todo» y el orden de FR12.5 y FR12.6;
  - escribir el ADR final, que elige la ganadora y la de respaldo, en
    `aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u17-comparacion/decisions.md`;
  - reescribir `PUBLICAR_EN_INTERNET.md` para la ganadora (FR8.1, FR8.2, FR8.3).
- **Despliegue:** ninguno.
- **Notas:**
  - las carpetas de las opciones que pierden se borran solo después de que el humano apruebe el ADR
    final (FR12.6);
  - U17 empieza cuando U6 terminó y U2 midió Cloudflare (revisión del 2026-10-25: las demás opciones
    no se construyen). Si Cloudflare pasa todo, es la elegida, sin respaldo construido (FR12.2c);
  - si una opción no pasa su corte o se abandona, el humano aprueba saltar sus unidades restantes. Esa
    opción queda en la tabla como «no pasa», con el motivo, y U17 ya no la espera. Si ninguna pasa todo,
    se aplica OQ2 (FR12.6).

## Cómo se trabaja

- **El humano y el asistente** suben directo a `develop`, sin PR (`team.md`, «Corrections», 2026-10-25).
  Es una excepción a FR5.3 solo para ellos. La revisión de PR no corre en ese caso, así que antes de cada
  push corren a mano lo mismo que ella: los ganchos de pre-commit y `python3 pruebas/simulacro.py 40` en
  «TODO BIEN». Si el cambio toca una opción, también la prueba común contra su URL.
- **El resto del equipo** trabaja en una rama `feat/despliegue-<opción>-<qué>` creada desde `develop`,
  con PR de máximo 400 líneas de código (`despliegues/LEEME.md`).
- **Una unidad grande** se parte en varios PR si no cabe en 400 líneas.
- **Ninguna unidad**, salvo U3, cambia `2_Aplicacion_Reto/`. Antes de U3 se comprueba con
  `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` (FR12.1). Después de U3, con
  `git diff --stat <último commit de U3> HEAD -- 2_Aplicacion_Reto/`. Los dos tienen que salir vacíos.
- **Un paquete nuevo**, en cualquier lenguaje, se aprueba antes de agregarlo (FR7.6).
