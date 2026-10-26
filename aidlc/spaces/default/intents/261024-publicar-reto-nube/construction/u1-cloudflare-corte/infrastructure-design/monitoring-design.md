# Monitoreo — U1

- Salud: `GET /api/publico` responde `{"ok": true}`; la prueba común lo revisa primero (U1-O3).
- Registros en vivo: `npx wrangler@4.148.0 tail`, solo arranque, cambios de estado y errores 500
  (U1-O1, U1-O2).
- Consumo: el tablero de Cloudflare muestra peticiones por día; el límite gratuito es 100.000
  (https://developers.cloudflare.com/workers/platform/limits/). U2 anota el consumo real de un ensayo
  (U1-E2).
