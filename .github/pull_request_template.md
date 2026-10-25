## Trazabilidad

- Rama origen → destino:
  - [ ] `refactor/...`, `fix/...`, `feat/...` o `chore/...` → `develop`
  - [ ] `develop` → `main` (versión final, ya desplegada y verificada desde `develop`)
- Intención AI-DLC / unidad (si aplica): `aidlc/spaces/default/intents/...`
- Fecha:

## Tipo de cambio

- [ ] Corrección (`fix`)
- [ ] Funcionalidad (`feat`)
- [ ] Refactorización sin cambio visible (`refactor`)
- [ ] Despliegue o configuración (`chore`)
- [ ] Documentación (`docs`)

## Resumen del cambio

>

## Partes que toca

- [ ] Servidor (`2_Aplicacion_Reto/servidor.py`)
- [ ] Pantallas (`2_Aplicacion_Reto/web/`)
- [ ] Banco de preguntas o scripts de datos (`4_Codigo_y_datos/scripts/`, regenerado, nunca a mano)
- [ ] Guías docentes (`3_Guia_docente/`)
- [ ] Despliegue (`render.yaml`, `Dockerfile`, `PUBLICAR_EN_INTERNET.md`)
- [ ] Lanzadores `.bat` / `.command`
- [ ] Documentación

## Cómo se probó

- [ ] `python3 pruebas/simulacro.py 40` desde `2_Aplicacion_Reto/` termina en «TODO BIEN» (obligatorio si cambia el servidor o el banco)
- [ ] Pruebas `unittest` nuevas o tocadas pasan; cobertura ≥ 80 % medida con `trace`
- [ ] Probado en el hosting desde `develop` (obligatorio en el PR a `main`)

Salida o evidencia:

>

## Invariantes del reto

- [ ] Las respuestas correctas no llegan al navegador antes de «resultados»
- [ ] El banco suma 1.000 puntos y no se editó ningún archivo generado a mano
- [ ] No cambia nada visible (pantallas, preguntas, puntajes, desempates, flujo de estados), salvo corregir una fuga
- [ ] No incluye claves docentes, `2_Aplicacion_Reto/datos/`, `datos_prueba/` ni `.herramientas/`
- [ ] No se despliega con un reto en curso

## Riesgo

- [ ] Bajo
- [ ] Medio
- [ ] Alto

Observaciones y cómo volver atrás:

>

## Lección aprendida (opcional)

>
