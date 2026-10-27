# Opción: Render con Docker y disco persistente

El servidor en Python corre en un contenedor de Render y guarda la base SQLite en un disco que
sobrevive a los reinicios.

**Estado:** documentada, no se despliega. El plan gratuito duerme y no tiene disco, y el plan con disco
cuesta US$ 7 al mes; la meta es US$ 0 (NFR6). Las cifras, con su URL oficial y la fecha de consulta, están
en la columna Render de [`../COMPARACION.md`](../COMPARACION.md). Para comprobar que cada cifra tiene
fuente:

```bash
python3 despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion render
```

Si el semillero aprueba un monto y un tope, se agregan las unidades para construirla (corte delgado,
reglas, salas y catálogo, resultados y exportación) y el monto queda en el ADR de esta opción (FR12.2a).

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

## Decidido (U15, 2026-10-25)

- Costo: verificado en la documentación oficial; el disco exige un plan de pago. No se paga durante la
  comparación.
- `render.yaml` de la raíz sigue desplegando la versión local y no se toca.
- Python: si algún día se construye, sigue `.claude/rules/python-code.md` y ruff (ADR-008).
