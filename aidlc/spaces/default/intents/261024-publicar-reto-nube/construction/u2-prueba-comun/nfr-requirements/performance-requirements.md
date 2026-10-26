# Rapidez — U2

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma** (una
herramienta que corre en la computadora de quien prueba, no un servicio desplegado), más lo que la prueba
mide de cada opción. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`,
`rules.md`) y del contrato (`contract-summary.md`, C2 y C3). Decisiones tomadas por el asistente con la
potestad que dio el humano («potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U2-P1 | La prueba no es el cuello de botella de la medición: 40 hilos reales (uno por participante) y 10 de tablero, cada petición con tope de 20 s, sin esperas artificiales dentro de la fase de carga | Revisión del código de `carga.py`; la fase de respuestas con 40 × 41 preguntas termina en menos de 3 minutos contra la versión local | NFR2, NFR3, BR7.1 |
| U2-P2 | Mide el p95 de `POST /api/responder` + `GET /api/estado` y el p95 de `GET /api/publico?sala=` con el método del vecino más cercano, con al menos 1.000 muestras de responder y 300 del tablero | `test_carga.py` sobre el percentil; conteo de muestras en el JSON (`detalle`) | NFR2, NFR3 |
| U2-P3 | Una corrida completa dura como máximo 20 minutos con la duración mínima de 10 minutos: calibración ≤ 3 min, carga ≤ 3 min, espera real de 10 min, cierre ≤ 2 min | Tiempo entre `inicio` y `fin` del JSON | C-09, BR4.2 |
| U2-P4 | La calibración cuesta como máximo 1 minuto de cómputo local: las huellas se calculan una vez por participante y la clave por texto se arma una sola vez | `test_guion.py`; tiempo de la calibración impreso en el paso 3 | BR2.3 |
