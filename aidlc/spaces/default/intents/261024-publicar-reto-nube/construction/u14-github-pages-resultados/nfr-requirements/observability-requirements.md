# Observación — U14

Requisitos no funcionales de U14, resultados y exportación de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U14 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U14-O1 | Se registran «Sala <código>: reiniciada, copia <id_copia>» y «Sala <código>: borrada con <n> copias»; nunca nombres ni contenido | `.claude/rules/python-code.md` («Logs»), NFR10 |
| U14-O2 | `metadatos.json` lleva `version_app` y `version_banco`: con el paquete se sabe qué código y qué banco produjeron los datos | FR9.1 |
| U14-O3 | `GET /api/admin/salas` sigue siendo la vista del semillero para confirmar, tras la guía de cierre, que no queda ninguna sala con datos | NFR10.1 |
