# Seguridad — diseño U1

Diseño no funcional de U1. Las decisiones están en `../decisions.md` (ADR-W1 a ADR-W5); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U1-S1 | Lista blanca de claves al armar cada pregunta pública; `revision` solo en resultados |
| U1-S2 | `opaco_de` en `reglas.js` con Web Crypto (ADR-W4) |
| U1-S3 | `banco.json` en `src/`, fuera del directorio de recursos estáticos (ADR-W5) |
| U1-S4 | `CLAVE_SEMILLERO` con `wrangler secret put`; con menos de 12 caracteres, las rutas de admin responden 500 y el registro dice por qué |
| U1-S5 | Huella SHA-256 y comparación en tiempo constante (ADR-W4) |
| U1-S6 | Solo se registran el arranque, cambios de estado y errores 500, sin datos |
| U1-S7 | Se lee el cuerpo con tope de 65.536 bytes |
| U1-S8, U1-S9 | Un único punto de salida arma las cabeceras y el 500 |
