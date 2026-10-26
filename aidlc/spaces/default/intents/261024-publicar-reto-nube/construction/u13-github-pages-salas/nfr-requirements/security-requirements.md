# Seguridad — U13

Requisitos no funcionales de U13, salas y catálogo de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U13 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U13-S1 | Una clave de sala no lee ni cambia otra sala: toda consulta de `/api/admin/*` lleva `WHERE sala = ?` con la sala que resolvió Acceso, y `?sala=` distinto da 403 | FR11.5, NFR9, BR1.3 de U11 |
| U13-S2 | Al regenerar la clave, la huella anterior se reemplaza en la misma transacción y la clave nueva se devuelve una sola vez; nunca se registra | ADR-003, NFR9 |
| U13-S3 | `GET /api/admin/salas` y `GET /api/admin/catalogo` nunca traen `clave_huella`, `token` ni `semilla` | NFR9, contrato C1 |
| U13-S4 | Borrar una sala exige la clave del semillero, estado cerrado o resultados y la palabra BORRAR; borra solo filas con esa sala | NFR10.1, revisión 05 de Domain Design |
| U13-S5 | Todo texto que llega del panel o del formulario pasa por `normalizar_texto` antes de SQLite; el SQL usa siempre parámetros `?` | FR10.2, `phases/construction.md` («Security») |
| U13-S6 | Las rutas nuevas del panel llevan las mismas cabeceras CORS de U11 (origen exacto, nunca `*`) | BR8.1 de U11 |
| U13-S7 | Una clave de sala con minúsculas o espacios se acepta igual que en mayúsculas; una clave con la forma `<código>-…` de una sala que no existe da 403 sin probar después la del semillero | hallazgos C-03 y C-10 |
