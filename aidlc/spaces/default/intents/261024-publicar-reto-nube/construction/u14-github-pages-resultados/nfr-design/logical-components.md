# Componentes lógicos — U14

Diseño no funcional de U14. Las decisiones son las del ADR de U11 (`../../u11-github-pages-corte/decisions.md`); los requisitos en `../nfr-requirements/`.

```mermaid
graph LR
  W[wsgi.py] --> R[Resultados]
  W --> X[Exportacion]
  R --> E[Examen: hora de entrega]
  X --> E
  R --> G[reglas.py: ordenar, calcular, examen_publico]
  X --> S[Salas: reiniciar]
  X --> Q[(reto.db + tabla copias)]
  X --> T[sqlite3 temporal: copia de la sala]
  R --> Q
```

Texto alternativo: Resultados y Exportacion piden a Examen aplicar la entrega antes de leer; Resultados
usa las reglas de clasificación y experimento; Exportacion arma la copia en un SQLite temporal, la guarda
en `copias` y, al reiniciar, pide a Salas vaciar la sala en la misma transacción.

| Sección de `servicio.py` | Componente | Qué agrega U14 |
|---|---|---|
| `Resultados` | Resultados | tablero por sala, revisión en resultados, resumen con ranking y experimento |
| `Exportacion` | Exportacion | CSV de hoy, paquete, copia de sala, reiniciar, copias, borrado con copias |
| `web/` | PanelDocente, Tablero | lista de copias, paquete, mensajes del tablero |
| `4_Codigo_y_datos/DICCIONARIO_DATOS_RETO.md` | — | diccionario de datos (FR9.3) |
