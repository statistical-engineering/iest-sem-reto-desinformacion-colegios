# Seguridad — diseño U16

Diseño no funcional de U16 (solo documentación sobre Cloudflare Containers). Los requisitos están en
`../nfr-requirements/`.

| Requisito | Cómo |
|---|---|
| U16-S1 | Antes del push se revisa la columna con `grep -n -i -E "clave|token|KQMT-" despliegues/COMPARACION.md`; nada de eso debe salir con un valor real |
| U16-S2 | No se activa el plan de pago; las URL son públicas y no exigen sesión |
| U16-S3 | La fila «Sobrevive a un reinicio» anota que las instantáneas duran 30 días: si algún día se aprobara, el cierre del reto tendría que borrarlas (NFR10.1) |
