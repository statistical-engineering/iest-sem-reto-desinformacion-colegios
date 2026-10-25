"""
Servidor del reto «Detectives de la desinformación».

Solo usa la biblioteca estándar de Python (3.9 o superior): no hay que instalar nada.

    python servidor.py                 # puerto 8000
    python servidor.py --puerto 8080
    python servidor.py --clave MICLAVE # fija la clave del panel docente

Al arrancar imprime las direcciones para estudiantes (/), tablero (/tablero) y
panel docente (/admin). Todo se guarda en datos/reto.db (SQLite): si el computador
se apaga, al volver a arrancar el reto continúa donde iba.

Reglas que hace cumplir el servidor (no el navegador):
  * las respuestas correctas nunca salen del servidor hasta publicar resultados;
  * cada pregunta se responde una sola vez;
  * el tiempo (90 min por defecto) lo mide el servidor; al vencerse, se entrega solo;
  * la clasificación es un orden total: nunca hay dos participantes en el mismo puesto.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import random
import re
import secrets
import socket
import sqlite3
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

AQUI = Path(__file__).resolve().parent
WEB = AQUI / "web"
DATOS = (
    Path(os.environ["RETO_DATOS"]).resolve() if os.environ.get("RETO_DATOS") else AQUI / "datos"
)  # en un hosting: el disco persistente
BANCO_PATH = AQUI / "banco_preguntas.json"
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para evitar confusiones
ESTADOS = ("inscripcion", "abierto", "cerrado", "resultados")

BANCO = json.loads(BANCO_PATH.read_text(encoding="utf-8"))
PREGUNTAS = {q["id"]: (m, q) for m in BANCO["misiones"] for q in m["preguntas"]}
PUNTOS_TOTALES = BANCO["puntos_totales"]
BONO_MAX = BANCO["bono_tiempo_max"]

LOCK = threading.RLock()
DB = None
CLAVE_ADMIN = ""
URLS = []
RUTA_DB = DATOS / "reto.db"


# =========================================================================== base de datos
def conectar(ruta):
    con = sqlite3.connect(ruta, check_same_thread=False, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS config (clave TEXT PRIMARY KEY, valor TEXT);
    CREATE TABLE IF NOT EXISTS participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE, token TEXT UNIQUE,
        nombre TEXT, colegio TEXT, grado TEXT, integrantes TEXT, grupo TEXT, semilla TEXT,
        creado REAL, inicio REAL, fin REAL, estado TEXT, motivo_fin TEXT,
        puntos REAL DEFAULT 0, bono REAL DEFAULT 0, total REAL DEFAULT 0, tiempo_usado REAL,
        tiempo_respuestas REAL, salidas INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS respuestas (
        participante_id INTEGER, pregunta_id TEXT, variante INTEGER, respuesta TEXT,
        fraccion REAL, puntos REAL, max_puntos REAL, momento REAL,
        PRIMARY KEY (participante_id, pregunta_id));
    CREATE TABLE IF NOT EXISTS eventos (participante_id INTEGER, tipo TEXT, momento REAL);
    """)
    return con


def cfg(clave, defecto=None):
    fila = DB.execute("SELECT valor FROM config WHERE clave=?", (clave,)).fetchone()
    return fila["valor"] if fila else defecto


def set_cfg(clave, valor):
    DB.execute(
        "INSERT INTO config(clave, valor) VALUES(?, ?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor",
        (clave, str(valor)),
    )


def inicializar_config():
    defaults = {
        "estado": "inscripcion",
        "sala": "".join(secrets.choice(ALFABETO[:24]) for _ in range(4)),
        "modo_sorpresa": "1",
        "retro": "1",
        "duracion_min": str(BANCO["duracion_min"]),
        "evento": "Sala de verificación",
        "reloj_global": "1",
    }
    for k, v in defaults.items():
        if cfg(k) is None:
            set_cfg(k, v)


def duracion_seg():
    return float(cfg("duracion_min", BANCO["duracion_min"])) * 60


# =========================================================================== examen por participante
def rng_para(semilla, clave):
    return random.Random(hashlib.sha256(f"{semilla}|{clave}".encode()).hexdigest())


def variante_de(p, q):
    if "variantes" not in q:
        return 0
    h = int(hashlib.sha256(f"{p['semilla']}|{q['id']}|var".encode()).hexdigest(), 16)
    return h % len(q["variantes"])


def resolver(p, q):
    """Pregunta completa (con respuesta) para este participante: variante elegida."""
    v = variante_de(p, q)
    cuerpo = {k: val for k, val in q.items() if k != "variantes"}
    if "variantes" in q:
        cuerpo.update(q["variantes"][v])
    return v, cuerpo


def visible_para(p, q):
    return q.get("solo_grupo") in (None, p["grupo"])


def version_publica(p, q):
    """Lo que ve el navegador: sin respuesta, sin explicación, con el orden barajado."""
    _, c = resolver(p, q)
    pub = {
        k: c[k]
        for k in (
            "id",
            "tipo",
            "enunciado",
            "puntos",
            "unidad",
            "min",
            "max",
            "paso",
            "grafico",
            "tabla",
            "categorias",
            "estilo",
            "requiere",
            "experimento",
            "entero",
            "max",
            "simulador",
        )
        if k in c
    }
    if "opciones" in c:
        ops = list(c["opciones"])
        rng_para(p["semilla"], q["id"]).shuffle(ops)
        pub["opciones"] = ops
    if "publicaciones" in c:
        pub["publicaciones"] = c["publicaciones"]
    if "items" in c:
        items = list(c["items"])
        clave = "m1_posts" if q["id"].startswith("m1_") else q["id"]
        r = rng_para(p["semilla"], clave)
        for _ in range(10):
            r.shuffle(items)
            if c["tipo"] != "ordenar" or [i["id"] for i in items] != c["respuesta"]:
                break
        pub["items"] = items
    if "partes" in c:
        r = rng_para(p["semilla"], q["id"] + "|partes")
        pub["partes"] = []
        for parte in c["partes"]:
            ops = list(parte["opciones"])
            r.shuffle(ops)
            pub["partes"].append({"id": parte["id"], "etiqueta": parte["etiqueta"], "opciones": ops})
    if q["id"] == "m1_compartir":  # mismo orden que la fase de veracidad
        pubs = list(c["publicaciones"])
        rng_para(p["semilla"], "m1_posts").shuffle(pubs)
        pub["publicaciones"] = pubs
    return pub


