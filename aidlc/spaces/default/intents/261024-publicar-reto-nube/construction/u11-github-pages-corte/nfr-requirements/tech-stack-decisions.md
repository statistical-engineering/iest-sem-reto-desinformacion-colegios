# Tecnología — U11

Requisitos no funcionales de U11, el corte delgado de GitHub Pages con la API en PythonAnywhere. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial consultada el 2026-10-25 (URL en `../decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Pantallas | GitHub Pages, sitio de proyecto en `https://<cuenta>.github.io/<repositorio>/`, publicado por un flujo de Actions solo manual (`workflow_dispatch`) | ADR-G2; Pages en GitHub Free «in public repositories» (https://docs.github.com/en/get-started/learning-about-github/githubs-plans) |
| API | PythonAnywhere, plan gratuito, app WSGI en `https://<usuario>.pythonanywhere.com` | ADR-G1 |
| Lenguaje | Python 3.10 o más reciente, solo biblioteca estándar (`sqlite3`, `hmac`, `hashlib`, `json`, `wsgiref`, `logging`); sin paquetes | ADR-G3; FR7.6 (nada que aprobar) |
| Dependencias | Ninguna; el `pyproject.toml` y el `uv.lock` de la raíz no cambian | FR7.6, `project.md` («Corrections», uv) |
| Almacén | Un archivo SQLite (`RETO_DATOS/reto.db`), WAL, `busy_timeout` 5 s | ADR-G5 |
| Despacho de rutas | Tabla `"MÉTODO /ruta" → (nivel, función)` en `src/wsgi.py` | FR7.2, ADR-G3 |
| Capa de base | No hay: una sola implementación | FR7.3, ADR-G3 |
| Pruebas | `unittest`; la API se prueba llamando a `application(environ, start_response)` sin red | `team.md` («Testing Posture»), ADR-G3 |
| Cobertura | `python3 -m trace --count --missing --coverdir=<carpeta ignorada> pruebas/…` sobre `src/`; piso 80 % de líneas | NFR12, `team.md` |
| Estilo | `uv run ruff format` y `uv run ruff check` con el `[tool.ruff]` del repositorio; complejidad ≤ 10 | ADR-008 |
| Prueba en local | `python3 despliegues/github-pages/src/servidor_local.py` (API en 8791 con `wsgiref`, pantallas en 8792 con `http.server`) | ADR-G3, ADR-G4 |
| Despliegue de la API | `git clone`/`git pull` en una consola Bash de PythonAnywhere (`.github.com` está en su lista permitida) y «Reload» en la pestaña Web | ADR-G1, ADR-G6 |
| Prueba común | Python 3 con la biblioteca estándar, con `--url` (API) y `--url-web` (Pages) | Delivery Planning Q6-A, ADR-G4 |
