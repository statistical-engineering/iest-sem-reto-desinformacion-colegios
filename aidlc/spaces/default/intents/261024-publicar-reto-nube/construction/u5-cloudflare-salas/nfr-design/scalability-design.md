# Escala — diseño U5

> **Revisión 2026-10-27 (una sola sala).** Un solo reto por objeto: se quitan las 10 salas y el
> catálogo; la lista de colegios es la del docente.

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W12, ADR-W19 y ADR-W20); los requisitos en `../nfr-requirements/`.

- Un solo objeto para el reto (ADR-W1) es suficiente: 40 equipos generan como máximo unas 12 peticiones
  por segundo en los picos, y cada petición tarda menos de 5 ms dentro del objeto; la cola no se acumula
  (U5-E1). U2 mide el p95 con la carga de NFR1.
- Consumo (U5-E2, U5-E3): U5 no agrega sondeos. Las rutas nuevas del panel (`config`, `colegios`,
  `participante`) se usan a mano, decenas de veces por sesión, no miles.
- Lista de colegios (U5-E4): índice `UNIQUE` en `nombre_normalizado`; `agregar` inserta con una sentencia
  por nombre dentro de la transacción; `GET /api/colegios` lee toda la lista (decenas de filas).
- Colegios (U5-E5): sin tope; la tarjeta del panel muestra cuántos hay.
