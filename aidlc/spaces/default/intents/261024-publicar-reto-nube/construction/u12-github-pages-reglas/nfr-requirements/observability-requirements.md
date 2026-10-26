# Observación — U12

Requisitos no funcionales de U12, las reglas de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U12 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U12-O1 | Las reglas no registran nada; lo que falla se ve en las pruebas (`unittest` imprime la fila de `casos_reglas.json` que no pasó, con `regla` y `funcion`, nunca la `salida_esperada` de Calificacion) | NFR8, NFR12 |
| U12-O2 | La cobertura de `reglas.py` se imprime al final de `herramientas/verificar.sh` como «reglas.py: <n> % de líneas» | NFR12 |
