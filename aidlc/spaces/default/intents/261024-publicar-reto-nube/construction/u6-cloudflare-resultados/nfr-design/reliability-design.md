# Confiabilidad — diseño U6

> **Revisión 2026-10-27 (una sola sala).** Reiniciar vacía el reto entero (también los colegios); la
> migración 3 guarda lo apartado por U5 antes de borrarlo y ya no crea el índice por sala. Nuevos los
> puntos de U6-R8 y U6-R9 (pantallas completas, ADR-W21).

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21); los requisitos en `../nfr-requirements/`.

- Reiniciar atómico (U6-R1): `reiniciar` corre entero dentro de `transactionSync`: lee las filas, arma el
  guion, inserta `copias` y `copia_trozos`, borra eventos, respuestas, participantes y colegios, reinicia
  `sqlite_sequence` de participantes y deja el reto en `inscripcion` con `abierto_en` y `cerrado_en` en
  `NULL`. Un `throw` en cualquier punto deshace todo y responde 500.
- Copia reabrible (U6-R2): `armar_copia` emite SQL estándar (sin `AUTOINCREMENT` ni `REFERENCES`, para
  que abra en cualquier SQLite) y la prueba común lo ejecuta con `sqlite3.connect(":memory:").executescript`
  y cuenta filas por tabla contra las del resumen.
- Integridad (U6-R3): `sha256` se guarda al crear la copia y se recalcula al concatenar los trozos; si
  difiere, 500 y registro.
- CSV iguales a hoy (U6-R4): `csv_python` replica `csv.writer` de Python (`;`, `\r\n`, comillas solo
  cuando el valor tiene `;`, `"`, `\r` o `\n`, con `"` doblada) y `json_como_python` replica
  `json.dumps(ensure_ascii=False)` (separadores `", "` y `": "`, `true`/`false`/`null`; `String(v)` de JS
  coincide con `repr` de Python salvo que Python escribe `1.0` donde JS escribe `1`, así que las
  respuestas numéricas que entraron como flotantes reciben `.0`). La prueba común corre el mismo guion
  contra la versión local y la nube y compara los dos archivos.
- Zip válido (U6-R5): `pruebas/exportacion.test.js` arma un zip de dos entradas y comprueba firmas,
  tamaños y CRC con una segunda implementación de CRC-32 en la prueba; si `unzip` existe en la máquina,
  además corre `unzip -t`.
- Migración 3 (U6-R6): en una transacción, `CREATE TABLE IF NOT EXISTS copias` y `copia_trozos`; si
  alguna tabla `v1_*` tiene filas, `armar_copia` las guarda como `migracion_v1.sql` (sin `clave_huella`,
  `token`, `semilla` ni `codigo`); `DROP` de las seis `v1_*`; `user_version = 3`. Si falla, el objeto
  responde 500 hasta que se corrija (BR8.1 de U5).
- Versión (U6-R7): `import version from "./version.json"`; si el archivo falta, `wrangler deploy`
  falla al construir el bundle, antes de publicar nada.
- Pantallas completas (U6-R8): `pruebas/pantallas.test.js` lee como texto `web/static/js/*.js`,
  `web/tablero.html` y `src/reto.js` (no lo importa, porque depende de `cloudflare:workers`), saca las
  rutas literales `/api/...` y las claves `"MÉTODO /api/..."` de `RUTAS`, y falla si una pantalla nombra
  una ruta ausente o escribe `?sala=` o `?clave=`.
- Pantallas con datos (U6-R9): las comprobaciones `pantalla_*` de la prueba común (U2) y el recorrido de
  `functional-spec.md` («Recorrido de las pantallas») en `wrangler dev`, con la consola abierta.
