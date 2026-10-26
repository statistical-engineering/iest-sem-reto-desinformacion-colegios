# Seguridad — U14

Requisitos no funcionales de U14, resultados y exportación de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U14 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U14-S1 | `GET /api/publico?sala=` no trae `verdad` ni `multitud_acierta` antes de «resultados»; `GET /api/estado` no trae `revision` antes de «resultados»; una prueba recorre los JSON y falla si aparece una clave secreta | FR6.1, NFR8 |
| U14-S2 | El paquete, los CSV y las copias solo salen por `/api/admin/*` con clave de la sala o del semillero; 403 sin datos en cualquier otro caso | FR9.5, NFR9 |
| U14-S3 | Ni el paquete ni la copia llevan `token`, `semilla`, `codigo` personal ni `clave_huella`; una prueba abre la copia con `sqlite3` y comprueba que esas columnas están vacías, y otra lee `participantes.csv` y comprueba que no existen | FR9.5, hallazgo C-06, R-11 |
| U14-S4 | El paquete nunca lleva ninguna clave ni filas de otra sala | FR9.5, ADR-005 |
| U14-S5 | Las descargas llevan las cabeceras CORS de origen exacto y `Access-Control-Expose-Headers: Content-Disposition`; nunca `*` | ADR-G4, BR8.1 de U11 |
| U14-S6 | Borrar la sala deja 0 filas de esa sala en cada tabla, copias incluidas; la respuesta lo confirma con un conteo | NFR10.1 |
| U14-S7 | El diccionario de datos no contiene datos de participantes ni respuestas del banco | FR9.3, `.claude/rules/markdown-docs.md` («Confidencialidad») |
