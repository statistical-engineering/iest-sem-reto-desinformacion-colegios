# Confiabilidad — U4

Requisitos no funcionales de U4, las reglas puras de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C4. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U4-R1 | Determinismo: la misma entrada y la misma hora dan la misma salida, en Workers y en Node 24; las pruebas con la tabla lo comprueban en Node y la prueba común (U2) lo comprueba contra Workers con los mismos puntos y orden que la versión local | NFR11, FR5.5 |
| U4-R2 | Los números coinciden con `servidor.py` bit a bit salvo en los casos marcados con `tolerancia` (divisiones del experimento), donde la diferencia es ≤ 1e-9 | NFR11, ADR-W8 |
| U4-R3 | Una entrada mal formada nunca lanza una excepción no controlada: `validar_respuesta` devuelve `{error}`, `traducir_respuesta` devuelve `null`, `validar_inscripcion` devuelve una lista; solo un tipo de pregunta desconocido lanza `RangeError`, y eso lo impide `validar_banco` al arrancar | `phases/construction.md` («Error Handling»), BR2.3 |
| U4-R4 | Las 23 pruebas de U1 siguen pasando sin cambios después de partir `reglas.js` (ADR-W6): la fachada conserva cada nombre exportado | FR12.3 (nada se debilita), ADR-W6 |
| U4-R5 | La copia de la tabla de casos no puede quedar vieja sin que se note: `verificar.sh` compara huellas SHA-256 y se detiene | ADR-W7, `project.md` («Corrections», huella del banco) |
