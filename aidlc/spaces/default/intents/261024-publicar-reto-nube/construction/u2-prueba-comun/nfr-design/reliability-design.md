# Confiabilidad — diseño U2

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

- **Determinismo** (U2-R1). `guion.Guion(semilla, participantes)` crea un `random.Random(semilla)` propio
  y consume el azar en un orden fijo: primero el grado de cada k, luego la decisión de acierto por
  (k, pregunta) en el orden de las misiones. Los hilos no tocan el generador: todas las decisiones se
  calculan antes de la fase de carga.
- **Repetible** (U2-R2). El sufijo de corrida (`sufijo()` de U1) va en cada nombre de sala, colegio y
  participante. En la nube cada corrida deja su sala de calibración en resultados y reinicia la sala más
  grande del reto; las demás quedan en resultados. No hay rutas para borrar salas hasta U6, y la prueba
  no las necesita.
- **Tolerancia a fallas de red** (U2-R3). `Cliente.pedir` captura `urllib.error.HTTPError` (devuelve el
  código y el cuerpo), `urllib.error.URLError` y `TimeoutError` (devuelve 0 y `{"error": "sin
  conexión"}`), y lee el cuerpo con `json.loads` dentro de un `try` que devuelve `{"error": "la respuesta
  no es JSON"}`. Un código 0 o 5xx hace fallar la comprobación en curso; `correr` solo termina con código
  2 si el primer `GET /api/publico` no conecta.
- **Detención ordenada** (U2-R4). `correr` recorre los pasos; cuando uno devuelve `False`, agrega «la
  prueba se detuvo en <paso>» y salta a `cerrar`, que escribe el JSON y espera a que los hilos de tablero
  terminen (`Event` compartido).
- **Reinicio a mitad** (U2-R5). `prueba.paso_6_reinicio`: `instantanea = {sala: resumen_recortado}` con
  estado, puntos, bono y respondidas por código; `manual` usa `input()`; `comando` usa
  `subprocess.run(comando, shell=True, timeout=300)` y después espera la salud hasta 120 s; la
  comparación es igualdad de diccionarios y la diferencia va al `detalle` solo como códigos y cifras.
- **Arranque en frío** (U2-R6). La primera petición de la corrida se mide siempre; solo con `--frio` se
  guarda como `arranque_frio_ms` y se compara con 30.000 ms.
- **Espera con reloj del servidor** (U2-R7). `carga.esperar_hasta(cliente, sala, objetivo)` lee
  `servidor_ahora` de `/api/publico?sala=` cada 10 s y duerme la diferencia; el objetivo es
  `abierto_en + duración + 2`, así un reinicio del servicio o un reloj local desviado no cambian el momento.
