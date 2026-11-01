# Confiabilidad — U6

> **Revisión 2026-10-27 (una sola sala).** Un solo reto, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`, nunca `?clave=`) y reloj por colegio (ADR-009 a ADR-011). Se quitan `?sala=`,
> `id_sala`, la clave del semillero y «Borrar la sala»; las copias se borran una a una (D7). Nuevos
> U6-R8 y U6-R9 (pantallas completas, ADR-W21).

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U6-R1 | Reiniciar es atómico: o la copia queda guardada y el reto vacío (participantes, respuestas, eventos y colegios), o nada cambia; nunca un reto vacío sin copia | FR1.1, R-17, BR5.2, `phases/construction.md` («Error Handling») |
| U6-R2 | La copia se puede volver a abrir: la prueba común ejecuta el guion con `sqlite3` de Python (`executescript`) en memoria y cuenta las filas por tabla contra las del resumen | FR4.3, ADR-W14 |
| U6-R3 | La copia descargada es la que se guardó: se comprueba su SHA-256 al leerla y un fallo responde 500 con registro, no un archivo truncado | ADR-W17, BR5.3 |
| U6-R4 | Los dos CSV de hoy son idénticos byte a byte a los de la versión local con las mismas respuestas; la prueba común los compara | FR4.3, NFR11, ADR-W16 |
| U6-R5 | El `.zip` abre con `unzip -t` sin errores y con las herramientas de Windows y macOS (formato «stored» con CRC-32 correcto) | FR9.1, ADR-W15 |
| U6-R6 | Desplegar U6 sobre un objeto con datos de U5 conserva el reto: la migración 3 crea `copias` y `copia_trozos`, guarda las tablas `v1_*` con filas como `migracion_v1.sql` y solo después las borra, todo en una transacción | NFR4, ADR-W10, BR9.1 |
| U6-R7 | Si falta `src/version.json`, el Worker no se construye (fallo rápido al desplegar) en vez de escribir una versión inventada en los metadatos | FR9.1, BR7.1 |
| U6-R8 | Ninguna pantalla de `web/` llama una ruta que no existe ni escribe `?sala=` o `?clave=`; lo comprueba `node --test` sin servidor | FR4.1, BR10.1, ADR-W21 |
| U6-R9 | Cada llamada de las tres pantallas responde con la forma que la pantalla lee (comprobaciones `pantalla_*` de la prueba común) y las tres se recorren completas en `wrangler dev` sin errores en la consola | FR4.2, BR10.2, BR10.3 |
