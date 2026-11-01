# Observación — U2

> **Revisión 2026-10-27 (una sola sala).** U2-O3 suma las claves agregadas del C3 revisado (`vencimiento`,
> `no_aplica`, `p95_resumen_ms`, `encabezados_csv`) y `nfr.colegios` en vez de `salas` (D8). U2-O4 cuenta
> la espera de cada colegio.

Requisitos no funcionales de U2, la prueba común completa. Son requisitos de la **prueba misma**, más lo
que la prueba entrega a U17. Salen de `requirements.md` (FR12.4), del contrato (C3) y del diseño funcional
(`rules.md`). Decisiones tomadas por el asistente con la potestad que dio el humano (2026-10-25).

| Id | Requisito | Origen |
|---|---|---|
| U2-O1 | Cada comprobación se imprime con ✔ o ✘ y su mensaje, agrupada por paso, como en U1 y en `simulacro.py`; al final «TODO BIEN» o la lista de fallas, y «No aplican: N» con los ids | BR1.2 |
| U2-O2 | Cada corrida escribe `despliegues/prueba_comun/mediciones/<opcion>_<AAAA-MM-DD>.json` (o la ruta de `--salida`) con el esquema C3 (`version_esquema` 1, partes `base`, `fugas`, `relojes`, `claves` y `nfr`), y es la única salida que U17 lee | FR12.4, C3, D8, BR8.1 |
| U2-O3 | El JSON trae, además de lo obligatorio (`nfr.colegios`, `participantes`, `peticiones`…), `duracion_min`, `vencimiento`, `no_aplica` ({id, motivo}), `p95_resumen_ms`, `fracciones` ({k, pregunta_id, fraccion}), `encabezados_csv` y el número de muestras de cada p95 en el `detalle` de sus comprobaciones, para que U17 compare la calificación y juzgue la medición | NFR11, BR8.1, BR8.2 |
| U2-O4 | La prueba imprime el tiempo de cada paso y, en la espera del vencimiento, cuánto falta para el vencimiento de cada colegio cada 60 s, para que quien la mira sepa que no está colgada | BR4.2 |
| U2-O5 | Ningún registro ni salida lleva claves, tokens ni respuestas correctas | NFR9, U2-S4 |
