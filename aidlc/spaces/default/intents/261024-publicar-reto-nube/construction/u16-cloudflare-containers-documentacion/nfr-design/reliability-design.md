# Confiabilidad — diseño U16

Diseño no funcional de U16 (solo documentación sobre Cloudflare Containers). Los requisitos están en
`../nfr-requirements/`.

- U16-R1 y U16-R2: la fila «Sobrevive a un reinicio» se escribe como «No con el Dockerfile actual (disco
  efímero, URL). Alternativas documentadas: instantáneas inmutables o FUSE a R2 (URL), las dos cambian la
  aplicación». El veredicto NFR4 va en negrita.
- U16-R3: la fila «Arranque en frío» dice «1 a 3 s según documentación» con veredicto «dentro de NFR5,
  sin medir».
- U16-R4: en la misma fila se anota el apagado: «duerme a los 10 min; la plataforma puede pararlo en
  cualquier momento (SIGTERM, hasta 15 min, SIGKILL)». Como el disco es efímero, cada parada equivale a
  perder el reto en curso: por eso NFR4 no se cumple aunque se pagara.
- U16-R5: NFR11 no se evalúa; la casilla de líneas de código dice «sin escribir».
