"""
Construye banco_preguntas.json, el banco de preguntas del reto.

Estructura: 3 expedientes de desinformación y lectura (¿Lo compartirías?, Detectives de
chequeos, Lo que dice la ciencia) y 7 casos estadísticos, cada uno con una mecánica distinta
(hipótesis antes de ver los datos, simulador de mezclas, proyección de un año incompleto,
probabilidad condicional, márgenes de error, elección de gráficos, media vs. mediana).

Las respuestas correctas de las preguntas con datos se CALCULAN aquí a partir de los archivos
limpios de ../1_Analisis_de_datos (no se escriben a mano). Cada clave que depende de un hecho
de los datos va acompañada de una comprobación (exigir): si los datos cambian y la clave deja
de ser cierta, el banco no se construye.

    python construir_banco.py

Requisito: haber corrido antes generar_analisis.py (está en esta misma carpeta).
"""

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]  # carpeta Reto_Desinformacion_Colegios
ANALISIS = RAIZ / "1_Analisis_de_datos"
SALIDA = RAIZ / "2_Aplicacion_Reto" / "banco_preguntas.json"
PUNTOS_TOTALES = 1000

CC = pd.read_csv(ANALISIS / "01_Colombiacheck_chequeos_verificados/datos/colombiacheck_verificado_limpio.csv")
H = pd.read_csv(ANALISIS / "02_DANE_ENTIC_horas_uso_internet/datos/dane_entic2024_horas_uso_internet_limpio.csv")
A = pd.read_csv(ANALISIS / "03_DANE_ENTIC_actividades_internet/datos/dane_entic2024_actividades_internet_limpio.csv")

FUENTE_CC = "Colombiacheck (Consejo de Redacción), chequeos con marcado ClaimReview, 2020–2026"
FUENTE_DANE = "DANE, Encuesta TIC en Hogares (ENTIC) 2024"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
ELECCIONES = {
    "2022-03": "Legislativas 2022",
    "2022-05": "Presidencial 2022 (1.ª vuelta)",
    "2022-06": "Presidencial 2022 (2.ª vuelta)",
    "2023-10": "Locales 2023",
    "2026-03": "Legislativas 2026",
    "2026-05": "Presidencial 2026 (1.ª vuelta)",
    "2026-06": "Presidencial 2026 (2.ª vuelta)",
}


def num(v, dec=1):
    return f"{v:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def exigir(condicion, mensaje):
    """La clave de una pregunta depende de un hecho de los datos: si deja de ser cierto, no se construye."""
    if not condicion:
        sys.exit(f"[error] la clave ya no coincide con los datos: {mensaje}")


# La afirmación verificada llega recortada a 75 caracteres en ClaimReview. Casi siempre es una frase completa;
# estas dos quedaron cortadas a mitad de palabra (revisado a mano): se quita la palabra rota y se pone «…».
RECORTADAS = {
    "video-de-supuesta-anaconda-gigante-en-el-rio-amazonas-fue-creado",
    "bomberos-no-han-advertido-sobre-nuevos-temblores-como-afirman-audios",
}


def chequeo(slug, calificacion):
    fila = CC[CC["url"].str.contains(slug, regex=False)]
    if len(fila) != 1:
        sys.exit(f"[error] el chequeo '{slug}' aparece {len(fila)} veces en los datos")
    f = fila.iloc[0]
    if f["calificacion"] != calificacion:
        sys.exit(f"[error] '{slug}' tiene calificación {f['calificacion']}, se esperaba {calificacion}")
    afirm = f["afirmacion_verificada"].strip()
    if slug in RECORTADAS:
        afirm = afirm.rsplit(" ", 1)[0] + "…"
    return {"afirmacion": afirm, "titulo": f["titulo"].strip(), "url": f["url"], "calificacion": f["calificacion"]}


def tot(df, ambito="Total nacional", sexo="Total"):
    return df[(df["ambito"] == ambito) & (df["sexo"] == sexo)].iloc[0]


# --------------------------------------------------------------------------- datos derivados
CC["fecha"] = pd.to_datetime(CC["fecha"])
N_CC = len(CC)
xa = pd.crosstab(CC["anio"], CC["calificacion"])
xa["total"] = xa.sum(axis=1)
xa["pct_falso"] = xa["Falso"] / xa["total"] * 100
FIN_CC = CC["fecha"].max()
tit = CC["titulo"].str.lower()
CC["ia"] = tit.str.contains(r"\bia\b|inteligencia artificial", regex=True)
CC["video"] = tit.str.contains(r"\bv[ií]deos?\b", regex=True)
CC["foto"] = tit.str.contains(r"\bfotos?\b|\bim[aá]gen(?:es)?\b", regex=True)
CC["falso"] = CC["calificacion"] == "Falso"
ia_anio = CC.groupby("anio")["ia"].sum().astype(int)
ia_pct = CC.groupby("anio")["ia"].mean() * 100
video_pct = CC.groupby("anio")["video"].mean() * 100
foto_pct = CC.groupby("anio")["foto"].mean() * 100

nac_h = tot(H)
urb_h, rur_h = tot(H, "Cabecera (urbano)"), tot(H, "Rural")
hom_h, muj_h = tot(H, sexo="Hombres"), tot(H, sexo="Mujeres")
dep_h = H[(H["nivel"] == "DEPARTAMENTO") & (H["sexo"] == "Total")].set_index("ambito")
act_urb, act_rur = tot(A, "Cabecera (urbano)"), tot(A, "Rural")


# --------------------------------------------------------------------------- piezas reutilizables
def grafico(  # noqa: PLR0913
    tipo,
    titulo,
    etiquetas,
    series,
    unidad="",
    decimales=0,
    subtitulo="",
    fuente="",
    valores=True,
    tooltips=True,
    y_min=None,
    y_max=None,
    destacar=None,
    x_max=None,
    letra=None,
    margenes=None,
):
    g = {
        "tipo": tipo,
        "titulo": titulo,
        "subtitulo": subtitulo,
        "fuente": fuente,
        "etiquetas": [str(e) for e in etiquetas],
        "unidad": unidad,
        "decimales": decimales,
        "series": [{"nombre": n, "valores": [round(float(v), 4) for v in vals]} for n, vals in series],
        "valores_visibles": valores,
        "tooltips": tooltips,
    }
    for k, v in (
        ("y_min", y_min),
        ("y_max", y_max),
        ("destacar", destacar),
        ("x_max", x_max),
        ("letra", letra),
        ("margenes", margenes),
    ):
        if v is not None:
            g[k] = v
    return g


def tabla(titulo, columnas, filas, subtitulo="", fuente="", letra=None):
    """Una tabla como pieza del expediente de evidencia."""
    return {
        "tipo": "tabla",
        "titulo": titulo,
        "subtitulo": subtitulo,
        "fuente": fuente,
        "letra": letra,
        "columnas": columnas,
        "filas": filas,
        "series": [],
        "etiquetas": [],
    }


def dispersion(titulo, puntos, eje_x, eje_y, unidad_x="", unidad_y="", subtitulo="", fuente="", letra=None):  # noqa: PLR0913
    return {
        "tipo": "dispersion",
        "titulo": titulo,
        "subtitulo": subtitulo,
        "fuente": fuente,
        "letra": letra,
        "eje_x": eje_x,
        "eje_y": eje_y,
        "unidad_x": unidad_x,
        "unidad_y": unidad_y,
        "tooltips": True,
        "valores_visibles": True,
        "decimales": 1,
        "etiquetas": [p["etiqueta"] for p in puntos],
        "series": [{"nombre": eje_y, "valores": [p["y"] for p in puntos]}],
        "puntos": puntos,
    }


def opciones(*pares):
    ops, correctas = [], []
    for i, (texto, ok) in enumerate(pares):
        oid = "abcdefgh"[i]
        ops.append({"id": oid, "texto": texto})
        if ok:
            correctas.append(oid)
    return ops, correctas


def q_opcion(qid, enunciado, pares, puntos, explicacion, **extra):
    ops, ok = opciones(*pares)
    assert len(ok) == 1, qid
    return {
        "id": qid,
        "tipo": "opcion",
        "enunciado": enunciado,
        "opciones": ops,
        "respuesta": ok[0],
        "puntos": puntos,
        "explicacion": explicacion,
        **extra,
    }


def q_multiple(qid, enunciado, pares, puntos, explicacion, **extra):
    ops, ok = opciones(*pares)
    return {
        "id": qid,
        "tipo": "multiple",
        "enunciado": enunciado,
        "opciones": ops,
        "respuesta": ok,
        "puntos": puntos,
        "explicacion": explicacion,
        **extra,
    }


def q_hipotesis(qid, enunciado, textos):
    """Hipótesis antes de ver los datos: sin puntos. Al responderla se abre el expediente del caso."""
    return {
        "id": qid,
        "tipo": "opcion",
        "puntos": 0,
        "enunciado": enunciado,
        "opciones": [{"id": "abcdefgh"[i], "texto": t} for i, t in enumerate(textos)],
        "explicacion": "Era tu hipótesis: no daba puntos. Lo importante es compararla con lo que mostraron los datos.",
    }


EVALUAR = [
    {"id": "R", "texto": "Respaldada por los datos"},
    {"id": "C", "texto": "Contradicha por los datos"},
    {"id": "N", "texto": "No se puede saber con estos datos"},
]
GLOSARIO_BASE = [
    {"termino": "Respaldada", "definicion": "La evidencia del expediente la muestra directamente."},
    {"termino": "Contradicha", "definicion": "La evidencia muestra lo contrario, o la frase exagera lo que muestra."},
    {
        "termino": "No se puede saber",
        "definicion": "Los datos no alcanzan: habla de causas, de algo que no se midió "
        "(creencias, lo que circuló) o de otra población.",
    },
]


def q_evaluar(qid, afirmaciones, puntos, enunciado=None, **extra):
    """afirmaciones = [(texto, 'R'|'C'|'N', razón)]"""
    items, resp, razones = [], {}, []
    for i, (texto, clave, razon) in enumerate(afirmaciones):
        iid = f"{qid}_{i + 1}"
        items.append({"id": iid, "texto": texto})
        resp[iid] = clave
        nombre = {"R": "Respaldada", "C": "Contradicha", "N": "No se puede saber"}[clave]
        razones.append(f"«{texto}» → {nombre}: {razon}")
    return {
        "id": qid,
        "tipo": "clasificar",
        "estilo": "expediente",
        "puntos": puntos,
        "categorias": EVALUAR,
        "enunciado": enunciado
        or "Con la evidencia del expediente, decide si cada afirmación está respaldada, "
        "contradicha o si los datos no permiten saberlo.",
        "items": items,
        "respuesta": resp,
        "explicacion": " ".join(razones),
        **extra,
    }


def q_construir(qid, partes, puntos, explicacion, enunciado=None, **extra):
    """partes = [(etiqueta, [(texto, correcta)])]. Arma la conclusión pieza por pieza."""
    ps, resp = [], {}
    for i, (etiqueta, pares) in enumerate(partes):
        ops, ok = opciones(*pares)
        assert len(ok) == 1, qid
        pid = f"parte{i + 1}"
        ps.append({"id": pid, "etiqueta": etiqueta, "opciones": ops})
        resp[pid] = ok[0]
    return {
        "id": qid,
        "tipo": "construir",
        "puntos": puntos,
        "partes": ps,
        "respuesta": resp,
        "enunciado": enunciado
        or "Arma la conclusión del caso como lo haría un investigador: una afirmación, "
        "la evidencia que la sostiene y la limitación que hay que declarar.",
        "explicacion": explicacion,
        **extra,
    }


def caso(cid, numero, titulo, idea, encargo, preguntas, glosario=(), dossier=None):  # noqa: PLR0913
    m = {
        "id": cid,
        "titulo": f"Caso {numero} · {titulo}",
        "subtitulo": f"Laboratorio · {idea}",
        "intro": encargo,
        "glosario": list(GLOSARIO_BASE) + list(glosario),
        "preguntas": preguntas,
    }
    if dossier:
        m["dossier"] = dossier
    return m


