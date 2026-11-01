# Tecnología — U6

> **Revisión 2026-10-27 (una sola sala).** Un solo reto, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`, nunca `?clave=`) y reloj por colegio (ADR-009 a ADR-011). Cambian el almacén de
> copias (se borran una a una, D7), las pruebas (se agrega `pantallas.test.js`, ADR-W21) y la exportación
> (también corre la migración 3).

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Lo de U1, U4 y U5 sigue igual; aquí solo lo que U6 agrega. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Tema | Decisión | Por qué |
|---|---|---|
| Copia (FR4.3) | Guion SQL `.sql` armado en `src/servicios/copia.js` (ADR-W14) | El objeto no tiene archivos ni `VACUUM INTO`; sin paquetes |
| Paquete | ZIP «stored» con CRC-32 propio en `src/servicios/zip.js` (ADR-W15) | Sin paquetes; `deflate-raw` queda como mejora posible |
| CSV | `src/servicios/csv.js` con `csv_python` (hoy: `;`, BOM, CRLF, coma decimal, `json_como_python`) y `csv_paquete` (coma, sin BOM, LF, RFC 4180) (ADR-W16) | Igualdad byte a byte con la versión local y paquetes fáciles de unir |
| Fechas | `fecha_iso_bogota` con desplazamiento fijo −05:00 (ADR-W18) | Colombia no tiene horario de verano; sin depender de datos de zonas |
| Almacén de copias | Tablas `copias` y `copia_trozos` (512 KiB), migración 3 (ADR-W17, ADR-W10); cada copia se borra sola con `POST /api/admin/copia/borrar` | Límite de 2 MB por fila; «Reiniciar» conserva las copias (D7) |
| Versión de la app | `src/version.json` escrito por `copiar.sh`, ignorado por git (ADR-W17) | El Worker no ve git |
| Exportación | `src/servicios/resultados.js` (vista del participante y tablero) y `src/servicios/exportacion.js` (CSV, paquete, copias, reiniciar, migración 3) | Dos bloques de `components.md`; archivos que caben en un PR |
| Pruebas | `node:test` para csv, zip, copia, fechas y diccionario (`pruebas/exportacion.test.js`) y para las llamadas de las pantallas (`pruebas/pantallas.test.js`, ADR-W21); reabrir la copia con SQLite lo hace la prueba común en Python (`sqlite3.executescript` en memoria), porque Node 24 solo trae `node:sqlite` como experimental | Sin paquetes; la comprobación que necesita SQLite vive donde SQLite ya existe |
| Diccionario | `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`, Markdown en español | FR9.3 |
| Paquetes nuevos | Ninguno; `wrangler` sigue fijado en `npx wrangler@4.148.0` | FR7.6 |
