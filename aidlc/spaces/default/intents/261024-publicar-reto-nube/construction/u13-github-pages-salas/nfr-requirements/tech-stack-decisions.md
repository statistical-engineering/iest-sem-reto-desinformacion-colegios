# Tecnología — U13

Requisitos no funcionales de U13, salas y catálogo de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U13 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Dónde vive | `src/servicio.py` (Salas, Acceso, CatalogoColegios, Inscripcion, Examen con su SQL) y la tabla de rutas de `src/wsgi.py`; sin archivos nuevos de código | ADR-G3 de U11 (sin capa aparte de base) |
| Esquema | Migración por versión en `PRAGMA user_version`: U13 agrega `unido_a` y `n_integrantes` con `ALTER TABLE` al arrancar si `user_version < 2` | NFR4: no se pierde la base del corte |
| Transacciones | `BEGIN IMMEDIATE` por operación de escritura; cierre de sala en una sola | ADR-G5, ADR-004 |
| Pruebas | `unittest` en `pruebas/test_servicio.py`, llamando a `application` con una base en `tempfile`; una prueba por regla con un caso válido y dos inválidos | `team.md`, FR10.5 |
| Pantallas | `herramientas/cambios_web.patch` crece con los cambios del panel; `copiar.sh` lo reaplica | Delivery Planning Q7-A |
| Sin paquetes | Igual que U11 | FR7.6 |
