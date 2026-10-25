"""
Escribe la clave de respuestas del reto (3_Guia_docente/CLAVE_DE_RESPUESTAS.md) leyendo
directamente banco_preguntas.json: es exactamente lo que califica la aplicación.

    python generar_clave_respuestas.py
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BANCO = RAIZ / "2_Aplicacion_Reto" / "banco_preguntas.json"
SALIDA = RAIZ / "3_Guia_docente" / "CLAVE_DE_RESPUESTAS.md"


def num(v):
    s = f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else f"{v:,}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def respuesta(q, c):
    t, r = q["tipo"], c.get("respuesta")
    if r is None:
        return ["*Sin respuesta correcta (no da puntos).*"]
    if t == "opcion":
        return [f"**{next(o['texto'] for o in c['opciones'] if o['id'] == r)}**"]
    if t == "multiple":
        return [f"- **{o['texto']}**" for o in c["opciones"] if o["id"] in r]
    if t == "clasificar":
        cats = {k["id"]: k["texto"] for k in q["categorias"]}
        return [f"- {i['texto']} → **{cats[r[i['id']]]}**" for i in c["items"]]
    if t == "ordenar":
        txt = {i["id"]: i["texto"] for i in c["items"]}
        return [f"{n}. {txt[x]}" for n, x in enumerate(r, 1)]
    if t == "construir":
        return [
            f"- *{p['etiqueta']}:* **{next(o['texto'] for o in p['opciones'] if o['id'] == r[p['id']])}**"
            for p in c["partes"]
        ]
    if t in ("numero", "estimar"):
        tol = q.get("tolerancia", 0)
        extra = (
            f" (se acepta ± {num(tol)}; "
            + ("puntaje según cercanía)" if t == "estimar" else "media nota hasta ± " + num(3 * tol) + ")")
            if tol
            else " (exacto)"
        )
        return [f"**{num(r)} {q.get('unidad', '')}**{extra}"]
    return [str(r)]


def main():
    banco = json.loads(BANCO.read_text(encoding="utf-8"))
    out = [
        f"# Clave de respuestas — {banco['titulo']}",
        "",
        f"Generada automáticamente desde `banco_preguntas.json` (versión **{banco.get('version')}**). Es exactamente "
        "lo que califica la aplicación. Si se modifica el banco, vuelve a generar este archivo.",
        "",
        "> Guarda este documento: contiene todas las respuestas. No lo compartas con los estudiantes antes del reto.",
        "",
    ]
    for i, m in enumerate(banco["misiones"], 1):
        pts = sum(q["puntos"] for q in m["preguntas"])
        out += [f"## Exp. {i:02d} · {m['titulo']} — {pts} puntos", "", f"*{m.get('intro', '')}*", ""]
        for j, q in enumerate(m["preguntas"], 1):
            extra = " · solo grupo B" if q.get("solo_grupo") else ""
            out += [f"### {j}. ({q['puntos']} pts · {q['tipo']}{extra})", ""]
            variantes = q.get("variantes")
            for k, v in enumerate(variantes or [q], 1):
                c = {**q, **v}
                if variantes:
                    out += [f"**Versión {k} de {len(variantes)}**", ""]
                out += [c["enunciado"], "", "Respuesta:", ""] + respuesta(q, c) + [""]
                if c.get("explicacion"):
                    out += [f"> {c['explicacion']}", ""]
    SALIDA.write_text("\n".join(out), encoding="utf-8")
    print(f"[ok] clave escrita en {SALIDA}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