def examen_publico(p, respondidas=frozenset()):
    misiones = []
    for m in BANCO["misiones"]:
        qs = [version_publica(p, q) for q in m["preguntas"] if visible_para(p, q)]
        mm = {k: m[k] for k in ("id", "titulo", "subtitulo", "intro", "glosario", "lectura", "dossier") if k in m}
        dos = m.get("dossier")
        if dos and dos.get("revelar_tras") and dos["revelar_tras"] not in respondidas:
            # la evidencia no sale del servidor hasta que el estudiante registre su hipótesis
            mm["dossier"] = {"titulo": dos["titulo"], "bloqueado": True, "n": len(dos["graficos"])}
        mm["preguntas"] = qs
        mm["puntos"] = sum(q["puntos"] for q in qs)
        misiones.append(mm)
    return misiones


# =========================================================================== calificación
def a_numero(texto, entero=False):
    """Coma o punto como decimal (82,5 = 82.5). Con varios puntos, o punto y coma juntos, los puntos son de
    miles (1.234.567 · 1.234,5). En preguntas de respuesta entera, 1.023 o 1,023 se leen como mil veintitrés."""
    if isinstance(texto, (int, float)):
        return float(texto)
    s = re.sub(r"[^\d,.\-]", "", str(texto))
    if not s or not re.search(r"\d", s):
        raise ValueError("no es un número")
    if entero and re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", s):
        return float(re.sub(r"[.,]", "", s))
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(",") > 1 or s.count(".") > 1:
        s = s.replace(",", "").replace(".", "")
    else:
        s = s.replace(",", ".")
    return float(s)


def validar_respuesta(q, r):
    t = q["tipo"]
    if t == "opcion":
        assert isinstance(r, str) and r in {o["id"] for o in q["opciones"]}
        return r
    if t == "multiple":
        ids = {o["id"] for o in q["opciones"]}
        assert isinstance(r, list) and set(r) <= ids and len(set(r)) == len(r)
        return sorted(r)
    if t in ("clasificar", "compartir", "recordatorio"):
        items = {i["id"] for i in q.get("items") or q.get("publicaciones")}
        cats = {c["id"] for c in q["categorias"]}
        assert isinstance(r, dict) and set(r) == items and set(r.values()) <= cats
        return r
    if t == "ordenar":
        assert isinstance(r, list) and sorted(r) == sorted(i["id"] for i in q["items"])
        return r
    if t == "construir":
        partes = {pt["id"]: {o["id"] for o in pt["opciones"]} for pt in q["partes"]}
        assert isinstance(r, dict) and set(r) == set(partes) and all(r[k] in partes[k] for k in partes)
        return r
    if t == "texto":
        assert isinstance(r, str) and 0 < len(r.strip()) <= q.get("max", 700) + 50
        return r.strip()
    if t in ("estimar", "numero"):
        x = a_numero(r, q.get("entero", False))
        if t == "estimar":
            assert q["min"] <= x <= q["max"]
        return x
    raise AssertionError("tipo desconocido")


def fraccion(q, r):  # noqa: C901
    t = q["tipo"]
    ok = q.get("respuesta")
    if not q.get("puntos"):
        return 0.0  # hipótesis, informe y fases sin puntos
    if t in ("compartir", "recordatorio", "texto"):
        return 0.0
    if t == "construir":
        return sum(r.get(k) == v for k, v in ok.items()) / len(ok)
    if t == "opcion":
        return 1.0 if r == ok else 0.0
    if t == "multiple":
        sel, cor = set(r), set(ok)
        return max(0.0, (len(sel & cor) - len(sel - cor)) / len(cor))
    if t == "clasificar":
        return sum(r.get(i) == c for i, c in ok.items()) / len(ok)
    if t == "ordenar":
        pos = {x: i for i, x in enumerate(r)}
        pares = [(ok[i], ok[j]) for i in range(len(ok)) for j in range(i + 1, len(ok))]
        return sum(pos[a] < pos[b] for a, b in pares) / len(pares)
    if t == "estimar":
        return max(0.0, 1 - abs(r - ok) / q["tolerancia"])
    if t == "numero":
        err, tol = abs(r - ok), q.get("tolerancia", 0)
        if err <= tol + 1e-9:
            return 1.0
        if tol > 0 and err <= 3 * tol + 1e-9:
            return 0.5
        return 0.0
    return 0.0


# =========================================================================== participantes
def participante_por_token(token):
    if not token:
        return None
    return DB.execute("SELECT * FROM participantes WHERE token=?", (token,)).fetchone()


def recalcular_puntos(pid):
    s = DB.execute("SELECT COALESCE(SUM(puntos),0) s FROM respuestas WHERE participante_id=?", (pid,)).fetchone()["s"]
    DB.execute("UPDATE participantes SET puntos=?, total=?+bono WHERE id=?", (s, s, pid))
    return s


