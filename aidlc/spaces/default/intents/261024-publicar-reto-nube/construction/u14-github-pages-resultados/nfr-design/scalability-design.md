# Escala — diseño U14

Diseño no funcional de U14. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- Tableros: la respuesta de `/api/publico?sala=` se arma en menos de 30 ms y pesa ≈ 5 KB; 10 tableros
  cada 2 s son 5 peticiones por segundo, la mitad de la carga del worker. Si U2 mide un p95 alto, la
  guía pide proyectar un solo tablero por sala y cerrar el panel mientras tanto (U14-E1). No se agrega
  caché en memoria de la vista pública: con un solo proceso y 2 s de sondeo la ganancia sería de
  milisegundos y complicaría FR3.2.
- Copias en `copias` como blob; la guía de cierre borra la sala con sus copias (U14-E2).
- Paquete en memoria con `io.BytesIO` (U14-E3).
