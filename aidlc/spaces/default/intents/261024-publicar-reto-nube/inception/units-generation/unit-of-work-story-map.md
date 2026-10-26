# Mapa de requisitos por unidad

No hay historias de usuario (la etapa User Stories se saltó por pedido del humano), así que cada fila es
un requisito `FR` de `../requirements-analysis/requirements.md`. Cuando una fila nombra tres unidades, es
porque cada opción gratuita cumple ese requisito en su propia carpeta: Cloudflare Workers, Apps Script y
GitHub Pages.

## Requisito → unidad

| Requisito | Unit ID | Directorio | Qué parte cubre |
|---|---|---|---|
| FR1.1 | U5; U9; U13 | u5-cloudflare-salas; u9-apps-script-salas; u13-github-pages-salas | estados de la sala y reiniciar |
| FR1.2 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | estados del participante |
| FR1.3 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | inscripción y grupo A/B |
| FR2.1 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | crédito parcial |
| FR2.2 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | bono de tiempo |
| FR2.3 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | desempates |
| FR2.4 | U1; U5; U7; U9; U11; U13 | u1-cloudflare-corte; u5-cloudflare-salas; u7-apps-script-corte; u9-apps-script-salas; u11-github-pages-corte; u13-github-pages-salas | una respuesta por pregunta; requiere y sin cruzarse en salas |
| FR3.1 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | comenzar con la hora del servidor |
| FR3.2 | U4; U5; U8; U9; U12; U13 | u4-cloudflare-reglas; u5-cloudflare-salas; u8-apps-script-reglas; u9-apps-script-salas; u12-github-pages-reglas; u13-github-pages-salas | vencimiento al consultar y entrega con un dueño |
| FR3.3 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | hora de entrega |
| FR4.1 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | rutas y claves JSON de web/js/ |
| FR4.2 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | páginas sin cambios visibles |
| FR4.3 | U6; U10; U14 | u6-cloudflare-resultados; u10-apps-script-resultados; u14-github-pages-resultados | CSV y copia de «Reiniciar» |
| FR5.1 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | enlace fijo por opción |
| FR5.2 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | despliegue manual en el LEEME |
| FR5.3 | — | — | flujo de ramas del equipo, no es trabajo de una unidad; el humano y el asistente tienen la excepción del push directo a `develop` (`team.md`, «Corrections») |
| FR5.4 | U3 | u3-local-fugas | modos locales siguen igual |
| FR5.5 | U2 | u2-prueba-comun | paridad medida con la prueba común |
| FR6.1 | U3; U6; U10; U14 | u3-local-fugas; u6-cloudflare-resultados; u10-apps-script-resultados; u14-github-pages-resultados | sin fugas en /api/publico |
| FR6.2 | U3; U1; U4; U7; U8; U11; U12 | u3-local-fugas; u1-cloudflare-corte; u4-cloudflare-reglas; u7-apps-script-corte; u8-apps-script-reglas; u11-github-pages-corte; u12-github-pages-reglas | ids opacos: el corte ya sale con ellos y las reglas lo completan |
| FR6.3 | U2 | u2-prueba-comun | comprobaciones de fugas |
| FR7.1 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | reglas probadas sin servidor ni base |
| FR7.2 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | nivel de acceso por ruta |
| FR7.3 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | capa de base según el ADR de la opción |
| FR7.4 | U4; U5; U8; U9; U12; U13 | u4-cloudflare-reglas; u5-cloudflare-salas; u8-apps-script-reglas; u9-apps-script-salas; u12-github-pages-reglas; u13-github-pages-salas | transiciones permitidas |
| FR7.5 | — | — | lista priorizada de refactors: Delivery Planning |
| FR7.6 | — | — | convención de idioma y dependencias de todas las unidades |
| FR8.0 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | LEEME de cada carpeta |
| FR8.1 | U17 | u17-comparacion | PUBLICAR_EN_INTERNET.md de la ganadora |
| FR8.2 | U17 | u17-comparacion | guía de cierre |
| FR8.3 | U17 | u17-comparacion | corrección de la guía |
| FR9.1 | U6; U10; U14 | u6-cloudflare-resultados; u10-apps-script-resultados; u14-github-pages-resultados | paquete .zip |
| FR9.2 | U6; U10; U14 | u6-cloudflare-resultados; u10-apps-script-resultados; u14-github-pages-resultados | formato de los CSV |
| FR9.3 | U6; U10; U14 | u6-cloudflare-resultados; u10-apps-script-resultados; u14-github-pages-resultados | diccionario de datos |
| FR9.4 | — | — | organización del Drive del semillero, fuera del código |
| FR9.5 | U5; U6; U9; U10; U13; U14 | u5-cloudflare-salas; u6-cloudflare-resultados; u9-apps-script-salas; u10-apps-script-resultados; u13-github-pages-salas; u14-github-pages-resultados | sin claves ni tokens |
| FR10.1 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | normalizar texto |
| FR10.2 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | validar campos |
| FR10.3 | U5; U9; U13 | u5-cloudflare-salas; u9-apps-script-salas; u13-github-pages-salas | catálogo y colegio provisional |
| FR10.4 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | integrantes |
| FR10.5 | U4; U8; U12 | u4-cloudflare-reglas; u8-apps-script-reglas; u12-github-pages-reglas | pruebas de las reglas |
| FR11.1 | U5; U9; U13 | u5-cloudflare-salas; u9-apps-script-salas; u13-github-pages-salas | varias salas |
| FR11.2 | U5; U9; U13 | u5-cloudflare-salas; u9-apps-script-salas; u13-github-pages-salas | datos por sala |
| FR11.3 | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | pantalla del estudiante igual |
| FR11.4 | U6; U10; U14 | u6-cloudflare-resultados; u10-apps-script-resultados; u14-github-pages-resultados | tablero por sala |
| FR11.5 | U5; U9; U13 | u5-cloudflare-salas; u9-apps-script-salas; u13-github-pages-salas | claves de sala y semillero |
| FR11.6 | U5; U6; U9; U10; U13; U14 | u5-cloudflare-salas; u6-cloudflare-resultados; u9-apps-script-salas; u10-apps-script-resultados; u13-github-pages-salas; u14-github-pages-resultados | reiniciar y borrar una sala |
| FR11.7 | U2 | u2-prueba-comun | prueba con varias salas |
| FR12.1 | — | — | regla: ninguna unidad salvo U3 cambia 2_Aplicacion_Reto/ |
| FR12.2 | U1; U7; U11; U15; U16 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte; u15-render-documentacion; u16-cloudflare-containers-documentacion | una carpeta por opción |
| FR12.2a | U15; U16 | u15-render-documentacion; u16-cloudflare-containers-documentacion | opciones de pago solo con documentación |
| FR12.2b | U1; U7; U11 | u1-cloudflare-corte; u7-apps-script-corte; u11-github-pages-corte | ADR de la opción antes del código |
| FR12.3 | U1; U2 | u1-cloudflare-corte; u2-prueba-comun | U1 crea la prueba común mínima y U2 la completa |
| FR12.4 | U17 | u17-comparacion | tabla de comparación |
| FR12.5 | U17 | u17-comparacion | «pasa todo» |
| FR12.6 | U17 | u17-comparacion | cómo se elige |

