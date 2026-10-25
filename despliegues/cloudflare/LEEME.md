# Opción: Cloudflare Workers con D1 y un Durable Object por sala

La API corre como un Worker de Cloudflare, los datos van en D1 y cada sala tiene un Durable Object que
lleva su reloj y su clasificación. Hay que reescribir el servidor en JavaScript o TypeScript.

**Estado:** sin código. Espera el ADR de esta opción.

## Estructura

```text
cloudflare/
├── LEEME.md
├── src/        código del Worker y del Durable Object
├── web/        pantallas copiadas de 2_Aplicacion_Reto/web/
└── pruebas/    pruebas unitarias de las reglas del reto
```

Cuando el ADR lo apruebe, aquí van también la configuración de Wrangler y el `package.json` con
versiones exactas.

## Pendiente de decidir en el ADR

- JavaScript o TypeScript, el runner de pruebas y la herramienta de cobertura. Cada paquete requiere
  aprobación.
- Las cuotas del plan gratuito de Workers, D1 y Durable Objects, verificadas en la documentación oficial
  con su URL.
- La regla de convenciones del lenguaje (`.claude/rules/`), que se escribe cuando se adopte el lenguaje.
