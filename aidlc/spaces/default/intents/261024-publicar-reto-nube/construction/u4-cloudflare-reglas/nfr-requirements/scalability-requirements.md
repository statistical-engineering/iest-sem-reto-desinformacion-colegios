# Escala — U4

Requisitos no funcionales de U4, las reglas puras de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C4. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U4-E1 | Las reglas reciben los datos de **una sala**: `ordenar` y `calcular` nunca reciben más de 40 participantes (NFR1) y su costo crece con el tamaño de la sala, no con el número de salas | NFR1, FR11.2 |
| U4-E2 | Ninguna regla guarda estado entre llamadas (sin caché interna, sin variables de módulo mutables); la única caché (examen por semilla) vive en `reto.js`, como en U1, y se vacía al reiniciar el objeto | ADR-001, NFR4 |
| U4-E3 | El tamaño de `casos_reglas.json` se mantiene por debajo de 500 KB para que la suite siga cargándolo en memoria en menos de 1 s | NFR12 |
