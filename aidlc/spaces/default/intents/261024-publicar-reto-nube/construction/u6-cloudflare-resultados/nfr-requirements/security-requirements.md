# Seguridad — U6

Requisitos no funcionales de U6, resultados y exportación en Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y de los contratos C1 y C5. Decisiones tomadas por el asistente con la potestad que dio el humano. Los de U1, U4 y U5 siguen vigentes.

| Id | Requisito | Origen |
|---|---|---|
| U6-S1 | `revision`, `puesto` y `nota` salen por `/api/estado` solo con la sala en `resultados` y el participante `finalizado`; la prueba común lo revisa en `abierto` y en `cerrado` | NFR8, FR6.2, BR1.1 |
| U6-S2 | `/api/publico` no trae `verdad`, `multitud_acierta`, `clase`, `por_publicacion` ni `multitud` fuera de `resultados`; en `cerrado` solo `n` y `listo` | FR6.1, ADR-W9 |
| U6-S3 | Toda descarga (CSV, paquete, copias) exige clave de esa sala o del semillero con `?sala=`; sin clave o con clave de otra sala, 403 sin cuerpo de datos | FR9.5, FR11.6, NFR9 |
| U6-S4 | Ningún archivo exportado (CSV de hoy, paquete, copia) contiene `token`, `semilla`, `codigo` personal ni `clave_huella`: las consultas nombran columnas y una prueba busca esas palabras en los encabezados y en los `CREATE TABLE` | FR9.5, R-11, C-06 |
| U6-S5 | Los CSV de hoy conservan `codigo` personal porque hoy lo traen (FR4.3) y solo los descarga la clave de la sala; el paquete no lo trae | FR4.3, FR9.5 |
| U6-S6 | La copia y el paquete llevan solo filas de la sala pedida: cada consulta lleva `id_sala`; la prueba común crea dos salas y comprueba que el paquete de una no trae nombres de la otra | FR11.6, R-05 |
| U6-S7 | Borrar la sala no deja filas en `copias` ni `copia_trozos`; después, `/api/admin/copias?sala=` da 404 | NFR10.1, FR8.2 |
| U6-S8 | Los nombres de archivo que arma el servidor (`copia_<sala>_<fecha>.sql`, `AAAA-MM-DD_<sala>_reto.zip`) solo contienen `[A-Z0-9_.-]`: el código de sala ya está acotado por `normalizar_codigo` | `phases/construction.md` («Security», salidas acotadas) |
| U6-S9 | Los registros no incluyen nombres de archivo con datos ni contenido de copias; solo «Sala <código> reiniciada» y «copia dañada <id_copia>» | NFR10, U1-S6 |
