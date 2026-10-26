# Rapidez — diseño U16

Diseño no funcional de U16 (solo documentación sobre Cloudflare Containers). Los requisitos están en
`../nfr-requirements/`.

- U16-P1: las cuatro filas de medición se escriben como «Sin medir: exige Workers Paid (FR12.2a)». No se
  inventa una latencia.
- U16-P2: la fila «Arranque en frío» dice «1 a 3 s según documentación; dentro de NFR5, sin medir», con
  la URL, y en la misma casilla el sueño a los 10 min y la parada en cualquier momento, porque en esta
  opción arrancar en frío significa arrancar **sin datos**.
