# Confiabilidad — U2

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba mide de cada opción. Salen de `requirements.md` (NFR4, NFR5, NFR11) y del diseño funcional
(`rules.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-R1 | La prueba es determinista en lo que decide: con la misma semilla (7 por defecto) y los mismos participantes, cada participante tiene el mismo papel, grado y decisiones de acierto; solo cambian los sufijos de nombres y las mediciones de tiempo | BR3.1, NFR11 |
| U2-R2 | Se puede repetir contra la misma URL sin borrar nada: nombres de salas, colegios y participantes únicos por corrida; en la nube la sala de calibración y las salas del reto quedan en resultados o reiniciadas | BR2.1, BR6.1 |
| U2-R3 | Una respuesta 5xx sin JSON, un 503 de la plataforma o un tope de tiempo de 20 s cuentan como falla de la comprobación y la corrida sigue; solo la falta total de conexión al arrancar termina con código 2 | BR1.4, C-15 |
| U2-R4 | Una comprobación esencial que falla detiene la corrida con un mensaje que dice en qué paso, y el JSON se escribe igual con `todo_bien: false` | BR1.3, BR8.1 |
| U2-R5 | Mide NFR4: con `--reinicio manual` o `comando`, compara el resumen de cada sala antes y después del reinicio; sin esa opción deja `sobrevive_reinicio` en `null` | NFR4, BR7.2 |
| U2-R6 | Mide NFR5: con `--frio`, la primera petición es el arranque en frío con umbral de 30.000 ms; sin la opción deja `arranque_frio_ms` en `null` | NFR5, BR7.3 |
| U2-R7 | El vencimiento se espera en tiempo real calculado con `abierto_en` del servidor, no con el reloj local, así un reinicio o un reloj local distinto no cambian el resultado | BR4.2, FR3.3 |
