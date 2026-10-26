# Seguridad — U4

Requisitos no funcionales de U4, las reglas puras de Cloudflare Workers. Salen de `requirements.md` (NFR1 a NFR12), del diseño funcional (`functional-spec.md`, `rules.md`) y del contrato C4. Decisiones tomadas por el asistente con la potestad que dio el humano.

| Id | Requisito | Origen |
|---|---|---|
| U4-S1 | Ni `casos_reglas.json`, ni `banco_prueba.json`, ni ningún archivo de `pruebas/` contiene una respuesta, explicación o veredicto del banco real; los casos de Calificacion y Experimento usan el banco de prueba inventado | NFR8, C4 (`no_lleva`), `project.md` («Forbidden») |
| U4-S2 | `examen_publico`, `respuesta_opaca` y `revision_publica` son las únicas funciones que producen datos para el navegador, y una prueba recorre el examen público del banco real buscando `respuesta`, `explicacion`, `tolerancia`, `solo_grupo` y `variantes` | NFR8, BR1.3 |
| U4-S3 | `experimento_publico` nunca devuelve `verdad`, `multitud_acierta`, `clase`, `por_publicacion` ni `multitud` fuera de `resultados` | FR6.1, ADR-W9 |
| U4-S4 | Toda entrada del navegador que llega a una regla está acotada antes de procesarse: `texto` ≤ `max` + 50 caracteres, `a_numero` sobre cadenas ≤ 64 caracteres, listas y objetos con como máximo el número de ítems de la pregunta; las expresiones regulares de `a_numero` y `normalizar_texto` no tienen retroceso catastrófico (sin cuantificadores anidados) | FR10.1, `phases/construction.md` («Security», validar en los bordes) |
| U4-S5 | Las reglas no leen `env`, secretos, `Date`, `Math.random` ni `crypto.getRandomValues`; solo `crypto.subtle` para HMAC y SHA-256 con la semilla que reciben | ADR-001, ADR-006 |
| U4-S6 | `generar_casos.py` solo importa `servidor.py`; nunca abre `2_Aplicacion_Reto/datos/` ni escribe fuera de `despliegues/prueba_comun/` | FR12.1, `CLAUDE.md` («Reglas para asistentes») |
