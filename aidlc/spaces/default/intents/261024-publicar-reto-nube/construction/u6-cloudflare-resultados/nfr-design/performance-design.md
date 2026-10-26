# Rapidez — diseño U6

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18); los requisitos en `../nfr-requirements/`.

- `publico` con `?sala=` hace tres consultas (sala, conteo por estado, finalizados con colegio
  definitivo) y, solo en `cerrado` o `resultados`, una cuarta con las respuestas del Exp. 01 de la sala;
  `ordenar` y `calcular` son las de U4 (U4-P1). Sin caché: 10 tableros cada 2 s son 5 peticiones/s de
  microsegundos cada una (U6-P1).
- `estado` en resultados agrega `revision_publica`, que reutiliza la caché de HMAC por semilla de
  `reto.js` (los ids opacos de la revisión son los mismos del examen), y `puesto_de` sobre los
  finalizados de la sala (U6-P2).
- El paquete se arma en memoria con `Uint8Array` y una sola concatenación final; los cuatro CSV salen de
  cuatro consultas (una por tabla, con `JOIN` a la vista de colegios), la copia de las mismas filas ya
  leídas, sin volver a consultar (U6-P3, U6-P5). Es síncrono dentro de `blockConcurrencyWhile`; con
  40 personas son ≈ 1.700 filas de respuestas, unos 50 ms de CPU estimados.
- Reiniciar reutiliza `armar_copia` y hace tres `DELETE` por `id_sala` más un `UPDATE` (U6-P4).
- El CRC-32 del zip usa tabla precalculada una vez por instancia del módulo.
