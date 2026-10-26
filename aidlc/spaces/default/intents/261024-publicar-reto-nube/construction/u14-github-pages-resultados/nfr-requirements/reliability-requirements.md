# Confiabilidad — U14

Requisitos no funcionales de U14, resultados y exportación de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U14 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U14-R1 | «Reiniciar» es atómico: o queda la copia guardada y la sala vacía, o nada; una caída a mitad no deja la sala a medias | R-17, ADR-G5 |
| U14-R2 | La copia se vuelve a abrir con `sqlite3` y contiene todas las filas de la sala (una prueba cuenta participantes, respuestas y eventos en la copia y en la base) | FR4.3, FR9.1 |
| U14-R3 | Un reinicio de la plataforma a mitad de la prueba común no pierde puntajes, respuestas ni clasificación (NFR4 medido por U2 contra esta opción) | NFR4 |
| U14-R4 | Las fechas del paquete llevan zona horaria fija `-05:00` (Colombia no tiene horario de verano), calculadas con `datetime.timezone(timedelta(hours=-5))`, sin depender de la zona del servidor de PythonAnywhere | FR9.2 |
| U14-R5 | Si falla armar el paquete (por ejemplo disco lleno al crear la copia temporal), se responde 503 y no queda ningún archivo temporal | contrato C1, `phases/construction.md` («Error Handling») |
