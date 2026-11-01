# Observación — U17

> **Revisión 2026-10-27 (una sola sala).** U17-O1 y U17-O4 cambian: dos corridas de Cloudflare y `GET /api/publico` sin parámetros devuelve los datos del tablero, ya no `{"ok": true}` (`project.md`, «Corrections», ADR-011).

Requisitos no funcionales de U17, la comparación final. Salen de `requirements.md` (NFR1 a NFR12), de
`functional-spec.md` y de `rules.md` de esta unidad. Decisiones del asistente con la potestad que dio el
humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U17-O1 | Cada casilla medida nombra, entre comillas invertidas, el archivo JSON del que salió (corrida pública o `wrangler dev`, ADR-C5) y cada casilla documentada su URL y fecha, para que cualquiera repita la lectura | FR12.4 |
| U17-O2 | La fila NFR7 se da por cumplida solo con el nombre y la fecha de la persona del semillero que desplegó la opción siguiendo solo su `LEEME.md` | NFR7 |
| U17-O3 | La fila NFR12 trae el comando de cobertura del ADR de la opción y la cifra obtenida (≥ 80 %) | NFR12 |
| U17-O4 | La guía dice cómo ver que el servicio responde (`…/api/publico` abre y muestra el nombre del evento) y dónde mira el semillero los registros y el consumo en el panel de Cloudflare | NFR7, FR8.2 |
