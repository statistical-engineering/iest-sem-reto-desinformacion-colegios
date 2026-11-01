# Escala — U2

> **Revisión 2026-10-27 (una sola sala).** La carga deja las 10 salas: son 40 equipos de 3 colegios
> (20, 12 y 8) con relojes que arrancan a 0, 20 y 40 s de la apertura, un tablero y un panel (BR6.1,
> BR7.1). La estimación de peticiones se rehízo con esa carga.

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba mide de cada opción. Salen de `requirements.md` (NFR1, NFR6) y del diseño funcional
(`rules.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-E1 | La carga por defecto es la de NFR1: 40 equipos en 3 colegios, A 20, B 12 y C 8, con un tablero sondeando `GET /api/publico` cada 2 s y un panel sondeando `GET /api/admin/resumen` cada 3 s; `--participantes` la cambia sin tocar el código (A la mitad hacia arriba, C la quinta parte hacia arriba con mínimo 2, B el resto) | NFR1, BR6.1, BR7.1 |
| U2-E2 | Una corrida completa hace como máximo 8.000 peticiones. Estimación con 40 participantes: calibración (40 inscripciones, 40 comienzos y 40 estados, unos 4 representantes × 45 respuestas y las llamadas del panel) ≈ 320; inscripción, colegios y comienzo ≈ 130; respuestas 40 × 41 × 2 = 3.280; tablero ≈ 110 y panel ≈ 60 durante la carga, más un sondeo cada 10 s en las esperas (≈ 20 en `wrangler dev`, ≈ 60 en local); cierre, resúmenes, CSV, paquete, copias, pantallas y restauración ≈ 200. Total ≈ 4.200, un 4,2 % de las 100.000 peticiones diarias del plan gratuito de Workers (https://developers.cloudflare.com/workers/platform/limits/, «Requests 100,000 per day», consultado el 2026-10-25). La cifra real va al JSON (`peticiones`) | NFR6, BR7.4 |
| U2-E3 | En modo local los 40 se inscriben con su colegio como texto y comparten un solo reloj; el tablero y el panel sondean igual, para que la carga de lectura sea comparable | NFR1, BR6.1 |
| U2-E4 | La prueba corre en una computadora común: 42 hilos de la biblioteca estándar como máximo, sin más de 42 conexiones abiertas a la vez y menos de 100 MB de memoria (las misiones de 40 participantes, unos 200 KB cada una) | BR7.1 |
