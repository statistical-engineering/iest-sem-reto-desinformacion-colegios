// Única línea que se cambia: la dirección del servidor del reto en PythonAnywhere.
// Este sitio no guarda preguntas ni respuestas; solo lleva al servidor, que es quien califica.
window.RETO_SERVIDOR = "https://angels16384.pythonanywhere.com";

// Lleva al servidor conservando la ruta pedida (/, /admin o /tablero) y el ?sala= si viene.
window.irAlReto = function (ruta) {
  var destino = window.RETO_SERVIDOR.replace(/\/$/, "") + ruta + location.search + location.hash;
  var enlace = document.getElementById("enlace");
  if (enlace) enlace.href = destino;
  if (window.RETO_SERVIDOR.indexOf("TU_USUARIO") === -1) location.replace(destino);
};
