# Preguntas de Requirements Analysis

Ya está fijado (tu pedido y Practices Discovery): un grupo de hasta 40 estudiantes durante 90 minutos;
el reto sobrevive a un reinicio o a que la instancia se duerma sin perder puntajes; gratis o casi
gratis y operable por un docente sin conocimientos técnicos; las respuestas correctas nunca llegan al
navegador antes de publicar resultados, hay clave docente, el tiempo lo mide el servidor y la
clasificación es un orden total sin empates; no cambia la conducta visible. Aquí solo va lo que falta.

## Q1. [Docente] ¿Habrá varios grupos al mismo tiempo?

Decide si el diseño necesita un reto por grupo en paralelo (varias salas con su propio reloj y podio) o
uno solo a la vez. Hoy el servidor maneja un único reto por instalación.

A. Nunca: un solo grupo de hasta 40 a la vez; grupos distintos van en horarios distintos
B. A veces 2 grupos a la vez (hasta 80 estudiantes), cada uno con su sala, reloj y podio separados
C. A veces 2 grupos a la vez, pero pueden compartir un mismo reto y un mismo podio
D. 3 o más grupos a la vez
X. Other (please specify)

[Answer]: X. por lo que entinedo esto lo estarán haciendo como 25 personas al mismo tiempo en diferentes computadores

## Q2. [Docente] ¿Cada cuánto se usará el reto?

Algunos planes gratuitos apagan la instancia tras un rato sin visitas o limitan horas al mes; la
frecuencia decide si eso importa y cuánto costaría mantener algo encendido.

A. Unas pocas veces al año (eventos puntuales)
B. Más o menos una vez al mes
C. Una o dos veces por semana durante un periodo escolar
D. Varias veces por semana
X. Other (please specify)

[Answer]: A

## Q3. [Desarrollador] Rapidez objetivo con 40 estudiantes conectados

Propuesta para medir con el simulacro y en el hosting: el 95 % de los envíos de respuesta (desde que el
estudiante pulsa «Enviar» hasta que ve «Respuesta guardada») tarda como máximo 1 segundo, y el 95 % de
los refrescos del tablero (`GET /api/publico`, que hoy se pide cada 2 segundos) responde en máximo 1,5
segundos.

A. Acepto la propuesta: respuesta ≤ 1 s y tablero ≤ 1,5 s (p95, con 40 estudiantes)
B. Más estricto: respuesta ≤ 500 ms y tablero ≤ 1 s
C. Más relajado: respuesta ≤ 2 s y tablero ≤ 3 s
X. Other (please specify)

[Answer]: A

## Q4. [Desarrollador] ¿Qué pasa con el reloj si el servicio se cae o se duerme a mitad del reto?

Hoy el reloj corre con la hora del servidor: si el servicio se reinicia, al volver el tiempo siguió
corriendo y lo vencido se entrega solo. Ninguna respuesta ya guardada se pierde.

A. Igual que hoy: ninguna respuesta aceptada se pierde y el reloj sigue corriendo durante la caída
B. Ninguna respuesta se pierde y el reloj se pausa mientras el servicio está caído (cambia la conducta actual)
C. Igual que hoy, y además la caída no puede durar más de 1 minuto
X. Other (please specify)

[Answer]: A

## Q5. [Docente] Tope de costo

«Gratis o casi gratis» tiene que quedar como una cifra para descartar opciones. Render con disco, la
opción ya configurada, cuesta unos US$ 7 al mes según `PUBLICAR_EN_INTERNET.md` (se verificará en la
documentación oficial).

A. US$ 0: solo planes gratuitos, aunque exijan más trabajo de migración
B. Hasta unos US$ 5 al mes, y solo los meses en que hay reto
C. Hasta unos US$ 10 al mes
D. Lo pagaría el colegio o el semillero; el tope lo pongo después
X. Other (please specify)

[Answer]: A

## Q6. [Docente] ¿Quién crea y mantiene el servicio en la nube?

Define cuánta parte técnica tiene que cubrir la guía para el docente en `PUBLICAR_EN_INTERNET.md`.

A. Alguien del semillero lo crea y despliega; el docente solo abre el enlace fijo y usa el panel con su clave
B. El docente lo crea y despliega solo, siguiendo una guía paso a paso con capturas
C. El semillero lo crea una vez; el docente puede redesplegar o reiniciar con un botón si algo falla
X. Other (please specify)

[Answer]: A

## Q7. [Desarrollador] Alcance de las correcciones de confidencialidad

El análisis encontró dos fugas antes de «resultados»: (1) `/api/publico` entrega el veredicto del
experimento ya en «cerrado» (`servidor.py:433-434`), y (2) los identificadores de las opciones siguen
el orden en que se escribió el banco, y ese orden se correlaciona con la clave; esos identificadores
llegan al navegador por `/api/estado`. Según tu regla, corregir fugas sí se permite.

A. Corregir las dos en esta intención, con una comprobación nueva en el simulacro para cada una
B. Corregir solo la (1) ahora; la (2) queda documentada para otra intención
C. Solo documentarlas; no se corrigen en esta intención
X. Other (please specify)

[Answer]: A

## Q8. [Docente] Datos de menores en un servicio en la nube

La app guarda nombre, colegio, grado y respuestas de menores. Publicarla en la nube significa que esos
datos quedan en servidores de un proveedor, probablemente fuera de Colombia.

A. Aceptable si el repositorio sigue privado, el acceso docente va con clave y los datos se borran al terminar el reto
B. Aceptable solo si los datos quedan en una región o país concreto (dime cuál)
C. Necesito confirmar con el colegio antes; por ahora asume A y lo dejo como pregunta abierta
X. Other (please specify)

[Answer]: A

## Q9. [Docente] Seguimiento de Q1: ¿un solo reto a la vez, con unas 25 personas?

En Q1 dijiste que serán unas 25 personas al mismo tiempo, cada una en su computador. Lo entiendo como un
solo grupo y un solo reto a la vez. En tu pedido inicial hablabas de hasta 40.

A. Sí: un solo reto a la vez; lo normal son unas 25 personas y el diseño se prueba con 40 como máximo
B. Un solo reto a la vez, pero el máximo real es 25 (se prueba con 25)
C. Son 25 personas, pero pueden ser grupos distintos en paralelo con retos separados
X. Other (please specify)

[Answer]: A
