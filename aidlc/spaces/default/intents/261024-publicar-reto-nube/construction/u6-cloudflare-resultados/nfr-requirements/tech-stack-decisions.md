# Tecnología — U6

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Lo de U1, U4 y U5 sigue igual; aquí solo lo que U6 agrega. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Tema | Decisión | Por qué |
|---|---|---|
| Copia (FR4.3) | Guion SQL `.sql` armado en `src/servicios/copia.js` (ADR-W14) | El objeto no tiene archivos ni `VACUUM INTO`; sin paquetes |
| Paquete | ZIP «stored» con CRC-32 propio en `src/servicios/zip.js` (ADR-W15) | Sin paquetes; `deflate-raw` queda como mejora posible |
| CSV | `src/servicios/csv.js` con `csv_python` (hoy: `;`, BOM, CRLF, coma decimal, `json_como_python`) y `csv_paquete` (coma, sin BOM, LF, RFC 4180) (ADR-W16) | Igualdad byte a byte con la versión local y paquetes fáciles de unir |
| Fechas | `fecha_iso_bogota` con desplazamiento fijo −05:00 (ADR-W18) | Colombia no tiene horario de verano; sin depender de datos de zonas |
| Almacén de copias | Tablas `copias` y `copia_trozos` (512 KiB), migración 3 (ADR-W17, ADR-W10) | Límite de 2 MB por fila; un solo borrado al cerrar |
| Versión de la app | `src/version.json` escrito por `copiar.sh`, ignorado por git (ADR-W17) | El Worker no ve git |
| Exportación | `src/servicios/resultados.js` (vista del participante, tablero) y `src/servicios/exportacion.js` (CSV, paquete, copias, reiniciar) | Dos bloques de `components.md`; archivos que caben en un PR |
| Pruebas | `node:test` para csv, zip, copia y fechas (`pruebas/exportacion.test.js`); reabrir la copia con SQLite lo hace la prueba común en Python (`sqlite3.executescript` en memoria), porque la prueba común ya es Python y Node 24 solo trae `node:sqlite` como experimental | Sin paquetes; la comprobación que necesita SQLite vive donde SQLite ya existe |
| Diccionario | `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`, Markdown en español | FR9.3 |
| Paquetes nuevos | Ninguno | FR7.6 |
