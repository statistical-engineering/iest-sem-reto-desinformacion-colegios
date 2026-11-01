# Instrucciones de pruebas — U4

> **Revisión 2026-10-27 (una sola sala).** Comandos para las reglas de un solo reto con reloj por colegio.

- Marco: `node:test` de Node 24 (24.21.0 en la máquina de desarrollo), sin paquetes (ADR-W2). Generador: Python
  3.12 con `unittest`. Todo se corre desde la raíz del repositorio.
- `node --test` con una carpeta falla en Node 24: siempre se nombra cada archivo (`project.md`, «Corrections»).

## Un archivo

```bash
node --test despliegues/cloudflare/pruebas/comun.test.js
node --test despliegues/cloudflare/pruebas/banco.test.js
node --test despliegues/cloudflare/pruebas/calificacion.test.js
node --test despliegues/cloudflare/pruebas/clasificacion.test.js
node --test despliegues/cloudflare/pruebas/ciclo_del_reto.test.js
node --test despliegues/cloudflare/pruebas/limpieza_entrada.test.js
node --test despliegues/cloudflare/pruebas/experimento.test.js
node --test despliegues/cloudflare/pruebas/casos_reglas.test.js
node --test despliegues/cloudflare/pruebas/reglas.test.js
```

`reglas.test.js` son las 23 pruebas de U1: pasan sin cambios y prueban que la fachada conserva cada nombre.

## Toda la unidad, con cobertura

```bash
node --test --experimental-test-coverage \
  --test-coverage-include='despliegues/cloudflare/src/reglas/**' \
  --test-coverage-lines=80 \
  despliegues/cloudflare/pruebas/*.test.js
```

Bash expande `*.test.js` a la lista de archivos, así que Node recibe nombres y no una carpeta. Termina con error
si la cobertura de líneas de `src/reglas/**` baja de 80 % (NFR12, U4-O3).

## Tabla de casos

```bash
python3 despliegues/prueba_comun/herramientas/generar_casos.py
python3 -m unittest discover -s despliegues/prueba_comun/herramientas -p 'test_generar_casos.py'
bash despliegues/cloudflare/herramientas/copiar.sh
sha256sum despliegues/prueba_comun/casos_reglas.json despliegues/cloudflare/pruebas/casos_reglas.json
uv run ruff format --check despliegues/prueba_comun/herramientas/
uv run ruff check despliegues/prueba_comun/herramientas/
```

- El generador solo se corre cuando cambia él mismo o `banco_prueba.json`; el JSON resultante se versiona.
- Las dos huellas de `sha256sum` deben ser iguales; si no, `verificar.sh` se detiene.
- Si una fila falla en `casos_reglas.test.js`, se corrige la regla en JS, nunca la tabla a mano.

## Comprobaciones de revisión

```bash
grep -rnE 'Date|Math\.random|getRandomValues|env\.|console\.' despliegues/cloudflare/src/reglas/
awk 'length > 120 {print FILENAME": "FNR}' despliegues/cloudflare/src/reglas/*.js
```

Las dos deben salir vacías. La complejidad ciclomática ≤ 10 se revisa a mano (`team.md`, «Code Style»).

## Verificación de la unidad

```bash
bash despliegues/cloudflare/herramientas/verificar.sh
(cd 2_Aplicacion_Reto && python3 pruebas/simulacro.py 40)
git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/
```

`verificar.sh` termina con código 0; el simulacro dice «TODO BIEN»; el `git diff` sale vacío (FR12.1).

- Sin *mocks* en las reglas: reciben datos y la hora. Datos de prueba: preguntas armadas en cada prueba y
  `banco_prueba.json` (inventado). El banco real (`src/banco.json`) solo se usa para estructura y para comprobar
  que ninguna clave secreta sale; nunca se copian sus respuestas a una prueba.
