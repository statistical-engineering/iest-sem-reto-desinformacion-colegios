# Preguntas de Functional Design — U1 `u1-cloudflare-corte`

U1 es el corte delgado de Workers: con la clave del semillero se crea y se abre una sala, un estudiante
se inscribe, comienza y responde una pregunta (`unit-of-work.md`, «U1, U7, U11»). Aquí se fija qué hace
cada paso, sin hablar todavía de Workers ni de D1: eso va en el ADR de la opción.

## Q1. [Producto] ¿Qué banco usa el corte?

A. El banco completo, como copia sin cambios de `2_Aplicacion_Reto/banco_preguntas.json`, hecha por un
   paso de copia y comprobada con su versión (huella). El corte valida que sume 1.000 puntos y muestra
   todas las misiones; nunca lo sirve como archivo (NFR8).
B. Un banco de prueba corto, propio del corte; el completo entra en U4.
X. Other (please specify)

[Answer]: A

## Q2. [Producto] ¿Qué tipos de pregunta califica el corte?

A. Solo `opcion`, con la misma fracción que hoy. Responder otro tipo da 400 «tipo aún no disponible» y
   U4 trae los otros 9 tipos.
B. Los 10 tipos desde el corte.
X. Other (please specify)

[Answer]: A

## Q3. [Producto] ¿Cómo elige el estudiante su colegio en el corte?

FR10.3 pide una lista cerrada de colegios. El catálogo completo del semillero entra en U5.

A. En el corte, el docente agrega colegios «provisionales» a su sala (`/api/admin/colegios`, acción
   `provisional`) y el estudiante elige de esa lista (`/api/colegios?sala=`). U5 agrega el catálogo
   único.
B. En el corte el colegio sigue como texto libre, como hoy; la lista entra en U5.
X. Other (please specify)

[Answer]: A

## Q4. [Producto] ¿Qué parte del reloj entra en el corte?

A. La hora de entrega completa (la menor entre ahora, inicio + duración y cierre de la sala): comenzar
   guarda la hora del servidor y responder después de vencido da 400, como hoy (FR3.1). Cerrar la sala
   queda para U5.
B. Solo «comenzar» con la hora del servidor; el vencimiento entra en U4.
X. Other (please specify)

[Answer]: A

## Q5. [Calidad] ¿Qué revisa la prueba común mínima?

A. En este orden: salud (`/api/publico` responde `{"ok": true}`), crear y abrir una sala con la clave del
   semillero, 403 con una clave mala, inscribirse, comenzar, ver `/api/estado` sin respuestas ni
   veredicto, responder una pregunta, 400 al responderla otra vez y ver la respuesta guardada. Contra la
   versión local, lo mismo con la clave docente y sin crear sala.
B. Solo salud, inscribirse y responder.
X. Other (please specify)

[Answer]: A
