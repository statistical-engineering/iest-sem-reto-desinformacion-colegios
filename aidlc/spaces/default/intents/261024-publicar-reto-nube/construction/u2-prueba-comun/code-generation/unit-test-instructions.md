# Instrucciones de pruebas — U2

- Marco: `unittest` de Python 3.12, sin paquetes (`project.md`, «Testing Posture»: `pytest` no está
  aprobado). La red se prueba con `pruebas/servidor_falso.py` (`http.server`); la lógica pura, sin mocks.
- Comando de la unidad (desde la raíz del repo):
  `PYTHONPATH=despliegues/prueba_comun/src python3 -m unittest discover -s despliegues/prueba_comun/pruebas -p 'test_*.py'`
- Un solo archivo: `PYTHONPATH=despliegues/prueba_comun/src python3 -m unittest despliegues/prueba_comun/pruebas/test_guion.py`.
- Cobertura objetivo: 80 % de líneas de `despliegues/prueba_comun/src/` (piso del alcance `classic`),
  medida con `trace` en una carpeta temporal fuera del repo:
  `PYTHONPATH=despliegues/prueba_comun/src python3 -m trace --count --missing --summary --coverdir=<carpeta temporal> --module unittest discover -s despliegues/prueba_comun/pruebas -p 'test_*.py'`;
  `prueba.py` se cubre corriendo la prueba bajo `trace` contra la versión local y contra `wrangler dev`.
- La clave docente va siempre por el entorno, nunca en un archivo versionado ni en la línea de comandos:
  - URL de Workers: `read -rs PRUEBA_CLAVE && export PRUEBA_CLAVE`;
  - `wrangler dev`: `verificar.sh` la toma de `despliegues/cloudflare/.dev.vars` (ignorado por git) y la
    exporta;
  - versión local: una clave de ensayo al azar en `PRUEBA_CLAVE`, pasada a `servidor.py` como
    `RETO_CLAVE`.
- Prueba común contra la versión local (dos terminales, base aparte para no tocar `datos/reto.db`):
  1. `cd 2_Aplicacion_Reto && RETO_CLAVE="$PRUEBA_CLAVE" RETO_DATOS=../despliegues/cloudflare/.wrangler/local-ref python3 servidor.py --puerto 8790 --db ../despliegues/cloudflare/.wrangler/local-ref/reto.db`
  2. `python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8790 --modo local --opcion local`
  - Se espera la parte base en «TODO BIEN»; fugas fallan mientras U3 siga saltada; relojes no aplican.
- Contra `wrangler dev`: `bash despliegues/cloudflare/herramientas/verificar.sh` (vencimiento real con
  `DURACION_MINIMA_MIN=1` en `.dev.vars` y `--duracion-min 2`, D9). Se espera «TODO BIEN».
- Contra la URL de Workers (solo sin reto en curso y con el reto vacío):
  `python3 despliegues/prueba_comun/src/prueba.py --url https://<nombre>.workers.dev --modo nube --opcion cloudflare --vencimiento omitir --reinicio manual --frio --referencia despliegues/prueba_comun/mediciones/local_<AAAA-MM-DD>.json`.
  Se espera «TODO BIEN», con el vencimiento real en «no aplica».
- Datos de prueba: preguntas inventadas en las pruebas `unittest`; nunca se copian respuestas del banco.
  La prueba común saca la clave de la `revision` de un reto de calibración y no la escribe en ningún lado.
- Después: `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` en «TODO BIEN».