# =========================================================================== 01 · ¿Lo compartirías?
POSTS = [
    ("colombia-si-tiene-el-10-de-la-biodiversidad-del-planeta", "Verdadero", "Publicación viral"),
    ("youtube-si-dijo-que-eliminaria-videos-que-contradigan-la-oms", "Verdadero", "Mensaje reenviado"),
    ("camilo-romero-acerto-en-su-afirmacion-sobre-la-menor-participacion", "Verdadero", "Publicación viral"),
    ("es-cierto-la-estatua-de-colon-en-ciudad-de-mexico-sera-reemplazada", "Verdadero", "Noticia compartida"),
    ("de-nuevo-no-es-cierto-que-la-tierra-esta-en-peligro-por-rayos-cosmicos", "Falso", "Reenviado muchas veces"),
    ("comer-platano-o-banano-no-bloquea-la-entrada-del-coronavirus", "Falso", "Reenviado muchas veces"),
    ("boton-de-unirme-en-whatsapp-es-una-tactica-de-hackeo", "Falso", "Mensaje reenviado"),
    ("la-nasa-no-ha-dicho-que-la-tierra-sera-impactada-por-un-asteroide", "Falso", "Publicación viral"),
    ("maculopatia-no-es-igual-cancer-de-ojo-ni-es-causada-por-la-luz-del-cel", "Falso", "Reenviado muchas veces"),
    ("no-espana-no-aprobo-dni-para-perros-y-gatos-en-enero-de-2022", "Falso", "Noticia compartida"),
]


# Ajustes de redacción para estudiantes (siglas o abreviaturas que confunden); no cambian el sentido
AJUSTES_TEXTO = {"en el DF": "en Ciudad de México", "COVID19": "COVID-19", "Nasa dijo": "La NASA dijo"}


def claro(texto):
    for a, b in AJUSTES_TEXTO.items():
        texto = texto.replace(a, b)
    return texto


def mision_compartir():
    pubs, resp = [], {}
    for i, (slug, cal_esperada, encabezado) in enumerate(POSTS):
        c = chequeo(slug, cal_esperada)
        pid = f"p{i + 1}"
        pubs.append(
            {"id": pid, "texto": claro(c["afirmacion"]), "encabezado": encabezado, "_titulo_chequeo": c["titulo"]}
        )
        resp[pid] = "V" if cal_esperada == "Verdadero" else "F"
    expl = "Las 10 publicaciones son afirmaciones reales verificadas por Colombiacheck. " + " ".join(
        f"«{p['texto']}»: {'VERDADERO' if resp[p['id']] == 'V' else 'FALSO'} ({p['_titulo_chequeo']})." for p in pubs
    )
    publicas = [{k: v for k, v in p.items() if not k.startswith("_")} for p in pubs]
    prompt = chequeo("ave-incluida-en-banners-de-la-presidencia-de-colombia-no-existe", "Verdadero")
    return {
        "id": "m1",
        "titulo": "¿Lo compartirías?",
        "subtitulo": "Desinformación · el experimento de la clase",
        "intro": "Vas a ver 10 afirmaciones reales que circularon en Colombia: algunas en redes y WhatsApp, otras "
        "dichas por figuras públicas o publicadas como noticia. Todas fueron revisadas por Colombiacheck. "
        "Primero decide, con "
        "honestidad, si las compartirías: esa parte NO da ni quita puntos. Después dirás si crees que "
        "son verdaderas o falsas: esa parte SÍ da puntos. Al final, el tablero mostrará qué hizo la clase "
        "y lo compararemos con el estudio de Nature.",
        "preguntas": [
            {
                "id": "m1_recordatorio",
                "tipo": "recordatorio",
                "puntos": 0,
                "solo_grupo": "B",
                "enunciado": "Antes de empezar: queremos probar un titular para futuros retos. Según lo que sabes, "
                "¿este titular es exacto?",
                "publicaciones": [{"id": "r1", "texto": prompt["afirmacion"], "encabezado": "Titular de prueba"}],
                "categorias": [{"id": "V", "texto": "Exacto"}, {"id": "F", "texto": "No exacto"}],
                "explicacion": "Esta pregunta era el «recordatorio de exactitud» del estudio de Nature: a la mitad de "
                "la clase (elegida al azar) se le pidió pensar en la exactitud de un titular antes de "
                "decidir qué compartir. No daba puntos.",
            },
            {
                "id": "m1_compartir",
                "tipo": "compartir",
                "puntos": 0,
                "experimento": "compartir",
                "enunciado": "Si vieras estas publicaciones en tus redes, ¿las compartirías? (No da puntos: responde "
                "lo que de verdad harías.)",
                "publicaciones": publicas,
                "categorias": [{"id": "S", "texto": "La compartiría"}, {"id": "N", "texto": "No la compartiría"}],
                "explicacion": "Esta parte no daba puntos: medía qué compartiría la clase para compararlo con lo que cree.",  # noqa: E501
            },
            {
                "id": "m1_veracidad",
                "tipo": "clasificar",
                "puntos": 120,
                "experimento": "veracidad",
                "requiere": "m1_compartir",
                "estilo": "publicaciones",
                "enunciado": "Ahora sí, con puntos: ¿cada publicación es verdadera o falsa?",
                "items": [{"id": p["id"], "texto": p["texto"], "encabezado": p["encabezado"]} for p in publicas],
                "categorias": [{"id": "V", "texto": "Verdadera"}, {"id": "F", "texto": "Falsa"}],
                "respuesta": resp,
                "explicacion": expl,
            },
        ],
    }


# =========================================================================== 02 · Detectives de chequeos
TRAMPAS = [
    {"id": "IA", "texto": "Creado o alterado con IA"},
    {"id": "CTX", "texto": "Real, pero de otro lugar o fecha"},
    {"id": "EST", "texto": "Estafa: busca tu dinero o tus datos"},
    {"id": "CITA", "texto": "Frase o mensaje atribuido falsamente"},
    {"id": "ALA", "texto": "Alarma o falsa ciencia sin fundamento"},
]
EXPEDIENTES = [  # cuatro juegos equivalentes: cada estudiante recibe uno
    [
        ("video-de-supuesta-anaconda-gigante-en-el-rio-amazonas-fue-creado", "IA"),
        ("video-del-rescate-de-un-gatito-entre-escombros-fue-grabado-en-brasil", "CTX"),
        ("ojo-un-supuesto-mensaje-de-instagram-sobre-haber-infringido-sus-reglas", "EST"),
        ("ustedes-que-ya-no-creen-no-esperan-no-oran-circula-mensaje-falsamente", "CITA"),
        ("cadena-de-domo-atmosferico-de-calor-en-los-proximos-dias-en-colombia", "ALA"),
    ],
    [
        ("este-video-en-el-que-suben-una-ballena-un-barco-para-quitarle-percebes", "IA"),
        ("video-de-desbordamiento-de-agua-en-el-parque-el-virrey-en-bogota-es-de", "CTX"),
        ("gobierno-no-esta-regalando-paneles-solares-como-dice-anuncio-en-facebo", "EST"),
        ("el-maravilloso-mensaje-sobre-lo-rapido-que-se-va-la-vida-que-le-atribu", "CITA"),
        ("bomberos-no-han-advertido-sobre-nuevos-temblores-como-afirman-audios", "ALA"),
    ],
    [
        ("imagen-de-falso-gato-serpiente-que-circula-en-redes-fue-creada-con-int", "IA"),
        ("esta-foto-no-muestra-una-lluvia-de-peces-sino-el-accidente-de-un-camio", "CTX"),
        ("cuidado-esta-pagina-que-muestra-supuesta-entrevista-de-carlos-calero", "EST"),
        ("el-papa-no-dijo-come-lo-que-quieras-en-semana-santa", "CITA"),
        ("falso-tormenta-solar-no-causara-terremotos-en-los-proximos-dias", "ALA"),
    ],
    [
        ("esta-imagen-no-muestra-la-cuenca-oriental-de-la-luna-ni-es-de-la-misio", "IA"),
        ("este-video-no-es-de-tsunami-por-terremoto-de-turquia-en-2023-sino-de-s", "CTX"),
        ("otra-falsa-oferta-de-empleo-de-almacenes-exito-circula-en-facebook", "EST"),
        ("falso-que-casio-respondio-shakira-en-twitter-por-su-nueva-cancion", "CITA"),
        ("cancer-no-es-causado-por-un-hongo-ni-se-cura-con-bicarbonato-de-sodio", "ALA"),
    ],
]
VEREDICTOS = [
    ("el-luchador-javier-blair-reyes-si-expuso-una-bandera-con-un-mensaje", "Verdadero", "V"),
    ("si-minsalud-confirmo-que-en-bogota-hay-una-paciente-con-coronavirus", "Verdadero", "V"),
    ("covid-19-si-tiene-sintomas-similares-la-gripa-pero-es-mucho-mas-contagiosa", "Verdadero pero...", "VP"),
    ("si-detectaron-gripe-aviar-en-filipinas-pero-no-es-nueva", "Verdadero pero...", "VP"),
    ("trino-hace-comparacion-cuestionable-sobre-la-magnitud-de-los-terremoto", "Cuestionable", "C"),
    ("usuario-de-tiktok-exagera-sobre-inflacion-estancamiento-economico", "Cuestionable", "C"),
    ("es-falso-que-les-apliquen-una-fotomulta-quienes-usen-dispositivos", "Falso", "F"),
    ("es-falso-que-vacunas-contra-covid-19-dejen-el-brazo-imantado", "Falso", "F"),
]


def mision_detectives():
    nombres = {t["id"]: t["texto"] for t in TRAMPAS}
    variantes = []
    for juego in EXPEDIENTES:
        items, resp, lineas = [], {}, []
        for i, (slug, trampa) in enumerate(juego):
            c = chequeo(slug, "Falso")
            iid = f"e{i + 1}"
            items.append({"id": iid, "texto": c["titulo"], "detalle": f"Lo que circulaba: «{c['afirmacion']}»"})
            resp[iid] = trampa
            lineas.append(f"«{c['titulo']}» → {nombres[trampa]}.")
        variantes.append({"items": items, "respuesta": resp, "explicacion": " ".join(lineas)})
    items, resp, lineas = [], {}, []
    for i, (slug, cal_esp, cod) in enumerate(VEREDICTOS):
        c = chequeo(slug, cal_esp)
        iid = f"v{i + 1}"
        items.append({"id": iid, "texto": c["titulo"], "detalle": f"Lo que circulaba: «{c['afirmacion']}»"})
        resp[iid] = cod
        lineas.append(f"«{c['titulo']}» → {cal_esp}.")
    return {
        "id": "m2",
        "titulo": "Detectives de chequeos",
        "subtitulo": "Desinformación · leer como verificador",
        "intro": "Un chequeo tiene dos partes: lo que circulaba y lo que encontró el verificador. Aprender a leer "
        "esas conclusiones es la mitad del trabajo.",
        "glosario": [
            {"termino": "Verdadero", "definicion": "La afirmación es correcta."},
            {
                "termino": "Verdadero, pero…",
                "definicion": "Es correcta en lo esencial, pero le falta contexto o tiene "
                "una imprecisión menor que no cambia su sentido.",
            },
            {
                "termino": "Cuestionable",
                "definicion": "Mezcla algo cierto con exageraciones, comparaciones "
                "tramposas o imprecisiones que sí cambian su sentido.",
            },
            {"termino": "Falso", "definicion": "La afirmación es incorrecta, inventada o manipulada."},
        ],
        "preguntas": [
            {
                "id": "m2_trampas",
                "tipo": "clasificar",
                "puntos": 65,
                "estilo": "expediente",
                "enunciado": "Lee lo que encontró el verificador y clasifica la TRAMPA que se usó en cada caso. Cada "
                "trampa aparece una sola vez.",
                "categorias": TRAMPAS,
                "variantes": variantes,
            },
            {
                "id": "m2_veredicto",
                "tipo": "clasificar",
                "puntos": 75,
                "estilo": "expediente",
                "enunciado": "El veredicto: según el titular del chequeo, ¿qué calificación le dio Colombiacheck a cada "  # noqa: E501
                "afirmación? Usa el glosario (hay dos de cada una).",
                "categorias": [
                    {"id": "V", "texto": "Verdadero"},
                    {"id": "VP", "texto": "Verdadero, pero…"},
                    {"id": "C", "texto": "Cuestionable"},
                    {"id": "F", "texto": "Falso"},
                ],
                "items": items,
                "respuesta": resp,
                "explicacion": "Pistas: «sí…» sin peros = Verdadero; «sí…, pero…» = Verdadero, pero…; «cuestionable», "
                "«exagera» = Cuestionable; «es falso que…» = Falso. " + " ".join(lineas),
            },
        ],
    }


