# Pila tecnológica

No hay archivo de dependencias (`requirements.txt`, `pyproject.toml`, `package.json`): las versiones
salen del código, del `Dockerfile` y de la documentación.

## Lenguajes y entornos

| Tecnología | Versión | Dónde | Evidencia |
|---|---|---|---|
| Python | 3.9 o superior (declarado); 3.12 en la imagen | App y scripts | Docstring de `servidor.py`, `Dockerfile` (`python:3.12-slim`), chequeo `sys.version_info[:2] >= (3, 9)` en `INICIAR_RETO_INTERNET.bat` |
| JavaScript (navegador, ES2017+) | Sin transpilación | `web/js/*.js`, `tablero.html` | `async`/`await`, `const`, plantillas, `Object.fromEntries`, `replaceChildren` |
| HTML5 + CSS3 | — | `web/*.html`, `web/css/reto.css` | Variables CSS, grid, `prefers-reduced-motion` |
| SQL (dialecto SQLite) | SQLite ≥ 3.27 | `servidor.py` | UPSERT `ON CONFLICT … DO UPDATE` (≥ 3.24), `VACUUM INTO` (≥ 3.27), `PRAGMA journal_mode=WAL` |
| Batch de Windows / bash | — | Lanzadores `.bat` y `.command` | |

## Biblioteca estándar de Python usada por la app

| Módulo | Uso |
|---|---|
| `http.server` (`ThreadingHTTPServer`, `BaseHTTPRequestHandler`) | Servidor HTTP/1.1 con un hilo por conexión |
| `sqlite3` | Persistencia |
| `threading` | `RLock` global e hilo vigilante |
| `secrets`, `hashlib`, `random` | Tokens, códigos, clave docente, semillas y barajado determinista |
| `json`, `csv`, `io` | API y exportaciones |
| `socket` | Doble pila IPv6/IPv4 e IP locales |
| `argparse`, `os`, `pathlib`, `re`, `time`, `sys`, `urllib.parse` | Arranque, rutas, normalización, reloj |
| `urllib.request`, `subprocess`, `tempfile`, `tarfile`, `platform`, `shutil`, `webbrowser`, `ctypes` | Solo en `simulacro.py`, `modo_prueba.py`, `iniciar_internet.py` |

## Bibliotecas de terceros

| Biblioteca | Versión | Dónde | Notas |
|---|---|---|---|
| pandas | No fijada | `generar_analisis.py`, `construir_banco.py` | No instalada en la máquina del autor (`CLAUDE.md`); la regeneración no se verificó allí |
| numpy | No fijada | `generar_analisis.py`, `estilo_graficos.py` | |
| matplotlib | No fijada (backend `Agg`) | `generar_analisis.py`, `estilo_graficos.py` | |

La aplicación (`2_Aplicacion_Reto/`) **no** usa bibliotecas de terceros, ni en Python ni en JS.

## Servicios y herramientas externas

| Servicio | Uso | Obligatorio |
|---|---|---|
| Google Fonts (Lexend, Bricolage Grotesque, Special Elite) | Tipografías de las tres páginas | No: hay tipografías de respaldo (`GUIA_DOCENTE.md` §11) |
| cloudflared (Cloudflare Quick Tunnel, `trycloudflare.com`) | Enlace HTTPS temporal | Solo en modo internet temporal; se descarga de GitHub Releases (`latest`) o se instala con Homebrew |
| Render (servicio web Docker + disco persistente) | Hosting con enlace fijo | Solo en modo publicado |
| GitHub / GitHub Desktop | Repositorio privado y origen del Blueprint | Solo para publicar |

## Infraestructura de ejecución

| Modo | Proceso | Persistencia | HTTPS |
|---|---|---|---|
| Red local | `python servidor.py` en el computador del docente, puerto 8000 | `2_Aplicacion_Reto/datos/reto.db` | No (HTTP en la LAN) |
| Túnel temporal | `iniciar_internet.py` = `cloudflared` + `servidor.py` | Igual que red local | Sí, en el borde de Cloudflare |
| Render | Contenedor `python:3.12-slim`, `CMD python servidor.py`, puerto `$PORT` | Disco de 1 GB en `/data` | Sí, en el proxy de Render |
| Simulacro | `servidor.py` en el puerto 8765 | BD temporal en `tempfile.mkdtemp()` | No |
| Modo prueba | `servidor.py` en el puerto 8010 | `2_Aplicacion_Reto/datos_prueba/` | No |

## Herramientas de calidad

| Tipo | Estado |
|---|---|
| Formateador | Ninguno configurado |
| Linter | Ninguno configurado; directivas `# noqa` sugieren flake8/ruff en algún momento |
| Tipos | Sin anotaciones; sin mypy |
| Pruebas | `pruebas/simulacro.py` (script propio); `unittest` aprobado para pruebas nuevas, `pytest` no aprobado (`aidlc/spaces/default/memory/project.md`) |
| CI | No hay |
