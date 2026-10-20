"""
Simulacro completo del reto con estudiantes ficticios.

Arranca el servidor en un puerto aparte y con una base de datos TEMPORAL (no toca
datos/reto.db), inscribe N estudiantes, los hace responder con distintos niveles
de acierto y verifica que:

  1. las respuestas correctas no salen del servidor antes de publicar resultados;
  2. una pregunta no se puede responder dos veces y se respeta el orden de la Misión 1;
  3. solo el grupo B ve el «recordatorio de exactitud»;
  4. el tiempo se vence solo y entrega el intento;
  5. la calificación es correcta en casos conocidos (todo bien = 1000, todo mal = 0);
  6. la clasificación es un orden total: puestos 1..N sin repetir;
  7. el experimento de clase, las exportaciones CSV y el reinicio funcionan.

    python pruebas/simulacro.py          (40 estudiantes)
    python pruebas/simulacro.py 80
"""
import json
import random
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
PUERTO = 8765
BASE = f"http://127.0.0.1:{PUERTO}"
CLAVE = "SIMULA"
FALLAS = []


def pedir(ruta, datos=None, token=None, admin=False, crudo=False):
    cab = {"Content-Type": "application/json"}
    if token:
        cab["Authorization"] = f"Bearer {token}"
    if admin:
        cab["X-Clave-Admin"] = CLAVE
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    req = urllib.request.Request(BASE + ruta, data=cuerpo, headers=cab, method="POST" if datos is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            texto = r.read().decode("utf-8")
            return (r.status, texto) if crudo else (r.status, json.loads(texto))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def comprobar(condicion, mensaje):
    print(("  ✔ " if condicion else "  ✘ ") + mensaje)
    if not condicion:
        FALLAS.append(mensaje)


def respuesta_para(q, cuerpo, acertar):
    """Construye una respuesta correcta (acertar=True) o incorrecta para la pregunta resuelta."""
    t, ok = q["tipo"], cuerpo.get("respuesta")
    if t in ("compartir", "recordatorio"):
        cats = [c["id"] for c in q["categorias"]]
        return {p["id"]: random.choice(cats) for p in cuerpo["publicaciones"]}
    if t == "opcion":
        if ok is None:  # hipótesis sin clave
            return cuerpo["opciones"][0]["id"]
        return ok if acertar else next(o["id"] for o in cuerpo["opciones"] if o["id"] != ok)
    if t == "multiple":
        return list(ok) if acertar else [o["id"] for o in cuerpo["opciones"] if o["id"] not in ok][:1]
    if t == "clasificar":
        cats = [c["id"] for c in q["categorias"]]
        return {k: (v if acertar else next(c for c in cats if c != v)) for k, v in ok.items()}
    if t == "ordenar":
        return list(ok) if acertar else list(reversed(ok))
    if t == "construir":
        return {k: (v if acertar else next(o["id"] for pt in cuerpo["partes"] if pt["id"] == k
                                           for o in pt["opciones"] if o["id"] != v)) for k, v in ok.items()}
    if t == "texto":
        return "Mi conclusión: las elecciones cambian la agenda del verificador (gráfico B), no el volumen (A)."
    if t == "estimar":
        if ok is None:  # hipótesis sin clave
            return (q["min"] + q["max"]) / 2
        if acertar:
            return ok
        lejos = ok + q["tolerancia"]
        return lejos if lejos <= q["max"] else ok - q["tolerancia"]
    if t == "numero":
        return str(ok).replace(".", ",") if acertar else ok + 1000
    raise ValueError(t)


def main(n_estudiantes):
    import servidor as S  # mismo banco y misma lógica de variantes que el servidor

    tmp = Path(tempfile.mkdtemp(prefix="simulacro_reto_"))
    db = tmp / "simulacro.db"
    proc = subprocess.Popen([sys.executable, str(APP / "servidor.py"), "--puerto", str(PUERTO), "--clave", CLAVE,
                             "--db", str(db)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + "/api/publico", timeout=1)
                break
            except OSError:
                time.sleep(0.2)
        print(f"Simulacro con {n_estudiantes} estudiantes · base temporal {db}")
        _, pub = pedir("/api/publico")
        sala = pub["sala"]

        print("\n1) Inscripción")
        st, r = pedir("/api/registro", {"nombre": "Prueba", "colegio": "X", "grado": "10", "sala": "ZZZZ"})
        comprobar(st == 400, "rechaza un código de sala incorrecto")
        st, r = pedir("/api/registro", {"nombre": "Prueba", "colegio": "X", "grado": "8", "sala": sala})
        comprobar(st == 400, "rechaza grados distintos de 9, 10 y 11")
        estudiantes = []
        for i in range(n_estudiantes):
            grado = random.choice("9 10 11".split())
            st, r = pedir("/api/registro", {"nombre": f"Estudiante {i:02d}", "colegio": "Colegio Simulado",
                                            "grado": grado, "sala": sala})
            assert st == 200, r
            estudiantes.append({**r, "grado": grado, "nivel": i / max(1, n_estudiantes - 1)})
        comprobar(len({e["codigo"] for e in estudiantes}) == n_estudiantes, "códigos únicos para todos")
        st, r = pedir("/api/registro", {"nombre": "estudiante 00", "colegio": "colegio simulado",
                                        "grado": estudiantes[0]["grado"], "sala": sala})
        comprobar(st == 400, "no deja inscribir dos veces el mismo nombre, colegio y grado")
        st, r = pedir("/api/entrar", {"codigo": estudiantes[0]["codigo"].lower()})
        comprobar(st == 200 and r["token"] == estudiantes[0]["token"], "entrar de nuevo con el código recupera la sesión")

        st, r = pedir("/api/comenzar", {}, token=estudiantes[0]["token"])
        comprobar(st == 400, "no se puede empezar antes de que el docente abra el reto")
        st, _ = pedir("/api/admin/estado", {"estado": "abierto"})
        comprobar(st == 403, "el panel docente exige la clave")
        pedir("/api/admin/estado", {"estado": "abierto"}, admin=True)

        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        filas = {f["token"]: dict(f) for f in con.execute("SELECT * FROM participantes")}

        print("\n2) Respuestas")
        texto_estado = ""
        for k, e in enumerate(estudiantes):
            tok = e["token"]
            pedir("/api/comenzar", {}, token=tok)
            st, est = pedir("/api/estado", token=tok)
            texto_estado += json.dumps(est["misiones"]) + ("REVISION" if "revision" in est else "")
            p = filas[tok]
            ids_vistos = {q["id"] for m in est["misiones"] for q in m["preguntas"]}
            if k < 2:
                comprobar(("m1_recordatorio" in ids_vistos) == (p["grupo"] == "B"),
                          f"grupo {p['grupo']}: recordatorio {'visible' if p['grupo'] == 'B' else 'oculto'}")
            if k == 0:
                st, r = pedir("/api/responder", {"pregunta": "m1_veracidad", "respuesta": {}}, token=tok)
                comprobar(st == 400, "la fase «¿es verdad?» exige responder antes «¿lo compartirías?»")
            for m in est["misiones"]:
                for qpub in m["preguntas"]:
                    _, q = S.PREGUNTAS[qpub["id"]]
                    _, cuerpo = S.resolver(p, q)
                    if k == 0:
                        acertar = True
                    elif k == 1:
                        acertar = False
                    else:
                        acertar = random.random() < 0.25 + 0.7 * e["nivel"]
                    st, r = pedir("/api/responder", {"pregunta": q["id"], "respuesta":
                                                     respuesta_para(q, cuerpo, acertar)}, token=tok)
                    assert st == 200, (q["id"], r)
            if k == 0:
                st, r = pedir("/api/responder", {"pregunta": "m3_sesgo", "respuesta": "a"}, token=tok)
                comprobar(st == 400, "una pregunta no se puede responder dos veces")
            if k < n_estudiantes - 3:
                time.sleep(random.uniform(0, 0.05))
                pedir("/api/finalizar", {}, token=tok)
        comprobar(all(k not in texto_estado for k in ('"respuesta"', '"explicacion"', '"tolerancia"', "REVISION")),
                  "el navegador nunca recibe respuestas correctas ni explicaciones durante el reto")

        print("\n2b) Reloj global")
        inicios = {r[0] for r in con.execute("SELECT inicio FROM participantes WHERE inicio IS NOT NULL")}
        abierto_en = float(con.execute("SELECT valor FROM config WHERE clave='abierto_en'").fetchone()[0])
        comprobar(inicios == {abierto_en}, "reloj global: todos los intentos comparten la misma hora de inicio (la de abrir el reto)")
        st, r = pedir("/api/registro", {"nombre": "Llegó tarde", "colegio": "Colegio Simulado", "grado": "10", "sala": sala})
        tarde = r
        con.execute("UPDATE config SET valor=? WHERE clave='abierto_en'", (str(abierto_en - 6000),))
        con.commit()
        st, r = pedir("/api/comenzar", {}, token=tarde["token"])
        comprobar(st == 400, "reloj global: no se puede comenzar cuando el tiempo general ya terminó")
        con.execute("UPDATE config SET valor=? WHERE clave='abierto_en'", (str(abierto_en),))
        con.commit()
        fila_tarde = con.execute("SELECT id FROM participantes WHERE token=?", (tarde["token"],)).fetchone()
        pedir("/api/admin/participante", {"id": fila_tarde["id"], "accion": "eliminar"}, admin=True)
        st, _ = pedir("/api/admin/config", {"reloj_global": False}, admin=True)
        comprobar(st == 400, "el tipo de reloj no se puede cambiar con el reto abierto")

        print("\n3) Tiempo")
        ultimos = [e["token"] for e in estudiantes[-3:]]
        con.execute(f"UPDATE participantes SET inicio = inicio - 6000 WHERE token IN ({','.join('?' * 3)})", ultimos)
        con.commit()
        st, est = pedir("/api/estado", token=ultimos[0])
        comprobar(est["participante"]["estado"] == "finalizado", "al vencerse los 90 min el intento se entrega solo")
        st, r = pedir("/api/responder", {"pregunta": "m3_sesgo", "respuesta": "a"}, token=ultimos[1])
        comprobar(st == 400, "no se aceptan respuestas fuera de tiempo")

        print("\n4) Calificación")
        _, adm = pedir("/api/admin/resumen", admin=True)
        por_codigo = {f["codigo"]: f for f in adm["participantes"]}
        perfecto, cero = por_codigo[estudiantes[0]["codigo"]], por_codigo[estudiantes[1]["codigo"]]
        comprobar(abs(perfecto["puntos"] - 1000) < 1e-6, f"todo correcto = 1000 puntos (obtuvo {perfecto['puntos']})")
        comprobar(cero["puntos"] < 1e-6, f"todo incorrecto = 0 puntos (obtuvo {cero['puntos']})")
        comprobar(0 < perfecto["bono"] <= 20, f"bono de tiempo entre 0 y 20 (obtuvo {perfecto['bono']})")
        vencidos = [por_codigo[e["codigo"]] for e in estudiantes[-3:]]
        comprobar(all(v["bono"] == 0 for v in vencidos), "quien responde su última pregunta al final del tiempo no recibe bono")

        print("\n5) Clasificación")
        pedir("/api/admin/estado", {"estado": "resultados"}, admin=True)
        _, adm = pedir("/api/admin/resumen", admin=True)
        puestos = sorted(f["puesto"] for f in adm["participantes"] if f["puesto"])
        comprobar(puestos == list(range(1, n_estudiantes + 1)), f"puestos 1..{n_estudiantes} sin repetir")
        orden = sorted((f for f in adm["participantes"] if f["puesto"]), key=lambda f: f["puesto"])
        comprobar(all(a["total"] >= b["total"] for a, b in zip(orden, orden[1:])), "ordenados por puntaje total")
        totales = [f["total"] for f in orden]
        print(f"     puntajes distintos: {len(set(totales))} de {len(totales)} · podio: "
              + ", ".join(f"{f['puesto']}.º {f['nombre']} {f['total']:.2f}" for f in orden[:3]))

        print("\n6) Revisión, experimento y exportaciones")
        st, est = pedir("/api/estado", token=estudiantes[5]["token"])
        comprobar("revision" in est and est["participante"].get("puesto"), "con resultados publicados hay revisión y puesto")
        _, pub = pedir("/api/publico")
        exp = pub.get("experimento", {})
        comprobar(exp.get("listo") and exp["n"] == n_estudiantes, "el experimento de clase usa a todos los participantes")
        comprobar(len(pub.get("ranking", [])) == min(10, n_estudiantes), "el tablero muestra el top 10")
        st, csv1 = pedir("/api/admin/resultados.csv", admin=True, crudo=True)
        comprobar(st == 200 and csv1.count("\n") == n_estudiantes + 1, "CSV de resultados con una fila por participante")
        st, csv2 = pedir("/api/admin/respuestas.csv", admin=True, crudo=True)
        comprobar(st == 200 and csv2.count("\n") > n_estudiantes * 30, "CSV con el detalle de cada respuesta")

        print("\n7) Reinicio")
        st, r = pedir("/api/admin/reiniciar", {"confirmar": "no"}, admin=True)
        comprobar(st == 400, "el reinicio exige escribir BORRAR")
        st, r = pedir("/api/admin/reiniciar", {"confirmar": "BORRAR"}, admin=True)
        _, pub = pedir("/api/publico")
        comprobar(st == 200 and pub["conteo"]["inscritos"] == 0 and (tmp / r["copia"]).exists(),
                  "reiniciar deja copia de seguridad y empieza de cero")
        con.close()
    finally:
        proc.terminate()
        proc.wait(5)
        err = proc.stderr.read().decode("utf-8", "replace").strip()
        if err:
            print("\n[stderr del servidor]\n" + err)

    print("\n" + ("TODO BIEN: el reto está listo." if not FALLAS else f"{len(FALLAS)} comprobación(es) fallaron:"))
    for f in FALLAS:
        print("  -", f)
    return 1 if FALLAS else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    random.seed(7)
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 40))
