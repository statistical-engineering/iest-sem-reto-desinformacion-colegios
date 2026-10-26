# Rapidez — U3

Requisitos no funcionales de U3, la corrección de fugas en `2_Aplicacion_Reto/servidor.py`. La versión
local no se vuelve a medir con la prueba común (`requirements.md`, «Non-functional requirements»: «queda
como línea base»), así que estos requisitos solo piden que la corrección no la haga más lenta de forma
notable. Salen del diseño funcional (`rules.md`) y de `../decisions.md`. Decisiones tomadas por el
asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Cómo se mide | Origen |
|---|---|---|---|
| U3-P1 | Un `GET /api/estado` con misiones calcula a lo sumo unos 250 HMAC-SHA256 (42 preguntas, unas 5 ids cada una) y eso agrega menos de 5 ms por petición en una computadora común | `python3 -m timeit` sobre `opacar_salida` con una pregunta inventada de 5 opciones, multiplicado por 42; se anota en el PR | BR2.1, ADR-L1 |
| U3-P2 | `POST /api/responder` agrega como máximo un grupo de HMAC (la pregunta respondida) | Revisión del código: `traducir_entrada` solo toca la pregunta recibida | BR3.1 |
| U3-P3 | No se agrega caché del examen por semilla: con 40 participantes que sondean cada 20 s el costo total es menor a 1 % de CPU y una caché sería abstracción prematura en una versión congelada | Decisión registrada; si `timeit` da más de 5 ms por estado, se revisa | ADR-L1 (consecuencias) |
