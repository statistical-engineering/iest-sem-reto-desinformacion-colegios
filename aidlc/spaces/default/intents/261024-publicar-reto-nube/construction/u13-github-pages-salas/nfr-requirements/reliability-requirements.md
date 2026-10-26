# Confiabilidad — U13

Requisitos no funcionales de U13, salas y catálogo de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U13 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U13-R1 | Cerrar una sala es una sola transacción: o se entregan todos los intentos en curso y se guarda `cerrada`, o nada; repetir el cierre no entrega dos veces (idempotente) | ADR-004, R-09 |
| U13-R2 | Dos salas no se cruzan: con dos salas abiertas, cerrar una no cambia relojes, puntajes ni estados de la otra | FR11.2, FR11.7 |
| U13-R3 | Las acciones del docente son idempotentes frente a un doble clic: repetir `finalizar` sobre un finalizado responde 400 y no cambia nada | ADR-007 |
| U13-R4 | Si un colegio provisional repite un nombre, el servidor no lo crea y devuelve el existente para que el docente lo elija | ADR-002 |
| U13-R5 | Un reinicio de la plataforma a mitad del reto no pierde ninguna sala, colegio ni acción que respondió 200 (todo en `reto.db`) | NFR4 |
