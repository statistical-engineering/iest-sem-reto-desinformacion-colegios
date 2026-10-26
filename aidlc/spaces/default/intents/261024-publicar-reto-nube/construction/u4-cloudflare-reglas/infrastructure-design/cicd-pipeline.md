# Integración y despliegue — U4

- Sin despliegue automático (`project.md`, «Mandated»): el semillero despliega a mano y sin reto en
  curso.
- Antes de cada push a `develop` (el humano y el asistente suben directo; el resto por PR de ≤ 400
  líneas, `team.md`): `bash despliegues/cloudflare/herramientas/verificar.sh`, que corre en este
  orden y se detiene al primer fallo:
  1. huellas de `casos_reglas.json` (origen y copia) iguales (U4-R5);
  2. `grep` de reloj, azar y `env` en `src/reglas/` vacío (U4-S5);
  3. `node --test --experimental-test-coverage` de cada archivo de `pruebas/`, nombrándolos uno a uno
     (`project.md`, «Corrections»), con 80 % de líneas en `src/reglas/` (U4-O3);
  4. el Worker local con la prueba común en modo nube y el simulacro local, como U1.
- La revisión de PR (`.github/workflows/revisar-pr.yml`) no cambia: ganchos, simulacro y 400 líneas. Las
  pruebas de esta unidad corren en local.
- Orden de los push a `casos_reglas.json` (pregunta abierta de C4): U4 es la primera unidad de reglas
  que llega (tanda 1, `bolt-plan.md`); U12 agrega sus casos después y U4 los pasa antes de U17.
