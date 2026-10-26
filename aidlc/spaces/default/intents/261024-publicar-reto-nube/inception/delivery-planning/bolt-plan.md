# Plan de Bolts

Un **Bolt** es una pasada de construcción sobre un pedazo del trabajo, que termina en algo que
funciona. Aquí hay un Bolt por unidad (Q3-A, `delivery-planning-questions.md`). Las unidades salen de
`unit-of-work.md`; el orden respeta las dependencias de `unit-of-work-dependency.md`, y los contratos son
los de `contract-summary.md`.

**Corte delgado** es la versión mínima de punta a punta que demuestra que todo encaja. Va primero, y el
humano aprueba su punto de control antes de seguir (`team.md`, «Walking Skeleton»).

## Orden

Las unidades de una misma tanda no dependen entre sí y se construyen en paralelo (Construcción etapa
por etapa y en paralelo, elección del humano del 2026-10-25).

| Tanda | Bolts | Por qué en esta tanda |
|---|---|---|
| 0 | B1 (U1) | Corte delgado; nada empieza antes de su punto de control |
| 1 | B2 (U2), B3 (U11), B4 (U4), B5 (U15), B6 (U16) | Primero lo más riesgoso: el corte de GitHub Pages y la prueba común (Q1-A). U15 y U16 no dependen de nadie |
| 2 | B7 (U3), B8 (U12), B9 (U5) | U3 necesita U2; U12 necesita U11; U5 necesita U4 |
| 3 | B10 (U13), B11 (U6) | Siguen sus cadenas |
| 4 | B12 (U14) | Último de GitHub Pages |
| 5 | B13 (U17) | Necesita U2, U6, U14, U15 y U16 |

**Apps Script (U7 a U10) no se construye** (Q2-A). Queda «no pasa» por contrato, con la evidencia del
hallazgo C-01 (`contract-design/reviews/review-01.md`). Al entrar en Construcción se te pide aprobar
que se salten esas cuatro unidades; con eso dejan de detener a U17 (`unit-of-work-dependency.md`, «Si se
abandona una opción»). U17 escribe Apps Script en la tabla como «no pasa», con el motivo (FR12.6).

## Reglas para todos los Bolts

Todo Bolt se da por hecho cuando además de lo suyo cumple:

- `python3 pruebas/simulacro.py 40`, desde `2_Aplicacion_Reto/`, en «TODO BIEN»;
- los ganchos de pre-commit pasan (ruff, mensaje de commit);
- `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` sale vacío (FR12.1), salvo en B7 (U3); después
  de B7, contra su último commit;
- si toca una opción o el contrato, la prueba común da «TODO BIEN» contra su URL;
- ningún archivo lleva una clave, una respuesta correcta ni datos de un reto real;
- el código nuevo tiene pruebas `unittest` y llega al 80 % de cobertura de líneas (`team.md`, «Testing
  Posture»).

La copia de `web/` en cada opción va en su propio commit, sin cambios, y no cuenta en el límite de 400
líneas; sí cuentan los cambios que se le hagan después (Q7-A).

## Bolts

### B1 — U1 `u1-cloudflare-corte` (corte delgado)

- **Qué prueba de la arquitectura:** Worker, D1 y un Durable Object por sala trabajando juntos detrás de
  un enlace fijo; claves de sala y del semillero; la prueba común corriendo contra una URL.
- **Hecho cuando:**
  - con la clave del semillero se crea y se abre una sala, un estudiante se inscribe y responde una
    pregunta, y `GET /api/publico` responde `{"ok": true}`;
  - la prueba común mínima (`despliegues/prueba_comun/src/prueba.py`, Python sin paquetes, Q6-A) da
    «TODO BIEN» contra la URL de Workers y su parte base contra la versión local;
  - existe `despliegues/prueba_comun/contrato_api.yaml` con las 16 rutas de hoy y los cambios de C1;
  - el contrato ya incluye los arreglos de la revisión que U1 necesita (Q4-A): ids opacos también en
    `respuestas` y `revision` de `/api/estado` (C-02), claves y códigos de sala en mayúsculas (C-03),
    copia sin `token`, `semilla`, `codigo` ni `clave_huella` (C-06) y la forma de los datos de cada
    regla en `casos_reglas.json` (C-05);
  - el ADR de la opción (`construction/u1-cloudflare-corte/decisions.md`) está aprobado antes de
    escribir su código.
