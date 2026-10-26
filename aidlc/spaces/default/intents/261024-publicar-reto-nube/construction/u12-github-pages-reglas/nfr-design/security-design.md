# Seguridad — diseño U12

Diseño no funcional de U12. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U12-S1 | `version_publica` copia solo una tupla cerrada de claves (la lista blanca de hoy); `calcular` recibe `estado_sala` y arma `por_publicacion` sin `verdad` ni `multitud_acierta` salvo en `resultados`; `test_reglas.py` recorre el JSON devuelto con una función `claves_de` y falla si aparece una clave de `SECRETAS` |
| U12-S2 | `opaco_de` usa `hmac.new(semilla.encode(), f"{pregunta_id}|{id}".encode(), "sha256")` y `base64.b32encode(...).lower()`; la semilla no aparece en ninguna salida |
| U12-S3 | `casos_reglas.json` trae un `banco_prueba` con tres misiones inventadas; `copiar.sh` se niega a copiarlo si contiene algún `id` de pregunta del banco real (comparación contra `src/banco.json`) |
| U12-S4 | `normalizar_texto` filtra con `unicodedata.category(c) in {"Cc", "Cf"}` y los `Zs` distintos de `" "` antes de juntar espacios |
| U12-S5 | `reglas.py` no importa `logging` ni `print` |
