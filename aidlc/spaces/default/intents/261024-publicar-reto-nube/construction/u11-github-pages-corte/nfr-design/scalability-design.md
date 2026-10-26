# Escala — diseño U11

Diseño no funcional de U11. Las decisiones están en `../decisions.md` (ADR-G1 a ADR-G7); los requisitos en `../nfr-requirements/`.

Estimación de una sesión de 90 minutos con 40 personas y 10 salas, con los sondeos de hoy
(`estudiante.js`: cada 20 s en curso; `tablero.html`: cada 2 s; panel: cada 3 s), la misma de U1:

| Fuente | Peticiones a la API |
|---|---|
| Estado en curso, 40 × 5.400 s / 20 s | 10.800 |
| Responder y estado tras responder, 40 × 60 × 2 | 4.800 |
| Tableros, 10 × 5.400 s / 2 s | 27.000 |
| Panel docente, 10 × 5.400 s / 3 s | 18.000 |
| Consultas previas `OPTIONS` (una por pestaña cada 600 s, 60 pestañas) | ≈ 540 |
| **Total** | **≈ 61.100** |

Son ≈ 11 peticiones por segundo en promedio para un solo worker. Con menos de 50 ms por petición dentro
del candado (U11-P3) el worker está ocupado alrededor del 55 % del tiempo: cabe, pero sin holgura grande.
Decisiones:

- PythonAnywhere no cuenta estas peticiones contra los CPU-segundos (U11-E2); lo que no tiene cifra es el
  ancho de banda. Cada respuesta de `/api/publico` pesa unos 5 KB con 40 personas: 27.000 × 5 KB ≈ 135 MB
  por sesión. U2 lo mide y U17 lo anota frente a «Low».
- Si el p95 no cumple, la guía pide cerrar el panel mientras se proyecta el tablero (baja a ≈ 43.000) o
  abrir menos tableros a la vez. No hay escala horizontal en el plan gratuito; es un límite de la opción.
- Pages: 15 MB por sesión frente a 100 GB al mes (U11-E3); no hace falta diseño.
- Disco: una sala pesa menos de 1 MB; las copias de U14 se cuentan en `copias` y la guía de cierre las
  borra con la sala (U11-E4).
