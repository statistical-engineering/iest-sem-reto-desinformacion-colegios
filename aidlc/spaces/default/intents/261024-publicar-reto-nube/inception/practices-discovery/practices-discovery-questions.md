# Preguntas de Practices Discovery

Borrador en `team-practices.md` y evidencia en `evidence.md` (misma carpeta). Solo se pregunta lo que la
evidencia del repositorio no puede establecer.

## Q1. [Desarrollador] Rama base y forma de fusión de esta intención

Hoy tienes tres ramas locales apiladas sin subir (`fix/normalizar-eol-bat` → `chore/setup-aidlc` →
`refactor/code-cleanup`). Si los cambios de construcción salen de `main`, no verían la configuración de
AI-DLC ni la corrección del `.bat`. ¿Desde qué rama salen los cambios y cómo vuelven a `main`?

A. Salen de `refactor/code-cleanup` (la rama actual) y al final todo vuelve a `main` con un pull request
B. Primero fusiono las ramas locales a `main`; luego cada unidad sale de `main` y vuelve con squash (un commit por unidad)
C. Todo en `refactor/code-cleanup`, un commit por unidad, sin squash; el merge a `main` lo hago yo después
D. Directo sobre `main`
X. Other (please specify)

[Answer]: X. primero terminamos todo, y después hacemos un PR a main, pero la condicion es que debe de estar desplegado, regla importante es que no debemos de cambiar nada del diseñño o logica de negocio.

## Q2. [Desarrollador] Revisión y formato de los mensajes de commit

En la historia hay subidas directas por la web de GitHub y commits con formatos distintos. ¿Cómo llega
un cambio a `main` y en qué formato van los mensajes?

A. Pull request revisado por otra persona del semillero; mensajes `tipo: descripción` (tipo en inglés, descripción en español)
B. Pull request sin revisión obligatoria (lo fusiono yo); mensajes `tipo: descripción`
C. Push directo a `main`; mensajes libres
D. Pull request sin revisión obligatoria; mensajes `tipo: descripción` todo en inglés
X. Other (please specify)

[Answer]: A

## Q3. [Desarrollador] ¿Construir primero un corte delgado de extremo a extremo?

Un *walking skeleton* es una versión mínima que corre de punta a punta y se construye primero para
probar que las piezas conectan antes de meter las funciones reales. Aquí sería, por ejemplo, desplegar
en el hosting elegido una versión mínima (inscribirse y responder una pregunta) y validarla con el
simulacro antes de migrar todo. El plan clásico no lo hace por defecto.

A. Sí: primero un corte delgado desplegado y verificado con `simulacro.py 40` y el chequeo de salud
B. No: se construye por unidades en orden, sin corte previo
X. Other (please specify)

[Answer]: A

## Q4. [Ingeniero de calidad] Orden de las pruebas del núcleo puro nuevo

El refactor separa el núcleo puro (calificación, podio, reloj, validación del banco) de la E/S. Esas
funciones nuevas llevarán pruebas `unittest`. ¿Se escriben antes o después del código?

A. Después del código (test-after), y el simulacro tras cada cambio en el servidor
B. Antes del código (TDD) para el núcleo puro; el simulacro sigue como aceptación al final
C. Mixto: primero pruebas de caracterización (fijan la conducta actual), luego refactor, luego pruebas nuevas
X. Other (please specify)

[Answer]: A

## Q5. [Ingeniero de calidad] Cobertura, lint y dónde corren las pruebas

El plan clásico pide un 80 % de cobertura de líneas y que las pruebas corran en CI antes de fusionar, y
ese piso no se puede bajar. Hoy no hay herramienta de cobertura ni CI, y cualquier paquete nuevo
necesita tu aprobación.

A. Apruebo `coverage` (solo como herramienta de desarrollo, no en la app) y un workflow de GitHub Actions que corra `unittest` + `simulacro.py 40`; sin linter
B. Lo mismo que A más `ruff` como linter/formateador de desarrollo
C. Sin paquetes nuevos: cobertura con el módulo `trace` de la biblioteca estándar y GitHub Actions
D. Sin CI: las pruebas corren en local antes de fusionar (sé que eso no cumple el piso del plan clásico)
X. Other (please specify)

[Answer]: D

## Q6. [Ingeniero de despliegue] Cómo se dispara el despliegue del enlace fijo

Si el hosting desplegara solo al fusionar a `main`, una fusión durante un reto reiniciaría el servicio,
y eso choca con «no cambiar el código con un reto en curso». ¿Cómo se despliega?

A. A mano: el docente o el semillero pulsa «desplegar» cuando no hay reto en curso; volver atrás = redesplegar la versión anterior
B. Automático al fusionar a `main`, con la regla de no fusionar con un reto en curso
C. A mano, con un entorno de ensayo en la nube aparte para probar antes de cada reto
X. Other (please specify)

[Answer]: A

## Q7. [Ingeniero de calidad] Seguimiento: «sin CI» frente al piso del plan clásico

En Q5 elegiste «Sin CI», pero el plan clásico fija como piso un 80 % de cobertura de líneas **y** que
las pruebas corran en CI antes de fusionar, y ese piso no se puede bajar para que una etapa pase. Las dos
cosas no pueden quedar a la vez. ¿Cuál prefieres?

A. Mantener «sin CI» pero medir el 80 % en local con `trace` de la biblioteca estándar (sin paquetes); la etapa de pruebas registrará que falta CI como excepción tuya
B. Agregar un workflow de GitHub Actions con solo biblioteca estándar (`unittest` + `simulacro.py 40` + `trace`), sin paquetes nuevos
C. Aprobar `coverage` solo para desarrollo y GitHub Actions (como Q5-A)
D. Cambiar este trabajo a un plan sin ese piso (por ejemplo «refactor»), que solo exige que el simulacro siga en «TODO BIEN»
X. Other (please specify)

[Answer]: A

## Q8. [Desarrollador] Seguimiento: alcance de «no cambiar el diseño ni la lógica de negocio»

En Q1 fijaste una regla importante: no cambiar nada del diseño ni de la lógica de negocio. El análisis
del código encontró que `/api/publico` entrega el veredicto del experimento (`por_publicacion[].verdad`)
ya en el estado «cerrado», antes de que el docente publique resultados (`servidor.py:433-434`). ¿Qué
cubre la regla?

A. La regla cubre la conducta que ve el usuario (pantallas, preguntas, puntajes, desempates, flujo de estados); corregir fugas de respuestas antes de «resultados» sí se permite porque cumple un invariante ya existente
B. Nada cambia en absoluto, ni siquiera esa fuga: el refactor y la migración deben dar exactamente la misma salida que hoy
C. La regla cubre solo el diseño visual (HTML/CSS/JS) y las reglas de calificación; el servidor puede cambiar mientras el simulacro diga «TODO BIEN»
X. Other (please specify)

[Answer]: A
