# Seguridad — diseño U6

Diseño no funcional de U6. Las decisiones están en `../decisions.md` (ADR-W14 a ADR-W18); los requisitos en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U6-S1 | `estado` agrega las tres claves dentro de un único `if (sala.estado === "resultados" && participante.estado === "finalizado")`; no hay otra rama que las construya |
| U6-S2 | `publico` llama a `experimento_publico(calcular(...), sala.estado)` (U4) y solo cuando el estado es `cerrado` o `resultados`; la clave `ranking` se agrega bajo su propia condición |
| U6-S3 | Las seis rutas de descarga van con nivel `sala` en la tabla de rutas; `dar_acceso` de U1 resuelve la sala y rechaza `?sala=` ajeno antes de llamar a la función |
| U6-S4 | `exportacion.js` tiene una constante `COLUMNAS_EXPORTABLES` por tabla y todas sus consultas se arman a partir de ella; `pruebas/exportacion.test.js` comprueba que `token`, `semilla`, `codigo` y `clave_huella` no aparecen en esa constante, en los encabezados de los CSV del paquete ni en los `CREATE TABLE` del guion |
| U6-S5 | `csv_resultados` y `csv_respuestas` del formato de hoy sí incluyen `codigo` (columna de hoy); se documenta en el diccionario como dato de la sala que no va al paquete |
| U6-S6 | Toda consulta de exportación lleva `WHERE p.id_sala = ?` o un `JOIN` a `participantes` con esa condición; la copia incluye la fila de `salas` solo de ese `id_sala` |
| U6-S7 | `borrar_sala` (U5) agrega `DELETE FROM copia_trozos WHERE id_copia IN (SELECT id_copia FROM copias WHERE id_sala = ?)` y `DELETE FROM copias WHERE id_sala = ?` dentro de la misma `transactionSync` |
| U6-S8 | Los nombres se arman con el código de sala (ya `[A-Z0-9]{3,8}`) y una fecha con formato fijo; ninguna cadena del usuario entra en una cabecera HTTP |
| U6-S9 | Los `console.log` de esta unidad llevan solo código de sala, `id_copia` y bytes |