def finalizar(p, ahora, motivo):
    """Cierra el intento.

    El bono de tiempo se mide con el momento EXACTO de la última respuesta (no con la hora de entrega): así,
    quien termina a los 40 minutos y olvida pulsar «Entregar» no pierde el bono, y dos personas con los mismos
    aciertos casi nunca empatan. El bono es proporcional a lo acertado: responder rápido y mal no da bono.
    """
    if p["estado"] != "en_curso":
        return
    dur = duracion_seg()
    fin = min(ahora, p["inicio"] + dur)
    usado = max(0.0, fin - p["inicio"])
    ultima = DB.execute("SELECT MAX(momento) m FROM respuestas WHERE participante_id=?", (p["id"],)).fetchone()["m"]
    t_resp = min(dur, max(0.0, (ultima if ultima is not None else fin) - p["inicio"]))
    puntos = recalcular_puntos(p["id"])
    bono = BONO_MAX * (puntos / PUNTOS_TOTALES) * (1 - t_resp / dur)
    DB.execute(
        "UPDATE participantes SET estado='finalizado', fin=?, tiempo_usado=?, tiempo_respuestas=?, bono=?, "
        "total=?, motivo_fin=? WHERE id=?",
        (fin, usado, t_resp, bono, puntos + bono, motivo, p["id"]),
    )


def vencer_tiempos():
    ahora = time.time()
    for p in DB.execute("SELECT * FROM participantes WHERE estado='en_curso'").fetchall():
        if ahora >= p["inicio"] + duracion_seg():
            finalizar(p, ahora, "tiempo")


def clasificacion():
    """Orden total: puntaje total ↓, puntos ↓, momento de la última respuesta ↑, hora de entrega ↑, inscripción ↑."""
    filas = DB.execute("SELECT * FROM participantes WHERE estado='finalizado'").fetchall()
    filas = sorted(
        filas, key=lambda p: (-round(p["total"], 9), -round(p["puntos"], 9), p["tiempo_respuestas"], p["fin"], p["id"])
    )
    salida = []
    for i, p in enumerate(filas, 1):
        salida.append(
            {
                "puesto": i,
                "id": p["id"],
                "codigo": p["codigo"],
                "nombre": p["nombre"],
                "colegio": p["colegio"],
                "grado": p["grado"],
                "puntos": round(p["puntos"], 4),
                "bono": round(p["bono"], 4),
                "total": round(p["total"], 4),
                "nota": round(1 + 4 * p["puntos"] / PUNTOS_TOTALES, 2),
                "tiempo_usado": round(p["tiempo_usado"], 1),
                "tiempo_respuestas": round(p["tiempo_respuestas"], 3),
                "salidas": p["salidas"],
                "motivo_fin": p["motivo_fin"],
            }
        )
    return salida


def puesto_de(pid):
    for f in clasificacion():
        if f["id"] == pid:
            return f["puesto"]
    return None


# =========================================================================== experimento de clase (estudio de Nature)
def experimento():
    q_ver = PREGUNTAS["m1_veracidad"][1]
    verdad = q_ver["respuesta"]
    resp = {}
    for r in DB.execute(
        "SELECT r.participante_id pid, r.pregunta_id q, r.respuesta, p.grupo FROM respuestas r "
        "JOIN participantes p ON p.id=r.participante_id WHERE p.estado != 'descalificado' AND "
        "r.pregunta_id IN ('m1_compartir','m1_veracidad')"
    ).fetchall():
        resp.setdefault(r["pid"], {"grupo": r["grupo"]})[r["q"]] = json.loads(r["respuesta"])
    completos = [v for v in resp.values() if "m1_compartir" in v and "m1_veracidad" in v]
    n = len(completos)
    if n < 2:
        return {"n": n, "listo": False}
    falsos = [k for k, v in verdad.items() if v == "F"]
    ciertos = [k for k, v in verdad.items() if v == "V"]

    def tasa(grupo, pregunta, valor, posts):
        vals = [x[pregunta][k] == valor for x in grupo for k in posts]
        return 100 * sum(vals) / len(vals) if vals else None

    def resumen(grupo):
        if not grupo:
            return None
        c_f, c_v = tasa(grupo, "m1_compartir", "S", falsos), tasa(grupo, "m1_compartir", "S", ciertos)
        b_f, b_v = tasa(grupo, "m1_veracidad", "V", falsos), tasa(grupo, "m1_veracidad", "V", ciertos)
        return {
            "n": len(grupo),
            "comparte_falsas": c_f,
            "comparte_verdaderas": c_v,
            "cree_falsas": b_f,
            "cree_verdaderas": b_v,
            "discernimiento_compartir": c_v - c_f,
            "discernimiento_creer": b_v - b_f,
        }

    # Sabiduría de la multitud: ¿acierta el promedio de la clase más que el estudiante promedio?
    aciertos_multitud, por_post = 0, []
    for k, v in verdad.items():
        pct_v = 100 * sum(x["m1_veracidad"][k] == "V" for x in completos) / n
        pct_comp = 100 * sum(x["m1_compartir"][k] == "S" for x in completos) / n
        veredicto = "V" if pct_v >= 50 else "F"
        aciertos_multitud += veredicto == v
        por_post.append(
            {
                "id": k,
                "verdad": v,
                "pct_cree_verdadera": pct_v,
                "pct_compartiria": pct_comp,
                "multitud_acierta": veredicto == v,
            }
        )
    individuales = [sum(x["m1_veracidad"][k] == v for k, v in verdad.items()) for x in completos]
    textos = {pp["id"]: pp["texto"] for pp in PREGUNTAS["m1_compartir"][1]["publicaciones"]}
    for pp in por_post:
        pp["texto"] = textos[pp["id"]]
    return {
        "n": n,
        "listo": True,
        "total_posts": len(verdad),
        "clase": resumen(completos),
        "grupo_sin_recordatorio": resumen([x for x in completos if x["grupo"] == "A"]),
        "grupo_con_recordatorio": resumen([x for x in completos if x["grupo"] == "B"]),
        "multitud": {
            "aciertos_multitud": aciertos_multitud,
            "promedio_individual": sum(individuales) / n,
            "mejor_individual": max(individuales),
            "pct_estudiantes_superados": 100 * sum(i < aciertos_multitud for i in individuales) / n,
        },
        "por_publicacion": por_post,
    }


