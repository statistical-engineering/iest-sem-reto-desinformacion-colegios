# Escala — diseño U6

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18); los requisitos en `../nfr-requirements/`.

- Copias (U6-E1, U6-E2, U6-E3): `copias (id_copia, id_sala, creada, nombre_archivo, bytes, sha256)` y
  `copia_trozos (id_copia, n, trozo TEXT)` con clave primaria `(id_copia, n)`; `guardar_copia` parte el
  texto en trozos de 524.288 caracteres (como mucho 4 bytes por carácter en UTF-8 quedan en ≈ 2 MB solo
  en el peor caso teórico; con texto en español real un trozo pesa ≈ 0,6 MB). Para que nunca dependa del
  peor caso, el corte se hace por **bytes** UTF-8 (`TextEncoder`) y se guardan trozos como `BLOB`,
  garantizando ≤ 512 KiB por valor.
- No hay límite de copias por sala en el código; la guía de cierre borra la sala y con ella todas.
- Tablero (U6-E4): consultas por `id_sala` con el índice implícito de la clave foránea; se agrega
  `CREATE INDEX participantes_sala_estado ON participantes (id_sala, estado)` en la migración 3 para
  que `publico`, `resumen` y `vencer_tiempos` no recorran otras salas.
- Paquete (U6-E5): una respuesta de ≈ 1 MB; si el ensayo de U2 muestra que pesa más de 10 MB en algún
  caso, se activa `deflate-raw` por entrada (ADR-W15) sin cambiar la API.
