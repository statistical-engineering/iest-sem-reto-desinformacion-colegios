# Reglas duras descubiertas

Solo restricciones que el humano declaró como obligatorias: en la entrevista (Q1, Q2, Q6, Q8 de
`practices-discovery-questions.md`) o por escrito en `CLAUDE.md`. Las que ya están en
`aidlc/spaces/default/memory/project.md` (respuestas fuera del navegador hasta publicar, banco de
1.000 puntos con `exigir(...)`, tiempo en el servidor con orden total, no cambiar banco ni código con
un reto en curso, no versionar claves ni `datos/`, simulacro en «TODO BIEN») no se repiten.

## Mandated

ALWAYS abrir el pull request a `main` solo cuando todo el trabajo esté terminado y el reto esté desplegado y verificado en el hosting elegido (fuente: entrevista Q1).
ALWAYS fusionar a `main` por pull request revisado por otra persona del semillero (fuente: entrevista Q2).
ALWAYS desplegar a mano y solo cuando no haya un reto en curso (fuente: entrevista Q6).
ALWAYS aceptar una sola respuesta por pregunta y participante (fuente: `CLAUDE.md`, «Invariantes que no se rompen»).
ALWAYS reiniciar el servidor después de regenerar el banco (fuente: `CLAUDE.md`, «Invariantes que no se rompen»).

## Forbidden

NEVER cambiar la conducta visible del reto (pantallas, preguntas, puntajes, desempates ni flujo de estados) al refactorizar o migrar; corregir fugas de respuestas antes de «resultados» sí se permite (fuente: entrevista Q1 y Q8).
NEVER editar `4_Codigo_y_datos/datos_originales/`, la única fuente de verdad de los datos (fuente: `CLAUDE.md`, «Fuente de verdad»).
NEVER poner respuestas del reto en material para estudiantes (fuente: `CLAUDE.md`, «Convenciones de idioma y código»; `.claude/rules/markdown-docs.md`, «Confidencialidad»).
NEVER versionar `2_Aplicacion_Reto/.herramientas/`, donde queda el binario de `cloudflared` (fuente: `CLAUDE.md`, «Gotchas»).
