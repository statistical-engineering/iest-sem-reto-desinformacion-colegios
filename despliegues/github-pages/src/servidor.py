"""
Servidor del reto «Detectives de la desinformación».

Solo usa la biblioteca estándar de Python (3.9 o superior): no hay que instalar nada.

    python servidor.py                 # puerto 8000
    python servidor.py --puerto 8080
    python servidor.py --clave MICLAVE # fija la clave del panel docente

Al arrancar imprime las direcciones para estudiantes (/), tablero (/tablero) y
panel docente (/admin). Todo se guarda en datos/reto.db (SQLite): si el computador
se apaga, al volver a arrancar el reto continúa donde iba.

En internet (PythonAnywhere u otro alojamiento WSGI) se usa `crear_app()`: ver
wsgi_pythonanywhere.py y «PUBLICAR EN INTERNET/GUIA_PUBLICAR_GRATIS.md».

Reglas que hace cumplir el servidor (no el navegador):
  * las respuestas correctas nunca salen del servidor hasta publicar resultados;
  * cada pregunta se responde una sola vez;
  * hay UN reloj para todos (todos los colegios a la vez): lo abre, pausa, alarga y
    cierra la organización desde el panel; al vencerse, el reto se cierra solo;
  * la clasificación es un orden total y única para todos los colegios.
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
# En el paquete de PythonAnywhere todo va junto (web/ y el banco al lado de este archivo). En el repositorio,
# web/ está en despliegues/github-pages/web y el banco en 2_Aplicacion_Reto/: ver herramientas/empaquetar.py.
WEB = Path(os.environ.get("RETO_WEB") or AQUI / "web")
DATOS = AQUI / "datos"
BANCO_PATH = Path(os.environ.get("RETO_BANCO") or AQUI / "banco_preguntas.json")
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
    con = sqlite3.connect(ruta, check_same_thread=False, isolation_level=None, timeout=15)
    con.row_factory = sqlite3.Row
    # WAL es lo más rápido en disco local; algunos alojamientos (discos de red) piden el modo clásico
    modo = os.environ.get("RETO_JOURNAL", "WAL").upper()
    try:
        con.execute(f"PRAGMA journal_mode={'DELETE' if modo == 'DELETE' else 'WAL'}")
    except sqlite3.DatabaseError:
        con.execute("PRAGMA journal_mode=DELETE")
    con.execute("PRAGMA synchronous=NORMAL")
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
        "colegios": "[]",
        "pausas": "[]",
        "extra_seg": "0",
    }
    for k, v in defaults.items():
        if cfg(k) is None:
            set_cfg(k, v)


def duracion_seg():
    """Duración total del reloj común: la configurada más los minutos que la organización agregue o quite."""
    return float(cfg("duracion_min", BANCO["duracion_min"])) * 60 + float(cfg("extra_seg", 0) or 0)


def colegios():
    try:
        return json.loads(cfg("colegios", "[]") or "[]")
    except json.JSONDecodeError:
        return []


# =========================================================================== reloj común
# Un solo reloj para todos los colegios. Corre desde que la organización abre el reto; las pausas no
# cuentan. «segundos_de_reto(t)» es cuánto reloj había corrido en el instante t.
def pausas():
    return json.loads(cfg("pausas", "[]") or "[]")


def en_pausa():
    ps = pausas()
    return bool(ps) and ps[-1][1] is None


def segundos_de_reto(t):
    inicio = float(cfg("abierto_en", 0) or 0)
    if not inicio or t <= inicio:
        return 0.0
    pausado = sum(max(0.0, min(t, fin if fin is not None else t) - max(ini, inicio)) for ini, fin in pausas())
    return max(0.0, t - inicio - pausado)


def restante_reto(t=None):
    """Segundos que le quedan al reloj común (None si el reto no está abierto)."""
    if cfg("estado") != "abierto":
        return None
    return max(0.0, duracion_seg() - segundos_de_reto(time.time() if t is None else t))


def reloj_publico():
    return {
        "restante_seg": restante_reto(),
        "pausado": en_pausa(),
        "duracion_seg": duracion_seg(),
        "transcurrido_seg": segundos_de_reto(time.time()) if cfg("abierto_en") else 0.0,
    }


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
    Todos los tiempos se miden con el reloj COMÚN (sin pausas), igual para todos los colegios.
    """
    if p["estado"] != "en_curso":
        return
    dur = duracion_seg()
    reloj_fin = min(dur, segundos_de_reto(ahora))
    usado = max(0.0, reloj_fin - segundos_de_reto(p["inicio"]))
    ultima = DB.execute("SELECT MAX(momento) m FROM respuestas WHERE participante_id=?", (p["id"],)).fetchone()["m"]
    t_resp = min(dur, segundos_de_reto(ultima) if ultima is not None else reloj_fin)
    puntos = recalcular_puntos(p["id"])
    bono = BONO_MAX * (puntos / PUNTOS_TOTALES) * max(0.0, 1 - t_resp / dur)
    DB.execute(
        "UPDATE participantes SET estado='finalizado', fin=?, tiempo_usado=?, tiempo_respuestas=?, bono=?, "
        "total=?, motivo_fin=? WHERE id=?",
        (ahora, usado, t_resp, bono, puntos + bono, motivo, p["id"]),
    )


