# Observación — U6

> **Revisión 2026-10-27 (una sola sala).** Un solo reto, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`, nunca `?clave=`) y reloj por colegio (ADR-009 a ADR-011). Se quitan `?sala=`,
> `id_sala`, la clave del semillero y «Borrar la sala»; las copias se borran una a una (D7).

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U6-O1 | Se registran «Reto reiniciado (copia <id_copia>, <bytes> bytes)», «Copia borrada <id_copia>», «Migración v3 aplicada.», «copia dañada <id_copia>» y el commit de `version.json` en el arranque; nada más de esta unidad | U1-O1, NFR10, BR5.2, BR6.2, BR9.1 |
| U6-O2 | No se registran descargas de CSV, del paquete ni de copias (llevarían la hora de un docente concreto sin necesidad) | NFR10 |
| U6-O3 | `metadatos.json` es la traza de cada paquete: versión del banco, de la app y del esquema con que se jugó, para reproducir un análisis años después | FR9.1, FR9.3 |
| U6-O4 | El cierre (NFR10.1) se comprueba con dos peticiones con la clave: `GET /api/admin/copias` responde `copias: []` y `GET /api/admin/resumen` responde `participantes: []` y `colegios: []`; la guía (U17) las nombra | NFR10.1, FR8.2, BR6.2 |
| U6-O5 | El cierre de U6 deja rastro escrito: el «Recorrido de las pantallas» se anota en `code-summary.md` de U6 con fecha, persona y «sí» o «no» por línea | BR10.3, ADR-W21 |
