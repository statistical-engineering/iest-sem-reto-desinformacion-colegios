# Escala — diseño U12

Diseño no funcional de U12. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- Cada función recibe las filas de una sola sala que `servicio.py` ya filtró con `WHERE sala = ?`; no
  hay variables de módulo con estado (U12-E1).
- Lo único que se guarda entre llamadas es la caché del examen por semilla, en `servicio.py`, con tope de
  200 entradas y borrado por orden de llegada (U11-P4).
- No suma cuota aparte (U12-E2).
