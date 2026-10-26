# Escala — diseño U13

Diseño no funcional de U13. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- Todas las salas comparten el candado del proceso (ADR-G5): con 10 salas y 40 personas la cola es de
  milisegundos, como en U1. Si U2 mide un p95 alto, la salida es la de U11 (menos sondeo del panel), no
  partir la base (U13-E1).
- Catálogo pequeño, consultas con índice (U13-E2).
- Las rutas del semillero no cambian la estimación de peticiones (U13-E3).
