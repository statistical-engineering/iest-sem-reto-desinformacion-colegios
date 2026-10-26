# Seguridad — diseño U4

Diseño no funcional de U4. Las decisiones están en `../decisions.md` (ADR-W6 a ADR-W9); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U4-S1 | `generar_casos.py` reemplaza `BANCO` y `PREGUNTAS` de `servidor.py` por `banco_prueba.json` antes de calcular; una prueba de `casos_reglas.test.js` recorre toda la tabla y falla si algún `entrada` o `salida_esperada` contiene un id de pregunta del banco real junto a una clave `respuesta` |
| U4-S2 | La lista blanca de claves sigue en `banco.js` (`CLAVES_PREGUNTA`, `CLAVES_ANIDADAS`); `respuesta_opaca` y `revision_publica` solo devuelven lo que entra por sus argumentos ya filtrado; la prueba «examen_publico no trae ninguna clave secreta» de U1 se extiende a los 10 tipos del banco real |
| U4-S3 | `experimento_publico` construye el objeto reducido desde cero (`{n, listo}`) en vez de borrar claves del completo, así una clave nueva no se filtra por omisión |
| U4-S4 | `validar_respuesta` comprueba el tipo JavaScript y el tamaño antes de recorrer (`Array.isArray`, `typeof`, `length` ≤ ítems de la pregunta); `a_numero` recorta la cadena a 64 caracteres antes de la expresión regular |
| U4-S5 | Revisión en el PR: `grep -n "Date\|Math.random\|getRandomValues\|env\." src/reglas/` debe salir vacío; es una comprobación de `verificar.sh` |
| U4-S6 | El generador fija `sys.path` a `2_Aplicacion_Reto/`, importa `servidor` sin ejecutar `main()` y usa `conectar(":memory:")`; no toca `RUTA_DB` ni `DATOS` |
