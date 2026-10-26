# Escala — diseño U2

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

- **Plan de salas** (U2-E1, U2-E3). `guion.plan_de_salas(participantes, salas, modo)` devuelve la lista de
  tamaños: en nube `[10, 7, 6, 5, 4, 3, 2, 1, 1, 1]` para 40 y 10; con otros valores reparte
  proporcionalmente y conserva al menos una sala de 1; en local devuelve `[participantes]`. Los papeles 0 a
  6 van a la primera sala (la más grande), así los casos especiales de `simulacro.py` conviven en una
  sala con al menos 7 participantes.
- **Peticiones contadas** (U2-E2). Cada `Cliente` lleva su propio contador y al final se suman; el número
  va al JSON como `peticiones`. U17 lo divide por la cuota de cada opción con su URL oficial.
- **Recursos de la computadora** (U2-E4). Un pool de 50 hilos como máximo; cada `Cliente` abre una
  conexión por petición y la cierra (`urllib` no mantiene conexiones vivas), así nunca hay más de 50
  abiertas; las misiones se guardan una vez por participante y se descartan al terminar la fase de carga.
- **Sondeos en la espera**. Durante los 10 minutos de vencimiento, los tableros bajan a un sondeo cada
  10 s: 600 peticiones en vez de 3.000, sin perder la medición de que el servicio sigue respondiendo.
