# Rapidez — diseño U17

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-P1 y U17-P2: cada casilla de latencia se escribe como «<valor> ms (<archivo>.json)» y el veredicto
  de la tabla «Veredicto por NFR» compara con 1.000 y 1.500 ms. Sin redondear hacia abajo: 1.001 ms no
  cumple.
- U17-P3: «arranque en frío» se escribe con el valor del JSON; si es `null`, con la cita oficial de que no
  duerme (Workers: `u1-cloudflare-corte/nfr-design/reliability-design.md`, «no se duerme como Render»)
  y el veredicto «cumple según documentación». Render y Containers traen las cifras de U15 y U16.
- U17-P4: la sección 4 de la guía dice «abre el enlace unos minutos antes» solo si la ganadora duerme;
  si no, dice que no hace falta, con la URL.
