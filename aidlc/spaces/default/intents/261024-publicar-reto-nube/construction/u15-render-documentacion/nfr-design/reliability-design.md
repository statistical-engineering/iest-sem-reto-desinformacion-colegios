# Confiabilidad — diseño U15

Diseño no funcional de U15 (solo documentación sobre Render). Los requisitos están en `../nfr-requirements/`.

- U15-R1 y U15-R2: la fila «Sobrevive a un reinicio» se escribe en dos partes, «Gratuito: no (…)» y
  «De pago con disco: sí según documentación, sin medir (…)», cada una con su URL.
- U15-R3: la fila «Arranque en frío» dice «15 min sin tráfico → duerme; despierta en about one minute»
  y el veredicto «no cumple NFR5».
- U15-R4: en la misma fila se anota el apagado a mitad del reto: «Render may also restart a Free web
  service at any time» y, con disco, el corte de unos segundos en cada despliegue. Es la razón de la regla
  de hoy «no desplegar con un reto en curso», que se conserva en cualquier guía.
- U15-R5: NFR11 no se evalúa; la casilla de líneas de código dice «sin escribir».
