# Rapidez — U11

Requisitos no funcionales de U11, el corte delgado de GitHub Pages con la API en PythonAnywhere. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial consultada el 2026-10-25 (URL en `../decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U11-P1 | `POST /api/responder` + `GET /api/estado`: p95 ≤ 1 s, contando la consulta previa `OPTIONS` cuando el navegador la hace | Prueba común contra la URL de la API (U2 lo mide con 40 participantes); el `OPTIONS` se mide aparte una vez por cliente | NFR2, hallazgo C-04 |
| U11-P2 | `GET /api/publico?sala=`: p95 ≤ 1,5 s | Prueba común | NFR3 |
| U11-P3 | Un solo worker atiende de a una petición (plan gratuito: «1 web app with 1 web worker»); ninguna petición del corte tarda más de 50 ms dentro del candado, para que 40 personas no se encolen más de 2 s en el peor caso | Prueba `unittest` que llama a `application` 200 veces y mide el tiempo medio; revisión del código | NFR1, NFR2, ADR-G1, ADR-G5 |
| U11-P4 | El banco se lee una vez al arrancar el proceso y queda en memoria; el examen de cada participante se guarda en memoria por semilla para no rehacer los HMAC en cada `/api/estado` | Revisión del código | NFR2 |
| U11-P5 | La espera de un código personal inexistente (BR3.4) dura 0,3 s y corre fuera del candado, así no frena a los demás más que ese tiempo si el worker atiende de a uno | Prueba `unittest` con dos llamadas seguidas | NFR2, suposición A3 |
| U11-P6 | La primera carga de una pantalla desde Pages pesa menos de 300 KB (HTML, CSS, JS y `config.js`), y la caché de Pages (`max-age=600`) la sirve sin volver a bajar durante el reto | `curl -sI` y suma de tamaños en `web/` | NFR3, ADR-G2 |
