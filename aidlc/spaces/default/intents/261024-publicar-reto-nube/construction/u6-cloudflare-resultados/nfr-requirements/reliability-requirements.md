# Confiabilidad — U6

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U6-R1 | Reiniciar es atómico: o la copia queda guardada y la sala vacía, o nada cambia; nunca una sala vacía sin copia | FR1.1, R-17, `phases/construction.md` («Error Handling») |
| U6-R2 | La copia se puede volver a abrir: la prueba unitaria ejecuta el guion con `sqlite3` de Python (`executescript`) en memoria y cuenta las filas por tabla contra las de la sala | FR4.3, ADR-W14 |
| U6-R3 | La copia descargada es la que se guardó: se comprueba su SHA-256 al leerla y un fallo responde 500 con registro, no un archivo truncado | ADR-W17, BR5.3 |
| U6-R4 | Los dos CSV de hoy son idénticos byte a byte a los de la versión local con las mismas respuestas; la prueba común los compara | FR4.3, NFR11, ADR-W16 |
| U6-R5 | El `.zip` abre con `unzip -t` sin errores y con las herramientas de Windows y macOS (formato «stored» con CRC-32 correcto) | FR9.1, ADR-W15 |
| U6-R6 | Desplegar U6 sobre un objeto con datos de U5 conserva todo: la migración 3 solo crea `copias` y `copia_trozos` | NFR4, ADR-W10 |
| U6-R7 | Si falta `src/version.json`, el Worker no se construye (fallo rápido al desplegar) en vez de escribir una versión inventada en los metadatos | FR9.1, BR7.1 |
