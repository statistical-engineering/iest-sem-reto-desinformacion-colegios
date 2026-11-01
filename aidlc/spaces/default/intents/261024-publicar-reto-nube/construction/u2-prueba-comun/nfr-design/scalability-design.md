# Escala — diseño U2

> **Revisión 2026-10-27 (una sola sala).** El plan de salas pasa a ser el reparto en 3 colegios (BR6.1);
> hay un solo tablero y un panel.

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

- **Reparto en colegios** (U2-E1, U2-E3). `guion.reparto_colegios(participantes)` devuelve los tamaños
  `(A, B, C)`: `(20, 12, 8)` para 40; con otros valores, A la mitad hacia arriba, C la quinta parte hacia
  arriba con mínimo 2 y B el resto. Los papeles especiales de `simulacro.py` (0 a 6 y el
  entregado_docente) van al colegio A; el primero de B es el no_inicia y el primero de C el
  vencido_colegio (BR3.1). En local se usan los mismos tres nombres como texto y un solo reloj.
- **Peticiones contadas** (U2-E2). Cada `Cliente` lleva su propio contador y al final se suman; el número
  va al JSON como `peticiones`. U17 lo compara con la cuota de Workers con su URL oficial.
- **Recursos de la computadora** (U2-E4). Un pool de 42 hilos como máximo; cada `Cliente` abre una
  conexión por petición y la cierra (`urllib` no mantiene conexiones vivas), así nunca hay más de 42
  abiertas; las misiones se guardan una vez por participante y se descartan al terminar la fase de carga.
- **Sondeos en la espera**. Durante las esperas del vencimiento, el tablero baja a un sondeo cada 10 s
  y el panel se detiene, sin perder la medición de que el servicio sigue respondiendo.
