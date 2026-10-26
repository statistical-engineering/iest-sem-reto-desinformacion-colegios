# Confiabilidad — diseño U14

Diseño no funcional de U14. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- Reiniciar: `BEGIN IMMEDIATE`; crear la copia temporal con `ATTACH` dentro de la misma conexión; leerla
  a bytes; `INSERT INTO copias`; `DELETE` de respuestas, eventos y participantes de la sala; `UPDATE
  salas`; `COMMIT`. Si algo falla, `ROLLBACK` y el archivo temporal se borra en `finally` (U14-R1,
  U14-R5).
- `test_exportacion.py` abre la copia con `sqlite3.connect` y compara conteos por tabla con la base
  (U14-R2).
- Nada vive en memoria entre peticiones salvo la caché del examen; el reinicio de la plataforma se mide
  con U2 (U14-R3).
- Zona horaria fija `-05:00` con `timezone(timedelta(hours=-5))` (U14-R4).
- `sqlite3.OperationalError` u `OSError` al armar la copia → 503 con `{"error": …}` y registro (U14-R5).
