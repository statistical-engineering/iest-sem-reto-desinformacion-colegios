# Observación — diseño U11

Diseño no funcional de U11. Las decisiones están en `../decisions.md` (ADR-G1 a ADR-G7); los requisitos en `../nfr-requirements/`.

- `logging.basicConfig` a `stderr` con formato fijo `hora nivel mensaje`; solo arranque, cambio de
  estado de sala, 503 y 500 con traza (U11-O1).
- En PythonAnywhere se leen en la pestaña Web: `<usuario>.pythonanywhere.com.error.log` (stderr) y
  `.server.log`; en local, en la terminal de `servidor_local.py` (U11-O2).
- Salud: `GET /api/publico` → `{"ok": true}` (U11-O3). No hay vigilante externo gratuito en esta
  opción: la prueba de humo de la guía lo pide a mano antes de cada reto.
- Qué pantallas están publicadas: el historial de «Actions → Publicar pantallas» y el entorno
  `github-pages` del repositorio muestran la referencia y la fecha (U11-O4).