- **Qué nos dice:** si Workers cumple el enlace fijo, la persistencia y la latencia con la API de hoy.
- **Demo:** abrir el enlace desde un celular con datos móviles, inscribirse y responder.
- **Si no pasa** (Q5-A): la prueba común mínima se termina igual y se verifica contra la versión local;
  U1 se cierra «no pasa» con el motivo y las otras opciones siguen.

### B2 — U2 `u2-prueba-comun`

- **Hecho cuando:** la prueba común tiene las dos partes de FR12.3 y da «TODO BIEN» contra Workers;
  contra la versión local, la parte base da «TODO BIEN» y las de fugas fallan hasta B7. Escribe el JSON
  de C3. Incluye los hallazgos menores que le tocan (C-07 a C-15), entre ellos:
  - comprobaciones de fugas para toda clave nueva que llegue al navegador sin clave (C-14);
  - tolerar un 5xx sin JSON de la plataforma (C-15).
- **Qué nos dice:** si la misma prueba sirve para todas las opciones.
- **Nota:** la duración mínima de un reto es 10 minutos, así que cada corrida completa espera al menos
  10 minutos reales (C-09).

### B3 — U11 `u11-github-pages-corte`

- **Hecho cuando:** con la clave del semillero se crea y se abre una sala, un estudiante se inscribe y
  responde una pregunta, y la prueba común mínima da «TODO BIEN». Resuelve CORS y la URL base de la API
  en `web/js/` (C-04). Su ADR se aprueba antes del código.
- **Qué nos dice:** si las pantallas en Pages con la API en otro servicio cumplen el contrato.

### B4 — U4 `u4-cloudflare-reglas`

- **Hecho cuando:** las «calculadoras» de C4 en JS pasan todos los casos de `casos_reglas.json` y sus
  pruebas unitarias corren sin servidor ni base.
- **Qué nos dice:** si las reglas dan los mismos puntos y el mismo orden que la versión local.

### B5 — U15 `u15-render-documentacion` y B6 — U16 `u16-cloudflare-containers-documentacion`

- **Hecho cuando:** las cifras de la tabla de comparación salen de la documentación oficial, cada una
  con su URL y su fecha de consulta. No se despliega nada de pago.

### B7 — U3 `u3-local-fugas`

- **Hecho cuando:** las comprobaciones de fugas de la prueba común pasan contra la versión local y
  `simulacro.py 40` sigue en «TODO BIEN» sin cambios.

### B8 — U12, B10 — U13, B12 — U14 (GitHub Pages) y B9 — U5, B11 — U6 (Workers)

- **Hecho cuando:** cada uno completa su capa (`unit-of-work.md`) y la prueba común da «TODO BIEN» contra
  la URL de su opción. U5 y U13 traen las reglas de salas que quedaron de Domain Design: configurar la
  sala solo antes de abrirla, y «Borrar la sala» solo con la sala cerrada y escribiendo BORRAR.
- **Qué nos dice:** si cada opción pasa todo (FR12.5).

### B13 — U17 `u17-comparacion`

- **Hecho cuando:** `despliegues/COMPARACION.md` tiene las cinco opciones con las cifras medidas, el ADR
  final elige la ganadora y `PUBLICAR_EN_INTERNET.md` se reescribe solo para ella (FR12.5).
- **Qué nos dice:** cuál opción usar en el aula.

## Comando de verificación

Cada punto de control corre un comando real. La prueba común todavía no existe: la crea B1. Por eso el
comando se elige en el punto de control de B1, con la prueba ya escrita.

## Sources

- `requirements.md` (requirements-analysis/): FR6, FR12.1 a FR12.6 y los NFR de FR12.5.
- `components.md` (domain-design/): reglas de salas que pasan a U5 y U13.
- `unit-of-work.md`, `unit-of-work-dependency.md` y `unit-of-work-story-map.md` (units-generation/).
- `contract-summary.md` y `reviews/review-01.md` (contract-design/).
- `team-practices.md` (practices-discovery/) y `team.md`: corte delgado, pruebas y forma de subir cambios.
- `delivery-planning-questions.md`: Q1 a Q8, todas A (2026-10-25).
