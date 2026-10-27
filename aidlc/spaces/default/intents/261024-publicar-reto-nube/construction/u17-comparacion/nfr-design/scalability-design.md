# Escala — diseño U17

> **Revisión 2026-10-27 (una sola sala).** U17-E1 pasa de 10 salas a 3 colegios; U17-E2 usa la estimación de un reto real (BR17.12); U17-E4 nombra la página 1027 y la sección 8 de la guía.

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-E1: la casilla NFR1 se escribe «sí: 3 colegios, 40 participantes (`cloudflare-dev_<fecha>.json`,
  parte `relojes`)». Si el JSON trae menos colegios o participantes, «no».
- U17-E2: la casilla «Consumo frente a la cuota» de Cloudflare se escribe con la estimación de BR17.12:
  «<total> peticiones en 90 min = <porcentaje> de 100.000 (<URL oficial>, <fecha>)», con la fórmula y cada
  número en el bloque «Consumo de un reto real»; al lado va `nfr.peticiones` de la corrida pública. La
  cuota es 100.000 peticiones por día (https://developers.cloudflare.com/workers/platform/limits/) y
  100.000 filas SQLite escritas por día (https://developers.cloudflare.com/durable-objects/platform/pricing/),
  las dos citadas en U1; cumple si las dos quedan ≤ 50 %. Los intervalos de refresco se leen de
  `despliegues/cloudflare/web/static/js/*.js` y `web/tablero.html`.
- U17-E3: Render y Cloudflare Containers copian la casilla de `scalability-design.md` de U15 y U16.
- U17-E4: la sección 8 de la guía dice qué pasa si se agota la cuota a mitad del reto: Cloudflare muestra
  su página de error 1027 hasta la medianoche UTC (las 19:00 en Colombia), y el reto sigue en red local o
  con el túnel temporal (BR17.12, ADR-W20 de U5).
