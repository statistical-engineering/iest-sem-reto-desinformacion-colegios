# Rapidez — diseño U11

Diseño no funcional de U11. Las decisiones están en `../decisions.md` (ADR-G1 a ADR-G7); los requisitos en `../nfr-requirements/`.

- El proceso WSGI carga el banco y abre SQLite una vez, al importar `src/wsgi.py`; el examen de cada
  participante se guarda en un diccionario por semilla con tope de 200 entradas (U11-P4).
- Cada petición de la API entra al candado del proceso solo para leer o escribir en SQLite; armar el
  JSON y calcular HMAC pasa fuera (U11-P3). Responder hace una transacción `BEGIN IMMEDIATE` corta:
  lectura del participante, inserción, suma de puntos (U11-P1).
- La espera de BR3.4 (0,3 s) se hace con `time.sleep` fuera del candado (U11-P5).
- `OPTIONS` se responde antes de la tabla de rutas y sin tocar la base; el navegador lo guarda 600 s
  (`Access-Control-Max-Age`), así solo la primera petición de cada pantalla paga el viaje extra (U11-P1).
- Las pantallas se sirven desde Pages con su caché de 600 s; `config.js` pesa una línea (U11-P6).
- Si U2 mide un p95 por encima de 1 s con 40 personas y un solo worker, la salida prevista es reducir el
  sondeo del panel docente mientras se proyecta el tablero (misma guía que U1); no hay forma de pedir más
  workers sin pagar.
