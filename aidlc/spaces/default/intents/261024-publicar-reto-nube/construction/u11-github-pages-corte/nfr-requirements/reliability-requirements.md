# Confiabilidad — U11

Requisitos no funcionales de U11, el corte delgado de GitHub Pages con la API en PythonAnywhere. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial consultada el 2026-10-25 (URL en `../decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U11-R1 | Toda escritura que respondió 200 queda en `reto.db` (SQLite en el disco persistente de PythonAnywhere, con `journal_mode=WAL`), que sobrevive a «Reload» de la app, a `git pull` y a los reinicios de los servidores de la plataforma | NFR4, ADR-G5 |
| U11-R2 | El reloj se calcula con horas guardadas, no con temporizadores en memoria: un reinicio no cambia ningún tiempo | NFR4, NFR11, ADR-004 |
| U11-R3 | Arranque en frío ≤ 30 s: la app no se apaga por inactividad corta, pero la plataforma reinicia sus servidores por mantenimiento y la primera petición vuelve a cargar el proceso (importar `src/`, validar el banco, abrir SQLite); U2 lo mide y la guía pide abrir el enlace unos minutos antes del reto | NFR5, ADR-G1 |
| U11-R4 | Si la plataforma agota el ancho de banda o cae, responde ella misma un error sin JSON; el navegador lo trata como un 5xx sin JSON (C-15). Si SQLite no consigue el candado en 5 s (`busy_timeout`), la API responde 503 `{"error": …}` (contrato C1) | NFR6, contrato C1 |
| U11-R5 | La app web gratuita vence si no se usa en un mes («1 month expiry», https://help.pythonanywhere.com/pages/FreeAccountsFeatures/); la guía exige prorrogarla desde la pestaña Web antes de cada reto y al recibir el correo de aviso, y el corte comprueba qué pasa con una app vencida (si basta un clic para reactivarla con sus datos intactos) | NFR6, NFR7 |
| U11-R6 | Las pantallas y la API fallan por separado: si Pages no responde, nadie entra; si la API no responde, las pantallas muestran «Sin conexión con el servidor…», el mensaje de hoy, y el estudiante reintenta con «Enviar» sin perder la sesión | FR5.1, contrato C1 |
