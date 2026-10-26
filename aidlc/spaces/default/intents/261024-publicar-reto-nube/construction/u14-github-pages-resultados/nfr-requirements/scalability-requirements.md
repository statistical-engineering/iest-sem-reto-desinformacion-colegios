# Escala — U14

Requisitos no funcionales de U14, resultados y exportación de la opción GitHub Pages. Salen de `requirements.md`, del diseño funcional de U14 y del ADR de U11. Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U14-E1 | 10 tableros a la vez (27.000 peticiones por sesión, ≈ 5 KB cada una ≈ 135 MB) sobre el único worker; es la carga dominante de la opción y U2 la mide frente al ancho de banda «Low» sin cifra del plan gratuito | NFR3, NFR6, U11-E2 |
| U14-E2 | Copias: cada «Reiniciar» guarda menos de 1 MB; 100 copias ocupan menos de 100 MB de los 512 MiB; la guía de cierre borra la sala con sus copias al terminar cada reto | NFR6, NFR10.1 |
| U14-E3 | El paquete se arma en memoria (`io.BytesIO`); con 40 personas pesa menos de 2 MB, muy por debajo de la memoria del worker | NFR2 |
