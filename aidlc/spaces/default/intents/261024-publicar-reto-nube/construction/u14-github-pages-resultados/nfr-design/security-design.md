# Seguridad — diseño U14

Diseño no funcional de U14. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U14-S1 | `calcular(..., estado_sala)` de U12 quita `verdad` y `multitud_acierta` salvo en `resultados`; `Resultados.estado` agrega `revision` solo si `sala.estado == "resultados"` y `participante.estado == "finalizado"`; `test_resultados.py` recorre el JSON con `claves_de` y `SECRETAS` |
| U14-S2 | Todas las rutas de exportación están en la tabla con nivel «clave»; `Acceso` resuelve la sala y cada consulta lleva `WHERE sala = ?` |
| U14-S3 | La copia se arma con `INSERT INTO copia.participantes (…) SELECT id, sala, '' AS codigo, '' AS token, '' AS semilla, nombre, …` y `INSERT INTO copia.salas (…) SELECT …, '' AS clave_huella, …`; `participantes.csv` tiene una lista fija de columnas que no incluye las secretas; `test_exportacion.py` abre la copia con `sqlite3` y lee el CSV |
| U14-S4 | Cada `INSERT … SELECT` filtra por `sala`; `colegios` se copia solo con `id_colegio IN (SELECT id_colegio FROM sala_colegios WHERE sala = ?)` más los definitivos a los que apuntan |
| U14-S5 | Las descargas pasan por el punto de salida de U11 con `Access-Control-Expose-Headers: Content-Disposition` agregado cuando hay `Content-Disposition` |
| U14-S6 | `Salas.borrar` ejecuta `DELETE FROM copias WHERE sala = ?` y luego cuenta en cada tabla; responde `{ok: true, filas_restantes: 0}` |
| U14-S7 | El diccionario describe columnas con tipos y ejemplos inventados («Ana Pérez» no: se usan ejemplos genéricos como «<nombre del equipo>»); lo revisa el PR |
