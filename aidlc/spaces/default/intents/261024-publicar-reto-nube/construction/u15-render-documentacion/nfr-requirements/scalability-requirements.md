# Escala — U15

Requisitos no funcionales de U15, unidad de solo documentación sobre Render. Salen de `requirements.md`
(NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Cifras de la documentación oficial consultada el
2026-10-25. Decisiones del asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U15-E1 | NFR1 (40 personas, 10 salas) no se mide; se anota que el plan con disco corre en una sola instancia («You can't scale a service to multiple instances if it has a disk attached», https://render.com/docs/disks), lo que coincide con «una sola instancia» de `project.md` | NFR1 |
| U15-E2 | La columna compara el consumo con la cuota que manda: 750 horas-instancia al mes del plan gratuito (https://render.com/docs/free) y 100 GB de ancho de banda del plan Hobby (https://render.com/pricing). Un enlace fijo siempre encendido usa 96 a 99 % de las horas: supera el 50 % de NFR6 | NFR6 |
| U15-E3 | La columna dice qué pasa si la cuota se agota a mitad del reto: los servicios gratuitos se suspenden el resto del mes (https://render.com/docs/free) | NFR6 |
