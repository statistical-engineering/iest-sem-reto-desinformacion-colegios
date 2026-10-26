# Monitoreo — U11

- Salud: `GET https://<usuario>.pythonanywhere.com/api/publico` responde `{"ok": true}`; la prueba común
  lo revisa primero y la prueba de humo de la guía lo pide a mano antes de cada reto (U11-O3). No hay
  vigilante automático gratuito en esta opción.
- Registros: `error.log` y `server.log` en la pestaña Web de PythonAnywhere; solo arranque, cambios de
  estado, 503 y 500 (U11-O1, U11-O2).
- Consumo: PythonAnywhere no cuenta las peticiones de la app web contra los CPU-segundos
  (https://help.pythonanywhere.com/pages/WhatAreCPUSeconds); el ancho de banda no tiene cifra pública,
  así que U2 anota las peticiones y los bytes de un ensayo (U11-E2). El panel de la cuenta muestra el
  disco usado frente a 512 MiB.
- Pantallas publicadas: historial de Actions y entorno `github-pages` del repositorio (U11-O4).
- Vencimiento de la app: el correo de aviso de PythonAnywhere una semana antes y el botón de prórroga de
  la pestaña Web (U11-R5).
