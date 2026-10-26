# Integración y despliegue — U5

- Sin despliegue automático; a mano y sin reto en curso (`project.md`, «Mandated»). Antes de
  desplegar, el paso 1 de `infrastructure-specification.md` comprueba que ninguna sala está abierta.
- Antes de cada push a `develop`: `bash despliegues/cloudflare/herramientas/verificar.sh`, que en U5
  además:
  1. arranca `wrangler dev` sobre un estado local **con datos de la versión anterior** guardado en
     `.wrangler/local-ref/` (ignorado por git) para probar la migración v2 (U5-R1);
  2. corre la prueba común en modo nube con dos salas (U5-R5, FR11.7) cuando U2 ya la tiene.
- El parche `cambios_web.patch` se prueba aplicándolo dos veces desde cero (`copiar.sh` dos veces) y
  comparando huellas, como U1.
- La revisión de PR no cambia. U5 supera 400 líneas; el humano y el asistente suben directo a
  `develop`; otra persona la parte por módulo de `servicios/` (`team.md`, «Corrections»).
