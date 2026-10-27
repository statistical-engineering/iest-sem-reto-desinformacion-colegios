# Seguridad — U2

> **Revisión 2026-10-27 (una sola sala).** Hay una sola clave, la docente (`CLAVE_DOCENTE` en el servicio,
> ADR-010): desaparecen las claves de sala y la «clave de otra sala» de U2-S6, que pasa a mayúsculas
> cambiadas y espacios (D6, BR6.3). U2-S1 prefiere la variable de entorno para que la clave no quede en
> la lista de procesos. U2-S5 exige el reto vacío (BR1.5). Entra U2-S8.

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba mide de cada opción. Salen de `requirements.md` (NFR8, NFR9, NFR10), del diseño funcional
(`rules.md`) y del contrato (C3). Decisiones tomadas por el asistente con la potestad que dio el humano
(2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-S1 | La clave docente llega por la variable de entorno `PRUEBA_CLAVE` (forma recomendada: no queda en el historial ni en la lista de procesos) o por `--clave`, y viaja solo en `X-Clave-Admin`, tal cual (sin recortar ni cambiar mayúsculas); nunca se imprime, nunca va en la URL (salvo la petición que comprueba que `?clave=` da 403) y nunca va al JSON | NFR9, D6, BR1.1 |
| U2-S2 | Los tokens de los participantes ficticios viven solo en memoria durante la corrida | NFR9, entities.md (ParticipanteFicticio) |
| U2-S3 | La clave por texto (respuestas correctas) se obtiene solo de `revision` con el reto de calibración en resultados, vive en memoria y nunca se escribe en disco, en la salida ni en el JSON; la prueba no lee `banco_preguntas.json` ni ningún archivo del repositorio salvo `--referencia` | NFR8, BR2.1, project.md («Forbidden») |
| U2-S4 | El JSON de mediciones y la salida impresa no llevan claves, tokens, nombres de la corrida ni de colegios, ni respuestas correctas; `detalle` solo lleva ids de pregunta, conteos y cifras | C3, BR8.1 |
| U2-S5 | Los datos de los participantes y colegios ficticios son inventados («Detective <k> <sufijo>», «Calibrador <n> <sufijo>», «Colegio Prueba <letra> <sufijo>») y la prueba nunca escribe en un reto con datos: si el reto no está en inscripción y vacío, termina con código 2 sin tocarlo; en local el LEEME exige `--db` y `RETO_DATOS` aparte | NFR10, BR1.5, `.claude/rules/python-code.md` («Pruebas») |
| U2-S6 | Las comprobaciones de NFR9 se hacen desde la prueba: sin cabecera, clave incorrecta, clave con las mayúsculas cambiadas y clave en la URL dan 403 sin datos; con espacios en los extremos da 200; `POST /api/admin/login` responde solo `ok`; la ruta quitada de crear salas da 404 | NFR9, D6, ADR-010, BR6.3 |
| U2-S7 | Las comprobaciones de NFR8 se hacen desde la prueba: lista de claves secretas en toda respuesta sin clave docente (`/api/estado`, `/api/publico`, `/api/colegios`), ids opacos, experimento recortado en «cerrado», modo sorpresa y CSV con ids del banco | NFR8, BR5.1 a BR5.5 |
| U2-S8 | Ningún archivo que escriba o lea la prueba guarda la clave docente; los comandos documentados (LEEME, `verificar.sh`) la pasan por el entorno. Contra `wrangler dev`, la clave de ensayo vive en `despliegues/cloudflare/.dev.vars`, ignorado por git y generado al azar (D9) | NFR9, project.md («Forbidden»: claves reales en archivos versionados) |
