# Confiabilidad — diseño U11

Diseño no funcional de U11. Las decisiones están en `../decisions.md` (ADR-G1 a ADR-G7); los requisitos en `../nfr-requirements/`.

- Todo dato vive en `RETO_DATOS/reto.db` con `journal_mode=WAL` y `synchronous=NORMAL`; cada escritura
  termina con `COMMIT` antes de responder 200 (U11-R1). «Reload», `git pull` y los reinicios de la
  plataforma no tocan ese archivo.
- Los tiempos se guardan como segundos desde 1970 y la entrega por tiempo se calcula en cada petición
  con `reglas.hora_de_entrega` (U11-R2), sin hilos ni temporizadores (ADR-004).
- Arranque en frío: importar `src/` tarda menos de 1 s en esta máquina; validar el banco y abrir SQLite,
  menos de 0,5 s. Lo que no controla el código es el tiempo que tarda la plataforma en levantar el
  proceso tras un reinicio: U2 lo mide con «primera petición tras dormir» y la guía pide abrir el enlace
  antes del reto (U11-R3).
- Errores de plataforma: `sqlite3.OperationalError` tras el `busy_timeout` de 5 s responde 503 con
  `{"error": "El servidor está ocupado. Intenta de nuevo."}`; cualquier otra excepción responde 500 sin
  detalles y se registra con traza (U11-R4). El navegador tolera un 5xx sin JSON (C-15).
- Vencimiento mensual: la guía tiene el paso «prorrogar la app en la pestaña Web» antes de cada reto y al
  recibir el aviso de PythonAnywhere. El corte deja escrito en el `LEEME.md` qué pasa con una app vencida
  (comprobado al desplegar, U11-R5); los archivos y `reto.db` quedan en el disco de la cuenta en cualquier
  caso.
- Pages y API independientes: `estudiante.js` ya muestra «Sin conexión con el servidor…» cuando `fetch`
  falla y conserva el token en `localStorage`; no hay reintento automático de POST (contrato C1)
  (U11-R6).
- Volver atrás: `git checkout <commit anterior>` y «Reload» para la API; «Run workflow» sobre la
  referencia anterior para Pages. Ninguno de los dos toca los datos.
