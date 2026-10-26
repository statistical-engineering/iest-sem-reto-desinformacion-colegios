# Integración y despliegue — U6

- Sin despliegue automático; a mano y sin reto en curso (`project.md`, «Mandated»).
- `copiar.sh` pasa a escribir `src/version.json`; `verificar.sh` falla si falta (U6-R7) y agrega:
  1. `node --test despliegues/cloudflare/pruebas/exportacion.test.js` (csv, zip, copia, fechas, columnas
     secretas, encabezados contra el diccionario), nombrando el archivo;
  2. en la prueba común (modo nube, contra `wrangler dev`): descargar los dos CSV y compararlos con los
     de la versión local corrida con el mismo guion (U6-R4), descargar el paquete, abrirlo con `zipfile`,
     reabrir la copia con `sqlite3` en memoria (U6-R2), reiniciar, listar y descargar la copia, borrar
     la sala y comprobar los 404 (U6-S7).
- El diccionario de datos cambia en el mismo push que cualquier columna (C5); la prueba unitaria de
  encabezados lo hace cumplir.
- La revisión de PR no cambia. U6 supera 400 líneas (zip, csv, copia, exportación, resultados); el
  humano y el asistente suben directo a `develop`; otra persona la parte en un PR por módulo de
  `servicios/` (`team.md`, «Corrections»).
- Al cerrar U6, la opción Cloudflare pasa la prueba común completa (U2) en «TODO BIEN»: es la condición
  de `bolt-plan.md` (B11) para que U17 la compare.
