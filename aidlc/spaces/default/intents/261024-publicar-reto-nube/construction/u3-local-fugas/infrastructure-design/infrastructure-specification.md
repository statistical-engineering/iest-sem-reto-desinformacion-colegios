# Infraestructura — U3 `u3-local-fugas`

Sale de `../nfr-design/` y de `../decisions.md`. U3 no agrega ninguna pieza: corre en los tres modos de
hoy de la versión local (`team.md`, «Deployment»: red local, túnel temporal y modo prueba), que no cambian
(FR5.4).

## Piezas

| Pieza | Configuración | Cambio de U3 |
|---|---|---|
| `servidor.py` | Python 3.9+, puerto 8000 o `$PORT`, datos en `datos/` o `$RETO_DATOS` | Seis funciones nuevas y cuatro líneas tocadas |
| `datos/reto.db` | SQLite, esquema de `conectar` | Ninguno |
| Lanzadores `INICIAR_RETO`, `INICIAR_RETO_INTERNET`, `PROBAR_ANTES_DEL_RETO` (`.bat` y `.command`) | Los de hoy | Ninguno |
| `modo_prueba.py` | Puerto 8010, `datos_prueba/` | Ninguno |
| `pruebas/test_servidor.py` | `unittest` | Nuevo |

## Cómo llega al docente

1. El semillero lleva el cambio a `develop` (el humano y el asistente suben directo; los demás por PR).
2. El docente actualiza su copia del repositorio solo con la sala en «inscripción» sin participantes o
   en «resultados», nunca con un reto en curso (`project.md`, «Forbidden»), y reinicia el servidor
   (`project.md`, «Mandated»).
3. Antes del reto corre `PROBAR_ANTES_DEL_RETO`, que ejecuta `simulacro.py` y debe decir «TODO BIEN».

## Volver atrás

Volver al commit anterior de `2_Aplicacion_Reto/` y reiniciar el servidor. La base no cambia de esquema,
así que no hay nada que migrar en ningún sentido (U3-R2, U3-R5).

## Comprobación de FR12.1 después de U3

`git diff --stat <último commit de U3> HEAD -- 2_Aplicacion_Reto/` debe salir vacío en todo commit
posterior (`unit-of-work.md`, «Cómo se trabaja»).
