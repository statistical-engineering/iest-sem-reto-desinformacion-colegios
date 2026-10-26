# Unidades de trabajo

Una unidad es un pedazo de trabajo que se construye, se prueba y se entrega por su cuenta. Las unidades
salen del plan aprobado por el humano (2026-10-25, `units-generation-questions.md`):

- Q1-A: cada opción tiene 4 unidades por capa, y la prueba común es otra unidad;
- Q2-A: solo se construyen las opciones gratuitas. Render y Cloudflare Containers entran con datos de su
  documentación oficial;
- Q3-A: una unidad corrige solo las fugas de respuestas en la versión local (OQ9 aprobada).

Los componentes son los de `../domain-design/components.md` y las decisiones las de
`../domain-design/decisions.md`. Aquí no se decide qué se construye primero: eso va en Delivery Planning.

## Tabla de unidades

| Unit ID | Directorio | Opción | Qué entrega | Tipo | Tamaño |
|---|---|---|---|---|---|
| U1 | `u1-cloudflare-corte` | Cloudflare Workers | Corte delgado inicial del proyecto: crear y abrir una sala, inscribirse y responder una pregunta, más la prueba común mínima | service | L |
| U2 | `u2-prueba-comun` | todas | La prueba común completa contra la URL de cualquier versión (FR12.3) | library | L |
| U3 | `u3-local-fugas` | local | Corrige solo las fugas de FR6 en `2_Aplicacion_Reto/` | service | S |
| U4 | `u4-cloudflare-reglas` | Cloudflare Workers | Las «calculadoras» de ADR-001 en JS, con sus pruebas | library | M |
| U5 | `u5-cloudflare-salas` | Cloudflare Workers | Salas, claves, catálogo de colegios, inscripción completa y examen completo | service | L |
| U6 | `u6-cloudflare-resultados` | Cloudflare Workers | Resultados, tablero por sala, CSV, paquete y copias | service | M |
| U7 | `u7-apps-script-corte` | Apps Script | Corte delgado desplegado | service | M |
| U8 | `u8-apps-script-reglas` | Apps Script | Las «calculadoras» en Apps Script, con sus pruebas | library | M |
| U9 | `u9-apps-script-salas` | Apps Script | Salas, claves, catálogo, inscripción y examen completos | service | L |
| U10 | `u10-apps-script-resultados` | Apps Script | Resultados, tablero, CSV, paquete y copias | service | M |
| U11 | `u11-github-pages-corte` | GitHub Pages | Corte delgado desplegado: pantallas en Pages y API en otro servicio | service | M |
| U12 | `u12-github-pages-reglas` | GitHub Pages | Las «calculadoras» en el lenguaje de su API, con sus pruebas | library | M |
| U13 | `u13-github-pages-salas` | GitHub Pages | Salas, claves, catálogo, inscripción y examen completos | service | L |
| U14 | `u14-github-pages-resultados` | GitHub Pages | Resultados, tablero, CSV, paquete y copias | service | M |
| U15 | `u15-render-documentacion` | Render | Cifras de la documentación oficial para la comparación, sin desplegar | spec | S |
| U16 | `u16-cloudflare-containers-documentacion` | Cloudflare Containers | Igual que U15 | spec | S |
| U17 | `u17-comparacion` | todas | `despliegues/COMPARACION.md`, ADR final de elección y guía del ganador | spec | M |

## Qué hace cada unidad

### U2 `u2-prueba-comun`

- **Responsabilidad:** completa la prueba común mínima que dejó U1 en `despliegues/prueba_comun/`. Es
  una sola prueba que recibe la URL y la **clave
  del semillero** por argumento o variable de entorno. Con esa clave crea las salas que necesita y usa
  las claves de sala que le devuelve el servicio. Contra la versión local, que tiene una sola sala,
  recibe la clave docente. Tiene dos partes (FR12.3):
  - **base:** las 29 comprobaciones de `simulacro.py 40`, sin debilitar ninguna;
  - **nueva:** todo lo que FR12.5 pone en la prueba común:
    - las fugas (FR6.3);
    - varias salas (FR11.7) y 10 salas de tamaños desiguales que suman 40 participantes (NFR1);
    - 403 con clave ausente, incorrecta o de otra sala (NFR9);
    - los mismos puntos y la misma clasificación que la versión local con las mismas respuestas (NFR11);
    - la latencia (NFR2, NFR3), un reinicio a mitad de la prueba (NFR4) y el arranque en frío (NFR5);
    - el consumo medido frente a la cuota gratuita (NFR6).
- **Despliegue:** no se despliega; corre desde la computadora de quien prueba.
- **Notas:**
  - no abre la base de datos ni pide una ruta para mover el reloj: el vencimiento se prueba esperando
    con una duración corta (`despliegues/prueba_comun/LEEME.md`, «Pendiente de decidir»);
  - contra la versión local, la parte base da «TODO BIEN»; las de fugas pasan después de U3, y las de
    varias salas no aplican;
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

### U5, U9, U13: salas y catálogo de cada opción

- **Responsabilidad:** los componentes Salas, Acceso, CatalogoColegios, Inscripcion y Examen completos
  (ADR-002, ADR-003, ADR-004, ADR-005, ADR-007): dos claves con el prefijo `KQMT-…`, código de sala fijo
  y único, colegios provisionales, acciones del docente, entrega con un solo dueño y la tabla «Revisar y
  escribir sin cruzarse».
- **Despliegue:** el mismo servicio del corte.
- **Pantallas:** cambia la copia de `web/` de la opción para:
  - la inscripción con colegio de la lista (FR10.3);
  - el panel de salas, claves y catálogo (FR11.5);
  - el código de sala que se ve sin poder editarse (R-12);
  - el botón «Borrar la sala» del semillero.
- **Notas:** las 2 reglas que dejó la última revisión de Domain Design (`../domain-design/reviews/review-05.md`):
  - configurar la sala (duración, reloj, colegios) solo se permite antes de abrirla, como hoy, y no se
    cruza con otra operación de la sala;
  - «Borrar la sala» solo se permite con la sala cerrada y pide escribir BORRAR, igual que «Reiniciar».

### U6, U10, U14: resultados y exportación de cada opción

- **Responsabilidad:** los componentes Resultados y Exportacion: vista del participante, tablero con
  `?sala=`, resumen del panel, los dos CSV de hoy, el paquete de datos, la copia de «Reiniciar» y su
  descarga (FR4.3, FR9, FR11.4).
- **Pantallas:** cambia la copia de `web/` de la opción para el tablero con `?sala=` y la lista de copias
  para descargar (`components.md`, «Cambios que el docente ve en el panel»).
- **Despliegue:** el mismo servicio del corte.
- **Notas:**
  - la copia lleva todas las filas de la sala, pero no `token`, `semilla`, `codigo` personal ni
    `clave_huella` (`components.md`, «Copias y borrado de una sala»);
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
  - U17 empieza cuando las tres opciones gratuitas terminaron su unidad de resultados (U6, U10, U14).
    Así la tabla nunca se llena a medias;
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
