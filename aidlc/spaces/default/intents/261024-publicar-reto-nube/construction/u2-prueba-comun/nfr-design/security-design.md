# Seguridad — diseño U2

> **Revisión 2026-10-27 (una sola sala).** Desaparecen `SalaDePrueba.clave_sala` y la prueba de la clave
> de otra sala; `claves_403` se reparte en las comprobaciones de la parte `claves` (BR6.3); la clave
> llega de preferencia por `PRUEBA_CLAVE` (U2-S8).

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U2-S1 | `main` toma la clave de `--clave` si se dio y si no de `os.environ["PRUEBA_CLAVE"]`; `argparse` no lleva `default` con la clave (así `--help` no la muestra). `Cliente` la recibe en su constructor, la guarda en un atributo que su `__repr__` no muestra y la pone solo en `X-Clave-Admin`, sin `strip()` ni cambio de mayúsculas. La única petición con `?clave=` es `claves_url`, y su URL no se imprime ni va al `detalle` |
| U2-S2 | `ParticipanteFicticio.token` es un campo de dataclass con `repr=False`, así un `print` accidental no lo muestra; no existe en `Medicion` |
| U2-S3 | `guion.clave_por_texto(revisiones, misiones)` devuelve un `dict` que vive en `Corrida` y muere con el proceso; ningún módulo abre archivos del repositorio: `prueba.py` solo escribe el JSON y lee `--referencia`; `test_sin_secretos.py` revisa que `src/` no contenga `banco_preguntas` ni `open(` fuera de `mediciones.py` |
| U2-S4 | `mediciones.armar(corrida)` construye el JSON solo con ids, partes, booleanos y cifras; `validar_medicion(medicion, clave)` rechaza cualquier `detalle` que contenga una clave de la lista secreta (`respuesta`, `explicacion`, `tolerancia`, `verdad`, `multitud_acierta`, `veredicto`), el texto de la clave docente o un token, y una `url` con `?` |
| U2-S5 | Nombres «Detective <k> <sufijo>», «Calibrador <n> <sufijo>» y «Colegio Prueba <letra> <sufijo>», con sufijo de fecha y microsegundos; `paso_2` exige el reto vacío (BR1.5); el LEEME repite la advertencia de no correr contra `datos/reto.db` y da el comando con `--db` y `RETO_DATOS` aparte |
| U2-S6 | Parte `claves` en `prueba.paso_2`: `base_panel_clave` (sin cabecera), `claves_incorrecta`, `claves_url`, `claves_mayusculas` (403 y el cuerpo sin `participantes` ni `ranking`), `claves_espacios` (200), `claves_login` (solo `ok`), `claves_rutas_quitadas` (404) y `claves_publico_sin_sala` |
| U2-S7 | `guion.claves_de(valor)` (la de U1) recorre todas las respuestas; `guion.es_opaco(id)` aplica la forma `^o[a-z2-7]{11}([a-z2-7]{5})?$`; `guion.ordenes_distintos(misiones_de_todos)` compara el orden de textos por pregunta; `guion.csv_sin_opacos(texto_csv)` revisa la columna `respuesta` |
| U2-S8 | `verificar.sh` exporta `PRUEBA_CLAVE` leída de `.dev.vars` y llama a la prueba sin `--clave`; el LEEME enseña `read -rs PRUEBA_CLAVE && export PRUEBA_CLAVE` para la URL de Workers y `RETO_CLAVE` (variable que ya lee `servidor.py`) para la versión local |
