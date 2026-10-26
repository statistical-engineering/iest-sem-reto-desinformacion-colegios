# Observación — diseño U1

Diseño no funcional de U1. Las decisiones están en `../decisions.md` (ADR-W1 a ADR-W5); los requisitos en `../nfr-requirements/`.

- `console.log` en el servidor solo para arranque, cambio de estado de sala y errores 500 (U1-O1).
- Se leen con `npx wrangler@4.148.0 tail` (U1-O2).
- Salud: `GET /api/publico` (U1-O3).
