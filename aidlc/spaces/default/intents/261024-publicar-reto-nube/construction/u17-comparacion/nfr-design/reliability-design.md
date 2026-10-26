# Confiabilidad — diseño U17

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-R1: la casilla «Sobrevive a un reinicio» de una opción medida se escribe «sí (<archivo>.json,
  `sobrevive_reinicio: true`)» o «no». `null` se escribe «sin evidencia» y la opción no pasa; U2 tiene
  que reiniciar de verdad (`wrangler deploy` a mitad de la prueba vale como reinicio en Workers).
- U17-R2: la casilla NFR11 lista el `id` de la comprobación de puntos y clasificación iguales a la local.
- U17-R3: `COMPARACION.md` lleva al pie la fecha de cierre y el commit; el ADR-C3 pasa a «Accepted» con
  esa fecha. Una medición nueva que cambie un «sí» por un «no» reabre el ADR: se anota como
  «Superseded by ADR-C5» y se vuelve a elegir.
- U17-R4: si ninguna pasa todo, el ADR-C3 queda en «Proposed» con la lista de NFR que fallan por opción
  y una pregunta al humano (OQ2): qué NFR relajar y hasta dónde. No se elige a ciegas.
- U17-R5: sección 7 de la guía: para Workers, «En el computador del semillero, ejecuta
  `npx wrangler@4.148.0 rollback` y elige la versión anterior. Los datos de las salas no se pierden.»
  (`u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`, «Volver atrás»).
