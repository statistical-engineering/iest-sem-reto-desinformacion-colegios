# Confiabilidad — U3

Requisitos no funcionales de U3. Salen de `requirements.md` (FR3.3, FR4.3, FR6.3), de `project.md`
(«Forbidden», «Mandated») y de `../decisions.md`. Decisiones tomadas por el asistente con la potestad que
dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U3-R1 | La función opaca es determinista y no depende del reloj ni de la base: un reinicio del servidor da los mismos ids a cada participante, así una pantalla abierta sigue funcionando después de reiniciar | ADR-006 («la función tiene que ser la misma mientras haya un reto en curso»), BR1.1 |
| U3-R2 | Las bases creadas antes de U3 se abren sin migración: el esquema no cambia y una respuesta guardada antes se muestra opaca igual que una guardada después | FR4.3, BR3.2 |
| U3-R3 | `python3 pruebas/simulacro.py 40` termina en «TODO BIEN» sin cambiar `simulacro.py`, y la parte de fugas de la prueba común (U2) pasa en modo local | FR6.3, B7 de `bolt-plan.md` |
| U3-R4 | Un valor de respuesta con forma inesperada (ni texto, ni lista, ni mapa) pasa por `traducir_entrada` sin excepción y lo rechaza `validar_respuesta` como hoy; ningún `except` nuevo traga errores | `phases/construction.md` («Error Handling»), BR3.1 |
| U3-R5 | La actualización se aplica solo sin reto en curso y con reinicio del servidor; volver atrás es volver al commit anterior de `2_Aplicacion_Reto/` | `project.md` («Forbidden», «Mandated»), BR5.2 |