# =========================================================================== vistas
def estado_participante(p):
    ahora = time.time()
    estado_reto = cfg("estado")
    filas = DB.execute("SELECT * FROM respuestas WHERE participante_id=?", (p["id"],)).fetchall()
    retro = cfg("retro") == "1" or estado_reto == "resultados"
    respuestas = {}
    for r in filas:
        item = {"respuesta": json.loads(r["respuesta"])}
        if retro:
            item.update({"puntos": round(r["puntos"], 2), "max": r["max_puntos"], "fraccion": round(r["fraccion"], 4)})
        respuestas[r["pregunta_id"]] = item
    restante = None
    if p["estado"] == "en_curso":
        restante = max(0, p["inicio"] + duracion_seg() - ahora)
    datos = {
        "reto": {
            "titulo": BANCO["titulo"],
            "evento": cfg("evento"),
            "estado": estado_reto,
            "n_misiones": len(BANCO["misiones"]),
            "duracion_min": duracion_seg() / 60,
            "puntos_totales": PUNTOS_TOTALES,
            "bono_max": BONO_MAX,
            "retro": retro,
            "reloj_global": cfg("reloj_global", "1") == "1",
        },
        "participante": {
            "codigo": p["codigo"],
            "nombre": p["nombre"],
            "colegio": p["colegio"],
            "grado": p["grado"],
            "estado": p["estado"],
            "restante_seg": restante,
            "tiempo_usado": p["tiempo_usado"],
        },
        "respuestas": respuestas,
        "servidor_ahora": ahora,
    }
    if p["estado"] in ("en_curso", "finalizado"):
        datos["misiones"] = examen_publico(p, frozenset(r["pregunta_id"] for r in filas))
    if p["estado"] == "finalizado" and retro:
        datos["participante"].update(
            {"puntos": round(p["puntos"], 2), "bono": round(p["bono"], 2), "total": round(p["total"], 2)}
        )
    if estado_reto == "resultados" and p["estado"] == "finalizado":
        datos["participante"]["puesto"] = puesto_de(p["id"])
        datos["participante"]["nota"] = round(1 + 4 * p["puntos"] / PUNTOS_TOTALES, 2)
        datos["revision"] = {}
        for qid, (m, q) in PREGUNTAS.items():  # noqa: B007
            if visible_para(p, q):
                _, c = resolver(p, q)
                datos["revision"][qid] = {"respuesta": c.get("respuesta"), "explicacion": c.get("explicacion", "")}
    return datos


def publico():
    estado = cfg("estado")
    cuenta = {
        r["estado"]: r["n"]
        for r in DB.execute("SELECT estado, COUNT(*) n FROM participantes GROUP BY estado").fetchall()
    }
    datos = {
        "evento": cfg("evento"),
        "titulo": BANCO["titulo"],
        "estado": estado,
        "sala": cfg("sala"),
        "urls": URLS,
        "duracion_min": duracion_seg() / 60,
        "abierto_en": float(cfg("abierto_en", 0) or 0),
        "cerrado_en": float(cfg("cerrado_en", 0) or 0),
        "servidor_ahora": time.time(),
        "modo_sorpresa": cfg("modo_sorpresa") == "1",
        "reloj_global": cfg("reloj_global", "1") == "1",
        "conteo": {
            "inscritos": sum(cuenta.values()) - cuenta.get("descalificado", 0),
            "en_curso": cuenta.get("en_curso", 0),
            "finalizados": cuenta.get("finalizado", 0),
        },
    }
    ranking = clasificacion()
    if estado == "resultados" or cfg("modo_sorpresa") != "1":
        datos["ranking"] = [
            {k: f[k] for k in ("puesto", "nombre", "colegio", "grado", "total", "puntos")} for f in ranking[:10]
        ]
    if estado in ("cerrado", "resultados"):
        datos["experimento"] = experimento()
    return datos


def resumen_admin():
    ahora = time.time()
    rank = {f["id"]: f for f in clasificacion()}
    resp_count = {
        r["participante_id"]: r["n"]
        for r in DB.execute("SELECT participante_id, COUNT(*) n FROM respuestas GROUP BY participante_id").fetchall()
    }
    total_preg = len(PREGUNTAS)
    filas = []
    for p in DB.execute("SELECT * FROM participantes ORDER BY id").fetchall():
        restante = max(0, p["inicio"] + duracion_seg() - ahora) if p["estado"] == "en_curso" else None
        f = rank.get(p["id"], {})
        filas.append(
            {
                "id": p["id"],
                "codigo": p["codigo"],
                "nombre": p["nombre"],
                "colegio": p["colegio"],
                "grado": p["grado"],
                "integrantes": p["integrantes"],
                "grupo": p["grupo"],
                "estado": p["estado"],
                "respondidas": resp_count.get(p["id"], 0),
                "total_preguntas": sum(visible_para(p, q) for _, q in PREGUNTAS.values()),
                "puntos": round(p["puntos"], 2),
                "bono": round(p["bono"], 2),
                "total": round(p["total"], 2),
                "tiempo_usado": p["tiempo_usado"],
                "tiempo_respuestas": p["tiempo_respuestas"],
                "restante_seg": restante,
                "salidas": p["salidas"],
                "puesto": f.get("puesto"),
                "nota": f.get("nota"),
                "motivo_fin": p["motivo_fin"],
            }
        )
    return {
        "config": {
            k: cfg(k)
            for k in (
                "estado",
                "sala",
                "modo_sorpresa",
                "retro",
                "duracion_min",
                "evento",
                "abierto_en",
                "cerrado_en",
                "reloj_global",
            )
        },
        "urls": URLS,
        "banco": {
            "version": BANCO.get("version"),
            "preguntas": total_preg,
            "puntos_totales": PUNTOS_TOTALES,
            "bono_max": BONO_MAX,
        },
        "participantes": filas,
        "experimento": experimento(),
        "servidor_ahora": ahora,
    }


