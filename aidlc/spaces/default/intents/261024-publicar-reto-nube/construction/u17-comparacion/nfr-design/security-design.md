# Seguridad — diseño U17

Diseño no funcional de U17. Las decisiones están en `../decisions.md` (ADR-C1 a ADR-C4); los requisitos en
`../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U17-S1 | Antes del push: `grep -n -i -E "clave|token|KQMT-|\?clave=" despliegues/COMPARACION.md PUBLICAR_EN_INTERNET.md aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u17-comparacion/decisions.md`; solo pasan menciones genéricas («la clave de sala»), nunca un valor |
| U17-S2 | En «Veredicto por NFR», la fila NFR8 lista los `id` de las comprobaciones `fugas` del JSON que pasaron, por ejemplo `fuga_verdad_cerrado`; una sola en `false` da «no» |
| U17-S3 | La fila NFR9 lista los `id` de las comprobaciones de 403 y, al lado, «código revisado por <persona>, <fecha>» |
| U17-S4 | Sección 1 de la guía: «La clave del semillero es una contraseña larga, de 12 letras o números como mínimo. Guárdala en el Drive privado del semillero. Nunca la escribas en el enlace ni la subas al repositorio.» Sección 3: «La clave de la sala se muestra una sola vez. Cópiala y entrégala al docente por un canal privado.» |
| U17-S5 | La fila NFR10 y NFR10.1 se escribe «sí: cierre probado por <persona> el <fecha>; sin filas ni archivos en el proveedor» o «sin evidencia» |
| U17-S6 | Sección 6 de la guía: «El repositorio es público: cualquiera puede verlo. Por eso los archivos con nombres de estudiantes van al Drive privado del semillero y nunca al repositorio.» |
