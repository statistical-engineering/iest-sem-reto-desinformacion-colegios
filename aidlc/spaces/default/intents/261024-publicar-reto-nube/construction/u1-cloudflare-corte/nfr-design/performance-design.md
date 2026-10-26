# Rapidez — diseño U1

Diseño no funcional de U1. Las decisiones están en `../decisions.md` (ADR-W1 a ADR-W5); los requisitos en `../nfr-requirements/`.

- El Worker no hace lógica: reenvía `/api/*` al Durable Object (U1-P3).
- El banco se lee una vez por instancia del objeto y queda en memoria (U1-P4).
- Las páginas se sirven como recursos estáticos, sin pasar por el objeto.
- Responder hace una transacción SQLite pequeña: lectura del participante, inserción, suma de puntos (U1-P1).
