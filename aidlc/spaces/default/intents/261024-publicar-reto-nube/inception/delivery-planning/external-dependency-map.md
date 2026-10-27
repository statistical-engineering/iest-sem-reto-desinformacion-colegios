# Lo que depende de afuera

Lo que el equipo no controla y puede frenar un **Bolt**, que es una pasada de construcción que termina
en algo que funciona (`bolt-plan.md`).

## Dependencias

| Dependencia | Dueño | Cuánto tarda | Bloquea | Si se atrasa |
|---|---|---|---|---|
| Cuenta gratuita de Cloudflare, con Workers, D1 y Durable Objects | Humano o semillero (Q8-A) | Minutos | B1 y su cadena (B4, B9, B11) | La prueba común mínima se termina contra la versión local (Q5-A) |
| Clave docente (`CLAVE_DOCENTE`) cargada como secreto en Cloudflare (antes, clave del semillero) | Humano o semillero | Minutos | Demo de B9 y siguientes | El asistente no la puede cargar: se espera |
| Cuenta de GitHub con Pages | — | — | Nada: GitHub Pages no se construye (revisión del 2026-10-25) | — |
| Documentación oficial de Render y Cloudflare Containers | Los proveedores | Lo que tarde leerla | B5, B6 | Se cita la versión consultada con su fecha |
| Aprobación de saltar U7 a U10 | Humano | Una respuesta | B13 | U17 espera |
| Que no haya un reto en curso al desplegar | Docente | Según calendario | Todo despliegue | Se despliega después del reto |

## Lo que no depende de afuera

Lo demás lo construye el agente desarrollador sin depender de nadie más (`team-allocation.md`). No se
agrega ningún paquete sin aprobación; la prueba común usa solo la biblioteca estándar de Python (Q6-A).