def vencer_tiempos():
    """Si el reloj común llegó a cero, el reto se cierra solo para todos."""
    if cfg("estado") == "abierto" and not en_pausa() and restante_reto() <= 0:
        cambiar_estado("cerrado", motivo="tiempo")


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
def estado_participante(p, firma_cliente=""):
    """Estado del estudiante. El examen completo (unos 100 KB) solo se envía si cambió desde la última vez
    (firma distinta): los sondeos periódicos son livianos, lo que importa cuando hay cientos conectados."""
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
    restante = restante_reto() if p["estado"] == "en_curso" else None
    respondidas = frozenset(r["pregunta_id"] for r in filas)
    desbloqueados = sorted(
        m["dossier"]["revelar_tras"]
        for m in BANCO["misiones"]
        if m.get("dossier", {}).get("revelar_tras") in respondidas
    )
    firma = hashlib.sha1(f"{BANCO.get('version')}|{p['estado']}|{estado_reto}|{desbloqueados}".encode()).hexdigest()[
        :12
    ]
    datos = {
        "reto": {
            "titulo": BANCO["titulo"],
            "evento": cfg("evento"),
            "estado": estado_reto,
            "n_misiones": len(BANCO["misiones"]),
            "pausado": en_pausa(),
            "duracion_min": duracion_seg() / 60,
            "puntos_totales": PUNTOS_TOTALES,
            "bono_max": BONO_MAX,
            "retro": retro,
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
        "firma": firma,
    }
    if p["estado"] in ("en_curso", "finalizado") and firma_cliente != firma:
        datos["misiones"] = examen_publico(p, respondidas)
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


def conteo_por_colegio():
    filas = DB.execute(
        "SELECT colegio, COUNT(*) n FROM participantes WHERE estado != 'descalificado' "
        "GROUP BY colegio ORDER BY n DESC, colegio"
    ).fetchall()
    return [{"colegio": f["colegio"], "n": f["n"]} for f in filas]


def publico(urls=None):
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
        "urls": urls or URLS,
        "duracion_min": duracion_seg() / 60,
        "abierto_en": float(cfg("abierto_en", 0) or 0),
        "cerrado_en": float(cfg("cerrado_en", 0) or 0),
        "servidor_ahora": time.time(),
        "reloj": reloj_publico(),
        "colegios": colegios(),
        "por_colegio": conteo_por_colegio(),
        "modo_sorpresa": cfg("modo_sorpresa") == "1",
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


def resumen_admin(urls=None):
    ahora = time.time()
    rank = {f["id"]: f for f in clasificacion()}
    resp_count = {
        r["participante_id"]: r["n"]
        for r in DB.execute("SELECT participante_id, COUNT(*) n FROM respuestas GROUP BY participante_id").fetchall()
    }
    total_preg = len(PREGUNTAS)
    filas = []
    restante_comun = restante_reto()
    for p in DB.execute("SELECT * FROM participantes ORDER BY id").fetchall():
        restante = restante_comun if p["estado"] == "en_curso" else None
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
                "extra_seg",
            )
        },
        "reloj": reloj_publico(),
        "colegios": colegios(),
        "por_colegio": conteo_por_colegio(),
        "urls": urls or URLS,
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
    lista = colegios()
    if lista:  # con lista de colegios, se elige de ella (así el ranking no tiene «Col. X» y «colegio x» separados)
        exacto = {c.lower(): c for c in lista}
        if colegio.lower() not in exacto:
            raise ErrorAPI("Elige tu colegio de la lista.")
        colegio = exacto[colegio.lower()]
    elif len(colegio) < 3:
        raise ErrorAPI("Escribe el nombre de tu colegio.")
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


