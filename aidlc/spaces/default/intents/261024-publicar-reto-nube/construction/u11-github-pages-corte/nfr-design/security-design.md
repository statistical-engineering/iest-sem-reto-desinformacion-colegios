# Seguridad — diseño U11

Diseño no funcional de U11. Las decisiones están en `../decisions.md` (ADR-G1 a ADR-G7); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U11-S1 | Lista blanca de claves al armar cada pregunta pública en `reglas.examen_publico`; `revision` solo en resultados (U14) |
| U11-S2 | `reglas.opaco_de` con `hmac.new(semilla, mensaje, "sha256")` y `base64.b32encode` en minúsculas (ADR-G6) |
| U11-S3 | `banco.json` en `src/`; `publicar-pages.yml` sube solo `despliegues/github-pages/web/`; la prueba común pide el banco por URL en los dos orígenes y exige 404 |
| U11-S4 | `wsgi.py` lee `CLAVE_SEMILLERO` del entorno; la plantilla del archivo WSGI de PythonAnywhere la carga desde `~/.reto_secretos/clave_semillero.txt`; con menos de 12 caracteres o con guion, las rutas de admin responden 500 y el registro dice «Clave del semillero inválida» sin mostrarla |
| U11-S5 | Huella `hashlib.sha256(secreto).hexdigest()`, `hmac.compare_digest` contra la huella guardada; `?clave=` se ignora y la ruta responde 403 si no hay cabecera |
| U11-S6 | `RETO_ORIGENES` separado por comas; el origen de la petición se compara exacto (`==`) contra esa lista; si coincide se devuelve ese mismo valor en `Access-Control-Allow-Origin` con `Vary: Origin`; si no, ninguna cabecera CORS (BR8.1) |
| U11-S7 | `logging` solo con eventos fijos: «Arranque: banco <huella>, <n> preguntas», «Sala <código>: <estado>», «503 <ruta>», «500 <ruta>» más la traza; nunca cuerpos, cabeceras ni `Origin` |
| U11-S8 | Se lee `CONTENT_LENGTH`; si falta o pasa de 65.536 se responde 413 sin leer; se lee `wsgi.input` con ese tope; `json.loads` en `try` → 400 |
| U11-S9, U11-S10 | Un único punto de salida (`responder(estado, cuerpo, cabeceras_extra)`) arma `Content-Type`, `Cache-Control: no-store`, `X-Content-Type-Options: nosniff` y las cabeceras CORS; el 500 pasa por el mismo punto |
| U11-S11 | `RETO_DATOS` apunta a `~/reto_datos/` y los secretos a `~/.reto_secretos/`, fuera del clon en `~/Reto_Desinformacion_Colegios/`; `.gitignore` de la opción ignora `datos/` y `*.db` para las pruebas locales |
