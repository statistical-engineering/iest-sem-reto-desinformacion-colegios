# Tecnología — U3

Requisitos no funcionales de U3. Salen de `requirements.md` (NFR12, FR7.6), `team.md` («Testing
Posture»), `.claude/rules/python-code.md` y `../decisions.md`. Decisiones tomadas por el asistente con la
potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Python 3.9 o más nuevo, solo biblioteca estándar: `hmac`, `hashlib`, `base64` | El docente arranca `servidor.py` con su propio Python (`python-code.md`, «Versión de Python»; ruff `per-file-target-version = py39`) |
| Sintaxis | Sin `match`/`case`; `from __future__ import annotations` si se anotan tipos; anotaciones y docstrings Google en las funciones nuevas | `python-code.md` («Tipado», «Nombres»); `servidor.py` sigue en `per-file-ignores` para `D`, `ANN` y `N` del código viejo, pero el código nuevo las cumple |
| HMAC | `hmac.new(semilla.encode("utf-8"), mensaje.encode("utf-8"), hashlib.sha256).digest()` y `base64.b32encode(...).decode("ascii").lower()` | ADR-006 («`hmac` en Python 3.9+»), ADR-L1 |
| Pruebas (U3-M1) | `unittest` en `2_Aplicacion_Reto/pruebas/test_servidor.py`; se corre con `python3 -m unittest discover -s 2_Aplicacion_Reto/pruebas -t 2_Aplicacion_Reto`; cobertura del código nuevo con `python3 -m trace --count --missing` ≥ 80 % de las líneas de las seis funciones nuevas | NFR12, `project.md` («Testing Posture»), `team.md` |
| Aceptación | `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` en «TODO BIEN»; prueba común en modo local | FR6.3 |
| Estilo | ruff: formato, complejidad ≤ 10, `# noqa` solo con código; las 10 líneas con `noqa` que `servidor.py` ya tiene no se tocan salvo las que caigan en la línea editada | ADR-008 |
| Dependencias | Ninguna; `pyproject.toml` no cambia | FR7.6 |
