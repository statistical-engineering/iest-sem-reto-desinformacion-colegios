# Tecnología — U17

> **Revisión 2026-10-27 (una sola sala).** Las mediciones son las dos corridas de Cloudflare; entran el `LEEME.md` de Cloudflare, `.gitattributes` y `revisar_comparacion.py` como comprobación de la tabla.

Requisitos no funcionales de U17, la comparación final. Decisiones del asistente con la potestad que dio
el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Markdown (`COMPARACION.md`, `decisions.md`, `PUBLICAR_EN_INTERNET.md`, `despliegues/cloudflare/LEEME.md`) y una línea de `.gitattributes`; sin código de producción | Unidad de tipo `spec` (`unit-of-work.md`) |
| Lectura de las mediciones | A mano, desde los JSON de C3; sin script nuevo | Son 2 archivos (corrida pública y `wrangler dev` de Cloudflare, ADR-C5); un script sería abstracción prematura |
| Conteo de líneas | `git ls-files … \| xargs wc -l` (BR17.6), biblioteca estándar del sistema | Repetible por cualquiera, sin paquetes |
| Comprobación de la tabla | `despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion <columna>` (de U15) para cada una de las cinco columnas | Ya existe, biblioteca estándar; exige URL o comando entre comillas invertidas en cada casilla con cifra |
| Comprobación de la guía | `python3 -c` con `re` sobre `PUBLICAR_EN_INTERNET.md` para contar palabras por frase (≤ 30) | Biblioteca estándar; no hay linter de Markdown aprobado |
| Pruebas | Ninguna prueba automática nueva (no hay código); antes del push, simulacro local en «TODO BIEN»; la prueba común contra Cloudflare no se repite porque U17 solo toca su `LEEME.md` | `bolt-plan.md`, «Reglas para todos los Bolts» |
| Cobertura | No aplica (NFR12 se evalúa de cada opción, no de U17) | — |
