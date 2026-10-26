# Monitoreo — U5

- Salud: `GET /api/publico` sin `?sala=` (U5-O4).
- Registros con `npx wrangler@4.148.0 tail`: arranque con versión del esquema, migraciones, salas
  creadas y borradas, cambios de estado por sala, errores 500 (U5-O1); nada de inscripciones ni claves
  (U5-O2).
- Vista de operación del semillero: `GET /api/admin/salas` (U5-O3), que `admin.js` muestra como tabla.
- CPU por petición: `npx wrangler@4.148.0 tail --format json` trae `cpuTime`; en el ensayo de U2 se
  anota el máximo de `resumen` y `responder` (U5-P4).
- Consumo diario: el tablero de Cloudflare, igual que U1 (U5-E2, U5-E3).