# =========================================================================== CASO 1 · hipótesis → evidencia
def caso_elecciones():
    m = CC.groupby(CC["fecha"].dt.to_period("M")).agg(chequeos=("url", "size"), elec=("tema_electoral", "sum"))
    m.index = m.index.astype(str)
    m = m.loc["2022-01":]
    m["pct"] = m["elec"] / m["chequeos"] * 100
    es_e = m.index.isin(list(ELECCIONES))
    con, sin = m[es_e], m[~es_e]
    etq = [f"{MESES[int(i[5:]) - 1]} {i[2:4]}" for i in m.index]
    idx_e = [int(i) for i, v in enumerate(es_e) if v]
    ratio_vol = con["chequeos"].mean() / sin["chequeos"].mean()
    pct_sin, pct_oct23, pct_jun26 = sin["pct"].mean(), m.loc["2023-10", "pct"], m.loc["2026-06", "pct"]
    anual = xa.loc[2020:2025, "total"]
    exigir(con["pct"].mean() > 3 * pct_sin, "la agenda electoral sube en meses de votación")
    exigir(ratio_vol < 1.5, "el volumen no sube 50 % en meses de votación")
    exigir(35 <= pct_jun26 <= 50, "jun-2026 ~ 4 de cada 10")
    exigir(pct_sin < 8, "fuera de elecciones el tema casi desaparece")
    exigir(anual.max() / anual.min() < 1.25, "volumen anual estable")
    razon = pct_oct23 / pct_sin
    req = {"requiere": "c1_hipotesis"}
    return caso(
        "c1",
        1,
        "¿Las elecciones disparan la desinformación?",
        "hipótesis y evidencia",
        "Encargo: un concejal dijo en la radio que «en elecciones todo se llena de noticias falsas». Tu editora te "
        "pide comprobarlo con 57 meses de chequeos (2022–2026), que incluyen siete jornadas electorales. Un buen "
        "analista anota su hipótesis ANTES de mirar los datos: el expediente se abre cuando la registres.",
        [
            q_hipotesis(
                "c1_hipotesis",
                "Tu hipótesis, antes de ver los datos (sin puntos): en los meses de "
                "elecciones, ¿qué crees que pasa con los chequeos que publica Colombiacheck?",
                [
                    "Se multiplican: el doble o más que en un mes normal",
                    "Suben un poco",
                    "Casi no cambian en cantidad, pero cambian de tema",
                    "Bajan, porque el equipo se dedica a cubrir las elecciones",
                ],
            ),
            q_evaluar(
                "c1_evaluar",
                [
                    (
                        "En los meses de elecciones, la parte de chequeos dedicada a temas electorales sube claramente",
                        "R",
                        f"en B, {num(con['pct'].mean())} % en meses de votación vs. {num(pct_sin)} % en el resto.",
                    ),
                    (
                        "En los meses de elecciones Colombiacheck publicó al menos un 50 % más de chequeos que en un mes típico",  # noqa: E501
                        "C",
                        f"en A, los meses de votación tienen en promedio {num(con['chequeos'].mean())} chequeos vs. "
                        f"{num(sin['chequeos'].mean())}: solo {num((ratio_vol - 1) * 100, 0)} % más.",
                    ),
                    (
                        "En junio de 2026 (segunda vuelta presidencial), cerca de 4 de cada 10 chequeos fueron sobre elecciones",  # noqa: E501
                        "R",
                        f"en B, {num(pct_jun26)} %.",
                    ),
                    (
                        "Fuera de época electoral, el tema electoral casi desaparece de lo que se verifica",
                        "R",
                        f"en B, los meses sin votación promedian {num(pct_sin)} %.",
                    ),
                    (
                        "Durante las elecciones circuló más desinformación electoral en las redes",
                        "N",
                        "los datos dicen qué VERIFICÓ el medio, no qué circuló; pudo haber más o lo mismo.",
                    ),
                    (
                        "Las elecciones hacen que la gente crea más en noticias falsas",
                        "N",
                        "ningún gráfico mide lo que la gente cree.",
                    ),
                ],
                36,
                **req,
            ),
            {
                "id": "c1_razon",
                "tipo": "numero",
                "puntos": 18,
                "tolerancia": 0.3,
                "unidad": "veces",
                **req,
                "enunciado": f"Usa el Gráfico B (pasa el cursor sobre «oct 23», elecciones locales de 2023). En los "
                f"meses SIN elecciones, en promedio el {num(pct_sin)} % de los chequeos fue sobre elecciones. "
                f"¿Cuántas VECES mayor fue esa proporción en octubre de 2023? (Un decimal.)",
                "respuesta": round(float(razon), 2),
                "explicacion": f"{num(pct_oct23)} % ÷ {num(pct_sin)} % ≈ {num(razon)} veces. Comparar proporciones "
                f"(«qué parte del total») permite ver un cambio que el conteo total esconde.",
            },
            q_construir(
                "c1_conclusion",
                [
                    (
                        "Conclusión principal",
                        [
                            (
                                "Las elecciones casi no cambian CUÁNTO verifica el medio, pero sí cambian DE QUÉ se ocupa",  # noqa: E501
                                True,
                            ),
                            (
                                "Las elecciones aumentan mucho el número de chequeos, porque en esos meses circula más "
                                "desinformación",
                                False,
                            ),
                            (
                                "El tema electoral es lo que más verifica Colombiacheck a lo largo de todo el periodo",
                                False,
                            ),
                            (
                                "En elecciones se verifica más contenido electoral porque la gente cree más en noticias falsas "  # noqa: E501
                                "en esas fechas",
                                False,
                            ),
                        ],
                    ),
                    (
                        "Evidencia que la sostiene",
                        [
                            (
                                "A y C: el volumen mensual y anual es casi estable; B: la parte electoral se dispara justo en "  # noqa: E501
                                "los meses de votación",
                                True,
                            ),
                            (
                                "A: los meses de votación son, uno por uno, los picos más altos de toda la serie mensual",  # noqa: E501
                                False,
                            ),
                            (
                                "B: la parte electoral se mantiene alta todo el tiempo, también fuera de época de elecciones",  # noqa: E501
                                False,
                            ),
                            ("C: el número de chequeos por año crece a medida que se acercan las elecciones", False),
                        ],
                    ),
                    (
                        "Limitación que hay que declarar",
                        [
                            (
                                "Muestra lo que el verificador decidió revisar, con un equipo de tamaño fijo, no cuánta "  # noqa: E501
                                "desinformación electoral circuló",
                                True,
                            ),
                            ("Incluye una sola jornada electoral, así que no permite comparar entre elecciones", False),
                            (
                                "Los meses tienen distinta cantidad de días, por eso sus porcentajes no se pueden comparar",  # noqa: E501
                                False,
                            ),
                            (
                                "Los datos vienen de una encuesta a ciudadanos y dependen de lo que la gente recuerde",
                                False,
                            ),
                        ],
                    ),
                ],
                36,
                "Un verificador tiene capacidad casi fija (C: entre "
                f"{num(anual.min(), 0)} y {num(anual.max(), 0)} chequeos al año). En elecciones no publica mucho más "
                "(A), pero dedica una parte mucho mayor a temas electorales (B). Eso describe su agenda, no el "
                "volumen de desinformación que circuló. Compara con tu hipótesis: ¿acertaste?",
                **req,
            ),
        ],
        glosario=[
            {
                "termino": "Conteo vs. proporción",
                "definicion": "Un conteo dice cuántos; una proporción dice qué parte del total.",
            }
        ],
        dossier={
            "titulo": "Expediente de evidencia · Caso 1",
            "revelar_tras": "c1_hipotesis",
            "graficos": [
                grafico(
                    "columnas",
                    "Chequeos publicados por mes",
                    etq,
                    [("Chequeos", m["chequeos"].tolist())],
                    subtitulo="Naranja = mes con elecciones",
                    fuente=FUENTE_CC,
                    valores=False,
                    destacar=idx_e,
                    letra="A",
                ),
                grafico(
                    "columnas",
                    "% de los chequeos del mes sobre elecciones",
                    etq,
                    [("% sobre elecciones", m["pct"].round(1).tolist())],
                    unidad="%",
                    decimales=1,
                    subtitulo="Título o afirmación con palabras como voto, candidato, registraduría, jurado, tarjetón",
                    fuente=FUENTE_CC,
                    valores=False,
                    destacar=idx_e,
                    letra="B",
                ),
                grafico(
                    "columnas",
                    "Chequeos por año (años completos)",
                    list(anual.index),
                    [("Chequeos", anual.tolist())],
                    fuente=FUENTE_CC,
                    letra="C",
                ),
            ],
        },
    )


