## Qué cambia y por qué
<!-- 2 líneas. Enlace a la tarea, intención AI-DLC o issue si hay. -->

## Dónde mirar primero
<!-- 1 o 2 líneas: lo que el revisor debe mirar con más cuidado (lógica, nombres, un caso borde). -->

## Cobertura
<!-- Alcance del PR. -->
- **Tocado:**
- **No revisar (generado o movido sin cambios):**

## Tamaño
<!-- Máximo 400 líneas de código (añadidas + borradas). Si pasa de 400, el revisor devuelve el PR
     sin revisarlo y se divide en varios. No cuentan .md, aidlc/ ni archivos generados.
     Cambia «develop» por la rama destino del PR. -->
- Líneas de código: **+__ / −__ = __**
- Comando:
  ```bash
  git diff --numstat develop...HEAD -- . ':(exclude)*.md' ':(exclude)aidlc/' \
    ':(exclude)1_Analisis_de_datos/' ':(exclude)2_Aplicacion_Reto/banco_preguntas.json' \
    | awk '{a+=$1; b+=$2} END {print "+" a+0 " / -" b+0 " = " a+b}'
  ```

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
- [ ] Máximo 400 líneas de código (sección «Tamaño»)
- [ ] `pre-commit run --all-files` pasa
- [ ] El mensaje de cada commit pasa `commit-msg` (`tipo: descripción`)
- [ ] Sin secretos ni claves docentes en el diff
- [ ] Sin atribución a la IA en los commits ni en esta descripción: la autoría es del equipo
- [ ] Sin datos sensibles: nada de `2_Aplicacion_Reto/datos/`, `datos_prueba/` ni nombres de estudiantes
- [ ] Sin archivos de más de 500 KB
- [ ] Si toca el servidor o el banco: simulacro en «TODO BIEN» y ninguna respuesta llega al navegador antes de «resultados»
