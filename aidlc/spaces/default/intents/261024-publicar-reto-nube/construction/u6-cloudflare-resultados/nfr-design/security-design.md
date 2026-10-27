# Seguridad — diseño U6

> **Revisión 2026-10-27 (una sola sala).** Las rutas de U6 van con nivel `clave` (ya no `sala` ni
> `semillero`); se quitan `?sala=` y `id_sala`; U6-S6 y U6-S7 cambian (clave fuera de los archivos,
> borrar una copia).

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18 y ADR-W21); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U6-S1 | `estado` agrega las cuatro claves dentro de un único `if (reto.estado === "resultados" && participante.estado === "finalizado")`; no hay otra rama que las construya |
| U6-S2 | `publico` llama a `experimento_publico(calcular(...), reto.estado)` (U4) solo cuando el estado es `cerrado` o `resultados`; `ranking` y `por_grado` se agregan bajo una sola condición (`resultados` o modo sorpresa apagado) |
| U6-S3 | Las siete rutas de U6 van con nivel `clave` en `RUTAS`; el acceso de U5 compara `X-Clave-Admin` con `CLAVE_DOCENTE` en tiempo constante y rechaza `?clave=` antes de llamar a la función |
| U6-S4 | `exportacion.js` tiene una constante `COLUMNAS_EXPORTABLES` por tabla y todas sus consultas se arman a partir de ella; `pruebas/exportacion.test.js` comprueba que `token`, `semilla`, `codigo` y `clave_huella` no aparecen en esa constante, en los encabezados de los CSV del paquete ni en los `CREATE TABLE` del guion |
| U6-S5 | `csv_resultados` y `csv_respuestas` del formato de hoy sí incluyen `codigo` (columna de hoy); el diccionario lo anota como dato que no va al paquete |
| U6-S6 | Ninguna función de exportación recibe `env`; la prueba unitaria arma un paquete con una clave de prueba conocida y la busca en los bytes del `.zip` |
| U6-S7 | `borrar_copia` hace `DELETE FROM copia_trozos WHERE id_copia = ?` y `DELETE FROM copias WHERE id_copia = ?` en la misma `transactionSync`; un id inexistente da 404 sin tocar nada |
| U6-S8 | Los nombres se arman con el código de sala (ya de 3 a 8 letras o números) y una fecha con formato fijo; ninguna cadena del usuario entra en una cabecera HTTP |
| U6-S9 | Los `console.log` de esta unidad llevan solo `id_copia`, bytes y el commit |
