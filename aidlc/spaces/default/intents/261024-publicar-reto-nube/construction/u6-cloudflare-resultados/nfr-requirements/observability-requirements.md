# Observación — U6

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U6-O1 | Se registran «Sala <código> reiniciada (copia <id_copia>, <bytes> bytes)», «copia dañada <id_copia>» y el commit de `version.json` en el arranque; nada más de esta unidad | U1-O1, NFR10 |
| U6-O2 | No se registran descargas de CSV ni de paquetes (llevarían la sala y la hora de un docente concreto sin necesidad) | NFR10 |
| U6-O3 | `metadatos.json` es la traza de cada paquete: versión del banco, de la app y del esquema con que se jugó, para reproducir un análisis años después | FR9.1, FR9.3 |
| U6-O4 | El semillero comprueba el cierre (NFR10.1) con dos peticiones: `GET /api/admin/salas` no lista la sala y `GET /api/publico?sala=` da 404; la guía (U17) las nombra | NFR10.1, FR8.2 |
