# Integración y despliegue — U5

> **Revisión 2026-10-27 (una sola sala).** `verificar.sh` usa `CLAVE_DOCENTE` y ya no corre la prueba
> con dos salas; la prueba de migración sigue el flujo F8 de `functional-spec.md`; el despliegue
> comprueba el estado del reto, no una lista de salas.

- Sin despliegue automático; a mano y sin reto en curso (`project.md`, «Mandated»). Antes de
  desplegar, el paso 1 de `infrastructure-specification.md` comprueba que el reto no está «abierto».
- Antes de cada push a `develop`: `bash despliegues/cloudflare/herramientas/verificar.sh`, que en U5:
  1. corre las pruebas `node --test` de las reglas, nombrando cada archivo (`project.md`, «Corrections»);
  2. crea `.dev.vars` con `CLAVE_DOCENTE` al azar (24 caracteres) si no existe, o le agrega esa línea si
     solo tiene la `CLAVE_SEMILLERO` de U1;
  3. arranca `wrangler dev` y corre la prueba común mínima en modo nube con la clave docente;
  4. corre el simulacro de la versión local, que debe decir «TODO BIEN».
- La prueba de la migración (F8, U5-R1) se hace a mano una vez antes del despliegue, sobre una copia del
  estado local de `wrangler dev` con datos del corte (`.wrangler/`, ignorado por git); su resultado se
  anota en `code-summary.md`.
- El parche `cambios_web.patch` se prueba corriendo `copiar.sh` dos veces desde cero y comparando las
  huellas de `web/`, como U1.
- La revisión de PR no cambia. U5 supera 400 líneas; el humano y el asistente suben directo a
  `develop`; otra persona la parte por módulo de `servicios/` (`team.md`, «Corrections»).
