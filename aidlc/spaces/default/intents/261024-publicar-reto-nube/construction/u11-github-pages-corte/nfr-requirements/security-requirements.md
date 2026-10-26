# Seguridad — U11

Requisitos no funcionales de U11, el corte delgado de GitHub Pages con la API en PythonAnywhere. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato (`contract-summary.md`). Las cuotas se citan de la documentación oficial consultada el 2026-10-25 (URL en `../decisions.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U11-S1 | Ninguna respuesta correcta, explicación, tolerancia ni veredicto sale al navegador antes de «resultados» | NFR8, BR6.2 |
| U11-S2 | Ids de opciones opacos con HMAC-SHA256 de la semilla del participante (`hmac` de la biblioteca estándar) | FR6.2, BR6.1, ADR-G6 |
| U11-S3 | El banco vive solo en `src/` de la API; el flujo de Pages sube únicamente `despliegues/github-pages/web/`, así que el banco nunca llega a GitHub Pages ni se sirve por URL en ninguno de los dos dominios | NFR8, BR6.3, ADR-G7 |
| U11-S4 | La clave del semillero es un secreto fuera del repositorio (`~/.reto_secretos/clave_semillero.txt` con permisos 600, leído por el archivo WSGI de PythonAnywhere), de 12 caracteres o más y sin guion; sin ella las rutas de administración responden 500 | NFR9, ADR-G6, Delivery Planning Q8-A |
| U11-S5 | Claves solo por `X-Clave-Admin`, comparadas con `hmac.compare_digest` y en mayúsculas; se guarda solo la huella SHA-256 del secreto de sala; `?clave=` no se acepta | NFR9, BR1.2, ADR-003 |
| U11-S6 | CORS con origen exacto: la API solo devuelve `Access-Control-Allow-Origin` al origen del sitio de Pages (y al de `localhost` al probar), nunca `*`, y nunca con credenciales de cookie | NFR9, BR8.1, ADR-G4 |
| U11-S7 | Ningún registro lleva claves, tokens, nombres, colegios, respuestas ni el `Origin` de la petición | NFR9, NFR10, `.claude/rules/python-code.md` («Logs») |
| U11-S8 | El cuerpo de un POST se rechaza con 413 si pasa de 65.536 bytes y con 400 si no es JSON; el tope se aplica antes de leer todo el cuerpo (`CONTENT_LENGTH` y lectura acotada) | FR4.1 (`api-documentation.md`) |
| U11-S9 | Toda respuesta de la API lleva `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`; las pantallas de Pages llevan las cabeceras que fija GitHub y no se pueden cambiar | FR4.1, ADR-G2 |
| U11-S10 | Un error inesperado responde 500 sin detalles | FR4.1 |
| U11-S11 | La base de datos y la carpeta de secretos están fuera del clon del repositorio en PythonAnywhere, así `git pull` nunca los toca ni los sube | NFR10, `project.md` («Forbidden») |
