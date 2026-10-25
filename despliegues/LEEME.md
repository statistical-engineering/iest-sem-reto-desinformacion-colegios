# Despliegues por opción de hosting

Aquí vive una versión del reto por cada opción de hosting que estamos comparando. Cada opción se
construye, se despliega y se mide **por separado**; al final gana la más simple que pase la misma prueba
(requisito FR12 de la intención `261024-publicar-reto-nube`, en
`aidlc/spaces/default/intents/261024-publicar-reto-nube/inception/requirements-analysis/requirements.md`).

La versión de hoy, `2_Aplicacion_Reto/`, **no se toca**: sigue sirviendo en red local y con el túnel, y
es la línea base y el respaldo.

## Estructura

```text
despliegues/
├── LEEME.md              este archivo: reglas comunes
├── COMPARACION.md        tabla final con lo que midió la prueba común
├── prueba_comun/         la misma prueba para todas las opciones, contra su URL
├── render/               Render con Docker y disco persistente
├── cloudflare/           Cloudflare Workers con D1 y un Durable Object por sala
├── cloudflare-containers/ Cloudflare Containers con el Dockerfile actual
├── apps-script/          Google Apps Script con Google Sheets
└── github-pages/         pantallas en GitHub Pages y la API en otro servicio
```

Cada carpeta de opción usa los mismos nombres, para que se puedan comparar lado a lado:

| Carpeta | Qué va dentro |
|---|---|
| `LEEME.md` | Qué es la opción, su estado, cómo se despliega y qué falta decidir |
| `src/` | El código del servidor (la API) |
| `web/` | Las pantallas del estudiante, el panel y el tablero, copiadas de `2_Aplicacion_Reto/web/` |
| `pruebas/` | Las pruebas unitarias de las reglas del reto de esa opción |

Si la plataforma obliga a otra ubicación (por ejemplo, Apps Script guarda el HTML junto al código), el
`LEEME.md` de esa opción lo dice.

## Reglas para trabajar aquí

- **Todavía no hay código de producción.** Cada carpeta espera el ADR de su opción: lenguaje,
  dependencias y archivos de configuración se aprueban ahí (pedido inicial: «no escribas código de
  producción hasta que yo apruebe el ADR»).
- **Una rama por cambio**, creada desde `develop`, con nombre `feat/despliegue-<opción>-<qué>` (por
  ejemplo `feat/despliegue-render-corte-delgado`), y PR a `develop` de máximo 400 líneas de código.
- **Una carpeta no depende de otra** ni de `2_Aplicacion_Reto/`. Lo que se reutiliza (las pantallas)
  se copia, sin cambiar lo que ve el estudiante.
- **Ningún PR cambia `2_Aplicacion_Reto/`.** Se comprueba con `git diff --stat develop -- 2_Aplicacion_Reto/`
  en la rama del PR, que debe salir vacío.
- **Nunca se versionan** claves docentes, tokens, archivos `.env`, bases de datos ni datos de
  participantes. Las claves se configuran como secretos en cada hosting.
- **Ninguna respuesta correcta llega al navegador** antes de que el docente publique resultados
  (`CLAUDE.md`, «Invariantes que no se rompen»).
- **Primero el corte delgado.** Cada opción sube primero una versión mínima que deja inscribirse y
  responder una pregunta, y la verifica con la prueba común. Solo después se construye el resto.
- **Si hay que agregar un paquete** (en Python, JavaScript o cualquier lenguaje), se pide aprobación antes.
- **Nada que cueste se despliega** sin aprobar antes el monto y un tope. Una opción sin plan gratuito
  entra en la comparación solo con datos de su documentación oficial.