class Freno:
    """Cuenta intentos fallidos (claves o códigos adivinados) por quien los hace, una IP o un navegador, y bloquea
    un rato a quien abusa. No usa sleep: en alojamientos con un solo proceso, dormir frenaría a todos los demás."""

    def __init__(self, maximo, ventana, mensaje="Demasiados intentos fallidos."):
        self.maximo, self.ventana, self.mensaje, self.fallos = maximo, ventana, mensaje, {}

    def revisar(self, quien):
        ahora = time.time()
        recientes = [t for t in self.fallos.get(quien, []) if ahora - t < self.ventana]
        self.fallos[quien] = recientes
        if len(recientes) >= self.maximo:
            espera = int(self.ventana - (ahora - recientes[0])) + 1
            raise ErrorAPI(f"{self.mensaje} Espera {espera} segundos e intenta de nuevo.", 429)

    def fallo(self, quien):
        self.fallos.setdefault(quien, []).append(time.time())
        if len(self.fallos) > 5000:  # no crecer sin límite
            self.fallos.clear()


# Los estudiantes de un colegio suelen salir a internet por la MISMA IP: los límites son generosos.
FRENO_CODIGOS = Freno(40, 60)
# Clave del panel. En un colegio todos comparten la IP, así que el bloqueo corto es por NAVEGADOR (cookie
# reto_nav): un estudiante que falla la clave se bloquea solo a sí mismo. El de la red entera frena a quien borra
# la cookie para seguir probando, pero no detiene a un navegador donde el docente ya entró (NAVEGADORES_DOCENTES).
FRENO_ADMIN = Freno(8, 300)
FRENO_ADMIN_RED = Freno(
    40,
    300,
    "Demasiados intentos fallidos desde esta red. Si eres docente, entra desde un navegador donde ya hayas "
    "abierto el panel, o con datos móviles.",
)
NAVEGADORES_DOCENTES = set()
COOKIE_NAVEGADOR = "reto_nav"


def navegador_de(cab):
    """Identificador del navegador (cookie reto_nav), o "" si no trae una válida."""
    m = re.search(rf"(?:^|;\s*){COOKIE_NAVEGADOR}=([A-Za-z0-9_-]{{22}})(?:;|$)", cab("Cookie") or "")
    return m.group(1) if m else ""


def revisar_clave_admin(clave, ip, nav):
    """True si la clave es la del panel. Aplica los dos frenos y recuerda el navegador que acertó."""
    quien = f"nav:{nav}" if nav else f"ip:{ip}"
    FRENO_ADMIN.revisar(quien)
    if nav not in NAVEGADORES_DOCENTES:
        FRENO_ADMIN_RED.revisar(ip)
    if not secrets.compare_digest(clave.encode("utf-8"), CLAVE_ADMIN.encode("utf-8")):
        FRENO_ADMIN.fallo(quien)
        FRENO_ADMIN_RED.fallo(ip)
        return False
    if nav and len(NAVEGADORES_DOCENTES) < 1000:
        NAVEGADORES_DOCENTES.add(nav)
    return True


