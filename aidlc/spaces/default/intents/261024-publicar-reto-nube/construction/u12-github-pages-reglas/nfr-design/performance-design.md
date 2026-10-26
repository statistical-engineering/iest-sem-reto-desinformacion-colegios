# Rapidez — diseño U12

Diseño no funcional de U12. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- `examen_publico` calcula los HMAC con `hmac.new(..., "sha256")` una vez por opción y los ordena con
  `sorted`; con 42 preguntas y unas 200 opciones son menos de 5 ms en esta máquina (U12-P1). La caché por
  semilla de `servicio.py` evita repetirlo en cada sondeo.
- `ordenar` usa una sola clave de orden con `sorted(key=...)` y el redondeo a 9 decimales con `round`
  (U12-P2); `calcular` recorre las respuestas una vez y acumula por grupo y publicación.
- Sin E/S: `reglas.py` solo importa `hmac`, `hashlib`, `base64`, `unicodedata`, `random`, `math`, `json`
  (U12-P3).