def csv_resultados():
    buf = io.StringIO()
    qids = list(PREGUNTAS)
    w = csv.writer(buf, delimiter=";")
    w.writerow(
        [
            "puesto",
            "codigo",
            "nombre",
            "colegio",
            "grado",
            "integrantes",
            "estado",
            "puntos_sobre_1000",
            "bono_tiempo",
            "puntaje_total",
            "nota_1a5",
            "tiempo_usado_min",
            "ultima_respuesta_min",
            "salidas_de_pestana",
            "motivo_fin",
            *qids,
        ]
    )
    rank = {f["id"]: f for f in clasificacion()}
    pts = {}
    for r in DB.execute("SELECT participante_id, pregunta_id, puntos FROM respuestas").fetchall():
        pts.setdefault(r["participante_id"], {})[r["pregunta_id"]] = r["puntos"]
    filas = DB.execute("SELECT * FROM participantes").fetchall()
    filas = sorted(filas, key=lambda p: (rank.get(p["id"], {}).get("puesto") or 10**6, p["id"]))
    fmt = lambda v: f"{v:.4f}".replace(".", ",") if isinstance(v, float) else v  # noqa: E731
    for p in filas:
        f = rank.get(p["id"], {})
        w.writerow(
            [
                f.get("puesto", ""),
                p["codigo"],
                p["nombre"],
                p["colegio"],
                p["grado"],
                p["integrantes"],
                p["estado"],
                fmt(p["puntos"]),
                fmt(p["bono"]),
                fmt(p["total"]),
                fmt(f["nota"]) if f else "",
                fmt(p["tiempo_usado"] / 60) if p["tiempo_usado"] is not None else "",
                fmt(p["tiempo_respuestas"] / 60) if p["tiempo_respuestas"] is not None else "",
                p["salidas"],
                p["motivo_fin"] or "",
                *(fmt(pts.get(p["id"], {}).get(q, "")) for q in qids),
            ]
        )
    return "﻿" + buf.getvalue()


def csv_respuestas():
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(
        [
            "codigo",
            "nombre",
            "grupo_experimento",
            "pregunta",
            "variante",
            "respuesta",
            "fraccion",
            "puntos",
            "max_puntos",
            "segundos_desde_inicio",
        ]
    )
    for r in DB.execute(
        "SELECT r.*, p.codigo, p.nombre, p.grupo, p.inicio FROM respuestas r JOIN participantes p "
        "ON p.id=r.participante_id ORDER BY p.id, r.momento"
    ).fetchall():
        w.writerow(
            [
                r["codigo"],
                r["nombre"],
                r["grupo"],
                r["pregunta_id"],
                r["variante"],
                r["respuesta"],
                f"{r['fraccion']:.4f}".replace(".", ","),
                f"{r['puntos']:.4f}".replace(".", ","),
                r["max_puntos"],
                round(r["momento"] - (r["inicio"] or r["momento"])),
            ]
        )
    return "﻿" + buf.getvalue()


# =========================================================================== acciones
class ErrorAPI(Exception):
    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.codigo = codigo


def limpiar(texto, largo=80):
    return re.sub(r"\s+", " ", str(texto or "")).strip()[:largo]


def nuevo_codigo():
    while True:
        c = "".join(secrets.choice(ALFABETO) for _ in range(5))
        if not DB.execute("SELECT 1 FROM participantes WHERE codigo=?", (c,)).fetchone():
            return c


def registrar(d):
    if cfg("estado") not in ("inscripcion", "abierto"):
        raise ErrorAPI("Las inscripciones están cerradas.")
    if limpiar(d.get("sala"), 10).upper() != cfg("sala"):
        raise ErrorAPI("El código de sala no es correcto. Míralo en el tablero.")
    nombre = limpiar(d.get("nombre"), 60)
    colegio = limpiar(d.get("colegio"), 80)
    grado = limpiar(d.get("grado"), 10)
    if len(nombre) < 3:
        raise ErrorAPI("Escribe tu nombre (o el del equipo).")
    if grado not in ("9", "10", "11"):
        raise ErrorAPI("Elige el grado: 9, 10 u 11.")
    if DB.execute(
        "SELECT 1 FROM participantes WHERE lower(nombre)=lower(?) AND lower(colegio)=lower(?) AND grado=?",
        (nombre, colegio, grado),
    ).fetchone():
        raise ErrorAPI(
            "Ya hay alguien inscrito con ese nombre en ese colegio y grado. Si eres tú, entra con tu "
            "código; si no, agrega tu segundo apellido."
        )
    n = DB.execute("SELECT COUNT(*) n FROM participantes").fetchone()["n"]
    grupo = "AB"[n % 2]  # asignación alternada: grupos del mismo tamaño para el experimento
    codigo, token = nuevo_codigo(), secrets.token_urlsafe(24)
    DB.execute(
        "INSERT INTO participantes(codigo, token, nombre, colegio, grado, integrantes, grupo, semilla, creado, "
        "estado) VALUES(?,?,?,?,?,?,?,?,?, 'registrado')",
        (
            codigo,
            token,
            nombre,
            colegio,
            grado,
            limpiar(d.get("integrantes"), 200),
            grupo,
            secrets.token_hex(8),
            time.time(),
        ),
    )
    return {"token": token, "codigo": codigo}


