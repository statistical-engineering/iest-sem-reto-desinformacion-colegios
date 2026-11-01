# Integración y despliegue — U6

> **Revisión 2026-10-27 (una sola sala).** La prueba común usa la clave docente (`CLAVE_DOCENTE` de
> `.dev.vars`); en vez de «borrar la sala», reinicia y borra cada copia; se agrega `pantallas.test.js`.

- Sin despliegue automático; a mano y sin reto en curso (`project.md`, «Mandated»).
- `copiar.sh` pasa a escribir `src/version.json`; `verificar.sh` falla si falta (U6-R7) y agrega:
  1. `node --test despliegues/cloudflare/pruebas/exportacion.test.js` (csv, zip, copia, fechas, columnas
     secretas, encabezados contra el diccionario) y
     `node --test despliegues/cloudflare/pruebas/pantallas.test.js` (BR10.1), cada uno nombrando el
     archivo (`project.md`, «Corrections»: `node --test` con una carpeta falla en Node 24);
  2. en la prueba común (modo nube, contra `wrangler dev`): las comprobaciones `pantalla_*` de cada fila
     de «Pantallas completas»; descargar los dos CSV y compararlos con los de la versión local corrida
     con el mismo guion (U6-R4); descargar el paquete, abrirlo con `zipfile` y reabrir la copia con
     `sqlite3` en memoria (U6-R2); reiniciar con BORRAR, listar, descargar y borrar la copia, y comprobar
     el 404 posterior (U6-S7).
- El diccionario de datos cambia en el mismo push que cualquier columna (C5); la prueba unitaria de
  encabezados lo hace cumplir.
- La revisión de PR no cambia. U6 supera 400 líneas (zip, csv, copia, exportación, resultados); el
  humano y el asistente suben directo a `develop` tras correr a mano `verificar.sh` y el simulacro; otra
  persona la parte en un PR por módulo de `servicios/` (`team.md`, «Corrections»).
- Al cerrar U6, la opción Cloudflare pasa la prueba común completa (U2) en «TODO BIEN» y el recorrido de
  las tres pantallas queda anotado (BR10.3): es la condición de `bolt-plan.md` (B11) para que U17 la
  compare.
