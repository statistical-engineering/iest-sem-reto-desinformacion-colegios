# Rapidez — diseño U2

> **Revisión 2026-10-27 (una sola sala).** Un hilo de tablero sobre `GET /api/publico` sin parámetros y
> un hilo de panel sobre `GET /api/admin/resumen`, en vez de 10 tableros con `?sala=`; los participantes
> de B y C esperan el arranque de su colegio; el tiempo total depende de contra qué se corre (D9).

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`; los componentes en
`logical-components.md`.

- **Hilos reales, no secuencia** (U2-P1). `carga.py` usa `concurrent.futures.ThreadPoolExecutor` con un
  hilo por participante (40), uno de tablero y uno de panel. Cada hilo tiene su propio `Cliente`, porque
  `urllib` no comparte conexiones y así no hay un candado común. El GIL no estorba: el tiempo se va en
  esperar la red. Los hilos de B y C esperan un `Event` que `prueba.py` marca al arrancar su colegio.
- **Medición en el hilo** (U2-P2). Cada hilo guarda sus muestras en una lista propia (`time.perf_counter`
  antes del `POST /api/responder` y después del `GET /api/estado` que le sigue); al terminar la fase se
  juntan y `percentil(muestras, 95)` calcula el p95 por el vecino más cercano: posición
  `ceil(0,95 × n) − 1` de la lista ordenada. Con unas 1.500 muestras de responder sobra para el umbral.
- **El tablero sondea con reloj propio** (U2-P2). El hilo de tablero duerme hasta el próximo múltiplo de
  2 s y pide `GET /api/publico` sin parámetros, igual que `tablero.html`; corre desde la apertura del reto
  principal hasta la publicación de resultados, y en las esperas del vencimiento pasa a 10 s para no
  inflar las peticiones (U2-E2). El hilo de panel pide el resumen cada 3 s durante la carga, como
  `admin.js`.
- **Calibración rápida** (U2-P4). Las huellas se calculan en memoria con `hashlib.sha256` sobre un JSON
  ordenado; los 40 calibradores comienzan y piden su estado en el mismo pool de hilos; solo los
  representantes (normalmente 4, uno por variante de `m2_trampas`) responden.
- **Tiempo total** (U2-P3). Las fases fuera de la espera son cortas. La espera real es `--duracion-min`
  más 40 s (el arranque de C) en la nube y la duración en local; con `--vencimiento omitir` no hay
  espera. No hay forma de acortarla sin mover el reloj, que está descartado (OQ3, D9).
