# Seguridad — diseño U13

Diseño no funcional de U13. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U13-S1 | `Acceso.resolver(cabeceras, consulta)` devuelve `(rol, sala)`; cada función de servicio recibe `sala` como argumento y la pone en su `WHERE`; una función que reciba `sala=None` en una ruta de sala responde 400 «Falta la sala.» |
| U13-S2 | `Salas.regenerar_clave`: nuevo secreto con `secrets.choice` sobre el ALFABETO, `UPDATE salas SET clave_huella = ?` en `BEGIN IMMEDIATE`, respuesta con la clave y `logging` solo con el código de sala |
| U13-S3 | Las consultas de `salas` y `catalogo` nombran sus columnas; nunca `SELECT *` |
| U13-S4 | `Salas.borrar` revisa rol, estado y `confirmar == "BORRAR"` y ejecuta los `DELETE … WHERE sala = ?` en una transacción (U14 agrega `copias`) |
| U13-S5 | `normalizar_texto` antes de cada `INSERT`/`UPDATE`; `sqlite3` con parámetros `?` en todas las consultas (ruff `S608` vigila las f-strings) |
| U13-S6 | Las rutas nuevas pasan por el mismo punto de salida de U11, que agrega CORS |
| U13-S7 | `Acceso` pasa la clave a `upper().strip()`; si tiene guion, separa el código; si la sala no existe → 403 sin seguir; si no tiene guion → `compare_digest` con la clave del semillero |
