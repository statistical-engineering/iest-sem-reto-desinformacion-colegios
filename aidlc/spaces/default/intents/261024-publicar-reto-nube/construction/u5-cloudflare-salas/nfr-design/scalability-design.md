# Escala — diseño U5

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W13); los requisitos en `../nfr-requirements/`.

- Un solo objeto para todas las salas (ADR-W1) sigue siendo suficiente: 40 personas generan como
  máximo unas 12 peticiones por segundo en los picos (todas responden a la vez), y cada petición tarda
  menos de 5 ms dentro del objeto; la cola no se acumula (U5-E1). U2 mide el p95 con 10 salas; si se
  acercara a 1 s, el camino es partir por sala (un objeto por sala) sin cambiar la API, como prevé
  ADR-W1.
- Consumo (U5-E2, U5-E3): U5 no agrega sondeos. Las rutas nuevas del panel se usan a mano (crear,
  regenerar, catálogo, colegios, acciones), decenas de veces por sesión, no miles.
- Catálogo (U5-E4): índice `UNIQUE` en `nombre_normalizado`; `GET /api/colegios?sala=` lee solo
  `sala_colegios` de esa sala.
- Salas (U5-E5): sin tope; `GET /api/admin/salas` muestra cuántas hay.
