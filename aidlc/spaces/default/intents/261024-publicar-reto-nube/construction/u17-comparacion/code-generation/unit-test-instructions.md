# Instrucciones de pruebas — U17

U17 es una unidad de documentación (tipo `spec`): no agrega código ni pruebas nuevas. Sus pruebas son
comprobaciones estructurales que cualquiera repite. Todas usan Python 3.12 sin paquetes.

## Antes de empezar (Paso 1 del plan)

- Existen las dos mediciones de Cloudflare (ADR-C5):
  `ls despliegues/prueba_comun/mediciones/cloudflare_*.json despliegues/prueba_comun/mediciones/cloudflare-dev_*.json`
- Cada una tiene esquema 1 y «TODO BIEN» (desde la raíz del repo):
  `python3 -c "import json,sys; [print(f, (d:=json.load(open(f)))['version_esquema'], d['todo_bien']) for f in sys.argv[1:]]" despliegues/prueba_comun/mediciones/cloudflare*.json`
  Se toma la de fecha mayor de cada corrida. Si una falta o dice `False`, U17 se detiene (BR17.8).

## La tabla (pasos 8 y 16)

- Suite de la herramienta, desde `despliegues/prueba_comun/herramientas/`:
  `python3 -m unittest -v test_revisar_comparacion`
- Cada columna, desde la raíz del repo; las cinco terminan en «TODO BIEN»:
  `python3 despliegues/prueba_comun/herramientas/revisar_comparacion.py --opcion cloudflare`
  y lo mismo con `render`, `"cloudflare containers"`, `"apps script"` y `"github pages"`.
- La herramienta exige, en cada casilla con cifra, una URL `https://` o algo entre comillas invertidas.
  Por eso el archivo de medición va entre comillas invertidas (`cloudflare_<fecha>.json`).
- Lee toda línea que empieza con `|`. Por eso la tabla «Veredicto por NFR» usa la primera columna
  «Criterio» y las mismas cinco columnas en el mismo orden; los demás bloques van como listas.
- Revisión a mano: cada cifra de la columna Cloudflare coincide con el JSON citado.

## Las guías (Paso 14)

- Frases de 30 palabras o menos en `PUBLICAR_EN_INTERNET.md` (sin salida = bien):
  `python3 -c "import re,sys; t=re.sub(r'\`[^\`]*\`','X',open(sys.argv[1]).read()); [print(len(f.split()), f.strip()[:60]) for f in re.split(r'[.?!]\s', t) if len(f.split())>30]" PUBLICAR_EN_INTERNET.md`
- Sin claves ni datos (U17-S1); solo pasan menciones genéricas y `UNACLAVEDEPRUEBA` de ejemplo:
  `grep -n -i -E "clave|token|KQMT-|\?clave=" despliegues/COMPARACION.md PUBLICAR_EN_INTERNET.md despliegues/cloudflare/LEEME.md aidlc/spaces/default/intents/261024-publicar-reto-nube/construction/u17-comparacion/decisions.md`
- Restos de la versión de varias salas (sin salida = bien):
  `grep -n -E "CLAVE_SEMILLERO|\?sala=|clave del semillero|clave de (la )?sala" PUBLICAR_EN_INTERNET.md`
  En `despliegues/cloudflare/LEEME.md` solo puede quedar `CLAVE_SEMILLERO` en el paso único
  `secret delete`.
- Fin de línea: `git check-attr eol -- despliegues/cloudflare/herramientas/copiar.sh despliegues/cloudflare/herramientas/cambios_web.patch` dice `eol: lf`.
- Pruebas de personas, anotadas con nombre y fecha en la casilla NFR7:
  - alguien del semillero que no diseñó la guía la lee y la entiende (FR8.1);
  - alguien sigue el `LEEME.md` en Windows con Git Bash, y `copiar.sh` y `verificar.sh` corren sin error.

## Siempre, antes de cada push

- `python3 pruebas/simulacro.py 40`, desde `2_Aplicacion_Reto/`, en «TODO BIEN».
- `git diff --stat c87c80d HEAD -- 2_Aplicacion_Reto/` sale vacío (FR12.1).
- Ganchos de pre-commit en verde.
- La prueba común contra Cloudflare no se repite: U17 no cambia su código, solo su `LEEME.md`.

## Cobertura

No aplica a U17: no escribe código. NFR12 se evalúa sobre Cloudflare con
`node --test --experimental-test-coverage` nombrando cada archivo de `despliegues/cloudflare/pruebas/`
(`project.md`, «Corrections»), y la cifra va en su casilla.
