# Tecnología — U12

Requisitos no funcionales de U12, las reglas de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U12 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Python 3.10 o más reciente, biblioteca estándar (`hmac`, `hashlib`, `base64`, `unicodedata`, `random`, `math`, `json`) | ADR-G3 de U11; sin paquetes (FR7.6) |
| Archivo | `despliegues/github-pages/src/reglas.py`, un solo módulo con seis secciones (una por regla de C4) | ADR-001; igual que `reglas.js` de Cloudflare, sin compartir código (FR12.2) |
| Origen del código | Las nueve funciones puras de `servidor.py` se copian tal cual (la versión local no cambia, FR12.1); las seis mezcladas se reescriben sin SQL ni reloj | NFR11: mismos puntos que hoy |
| Pruebas | `unittest`, `pruebas/test_reglas.py`, casos de `pruebas/casos_reglas.json` con `subTest` | `team.md` («Testing Posture»), contrato C4 |
| Cobertura | `python3 -m trace --count --missing` sobre `src/reglas.py`; piso 80 % | NFR12 |
| Estilo | ruff con el `[tool.ruff]` del repositorio, complejidad ≤ 10 (las funciones copiadas que ya traen `# noqa: C901` lo conservan, ADR-008) | ADR-008 |
| Datos compartidos | `casos_reglas.json` se copia desde `despliegues/prueba_comun/`; nunca se importa código de otra opción | `project.md` («Corrections», solo datos) |
