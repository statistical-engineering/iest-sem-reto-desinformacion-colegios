# Infraestructura — U2 `u2-prueba-comun`

Sale de `../nfr-design/` y de `../nfr-requirements/`. La prueba común **no se despliega**: corre desde la
computadora de quien prueba (`unit-of-work.md`, U2, «Despliegue»). No crea ningún recurso en la nube ni
gasta nada (regla de `project.md`, NFR6).

## Piezas

| Pieza | Configuración | Dónde |
|---|---|---|
| Intérprete | Python 3.12 (`.python-version`), solo biblioteca estándar | computadora de quien prueba |
| Código | `despliegues/prueba_comun/src/` (`prueba.py`, `cliente.py`, `guion.py`, `carga.py`, `mediciones.py`) | repositorio, rama `develop` |
| Pruebas | `despliegues/prueba_comun/pruebas/test_*.py` y `servidor_falso.py` | repositorio |
| Salida | `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` | repositorio, versionado (sin secretos) |
| Clave | `PRUEBA_CLAVE` en el entorno de la terminal, o `--clave` | nunca en un archivo versionado |
| Referencia local | `servidor.py` con `--db` y `RETO_DATOS` en una carpeta ignorada por git, puerto 8790 | `despliegues/cloudflare/.wrangler/local-ref/` (ya ignorada) o cualquier carpeta fuera de `2_Aplicacion_Reto/datos/` |

## Cómo se corre contra cada versión

1. **Versión local** (referencia de NFR11):

   ```bash
   cd 2_Aplicacion_Reto
   RETO_DATOS=../despliegues/cloudflare/.wrangler/local-ref python3 servidor.py --puerto 8790 --clave UNACLAVEDEPRUEBA --db ../despliegues/cloudflare/.wrangler/local-ref/reto.db
   # en otra terminal, desde la raíz
   PRUEBA_CLAVE=UNACLAVEDEPRUEBA python3 despliegues/prueba_comun/src/prueba.py --url http://localhost:8790 --modo local --opcion local
   ```

   La parte base da «TODO BIEN»; la parte de fugas falla hasta U3 (FR12.3).
2. **Workers en local** (sin publicar): `bash despliegues/cloudflare/herramientas/verificar.sh`, que
   levanta `wrangler dev` y corre la prueba en modo nube. Es el comando de verificación de Construcción
   (`verification-command.txt`).
3. **Workers publicado**: la URL de `workers.dev` con la clave del semillero, `--opcion cloudflare`,
   `--reinicio manual` (quien prueba redespliega con `npx wrangler@4.148.0 deploy` cuando la prueba lo
   pide) y `--frio` si pasaron 15 minutos sin tráfico. Después, `--referencia` con el JSON de la corrida
   local para comparar fracciones (BR8.2).

## Qué deja en el servicio probado

- Nube: una sala «calibración» en resultados y 10 salas del reto, la más grande reiniciada y las demás en
  resultados. No se borran: la ruta de borrar salas llega con U6, y los nombres únicos por corrida evitan
  choques.
- Local: la única sala reiniciada dos veces (calibración y paso 10), con sus dos copias `.db` en la
  carpeta de `--db`.

## Volver atrás

No aplica: la prueba no cambia nada del repositorio salvo el JSON de mediciones, que se puede borrar o
reescribir con otra corrida.