def entrar(d, ip=""):
    FRENO_CODIGOS.revisar(ip)
    codigo = limpiar(d.get("codigo"), 10).upper()
    p = DB.execute("SELECT * FROM participantes WHERE codigo=?", (codigo,)).fetchone()
    if not p:
        FRENO_CODIGOS.fallo(ip)
        raise ErrorAPI("No encontramos ese código. Revísalo (son 5 caracteres).", 404)
    return {"token": p["token"], "codigo": p["codigo"]}


def comenzar(p):
    if p["estado"] != "registrado":
        return
    if cfg("estado") != "abierto":
        raise ErrorAPI("El reto todavía no ha empezado. Espera la señal de la organización.")
    DB.execute("UPDATE participantes SET estado='en_curso', inicio=? WHERE id=?", (time.time(), p["id"]))


def responder(p, d):  # noqa: C901
    ahora = time.time()
    if p["estado"] != "en_curso":
        raise ErrorAPI("Tu intento ya terminó.")
    if cfg("estado") != "abierto":
        raise ErrorAPI("El reto está cerrado.")
    if en_pausa():
        raise ErrorAPI("El reto está en pausa. Tu respuesta no se envió: espera a que se reanude y envíala de nuevo.")
    if restante_reto(ahora) <= 0:
        vencer_tiempos()
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


def cambiar_estado(nuevo, motivo="cierre"):
    if nuevo not in ESTADOS:
        raise ErrorAPI("Estado no válido.")
    actual = cfg("estado")
    if ESTADOS.index(nuevo) < ESTADOS.index(actual):
        raise ErrorAPI("El reto no puede volver a una etapa anterior. Para empezar de cero usa «Reiniciar».")
    if nuevo == actual:
        return
    ahora = time.time()
    if nuevo == "abierto" and not cfg("abierto_en"):
        set_cfg("abierto_en", ahora)
    if nuevo in ("cerrado", "resultados"):
        if en_pausa():  # cerrar en pausa: la pausa termina aquí
            ps = pausas()
            ps[-1][1] = ahora
            set_cfg("pausas", json.dumps(ps))
        for p in DB.execute("SELECT * FROM participantes WHERE estado='en_curso'").fetchall():
            finalizar(p, ahora, motivo)
        DB.execute("UPDATE participantes SET estado='no_inicio' WHERE estado='registrado'")
        if not cfg("cerrado_en"):
            set_cfg("cerrado_en", ahora)
    set_cfg("estado", nuevo)


def controlar_reloj(d):
    """Pausar, reanudar y sumar o quitar minutos al reloj común (solo con el reto abierto)."""
    if cfg("estado") != "abierto":
        raise ErrorAPI("El reloj solo se controla con el reto abierto.")
    accion, ahora = d.get("accion"), time.time()
    ps = pausas()
    if accion == "pausar":
        if not en_pausa():
            ps.append([ahora, None])
    elif accion == "reanudar":
        if en_pausa():
            ps[-1][1] = ahora
    elif accion == "sumar":
        minutos = float(d.get("minutos", 0))
        if not -60 <= minutos <= 60 or minutos == 0:
            raise ErrorAPI("Indica entre −60 y 60 minutos.")
        nuevo_extra = float(cfg("extra_seg", 0) or 0) + minutos * 60
        if duracion_seg() + minutos * 60 - segundos_de_reto(ahora) < 60:
            raise ErrorAPI("No se puede: al reloj le quedaría menos de 1 minuto. Para terminar, cierra el reto.")
        set_cfg("extra_seg", nuevo_extra)
    else:
        raise ErrorAPI("Acción de reloj no válida.")
    set_cfg("pausas", json.dumps(ps))
    return {"ok": True, "reloj": reloj_publico()}


