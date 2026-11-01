# Componentes lógicos — U4

> **Revisión 2026-10-27 (una sola sala).** `ciclo_de_sala.js` (CicloDeSala) pasa a `ciclo_del_reto.js` (CicloDelReto), como en `../functional-design/functional-spec.md`; todos los módulos pueden usar `comun.js` (`redondear` lo usan Calificacion y Clasificacion).

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

```mermaid
graph LR
  R[reto.js] --> F[reglas.js: fachada]
  F --> B[reglas/banco.js]
  F --> C[reglas/calificacion.js]
  F --> K[reglas/clasificacion.js]
  F --> S[reglas/ciclo_del_reto.js]
  F --> L[reglas/limpieza_entrada.js]
  F --> X[reglas/experimento.js]
  B --> M[reglas/comun.js]
  C --> M
  K --> M
  S --> M
  L --> M
  X --> M
  P[pruebas/*.test.js] --> F
  P --> T[pruebas/casos_reglas.json]
  G[prueba_comun/herramientas/generar_casos.py] --> U[prueba_comun/casos_reglas.json]
  G -.lee.-> V[2_Aplicacion_Reto/servidor.py]
  U -.copiar.sh.-> T
```

Texto alternativo: `reto.js` sigue importando la fachada `reglas.js`, que reexporta seis módulos, uno por
componente de la capa Reglas; los seis usan `comun.js` y no se importan entre sí. Las pruebas importan
la fachada y leen la copia de la tabla de casos, que `copiar.sh` trae desde `despliegues/prueba_comun/`,
donde la genera un script de Python que solo lee `servidor.py`.

| Archivo | Componente de `components.md` |
|---|---|
| `src/reglas/banco.js` | Banco |
| `src/reglas/calificacion.js` | Calificacion |
| `src/reglas/clasificacion.js` | Clasificacion |
| `src/reglas/ciclo_del_reto.js` | CicloDelReto |
| `src/reglas/limpieza_entrada.js` | LimpiezaEntrada |
| `src/reglas/experimento.js` | Experimento |
| `src/reglas/comun.js`, `src/reglas.js` | apoyo y fachada (ADR-W6) |
| `despliegues/prueba_comun/herramientas/generar_casos.py`, `casos_reglas.json`, `banco_prueba.json` | contrato C4 (datos compartidos, ADR-W7) |
