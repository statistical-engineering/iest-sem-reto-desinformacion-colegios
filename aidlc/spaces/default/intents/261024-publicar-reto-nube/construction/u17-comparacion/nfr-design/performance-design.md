# Rapidez — diseño U17

> **Revisión 2026-10-27 (una sola sala).** Las latencias y el arranque en frío salen solo de la corrida pública de Cloudflare; la precaución de abrir antes va en la sección 5 de la guía.

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-P1 y U17-P2: cada casilla de latencia se escribe como «<valor> ms (`cloudflare_<fecha>.json`)», de la
  corrida pública (ADR-C5), y el veredicto
  de la tabla «Veredicto por NFR» compara con 1.000 y 1.500 ms. Sin redondear hacia abajo: 1.001 ms no
  cumple.
- U17-P3: «arranque en frío» se escribe con el valor del JSON; si es `null`, con la cita oficial de que no
  duerme (Workers: `u1-cloudflare-corte/nfr-design/reliability-design.md`, «no se duerme como Render»)
  y el veredicto «cumple según documentación». Render y Containers traen las cifras de U15 y U16.
- U17-P4: la sección 5 de la guía dice «abre el enlace unos minutos antes» (`functional-spec.md`, «Forma
  de `PUBLICAR_EN_INTERNET.md`»), aunque Workers no duerme como Render: es una precaución barata.
