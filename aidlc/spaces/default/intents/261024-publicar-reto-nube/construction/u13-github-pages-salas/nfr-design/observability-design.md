# Observación — diseño U13

Diseño no funcional de U13. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- `logging.info` con mensajes fijos: «Sala <código>: creada», «Sala <código>: <estado>», «Sala <código>:
  clave regenerada», «Sala <código>: borrada»; nunca la clave ni nombres (U13-O1).
- `GET /api/admin/salas` como vista del semillero (U13-O2).
