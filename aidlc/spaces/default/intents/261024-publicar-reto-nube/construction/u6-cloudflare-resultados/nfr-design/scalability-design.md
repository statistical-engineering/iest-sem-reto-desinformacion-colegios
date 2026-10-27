# Escala — diseño U6

> **Revisión 2026-10-27 (una sola sala).** `copias` pierde `id_sala`; las copias ya no se borran con una
> sala sino una a una (D7); se quita el índice `participantes_sala_estado`.

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21); los requisitos en `../nfr-requirements/`.

- Copias (U6-E1, U6-E2, U6-E3): `copias (id_copia, creada, nombre_archivo, bytes, sha256)` y
  `copia_trozos (id_copia, n, contenido BLOB)` con clave primaria `(id_copia, n)`. `guardar_copia` corta
  el texto por **bytes** UTF-8 (`TextEncoder`) en trozos de 524.288 bytes, así ningún valor pasa de
  512 KiB, sin depender del peor caso de caracteres de 4 bytes.
- No hay límite de copias en el código; cada «Reiniciar» suma una y el docente las borra con «Borrar»
  después de guardar el paquete (NFR10.1).
- Tablero (U6-E4): con un solo reto y ≤ 40 participantes, las consultas recorren tablas pequeñas; no hace
  falta índice nuevo.
- Paquete (U6-E5): una respuesta de ≈ 1 MB; si el ensayo de U2 muestra más de 10 MB en algún caso, se
  activa `deflate-raw` por entrada (ADR-W15) sin cambiar la API.
