# Observación — U3

Requisitos no funcionales de U3. La versión local imprime en consola lo que el docente necesita
(`servidor.py`, `main`) y los errores en `stderr`; U3 no agrega registro. Decisiones tomadas por el
asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U3-O1 | La consola del docente no cambia: mismas líneas de arranque (título, banco, URL, sala, clave) | NFR7, FR5.4 |
| U3-O2 | Un error dentro de las funciones nuevas llega al `except Exception` del manejador, que responde 500 e imprime `[error]` con la excepción, como hoy; nunca imprime la semilla ni la respuesta | `python-code.md` («Errores»: el único `try` amplio vive en el punto de entrada), U3-S6 |
| U3-O3 | La forma de verificar que la corrección está activa es externa: `fuga_ids_opacos` y `fuga_verdad_cerrado` de la prueba común en modo local pasan | FR6.3 |
