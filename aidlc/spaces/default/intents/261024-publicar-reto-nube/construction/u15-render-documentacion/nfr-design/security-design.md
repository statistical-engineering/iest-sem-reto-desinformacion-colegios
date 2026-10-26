# Seguridad — diseño U15

Diseño no funcional de U15 (solo documentación sobre Render). Los requisitos están en `../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U15-S1 | Antes del push se revisa la columna con `grep -n -i -E "clave|token|KQMT-" despliegues/COMPARACION.md`; nada de eso debe salir con un valor real |
| U15-S2 | No se abre cuenta en Render; las URL son públicas y no exigen sesión |
| U15-S3 | La fila «Sobrevive a un reinicio» anota que las copias del disco duran 7 días: si algún día se aprueba Render, el cierre del reto tiene que esperar o borrar esas copias (NFR10.1) |
