# Confiabilidad — diseño U13

Diseño no funcional de U13. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- Cierre en una transacción con `UPDATE … WHERE id = ? AND estado = 'en_curso'`: si otra petición ya
  entregó a alguien, el `UPDATE` no toca su fila (U13-R1).
- Toda consulta de participantes, respuestas y eventos lleva `sala`; la prueba de dos salas de U2 lo
  comprueba desde fuera y `test_servicio.py` desde dentro (U13-R2).
- Acciones del docente con condición de estado en el `WHERE`; `rowcount == 0` → 400 con el mensaje de
  hoy (U13-R3).
- `INSERT` del colegio con `UNIQUE(nombre_normalizado)`; `IntegrityError` → se busca el existente y se
  responde 400 con `existente` (U13-R4).
- Migración de esquema con `user_version` al arrancar, idempotente (U13-R5).
