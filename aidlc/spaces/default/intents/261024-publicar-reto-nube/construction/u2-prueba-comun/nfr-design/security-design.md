# Seguridad — diseño U2

Diseño no funcional de U2. Los requisitos están en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U2-S1 | `Cliente` recibe la clave en su constructor y la pone solo en `X-Clave-Admin`; la única petición con `?clave=` es la comprobación `claves_403`, con una clave falsa, y se arma en `prueba.py` con un comentario de docstring que lo dice; `argparse` no imprime los valores por defecto de `--clave` |
| U2-S2 | `SalaDePrueba.clave_sala` y `ParticipanteFicticio.token` son campos de dataclasses con `repr=False`, así un `print` accidental no los muestra; no existen en `Medicion` |
| U2-S3 | `guion.clave_por_texto(revisiones, misiones)` devuelve un `dict` que vive en `Corrida` y muere con el proceso; ningún módulo abre archivos del repositorio: `prueba.py` solo escribe el JSON y lee `--referencia`; una prueba `unittest` revisa que `src/` no contenga `banco_preguntas` ni `open(` fuera de `mediciones.py` |
| U2-S4 | `mediciones.armar(corrida)` construye el JSON solo con ids, partes, booleanos y cifras; `validar_medicion` rechaza cualquier `detalle` que contenga una clave de la lista secreta (`respuesta`, `explicacion`, `tolerancia`, `verdad`, `multitud_acierta`, `veredicto`) o el texto de la clave de la corrida |
| U2-S5 | Nombres «Detective <k> <sufijo>», «Calibrador <n> <sufijo>» y «Colegio de prueba <sufijo>», con sufijo de fecha y microsegundos; el LEEME repite la advertencia de no correr contra `datos/reto.db` y da el comando con `--db` aparte |
| U2-S6 | `claves_403` en `prueba.py`: sin cabecera, clave inventada, clave de la sala A sobre la sala B (nube) y `?clave=`; cada una exige 403 y que el cuerpo no traiga `participantes` ni `ranking` |
| U2-S7 | `guion.claves_de(valor)` (la de U1) recorre todas las respuestas; `guion.es_opaco(id)` aplica la forma `^o[a-z2-7]{11}([a-z2-7]{5})?$`; `guion.ordenes_distintos(misiones_de_todos)` compara el orden de textos por pregunta; `csv_sin_opacos(texto_csv)` revisa la columna `respuesta` |
