# Escala — diseño U17

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-E1: la casilla NFR1 se escribe «sí: 10 salas, 40 participantes (<archivo>.json, comprobaciones
  `salas_*`)». Si el JSON trae menos salas o participantes, «no».
- U17-E2: la casilla «Consumo frente a la cuota» de una opción medida se escribe
  «<peticiones> peticiones en <duración> = <porcentaje> de <cuota> (<URL oficial>)». Para Workers la
  cuota es 100.000 peticiones por día (https://developers.cloudflare.com/workers/platform/limits/) y
  100.000 filas SQLite escritas por día (https://developers.cloudflare.com/durable-objects/platform/pricing/),
  las dos citadas en U1; cumple si las dos quedan ≤ 50 %. Si U2 mide una sesión más corta que 90 minutos,
  la casilla extrapola a 90 y lo dice.
- U17-E3: Render y Cloudflare Containers copian la casilla de `scalability-design.md` de U15 y U16.
- U17-E4: la sección 0 de la guía dice, para la ganadora, qué pasa si se agota la cuota a mitad del
  reto (Workers: la plataforma responde con su propio error y el navegador muestra «Error 5xx», U1-R4).
