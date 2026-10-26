# Preguntas de Delivery Planning

Aquí se elige el orden en que se construyen las 17 unidades. Cada unidad se construye en un **Bolt**:
una pasada de construcción sobre un pedazo del trabajo, que termina en algo que funciona.

Ya está fijado:

- U1, el corte de Cloudflare Workers, va primero. Es el **corte delgado**: la versión mínima de punta a
  punta que demuestra que todo encaja (`unit-of-work-dependency.md`, «Corte delgado»).
- Construcción va etapa por etapa y en paralelo (elección del humano, 2026-10-25).
- El humano y el asistente suben directo a `develop` (`team.md`, «Corrections»).

## Q1. [Entrega] ¿Qué se construye después del corte de Workers?

A. Primero lo más riesgoso: los cortes de Apps Script (U7) y de GitHub Pages (U11) y la prueba común
   (U2), en paralelo. Si una opción no pasa su corte, se sabe pronto y no se gasta trabajo en sus otras
   unidades. Después, las cadenas de cada opción.
B. Primero lo más valioso: terminar entera la opción Workers (U4 a U6) y después las otras.
X. Other (please specify)

[Answer]: A

## Q2. [Entrega] ¿Qué hacemos con Apps Script (hallazgo C-01 de la revisión de contratos)?

La documentación oficial de Apps Script muestra que no lee cabeceras ni fija los códigos 401, 403 o
404, y no contesta la consulta previa de CORS (`contract-design/reviews/review-01.md`, C-01).

A. Queda como «no pasa» por contrato, con esa evidencia en la tabla de comparación (FR12.6). Se saltan
   U7 a U10 con tu aprobación. Es lo más simple, como pide la regla de parsimonia (`project.md`).
B. U7 se construye como prueba corta: si se confirma el problema, se cierra «no pasa» y se saltan U8 a
   U10.
C. Un perfil de contrato propio para Apps Script (clave y token en el cuerpo, error dentro del JSON),
   con cambios en `web/js/` y en la prueba común solo para esa opción.
X. Other (please specify)

[Answer]: A

## Q3. [Entrega] ¿De qué tamaño es cada Bolt?

A. Un Bolt por unidad. Cada unidad ya cabe en uno o dos PR (Units Generation, Q1-A).
B. Varias unidades por Bolt, por ejemplo toda la cadena de una opción.
X. Other (please specify)

[Answer]: A

## Q4. [Arquitectura] ¿Dónde se arreglan los hallazgos de la revisión de contratos?

Lo que la revisión pidió completar (C-02 a C-15) es trabajo de construcción.

A. Cada hallazgo va a la Definición de Hecho de la primera unidad que lo necesita:
   - U1: ids opacos en las respuestas propias y la revisión (C-02), mayúsculas en claves (C-03),
     copia sin columnas secretas (C-06) y la forma de los datos de las reglas (C-05);
   - U11: CORS y URL base de la API (C-04);
   - U2: el resto.
   Con la forma de las reglas fijada en U1, U4, U8 y U12 pueden ir en paralelo.
B. Antes de Construcción: se vuelve a abrir Contract Design y se corrige el contrato.
X. Other (please specify)

[Answer]: A

## Q5. [Riesgo] ¿Y si el corte de Workers (U1) no pasa?

A. La prueba común mínima se termina igual y se verifica contra la versión local. U1 se cierra como
   «no pasa», con el motivo, y las otras opciones siguen desde ahí.
B. Se detiene todo hasta decidir con vos.
X. Other (please specify)

[Answer]: A

## Q6. [Calidad] ¿En qué lenguaje se escribe la prueba común?

A. Python con solo la biblioteca estándar, como `simulacro.py`. Se corre con
   `python3 despliegues/prueba_comun/prueba.py --url <URL>` y la clave por variable de entorno. No
   necesita paquetes nuevos.
B. JavaScript con Node.
X. Other (please specify)

[Answer]: A

## Q7. [Entrega] ¿Cuenta la copia de `web/` en el límite de 400 líneas por PR?

Cada opción necesita su copia de `web/` (1.734 líneas), porque las opciones no comparten código
(FR12.2).

A. La copia sin cambios no cuenta, como los archivos generados. Va en su propio commit y solo cuentan
   los cambios que se le hagan después.
B. Cuenta: se parte en varios PR.
X. Other (please specify)

[Answer]: A

## Q8. [Entrega] ¿Quién crea las cuentas y los secretos de cada hosting?

Cada corte necesita una cuenta gratuita (Cloudflare, GitHub Pages y, si sigue, Google) y la clave del
semillero como secreto del hosting.

A. Vos o alguien del semillero crea cada cuenta y carga la clave antes de su corte. El asistente
   escribe los pasos en el `LEEME.md` de la opción y nunca ve la clave.
B. El asistente despliega con una cuenta que le prestan.
X. Other (please specify)

[Answer]: A
