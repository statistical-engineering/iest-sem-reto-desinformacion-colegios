# Monitoreo — U5

> **Revisión 2026-10-27 (una sola sala).** Salud sin `?sala=`; ya no hay `GET /api/admin/salas`: la vista
> de operación es la tarjeta «Colegios» del panel.

- Salud: `GET /api/publico` sin parámetros (U5-O4); 500 si falta `CLAVE_DOCENTE` o falló una migración.
- Registros con `npx wrangler@4.148.0 tail`: arranque con versión del esquema, migraciones, cambios de
  estado del reto, relojes arrancados, errores 500 (U5-O1); nada de inscripciones ni claves (U5-O2).
- Vista de operación: la tarjeta «Colegios» del panel, con el reloj y los equipos de cada colegio (U5-O3).
- CPU por petición: `npx wrangler@4.148.0 tail --format json` trae `cpuTime`; en el ensayo de U2 se
  anota el máximo de `resumen` y `responder` (U5-P4).
- Consumo diario: el tablero de Cloudflare, igual que U1 (U5-E2, U5-E3); si aparece la página 1027, se
  sigue la guía de U17 (ADR-W20).
