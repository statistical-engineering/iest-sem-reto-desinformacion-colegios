# Seguridad — U2

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba mide de cada opción. Salen de `requirements.md` (NFR8, NFR9, NFR10), del diseño funcional
(`rules.md`) y del contrato (C3). Decisiones tomadas por el asistente con la potestad que dio el humano
(2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-S1 | La clave llega por `--clave` o `PRUEBA_CLAVE` y viaja solo en `X-Clave-Admin`; nunca se imprime, nunca va en la URL (salvo la petición que comprueba que `?clave=` da 403) y nunca va al JSON | NFR9, BR1.1 |
| U2-S2 | Las claves de sala que devuelve `/api/admin/salas/crear` y los tokens de los participantes viven solo en memoria durante la corrida | NFR9, entities.md (SalaDePrueba, ParticipanteFicticio) |
| U2-S3 | La clave por texto (respuestas correctas) se obtiene solo de `revision` con la sala en resultados, vive en memoria y nunca se escribe en disco, en la salida ni en el JSON; la prueba no lee `banco_preguntas.json` ni ningún archivo del repositorio | NFR8, BR2.1, project.md («Forbidden») |
| U2-S4 | El JSON de mediciones y la salida impresa no llevan claves, tokens, nombres de participantes reales ni respuestas correctas; `detalle` solo lleva ids de pregunta, conteos y cifras | C3, BR8.1 |
| U2-S5 | Los datos de los participantes ficticios son inventados («Detective <k> <sufijo>», «Colegio de prueba <sufijo>») y nunca se corre la prueba contra la base de un reto real: el LEEME lo dice y en modo local se exige `--db` aparte | NFR10, `.claude/rules/python-code.md` («Pruebas») |
| U2-S6 | Las comprobaciones de NFR9 se hacen desde la prueba: clave ausente, incorrecta, de otra sala y en la URL dan 403 sin datos | NFR9, BR6.3 |
| U2-S7 | Las comprobaciones de NFR8 se hacen desde la prueba: lista de claves secretas en toda respuesta sin clave docente, ids opacos, veredicto solo en resultados y CSV con ids del banco | NFR8, BR5.1 a BR5.4 |
