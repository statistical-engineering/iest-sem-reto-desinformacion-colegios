# Confiabilidad — diseño U12

Diseño no funcional de U12. Las decisiones son las del ADR de U11; los requisitos en `../nfr-requirements/`.

- Mismos resultados que hoy: las nueve funciones puras de `servidor.py` se copian sin cambios; las seis
  reescritas se comprueban fila a fila contra `casos_reglas.json`, cuya `salida_esperada` se calculó con
  la versión local (U12-R1).
- Determinismo: la única aleatoriedad es `rng_para(semilla)` (`random.Random` sembrado), igual que hoy;
  `ordenar` no usa `set` ni `dict` sin orden (U12-R2).
- `ordenar` cierra la clave de orden con `id`, que es único por participante (U12-R3).
- Entradas mal formadas: `validar_respuesta` devuelve `("error", mensaje)`; `traducir_opaco` devuelve
  `None`; `hora_de_entrega` acepta `cierre=None`; `normalizar_texto` acepta `None` y devuelve `""`.
  `servicio.py` convierte cada uno en el 400 de hoy (U12-R4).
