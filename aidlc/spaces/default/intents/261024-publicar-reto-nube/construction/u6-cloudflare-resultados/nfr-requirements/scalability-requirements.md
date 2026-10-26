# Escala — U6

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Las cuotas se citan de la documentación oficial consultada el 2026-10-25. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U6-E1 | Almacenamiento de copias: ≤ 0,5 MB por copia con 40 personas; 10 salas con 5 copias cada una ≈ 25 MB, frente a los 5 GB del plan gratuito («Storage per account 5GB (Free)», https://developers.cloudflare.com/durable-objects/platform/limits/) y el límite por objeto; las copias se borran con la sala al cerrar el reto | NFR6, NFR10.1, ADR-W17 |
| U6-E2 | Ninguna fila ni valor supera 2 MB («Maximum string, BLOB or table row size 2 MB», misma URL): el contenido de una copia va en trozos de 512 KiB, cualquiera sea su tamaño | ADR-W17 |
| U6-E3 | Escrituras por copia: una fila en `copias` más un trozo por cada 512 KiB (1 o 2); reiniciar 10 salas gasta ≈ 30 filas, despreciable frente a las 100.000 filas escritas por día («SQLite rows written 100,000 per day», https://developers.cloudflare.com/durable-objects/platform/pricing/) | NFR6 |
| U6-E4 | El ranking del tablero (`/api/publico` cada 2 s por sala) ordena ≤ 40 filas y recorta a 10; su costo no crece con el número de salas porque cada petición lee una sala | NFR1, NFR3 |
| U6-E5 | El paquete pesa ≈ 1 MB sin compresión para 40 personas (ADR-W15); se devuelve de una vez, sin flujo, dentro de los límites de respuesta del Worker | FR9.1 |