# =========================================================================== CASO 2 · simulador de mezclas
def caso_composicion():
    tipos = ["Contenido viral en redes", "Discurso público"]
    orden_cal = ["Falso", "Cuestionable", "Verdadero pero...", "Verdadero"]
    xt = pd.crosstab(CC["tipo"], CC["calificacion"], normalize="index").reindex(columns=orden_cal) * 100
    n_t = CC["tipo"].value_counts()
    por_anio = pd.crosstab(CC["anio"], CC["tipo"])
    pf = CC.groupby(["anio", "tipo"])["calificacion"].apply(lambda s: (s == "Falso").mean() * 100).unstack()
    anios = list(range(2020, 2026))
    redes, disc, total = pf.loc[anios, tipos[0]], pf.loc[anios, tipos[1]], xa.loc[anios, "pct_falso"]
    f_redes, f_disc = xt.loc[tipos[0], "Falso"], xt.loc[tipos[1], "Falso"]
    meta = 75.0
    p_meta = (f_redes - meta) / (f_redes - f_disc) * 100
    share22 = por_anio.loc[2022, tipos[1]] / por_anio.loc[2022].sum() * 100
    exigir(xt.loc[tipos[1], "Cuestionable"] > 2 * xt.loc[tipos[0], "Cuestionable"], "discurso mucho más cuestionable")
    exigir(por_anio.loc[2024:, tipos[1]].max() <= 15, "discurso casi desaparece desde 2024")
    exigir(not redes.is_monotonic_increasing, "redes no crece sin parar")
    exigir((redes > disc).all(), "redes más Falso que discurso todos los años")
    exigir(redes[2025] - redes[2023] > 3, "redes también subió entre 2023 y 2025")
    exigir(5 < p_meta < 20, "la meta del simulador es alcanzable")
    brecha22, brecha25 = redes[2022] - total[2022], redes[2025] - total[2025]
    return caso(
        "c2",
        2,
        "¿Más falso… o distinto?",
        "promedios y mezclas",
        f"Encargo: un titular celebra que «lo que circula hoy es más falso que nunca: {num(total[2025])} % de "
        f"los chequeos son Falsos» (en 2022 eran {num(total[2022])} %). Colombiacheck verifica dos cosas distintas: "
        f"contenido viral en redes (publicaciones, videos y cadenas que circulan) y discurso público (lo que dicen "
        f"políticos y figuras públicas). En los dos grupos hay cosas falsas y cosas ciertas: el grupo dice DÓNDE "
        f"circuló, la calificación dice si era verdad. Antes "
        f"de repetir el titular, usa el simulador para entender cómo se mueve un promedio cuando cambia la mezcla.",
        [
            {
                "id": "c2_simulador",
                "tipo": "numero",
                "puntos": 25,
                "tolerancia": 0.5,
                "unidad": "%",
                "simulador": {
                    "etiqueta": "Parte de los chequeos que es discurso público",
                    "min": 0,
                    "max": 40,
                    "paso": 0.1,
                    "inicial": 0,
                    "unidad": "%",
                    "resultado": "% Falso del total",
                    "decimales": 1,
                    "grupos": [
                        {"nombre": "Contenido viral en redes", "valor": round(float(f_redes), 2)},
                        {"nombre": "Discurso público", "valor": round(float(f_disc), 2)},
                    ],
                },
                "enunciado": f"Simulador: en todo el periodo, el contenido de redes es Falso el {num(f_redes)} % de las "  # noqa: E501
                f"veces y el discurso público el {num(f_disc)} % (Gráfico A). Mueve el deslizador: ¿qué "
                f"porcentaje de discurso público tendría que haber en la mezcla para que el % Falso TOTAL "
                f"fuera exactamente {num(meta, 0)} %? (Un decimal; también lo puedes despejar.)",
                "respuesta": round(float(p_meta), 2),
                "explicacion": f"Total = {num(f_redes)} × (1 − p) + {num(f_disc)} × p = {num(meta, 0)} → p = "
                f"({num(f_redes)} − {num(meta, 0)}) ÷ ({num(f_redes)} − {num(f_disc)}) ≈ {num(p_meta)} %. "
                f"Ninguno de los dos grupos cambió: solo la mezcla. En 2022 el discurso público era el "
                f"{num(share22)} % de los chequeos.",
            },
            q_evaluar(
                "c2_evaluar",
                [
                    (
                        "Las afirmaciones de discurso público terminan en «Cuestionable» con mucha más frecuencia que el "  # noqa: E501
                        "contenido de redes",
                        "R",
                        f"A: {num(xt.loc[tipos[1], 'Cuestionable'])} % vs. {num(xt.loc[tipos[0], 'Cuestionable'])} %.",
                    ),
                    (
                        "Desde 2024 Colombiacheck casi dejó de verificar discurso público",
                        "R",
                        f"C: {', '.join(str(int(v)) for v in por_anio.loc[2024:, tipos[1]])} chequeos en 2024–2026.",
                    ),
                    (
                        "Dentro del contenido de redes, el % de Falso crece sin parar año tras año",
                        "C",
                        "B: la línea de redes baja hasta 2022–2023 y luego sube; no crece siempre.",
                    ),
                    (
                        "El aumento del % Falso total entre 2023 y 2025 se explica SOLO porque hubo menos discurso público",  # noqa: E501
                        "C",
                        f"B: las redes por sí solas también subieron ({num(redes[2023])} % → {num(redes[2025])} %); la mezcla "  # noqa: E501
                        f"explica una parte, no todo.",
                    ),
                    (
                        "Los políticos dicen menos mentiras que las redes sociales",
                        "N",
                        "el verificador elige QUÉ afirmaciones revisar y las califica con criterios distintos; no es una "  # noqa: E501
                        "muestra de todo lo que dicen.",
                    ),
                ],
                30,
            ),
            q_opcion(
                "c2_brecha",
                f"En 2022 el % Falso total ({num(total[2022])} %) quedó {num(brecha22)} puntos por DEBAJO del de "
                f"redes ({num(redes[2022])} %). En 2025 la diferencia fue de solo {num(brecha25)} puntos. ¿Por qué "
                f"se cerró la brecha?",
                [
                    (
                        "Porque en 2022 una parte de los chequeos era discurso público, que rara vez es «Falso», y "
                        "jalaba el promedio total hacia abajo; en 2025 casi todo era contenido de redes",
                        True,
                    ),
                    (
                        "Porque en 2025 se publicaron más chequeos que en 2022, y con más datos el total siempre se "
                        "acerca al de redes",
                        False,
                    ),
                    (
                        "Porque el % de redes se calcula sobre todos los chequeos del año, así que en 2025 los dos "
                        "números son el mismo cálculo",
                        False,
                    ),
                    (
                        "Porque en 2022 hubo errores de calificación que Colombiacheck corrigió en los años siguientes",
                        False,
                    ),
                ],
                15,
                "El total es un promedio ponderado de los dos grupos. Cuando un grupo (discurso público) casi "
                "desaparece (C), el total se pega al otro grupo (redes). Es un efecto de composición.",
            ),
            q_construir(
                "c2_conclusion",
                [
                    (
                        "Conclusión principal",
                        [
                            (
                                "El % Falso total depende de la MEZCLA de lo que se verifica: al dejar de revisar discurso "  # noqa: E501
                                "público, el total sube aunque las redes cambien menos",
                                True,
                            ),
                            (
                                "El % Falso total subió porque el contenido de redes se volvió más falso año tras año desde "  # noqa: E501
                                "2020",
                                False,
                            ),
                            (
                                "El total subió porque Colombiacheck empezó a calificar con más dureza el discurso público "  # noqa: E501
                                "desde 2024",
                                False,
                            ),
                            (
                                "Los datos muestran que los políticos dicen la verdad más a menudo que las publicaciones de "  # noqa: E501
                                "redes",
                                False,
                            ),
                        ],
                    ),
                    (
                        "Evidencia que la sostiene",
                        [
                            (
                                "A: el discurso público rara vez es «Falso»; C: casi desapareció después de 2023; B: la línea "  # noqa: E501
                                "total se pega a la de redes",
                                True,
                            ),
                            (
                                "B: la línea de redes sube todos los años sin excepción y arrastra con ella al total",
                                False,
                            ),
                            (
                                "A: los chequeos de redes son «Cuestionable» casi tan a menudo como los de discurso público",  # noqa: E501
                                False,
                            ),
                            ("C: los chequeos de discurso público se duplicaron entre 2022 y 2025", False),
                        ],
                    ),
                    (
                        "Precaución que hay que declarar",
                        [
                            (
                                "Comparar promedios totales de años con mezclas distintas puede engañar: hay que mirar cada "  # noqa: E501
                                "grupo por separado",
                                True,
                            ),
                            (
                                "Hay que sumar los porcentajes de los dos tipos para obtener el % Falso total de cada año",  # noqa: E501
                                False,
                            ),
                            ("Los años con pocos chequeos de discurso público invalidan todo el gráfico B", False),
                            ("Como 2026 no tiene discurso público, ningún año se puede comparar con otro", False),
                        ],
                    ),
                ],
                25,
                "Mirar solo el total habría llevado a concluir que «todo se volvió más falso». Separando los "
                "grupos se ve que parte del cambio es de mezcla: menos discurso público (que casi nunca es Falso).",
            ),
        ],
        glosario=[
            {
                "termino": "Promedio ponderado",
                "definicion": "Un total que mezcla grupos según su tamaño: el grupo más grande pesa más.",
            },
            {
                "termino": "Efecto de composición",
                "definicion": "El total cambia porque cambió la MEZCLA de grupos, aunque cada grupo cambie poco.",
            },
        ],
        dossier={
            "titulo": "Expediente de evidencia · Caso 2",
            "graficos": [
                grafico(
                    "columnas",
                    "Calificación según el tipo de chequeo (%)",
                    ["Falso", "Cuestionable", "Verdadero, pero…", "Verdadero"],
                    [(f"{t} (n = {num(n_t[t], 0)})", xt.loc[t].round(1).tolist()) for t in tipos],
                    unidad="%",
                    decimales=1,
                    fuente=FUENTE_CC,
                    letra="A",
                ),
                grafico(
                    "lineas",
                    "% de chequeos «Falso» por año",
                    anios,
                    [
                        ("Total", total.round(1).tolist()),
                        ("Solo redes", redes.round(1).tolist()),
                        ("Solo discurso público", disc.round(1).tolist()),
                    ],
                    unidad="%",
                    decimales=1,
                    y_min=0,
                    y_max=100,
                    fuente=FUENTE_CC,
                    letra="B",
                ),
                grafico(
                    "columnas",
                    "Chequeos de discurso público por año",
                    list(por_anio.index),
                    [("Chequeos de discurso público", por_anio[tipos[1]].tolist())],
                    subtitulo="2026: datos hasta septiembre",
                    fuente=FUENTE_CC,
                    letra="C",
                ),
            ],
        },
    )


