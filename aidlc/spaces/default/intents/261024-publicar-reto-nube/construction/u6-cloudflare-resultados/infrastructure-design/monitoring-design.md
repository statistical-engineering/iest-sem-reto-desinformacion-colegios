# Monitoreo — U6

> **Revisión 2026-10-27 (una sola sala).** Sin `GET /api/admin/salas`: el almacenamiento se revisa con la
> tarjeta «Copias» del panel.

- Salud y registros como U1 y U5; U6 suma las líneas de reiniciar, borrar copia, migración 3, «copia
  dañada» y el commit en el arranque (U6-O1), y no registra descargas (U6-O2).
- Almacenamiento: el panel de Cloudflare muestra el almacenamiento del objeto; con la regla de borrar
  las copias al cerrar el reto se mantiene en MB (U6-E1). Si un día supera 1 GB, la guía dice revisar la
  tarjeta «Copias» y borrar las ya guardadas en el Drive.
- CPU del paquete y de reiniciar: `wrangler tail --format json` (`cpuTime`) en el ensayo de U2 (U6-P3,
  U6-P4); la cifra va a la tabla de U17.
- Trazabilidad de cada paquete: `metadatos.json` (U6-O3).
- Cierre: los pasos de comprobación de `infrastructure-specification.md` («Cierre de un reto») (U6-O4).
- Cierre de la unidad: el recorrido de las tres pantallas anotado en `code-summary.md` (U6-O5).
