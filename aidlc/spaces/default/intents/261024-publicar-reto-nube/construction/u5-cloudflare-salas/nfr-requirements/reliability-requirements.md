# Confiabilidad — U5

Requisitos no funcionales de U5, salas y examen completos en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U5-R1 | Desplegar U5 sobre un objeto con datos del corte (U1) conserva salas, colegios, participantes y respuestas: la migración a la versión 2 del esquema corre una vez y es idempotente | NFR4, ADR-W10 |
| U5-R2 | Cerrar la sala es atómico: o todos los en curso quedan entregados con la misma hora de cierre y los registrados en `no_inicio`, o nada cambia | FR3.2, ADR-004, NFR11 |
| U5-R3 | Cada acción del docente y cada cambio de configuración es una transacción; un error a mitad no deja la sala en un estado intermedio | `phases/construction.md` («Error Handling»), R-10 |
| U5-R4 | Un reinicio del objeto a mitad del reto no cambia ningún tiempo ni pierde respuestas con 200: todo está en SQLite y los tiempos son horas guardadas (U1-R2); la prueba común reinicia a mitad y compara | NFR4, FR12.5 (fila NFR4) |
| U5-R5 | Un mismo reto con una sola sala se comporta como hoy para el estudiante y el tablero: la parte base de la prueba común da «TODO BIEN» | FR11.7 |
| U5-R6 | Una migración que falla deja al objeto sin atender (500 con registro del motivo) en vez de atender con un esquema a medias | ADR-W10, `phases/construction.md` (fallar rápido) |