# =========================================================================== CASO 3 · año incompleto y proyección
def caso_ia():
    anios = list(ia_anio.index)
    falso_ia = CC.loc[CC["ia"], "falso"].mean() * 100
    falso_no = CC.loc[~CC["ia"], "falso"].mean() * 100
    pct26 = ia_anio[2026] / xa.loc[2026, "total"] * 100
    dia = FIN_CC.dayofyear
    proy = xa.loc[2026, "total"] * 365 / dia
    exigir(ia_anio[2026] < ia_anio[2025], "conteo 2026 < 2025")
    exigir(ia_pct.idxmax() == 2026, "proporción máxima en 2026")
    exigir(falso_ia > 95, "casi todo lo de IA es Falso")
    exigir(video_pct[2026] > 3 * video_pct[2020], "videos ganan peso")
    exigir(ia_anio.loc[:2022].sum() == 0, "sin IA antes de 2023")
    exigir(proy < xa.loc[2020:2025, "total"].min(), "aun proyectado, 2026 tiene menos chequeos")
    etq = [f"{a}*" if a == 2026 else str(a) for a in anios]
    return caso(
        "c3",
        3,
        "La era de la IA",
        "años incompletos y proyecciones",
        f"Encargo: preparas una nota sobre la inteligencia artificial y la desinformación. El problema: los datos "
        f"de 2026 llegan solo hasta el {FIN_CC:%d} de septiembre (día {dia} del año). Comparar ese año «tal cual» con "
        f"años completos sería un error. Vas a usar proporciones y una proyección para no caer en la trampa.",
        [
            q_evaluar(
                "c3_evaluar",
                [
                    (
                        "Los datos muestran que la desinformación con IA empezó a bajar en 2026",
                        "C",
                        f"A cuenta {ia_anio[2026]} casos, pero 2026 está incompleto; en B (proporción) 2026 es el máximo "  # noqa: E501
                        f"({num(ia_pct[2026])} %).",
                    ),
                    (
                        "En proporción al total, 2026 es el año con más chequeos sobre IA",
                        "R",
                        f"B: {num(ia_pct[2026])} % frente a {num(ia_pct[2025])} % en 2025.",
                    ),
                    (
                        "Casi todo lo que Colombiacheck verificó sobre IA terminó calificado «Falso»",
                        "R",
                        f"C: {num(falso_ia)} %.",
                    ),
                    (
                        "Los videos ganaron mucho peso entre lo que se verifica",
                        "R",
                        f"D: de {num(video_pct[2020])} % de los títulos en 2020 a {num(video_pct[2026])} % en 2026.",
                    ),
                    (
                        "Antes de 2023 no existía desinformación hecha con IA",
                        "N",
                        "que ningún título lo mencione no prueba que no existiera: pudo no detectarse o no nombrarse "
                        "(ausencia de evidencia no es evidencia de ausencia).",
                    ),
                ],
                30,
            ),
            {
                "id": "c3_proporcion",
                "tipo": "numero",
                "puntos": 15,
                "tolerancia": 0.1,
                "unidad": "%",
                "tabla": {
                    "columnas": ["Año", "Chequeos con IA en el título", "Chequeos totales"],
                    "filas": [[str(a), str(int(ia_anio[a])), num(xa.loc[a, "total"], 0)] for a in anios],
                },
                "enunciado": "Con la tabla, calcula qué PORCENTAJE de los chequeos de 2026 menciona IA en el título. "
                "(Un decimal.)",
                "respuesta": round(float(pct26), 2),
                "explicacion": f"{ia_anio[2026]} ÷ {num(xa.loc[2026, 'total'], 0)} × 100 = {num(pct26, 2)} %. Con menos "  # noqa: E501
                f"casos que 2025, 2026 tiene una proporción mayor.",
            },
            {
                "id": "c3_proyeccion",
                "tipo": "numero",
                "puntos": 15,
                "tolerancia": 6,
                "unidad": "chequeos",
                "enunciado": f"Proyección: hasta el día {dia} del año, 2026 lleva {num(xa.loc[2026, 'total'], 0)} chequeos "  # noqa: E501
                f"publicados. Si siguiera al MISMO ritmo hasta el 31 de diciembre (día 365), ¿cuántos "
                f"chequeos tendría en total? (Redondea a un número entero.)",
                "respuesta": round(float(proy)),
                "explicacion": f"{num(xa.loc[2026, 'total'], 0)} × 365 ÷ {dia} ≈ {num(proy, 0)} chequeos. Aun proyectado, "  # noqa: E501
                f"2026 tendría menos que cualquier año entre 2020 y 2025 ({num(xa.loc[2020:2025, 'total'].min(), 0)} "
                f"o más). Ojo: una proyección supone que el ritmo no cambia (por ejemplo, diciembre suele "
                f"tener menos chequeos), así que es una estimación, no un dato.",
            },
            q_construir(
                "c3_conclusion",
                [
                    (
                        "Conclusión principal",
                        [
                            (
                                "La IA gana terreno como herramienta de engaño: su peso entre lo verificado sube cada año, "  # noqa: E501
                                "aunque el conteo de 2026 aún no esté completo",
                                True,
                            ),
                            (
                                "La IA empezó a perder fuerza en 2026: ese año se verificaron menos casos que en 2025",
                                False,
                            ),
                            (
                                "La IA ya es la forma principal de desinformación en Colombia, por encima de cualquier otra",  # noqa: E501
                                False,
                            ),
                            (
                                "El contenido hecho con IA resulta verdadero tan a menudo como el resto de lo que se verifica",  # noqa: E501
                                False,
                            ),
                        ],
                    ),
                    (
                        "Evidencia que la sostiene",
                        [
                            (
                                "B: el porcentaje con IA sube cada año hasta 2026; C: casi todo lo de IA es «Falso»; D: los "  # noqa: E501
                                "videos ganan peso",
                                True,
                            ),
                            (
                                "A: el conteo de 2026 es menor que el de 2025, lo que confirma que la tendencia ya cambió",  # noqa: E501
                                False,
                            ),
                            ("C: lo de IA y el resto se califican «Falso» en proporciones muy parecidas", False),
                            ("D: las fotos crecen mucho más rápido que los videos, señal de imágenes generadas", False),
                        ],
                    ),
                    (
                        "Limitación que hay que declarar",
                        [
                            (
                                "Se cuentan palabras en el título (un chequeo de IA que no lo diga no se cuenta) y 2026 es un "  # noqa: E501
                                "año incompleto",
                                True,
                            ),
                            (
                                "La proporción de 2026 no es válida porque se calcula con un total de chequeos más pequeño",  # noqa: E501
                                False,
                            ),
                            ("Los gráficos A y B se contradicen, así que alguno de los dos está mal calculado", False),
                            ("Los años 2020 a 2022 deberían quitarse porque en ellos no hay ningún caso de IA", False),
                        ],
                    ),
                ],
                30,
                "El conteo (A) engaña por el año incompleto; la proporción (B) muestra la tendencia real. C y D "
                "dicen qué tipo de engaño es: contenido fabricado (casi siempre Falso) y cada vez más en video.",
            ),
        ],
        glosario=[
            {
                "termino": "Año incompleto",
                "definicion": f"2026 llega hasta el {FIN_CC:%d-%m}: su conteo no se compara con años completos.",
            },
            {
                "termino": "Proyección",
                "definicion": "Estimar el total de un periodo suponiendo que el ritmo "
                "observado se mantiene. Es una suposición, no un dato.",
            },
        ],
        dossier={
            "titulo": "Expediente de evidencia · Caso 3",
            "graficos": [
                grafico(
                    "columnas",
                    "Chequeos cuyo título menciona IA",
                    etq,
                    [("Chequeos con IA", ia_anio.tolist())],
                    subtitulo="* 2026: datos hasta septiembre",
                    fuente=FUENTE_CC,
                    destacar=[len(anios) - 1],
                    letra="A",
                ),
                grafico(
                    "lineas",
                    "% de los chequeos del año que mencionan IA",
                    etq,
                    [("% con IA", ia_pct.round(1).tolist())],
                    unidad="%",
                    decimales=1,
                    y_min=0,
                    fuente=FUENTE_CC,
                    letra="B",
                ),
                grafico(
                    "barras_h",
                    "% calificado «Falso»",
                    ["Títulos que mencionan IA", "Resto de chequeos"],
                    [("% Falso", [round(falso_ia, 1), round(falso_no, 1)])],
                    unidad="%",
                    decimales=1,
                    x_max=100,
                    fuente=FUENTE_CC,
                    letra="C",
                ),
                grafico(
                    "lineas",
                    "% de títulos que mencionan video o foto",
                    etq,
                    [("Video", video_pct.round(1).tolist()), ("Foto o imagen", foto_pct.round(1).tolist())],
                    unidad="%",
                    decimales=1,
                    y_min=0,
                    fuente=FUENTE_CC,
                    letra="D",
                ),
            ],
        },
    )


# =========================================================================== CASO 4 · correlación y promedio ponderado
def caso_exposicion():
    d = dep_h.copy()
    r = d["pct_usan_todos_los_dias"].corr(d["horas_dia_promedio"])
    etiquetar = {"San Andrés", "Bogotá D.C.", "Huila", "Vaupés", "Chocó", "Magdalena"}
    puntos = [
        {
            "x": round(float(f["pct_usan_todos_los_dias"]), 1),
            "y": round(float(f["horas_dia_promedio"]), 2),
            "etiqueta": nombre,
            "mostrar": nombre in etiquetar,
        }
        for nombre, f in d.iterrows()
    ]
    acts = [
        "Redes sociales",
        "Videollamada o mensajería",
        "Correo electrónico",
        "Periódicos, revistas o libros digitales",
        "Buscar información de salud",
    ]
    u_urb, u_rur = act_urb["usuarios_internet"] / 1e6, act_rur["usuarios_internet"] / 1e6
    share_urb = u_urb / (u_urb + u_rur) * 100
    exigir(abs(r) < 0.3, "correlación débil")
    exigir(abs(act_urb["Redes sociales"] - act_rur["Redes sociales"]) < 3, "redes casi iguales")
    exigir(act_urb["Correo electrónico"] - act_rur["Correo electrónico"] > 15, "correo mucho menor rural")
    exigir(share_urb > 75, "la mayoría de usuarios es urbana")
    exigir(
        act_urb["Periódicos, revistas o libros digitales"] > 2 * act_rur["Periódicos, revistas o libros digitales"],
        "periódicos digitales mucho menos en lo rural",
    )
    vaupes = d.loc["Vaupés"]
    return caso(
        "c4",
        4,
        "¿Quién está más expuesto?",
        "correlación y promedio ponderado",
        "Encargo: una fundación quiere lanzar una campaña contra la desinformación y te pregunta a quién dirigirla. "
        "Con la encuesta del DANE comparas departamentos y zonas urbanas y rurales. Pregunta clave: ¿qué se puede "
        "afirmar con datos de USO de internet, y qué no?",
        [
            q_evaluar(
                "c4_evaluar",
                [
                    (
                        "En los departamentos donde más usuarios se conectan a diario, la gente pasa claramente más horas "  # noqa: E501
                        "conectada",
                        "C",
                        f"A: la correlación es muy débil (r = {num(r, 2)}); Vaupés tiene el uso diario más "
                        f"bajo ({num(vaupes['pct_usan_todos_los_dias'])} %) y aun así "
                        f"{num(vaupes['horas_dia_promedio'], 2)} h.",
                    ),
                    (
                        "En la zona rural, las redes sociales son una puerta de entrada casi tan usada como en la ciudad",  # noqa: E501
                        "R",
                        f"B: {num(act_rur['Redes sociales'])} % rural vs. {num(act_urb['Redes sociales'])} % urbano.",
                    ),
                    (
                        "En la zona rural se usan mucho menos otras fuentes digitales, como periódicos o correo",
                        "R",
                        f"B: periódicos digitales {num(act_rur['Periódicos, revistas o libros digitales'])} % vs. "
                        f"{num(act_urb['Periódicos, revistas o libros digitales'])} %.",
                    ),
                    (
                        "El promedio nacional de horas queda más cerca del urbano porque la mayoría de los usuarios vive en "  # noqa: E501
                        "cabeceras",
                        "R",
                        f"C: {num(share_urb, 0)} % de los usuarios es urbano; D: el nacional "
                        f"({num(nac_h['horas_dia_promedio'], 2)} h) está cerca del urbano.",
                    ),
                    (
                        "La población rural cree más fácilmente en noticias falsas",
                        "N",
                        "el DANE mide uso de internet, no creencias ni exposición a desinformación.",
                    ),
                    (
                        "Los usuarios rurales pasan menos horas en redes sociales que los urbanos",
                        "N",
                        "D mide horas de INTERNET en general; nadie midió horas en redes sociales.",
                    ),
                ],
                36,
            ),
            q_opcion(
                "c4_ponderado",
                f"Imagina que mañana se conecta un millón de usuarios rurales nuevos que usan internet "
                f"{num(rur_h['horas_dia_promedio'], 2)} horas al día, y nadie más cambia sus hábitos. ¿Qué pasa con "
                f"el promedio nacional de horas?",
                [
                    ("Baja un poco, aunque ninguna persona haya cambiado sus hábitos", True),
                    ("Sube, porque al haber más usuarios conectados aumenta el uso de internet del país", False),
                    ("No cambia, porque el promedio de cada grupo (urbano y rural) sigue siendo el mismo", False),
                    (
                        f"Baja hasta {num(rur_h['horas_dia_promedio'], 2)} horas, porque el grupo nuevo arrastra a "
                        f"todo el país a su promedio",
                        False,
                    ),
                ],
                18,
                "El promedio nacional es un promedio ponderado: si crece el grupo que usa menos horas, el "
                "total baja aunque nadie cambie. Es el mismo efecto de composición del Caso 2.",
            ),
            q_construir(
                "c4_conclusion",
                [
                    (
                        "Conclusión principal",
                        [
                            (
                                "Las redes llegan casi por igual al campo y a la ciudad, pero en el campo se usan mucho menos otras "  # noqa: E501
                                "fuentes digitales para contrastar información",
                                True,
                            ),
                            (
                                "La población rural está más desinformada porque usa menos horas de internet que la urbana",  # noqa: E501
                                False,
                            ),
                            (
                                "Donde la gente se conecta a diario pasa más horas en internet, y por eso está más expuesta",  # noqa: E501
                                False,
                            ),
                            (
                                "En la ciudad se usan menos las redes sociales, porque allí hay más alternativas digitales",  # noqa: E501
                                False,
                            ),
                        ],
                    ),
                    (
                        "Evidencia que la sostiene",
                        [
                            (
                                "B: redes con porcentajes casi iguales; periódicos digitales y correo mucho más bajos en lo rural",  # noqa: E501
                                True,
                            ),
                            ("A: la nube de puntos sube con claridad: más uso diario, más horas al día", False),
                            (
                                "C y D: hay casi tantos usuarios rurales como urbanos y usan internet las mismas horas",
                                False,
                            ),
                            ("D: el promedio nacional queda justo a mitad de camino entre lo urbano y lo rural", False),
                        ],
                    ),
                    (
                        "Limitación que hay que declarar",
                        [
                            (
                                "La encuesta mide si se hace cada actividad y cuántas horas de internet, no cuánta desinformación "  # noqa: E501
                                "ve o cree cada persona",
                                True,
                            ),
                            ("La zona rural tiene tan pocos usuarios que no se puede comparar con la urbana", False),
                            (
                                "Los departamentos con pocos habitantes deberían borrarse del gráfico A para no confundir",  # noqa: E501
                                False,
                            ),
                            ("Como es una encuesta y no un censo, sus cifras no permiten concluir nada", False),
                        ],
                    ),
                ],
                36,
                "B permite hablar de canales de información (las redes llegan a todos; las alternativas para "
                "contrastar, no). Para hablar de vulnerabilidad haría falta medir creencias o exposición, que esta "
                "encuesta no mide.",
            ),
        ],
        glosario=[
            {
                "termino": "Correlación",
                "definicion": "Qué tanto dos variables se mueven juntas (de −1 a 1). Cerca "
                "de 0 = casi ninguna relación. Correlación no es causa.",
            },
            {
                "termino": "Promedio ponderado",
                "definicion": "Un promedio nacional mezcla grupos según su tamaño: el grupo más grande pesa más.",
            },
        ],
        dossier={
            "titulo": "Expediente de evidencia · Caso 4",
            "graficos": [
                dispersion(
                    "Departamentos: uso diario vs. horas al día",
                    puntos,
                    "% de usuarios que se conecta a diario",
                    "Horas al día usando internet",
                    unidad_x="%",
                    unidad_y=" h",
                    subtitulo=f"Cada punto es un departamento · correlación r = {num(r, 2)}",
                    fuente=FUENTE_DANE,
                    letra="A",
                ),
                grafico(
                    "columnas",
                    "Qué hacen en internet: ciudad vs. campo (% de usuarios)",
                    ["Redes sociales", "Mensajería", "Correo", "Periódicos digitales", "Info de salud"],
                    [("Cabecera (urbano)", [act_urb[a] for a in acts]), ("Rural", [act_rur[a] for a in acts])],
                    unidad="%",
                    decimales=1,
                    fuente=FUENTE_DANE,
                    letra="B",
                ),
                grafico(
                    "columnas",
                    "Usuarios de internet (millones)",
                    ["Cabecera (urbano)", "Rural"],
                    [("Millones de usuarios", [round(u_urb, 2), round(u_rur, 2)])],
                    decimales=2,
                    fuente=FUENTE_DANE,
                    letra="C",
                ),
                grafico(
                    "columnas",
                    "Horas al día usando internet",
                    ["Cabecera (urbano)", "Rural", "Total nacional"],
                    [
                        (
                            "Horas",
                            [urb_h["horas_dia_promedio"], rur_h["horas_dia_promedio"], nac_h["horas_dia_promedio"]],
                        )
                    ],
                    unidad=" h",
                    decimales=2,
                    fuente=FUENTE_DANE,
                    destacar=[2],
                    letra="D",
                ),
            ],
        },
    )


