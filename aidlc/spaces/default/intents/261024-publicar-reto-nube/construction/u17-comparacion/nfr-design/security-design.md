# Seguridad — diseño U17

> **Revisión 2026-10-27 (una sola sala).** Una sola clave, `CLAVE_DOCENTE` (ADR-010): U17-S3 y U17-S4 ya no hablan de clave del semillero ni de sala; U17-S1 revisa también el `LEEME.md` de Cloudflare; secciones renumeradas según `functional-spec.md`.

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U17-S1 | Antes del push: `grep -n -i -E "clave|token|KQMT-|\?clave=" despliegues/COMPARACION.md PUBLICAR_EN_INTERNET.md despliegues/cloudflare/LEEME.md aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u17-comparacion/decisions.md`; solo pasan menciones genéricas («la clave docente», `UNACLAVEDEPRUEBA` de ejemplo en `.dev.vars`), nunca un valor |
| U17-S2 | En «Veredicto por NFR», la fila NFR8 lista los `id` de las comprobaciones `fugas` del JSON que pasaron, por ejemplo `fuga_verdad_cerrado`; una sola en `false` da «no» |
| U17-S3 | La fila NFR9 lista los `id` de la parte `claves` (403 con clave ausente, incorrecta o en la URL) y, al lado, «código revisado por <persona>, <fecha>» |
| U17-S4 | Sección 1 de la guía: «La clave docente es una contraseña larga, de 12 letras o números como mínimo. Guárdala en el Drive privado del semillero. Nunca la escribas en el enlace ni la subas al repositorio.» Sección 2: se guarda con `npx wrangler@4.148.0 secret put CLAVE_DOCENTE`, que la pide en la terminal. Sección 3: «Entrega al docente el enlace y la clave por un canal privado.» |
| U17-S5 | La fila NFR10 y NFR10.1 se escribe «sí: cierre probado por <persona> el <fecha>; `/api/admin/resumen` sin participantes y `/api/admin/copias` vacía» o «sin evidencia» |
| U17-S6 | Sección 7 de la guía: «El repositorio es público: cualquiera puede verlo. Por eso los archivos con nombres de estudiantes van al Drive privado del semillero y nunca al repositorio.» |
