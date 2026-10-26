# Confiabilidad — diseño U6

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18); los requisitos en `../nfr-requirements/`.

- Reiniciar atómico (U6-R1): `reiniciar` corre entero dentro de `transactionSync`: lee las filas, arma el
  guion, inserta `copias` y `copia_trozos`, borra eventos, respuestas y participantes de la sala y
  actualiza la sala. Un `throw` en cualquier punto deshace todo y responde 500.
- Copia reabrible (U6-R2): `armar_copia` emite SQL estándar (sin `AUTOINCREMENT` ni `REFERENCES`, para
  que abra en cualquier SQLite) y la prueba común lo ejecuta con `sqlite3.connect(":memory:").executescript`
  y cuenta filas por tabla contra las del resumen.
- Integridad (U6-R3): `sha256` se guarda al crear la copia y se recalcula al concatenar los trozos; si
  difiere, 500 y registro.
- CSV iguales a hoy (U6-R4): `csv_python` replica `csv.writer` de Python (`;`, `\r\n`, comillas solo
  cuando el valor tiene `;`, `"`, `\r` o `\n`, con `"` doblada) y `json_como_python` replica
  `json.dumps(ensure_ascii=False)` (separadores `", "` y `": "`, `true`/`false`/`null`, flotantes con
  `repr` de Python: `String(v)` coincide salvo que Python escribe `1.0` donde JS escribe `1`; por eso las
  respuestas numéricas se serializan con una función que agrega `.0` a los enteros que en la base
  entraron como flotantes de `a_numero`). La prueba común corre el mismo guion contra la versión local y
  la nube y compara los dos archivos.
- Zip válido (U6-R5): `pruebas/exportacion.test.js` arma un zip de dos entradas y comprueba firmas,
  tamaños y CRC con una segunda implementación de CRC-32 en la prueba; si `unzip` existe en la máquina,
  además corre `unzip -t`.
- Migración 3 (U6-R6): solo `CREATE TABLE copias`, `CREATE TABLE copia_trozos` y el índice
  `participantes_sala_estado`; idempotente con `IF NOT EXISTS` y `user_version = 3`.
- Versión (U6-R7): `import version from "./version.json"`; si el archivo falta, `wrangler deploy`
  falla al construir el bundle, antes de publicar nada.
