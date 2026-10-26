# Escala — U16

Requisitos no funcionales de U16, unidad de solo documentación sobre Cloudflare Containers. Salen de
`requirements.md` (NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Cifras de la documentación
oficial consultada el 2026-10-25. Decisiones del asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U16-E1 | NFR1 (40 personas, 10 salas) no se mide; se anota que una instancia `lite` (1/16 vCPU, 256 MiB, https://developers.cloudflare.com/containers/platform-details/limits/) correría el mismo `servidor.py` de hoy, que ya atiende 40 personas en un computador de aula, y que no hay autoescalado (https://developers.cloudflare.com/containers/beta-info/), lo que coincide con «una sola instancia» | NFR1 |
| U16-E2 | No hay cuota gratuita: la columna compara el consumo de una sesión con el uso incluido en Workers Paid (25 GiB-h, 375 vCPU-min, 200 GB-h, https://developers.cloudflare.com/containers/pricing/) y da el porcentaje en `lite` | NFR6 |
| U16-E3 | La columna agrega el caso «siempre encendido», porque no dormir sería la única forma de no perder SQLite, y muestra que excede el uso incluido | NFR6, NFR4 |
| U16-E4 | La columna dice qué pasa al pasar el uso incluido: se cobra por segundo según C4, sin suspensión | NFR6 |
