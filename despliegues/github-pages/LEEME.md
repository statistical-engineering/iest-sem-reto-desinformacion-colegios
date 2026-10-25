# Opción: GitHub Pages con la API en otro servicio

GitHub Pages solo sirve archivos estáticos: las pantallas van en Pages, y la API, que califica y guarda
los datos, corre en otro servicio.

**Estado:** sin código. Espera el ADR de esta opción.

## Estructura

```text
github-pages/
├── LEEME.md
├── web/        sitio que publica GitHub Pages (pantallas copiadas de 2_Aplicacion_Reto/web/)
├── src/        la API en el servicio que elija el ADR
└── pruebas/    pruebas unitarias de las reglas del reto
```

## Pendiente de decidir en el ADR

- Qué servicio aloja la API. Si es uno de los de las otras carpetas, esta opción mide sobre todo cuánto
  cambia separar las pantallas de la API.
- Cómo las pantallas llaman a una API en otro dominio (CORS), sin cambiar lo que ve el estudiante.
- Cómo se publica `web/` desde esta carpeta (GitHub Actions o la configuración de Pages), verificado en
  la documentación oficial de GitHub.
