# Tecnología — U14

Requisitos no funcionales de U14, resultados y exportación de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U14 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Dónde vive | `src/servicio.py` gana las secciones Resultados y Exportacion; rutas nuevas en la tabla de `src/wsgi.py` | ADR-G3 de U11 |
| Copia | `sqlite3` con `ATTACH` a un archivo temporal (`tempfile.NamedTemporaryFile`) y `INSERT … SELECT … WHERE sala = ?`; se guarda como blob en la tabla `copias` (migración `user_version = 3`) | ADR-G5, FR4.3 (SQLite → `reto.db`), R-05 |
| Paquete | `zipfile.ZipFile` sobre `io.BytesIO`, `csv.writer`, `json.dumps`; sin paquetes | FR7.6 |
| Fechas | `datetime` con `timezone(timedelta(hours=-5))` | FR9.2 |
| Versión de la app | `src/version.txt` escrito por `herramientas/copiar.sh` con `git rev-parse --short HEAD` | FR9.1 (version_app) |
| Diccionario | `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md`, un `.md` en español (nombre por confirmar en FR9.3; se mantiene) | FR9.3 |
| Pruebas | `unittest` en `pruebas/test_exportacion.py` y `pruebas/test_resultados.py`, con base en `tempfile` y la copia abierta con `sqlite3` | `team.md` |
| Pantallas | `cambios_web.patch` crece con la lista de copias, el paquete y los mensajes del tablero | Delivery Planning Q7-A |
