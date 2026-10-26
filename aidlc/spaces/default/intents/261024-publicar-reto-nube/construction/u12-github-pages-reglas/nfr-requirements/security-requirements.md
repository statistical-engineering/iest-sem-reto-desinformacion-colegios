# Seguridad — U12

Requisitos no funcionales de U12, las reglas de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U12 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U12-S1 | `examen_publico` y `calcular` nunca devuelven `respuesta`, `explicacion`, `tolerancia`, `verdad` ni `multitud_acierta` antes de «resultados»; una prueba recorre todo el JSON devuelto y falla si aparece alguna de esas claves | NFR8, FR6.1, FR6.2 |
| U12-S2 | Los ids opacos salen de HMAC-SHA256 con la semilla (`hmac`); la semilla nunca es parte de una salida | FR6.2, ADR-006, ADR-G6 |
| U12-S3 | `pruebas/casos_reglas.json` no contiene respuestas del banco real: los casos de Calificacion usan un banco de prueba propio (contrato C4, «no_lleva») | NFR8, `project.md` («Forbidden») |
| U12-S4 | `normalizar_texto` quita caracteres de control y formato antes de que un texto llegue a SQLite o al tablero | FR10.2 |
| U12-S5 | Ninguna regla registra nada (`logging` no se importa en `reglas.py`) | NFR10 |