def entrar(d):
    codigo = limpiar(d.get("codigo"), 10).upper()
    p = DB.execute("SELECT * FROM participantes WHERE codigo=?", (codigo,)).fetchone()
    if not p:
        time.sleep(0.6)  # frena a quien intente adivinar códigos
        raise ErrorAPI("No encontramos ese código. Revísalo (son 5 caracteres).", 404)
    return {"token": p["token"], "codigo": p["codigo"]}


def comenzar(p):
    if p["estado"] != "registrado":
        return
    if cfg("estado") != "abierto":
        raise ErrorAPI("El reto todavía no ha empezado. Espera la señal del docente.")
    ahora = time.time()
    inicio = ahora
    if cfg("reloj_global", "1") == "1":
        # Reloj global: el tiempo corre desde que el docente abrió el reto y termina a la misma hora para todos.
        abierto = float(cfg("abierto_en", 0) or 0)
        if abierto:
            inicio = abierto
        if ahora >= inicio + duracion_seg():
            raise ErrorAPI("El tiempo del reto ya terminó.")
    DB.execute("UPDATE participantes SET estado='en_curso', inicio=? WHERE id=?", (inicio, p["id"]))


def responder(p, d):
    ahora = time.time()
    if p["estado"] != "en_curso":
        raise ErrorAPI("Tu intento ya terminó.")
    if cfg("estado") != "abierto":
        raise ErrorAPI("El reto está cerrado.")
    if ahora >= p["inicio"] + duracion_seg():
        finalizar(p, ahora, "tiempo")
        raise ErrorAPI("Se acabó el tiempo. Tus respuestas quedaron guardadas.")
    qid = d.get("pregunta")
    if qid not in PREGUNTAS:
        raise ErrorAPI("Pregunta desconocida.")
    _, q = PREGUNTAS[qid]
    if not visible_para(p, q):
        raise ErrorAPI("Pregunta no disponible.")
    if DB.execute("SELECT 1 FROM respuestas WHERE participante_id=? AND pregunta_id=?", (p["id"], qid)).fetchone():
        raise ErrorAPI("Esa pregunta ya fue respondida.")
    if (
        q.get("requiere")
        and not DB.execute(
            "SELECT 1 FROM respuestas WHERE participante_id=? AND pregunta_id=?", (p["id"], q["requiere"])
        ).fetchone()
    ):
        raise ErrorAPI("Primero responde la parte anterior de esta misión.")
    var, cuerpo = resolver(p, q)
    try:
        r = validar_respuesta(cuerpo, d.get("respuesta"))
    except (AssertionError, ValueError, TypeError):
        raise ErrorAPI("Respuesta incompleta o con formato no válido.")  # noqa: B904
    frac = fraccion(cuerpo, r)
    pts = frac * q["puntos"]
    DB.execute(
        "INSERT INTO respuestas VALUES(?,?,?,?,?,?,?,?)",
        (p["id"], qid, var, json.dumps(r, ensure_ascii=False), frac, pts, q["puntos"], ahora),
    )
    recalcular_puntos(p["id"])
    if cfg("retro") == "1":
        return {"ok": True, "puntos": round(pts, 2), "max": q["puntos"], "fraccion": round(frac, 4)}
    return {"ok": True}


def cambiar_estado(nuevo):
    if nuevo not in ESTADOS:
        raise ErrorAPI("Estado no válido.")
    ahora = time.time()
    if nuevo == "abierto" and not cfg("abierto_en"):
        set_cfg("abierto_en", ahora)
    if nuevo in ("cerrado", "resultados"):
        for p in DB.execute("SELECT * FROM participantes WHERE estado='en_curso'").fetchall():
            finalizar(p, ahora, "cierre")
        DB.execute("UPDATE participantes SET estado='no_inicio' WHERE estado='registrado'")
        if not cfg("cerrado_en"):
            set_cfg("cerrado_en", ahora)
    set_cfg("estado", nuevo)


def accion_participante(d):
    p = DB.execute("SELECT * FROM participantes WHERE id=?", (int(d.get("id", 0)),)).fetchone()
    if not p:
        raise ErrorAPI("Participante no encontrado.", 404)
    accion = d.get("accion")
    if accion == "descalificar":
        DB.execute(
            "UPDATE participantes SET estado='descalificado', motivo_fin=? WHERE id=?",
            (f"descalificado (antes: {p['estado']})", p["id"]),
        )
    elif accion == "reactivar" and p["estado"] == "descalificado":
        previo = re.search(r"antes: (\w+)", p["motivo_fin"] or "")
        DB.execute(
            "UPDATE participantes SET estado=?, motivo_fin=NULL WHERE id=?",
            (previo.group(1) if previo else "finalizado", p["id"]),
        )
    elif accion == "finalizar":
        finalizar(p, time.time(), "docente")
    elif accion == "eliminar" and p["estado"] in ("registrado", "no_inicio"):
        DB.execute("DELETE FROM participantes WHERE id=?", (p["id"],))
    else:
        raise ErrorAPI("Acción no válida para este participante.")