def guardar_colegios(texto):
    nombres, vistos = [], set()
    for linea in str(texto or "").splitlines():
        n = limpiar(linea, 80)
        if len(n) >= 3 and n.lower() not in vistos:
            vistos.add(n.lower())
            nombres.append(n)
    if len(nombres) > 200:
        raise ErrorAPI("Máximo 200 colegios.")
    set_cfg("colegios", json.dumps(nombres, ensure_ascii=False))


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
    set_cfg("pausas", "[]")
    set_cfg("extra_seg", "0")
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


def origen_y_urls(cab):
    """Dirección pública con la que entran los estudiantes. En internet es el propio dominio
    (p. ej. https://usuario.pythonanywhere.com); en un salón, las IP del computador en el wifi."""
    fija = os.environ.get("RETO_URL_PUBLICA", "").rstrip("/")
    if fija:
        return [fija]
    host = (cab("X-Forwarded-Host") or cab("Host") or "").split(",")[0].strip()
    nombre = host.rsplit(":", 1)[0].strip("[]").lower() if not host.startswith("[") else host.split("]")[0][1:]
    if not host or nombre in ("localhost", "127.0.0.1", "::1") or re.fullmatch(r"(10|192\.168|172\.\d+)\..*", nombre):
        return URLS
    proto = (cab("X-Forwarded-Proto") or "http").split(",")[0].strip()
    return [f"{proto}://{host}"]


def atender(metodo, ruta, cab, leer_cuerpo, ip):
    """Núcleo HTTP común al servidor local y al alojamiento WSGI.
    cab(nombre) → valor de cabecera; leer_cuerpo(n) → bytes. Devuelve (código, tipo, bytes, cabeceras extra).
    Si el navegador no trae la cookie reto_nav, la respuesta se la entrega (ver FRENO_ADMIN)."""
    nav = navegador_de(cab)
    codigo, tipo, datos, extra = _atender(metodo, ruta, cab, leer_cuerpo, ip, nav)
    if not nav:
        segura = "; Secure" if (cab("X-Forwarded-Proto") or "").startswith("https") else ""
        valor = f"{COOKIE_NAVEGADOR}={secrets.token_urlsafe(16)}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Strict"
        extra = {**extra, "Set-Cookie": valor + segura}
    return codigo, tipo, datos, extra


