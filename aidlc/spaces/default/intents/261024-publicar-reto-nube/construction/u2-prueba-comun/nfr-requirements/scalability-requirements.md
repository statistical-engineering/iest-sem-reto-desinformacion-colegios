# Escala — U2

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba mide de cada opción. Salen de `requirements.md` (NFR1, NFR6) y del diseño funcional
(`rules.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-E1 | La carga por defecto es la de NFR1: 10 salas de tamaños 10, 7, 6, 5, 4, 3, 2, 1, 1 y 1 (40 participantes), abiertas a la vez, con un tablero sondeando cada 2 s por sala; `--participantes` y `--salas` la cambian sin tocar el código | NFR1, BR6.1 |
| U2-E2 | Una corrida completa hace como máximo 8.000 peticiones. Estimación con 40 participantes: calibración 40 × 3 + 4 × 45 ≈ 300; inscripción y comienzo 40 × 3 = 120; respuestas 40 × 41 × 2 = 3.280; tableros 10 × 180 s / 2 s = 900 en la carga y 10 × 600 s / 10 s = 600 en la espera; cierre, resúmenes y CSV ≈ 150; pantallas 10. Total ≈ 5.400, un 5,4 % de las 100.000 peticiones diarias del plan gratuito de Workers (https://developers.cloudflare.com/workers/platform/limits/, «Requests 100,000 per day», consultado el 2026-10-25). La cifra real va al JSON (`peticiones`) | NFR6, BR7.4 |
| U2-E3 | En modo local la misma carga va a una sola sala de 40; los 10 hilos de tablero sondean esa sala para que la carga de lectura sea comparable | NFR1, BR6.1 |
| U2-E4 | La prueba corre en una computadora común: 50 hilos de la biblioteca estándar, sin más de 50 conexiones abiertas a la vez y menos de 100 MB de memoria (las misiones de 40 participantes, unos 200 KB cada una) | BR7.1 |
