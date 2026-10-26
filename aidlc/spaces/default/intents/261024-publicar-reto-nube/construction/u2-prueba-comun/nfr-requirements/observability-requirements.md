# Observación — U2

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba entrega a U17. Salen de `requirements.md` (FR12.4), del contrato (C3) y del diseño funcional
(`rules.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-O1 | Cada comprobación se imprime con ✔ o ✘ y su mensaje, agrupada por paso, como en U1 y en `simulacro.py`; al final «TODO BIEN» o la lista de fallas | BR1.2 |
| U2-O2 | Cada corrida escribe `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` con el esquema C3 (`version_esquema` 1), y es la única salida que U17 lee | FR12.4, C3, BR8.1 |
| U2-O3 | El JSON trae, además de lo obligatorio, `duracion_min`, `fracciones` (k, pregunta_id, fracción) y el número de muestras de cada p95 en el `detalle` de sus comprobaciones, para que U17 compare la calificación y juzgue la medición | NFR11, BR8.1 |
| U2-O4 | La prueba imprime el tiempo de cada paso y, en la espera del vencimiento, cuánto falta cada 60 s, para que quien la mira sepa que no está colgada | BR4.2 |
| U2-O5 | Ningún registro ni salida lleva claves, tokens ni respuestas correctas | NFR9, U2-S4 |