# =========================================================================== CASO 5 · probabilidad condicional
def caso_condicional():
    ia, f = CC["ia"], CC["falso"]
    a, b = int((ia & f).sum()), int((ia & ~f).sum())
    c, d = int((~ia & f).sum()), int((~ia & ~f).sum())
    p_f_ia, p_ia_f, p_f_no = a / (a + b) * 100, a / (a + c) * 100, c / (c + d) * 100
    f25 = CC["anio"] == 2025
    ia_en_f25 = (ia & f & f25).sum() / (f & f25).sum() * 100
    exigir(p_f_ia > 95 and p_ia_f < 10, "P(F|IA) alta y P(IA|F) baja")
    exigir(ia_en_f25 < 30, "en 2025 la IA no es la mayoría de los Falsos")
    req = {"requiere": "c5_hipotesis"}
    return caso(
        "c5",
        5,
        "¿Falso porque es IA, o IA porque es falso?",
        "probabilidad condicional",
        "Encargo: un influencer publicó: «El 98 % de lo que tiene que ver con IA es falso. O sea: casi toda la "
        "desinformación es inteligencia artificial». Suena convincente… pero mezcla dos preguntas distintas. Antes "
        "de ver la tabla, haz tu apuesta.",
        [
            {
                "id": "c5_hipotesis",
                "tipo": "estimar",
                "puntos": 0,
                "min": 0,
                "max": 100,
                "paso": 1,
                "unidad": "%",
                "enunciado": "Tu apuesta, antes de ver los datos (sin puntos): de cada 100 chequeos calificados «Falso», "  # noqa: E501
                "¿cuántos crees que tratan de inteligencia artificial?",
                "explicacion": f"Era tu apuesta. El dato real: {num(p_ia_f)} de cada 100.",
            },
            {
                "id": "c5_f_dado_ia",
                "tipo": "numero",
                "puntos": 20,
                "tolerancia": 0.2,
                "unidad": "%",
                **req,
                "enunciado": "Con la tabla A: si escoges AL AZAR un chequeo cuyo título menciona IA, ¿cuál es la "
                "probabilidad (en %) de que esté calificado «Falso»? (Un decimal.)",
                "respuesta": round(p_f_ia, 2),
                "explicacion": f"Se mira solo la fila «Menciona IA»: {a} ÷ {a + b} = {num(p_f_ia)} %. Es P(Falso | IA).",  # noqa: E501
            },
            {
                "id": "c5_ia_dado_f",
                "tipo": "numero",
                "puntos": 20,
                "tolerancia": 0.2,
                "unidad": "%",
                **req,
                "enunciado": "Ahora al revés: si escoges AL AZAR un chequeo calificado «Falso», ¿cuál es la probabilidad "  # noqa: E501
                "(en %) de que su título mencione IA? (Un decimal.)",
                "respuesta": round(p_ia_f, 2),
                "explicacion": f"Se mira solo la columna «Falso»: {a} ÷ {a + c} = {num(p_ia_f)} %. Es P(IA | Falso): "
                f"muy distinta de la anterior, porque los chequeos de IA son pocos frente al total.",
            },
            q_opcion(
                "c5_falacia",
                "¿Cuál es el error del influencer?",
                [
                    (
                        f"Confunde dos probabilidades: que lo de IA sea casi siempre falso ({num(p_f_ia, 0)} %) no "
                        f"significa que lo falso sea casi siempre IA ({num(p_ia_f)} %)",
                        True,
                    ),
                    (
                        "Ninguno: si el 98 % de lo de IA es falso, entonces casi todo lo falso tiene que ser de IA",
                        False,
                    ),
                    ("Su único error es redondear 98,4 % a 98 %", False),
                    ("El error es usar porcentajes: con conteos la conclusión sí sería correcta", False),
                ],
                20,
                "Es la «falacia de la probabilidad inversa»: P(A | B) no es igual a P(B | A). Pasa en medicina, "
                "en juicios y en redes sociales. La clave es preguntar siempre: ¿de qué total estoy hablando?",
                **req,
            ),
            q_evaluar(
                "c5_evaluar",
                [
                    ("Si escoges al azar un chequeo de IA, es casi seguro que sea «Falso»", "R", f"A: {a} de {a + b}."),
                    (
                        "Si escoges al azar un chequeo «Falso», lo más probable es que sea de IA",
                        "C",
                        f"A: solo {a} de {a + c} ({num(p_ia_f)} %).",
                    ),
                    (
                        "Entre los chequeos que NO mencionan IA, unos 3 de cada 4 son «Falso»",
                        "R",
                        f"A: {c} de {c + d} ({num(p_f_no)} %).",
                    ),
                    (
                        "En 2025, la mayoría de los chequeos «Falso» mencionaba IA",
                        "C",
                        f"B: en 2025 fue el {num(ia_en_f25)} %.",
                    ),
                    (
                        "Usar IA hace que un contenido sea falso",
                        "N",
                        "es una afirmación de CAUSA; además, lo que se verifica de IA suele ser contenido fabricado. La "  # noqa: E501
                        "tabla solo muestra cómo se reparten los casos.",
                    ),
                ],
                35,
                **req,
            ),
        ],
        glosario=[
            {
                "termino": "P(A | B)",
                "definicion": "«Probabilidad de A sabiendo que pasó B»: se calcula SOLO dentro del grupo B.",
            },
            {
                "termino": "Tabla de doble entrada",
                "definicion": "Filas y columnas cruzan dos variables. Para "
                "P(Falso | IA) mira la fila de IA; para "
                "P(IA | Falso), la columna de Falso.",
            },
        ],
        dossier={
            "titulo": "Expediente de evidencia · Caso 5",
            "revelar_tras": "c5_hipotesis",
            "graficos": [
                tabla(
                    "Chequeos según su título y su calificación (2020–2026)",
                    ["", "Falso", "Otra calificación", "Total"],
                    [
                        ["Menciona IA", num(a, 0), num(b, 0), num(a + b, 0)],
                        ["No menciona IA", num(c, 0), num(d, 0), num(c + d, 0)],
                        ["Total", num(a + c, 0), num(b + d, 0), num(N_CC, 0)],
                    ],
                    subtitulo="Tabla de doble entrada · cada chequeo cae en una sola casilla",
                    fuente=FUENTE_CC,
                    letra="A",
                ),
                grafico(
                    "columnas",
                    "Chequeos «Falso» por año: ¿cuántos mencionan IA?",
                    list(range(2020, 2027)),
                    [
                        ("Mencionan IA", [int((ia & f & (CC["anio"] == y)).sum()) for y in range(2020, 2027)]),
                        ("No mencionan IA", [int((~ia & f & (CC["anio"] == y)).sum()) for y in range(2020, 2027)]),
                    ],
                    subtitulo="2026: datos hasta septiembre",
                    fuente=FUENTE_CC,
                    letra="B",
                ),
            ],
        },
    )


