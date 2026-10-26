# Observación — diseño U14

Diseño no funcional de U14. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- `logging.info("Sala %s: reiniciada, copia %s", codigo, id_copia)` y
  `logging.info("Sala %s: borrada con %d copias", codigo, n)` (U14-O1).
- `metadatos.json` con `version_app` de `src/version.txt` y `version_banco` de `src/banco_huella.json`
  (U14-O2).
- `GET /api/admin/salas` como comprobación final de la guía de cierre (U14-O3).