def reiniciar(d):
    if d.get("confirmar") != "BORRAR":
        raise ErrorAPI("Escribe BORRAR para confirmar.")
    copia = RUTA_DB.parent / f"copia_reto_{time.strftime('%Y%m%d_%H%M%S')}.db"
    DB.execute("VACUUM INTO ?", (str(copia),))
    DB.executescript(
        "DELETE FROM respuestas; DELETE FROM eventos; DELETE FROM participantes; "
        "DELETE FROM sqlite_sequence WHERE name='participantes';"
    )
    for k in ("abierto_en", "cerrado_en"):
        DB.execute("DELETE FROM config WHERE clave=?", (k,))
    set_cfg("estado", "inscripcion")
    return {"ok": True, "copia": copia.name}


# =========================================================================== HTTP
TIPOS = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".json": "application/json; charset=utf-8",
    ".woff2": "font/woff2",
}
PAGINAS = {"/": "estudiante.html", "/admin": "admin.html", "/tablero": "tablero.html"}


class Manejador(BaseHTTPRequestHandler):
    server_version = "RetoDesinformacion/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # silencio: solo se imprimen errores

    # ---- respuesta
    def enviar(self, codigo, cuerpo, tipo="application/json; charset=utf-8", extra=None):
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo, ensure_ascii=False)
        datos = cuerpo.encode("utf-8") if isinstance(cuerpo, str) else cuerpo
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(datos)

    def cuerpo_json(self):
        largo = int(self.headers.get("Content-Length") or 0)
        if largo > 65536:
            raise ErrorAPI("Petición demasiado grande.", 413)
        try:
            return json.loads(self.rfile.read(largo) or b"{}")
        except json.JSONDecodeError:
            raise ErrorAPI("JSON no válido.")  # noqa: B904

    def token(self):
        aut = self.headers.get("Authorization", "")
        return aut[7:] if aut.startswith("Bearer ") else ""

    def es_admin(self, qs):
        clave = self.headers.get("X-Clave-Admin") or (qs.get("clave") or [""])[0]
        return secrets.compare_digest(clave.strip().upper().encode("utf-8"), CLAVE_ADMIN.encode("utf-8"))

    # ---- rutas
    def do_GET(self):  # noqa: C901
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        try:
            if url.path in PAGINAS:
                return self.archivo(WEB / PAGINAS[url.path])
            if url.path.startswith("/static/"):
                return self.archivo(WEB / url.path[len("/static/") :])
            with LOCK:
                vencer_tiempos()
                if url.path == "/api/estado":
                    p = participante_por_token(self.token())
                    if not p:
                        raise ErrorAPI("Sesión no encontrada.", 401)
                    return self.enviar(200, estado_participante(p))
                if url.path == "/api/publico":
                    return self.enviar(200, publico())
                if url.path.startswith("/api/admin/"):
                    if not self.es_admin(qs):
                        raise ErrorAPI("Clave de docente incorrecta.", 403)
                    if url.path == "/api/admin/resumen":
                        return self.enviar(200, resumen_admin())
                    if url.path == "/api/admin/resultados.csv":
                        return self.enviar(
                            200,
                            csv_resultados(),
                            "text/csv; charset=utf-8",
                            {"Content-Disposition": 'attachment; filename="resultados_reto.csv"'},
                        )
                    if url.path == "/api/admin/respuestas.csv":
                        return self.enviar(
                            200,
                            csv_respuestas(),
                            "text/csv; charset=utf-8",
                            {"Content-Disposition": 'attachment; filename="respuestas_detalle.csv"'},
                        )
            raise ErrorAPI("No encontrado.", 404)
        except ErrorAPI as e:
            self.enviar(e.codigo, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            print("[error]", repr(e), file=sys.stderr)
            self.enviar(500, {"error": "Error interno del servidor."})

    def do_POST(self):  # noqa: C901
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        try:
            d = self.cuerpo_json()
            with LOCK:
                vencer_tiempos()
                if url.path == "/api/registro":
                    return self.enviar(200, registrar(d))
                if url.path == "/api/entrar":
                    return self.enviar(200, entrar(d))
                if url.path.startswith("/api/admin/"):
                    if not self.es_admin(qs):
                        raise ErrorAPI("Clave de docente incorrecta.", 403)
                    if url.path == "/api/admin/login":
                        return self.enviar(200, {"ok": True})
                    if url.path == "/api/admin/estado":
                        cambiar_estado(d.get("estado"))
                    elif url.path == "/api/admin/config":
                        for k in ("modo_sorpresa", "retro"):
                            if k in d:
                                set_cfg(k, "1" if d[k] else "0")
                        if "sala" in d:
                            sala = limpiar(d["sala"], 8).upper()
                            if not re.fullmatch(r"[A-Z0-9]{3,8}", sala):
                                raise ErrorAPI("La sala debe tener de 3 a 8 letras o números.")
                            set_cfg("sala", sala)
                        if "evento" in d:
                            set_cfg("evento", limpiar(d["evento"], 80) or "Reto")
                        if "reloj_global" in d:
                            if cfg("estado") != "inscripcion":
                                raise ErrorAPI("El tipo de reloj solo se cambia antes de abrir el reto.")
                            set_cfg("reloj_global", "1" if d["reloj_global"] else "0")
                        if "duracion_min" in d:
                            if cfg("estado") != "inscripcion":
                                raise ErrorAPI("La duración solo se cambia antes de abrir el reto.")
                            set_cfg("duracion_min", max(10, min(240, int(d["duracion_min"]))))
                    elif url.path == "/api/admin/participante":
                        accion_participante(d)
                    elif url.path == "/api/admin/reiniciar":
                        return self.enviar(200, reiniciar(d))
                    else:
                        raise ErrorAPI("No encontrado.", 404)
                    return self.enviar(200, {"ok": True})
                p = participante_por_token(self.token())
                if not p:
                    raise ErrorAPI("Sesión no encontrada. Vuelve a entrar con tu código.", 401)
                if url.path == "/api/comenzar":
                    comenzar(p)
                    return self.enviar(200, {"ok": True})
                if url.path == "/api/responder":
                    return self.enviar(200, responder(p, d))
                if url.path == "/api/finalizar":
                    finalizar(p, time.time(), "entrega")
                    return self.enviar(200, {"ok": True})
                if url.path == "/api/evento":
                    if d.get("tipo") == "salida" and p["estado"] == "en_curso":
                        DB.execute("UPDATE participantes SET salidas=salidas+1 WHERE id=?", (p["id"],))
                        DB.execute("INSERT INTO eventos VALUES(?,?,?)", (p["id"], "salida", time.time()))
                    return self.enviar(200, {"ok": True})
            raise ErrorAPI("No encontrado.", 404)
        except ErrorAPI as e:
            self.enviar(e.codigo, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            print("[error]", repr(e), file=sys.stderr)
            self.enviar(500, {"error": "Error interno del servidor."})

    def archivo(self, ruta):
        ruta = ruta.resolve()
        if WEB.resolve() not in ruta.parents or not ruta.is_file():
            raise ErrorAPI("No encontrado.", 404)
        self.enviar(200, ruta.read_bytes(), TIPOS.get(ruta.suffix, "application/octet-stream"))


# =========================================================================== arranque
def ips_locales():
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))  # no envía nada; solo elige la interfaz de salida
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith("127."))