# =========================================================================== CASO 6 · encuestas e incertidumbre
def caso_encuestas():
    d = dep_h.copy()
    elegidos = [
        "San Andrés",
        "Atlántico",
        "Magdalena",
        "Bogotá D.C.",
        "Guainía",
        "Antioquia",
        "Vaupés",
        "Caldas",
        "La Guajira",
        "Valle del Cauca",
        "Cauca",
        "Huila",
    ]
    sub = d.loc[elegidos].sort_values("horas_dia_promedio", ascending=False)

    def comparar(x, y):
        lo1, hi1 = (
            d.loc[x, "horas_dia_promedio"] - d.loc[x, "horas_dia_ic"],
            d.loc[x, "horas_dia_promedio"] + d.loc[x, "horas_dia_ic"],
        )
        lo2, hi2 = (
            d.loc[y, "horas_dia_promedio"] - d.loc[y, "horas_dia_ic"],
            d.loc[y, "horas_dia_promedio"] + d.loc[y, "horas_dia_ic"],
        )
        return "P" if lo1 > hi2 else "S" if lo2 > hi1 else "N"

    pares = [
        ("Bogotá D.C.", "Antioquia"),
        ("Caldas", "La Guajira"),
        ("Valle del Cauca", "Bogotá D.C."),
        ("Huila", "Cauca"),
        ("San Andrés", "Atlántico"),
        ("Vaupés", "Antioquia"),
    ]
    claves = {f"{x} vs. {y}": comparar(x, y) for x, y in pares}
    exigir(set(claves.values()) == {"P", "S", "N"}, "hay pares de los tres tipos")
    exigir(d.loc["Vaupés", "horas_dia_ic"] > d.loc["Bogotá D.C.", "horas_dia_ic"], "Vaupés más impreciso")
    deps = ["Bogotá D.C.", "Antioquia", "Atlántico", "Meta", "Chocó"]
    diarios = {x: d.loc[x, "usan_todos_los_dias"] / 1e6 for x in deps}
    orden_ok = sorted(deps, key=lambda x: -diarios[x])
    veces = diarios["Bogotá D.C."] / diarios["Meta"]
    exigir(
        abs(d.loc["Meta", "pct_usan_todos_los_dias"] - d.loc["Bogotá D.C.", "pct_usan_todos_los_dias"]) < 3,
        "Meta y Bogotá con % parecido",
    )
    nombres = {"P": "el primero", "S": "el segundo", "N": "no se puede asegurar"}
    items = [{"id": f"par{i + 1}", "texto": k} for i, k in enumerate(claves)]
    return caso(
        "c6",
        6,
        "El ranking que no era",
        "encuestas y margen de error",
        "Encargo: un periódico quiere publicar el ranking «los departamentos más pegados a internet». Pero las horas "
        "vienen de una ENCUESTA: el DANE preguntó a una muestra de hogares, y cada cifra tiene un margen de error. "
        "Tu trabajo: decir qué partes del ranking son seguras y cuáles no, y no confundir porcentajes con cantidades.",
        [
            {
                "id": "c6_pares",
                "tipo": "clasificar",
                "estilo": "expediente",
                "puntos": 30,
                "enunciado": "Usa el Gráfico A (cada barra horizontal es el intervalo de confianza del 95 %). En cada "
                "pareja, ¿en cuál de los dos departamentos se usa internet más horas al día? Si los intervalos se "
                "cruzan, no se puede asegurar.",
                "categorias": [
                    {"id": "P", "texto": "En el primero se usa más"},
                    {"id": "S", "texto": "En el segundo se usa más"},
                    {"id": "N", "texto": "No se puede asegurar (los intervalos se cruzan)"},
                ],
                "items": items,
                "respuesta": {it["id"]: claves[it["texto"]] for it in items},
                "explicacion": " ".join(f"{k}: {nombres[v]}." for k, v in claves.items())
                + " Que un número sea mayor que otro no basta: si sus márgenes de error se cruzan, la "
                "diferencia puede ser puro azar de la muestra.",
            },
            q_opcion(
                "c6_ancho",
                f"Los intervalos de Vaupés (± {num(d.loc['Vaupés', 'horas_dia_ic'], 2)} h) y de Guainía "
                f"(± {num(d.loc['Guainía', 'horas_dia_ic'], 2)} h) son más anchos que el de Bogotá "
                f"(± {num(d.loc['Bogotá D.C.', 'horas_dia_ic'], 2)} h). ¿Por qué?",
                [
                    (
                        "Porque allí la estimación es menos precisa: se encuesta a menos hogares y las respuestas varían "  # noqa: E501
                        "más, así que hay más incertidumbre",
                        True,
                    ),
                    ("Porque en Vaupés y Guainía la gente usa internet más horas que en Bogotá", False),
                    ("Porque el DANE se equivocó al hacer la encuesta en esos departamentos", False),
                    ("Porque son departamentos más grandes en territorio, y eso agranda el intervalo", False),
                ],
                15,
                "El ancho del intervalo depende sobre todo del tamaño de la muestra y de cuánto varían las "
                "respuestas. Con pocos datos, más incertidumbre: por eso los rankings con encuestas deben "
                "mostrar el margen de error.",
            ),
            {
                "id": "c6_ordenar",
                "tipo": "ordenar",
                "puntos": 25,
                "enunciado": "Ordena de MÁS a MENOS según el NÚMERO de personas que usan internet todos los días. "
                "Necesitas combinar los Gráficos B y C (cantidad = % × usuarios).",
                "items": [{"id": f"d{i}", "texto": x} for i, x in enumerate(deps)],
                "respuesta": [f"d{deps.index(x)}" for x in orden_ok],
                "explicacion": "Personas conectadas a diario (millones): "
                + "; ".join(f"{x} ≈ {num(diarios[x], 2)}" for x in orden_ok)
                + ". El orden por porcentaje (B) es otro: un % alto en una población pequeña da pocas "
                "personas.",
            },
            q_opcion(
                "c6_cantidad",
                f"Meta y Bogotá tienen porcentajes de uso diario parecidos (Gráfico B). ¿Por qué entonces Bogotá "
                f"tiene unas {num(veces, 0)} veces más personas conectadas a diario?",
                [
                    (
                        "Porque el porcentaje se calcula sobre poblaciones de tamaño muy distinto: el mismo % de una base "  # noqa: E501
                        "más grande da muchas más personas",
                        True,
                    ),
                    ("Porque en Bogotá cada persona se conecta más veces al día", False),
                    ("Porque los porcentajes de Meta están mal calculados", False),
                    ("Porque Bogotá tiene un porcentaje mucho más alto que Meta", False),
                ],
                20,
                "Un porcentaje responde «qué parte»; una cantidad responde «cuántos». Para una campaña que "
                "quiere llegar a más personas importa la cantidad; para comparar hábitos, el porcentaje.",
            ),
        ],
        glosario=[
            {
                "termino": "Intervalo de confianza 95 %",
                "definicion": "Rango donde muy probablemente está el valor real de toda la población.",
            },
            {
                "termino": "Muestra",
                "definicion": "Las personas que sí respondieron la encuesta; con ellas se estima para todos.",
            },
            {
                "termino": "Porcentaje vs. cantidad",
                "definicion": "«Qué parte» vs. «cuántos». Cantidad = porcentaje × total.",
            },
        ],
        dossier={
            "titulo": "Expediente de evidencia · Caso 6",
            "graficos": [
                grafico(
                    "intervalos",
                    "Horas al día usando internet, con margen de error (IC 95 %)",
                    list(sub.index),
                    [("Horas al día", sub["horas_dia_promedio"].tolist())],
                    unidad=" h",
                    decimales=2,
                    margenes=sub["horas_dia_ic"].round(2).tolist(),
                    fuente=FUENTE_DANE,
                    subtitulo="Punto = estimación · barra = intervalo de confianza",
                    letra="A",
                )
                | {"ancho_completo": True},
                grafico(
                    "barras_h",
                    "% de usuarios que usa internet todos los días",
                    deps,
                    [("% diario", [d.loc[x, "pct_usan_todos_los_dias"] for x in deps])],
                    unidad="%",
                    decimales=1,
                    x_max=100,
                    fuente=FUENTE_DANE,
                    letra="B",
                ),
                grafico(
                    "barras_h",
                    "Usuarios de internet (millones de personas)",
                    deps,
                    [("Millones", [round(d.loc[x, "usuarios_internet"] / 1e6, 2) for x in deps])],
                    decimales=2,
                    fuente=FUENTE_DANE,
                    letra="C",
                ),
            ],
        },
    )


# =========================================================================== CASO 7 · taller del gráfico
def caso_taller():
    anios = list(range(2020, 2026))
    pf = xa.loc[anios, "pct_falso"]
    subida_real = pf[2025] - pf[2020]
    subida_trino = pf[2025] - pf[2022]
    exigir(pf.idxmin() == 2022, "2022 es el año más bajo")
    aut = CC["autor_chequeo"].value_counts()
    media, mediana = len(CC) / len(aut), float(aut.median())
    tramos = pd.cut(aut, [0, 1, 5, 20, 100, 10_000], labels=["1", "2 a 5", "6 a 20", "21 a 100", "más de 100"])
    hist = tramos.value_counts().sort_index()
    exigir(mediana == 1 and media > 10, "media alta y mediana 1")
    dif_min = (hom_h["horas_dia_promedio"] - muj_h["horas_dia_promedio"]) * 60
    tipos_g = [
        {"id": "LIN", "texto": "Líneas: cambio a lo largo del tiempo"},
        {"id": "BAR", "texto": "Barras: comparar cantidades entre categorías"},
        {"id": "DIS", "texto": "Dispersión: ver si dos variables se relacionan"},
        {"id": "PAR", "texto": "Barras al 100 %: qué parte de un total es cada grupo"},
    ]
    preguntas_g = [
        ("¿Cómo cambió entre 2020 y 2026 el porcentaje de chequeos sobre inteligencia artificial?", "LIN"),
        ("¿Qué día de la semana publica Colombiacheck más chequeos?", "BAR"),
        ("¿Los departamentos donde más gente se conecta a diario son los que más horas pasan conectados?", "DIS"),
        ("En 2022, ¿qué PARTE de los chequeos fue de redes y qué parte de discurso público?", "PAR"),
        ("¿Qué departamento tiene más usuarios de internet?", "BAR"),
    ]
    items = [{"id": f"g{i + 1}", "texto": t} for i, (t, _) in enumerate(preguntas_g)]
    return caso(
        "c7",
        7,
        "El taller del gráfico",
        "elegir, leer y desarmar gráficos",
        "Encargo: te nombran editor de datos del periódico escolar. Tu trabajo tiene tres partes: escoger el gráfico "
        "correcto para cada pregunta, descubrir los trucos con que otros presentan los datos, y elegir el número "
        "que mejor resume un grupo. Cada pregunta trae su propio gráfico.",
        [
            {
                "id": "c7_elegir",
                "tipo": "clasificar",
                "estilo": "expediente",
                "puntos": 25,
                "categorias": tipos_g,
                "enunciado": "Para cada pregunta de investigación, ¿qué tipo de gráfico la responde mejor?",
                "items": items,
                "respuesta": {it["id"]: k for it, (_, k) in zip(items, preguntas_g)},  # noqa: B905
                "explicacion": "Tiempo → líneas; comparar categorías → barras; relación entre dos variables → "
                "dispersión; partes de un total → barras al 100 %. Elegir mal el gráfico puede esconder "
                "o inventar un patrón.",
            },
            q_opcion(
                "c7_eje",
                "Un perfil publicó este gráfico con el mensaje: «¡Los hombres usan internet MUCHÍSIMO más que "
                "las mujeres!». ¿Qué tiene de tramposo?",
                [
                    (
                        f"El eje vertical empieza en 4,80 y no en cero: una diferencia de unos {num(dif_min, 0)} "
                        f"minutos parece enorme",
                        True,
                    ),
                    ("Nada: la diferencia de verdad es enorme", False),
                    ("Los colores de las barras están invertidos", False),
                    ("Debería ser un gráfico de líneas porque son dos grupos", False),
                ],
                15,
                f"Hombres {num(hom_h['horas_dia_promedio'], 2)} h y mujeres "
                f"{num(muj_h['horas_dia_promedio'], 2)} h: unos {num(dif_min, 0)} minutos de diferencia. "
                f"Cortar el eje en barras exagera las diferencias.",
                grafico=grafico(
                    "columnas",
                    "Horas al día usando internet",
                    ["Hombres", "Mujeres"],
                    [("Horas", [hom_h["horas_dia_promedio"], muj_h["horas_dia_promedio"]])],
                    unidad=" h",
                    decimales=2,
                    y_min=4.80,
                    y_max=5.0,
                    subtitulo="Publicación viral",
                    fuente=FUENTE_DANE,
                ),
            ),
            {
                "id": "c7_subida",
                "tipo": "numero",
                "puntos": 15,
                "tolerancia": 0.1,
                "unidad": "puntos porcentuales",
                "grafico": grafico(
                    "lineas",
                    "% de chequeos «Falso» por año",
                    anios,
                    [("% Falso", pf.round(1).tolist())],
                    unidad="%",
                    decimales=1,
                    y_min=0,
                    y_max=100,
                    fuente=FUENTE_CC,
                ),
                "enunciado": f"Un trino dice: «¡Desde 2022 lo falso se disparó: subió {num(subida_trino, 0)} puntos!». "
                f"Con el gráfico (pasa el cursor por los puntos), ¿cuántos puntos porcentuales subió el % "
                f"Falso entre 2020, el primer año de la serie, y 2025? (Un decimal.)",
                "respuesta": round(float(subida_real), 2),
                "explicacion": f"{num(pf[2025])} − {num(pf[2020])} = {num(subida_real)} puntos, no {num(subida_trino)}.",  # noqa: E501
            },
            q_opcion(
                "c7_truco",
                "¿Qué truco usó el trino?",
                [
                    (
                        f"Escogió como punto de partida 2022, el año más bajo de la serie, para que la subida pareciera "  # noqa: E501, F541
                        f"mucho mayor",  # noqa: F541
                        True,
                    ),
                    ("Usó porcentajes en vez de conteos, y los porcentajes siempre exageran los cambios", False),
                    ("Comparó un año incompleto con uno completo", False),
                    ("No hay truco: desde 2022 hasta 2025 la subida es la misma que en toda la serie", False),
                ],
                15,
                "Elegir a conveniencia el inicio o el final de una serie («cherry picking») es uno de los trucos "
                "más usados. Antes de creer una subida, mira la serie completa (y recuerda el Caso 2: parte "
                "de ese cambio es de mezcla).",
            ),
            {
                "id": "c7_mediana",
                "tipo": "numero",
                "puntos": 10,
                "tolerancia": 0,
                "unidad": "chequeo(s)",
                "entero": True,
                "grafico": grafico(
                    "columnas",
                    "Periodistas según cuántos chequeos firmaron",
                    list(hist.index),
                    [("Periodistas", hist.tolist())],
                    fuente=FUENTE_CC,
                    subtitulo=f"{len(aut)} periodistas firmaron {num(len(CC), 0)} chequeos",
                ),
                "enunciado": f"{len(aut)} periodistas firmaron {num(len(CC), 0)} chequeos. Con el gráfico, ¿cuál es la "
                f"MEDIANA de chequeos por periodista? (Pista: busca al periodista que queda en la mitad de "
                f"la fila si los ordenas de menos a más.)",
                "respuesta": mediana,
                "explicacion": f"Con {len(aut)} periodistas, la mediana es el número {(len(aut) + 1) // 2}. Como "
                f"{hist.iloc[0]} periodistas firmaron 1 solo chequeo (más de la mitad), la mediana es "
                f"{num(mediana, 0)}.",
            },
            q_opcion(
                "c7_tipico",
                f"El PROMEDIO es {num(media)} chequeos por periodista, pero la mediana es {num(mediana, 0)}. ¿Qué "
                f"número describe mejor al periodista típico, y por qué?",
                [
                    (
                        f"La mediana: unos pocos periodistas con más de 100 chequeos ({hist.iloc[-1]} personas) inflan el "  # noqa: E501
                        f"promedio, mientras la mayoría firmó muy pocos",
                        True,
                    ),
                    ("El promedio, porque usa todos los datos y por eso siempre es el mejor resumen", False),
                    ("Los dos por igual, porque siempre dan casi el mismo resultado", False),
                    ("Ninguno: con tantos periodistas no se puede resumir", False),
                ],
                10,
                "Cuando unos pocos valores son muy grandes (distribución sesgada), el promedio se va hacia ellos "
                "y la mediana describe mejor a la mayoría. Pasa con salarios, likes o seguidores.",
            ),
            {
                "id": "c7_informe",
                "tipo": "texto",
                "puntos": 0,
                "max": 700,
                "enunciado": "Informe final del analista (sin puntos, lo lee tu docente): elige UNO de los siete casos y "  # noqa: E501
                "escribe en 3 a 5 frases su conclusión más importante, con qué gráficos la sostienes y qué "
                "limitación tiene.",
                "explicacion": "Pregunta abierta: no tiene una única respuesta correcta.",
            },
        ],
        glosario=[
            {
                "termino": "Mediana",
                "definicion": "El valor del medio cuando ordenas los datos. No la mueven los valores extremos.",
            },
            {
                "termino": "Cherry picking",
                "definicion": "Escoger solo la parte de los datos que conviene a tu mensaje.",
            },
        ],
    )


