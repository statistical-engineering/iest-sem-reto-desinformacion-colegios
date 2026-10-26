# Seguridad — diseño U5

Diseño no funcional de U5. Las decisiones están en `../decisions.md` (ADR-W10 a ADR-W13); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U5-S1 | `dar_acceso` de U1 deja `contexto.sala` resuelta para el nivel `sala`; toda consulta de participantes del panel lleva `AND id_sala = ?` con esa sala, y `accion_participante` busca `WHERE id = ? AND id_sala = ?` (404 si no está) |
| U5-S2 | Nivel `semillero` en la tabla de rutas para `salas`, `salas/clave`, `salas/borrar` y `POST catalogo`; `GET catalogo` queda en nivel `clave` |
| U5-S3 | `UPDATE salas SET clave_huella = ?` dentro de la misma petición; la respuesta `{sala, clave}` no pasa por `console.log` (la salida de errores de U1 tampoco registra cuerpos) |
| U5-S4 | `ErrorAPI` con `esperar_ms = 600` en `acceso_admin` cuando la clave no coincide; `Reto.fetch` ya espera fuera del bloqueo |
| U5-S5 | Las consultas de `salas` y `catalogo` nombran columnas (`SELECT codigo, estado, evento, creada, abierta, cerrada`), nunca `SELECT *` |
| U5-S6 | `responder` pasa por `traducir_respuesta` → `validar_respuesta` → `fraccion` de U4; `respuesta_publica` usa `respuesta_opaca` para todos los tipos |
| U5-S7 | `borrar_sala` ejecuta en una `transactionSync` los `DELETE` en orden eventos, respuestas, participantes, sala_colegios, salas (y `copias` desde U6); la prueba común crea una sala, la llena, la borra y pide `/api/publico?sala=` esperando 404 |
| U5-S8 | `resumen` llama a `Experimento.calcular` (completo) y `publico` (U6) a `experimento_publico`; son dos funciones distintas, no un parámetro |

OQ5 (nombres de menores en el tablero público): se conserva como hoy, porque cambiarlo altera la
conducta visible (`project.md`, «Forbidden»); la guía del docente recomienda proyectar el tablero
solo en el aula. La alternativa de mostrar solo el código personal queda anotada y rechazada por ese
motivo (A2 de `requirements.md`).
