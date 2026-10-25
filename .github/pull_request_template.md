## Qué cambia y por qué
<!-- 2 líneas. Enlace a la tarea, intención AI-DLC o issue si hay. -->

## Dónde mirar primero
<!-- 1 o 2 líneas: lo que el revisor debe mirar con más cuidado (lógica, nombres, un caso borde). -->

## Cobertura
<!-- Alcance del PR. -->
- **Tocado:**
- **No revisar (generado o movido sin cambios):**

## Cómo verificar
<!-- Comandos exactos que corrí y su resultado, para repetirlos. -->
| Comando | Resultado |
|---|---|
| `pre-commit run --all-files` | |
| `python3 -m unittest` (desde `2_Aplicacion_Reto/`) | |
| `python3 pruebas/simulacro.py 40` (desde `2_Aplicacion_Reto/`) | |

## Fuente de verdad
<!-- 4_Codigo_y_datos/datos_originales/ es de solo lectura. -->
- `git diff --stat develop...HEAD -- 4_Codigo_y_datos/datos_originales/` → (vacío)
- Salidas regeneradas: (ninguna / cuáles y con qué script)

## Decisiones que tomé solo
<!-- Decisión → alternativa descartada y por qué. «Ninguna» si no hubo. -->
-

## Checklist
- [ ] `pre-commit run --all-files` pasa
- [ ] El mensaje de cada commit pasa `commit-msg` (`tipo: descripción`)
- [ ] Sin secretos ni claves docentes en el diff
- [ ] Sin datos sensibles: nada de `2_Aplicacion_Reto/datos/`, `datos_prueba/` ni nombres de estudiantes
- [ ] Sin archivos de más de 500 KB
- [ ] Si toca el servidor o el banco: simulacro en «TODO BIEN» y ninguna respuesta llega al navegador antes de «resultados»
