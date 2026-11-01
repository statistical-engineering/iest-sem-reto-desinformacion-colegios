# Plan de Bolts

Un **Bolt** es una pasada de construcción sobre un pedazo del trabajo, que termina en algo que
funciona. Aquí hay un Bolt por unidad (Q3-A, `delivery-planning-questions.md`). Las unidades salen de
`unit-of-work.md`; el orden respeta las dependencias de `unit-of-work-dependency.md`, y los contratos son
los de `contract-summary.md`.

**Corte delgado** es la versión mínima de punta a punta que demuestra que todo encaja. Va primero, y el
humano aprueba su punto de control antes de seguir (`team.md`, «Walking Skeleton»).

## Orden

**Revisión del 2026-10-25 (una sola sala, solo Cloudflare).** Con los requisitos, el dominio, las
unidades y el contrato revisados, solo quedan los Bolts de Cloudflare, la prueba común y la comparación.
B1 (U1) ya pasó su punto de control y está desplegado; B5 (U15) y B6 (U16) ya están hechos.

| Tanda | Bolts | Por qué en esta tanda |
|---|---|---|
| 0 | B1 (U1) | Hecho: corte delgado desplegado en Workers |
| 1 | B4 (U4), B5 (U15), B6 (U16) | U4 es lo más riesgoso que queda: los 10 tipos de pregunta tienen que dar los mismos puntos que la versión local. U15 y U16 ya están hechos |
| 2 | B9 (U5) | Necesita las reglas de U4; quita el multi-sala del corte y agrega clave docente, colegios y relojes |
| 3 | B11 (U6), B2 (U2) | U6 necesita U5; U2 se completa contra el contrato de una sala y mide la versión terminada |
| 4 | B13 (U17) | Necesita U2, U6, U15 y U16 |

**Se saltan** con la aprobación del humano («lo referente solo a cloudflare», 2026-10-25), sin borrar
sus unidades (`project.md`, «Corrections»): B7 (U3, fugas de la versión local), Apps Script (U7 a U10)
y GitHub Pages (B3, B8, B10, B12: U11 a U14). U17 las escribe en la tabla como «no pasa» (Apps Script,
por contrato) o «no se construye» (GitHub Pages), con el motivo. Los archivos a medias que dejó U11 en
`despliegues/github-pages/` no se versionan.

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

### B1 — U1 `u1-cloudflare-corte` (corte delgado, hecho)

- Desplegado en Workers con un Durable Object y SQLite; la prueba común mínima dio «TODO BIEN». Lo que
  dejó para varias salas (clave del semillero, claves de sala, crear sala) lo reemplaza B9.

### B4 — U4 `u4-cloudflare-reglas`

- **Hecho cuando:** las «calculadoras» de C4 en JS (los 10 tipos de pregunta, bono, orden total con los
  tiempos relativos al arranque del colegio, podio general, puesto por grado y nota, transiciones de
  estado, entrega por colegio) pasan todos los casos de `casos_reglas.json` y sus pruebas `node --test`
  corren sin servidor ni base.
- **Qué nos dice:** si las reglas dan los mismos puntos y el mismo orden que la versión local.

### B9 — U5 `u5-cloudflare-salas` (reto, colegios y relojes)

- **Hecho cuando:** el servicio tiene una sola sala, la clave docente única (`CLAVE_DOCENTE`), la lista de
  colegios del docente con «Arrancar reloj», el vencimiento por colegio, todas las transiciones de estado
  y las acciones del docente; las copias de `web/` muestran el aviso de espera y el panel de colegios; la
  prueba común mínima, ya cambiada a la clave docente, da «TODO BIEN» contra `wrangler dev`.
- **Qué nos dice:** si el reloj por colegio funciona de punta a punta.

### B11 — U6 `u6-cloudflare-resultados`

- **Hecho cuando:** el tablero muestra el podio general y por grado, el panel tiene su resumen, salen
  los CSV y el paquete, y «Reiniciar» pide BORRAR y guarda la copia antes.

### B2 — U2 `u2-prueba-comun`

- **Hecho cuando:** la prueba común tiene las dos partes de FR12.3 para una sala, da «TODO BIEN» contra
  `wrangler dev` (vencimiento con `DURACION_MINIMA_MIN=2`, D9) y contra la URL de Workers (sin vencimiento real), y su
  parte base da «TODO BIEN» contra la versión local. Escribe el JSON de C3.

### B5 — U15 y B6 — U16 (hechos)

- Columnas de Render y Cloudflare Containers con cifras de la documentación oficial.

### B13 — U17 `u17-comparacion`

- **Hecho cuando:** `despliegues/COMPARACION.md` tiene Cloudflare medido y las demás opciones con su
  motivo, el ADR final registra la elección y `PUBLICAR_EN_INTERNET.md` y el `LEEME.md` de Cloudflare
  explican cómo desplegarla, también desde Windows con Git Bash.
- **Qué nos dice:** si Cloudflare queda lista para el aula.

## Comando de verificación

Cada punto de control corre un comando real: el que se eligió en el punto de control de B1 (la prueba
común contra la versión de Cloudflare), más `node --test` de las pruebas de la opción.

## Sources

- `requirements.md` (requirements-analysis/): FR6, FR12.1 a FR12.6 y los NFR de FR12.5.
- `components.md` (domain-design/): reglas de salas que pasan a U5 y U13.
- `unit-of-work.md`, `unit-of-work-dependency.md` y `unit-of-work-story-map.md` (units-generation/).
- `contract-summary.md` y `reviews/review-01.md` (contract-design/).
- `team-practices.md` (practices-discovery/) y `team.md`: corte delgado, pruebas y forma de subir cambios.
- `delivery-planning-questions.md`: Q1 a Q8, todas A (2026-10-25).
