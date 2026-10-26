# Escala — diseño U15

Diseño no funcional de U15 (solo documentación sobre Render). Los requisitos están en `../nfr-requirements/`.

Cómo se calcula la fila «Consumo frente a la cuota gratuita» (U15-E2, U15-E3):

| Cuota | Cifra oficial | Consumo | Porcentaje |
|---|---|---|---|
| Horas-instancia gratis al mes | 750 (https://render.com/docs/free) | Un servicio con enlace fijo encendido todo el mes: 720 a 744 h | 96 a 99 % |
| Horas-instancia de una sola sesión | 750 | 1,5 h, pero solo si alguien lo apaga y lo enciende para cada reto, lo que rompe «enlace fijo que no depende de nadie» (FR5.1) | 0,2 % |
| Ancho de banda Hobby | 100 GB al mes (https://render.com/pricing) | ≈ 60.600 peticiones × 5 KB ≈ 0,3 GB por sesión | 0,3 % |

Decisión: la cifra que se escribe en la casilla es la de las horas-instancia con el servicio encendido,
porque es el modo de uso que piden los requisitos. Supera el 50 % de NFR6 y, al agotarse, Render suspende
el servicio el resto del mes. Con el plan de pago no hay cuota de horas, pero cuesta (NFR6).
