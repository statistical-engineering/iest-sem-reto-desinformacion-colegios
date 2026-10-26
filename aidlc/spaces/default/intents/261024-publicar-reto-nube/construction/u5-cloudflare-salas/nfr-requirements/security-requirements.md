# Seguridad — U5

Requisitos no funcionales de U5, salas y examen completos en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C1. Decisiones tomadas por el asistente con la potestad que dio el humano. Los de U1 (U1-S1 a U1-S9) siguen vigentes.

| Id | Requisito | Origen |
|---|---|---|
| U5-S1 | Toda ruta `/api/admin/*` de una sala actúa solo sobre la sala de la clave: una clave de sala con `?sala=` de otra da 403 sin datos; un `id` de participante de otra sala da 404; la prueba común lo revisa en cada ruta de sala | FR11.5, NFR9, FR12.5 (fila NFR9) |
| U5-S2 | Las rutas del semillero (`salas`, `salas/clave`, `salas/borrar`, `catalogo` POST) responden 403 con clave de sala | FR11.5, NFR9 |
| U5-S3 | Una clave regenerada deja de servir en la misma petición que la reemplaza; la clave nueva se devuelve una sola vez y nunca se registra ni se guarda | ADR-003, NFR9 |
| U5-S4 | No hay bloqueo por intentos fallidos; la espera de 600 ms ante clave incorrecta corre fuera del bloqueo del objeto para que no frene a las demás salas | OQ6, ADR-W12 |
| U5-S5 | `GET /api/admin/salas` y `GET /api/admin/catalogo` nunca traen `clave_huella`, tokens, semillas ni nombres de participantes | NFR9, NFR10 |
| U5-S6 | Las respuestas de los 10 tipos se validan en el servidor antes de guardarse (tipo, tamaño, ids), aunque la petición no venga de `web/js/`; las guardadas salen al navegador solo con ids opacos | FR10.1, FR6.2, `phases/construction.md` («Security») |
| U5-S7 | Borrar la sala no deja filas de esa sala en ninguna tabla; una prueba cuenta filas por `id_sala` después de borrar | NFR10.1, FR11.6 |
| U5-S8 | El resumen del panel trae el experimento completo solo porque va con clave; nada del experimento sale sin clave antes de resultados | FR6.1, NFR8 |
