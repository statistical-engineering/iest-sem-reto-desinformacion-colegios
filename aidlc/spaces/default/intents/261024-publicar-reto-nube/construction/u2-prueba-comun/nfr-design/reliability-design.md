# Confiabilidad — diseño U2

> **Revisión 2026-10-27 (una sola sala).** «Repetible» ya no deja salas en resultados: la prueba exige el
> reto vacío y lo restaura al final (BR1.5, BR1.6, U2-R8). El reinicio compara el resumen del único reto
> y la espera usa el arranque de cada colegio.

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

- **Determinismo** (U2-R1). `guion.Guion(semilla, participantes)` crea un `random.Random(semilla)` propio
  y consume el azar en un orden fijo: primero el colegio, el papel y el grado de cada k, luego la decisión
  de acierto por (k, pregunta) en el orden de las misiones. Los hilos no tocan el generador: todas las
  decisiones se calculan antes de la fase de carga.
- **Repetible** (U2-R2). `prueba.paso_2` lee el resumen y guarda la `ConfiguracionInicial` (duración,
  modo sorpresa, retro, colegios y copias); si el reto no está en inscripción y vacío, termina con
  código 2 sin escribir nada. El sufijo de corrida (`sufijo()` de U1) va en cada nombre de colegio y
  participante.
- **Restauración siempre** (U2-R4, U2-R8). `correr` envuelve los pasos en `try`/`finally`: el `finally`
  llama a `restaurar(cliente, configuracion_inicial, copias_creadas)` (BR1.6) y después escribe el JSON.
  `KeyboardInterrupt` también pasa por ahí. Lo que no se pudo restaurar va al `detalle` de
  `reto_restaurado`.
- **Tolerancia a fallas de red** (U2-R3). `Cliente.pedir` captura `urllib.error.HTTPError` (devuelve el
  código y el cuerpo), `urllib.error.URLError` y `TimeoutError` (devuelve 0 y `{"error": "sin
  conexión"}`), y lee el cuerpo con `json.loads` dentro de un `try` que devuelve `{"error": "la respuesta
  no es JSON"}`. Un código 0 o 5xx hace fallar la comprobación en curso; `correr` solo termina con código
  2 si el primer `GET /api/publico` no conecta o si el reto tiene datos.
- **Detención ordenada** (U2-R4). Cuando una esencial devuelve `False`, `correr` agrega «la prueba se
  detuvo en <paso>», marca el `Event` que detiene los hilos de tablero y panel y salta al cierre.
- **Reinicio a mitad** (U2-R5). `prueba.paso_6_reinicio`: `instantanea = resumen_recortado(resumen)` con
  estado, puntos, bono y respondidas por código, y `colegios[]` con su arranque; `manual` usa `input()`;
  `comando` usa `subprocess.run(comando, shell=True, timeout=300)` y después espera la salud hasta
  120 s; la comparación es igualdad de diccionarios y la diferencia va al `detalle` solo como códigos y
  cifras.
- **Arranque en frío** (U2-R6). La primera petición de la corrida se mide siempre; solo con `--frio` se
  guarda como `arranque_frio_ms` y se compara con 30.000 ms.
- **Espera con reloj del servidor** (U2-R7). `carga.esperar_hasta(cliente, objetivo)` lee
  `servidor_ahora` de `GET /api/publico` cada 10 s y duerme la diferencia; los objetivos son
  `arranque_A + duración + 2` y `arranque_C + duración + 2` en la nube (arranques leídos de `colegios[]`
  del resumen) y `abierto_en + duración + 2` en local, así un reinicio del servicio o un reloj local
  desviado no cambian el momento.