# =========================================================================== 10 · Lo que dice la ciencia
LECTURA_NATURE = (
    "Arechar y colaboradores (2023) hicieron un experimento en 16 países de 6 continentes con 34.286 usuarios de "
    "redes sociales. Cada persona vio 20 titulares sobre COVID-19 (10 verdaderos y 10 falsos). A unos se les "
    "preguntó si cada titular era exacto; a otros, si lo compartirían. Algunos recibieron antes un «recordatorio "
    "de exactitud» (calificar si UN titular cualquiera era exacto) y otros leyeron cuatro consejos breves de "
    "alfabetización digital.\n\n"
    "Resultados: (1) En todos los países, quienes tenían un estilo de pensamiento más analítico y valoraban más "
    "la exactitud distinguían mejor lo verdadero de lo falso; confiar en general en la gente no hacía diferencia. "
    "(2) Lo que la gente compartiría distinguía mucho menos entre verdadero y falso que lo que creía: muchas "
    "personas compartirían titulares falsos que reconocerían como falsos si se les preguntara. (3) El "
    "recordatorio de exactitud mejoró la calidad de lo que compartían; los consejos también, con un efecto menor. "
    "Curiosamente, la gente dijo que los consejos le parecían más útiles que el recordatorio. (4) Promediando "
    "las opiniones de personas no expertas («sabiduría de la multitud») se distinguían titulares verdaderos de "
    "falsos con alta precisión en todos los países.\n\n"
    "Participaron Argentina, Australia, Brasil, China, Egipto, España, Estados Unidos, Filipinas, India, Italia, "
    "México, Nigeria, Reino Unido, Rusia, Arabia Saudita y Sudáfrica. Los autores reconocen límites: el «compartir» "
    "fue hipotético (lo que dijeron que harían), solo usaron titulares de COVID-19 y las muestras no eran "
    "totalmente representativas."
)


def mision_ciencia():
    return {
        "id": "m5",
        "titulo": "Lo que dice la ciencia",
        "subtitulo": "Lectura · Nature Human Behaviour, 2023",
        "intro": "Lee el resumen del estudio (lo tienes a la vista en toda la misión) y responde.",
        "lectura": {
            "titulo": "¿Por qué creemos y compartimos desinformación? Un experimento en 16 países",
            "texto": LECTURA_NATURE,
            "cita": "Arechar, A. A. et al. (2023). Understanding and combatting misinformation across 16 "
            "countries on six continents. Nature Human Behaviour, 7, 1502–1513. "
            "doi:10.1038/s41562-023-01641-6",
        },
        "preguntas": [
            q_opcion(
                "m5_creer_compartir",
                "¿Qué encontraron al comparar lo que la gente CREE con lo que COMPARTE?",
                [
                    (
                        "Muchas personas compartirían titulares falsos que reconocerían como falsos si se les "
                        "preguntara por su exactitud",
                        True,
                    ),
                    ("La gente solo comparte lo que cree que es verdad", False),
                    ("Nadie dijo que compartiría titulares falsos", False),
                    ("Quienes más comparten son siempre quienes menos saben", False),
                ],
                20,
                "Es la «brecha entre creer y compartir». El tablero de la clase compara cuánto compartieron "
                "con cuánto creyeron.",
            ),
            q_opcion(
                "m5_intervenciones",
                "¿Qué intervención fue más efectiva y cuál le pareció más útil a la gente?",
                [
                    ("Más efectivo: el recordatorio de exactitud. Más útil según la gente: los consejos", True),
                    ("Más efectivos: los consejos. Más útil según la gente: el recordatorio", False),
                    ("Ninguna de las dos funcionó", False),
                    ("Las dos fueron igual de efectivas y les parecieron igual de útiles", False),
                ],
                20,
                "Lo que parece útil no siempre es lo que funciona; por eso se mide con experimentos.",
            ),
            q_opcion(
                "m5_azar",
                "En el estudio (y en nuestra clase) las personas se repartieron AL AZAR entre los "
                "grupos con y sin recordatorio. ¿Para qué sirve repartir al azar?",
                [
                    (
                        "Para que los grupos se parezcan en todo lo demás, y así la diferencia se pueda atribuir al "
                        "recordatorio",
                        True,
                    ),
                    ("Para que los resultados salgan más altos", False),
                    ("Para no tener que contar cuántas personas hay en cada grupo", False),
                    ("Para que cada persona pueda escoger el grupo que prefiera", False),
                ],
                15,
                "La asignación al azar es lo que permite pasar de «van juntos» (correlación) a «esto causó "
                "aquello» (efecto causal) en un experimento.",
            ),
            q_opcion(
                "m5_multitud",
                "¿Qué significa la «sabiduría de la multitud» en este estudio?",
                [
                    (
                        "Que el promedio de las opiniones de muchas personas no expertas distinguía titulares "
                        "verdaderos de falsos con alta precisión",
                        True,
                    ),
                    ("Que lo que comparte la mayoría siempre es verdad", False),
                    ("Que los expertos se equivocan más que la gente común", False),
                    ("Que hay que creer lo que tiene más «me gusta»", False),
                ],
                15,
                "No es «la mayoría tiene razón»: es promediar juicios independientes sobre la exactitud.",
            ),
            q_multiple(
                "m5_paises",
                "¿Qué países de América Latina participaron en el estudio? Marca TODOS.",
                [
                    ("Argentina", True),
                    ("Brasil", True),
                    ("México", True),
                    ("Colombia", False),
                    ("Chile", False),
                    ("Perú", False),
                ],
                15,
                "Colombia NO participó: este reto es una pequeña réplica con titulares colombianos reales.",
            ),
            q_opcion(
                "m5_limites",
                "¿Cuál es una limitación que reconocen los propios autores?",
                [
                    ("El «compartir» fue hipotético y solo usaron titulares sobre COVID-19", True),
                    ("Solo participaron 16 personas", False),
                    ("Solo se hizo en Estados Unidos", False),
                    ("No usaron titulares falsos", False),
                ],
                15,
                "Reconocer límites hace más confiable un estudio, no menos.",
            ),
        ],
    }


# =========================================================================== VALIDACIÓN Y SALIDA
def validar(banco):  # noqa: C901
    total, ids = 0, set()
    for m in banco["misiones"]:
        for q in m["preguntas"]:
            assert q["id"] not in ids, f"id repetido {q['id']}"
            ids.add(q["id"])
            total += q["puntos"]
            for v in q.get("variantes", [q]):
                cuerpo = {**q, **v}
                assert "enunciado" in cuerpo, q["id"]
                if q["puntos"] == 0:
                    continue
                assert "respuesta" in cuerpo and "explicacion" in cuerpo, q["id"]
                if q["tipo"] == "clasificar":
                    cats = {c["id"] for c in q["categorias"]}
                    items = {i["id"] for i in cuerpo["items"]}
                    assert set(cuerpo["respuesta"]) == items, q["id"]
                    assert set(cuerpo["respuesta"].values()) <= cats, q["id"]
                if q["tipo"] in ("opcion", "multiple"):
                    oids = {o["id"] for o in cuerpo["opciones"]}
                    r = cuerpo["respuesta"]
                    assert (r in oids) if isinstance(r, str) else set(r) <= oids, q["id"]
                if q["tipo"] == "ordenar":
                    assert sorted(cuerpo["respuesta"]) == sorted(i["id"] for i in cuerpo["items"]), q["id"]
                if q["tipo"] == "construir":
                    partes = {p["id"]: {o["id"] for o in p["opciones"]} for p in cuerpo["partes"]}
                    assert set(cuerpo["respuesta"]) == set(partes), q["id"]
                    assert all(cuerpo["respuesta"][k] in partes[k] for k in partes), q["id"]
        for q in m["preguntas"]:
            if "requiere" in q:
                assert q["requiere"] in ids, q["id"]
        rev = (m.get("dossier") or {}).get("revelar_tras")
        if rev:
            assert rev in ids, m["id"]
    assert total == PUNTOS_TOTALES, f"El banco suma {total} puntos, no {PUNTOS_TOTALES}"
    return total, len(ids)


def main():
    banco = {
        "titulo": "Detectives de la desinformación",
        "descripcion": "Reto de 90 minutos para estudiantes de 9.° a 11.°: 3 expedientes sobre desinformación y 7 "
        "casos estadísticos con datos reales de Colombiacheck y el DANE.",
        "duracion_min": 90,
        "bono_tiempo_max": 20,
        "puntos_totales": PUNTOS_TOTALES,
        "misiones": [
            mision_compartir(),
            mision_detectives(),
            caso_elecciones(),
            caso_composicion(),
            caso_ia(),
            caso_exposicion(),
            caso_condicional(),
            caso_encuestas(),
            caso_taller(),
            mision_ciencia(),
        ],
    }
    total, n = validar(banco)
    texto = json.dumps(banco, ensure_ascii=False, indent=1)
    banco["version"] = hashlib.sha256(texto.encode()).hexdigest()[:10]
    SALIDA.write_text(json.dumps(banco, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[ok] {n} preguntas, {total} puntos, versión {banco['version']} -> {SALIDA.name}")
    for m in banco["misiones"]:
        print(
            f"   {m['id']}  {m['titulo']:<58} {sum(q['puntos'] for q in m['preguntas']):>4} pts  "
            f"{len(m['preguntas'])} preguntas"
        )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
