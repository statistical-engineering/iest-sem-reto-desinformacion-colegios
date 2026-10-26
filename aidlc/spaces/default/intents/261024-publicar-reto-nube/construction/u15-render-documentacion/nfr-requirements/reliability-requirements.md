# Confiabilidad — U15

Requisitos no funcionales de U15, unidad de solo documentación sobre Render. Salen de `requirements.md`
(NFR1 a NFR12) y de `functional-spec.md` de esta unidad. Cifras de la documentación oficial consultada el
2026-10-25. Decisiones del asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U15-R1 | NFR4 en el plan gratuito queda «no cumple»: sistema de archivos efímero que se pierde al redesplegar, reiniciar o dormir, y sin disco persistente (https://render.com/docs/free) | NFR4 |
| U15-R2 | NFR4 en el plan de pago con disco queda «sí según documentación, sin medir»: copia cada 24 h guardada 7 días (https://render.com/docs/disks) | NFR4 |
| U15-R3 | NFR5 en el plan gratuito queda «no cumple»: duerme a los 15 minutos y despierta en «about one minute» (https://render.com/docs/free), más de los 30 s de NFR5 | NFR5 |
| U15-R4 | La columna anota el apagado a mitad del reto: en gratuito, Render puede reiniciar en cualquier momento («may also restart a Free web service at any time»); con disco, cada despliegue deja el servicio sin responder unos segundos (https://render.com/docs/disks) | NFR4, `project.md` («no cambiar nada con un reto en curso») |
| U15-R5 | NFR11 no se evalúa: no hay código desplegado | NFR11 |
