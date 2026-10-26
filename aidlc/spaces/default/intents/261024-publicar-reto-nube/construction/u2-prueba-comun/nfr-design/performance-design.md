# Rapidez — diseño U2

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`; los componentes en
`logical-components.md`.

- **Hilos reales, no secuencia** (U2-P1). `carga.py` usa `concurrent.futures.ThreadPoolExecutor` con un
  hilo por participante (40) y un hilo por tablero (10). Cada hilo tiene su propio `Cliente`, porque
  `urllib` no comparte conexiones y así no hay un candado común. El GIL no estorba: el tiempo se va en
  esperar la red.
- **Medición en el hilo** (U2-P2). Cada hilo guarda sus muestras en una lista propia (`time.perf_counter`
  antes del `POST /api/responder` y después del `GET /api/estado` que le sigue); al terminar la fase se
  juntan y `percentil(muestras, 95)` calcula el p95 por el vecino más cercano: posición
  `ceil(0,95 × n) − 1` de la lista ordenada. Con 40 × 41 = 1.640 muestras de responder y unas 900 del
  tablero sobra para el umbral.
- **El tablero sondea con reloj propio** (U2-P2). Cada hilo de tablero duerme hasta el próximo múltiplo de
  2 s y pide `/api/publico?sala=`, igual que `tablero.html`; en la espera del vencimiento pasa a 10 s para
  no inflar las peticiones (U2-E2).
- **Calibración rápida** (U2-P4). Las huellas se calculan en memoria con `hashlib.sha256` sobre un JSON
  ordenado; los 40 calibradores comienzan y piden su estado en el mismo pool de hilos; solo los
  representantes (normalmente 4, uno por variante de `m2_trampas`) responden.
- **Tiempo total** (U2-P3). Las fases fuera de la espera son cortas; la espera real son los 10 minutos de
  `--duracion-min`. No hay forma de acortarla sin mover el reloj, que está descartado (OQ3).
