# Tecnología — U15

Requisitos no funcionales de U15, unidad de solo documentación sobre Render. Decisiones del asistente con
la potestad que dio el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Ninguno: solo Markdown en `despliegues/COMPARACION.md` | Unidad de solo documentación (FR12.2a) |
| Plataforma | Render **no se despliega** | Nada de pago sin aprobar monto y tope (FR12.2a) |
| Pruebas | Ninguna prueba automática; la revisión es leer la columna contra `functional-spec.md` («Cifras oficiales») | No hay código (NFR12 no aplica) |
| Verificación de cifras | Cada URL se vuelve a abrir el día que se llena la tabla; si una cifra cambió, se actualiza con la nueva fecha | NFR6 («documentación oficial actual») |
| Si se aprueba el costo | Python 3.12 con uv, `unittest`, ruff, mismo `Dockerfile` de hoy copiado a `despliegues/render/` (`despliegues/render/LEEME.md`) | Lo fija el ADR de esa opción (FR12.2b) |
