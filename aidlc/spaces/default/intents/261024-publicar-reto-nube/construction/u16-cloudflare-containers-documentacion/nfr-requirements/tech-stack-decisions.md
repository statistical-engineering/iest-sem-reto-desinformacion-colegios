# Tecnología — U16

Requisitos no funcionales de U16, unidad de solo documentación sobre Cloudflare Containers. Decisiones
del asistente con la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Ninguno: solo Markdown en `despliegues/COMPARACION.md` y en `despliegues/cloudflare-containers/LEEME.md` | Unidad de solo documentación (FR12.2a) |
| Plataforma | Cloudflare Containers **no se despliega** | Solo en Workers Paid (US$ 5 al mes); nada de pago sin aprobar monto y tope (FR12.2a) |
| Pruebas | Ninguna prueba automática; la revisión es leer la columna contra `functional-spec.md` («Cifras oficiales») | No hay código (NFR12 no aplica) |
| Verificación de cifras | Cada URL se vuelve a abrir el día que se llena la tabla; si una cifra cambió, se actualiza con la nueva fecha | NFR6 («documentación oficial actual») |
| Si se aprobara el costo | Python 3.12 con el `Dockerfile` de hoy copiado, más Worker en JavaScript con la clase `Container`, Docker local y `wrangler`; **y** un cambio de la aplicación para guardar datos fuera del contenedor | Lo fija el ADR de esa opción (FR12.2b); el cambio de la app es obligatorio por el disco efímero (NFR4) |
| Recomendación | No pedir aprobación de costo para esta opción: Workers (U1) ya cubre lo mismo gratis y con persistencia | `functional-spec.md`, «Comparación con la opción Cloudflare Workers» |
