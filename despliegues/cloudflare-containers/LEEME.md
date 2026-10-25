# Opción: Cloudflare Containers con el Dockerfile actual

El servidor en Python corre en un contenedor de Cloudflare, armado igual que la imagen de hoy
(`2_Aplicacion_Reto/Dockerfile`). Es la opción b del pedido inicial.

**Estado:** sin código. Espera el ADR de esta opción.

## Estructura

```text
cloudflare-containers/
├── LEEME.md
├── src/        servidor en Python 3.12 (la API)
├── web/        pantallas copiadas de 2_Aplicacion_Reto/web/
└── pruebas/    pruebas unitarias con unittest (test_<modulo>.py)
```

Cuando el ADR lo apruebe, aquí van también el `Dockerfile` propio de esta opción y su configuración de
Cloudflare. La versión de hoy no se toca: el `Dockerfile` se copia, no se mueve.

## Pendiente de decidir en el ADR

- Dónde quedan los datos: si el contenedor tiene disco persistente o se apaga a mitad del reto, y qué
  pasa con la base SQLite en ese caso. Se verifica en la documentación oficial de Cloudflare.
- Si esta opción tiene plan gratuito. Si no lo tiene, no se despliega sin aprobar antes el costo
  (FR12.2a).
- Python: las convenciones están en `.claude/rules/python-code.md` y ruff revisa el estilo (ADR-008).
