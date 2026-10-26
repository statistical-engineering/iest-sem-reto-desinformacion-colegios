# Rapidez — diseño U3

Diseño no funcional de U3. Las decisiones están en `../decisions.md` (ADR-L1 a ADR-L3); los requisitos en
`../nfr-requirements/`.

- **Un HMAC por id, un `hmac.new` por grupo** (U3-P1). `opacos_de` crea la clave una vez por grupo y
  firma cada id; `opacar_salida` llama a `opacos_de` a lo sumo cinco veces por pregunta (opciones, ítems,
  publicaciones, partes y las opciones de cada parte). Con 42 preguntas son unos 250 HMAC-SHA256 de
  mensajes cortos: del orden de 1 a 3 ms en total.
- **Solo la pregunta recibida** (U3-P2). `traducir_entrada` calcula los opacos de la pregunta que llega,
  no del examen entero.
- **Sin caché** (U3-P3). El examen se arma en cada `/api/estado` como hoy; el costo extra es menor que
  el de serializar el JSON de las misiones (unos 200 KB). Si `timeit` mostrara más de 5 ms por estado,
  la caché por semilla de Workers (`code-summary.md` de U1, desviación 13) sería el siguiente paso, en
  otra unidad.
- **Dentro del `LOCK`**. Todo sigue dentro del candado global de hoy; con 40 participantes y sondeo
  cada 20 s (U3-E1) el candado se ocupa unos milisegundos más por segundo.
