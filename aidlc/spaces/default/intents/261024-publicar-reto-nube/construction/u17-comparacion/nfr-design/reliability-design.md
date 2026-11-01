# Confiabilidad — diseño U17

> **Revisión 2026-10-27 (una sola sala).** U17-R1 lee las dos corridas (ADR-C5); U17-R3 reabre con ADR-C7 porque ADR-C5 ya existe; U17-R5 advierte no volver a la versión de varias salas y pasa a la sección 8 de la guía.

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

- U17-R1: la casilla «Sobrevive a un reinicio» de Cloudflare se escribe «sí (`cloudflare_<fecha>.json` y
  `cloudflare-dev_<fecha>.json`, `sobrevive_reinicio: true`)» o «no». `null` en cualquiera de las dos se
  escribe «sin evidencia» y Cloudflare no pasa; U2 tiene que reiniciar de verdad (`wrangler deploy` a
  mitad de la prueba en la pública, `--reinicio comando` en dev, ADR-C5).
- U17-R2: la casilla NFR11 lista los `id` `mismas_fracciones_que_local` y `mismos_csv_que_local`.
- U17-R3: `COMPARACION.md` lleva al pie la fecha de cierre y el commit; el ADR-C3 pasa a «Accepted» con
  esa fecha. Una medición nueva que cambie un «sí» por un «no» reabre el ADR: se anota como
  «Superseded by ADR-C7» (ADR-C5 y ADR-C6 ya existen) y se vuelve a elegir.
- U17-R4: si Cloudflare no pasa todo, el ADR-C3 queda en «Proposed» con la lista de NFR que fallan por opción
  y una pregunta al humano (OQ2): qué NFR relajar y hasta dónde. No se elige a ciegas.
- U17-R5: sección 8 de la guía: «En el computador del semillero, ejecuta `npx wrangler@4.148.0 rollback`
  y elige la versión anterior. Los datos del reto no se pierden. Nunca vuelvas a una versión anterior a
  la de una sala.» (`u1-cloudflare-corte/infrastructure-design/infrastructure-specification.md`, «Volver
  atrás»; ADR-W19 de U5).
