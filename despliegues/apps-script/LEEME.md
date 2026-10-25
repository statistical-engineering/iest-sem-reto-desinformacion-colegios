# Opción: Google Apps Script con Google Sheets

La API corre como una aplicación web de Apps Script y los datos se guardan en una hoja de cálculo de
Google. Hay que reescribir el servidor en Apps Script (JavaScript).

**Estado:** sin código. Espera el ADR de esta opción.

## Estructura

```text
apps-script/
├── LEEME.md
├── src/        código .gs y las pantallas .html (Apps Script sirve el HTML desde el mismo proyecto)
└── pruebas/    pruebas unitarias de las reglas del reto
```

Esta opción no tiene `web/`: Apps Script exige que las pantallas vivan junto al código, en `src/`. Se
copian de `2_Aplicacion_Reto/web/` sin cambiar lo que ve el estudiante.

## Pendiente de decidir en el ADR

- Cómo se sube el código (a mano o con `clasp`, que es un paquete y requiere aprobación). El archivo
  `.clasp.json` lleva el identificador del proyecto: si se usa, no se versiona.
- Las cuotas de ejecuciones simultáneas, `LockService` y la latencia, verificadas en la documentación
  oficial de Google con su URL.
- Cómo se evita que la hoja de cálculo exponga las respuestas antes de «resultados».