def _atender(metodo, ruta, cab, leer_cuerpo, ip, nav):  # noqa: C901
    url = urlparse(ruta)
    qs = parse_qs(url.query)

    def json_r(codigo, obj):
        return codigo, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False).encode("utf-8"), {}

    def es_admin():
        # Solo por la cabecera: una clave en la URL (?clave=) queda en los registros del alojamiento.
        return revisar_clave_admin((cab("X-Clave-Admin") or "").strip().upper(), ip, nav)

    def token():
        aut = cab("Authorization") or ""
        return aut[7:] if aut.startswith("Bearer ") else ""

    try:
        if metodo == "GET" and url.path in PAGINAS:
            return archivo(WEB / PAGINAS[url.path])
        if metodo == "GET" and url.path.startswith("/static/"):
            return archivo(WEB / url.path[len("/static/") :])
        if metodo == "POST":
            largo = int(cab("Content-Length") or 0)
            if largo > 65536:
                raise ErrorAPI("Petición demasiado grande.", 413)
            try:
                d = json.loads(leer_cuerpo(largo) or b"{}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise ErrorAPI("JSON no válido.")  # noqa: B904
            if not isinstance(d, dict):
                raise ErrorAPI("JSON no válido.")
        elif metodo != "GET":
            raise ErrorAPI("Método no permitido.", 405)
        with LOCK:
            vencer_tiempos()
            if metodo == "GET":
                if url.path == "/api/estado":
                    p = participante_por_token(token())
                    if not p:
                        raise ErrorAPI("Sesión no encontrada.", 401)
                    return json_r(200, estado_participante(p, (qs.get("firma") or [""])[0]))
                if url.path == "/api/publico":
                    return json_r(200, publico(origen_y_urls(cab)))
                if url.path.startswith("/api/admin/"):
                    if not es_admin():
                        raise ErrorAPI("Clave de docente incorrecta.", 403)
                    if url.path == "/api/admin/resumen":
                        return json_r(200, resumen_admin(origen_y_urls(cab)))
                    if url.path == "/api/admin/resultados.csv":
                        return (
                            200,
                            "text/csv; charset=utf-8",
                            csv_resultados().encode("utf-8"),
                            {"Content-Disposition": 'attachment; filename="resultados_reto.csv"'},
                        )
                    if url.path == "/api/admin/respuestas.csv":
                        return (
                            200,
                            "text/csv; charset=utf-8",
                            csv_respuestas().encode("utf-8"),
                            {"Content-Disposition": 'attachment; filename="respuestas_detalle.csv"'},
                        )
                raise ErrorAPI("No encontrado.", 404)

            if url.path == "/api/registro":
                return json_r(200, registrar(d))
            if url.path == "/api/entrar":
                return json_r(200, entrar(d, ip))
            if url.path.startswith("/api/admin/"):
                if not es_admin():
                    raise ErrorAPI("Clave de docente incorrecta.", 403)
                if url.path == "/api/admin/login":
                    return json_r(200, {"ok": True})
                if url.path == "/api/admin/estado":
                    cambiar_estado(d.get("estado"))
                elif url.path == "/api/admin/reloj":
                    return json_r(200, controlar_reloj(d))
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
                    if "colegios" in d:
                        guardar_colegios(d["colegios"])
                    if "duracion_min" in d:
                        if cfg("estado") != "inscripcion":
                            raise ErrorAPI(
                                "La duración solo se cambia antes de abrir el reto. Con el reto "
                                "abierto, usa «+5 min» o «−5 min» en el reloj."
                            )
                        set_cfg("duracion_min", max(10, min(240, int(d["duracion_min"]))))
                elif url.path == "/api/admin/participante":
                    accion_participante(d)
                elif url.path == "/api/admin/reiniciar":
                    return json_r(200, reiniciar(d))
                else:
                    raise ErrorAPI("No encontrado.", 404)
                return json_r(200, {"ok": True})
            p = participante_por_token(token())
            if not p:
                raise ErrorAPI("Sesión no encontrada. Vuelve a entrar con tu código.", 401)
            if url.path == "/api/comenzar":
                comenzar(p)
                return json_r(200, {"ok": True})
            if url.path == "/api/responder":
                return json_r(200, responder(p, d))
            if url.path == "/api/finalizar":
                finalizar(p, time.time(), "entrega")
                return json_r(200, {"ok": True})
            if url.path == "/api/evento":
                if d.get("tipo") == "salida" and p["estado"] == "en_curso":
                    DB.execute("UPDATE participantes SET salidas=salidas+1 WHERE id=?", (p["id"],))
                    DB.execute("INSERT INTO eventos VALUES(?,?,?)", (p["id"], "salida", time.time()))
                return json_r(200, {"ok": True})
            raise ErrorAPI("No encontrado.", 404)
    except ErrorAPI as e:
        return json_r(e.codigo, {"error": str(e)})
    except Exception as e:  # noqa: BLE001
        print("[error]", repr(e), file=sys.stderr)
        return json_r(500, {"error": "Error interno del servidor."})


def archivo(ruta):
    ruta = ruta.resolve()
    if WEB.resolve() not in ruta.parents or not ruta.is_file():
        raise ErrorAPI("No encontrado.", 404)
    # css/js se pueden guardar unos minutos en el navegador: menos tráfico con cientos de estudiantes
    extra = {"Cache-Control": "public, max-age=300"} if ruta.suffix in (".css", ".js", ".png", ".svg") else {}
    return 200, TIPOS.get(ruta.suffix, "application/octet-stream"), ruta.read_bytes(), extra


class Manejador(BaseHTTPRequestHandler):
    """Servidor local (un computador en el wifi del salón)."""

    server_version = "RetoDesinformacion/2.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # silencio: solo se imprimen errores

    def _servir(self, metodo):
        codigo, tipo, datos, extra = atender(
            metodo, self.path, self.headers.get, self.rfile.read, self.client_address[0]
        )
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if "Cache-Control" not in extra:
            self.send_header("Cache-Control", "no-store")
        for k, v in extra.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        self._servir("GET")

    def do_POST(self):
        self._servir("POST")


# =========================================================================== alojamiento en internet (WSGI)
ESTADOS_HTTP = {
    200: "200 OK",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    413: "413 Payload Too Large",
    429: "429 Too Many Requests",
    500: "500 Internal Server Error",
}


def preparar(ruta_db=None, clave=None):
    """Abre la base de datos y fija la clave del panel. La usan el servidor local y crear_app()."""
    global DB, CLAVE_ADMIN, RUTA_DB
    RUTA_DB = Path(ruta_db or os.environ.get("RETO_DB") or DATOS / "reto.db").resolve()
    RUTA_DB.parent.mkdir(parents=True, exist_ok=True)
    DB = conectar(RUTA_DB)
    inicializar_config()
    archivo_clave = RUTA_DB.parent / "clave_docente.txt"  # junto a la base: un simulacro no toca la clave real
    clave = clave or os.environ.get("CLAVE_ADMIN")
    if clave:
        CLAVE_ADMIN = clave.strip().upper()
        archivo_clave.write_text(CLAVE_ADMIN, encoding="utf-8")
    elif archivo_clave.exists():
        CLAVE_ADMIN = archivo_clave.read_text(encoding="utf-8").strip().upper()
    else:
        CLAVE_ADMIN = "".join(secrets.choice(ALFABETO) for _ in range(10))
        archivo_clave.write_text(CLAVE_ADMIN, encoding="utf-8")
    return CLAVE_ADMIN


def crear_app():
    """Aplicación WSGI para alojamientos como PythonAnywhere (ver wsgi_pythonanywhere.py).
    Variables de entorno: CLAVE_ADMIN (obligatoria en internet), RETO_DB, RETO_JOURNAL, RETO_URL_PUBLICA."""
    if len(os.environ.get("CLAVE_ADMIN", "").strip()) < 10:
        raise RuntimeError("En internet define CLAVE_ADMIN con al menos 10 caracteres (ver wsgi_pythonanywhere.py).")
    preparar()

    def aplicacion(environ, start_response):
        def cab(nombre):
            clave = nombre.upper().replace("-", "_")
            return environ.get(clave if clave in ("CONTENT_LENGTH", "CONTENT_TYPE") else "HTTP_" + clave)

        ruta = environ.get("PATH_INFO", "/") + (("?" + environ["QUERY_STRING"]) if environ.get("QUERY_STRING") else "")
        ip = (
            environ.get("HTTP_X_REAL_IP")
            or environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or environ.get("REMOTE_ADDR", "")
        )
        codigo, tipo, datos, extra = atender(
            environ.get("REQUEST_METHOD", "GET"), ruta, cab, environ["wsgi.input"].read, ip
        )
        cabeceras = [("Content-Type", tipo), ("Content-Length", str(len(datos))), ("X-Content-Type-Options", "nosniff")]
        if "Cache-Control" not in extra:
            cabeceras.append(("Cache-Control", "no-store"))
        cabeceras += list(extra.items())
        start_response(ESTADOS_HTTP.get(codigo, f"{codigo} Error"), cabeceras)
        return [datos]

    return aplicacion


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
    global URLS
    ap = argparse.ArgumentParser(description="Servidor del reto Detectives de la desinformación")
    ap.add_argument("--puerto", type=int, default=8000)
    ap.add_argument("--clave", help="clave del panel docente (si no se da, se genera y se guarda en datos/)")
    ap.add_argument("--db", default=str(DATOS / "reto.db"))
    a = ap.parse_args()

    DATOS.mkdir(exist_ok=True)
    preparar(a.db, a.clave)

    URLS = [f"http://{ip}:{a.puerto}" for ip in ips_locales()] or [f"http://localhost:{a.puerto}"]
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
    print("  ESTUDIANTES (misma red wifi):")
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
