# Integración y despliegue — U17

- U17 no despliega. Sus cambios son Markdown y un commit de borrado de carpetas; el Markdown no cuenta
  en el límite de 400 líneas (`team.md`, «Corrections»). El borrado de carpetas de código sí cuenta como
  líneas borradas: si pasa de 400, se parte en un commit por carpeta.
- Orden de los push a `develop` (humano y asistente, sin PR):
  1. `docs: llenar la tabla de comparación y proponer el ADR final` (`COMPARACION.md` y `decisions.md`
     en «Proposed»).
  2. Aprobación del humano en el ADR (estado «Accepted»).
  3. `docs: reescribir la guía de publicación para <ganadora>` (`PUBLICAR_EN_INTERNET.md`).
  4. `chore: borrar las carpetas de las opciones descartadas` (BR17.9).
- Antes de cada push: ganchos de pre-commit, `python3 pruebas/simulacro.py 40` en «TODO BIEN»,
  `git diff --stat <último commit de U3> HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1) y, si se tocó la
  carpeta de la ganadora, la prueba común contra su URL (`bolt-plan.md`, «Reglas para todos los Bolts»).
- Comprobación de la guía (BR17.10): conteo de palabras por frase ≤ 30 y lectura por alguien del
  semillero ajeno al diseño (FR8.1).
- Después del commit 4, el PR final de `develop` a `main` queda habilitado cuando la ganadora esté
  desplegada y verificada (`project.md`, «Mandated»).
