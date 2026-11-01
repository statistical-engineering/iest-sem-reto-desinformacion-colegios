# Integración y despliegue — U17

> **Revisión 2026-10-27 (una sola sala).** Entra el commit del `LEEME.md` de Cloudflare y
> `.gitattributes` (ADR-C6); el borrado nombra las cuatro carpetas; el `git diff` de FR12.1 usa
> `c87c80d`, porque U3 se saltó.

- U17 no despliega. Sus cambios son Markdown, dos líneas de `.gitattributes` y un commit de borrado de
  carpetas; el Markdown no cuenta en el límite de 400 líneas (`team.md`, «Corrections»). El borrado de
  carpetas de código sí cuenta como líneas borradas: si pasa de 400, se parte en un commit por carpeta.
- Orden de los push a `develop` (humano y asistente, sin PR):
  1. `docs: llenar la tabla de comparación y proponer el ADR final` (`COMPARACION.md` y `decisions.md`
     en «Proposed»).
  2. `docs: dejar el LEEME de cloudflare para una sala y windows` (`despliegues/cloudflare/LEEME.md` y
     `.gitattributes`, BR17.13).
  3. Aprobación del humano en el ADR (estado «Accepted»).
  4. `docs: reescribir la guía de publicación para cloudflare` (`PUBLICAR_EN_INTERNET.md`).
  5. `chore: borrar las carpetas de las opciones descartadas` (BR17.9: `apps-script/`, `render/`,
     `cloudflare-containers/`, `github-pages/`).
- Antes de cada push: ganchos de pre-commit, `python3 pruebas/simulacro.py 40` en «TODO BIEN» y
  `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` vacío (FR12.1). U17 no toca el código de
  Cloudflare, así que la prueba común no se repite; las dos mediciones de U2 siguen valiendo.
- Comprobación de la guía (BR17.10): conteo de palabras por frase ≤ 30 y lectura por alguien del
  semillero ajeno al diseño (FR8.1). Comprobación del `LEEME.md` (BR17.13): alguien lo sigue en Windows
  con Git Bash, y `copiar.sh` y `verificar.sh` corren sin error de fin de línea.
- Después del commit 5, el PR final de `develop` a `main` queda habilitado cuando Cloudflare esté
  desplegada y verificada (`project.md`, «Mandated»).
