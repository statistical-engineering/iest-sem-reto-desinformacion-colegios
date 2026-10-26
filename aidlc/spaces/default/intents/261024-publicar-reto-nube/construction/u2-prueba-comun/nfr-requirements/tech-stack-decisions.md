# Tecnología — U2

Requisitos no funcionales de U2, la prueba común completa. Salen de `requirements.md` (NFR12, FR7.6),
`team.md` («Testing Posture»), `.claude/rules/python-code.md` y Delivery Planning (Q6-A). Decisiones
tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Python 3.12, solo biblioteca estándar (`urllib.request`, `json`, `hashlib`, `threading`, `concurrent.futures`, `statistics`, `argparse`, `http.server` en las pruebas) | Delivery Planning Q6-A; «sin paquetes nuevos»; corre con el `.python-version` del repo |
| Sintaxis | `match`/`case` permitido (3.12), anotaciones completas, docstrings Google | `.claude/rules/python-code.md` («Versión de Python»: `match` en scripts 3.12) |
| Pruebas | `unittest`, archivos `test_<modulo>.py` en `despliegues/prueba_comun/pruebas/`; se corren con `python3 -m unittest discover -s despliegues/prueba_comun/pruebas -t despliegues/prueba_comun` | `project.md` («Testing Posture»: `unittest` sí, `pytest` no) |
| Cobertura (U2-M1) | 80 % de líneas del código nuevo, medido con `python3 -m trace --count --coverdir=<carpeta> --missing`: la suite `unittest` cubre `guion.py`, `mediciones.py`, `cliente.py` y `carga.py`; `prueba.py` se cubre corriendo la prueba bajo `trace` contra la versión local con `--db` aparte | NFR12, `team.md` («Testing Posture»: `trace`, sin paquetes nuevos) |
| Estilo | ruff (`[tool.ruff]` de `pyproject.toml`): formato, `D`, `ANN`, `N`, complejidad ≤ 10, ≤ 6 parámetros | ADR-008; `despliegues/prueba_comun/` no está en `per-file-ignores`, así que entra completo |
| Servidor de prueba | Un `http.server` mínimo en `pruebas/servidor_falso.py` que responde JSON fijo y cuenta peticiones, para probar `cliente.py` y `carga.py` sin el reto | `python-code.md` («Pruebas»: sin mocks en lógica pura; la red se prueba con un servidor real de la biblioteca estándar) |
| Salida | JSON del contrato C3 en `mediciones/`, versionado (no lleva secretos) | FR12.4, C3 |
| Dependencias | Ninguna; `pyproject.toml` no cambia | FR7.6 |
