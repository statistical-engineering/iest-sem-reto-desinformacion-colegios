# Aplicación del reto — documentación técnica

Servidor web en **Python puro** (solo biblioteca estándar, Python 3.9+) con base de datos SQLite.
Los estudiantes no instalan nada: usan el navegador.

## Uso rápido

| Acción | Cómo |
|---|---|
| Probar que todo funciona | Doble clic en `PROBAR_ANTES_DEL_RETO.bat` (Windows) o `.command` (Mac) — o `python3 pruebas/simulacro.py 40` |
| Iniciar el reto | Doble clic en `INICIAR_RETO.bat` (Windows) o `INICIAR_RETO.command` (Mac) — o `python3 servidor.py` |
| Otro puerto | `python servidor.py --puerto 8080` |
| Fijar la clave docente | `python3 servidor.py --clave MICLAVE` |
| Abrir el reto por internet desde tu Mac (temporal) | `INICIAR_RETO_INTERNET.command` |

Al arrancar imprime las direcciones:

- **Estudiantes:** `http://<IP-del-computador>:8000/`
- **Tablero (proyector):** `http://<IP>:8000/tablero`
- **Panel docente:** `http://localhost:8000/admin` (clave en la consola y en `datos/clave_docente.txt`)

## Cómo se conectan los estudiantes
| Situación | Qué usar |
|---|---|
| Todos en la **misma red wifi** | `INICIAR_RETO` y la dirección `http://192.168.x.x:8000` que muestra la ventana y el tablero. En Mac, si pregunta por conexiones entrantes, pulsa **Permitir**. Algunos wifi de colegios bloquean la conexión entre equipos: usa entonces internet. |
| **Cualquier red** (enlace fijo, sin depender de tu computador) | Publicar en un hosting: ver `../PUBLICAR_EN_INTERNET.md` |
| **Cualquier red, solo por hoy**, desde tu Mac | `INICIAR_RETO_INTERNET.command` (instala `cloudflared` con Homebrew la primera vez). El enlace `https://….trycloudflare.com` cambia cada vez y el Mac debe quedar encendido, con la ventana abierta. |

El panel docente siempre se abre desde el computador del docente (`http://localhost:8000/admin`) y pide la clave,
aunque los estudiantes entren por un enlace público.

## Archivos

| Archivo | Qué es |
|---|---|
| `servidor.py` | Servidor: inscripción, reloj, calificación, clasificación, experimento de clase, exportaciones |
| `banco_preguntas.json` | Banco de 42 preguntas (41 para el grupo A y 42 para el B del experimento; 37 con puntos) con respuestas. **Solo lo lee el servidor**; nunca se envía al navegador |
| *(el generador del banco está en `../4_Codigo_y_datos/scripts/construir_banco.py`)* | Las respuestas de datos se calculan, no se escriben a mano |
| `web/estudiante.html`, `web/js/estudiante.js` | App del estudiante |
| `web/admin.html`, `web/js/admin.js` | Panel docente |
| `web/tablero.html` | Tablero para proyectar (inscripción, cuenta regresiva, podio, experimento) |
| `web/js/graficos.js` | Gráficos SVG interactivos sin librerías externas (funcionan sin internet) |
| `web/css/reto.css` | Estilos |
| `pruebas/simulacro.py` | Simulacro automático con estudiantes ficticios (27 comprobaciones) |
| `datos/` | Se crea al iniciar: `reto.db` (todo el reto), `clave_docente.txt` y copias de seguridad |

## Garantías que hace cumplir el servidor

- Las respuestas correctas y explicaciones solo se envían cuando el docente publica resultados.
- Cada pregunta se responde una vez; la fase «¿es verdad?» del Expediente 01 exige haber respondido
  antes «¿lo compartirías?».
- El tiempo lo mide el servidor (90 min desde «Comenzar»); un vigilante entrega los intentos vencidos
  cada 3 segundos, aunque el estudiante haya cerrado el navegador.
- Clasificación en orden total: puntaje total ↓, puntos ↓, momento de la última respuesta ↑, hora de
  entrega ↑, orden de inscripción ↑.
- Grupo A/B del experimento asignado de forma alternada (grupos del mismo tamaño); solo el grupo B ve
  el «recordatorio de exactitud» (sin puntos).

## API (por si se quiere integrar algo)

| Método y ruta | Quién | Para qué |
|---|---|---|
| `POST /api/registro` | estudiante | `{nombre, colegio, grado, integrantes, sala}` → `{token, codigo}` |
| `POST /api/entrar` | estudiante | `{codigo}` → `{token}` |
| `GET /api/estado` | estudiante (Bearer token) | Estado, preguntas públicas, respuestas propias; revisión si hay resultados |
| `POST /api/comenzar`, `/api/responder`, `/api/finalizar`, `/api/evento` | estudiante | Flujo del reto |
| `GET /api/publico` | tablero | Estado, conteos, top 10 (si no hay modo sorpresa), experimento |
| `GET /api/admin/resumen`, `/api/admin/resultados.csv`, `/api/admin/respuestas.csv` | docente (`X-Clave-Admin`) | Panel y exportaciones |
| `POST /api/admin/estado`, `/config`, `/participante`, `/reiniciar` | docente | Control |

## Verificación realizada

- `pruebas/simulacro.py`: 27 comprobaciones (inscripción, bloqueo de respuestas, grupos del experimento,
  vencimiento del tiempo, 1.000 puntos con todo correcto y 0 con todo incorrecto, puestos únicos,
  revisión, CSV, reinicio). Resultado: todas correctas.
- Prueba de carga: 60 estudiantes simultáneos, 4.320 peticiones en 10 s, 0 errores, latencia
  mediana 139 ms.
- Recorrido completo en navegador (escritorio y celular): inscripción, misiones, gráficos, entrega,
  panel docente, tablero, podio y revisión.

## Modificar preguntas

1. Editar `../4_Codigo_y_datos/scripts/construir_banco.py` (cada expediente es una función).
2. Doble clic en `../4_Codigo_y_datos/REGENERAR_TODO.bat` → valida que todo sume 1.000 puntos, que cada clave coincida con los datos y regenera la clave de respuestas.
3. `python pruebas/simulacro.py` → confirma que todo sigue funcionando.
4. Reiniciar el servidor. **No cambiar el banco con un reto en curso.**

## Reloj global (nuevo)
Por defecto el reloj es **global**: arranca cuando el docente pulsa «Abrir el reto» y termina a la misma hora para todos
los estudiantes, sin importar desde qué sitio o dispositivo se conecten (el tiempo lo cuenta el servidor, no el dispositivo).
Quien pulse «Comenzar» tarde tiene menos tiempo; si ya se acabó el tiempo general, no puede comenzar.
En el panel docente → Configuración se puede apagar «Reloj global» para volver a un reloj individual desde «Comenzar»
(solo se puede cambiar antes de abrir el reto). Internamente: opción `reloj_global` en la tabla `config`.
