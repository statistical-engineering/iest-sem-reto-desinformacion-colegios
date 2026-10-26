# Tecnología — U17

Requisitos no funcionales de U17, la comparación final. Decisiones del asistente con la potestad que dio
el humano (2026-10-25).

| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje | Markdown (`COMPARACION.md`, `decisions.md`, `PUBLICAR_EN_INTERNET.md`); sin código de producción | Unidad de tipo `spec` (`unit-of-work.md`) |
| Lectura de las mediciones | A mano, desde los JSON de C3; sin script nuevo | Son 2 archivos como máximo (Workers y GitHub Pages); un script sería abstracción prematura |
| Conteo de líneas | `git ls-files … \| xargs wc -l` (BR17.6), biblioteca estándar del sistema | Repetible por cualquiera, sin paquetes |
| Comprobación de la guía | `python3 -c` con `re` sobre `PUBLICAR_EN_INTERNET.md` para contar palabras por frase (≤ 30) | Biblioteca estándar; no hay linter de Markdown aprobado |
| Pruebas | Ninguna prueba automática nueva (no hay código); antes del push, simulacro local en «TODO BIEN» y prueba común contra la ganadora si se tocó su carpeta | `bolt-plan.md`, «Reglas para todos los Bolts» |
| Cobertura | No aplica (NFR12 se evalúa de cada opción, no de U17) | — |
