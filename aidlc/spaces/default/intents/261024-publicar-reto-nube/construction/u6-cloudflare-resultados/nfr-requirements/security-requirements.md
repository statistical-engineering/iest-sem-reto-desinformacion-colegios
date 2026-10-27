# Seguridad — U6

> **Revisión 2026-10-27 (una sola sala).** Un solo reto, una sola clave docente (`CLAVE_DOCENTE`, solo
> por `X-Clave-Admin`, nunca `?clave=`) y reloj por colegio (ADR-009 a ADR-011). Se quitan `?sala=`,
> `id_sala`, la clave del semillero y «Borrar la sala»; las copias se borran una a una (D7). U6-S6
> pasa de «filas de una sala» a «la clave nunca sale en un archivo».

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Decisiones tomadas por el asistente con la potestad que dio el humano. Los de U1, U4 y U5 siguen vigentes.

| Id | Requisito | Origen |
|---|---|---|
| U6-S1 | `revision`, `puesto`, `puesto_grado` y `nota` salen por `/api/estado` solo con el reto en `resultados` y el participante `finalizado`; la prueba común lo revisa en `abierto` y en `cerrado` | NFR8, FR6.2, BR1.1 |
| U6-S2 | `/api/publico` no trae `verdad`, `multitud_acierta`, `clase`, `por_publicacion` ni `multitud` fuera de `resultados`; en `cerrado` solo `n` y `listo`; `ranking` y `por_grado` salen y se ocultan juntos con el modo sorpresa | FR6.1, ADR-W9, BR2.1, BR2.2 |
| U6-S3 | Toda descarga y toda ruta de copias (los dos CSV, `paquete.zip`, `copias`, `copia`, `copia/borrar`, `reiniciar`) exige la clave docente en `X-Clave-Admin`; sin clave, con una incorrecta o con `?clave=` en la URL (aunque la cabecera sea correcta), 403 «Clave de docente incorrecta.» sin datos | FR9.5, NFR9, ADR-010, BR3.3 |
| U6-S4 | Ningún archivo del paquete ni ninguna copia contiene `token`, `semilla`, `codigo` personal ni `clave_huella`: las consultas nombran columnas y una prueba busca esas palabras en los encabezados y en los `CREATE TABLE` | FR9.5, R-11, C-06, BR4.4 |
| U6-S5 | Los CSV de hoy conservan `codigo` personal porque hoy lo traen (`csv_resultados` de `servidor.py`, FR4.3) y solo los descarga la clave docente; el paquete no lo trae | FR4.3, FR9.5 |
| U6-S6 | Ni la clave docente ni su valor de prueba aparecen en ningún archivo exportado ni en el registro; una prueba busca la clave de prueba en todo el `.zip` | NFR9, BR4.4 |
| U6-S7 | Borrar una copia no deja filas en `copias` ni `copia_trozos` de ese id; después, `GET /api/admin/copia?id=` da 404 «No existe esa copia.» | NFR10.1, FR8.2, BR6.2 |
| U6-S8 | Los nombres de archivo que arma el servidor (`copia_<código>_<fecha>.sql`, `AAAA-MM-DD_<código>_reto.zip`) solo contienen `[A-Z0-9_.-]`: el código de sala ya está acotado a 3 a 8 letras o números por `/api/admin/config` | `phases/construction.md` («Security», salidas acotadas) |
| U6-S9 | Los registros no incluyen nombres de participantes ni contenido de copias; solo los mensajes de U6-O1 | NFR10, U1-S6 |
