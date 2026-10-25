# Opción: Render con Docker y disco persistente

El servidor en Python corre en un contenedor de Render y guarda la base SQLite en un disco que
sobrevive a los reinicios.

**Estado:** sin código. Espera el ADR de esta opción.

## Estructura

```text
render/
├── LEEME.md
├── src/        servidor en Python 3.12 (la API)
├── web/        pantallas copiadas de 2_Aplicacion_Reto/web/
└── pruebas/    pruebas unitarias con unittest (test_<modulo>.py)
```

Cuando el ADR lo apruebe, aquí van también el `Dockerfile` y la configuración de Render de esta opción.
El `render.yaml` de la raíz del repositorio despliega la versión local (`2_Aplicacion_Reto/`) y no se
toca.

## Pendiente de decidir en el ADR

- Costo: el comentario de `render.yaml` dice que el disco exige un plan de pago, y la meta del proyecto
  es US$ 0 (NFR6). Hay que verificarlo en la documentación oficial de Render y decidir si se acepta pagar
  durante la comparación.
- Si Render puede leer un Blueprint fuera de la raíz del repositorio, o si esta opción se crea a mano en
  el panel de Render.
- Python: las convenciones están en `.claude/rules/python-code.md` y ruff revisa el estilo (ADR-008).