## Requisitos que cruzan varias unidades

| Requisito | Unidades | Cómo se reparte |
|---|---|---|
| FR2.4 | corte; salas | El corte acepta una respuesta por pregunta. Salas agrega `requiere` y la regla de no cruzarse |
| FR3.2 | reglas; salas | Las reglas calculan la hora de entrega. Examen, en salas, la escribe con un solo dueño |
| FR6.1, FR6.2 | U3; corte, reglas y resultados de cada opción | U3 corrige la versión local. Cada opción nace sin la fuga: el corte ya trae los ids opacos |
| FR7.4 | reglas; salas | Las reglas tienen la tabla de transiciones. Salas la aplica |
| FR9.5 | salas; resultados | Salas guarda solo la huella de la clave. Exportacion no pone token, semilla, código ni huella en el paquete |
| FR11.6 | salas; resultados | Salas reinicia y borra. Exportacion arma la copia antes de reiniciar |
| FR12.2 | cortes; U15; U16 | Las gratuitas se construyen. Las de pago entran solo con documentación |

## Orden dentro de cada unidad

- **U1:** primero el ADR de Cloudflare Workers; después la prueba común mínima, `GET /api/publico`, crear
  y abrir una sala, inscribirse, comenzar y responder; al final el despliegue y el `LEEME.md`.
- **U2:** primero la parte base (las 29 comprobaciones), validada contra la versión local; después la
  parte nueva (fugas, salas, claves, paridad, latencia, reinicio, arranque en frío y consumo) y el archivo
  JSON de mediciones.
- **Cortes U7 y U11:** primero el ADR de la opción; después `GET /api/publico`, inscribirse,
  comenzar y responder; al final el despliegue y el `LEEME.md`.
- **Reglas (U4, U8, U12):** primero las pruebas por tabla de casos, compartidas en contenido con las
  demás opciones; después cada regla, hasta que todas pasen.
- **Salas (U5, U9, U13):** primero las salas y las claves; después el catálogo, la inscripción completa,
  el examen completo y la regla de no cruzarse.
- **Resultados (U6, U10, U14):** primero las vistas y el tablero; después los CSV, el paquete y las
  copias; al final la prueba común completa.
- **U17:** se llena la tabla, se aplican FR12.5 y FR12.6, y después se escriben el ADR final y la guía.

## Comprobación de cobertura

Se revisó con un script contra `../domain-design/traceability.json`, que tiene la lista de los 56 FR de
los requisitos:

- 56 FR en total, y cada uno tiene su fila;
- 51 FR tienen al menos una unidad;
- 5 no son trabajo de una unidad, por las razones que dice su fila: FR5.3, FR7.5, FR7.6, FR9.4 y FR12.1;
- cada una de las 17 unidades aparece en al menos una fila.
