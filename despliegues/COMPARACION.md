# Comparación de las opciones de hosting

Tabla que se llena con lo que mide la prueba común (`prueba_comun/`) contra el enlace de cada opción
(requisito FR12.4). Cada cifra lleva al lado el comando o la URL oficial de donde salió; una casilla sin
medir dice «pendiente».

| Criterio | Render | Cloudflare | Cloudflare Containers | Apps Script | GitHub Pages | PythonAnywhere |
|---|---|---|---|---|---|---|
| Pasa el corte delgado | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Pasa la prueba común («TODO BIEN») | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Latencia p95 al responder (meta ≤ 1 s) | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Latencia p95 del tablero (meta ≤ 1,5 s) | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Sobrevive a un reinicio sin perder puntajes | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Arranque en frío | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Consumo frente a la cuota gratuita (con URL oficial) | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Costo en US$ | de pago según `render.yaml`: no cumple NFR6 mientras no se apruebe el costo | pendiente | pendiente | pendiente | pendiente | pendiente |
| Piezas y servicios | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Líneas de código | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |
| Pasos para desplegar (persona del semillero) | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |

«PythonAnywhere» es el servidor que hoy corre el reto (`despliegues/github-pages/LEEME.md`); «GitHub Pages» solo redirige a él.

«Pasa todo» y el orden para elegir la más simple están en FR12.5 y FR12.6 de los requisitos. La
elección y la alternativa de respaldo las aprueba el humano en un ADR.
