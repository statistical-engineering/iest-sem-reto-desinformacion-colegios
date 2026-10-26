# Seguridad — U3

Requisitos no funcionales de U3. Salen de `requirements.md` (FR6, NFR8, NFR9), de ADR-006 y de
`../decisions.md`. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U3-S1 | Ningún id que llega al navegador por `/api/estado` (opciones, ítems, publicaciones, partes) contiene el texto, la posición en el banco ni un dato derivado de la clave: todos salen de HMAC-SHA256 con la semilla secreta del participante | FR6.2, ADR-006, BR1.1 |
| U3-S2 | La semilla sigue sin salir del servidor: no va en `/api/estado`, `/api/publico`, el resumen ni los CSV; el único cambio es que ahora además es la clave del HMAC | ADR-006 (consecuencias: «la semilla tiene que seguir siendo secreta») |
| U3-S3 | Antes de «resultados», `/api/publico` no entrega `verdad`, `multitud_acierta` ni ningún agregado del experimento del que se pueda deducir el veredicto: en «cerrado» solo `n` y `listo` | FR6.1, NFR8, ADR-L2, BR4.1 |
| U3-S4 | `respuestas`, `revision` y el examen salen opacos con la misma función, así `estudiante.js` no recibe dos alfabetos de ids | C-02 del contrato, BR2.2 |
| U3-S5 | Aceptar un id del banco a la entrada no revela nada: la respuesta de `/api/responder` es la de hoy (`ok`, y con `retro` la fracción de la propia respuesta); un id opaco inventado da 400 sin detalle | ADR-L1, BR3.1 |
| U3-S6 | Nada nuevo se registra: ni semillas, ni ids opacos, ni respuestas; los `print` de error siguen siendo los de hoy | `.claude/rules/python-code.md` («Logs») |
| U3-S7 | Las pruebas nuevas usan preguntas inventadas; ningún archivo de la unidad lleva una respuesta del banco ni una clave docente | `python-code.md` («Pruebas»), `project.md` («Forbidden») |
