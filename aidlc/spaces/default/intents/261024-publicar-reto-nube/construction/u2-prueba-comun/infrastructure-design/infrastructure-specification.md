# Infraestructura — U2 `u2-prueba-comun`

> **Revisión 2026-10-27 (una sola sala).** La clave es siempre la docente (`CLAVE_DOCENTE` en el
> servicio, `PRUEBA_CLAVE` en la terminal); contra `wrangler dev` se prueba el vencimiento real con
> `DURACION_MINIMA_MIN` en `.dev.vars` (D9) y contra la URL de Workers no; la prueba ya no deja salas
> en el servicio: exige el reto vacío y lo restaura (BR1.5, BR1.6).

Sale de `../nfr-design/` y de `../nfr-requirements/`. La prueba común **no se despliega**: corre desde la
computadora de quien prueba (`unit-of-work.md`, U2, «Despliegue»). No crea ningún recurso en la nube ni
gasta nada (regla de `project.md`, NFR6).

## Piezas

| Pieza | Configuración | Dónde |
|---|---|---|
| Intérprete | Python 3.12 (`.python-version`), solo biblioteca estándar | computadora de quien prueba |
| Código | `despliegues/prueba_comun/src/` (`prueba.py`, `cliente.py`, `guion.py`, `carga.py`, `pantallas.py`, `mediciones.py`) y `contrato_api.yaml` | repositorio, rama `develop` |
| Pruebas | `despliegues/prueba_comun/pruebas/test_*.py` y `servidor_falso.py` | repositorio |
| Salida | `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` (la corrida contra `wrangler dev` usa `--salida …/cloudflare-dev_<AAAA-MM-DD>.json`) | repositorio, versionado (sin secretos) |
| Clave | `PRUEBA_CLAVE` en el entorno de la terminal; `--clave` existe pero no se usa en los comandos documentados | nunca en un archivo versionado |
| Clave y mínimo de ensayo en Workers local | `despliegues/cloudflare/.dev.vars` con `CLAVE_DOCENTE` (al azar, 24 caracteres) y `DURACION_MINIMA_MIN=1` | ignorado por git; nunca en `wrangler.jsonc` ni como secreto del despliegue (D9) |
| Referencia local | `servidor.py` con `RETO_CLAVE`, `--db` y `RETO_DATOS` en una carpeta ignorada por git, puerto 8790 | `despliegues/cloudflare/.wrangler/local-ref/` (ya ignorada) o cualquier carpeta fuera de `2_Aplicacion_Reto/datos/` |

## Cómo se corre contra cada versión

1. **Versión local** (referencia de NFR11):

   ```bash
   export PRUEBA_CLAVE="$(python3 -c 'import secrets; print(secrets.token_hex(12))')"
   (cd 2_Aplicacion_Reto && RETO_CLAVE="$PRUEBA_CLAVE" RETO_DATOS=../despliegues/cloudflare/.wrangler/local-ref \
     python3 servidor.py --puerto 8790 --db ../despliegues/cloudflare/.wrangler/local-ref/reto.db) &
   python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8790 --modo local --opcion local
   ```

   La parte base da «TODO BIEN»; la parte de fugas falla mientras U3 siga saltada y los relojes no
   aplican (FR12.3).
2. **Workers en local** (sin publicar): `bash despliegues/cloudflare/herramientas/verificar.sh`, que crea
   `.dev.vars` si falta, levanta `wrangler dev` y corre la prueba en modo nube con `--duracion-min 2`,
   vencimiento real y reinicio por comando. Es el comando de verificación de Construcción
   (`verification-command.txt`).
3. **Workers publicado**: solo sin reto en curso y con el reto vacío. Quien prueba escribe la clave docente
   sin que se vea (`read -rs PRUEBA_CLAVE && export PRUEBA_CLAVE`) y corre la prueba con
   `--opcion cloudflare --vencimiento omitir --reinicio manual` (redespliega con
   `npx wrangler@4.148.0 deploy` cuando la prueba lo pide), `--frio` si pasaron 15 minutos sin tráfico y
   `--referencia` con el JSON de la corrida local para comparar fracciones y CSV (BR8.2).

## Qué deja en el servicio probado

- Antes de escribir nada exige el reto en inscripción y sin inscritos; si no, termina con código 2.
- Al terminar, aunque una esencial falle o se corte con Ctrl+C: el reto reiniciado, la misma
  configuración y la misma lista de colegios del docente, y sin las copias que la prueba creó (en la nube).
- Local: la configuración restaurada; las copias `.db` de «Reiniciar» quedan en la carpeta de `--db`,
  porque la versión local no las borra.

## Volver atrás

No aplica: la prueba no cambia nada del repositorio salvo el JSON de mediciones, que se puede borrar o
reescribir con otra corrida.
