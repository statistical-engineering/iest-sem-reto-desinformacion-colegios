# Escala — diseño U1

Diseño no funcional de U1. Las decisiones están en `../decisions.md` (ADR-W1 a ADR-W5); los requisitos en `../nfr-requirements/`.

Estimación de una sesión de 90 minutos con 40 personas y 10 salas, con los sondeos de hoy (`estudiante.js`: cada 20 s en curso; `tablero.html`: cada 2 s):

| Fuente | Peticiones |
|---|---|
| Estado en curso, 40 × 5.400 s / 20 s | 10.800 |
| Responder y estado tras responder, 40 × 60 × 2 | 4.800 |
| Tableros, 10 × 5.400 s / 2 s | 27.000 |
| Panel docente, 10 × 5.400 s / 3 s | 18.000 |
| **Total** | **≈ 60.600** |

Pasa el 50 % de 100.000 por día si las 10 salas proyectan tablero y panel a la vez. Con 5 salas, la cifra baja a ≈ 38.000 (38 %). Decisión: se acepta para el corte; U2 mide el consumo real y U17 lo pone en la tabla (NFR6). Si se acerca al límite, la guía dice que el panel se cierre mientras se proyecta el tablero.
