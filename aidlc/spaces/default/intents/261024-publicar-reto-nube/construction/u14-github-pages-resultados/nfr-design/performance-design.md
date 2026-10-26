# Rapidez — diseño U14

Diseño no funcional de U14. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- `/api/publico?sala=`: una consulta de finalizados con `JOIN` a colegios y una de respuestas del
  experimento, ambas con `WHERE sala = ?`; `ordenar` y `calcular` en Python fuera del candado (U14-P1).
- Paquete: dentro del candado solo se leen las filas de la sala y se construye la copia temporal
  (U14-P3); `zipfile` y `csv` corren fuera, sobre las filas ya leídas (U14-P2, U14-P4).
- La copia usa `ATTACH DATABASE ? AS copia` y `INSERT INTO copia.<tabla> SELECT … WHERE sala = ?` por
  tabla; seis sentencias, sin bucles en Python.
- Los CSV de hoy se generan con `csv.writer` sobre `io.StringIO` y se devuelven completos (no en
  streaming): con 40 personas pesan menos de 100 KB.
