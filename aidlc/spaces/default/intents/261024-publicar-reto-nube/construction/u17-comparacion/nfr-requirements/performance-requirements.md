# Rapidez — U17

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U17-P1 | La fila «p95 al responder» de cada opción medida sale de `nfr.p95_responder_ms` del JSON de C3 y se compara con 1.000 ms | Lectura del JSON (BR17.1, BR17.2) | NFR2 |
| U17-P2 | La fila «p95 del tablero» sale de `nfr.p95_tablero_ms` y se compara con 1.500 ms | Lectura del JSON | NFR3 |
| U17-P3 | La fila «arranque en frío» sale de `nfr.arranque_frio_ms` (≤ 30.000 ms) o, si es `null`, de una cita oficial de que la plataforma no duerme | Lectura del JSON o URL | NFR5 |
| U17-P4 | La guía indica abrir el enlace unos minutos antes del reto si la ganadora duerme; si no duerme, lo dice con su URL | Lectura de la guía | NFR5 |
