# Observación — diseño U5

> **Revisión 2026-10-27 (una sola sala).** Ya no hay salas creadas ni borradas que registrar; se
> registran los cambios de estado del reto y los relojes arrancados (U5-O1 revisado).

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20); los requisitos en `../nfr-requirements/`.

- `console.log` solo en: «Arranque: banco <versión>, <n> preguntas, esquema v<n>.», «Migración v<n>
  aplicada.», «Reto: <estado anterior> -> <estado nuevo>» y «Reloj arrancado: <colegio>.» (U5-O1). Nada
  en registro, responder, acciones sobre participantes ni claves (U5-O2).
- Los errores 500 siguen con `console.error` y traza, sin cuerpo de la petición; si falta
  `CLAVE_DOCENTE` se registra «Falta CLAVE_DOCENTE o tiene menos de 12 caracteres.», nunca el valor.
- La tarjeta «Colegios» del panel es la vista de operación (U5-O3); no se agrega ningún panel de
  métricas.
- `GET /api/publico` sin parámetros es tablero y salud (U5-O4); responde 500 si el arranque falló, para
  que la prueba de humo lo note.
