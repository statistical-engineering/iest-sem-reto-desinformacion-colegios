# Escala — diseño U3

Diseño no funcional de U3. Las decisiones están en `../decisions.md`; los requisitos en
`../nfr-requirements/`.

- **Nada que guardar** (U3-E2). Los ids opacos se calculan por petición; `reto.db` conserva su esquema y
  las copias de «Reiniciar» su tamaño. Es la ventaja de la alternativa A de ADR-006 frente a una tabla de
  equivalencias.
- **Carga de hoy** (U3-E1). Con 40 participantes, el sondeo de `estudiante.js` (cada 20 s en curso) y el
  del tablero (cada 2 s, que no calcula opacos) el costo nuevo es de unos 500 HMAC por segundo en el peor
  caso: despreciable frente al `LOCK` y a SQLite.
- **Una instancia** (U3-E3). No hay estado nuevo en memoria: la versión local sigue con un proceso, un
  candado y un archivo SQLite, como dice `project.md` («Deployment»).
