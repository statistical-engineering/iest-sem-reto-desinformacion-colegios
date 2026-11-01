# Rapidez — U2

> **Revisión 2026-10-27 (una sola sala).** Cambian U2-P1 a U2-P3: un solo tablero sin `?sala=` y un hilo
> de panel en vez de 10 tableros, y la duración de cada corrida según contra qué corre (`wrangler dev`
> con 2 minutos, URL de Workers sin vencimiento real, versión local con 10 minutos; D9, BR4.2).

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma** (una
herramienta que corre en la computadora de quien prueba, no un servicio desplegado), más lo que la prueba
mide de cada opción. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`,
`rules.md`) y del contrato (`contract-summary.md`, C2 y C3). Decisiones tomadas por el asistente con la
potestad que dio el humano («potestad absoluta para decidir», 2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U2-P1 | La prueba no es el cuello de botella de la medición: 40 hilos reales (uno por participante), un hilo de tablero y uno de panel, cada petición con tope de 20 s, sin esperas artificiales dentro de la fase de respuestas (las únicas esperas son los arranques de B y C, a 20 y 40 s de la apertura) | Revisión del código de `carga.py`; la fase de respuestas termina en menos de 3 minutos contra la versión local | NFR2, NFR3, BR6.1, BR7.1 |
| U2-P2 | Mide el p95 de `POST /api/responder` + `GET /api/estado` y el p95 de `GET /api/publico` (sin parámetros, como el tablero) con el método del vecino más cercano, con al menos 1.000 muestras de responder y 50 del tablero; el p95 de `GET /api/admin/resumen` se anota sin umbral | `test_carga.py` sobre el percentil; conteo de muestras en el `detalle` de `nfr_p95_responder` y `nfr_p95_tablero` | NFR2, NFR3, BR7.1 |
| U2-P3 | Una corrida dura como máximo: 12 minutos contra `wrangler dev` (duración 2 minutos, dos esperas), 8 minutos contra la URL de Workers (sin espera del vencimiento) y 20 minutos contra la versión local (espera real de 10 minutos); en las tres, calibración ≤ 3 min y carga ≤ 3 min | Tiempo entre `inicio` y `fin` del JSON | C-09, D9, BR4.2 |
| U2-P4 | La calibración cuesta como máximo 1 minuto de cómputo local: las huellas se calculan una vez por calibrador y la clave por texto se arma una sola vez | `test_guion.py`; tiempo de la calibración impreso en el paso 3 | BR2.3 |
