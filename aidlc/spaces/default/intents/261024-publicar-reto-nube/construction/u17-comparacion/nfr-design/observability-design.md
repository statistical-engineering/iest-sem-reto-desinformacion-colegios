# Observación — diseño U17

> **Revisión 2026-10-27 (una sola sala).** U17-O1 pide el archivo entre comillas invertidas; U17-O4 cambia la respuesta esperada del chequeo de salud y su sección de la guía (5, según `functional-spec.md`).

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-O1: convención de casilla: «<valor> (`<archivo>.json`)» para lo medido, con el nombre entre comillas
  invertidas para que lo acepte `revisar_comparacion.py`; «<valor> (<URL>, 2026-10-25)»
  para lo documentado; «<comando> sobre <commit>» para lo contado (BR17.6).
- U17-O2: la casilla NFR7 se escribe «sí: <persona> desplegó con `despliegues/<opcion>/LEEME.md` el
  <fecha>» o «sin evidencia». La persona no puede ser quien construyó la opción.
- U17-O3: la casilla NFR12 se escribe «<porcentaje> con `<comando>` (<commit>)». Para Workers el
  comando es `node --test --experimental-test-coverage despliegues/cloudflare/pruebas/reglas.test.js`
  (`u1-cloudflare-corte/nfr-requirements/tech-stack-decisions.md`; `project.md`, «Corrections»: nombrar el
  archivo, no la carpeta).
- U17-O4: sección 5 de la guía: «Abre `<enlace>/api/publico`. Si ves el nombre del evento, el servicio
  responde.» Ya no se espera `{"ok": true}`: sin parámetros devuelve los datos del tablero (ADR-011). Y
  para el semillero: dónde ver registros y consumo en el panel de Cloudflare (Workers:
  `npx wrangler@4.148.0 tail` y el tablero de Cloudflare, `u1-cloudflare-corte/infrastructure-design/monitoring-design.md`).
