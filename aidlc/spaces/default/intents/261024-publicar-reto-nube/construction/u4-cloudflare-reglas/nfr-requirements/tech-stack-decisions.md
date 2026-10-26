# Tecnología — U4

Requisitos no funcionales de U4, las reglas puras de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C4. Decisiones tomadas por el asistente con la potestad que dio el humano. Lo de U1 (`../../u1-cloudflare-corte/nfr-requirements/tech-stack-decisions.md`) sigue igual; aquí solo lo que U4 agrega.

| Tema | Decisión | Por qué |
|---|---|---|
| Organización | `src/reglas/<componente>.js` más la fachada `src/reglas.js` (ADR-W6) | Un archivo por bloque de `components.md`; `reto.js` no cambia su import |
| Pruebas | Un `pruebas/<componente>.test.js` por archivo más `pruebas/casos_reglas.test.js`; se corren nombrando cada archivo | `project.md` («Corrections»): `node --test` con carpeta falla en Node 24 |
| Cobertura | `node --test --experimental-test-coverage --test-coverage-include='despliegues/cloudflare/src/reglas/**'` con piso de 80 % de líneas, comprobado en `verificar.sh` | NFR12; viene con Node 24, sin paquetes |
| Tabla de casos | `despliegues/prueba_comun/casos_reglas.json`, generada por `herramientas/generar_casos.py` (Python 3.12, biblioteca estándar, ADR-W7) y copiada por `copiar.sh` | C4; `project.md`: entre opciones solo se comparten datos |
| Banco de prueba | `despliegues/prueba_comun/banco_prueba.json`, inventado, 1.000 puntos, con un Expediente 01 propio | NFR8: ningún caso lleva respuestas del banco real |
| Criptografía | `crypto.subtle` (Web Crypto) para HMAC-SHA256 y SHA-256, como U1 | Existe igual en Workers y en Node 24 |
| Números | `Number` (doble IEEE 754) y `BigInt` solo para la variante (`variante_de`), como U1; `toFixed(9)` para la clave de orden (ADR-W8) | Igualdad con Python sin paquetes |
| Paquetes nuevos | Ninguno | FR7.6: cada paquete requiere aprobación; no hace falta |