class ServidorDual(ThreadingHTTPServer):
    """Escucha en IPv6 e IPv4 a la vez: así «localhost» (que Windows resuelve a ::1) responde sin demora."""

    address_family = socket.AF_INET6
    daemon_threads = True

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        super().server_bind()


def vigilante():
    while True:
        time.sleep(3)
        try:
            with LOCK:
                vencer_tiempos()
        except Exception as e:  # noqa: BLE001
            print("[vigilante]", repr(e), file=sys.stderr)


def main():
    global DB, CLAVE_ADMIN, URLS, RUTA_DB
    ap = argparse.ArgumentParser(description="Servidor del reto Detectives de la desinformación")
    ap.add_argument("--puerto", type=int, default=int(os.environ.get("PORT", 8000)))  # PORT: lo fijan los hostings
    ap.add_argument(
        "--clave",
        default=os.environ.get("RETO_CLAVE", ""),
        help="clave del panel docente (si no se da, se genera y se guarda en datos/)",
    )
    ap.add_argument("--db", default=str(DATOS / "reto.db"))
    ap.add_argument(
        "--url-publica",
        default=os.environ.get("RETO_URL_PUBLICA", ""),
        help="dirección pública (https://...) si el reto se abre por internet con un túnel o un hosting",
    )
    a = ap.parse_args()

    DATOS.mkdir(parents=True, exist_ok=True)
    RUTA_DB = Path(a.db).resolve()
    RUTA_DB.parent.mkdir(parents=True, exist_ok=True)
    DB = conectar(RUTA_DB)
    inicializar_config()
    archivo_clave = RUTA_DB.parent / "clave_docente.txt"  # junto a la base: un simulacro no toca la clave real
    if a.clave:
        CLAVE_ADMIN = a.clave.strip().upper()
        archivo_clave.write_text(CLAVE_ADMIN, encoding="utf-8")
    elif archivo_clave.exists():
        CLAVE_ADMIN = archivo_clave.read_text(encoding="utf-8").strip().upper()
    else:
        CLAVE_ADMIN = "".join(secrets.choice(ALFABETO) for _ in range(6))
        archivo_clave.write_text(CLAVE_ADMIN, encoding="utf-8")

    URLS = [f"http://{ip}:{a.puerto}" for ip in ips_locales()] or [f"http://localhost:{a.puerto}"]
    publica = (a.url_publica or os.environ.get("RENDER_EXTERNAL_URL", "")).strip().rstrip("/")
    if publica:
        URLS.insert(0, publica)  # la pública va primero: es la que ven el tablero y el panel
        if os.environ.get("RETO_HOSTING") or os.environ.get("RENDER"):
            URLS = [publica]  # en un hosting las IP internas no le sirven a nadie
    threading.Thread(target=vigilante, daemon=True).start()
    try:
        servidor = ServidorDual(("::", a.puerto), Manejador)
    except OSError:
        servidor = ThreadingHTTPServer(("0.0.0.0", a.puerto), Manejador)
        servidor.daemon_threads = True

    linea = "=" * 66
    print(linea)
    print(f"  {BANCO['titulo']}  ·  banco v{BANCO.get('version')}  ·  {len(PREGUNTAS)} preguntas")
    print(linea)
    print("  ESTUDIANTES (los de la misma red wifi pueden usar cualquiera de estas):")
    for u in URLS:
        print(f"      {u}")
    print(f"  CÓDIGO DE SALA:  {cfg('sala')}")
    print(f"  TABLERO (proyector):  {URLS[0]}/tablero")
    print(f"  PANEL DOCENTE:        http://localhost:{a.puerto}/admin")
    print(f"  CLAVE DOCENTE:        {CLAVE_ADMIN}   (guardada en datos/clave_docente.txt)")
    print(linea)
    print("  Deja esta ventana abierta durante todo el reto. Ctrl+C para detener.")
    print(linea)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido. Los datos quedan en", a.db)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    main()
