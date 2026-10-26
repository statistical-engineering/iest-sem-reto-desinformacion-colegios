# Observación — diseño U5

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W13); los requisitos en `../nfr-requirements/`.

- `console.log` solo en: «Arranque: banco <versión>, <n> preguntas, esquema v<n>.», «Migración v<n>
  aplicada.», «Sala <código>: <estado anterior> -> <estado nuevo>», «Sala <código> creada.» y «Sala
  <código> borrada.» (U5-O1). Nada en registro, responder, acciones ni claves (U5-O2).
- Los errores 500 siguen con `console.error` y traza, sin cuerpo de la petición.
- `GET /api/admin/salas` es la vista de operación del semillero (U5-O3); no se agrega ningún panel de
  métricas.
- `publico` sin `?sala=` responde antes de tocar la base (U5-O4), como U1.
