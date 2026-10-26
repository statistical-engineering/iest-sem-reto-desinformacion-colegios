# Prueba común

Una sola prueba que corre contra la dirección de cualquier versión del reto (requisito FR12.3), para que
todas las opciones de hosting se midan igual. Hoy es la prueba común **mínima** del corte delgado (U1): los
8 pasos de `functional-spec.md` de U1 y las pantallas. Las unidades siguientes la amplían.

Solo usa la biblioteca estándar de Python 3.12: no hay que instalar nada.

## Cómo se corre

Desde la raíz del repositorio:

```bash
python3 despliegues/prueba_comun/src/prueba.py --url <dirección> --clave <clave> --modo nube
python3 despliegues/prueba_comun/src/prueba.py --url <dirección> --clave <clave> --modo local
```

- `--url`: la dirección de la versión, por ejemplo `http://localhost:8787` o la de `workers.dev`.
- `--clave`: en `--modo nube`, la clave del semillero; en `--modo local`, la clave docente de
  `servidor.py`.
- `--modo nube` (el de siempre): la prueba crea una sala propia y un colegio de ensayo con un nombre
  único por corrida, así que se puede repetir sin borrar nada.
- `--modo local`: para la versión de `2_Aplicacion_Reto/`, que tiene una sola sala y escribe el colegio
  como texto. Corre `servidor.py` con una base aparte para no tocar la real, por ejemplo:

  ```bash
  cd 2_Aplicacion_Reto
  RETO_DATOS=../despliegues/cloudflare/.wrangler/local-ref python3 servidor.py --puerto 8790 --clave UNACLAVEDEPRUEBA --db ../despliegues/cloudflare/.wrangler/local-ref/reto.db
  ```

  Esa carpeta está ignorada por git. Ojo: en modo local la prueba abre la sala, inscribe a alguien y lo
  hace entregar; nunca la corras contra la base de un reto real.

La dirección y la clave también se pueden dar con las variables `PRUEBA_URL` y `PRUEBA_CLAVE`, para no
escribir la clave en la línea de comandos.

## Qué revisa

1. Salud: `GET /api/publico` sin `?sala=` responde solo `{"ok": true}` en la nube.
2. Claves: una clave mala da 403, la clave en la dirección (`?clave=`) no sirve, la del semillero crea una
   sala y la de la sala entra con rol «sala» (en local: la clave docente entra).
3. Colegio provisional con nombre único; el mismo nombre en mayúsculas da 400 con «existente»; la clave
   de una sala no actúa sobre otra; la sala se abre.
4. Inscripción; un colegio que no está en la lista da 400; la inscripción repetida da 400; volver a
   entrar con el código.
5. Comenzar: `/api/estado` no trae respuesta, explicación, tolerancia ni veredicto, y en la nube todos los
   ids que ve el navegador son opacos.
6. Responder una pregunta de opción una sola vez; la segunda vez da 400.
7. La respuesta guardada sale igual a la enviada.
8. Entregar; después ya no se acepta responder.
9. Pantallas: `/`, `/admin`, `/tablero` y archivos de `/static/` responden 200; el banco nunca se sirve
   por una dirección (404).

Termina en «TODO BIEN» (código 0) o con la lista de fallas (código 1); si no hay conexión, código 2. Nunca
imprime claves, tokens ni respuestas correctas.

## Lo que todavía no revisa

Las demás comprobaciones de `2_Aplicacion_Reto/pruebas/simulacro.py`, la separación entre varias salas,
la latencia, el reinicio y el arranque en frío llegan con las unidades siguientes. `simulacro.py` no se
copia ni se cambia: sigue siendo la prueba de la versión local.
