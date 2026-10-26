# Monitoreo — U2

- La prueba es el monitor: su salida impresa (U2-O1) y el JSON de C3 (U2-O2) son lo que se mira.
- Qué mide de cada opción: p95 de responder y del tablero, si sobrevive un reinicio, el arranque en
  frío y las peticiones de la corrida (`nfr` del JSON, BR7.1 a BR7.4). U17 pone esas cifras en
  `despliegues/COMPARACION.md` junto a la cuota oficial de cada opción.
- Qué mira quien prueba durante la corrida: el tiempo de cada paso y la cuenta regresiva del
  vencimiento (U2-O4). Una corrida sin salida por más de 60 s en la espera es señal de que el servicio
  no responde; el tope de 20 s por petición la hace fallar sola (U2-R3).
- Consumo de cuota: después de una corrida contra Workers, quien prueba compara `peticiones` del JSON
  con el panel de Cloudflare (límite gratuito: 100.000 peticiones por día,
  https://developers.cloudflare.com/workers/platform/limits/, consultado el 2026-10-25) y lo anota en el
  `detalle` de la fila de NFR6 de la comparación.
- Nada se guarda aparte: no hay servicio de la prueba que vigilar.
