# Preguntas de Units Generation

Una unidad es un pedazo de trabajo que se construye y se prueba por su cuenta. Ya está fijado:

- una carpeta por opción bajo `despliegues/`, sin que ninguna dependa de otra ni de `2_Aplicacion_Reto/`
  (FR12.1, FR12.2);
- cada opción empieza con su corte delgado: inscribirse y responder una pregunta, verificado con la
  prueba común (`despliegues/LEEME.md`);
- cada PR tiene como máximo 400 líneas de código (`team.md`, «Corrections»);
- las opciones se pueden trabajar en paralelo, porque no dependen entre sí.

Aquí no se elige qué se construye primero: eso va en Delivery Planning.

## Q1. ¿Qué tan grande es cada unidad?

A. Por opción y por capa. Cada opción tiene 4 unidades: corte delgado, reglas («calculadoras» de
   ADR-001), salas y catálogo, y resultados y exportación. A eso se suma la prueba común. Cada unidad
   cabe en uno o dos PR, y varias personas pueden trabajar en la misma opción.
B. Una unidad por opción, más la prueba común: 6 unidades grandes, cada una de muchos PR.
X. Other (please specify)

[Answer]: A

## Q2. ¿Qué opciones se construyen ahora?

Render y Cloudflare Containers son de pago (FR12.2a). Sin un monto aprobado, no se despliegan.

A. Solo las gratuitas (Cloudflare Workers, Apps Script y GitHub Pages) se construyen. Render y
   Cloudflare Containers quedan como una unidad de solo documentación: sus cifras salen de la
   documentación oficial para la tabla de comparación.
B. Las cinco se construyen. Las de pago se prueban en local y se despliegan solo cuando apruebes el
   costo.
X. Other (please specify)

[Answer]: A

## Q3. ¿Se corrigen las fugas de respuestas en la versión local (OQ9)?

Hoy la versión local deja ver algunas respuestas antes de «resultados» (FR6). `2_Aplicacion_Reto/` está
congelada (FR12.1). La única excepción posible es esta.

A. Sí. Una unidad aparte corrige solo esas fugas en `2_Aplicacion_Reto/`, con `simulacro.py` en
   «TODO BIEN», porque el reto local se sigue usando en el aula.
B. No. La versión local queda igual, y las fugas se corrigen solo en las versiones de la nube.
X. Other (please specify)

[Answer]: A

## Nota del humano

«nosotros no necesitamos hacer PR, podemos hacer push directo a develop. listo ? los PR son para los
minions». El humano y el asistente suben directo a `develop`; el resto del equipo trabaja con ramas y
PR de máximo 400 líneas.
