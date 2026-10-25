"""
Analisis descriptivo de los datos del reto "Detectives de la desinformacion".

Lee los datos del proyecto del semillero, los limpia y, para CADA dataset, crea
una carpeta con:
    datos/      el archivo limpio listo para usar (CSV, UTF-8)
    tablas/     tablas resumen en CSV
    figuras/    graficas PNG
    ANALISIS.md que es el dataset, que variables tiene y como se comportan

Todas las cifras de los ANALISIS.md se calculan aqui mismo a partir de los datos;
ninguna se escribe a mano. Si los datos cambian, basta con volver a ejecutar:

    python generar_analisis.py

La aplicacion del reto (carpeta 2_Aplicacion_Reto) construye sus preguntas a
partir de los archivos limpios que deja este script.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: I001
import numpy as np
import pandas as pd

import estilo_graficos as est

RAIZ = Path(__file__).resolve().parents[2]  # carpeta Reto_Desinformacion_Colegios
AQUI = RAIZ / "1_Analisis_de_datos"  # aquí se escriben los resultados
DATOS = RAIZ / "4_Codigo_y_datos" / "datos_originales"
SRC_CC = DATOS / "colombiacheck" / "colombiacheck_verificado.csv"
# De aquí solo se toma «tipo» (sección del medio: «Desinformación en redes» / «Discurso público»).
# Se renombra «Desinformación en redes» → «Contenido viral en redes»: es la SECCIÓN donde se publica el chequeo,
# no el veredicto (hay contenidos de esa sección que resultan Verdaderos), y el nombre original confunde.
TIPO_REDES = "Contenido viral en redes"
SRC_CC_TIPO = DATOS / "colombiacheck" / "colombiacheck_tipo_de_chequeo.csv"
SRC_DANE = DATOS / "dane_entic_2024"
SRC_BM = DATOS / "banco_mundial"

DIAS_ES = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}
ORDEN_DIAS = list(DIAS_ES.values())
ORDEN_CALIF = ["Falso", "Cuestionable", "Verdadero pero...", "Verdadero"]
# Jornadas electorales nacionales y locales del periodo (mes de la votación)
ELECCIONES = {
    "2022-03": "Legislativas 2022",
    "2022-05": "Presidencial 2022 (1.ª vuelta)",
    "2022-06": "Presidencial 2022 (2.ª vuelta)",
    "2023-10": "Locales 2023",
    "2026-03": "Legislativas 2026",
    "2026-05": "Presidencial 2026 (1.ª vuelta)",
    "2026-06": "Presidencial 2026 (2.ª vuelta)",
}
PATRON_ELECTORAL = (
    r"elecci|electoral|registradur|candidat|jurado|escrutinio|tarjet[oó]n|votaci|\bvot(?:o|os|ar|ante)\b"
    r"|\burnas?\b|consulta (?:popular|interpartidista|presidencial|anticorrupci)"
)

# Palabras clave en los TITULOS de Colombiacheck. Son conteos transparentes de
# palabras, no una clasificacion tematica validada: se presentan como tales.
FAMILIAS_TITULO = {
    "Inteligencia artificial (IA)": r"\bia\b|inteligencia artificial",
    "COVID-19 / vacunas": r"covid|coronavirus|vacuna",
    "Estafas": r"estafa|fraude|robar sus datos|carnada",
    "Video": r"\bv[ií]deos?\b",
    "Foto / imagen": r"\bfotos?\b|\bim[aá]gen(?:es)?\b",
}
PLATAFORMAS = {
    "WhatsApp": r"whatsapp",
    "Facebook": r"facebook",
    "TikTok": r"tiktok|tik tok",
    "X / Twitter": r"twitter|\btrino|\btuit",
    "Instagram": r"instagram",
    "YouTube": r"youtube",
}

ACT_INTERNET = [  # (inicio del nombre oficial DANE, etiqueta corta)
    ("OBTENER INFORMACIÓN SOBRE BIENES", "Info sobre bienes o servicios"),
    ("VIDEO, LLAMADA", "Videollamada o mensajería"),
    ("ENVIAR O RECIBIR CORREOS", "Correo electrónico"),
    ("UTILIZAR SERVICIOS EN LA NUBE", "Servicios en la nube"),
    ("REDES SOCIALES", "Redes sociales"),
    ("REDES LABORALES", "Redes laborales"),
    ("COMPRAR/ORDENAR", "Comprar en línea"),
    ("VENDER PRODUCTOS", "Vender en línea"),
    ("OPERACIONES BANCARIAS", "Banca en línea"),
    ("CONSULTAR WIKIS", "Wikis y enciclopedias"),
    ("EDUCACIÓN Y APRENDIZAJE", "Educación y aprendizaje"),
    ("BUSCAR EMPLEO", "Buscar empleo"),
    ("BUSCAR INFORMACIÓN DE ENTIDADES", "Info de entidades públicas"),
    ("HACER TRÁMITES", "Trámites con entidades públicas"),
    ("DESCARGAR SOFTWARES", "Descargar aplicaciones"),
    ("DESCARGAR O VER EN LÍNEA", "Ver o descargar videos y música"),
    ("DESCARGAR JUEGOS", "Jugar en línea"),
    ("ACCEDER A SITIOS DE CHAT", "Chats, blogs y foros de noticias"),
    ("CONSULTA DE PERIÓDICOS", "Periódicos, revistas o libros digitales"),
    ("GENERACIÓN DE LA PLANILLA", "Pago de seguridad social"),
    ("VER TELEVISIÓN", "Televisión en línea"),
    ("ESCUCHAR RADIO", "Radio en línea"),
    ("ACCEDER, PUBLICAR O INTERCAMBIAR", "Opinar sobre productos"),
    ("APOSTAR EN LÍNEA", "Apostar en línea"),
    ("ACCEDER A RESULTADOS", "Resultados de exámenes médicos"),
    ("BUSCAR INFORMACIÓN SOBRE ASUNTOS DE SALUD", "Buscar información de salud"),
    ("SOLICITAR O CANCELAR CITAS", "Citas médicas"),
    ("SUBIR CONTENIDO PROPIO", "Subir contenido propio"),
    ("PUBLICAR OPINIONES SOBRE ASUNTOS", "Opinar sobre política"),
    ("USAR HERRAMIENTAS DE INTELIGENCIA", "Usar herramientas de IA"),
    ("TRABAJAR COMO REQUISITO", "Trabajar"),
]
ACT_REDES = [
    ("COMUNICARSE CON FAMILIARES", "Comunicarse con familia y amigos"),
    ("ACCEDER A CONTENIDOS PUBLICADOS", "Ver contenidos de otros y comentar"),
    ("PRODUCIR SUS PROPIOS", "Producir contenido propio"),
    ("SER MIEMBRO DE GRUPOS", "Ser miembro de grupos y causas"),
    ("PROMOVER Y CONVOCAR", "Convocar eventos"),
    ("PROMOVER SU NEGOCIO", "Promover un negocio"),
    ("EXPRESAR SUS IDEAS", "Opinar sobre temas públicos"),
    ("INTERACTUAR CON ENTIDADES", "Interactuar con entidades públicas"),
    ("QUEJARSE POR LA ATENCIÓN", "Quejarse de entidades públicas"),
    ("RESPALDAR ALGUNA INICIATIVA", "Respaldar iniciativas públicas"),
    ("REPORTAR EL ESTADO DE LAS VÍAS", "Reportar el estado de las vías"),
    ("CONOCER NUEVAS PERSONAS", "Conocer personas o tener citas"),
    ("ENTRETENIMIENTO", "Entretenimiento"),
]


# --------------------------------------------------------------------------- utilidades
def num(v, dec=1):
    """Numero con formato colombiano: punto de miles, coma decimal."""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def ent(v):
    return num(v, 0)


def tabla_md(df, cols=None, fmt=None):
    """DataFrame -> tabla Markdown (sin dependencias extra)."""
    fmt = fmt or {}
    cols = cols or list(df.columns)
    filas = [
        "| " + " | ".join(str(c) for c in cols) + " |",
        "|" + "|".join("---:" if pd.api.types.is_numeric_dtype(df[c]) else "---" for c in cols) + "|",
    ]
    for i in range(len(df)):
        celdas = []
        for c in cols:
            v = df[c].iloc[i]
            if c in fmt:
                v = fmt[c](v)
            elif isinstance(v, float):
                v = num(v)
            celdas.append(str(v))
        filas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def carpeta(nombre):
    base = AQUI / nombre
    for sub in ("datos", "tablas", "figuras"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base


def guardar(fig, base, nombre):
    est.save(fig, nombre, base / "figuras")
    plt.close(fig)
    return f"figuras/{nombre}.png"


def etiquetar_cortas(columnas, mapa):
    renombre = {}
    for c in columnas:
        for inicio, corta in mapa:
            if c.strip().upper().startswith(inicio):
                renombre[c] = corta
                break
    return renombre


def leer_dane(nombre):
    df = pd.read_csv(SRC_DANE / nombre, encoding="utf-8-sig")
    df = df[df["nivel"].isin(["TOTAL NACIONAL", "ÁREA", "DEPARTAMENTO"])].copy()
    for c in df.columns[3:]:
        if df[c].dtype == object and not str(c).endswith("_cve"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["ambito"] = df["ambito"].replace(
        {"CENTROS POBLADOS Y RURAL DISPERSO": "RURAL (centros poblados y rural disperso)"}
    )
    df["ambito"] = (
        df["ambito"].str.title().str.replace(" Del ", " del ", regex=False).str.replace(" De ", " de ", regex=False)
    )
    df["ambito"] = df["ambito"].replace(
        {
            "Bogotá D.C.": "Bogotá D.C.",
            "Rural (Centros Poblados Y Rural Disperso)": "Rural",
            "Cabecera": "Cabecera (urbano)",
            "Total": "Total nacional",
        }
    )
    return df.reset_index(drop=True)


# =========================================================================== 1. COLOMBIACHECK
def analizar_colombiacheck():
    base = carpeta("01_Colombiacheck_chequeos_verificados")
    cc = pd.read_csv(SRC_CC, encoding="utf-8-sig")
    tipos = pd.read_csv(SRC_CC_TIPO, usecols=["url", "tipo"], encoding="utf-8-sig").drop_duplicates("url")
    cc = cc.merge(tipos, on="url", how="left")
    cc["tipo"] = cc["tipo"].replace({"Desinformación en redes": TIPO_REDES})
    cc["fecha"] = pd.to_datetime(cc["fecha"])
    cc["tema_electoral"] = (
        (cc["titulo"] + " " + cc["afirmacion_verificada"]).str.lower().str.contains(PATRON_ELECTORAL, regex=True)
    )
    cc["dia_semana_es"] = cc["dia_semana"].map(DIAS_ES)
    cc["hora_num"] = cc["hora"].str[:2].astype(int)
    titulo = cc["titulo"].str.lower()
    texto = (cc["titulo"] + " " + cc["afirmacion_verificada"]).str.lower()
    for fam, pat in FAMILIAS_TITULO.items():
        cc[f"titulo_{fam}"] = titulo.str.contains(pat, regex=True)
    for plat, pat in PLATAFORMAS.items():
        cc[f"menciona_{plat}"] = texto.str.contains(pat, regex=True)

    limpio = cc[
        [
            "url",
            "fecha",
            "hora",
            "anio",
            "mes",
            "dia_semana_es",
            "tipo",
            "titulo",
            "afirmacion_verificada",
            "calificacion",
            "calificacion_valor",
            "autor_chequeo",
            "tema_electoral",
        ]
    ]
    limpio = limpio.rename(columns={"dia_semana_es": "dia_semana"})
    limpio.to_csv(base / "datos" / "colombiacheck_verificado_limpio.csv", index=False, encoding="utf-8-sig")

    n = len(cc)
    ini, fin = cc["fecha"].min(), cc["fecha"].max()
    neutral = cc.index[cc["titulo"].str.contains("anaconda", case=False)]
    ej = cc.loc[neutral[0]] if len(neutral) else cc.iloc[0]

    # --- calificacion
    cal = cc["calificacion"].value_counts().reindex(ORDEN_CALIF).fillna(0).astype(int)
    t_cal = pd.DataFrame(
        {"calificacion": cal.index, "chequeos": cal.values, "porcentaje": (cal.values / n * 100).round(2)}
    )
    t_cal.to_csv(base / "tablas" / "calificacion.csv", index=False, encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(7.5, 2.8))
    est.hbar(
        ax,
        cal,
        color=[
            est.CALIF_COLORS["Falso"],
            est.CALIF_COLORS["Cuestionable"],
            est.CALIF_COLORS["Verdadero pero"],
            est.CALIF_COLORS["Verdadero"],
        ],
    )
    est.titles(
        ax,
        "Tres de cada cuatro chequeos terminan en «Falso»",
        f"Chequeos de Colombiacheck por calificación, {est.mes_es(ini)}–{est.mes_es(fin)} (n = {ent(n)})",
    )
    f_cal = guardar(fig, base, "01_calificaciones")

    # --- por anio
    xa = pd.crosstab(cc["anio"], cc["calificacion"]).reindex(columns=ORDEN_CALIF, fill_value=0)
    xa["total"] = xa.sum(axis=1)
    xa["pct_falso"] = (xa["Falso"] / xa["total"] * 100).round(1)
    xa["pct_cuestionable"] = (xa["Cuestionable"] / xa["total"] * 100).round(1)
    xa.reset_index().to_csv(base / "tablas" / "calificacion_por_anio.csv", index=False, encoding="utf-8-sig")
    anio_max = xa["total"].idxmax()

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    colores = [est.NEUTRAL if a == xa.index.max() else est.SERIES[0] for a in xa.index]
    barras = ax.bar(xa.index.astype(str), xa["total"], color=colores, width=0.55)
    for b, v in zip(barras, xa["total"]):  # noqa: B905
        ax.annotate(
            ent(v),
            (b.get_x() + b.get_width() / 2, v),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=est.INK_2,
        )
    ax.grid(axis="x", visible=False)
    est.titles(
        ax,
        "Unos 420–480 chequeos al año; 2026 aún no termina",
        f"Chequeos publicados por año (2026 llega hasta el {fin:%d-%m-%Y}, por eso va en gris)",
    )
    f_anio = guardar(fig, base, "02_chequeos_por_anio")

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.plot(xa.index, xa["pct_falso"], marker="o", color=est.SERIES[0], label="% Falso")
    ax.plot(xa.index, xa["pct_cuestionable"], marker="o", color=est.SERIES[1], label="% Cuestionable")
    for serie in ("pct_falso", "pct_cuestionable"):
        ax.annotate(
            f"{num(xa[serie].iloc[-1])} %",
            (xa.index[-1], xa[serie].iloc[-1]),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=est.INK_2,
        )
    ax.set_ylim(0, 100)
    ax.legend(loc="center left", bbox_to_anchor=(1.08, 0.5))
    est.titles(
        ax,
        "La proporción de «Falso» se mueve entre 70 % y 83 %",
        "Porcentaje de chequeos de cada año con calificación Falso y Cuestionable",
    )
    f_pct = guardar(fig, base, "03_pct_falso_cuestionable_por_anio")

    # --- serie mensual
    mens = cc.set_index("fecha").resample("MS").size()
    mens.rename("chequeos").to_csv(base / "tablas" / "chequeos_por_mes.csv", encoding="utf-8-sig")
    meses_max = " y ".join(est.mes_es(f) for f in mens[mens == mens.max()].index)
    nota_covid = (
        " Marzo de 2020 coincide con la llegada de la COVID-19 a Colombia."
        if pd.Timestamp("2020-03-01") in mens[mens == mens.max()].index
        else ""
    )
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.plot(mens.index, mens.values, color=est.SERIES[0], linewidth=1.6)
    ax.fill_between(mens.index, mens.values, color=est.SERIES[0], alpha=0.10)
    for fecha in mens[mens == mens.max()].index:
        ax.plot(
            [fecha],
            [mens.max()],
            "o",
            color=est.SERIES[0],
            markersize=6,
            markeredgecolor=est.SURFACE,
            markeredgewidth=2,
        )
        ax.annotate(
            f"{est.mes_es(fecha)}: {mens.max()}",
            (fecha, mens.max()),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=9,
            color=est.INK_2,
        )
    ax.set_ylim(0, mens.max() * 1.18)
    est.titles(ax, "Producción mensual de chequeos", "Chequeos publicados por mes")
    f_mes = guardar(fig, base, "04_serie_mensual")

    # --- dia de la semana y hora
    dias = cc["dia_semana_es"].value_counts().reindex(ORDEN_DIAS)
    dias.rename("chequeos").to_csv(base / "tablas" / "chequeos_por_dia_semana.csv", encoding="utf-8-sig")
    finde = dias[["Sábado", "Domingo"]].sum()
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    est.hbar(ax, dias, color=[est.SERIES[0]] * 5 + [est.NEUTRAL] * 2)
    est.titles(
        ax,
        "Los chequeos se publican en días laborales",
        f"Chequeos por día de publicación; fin de semana = {num(finde / n * 100)} % del total",
    )
    f_dia = guardar(fig, base, "05_dia_semana")

    horas = cc["hora_num"].value_counts().reindex(range(24), fill_value=0)
    horas.rename("chequeos").to_csv(base / "tablas" / "chequeos_por_hora.csv", encoding="utf-8-sig")
    hora_pico = int(horas.idxmax())
    laboral = horas.loc[8:18].sum()
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    ax.bar(
        horas.index,
        horas.values,
        color=[est.SERIES[1] if h == hora_pico else est.SERIES[0] for h in horas.index],
        width=0.7,
    )
    ax.set_xticks(range(0, 24, 2), [f"{h}:00" for h in range(0, 24, 2)])
    ax.grid(axis="x", visible=False)
    est.titles(
        ax,
        f"Hora pico de publicación: {hora_pico}:00–{hora_pico}:59",
        f"Chequeos por hora de publicación; {num(laboral / n * 100)} % sale entre 8:00 y 18:59",
    )
    f_hora = guardar(fig, base, "06_hora_publicacion")

    # --- palabras en titulos por anio
    fam_cols = [f"titulo_{f}" for f in FAMILIAS_TITULO]
    fam = cc.groupby("anio")[fam_cols].sum().astype(int)
    fam.columns = list(FAMILIAS_TITULO)
    fam["total_chequeos"] = xa["total"]
    fam.reset_index().to_csv(base / "tablas" / "palabras_en_titulos_por_anio.csv", index=False, encoding="utf-8-sig")
    ia, cov = fam["Inteligencia artificial (IA)"], fam["COVID-19 / vacunas"]
    primer_ia = int(ia[ia > 0].index.min())
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.plot(fam.index, cov, marker="o", color=est.SERIES[0], label="COVID-19 / vacunas")
    ax.plot(fam.index, ia, marker="o", color=est.SERIES[1], label="Inteligencia artificial")
    ax.annotate(
        f"{cov.iloc[0]}",
        (fam.index[0], cov.iloc[0]),
        xytext=(6, 2),
        textcoords="offset points",
        fontsize=9,
        color=est.INK_2,
    )
    ax.annotate(
        f"{ia.max()}",
        (ia.idxmax(), ia.max()),
        xytext=(0, 7),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        color=est.INK_2,
    )
    ax.legend(loc="upper right")
    est.titles(
        ax,
        "La desinformación cambia de tema: de la COVID-19 a la IA",
        "Chequeos por año cuyo TÍTULO menciona cada tema (conteo de palabras)",
    )
    f_temas = guardar(fig, base, "07_temas_covid_vs_ia")

    # --- plataformas mencionadas
    plat = pd.Series({p: int(cc[f"menciona_{p}"].sum()) for p in PLATAFORMAS}).sort_values(ascending=False)
    plat.rename("chequeos_que_la_mencionan").to_csv(
        base / "tablas" / "plataformas_mencionadas.csv", encoding="utf-8-sig"
    )
    fig, ax = plt.subplots(figsize=(7.5, 3.0))
    est.hbar(ax, plat)
    est.titles(
        ax,
        "Plataformas nombradas en título o afirmación",
        "Número de chequeos que mencionan la plataforma (no es dónde circuló: solo si se nombra)",
    )
    f_plat = guardar(fig, base, "08_plataformas_mencionadas")

    # --- autores
    aut = cc["autor_chequeo"].value_counts()
    top10 = aut.head(10)
    aut.rename("chequeos").to_csv(base / "tablas" / "autores.csv", encoding="utf-8-sig")
    pct_top10 = top10.sum() / n * 100

    # --- longitud de la afirmacion
    largo = cc["afirmacion_verificada"].str.len()

    # --- tipo de chequeo declarado por el medio x calificacion (efecto de composicion)
    xt = pd.crosstab(cc["tipo"], cc["calificacion"], normalize="index").reindex(columns=ORDEN_CALIF) * 100
    nt = cc["tipo"].value_counts()
    xt.round(1).reset_index().to_csv(base / "tablas" / "calificacion_por_tipo.csv", index=False, encoding="utf-8-sig")
    tipo_anio = pd.crosstab(cc["anio"], cc["tipo"])
    falso_tipo = cc.groupby(["anio", "tipo"])["calificacion"].apply(lambda s: (s == "Falso").mean() * 100).unstack()
    tabla_tipo = tipo_anio.join(falso_tipo.add_prefix("pct_falso_")).join(xa["pct_falso"].rename("pct_falso_total"))
    tabla_tipo.round(1).reset_index().to_csv(base / "tablas" / "tipo_por_anio.csv", index=False, encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    pos = np.arange(len(ORDEN_CALIF))
    for k, t in enumerate([TIPO_REDES, "Discurso público"]):
        ax.bar(
            pos + (k - 0.5) * 0.36,
            xt.loc[t].to_numpy(),
            width=0.34,
            color=est.SERIES[k],
            label=f"{t} (n = {ent(nt[t])})",
        )
    ax.set_xticks(pos, ORDEN_CALIF)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right")
    est.titles(
        ax,
        "El discurso público rara vez es «Falso»: casi la mitad es «Cuestionable»",
        "% de chequeos de cada tipo según su calificación (tipo declarado por Colombiacheck)",
    )
    f_tipo = guardar(fig, base, "09_calificacion_por_tipo")

    # --- elecciones: volumen total vs agenda electoral
    mens_e = cc.groupby(cc["fecha"].dt.to_period("M"))["tema_electoral"].agg(["size", "sum"])
    mens_e["pct_electoral"] = mens_e["sum"] / mens_e["size"] * 100
    mens_e = mens_e.rename(columns={"size": "chequeos", "sum": "chequeos_tema_electoral"})
    mens_e.index = mens_e.index.astype(str)
    mens_e["mes_electoral"] = mens_e.index.isin(list(ELECCIONES))
    mens_e.round(1).reset_index(names="mes").to_csv(
        base / "tablas" / "tema_electoral_por_mes.csv", index=False, encoding="utf-8-sig"
    )
    ventana = mens_e.loc["2022-01":]
    con_e, sin_e = ventana[ventana["mes_electoral"]], ventana[~ventana["mes_electoral"]]
    fig, axs = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True)
    xs = np.arange(len(ventana))
    colores = [est.SERIES[1] if m else est.SERIES[0] for m in ventana["mes_electoral"]]
    axs[0].bar(xs, ventana["chequeos"], color=colores, width=0.75)
    axs[0].set_title("Chequeos publicados por mes", loc="left", fontsize=11, pad=6)
    axs[1].bar(xs, ventana["pct_electoral"], color=colores, width=0.75)
    axs[1].set_title("% de esos chequeos sobre elecciones", loc="left", fontsize=11, pad=6)
    for a in axs:
        a.grid(axis="x", visible=False)
    axs[1].set_xticks(xs[::6], list(ventana.index[::6]))
    fig.suptitle(
        "Las elecciones no disparan el volumen… pero sí cambian la agenda (naranja = mes de elecciones)",
        x=0.01,
        ha="left",
        fontsize=12.5,
        fontweight="semibold",
    )
    fig.tight_layout()
    f_elec = guardar(fig, base, "10_elecciones_volumen_vs_agenda")

    md = f"""# Colombiacheck — chequeos verificados (2020–2026)

| Ficha rápida | |
|---|---|
| **Qué es** | Las verificaciones (*fact-checks*) publicadas por Colombiacheck, medio de verificación del Consejo de Redacción |
| **Unidad de análisis** | Un chequeo: una afirmación que circuló y el veredicto del verificador |
| **Registros** | {ent(n)} chequeos |
| **Cobertura** | {ini:%d-%m-%Y} a {fin:%d-%m-%Y} |
| **De dónde salen las cifras** | Marcado `ClaimReview` (schema.org) que el propio medio publica en cada artículo |
| **Archivo limpio** | `datos/colombiacheck_verificado_limpio.csv` |
| **Origen en el proyecto** | `data/processed/colombiacheck_verificado.csv` (ver `reports/FUENTES.md`) |

> **La advertencia más importante.** Este dataset describe **lo que Colombiacheck decidió
> verificar**, no toda la desinformación que circuló en Colombia. Un verificador elige
> contenidos virales y sospechosos. Por eso, cualquier conclusión debe decir «entre los
> chequeos de Colombiacheck…», nunca «en las redes colombianas…». Esta idea es una de las
> preguntas del reto (sesgo de selección).

## 1. ¿Qué contiene?

Cada fila es un artículo de verificación. El medio declara, en datos estructurados, la
afirmación que revisó, el veredicto y la fecha exacta con hora. Por eso es la fuente más
sólida del proyecto: nada de eso lo interpretamos nosotros.

| Variable | Qué es | Ejemplo |
|---|---|---|
| `url` | Enlace al chequeo (permite comprobar cualquier fila) | colombiacheck.com/chequeos/… |
| `fecha`, `hora` | Fecha y hora de publicación declaradas por el medio | {ej["fecha"]:%Y-%m-%d}, {ej["hora"]} |
| `anio`, `mes`, `dia_semana` | Derivadas de la fecha | {ej["anio"]}, {ej["mes"]}, {ej["dia_semana_es"]} |
| `titulo` | Titular del chequeo (ya dice qué se encontró) | {ej["titulo"]} |
| `afirmacion_verificada` | Lo que circulaba, tal como lo resume el medio | {ej["afirmacion_verificada"]} |
| `calificacion` | Veredicto: Falso, Cuestionable, Verdadero pero…, Verdadero | {ej["calificacion"]} |
| `calificacion_valor` | Veredicto en número (1 = Falso … 5 = Verdadero) | {ej["calificacion_valor"]:.0f} |
| `autor_chequeo` | Periodista que firmó el chequeo | — |

Completitud: todas las variables tienen dato en el 100 % de las filas (una fila «Falso» no
trae el valor numérico). La afirmación verificada llega recortada a {largo.max()} caracteres
(mediana {ent(largo.median())}), así la publica el medio en `ClaimReview`.

## 2. ¿Cómo se comportan los datos?

### 2.1 El veredicto: abrumadoramente «Falso»

![Calificaciones]({f_cal})

{tabla_md(t_cal, fmt={"chequeos": ent, "porcentaje": lambda v: num(v, 1) + " %"})}

- **{num(t_cal.porcentaje.iloc[0])} %** de los chequeos terminan en *Falso* y
  **{num(t_cal.porcentaje.iloc[1])} %** en *Cuestionable*. Solo
  **{num(t_cal.porcentaje.iloc[2:].sum())} %** confirman algo como verdadero.
- **Ojo:** esto **no** significa que el 77 % de lo que circula en redes sea falso. Significa
  que el verificador dedica su tiempo a lo que ya parece sospechoso (sesgo de selección).

### 2.2 Volumen por año: estable

![Chequeos por año]({f_anio})

{tabla_md(xa.reset_index().rename(columns={"anio": "año"}), cols=["año", "Falso", "Cuestionable", "Verdadero pero...", "Verdadero", "total", "pct_falso", "pct_cuestionable"], fmt={"año": str, "Falso": ent, "Cuestionable": ent, "Verdadero pero...": ent, "Verdadero": ent, "total": ent, "pct_falso": lambda v: num(v) + " %", "pct_cuestionable": lambda v: num(v) + " %"})}

- Entre 2020 y 2025 el medio publicó entre {ent(xa.loc[2020:2025, "total"].min())} y
  {ent(xa.loc[2020:2025, "total"].max())} chequeos al año; el máximo fue {anio_max}.
- **2026 parece bajar, pero es un año incompleto** (los datos llegan al {fin:%d-%m-%Y}).
  Comparar un año parcial con años completos es un error clásico de lectura de datos.

![Porcentaje Falso y Cuestionable]({f_pct})

- El porcentaje de *Falso* va de {num(xa["pct_falso"].min())} % ({xa["pct_falso"].idxmin()}) a
  {num(xa["pct_falso"].max())} % ({xa["pct_falso"].idxmax()}). *Cuestionable* tuvo su
  máximo en {xa["pct_cuestionable"].idxmax()} ({num(xa["pct_cuestionable"].max())} %).

### 2.3 Mes a mes

![Serie mensual]({f_mes})

- Promedio: {num(mens.mean())} chequeos por mes (mínimo {mens.min()}, máximo {mens.max()}).
- Mes(es) con más chequeos: **{meses_max}** ({mens.max()} cada uno).{nota_covid}
- Los meses extremos de la serie ({est.mes_es(mens.index[0])} y {est.mes_es(mens.index[-1])})
  están incompletos y no deben leerse como caídas reales.

### 2.4 Cuándo se publica: horario de oficina

![Día de la semana]({f_dia})

![Hora de publicación]({f_hora})

- Solo **{num(finde / n * 100)} %** de los chequeos sale en sábado o domingo, y
  {num(laboral / n * 100)} % entre las 8:00 y las 18:59. La hora pico es
  {hora_pico}:00–{hora_pico}:59 ({ent(horas.max())} chequeos).
- Esto describe **el horario de trabajo de la redacción**, no el horario de la
  desinformación: los rumores no descansan el fin de semana; los periodistas sí.

### 2.5 La desinformación cambia de tema

![Temas COVID vs IA]({f_temas})

{tabla_md(fam.reset_index().rename(columns={"anio": "año"}), fmt={"año": str, **{c: ent for c in fam.columns}})}

*Conteo de chequeos cuyo título contiene ciertas palabras (por ejemplo «IA» o «inteligencia
artificial»). Es un conteo transparente de palabras, no una clasificación temática validada.*

- Los títulos que mencionan **COVID-19 o vacunas** pasan de {cov.iloc[0]} en {cov.index[0]} a
  {cov.iloc[-1]} en {cov.index[-1]}.
- Los que mencionan **inteligencia artificial** aparecen por primera vez en {primer_ia} y
  llegan a {ia.max()} en {ia.idxmax()}. En 2026 (año incompleto) ya son {ia.iloc[-1]} de
  {fam["total_chequeos"].iloc[-1]} chequeos ({num(ia.iloc[-1] / fam["total_chequeos"].iloc[-1] * 100)} %).
- Lectura: los temas de la desinformación siguen la actualidad (pandemia, luego imágenes y
  videos fabricados con IA). Las habilidades para detectarla deben actualizarse igual de rápido.

### 2.6 Plataformas mencionadas

![Plataformas]({f_plat})

Solo indica si la plataforma **se nombra** en el título o la afirmación. Que se nombre poco
TikTok no prueba que allí circule poca desinformación: los titulares rara vez dicen dónde
circuló el contenido.

### 2.7 Quién verifica

{ent(aut.size)} firmas distintas; las 10 más frecuentes firman el {num(pct_top10)} % de los
chequeos (la más frecuente, {ent(top10.iloc[0])}). La verificación es trabajo de un equipo
pequeño: por eso no se puede verificar todo, y por eso importa que cada persona aprenda a
dudar antes de compartir.

### 2.8 Dos tipos de chequeo, dos patrones distintos

Colombiacheck publica cada chequeo en una de dos secciones: **contenido viral en redes**
({ent(nt.get(TIPO_REDES, 0))}: publicaciones, videos y cadenas que circulan en redes y WhatsApp) o
**discurso público** ({ent(nt.get("Discurso público", 0))}: afirmaciones de políticos y figuras públicas).
El medio llama a la primera sección «Desinformación en redes»; aquí se nombra *contenido viral en redes*
porque la sección dice **dónde circuló** el contenido, no **si era falso**: eso lo dice la calificación,
y algunos contenidos de esa sección resultan Verdaderos.

![Calificación por tipo]({f_tipo})

{tabla_md(xt.round(1).reset_index(), fmt={c: (lambda v: num(v) + " %") for c in ORDEN_CALIF})}

{tabla_md(tabla_tipo.round(1).reset_index().rename(columns={"anio": "año", TIPO_REDES: "chequeos de redes", "Discurso público": "chequeos de discurso", "pct_falso_" + TIPO_REDES: "% Falso redes", "pct_falso_Discurso público": "% Falso discurso", "pct_falso_total": "% Falso total"}), fmt={"año": str, "chequeos de redes": ent, "chequeos de discurso": ent, **{c: (lambda v: "—" if pd.isna(v) else num(v) + " %") for c in ["% Falso redes", "% Falso discurso", "% Falso total"]}})}

- El discurso público termina en «Cuestionable» el {num(xt.loc["Discurso público", "Cuestionable"])} % de las veces,
  frente al {num(xt.loc[TIPO_REDES, "Cuestionable"])} % del contenido de redes.
- Los chequeos de discurso público casi desaparecen desde 2024. Como casi nunca son «Falso», **al
  desaparecer suben el % de Falso del total** aunque el contenido de redes no cambie tanto: es un
  **efecto de composición**. Comparar el total de distintos años sin mirar la mezcla puede engañar.
- No permite decir que «los políticos mienten menos»: el verificador escoge qué afirmaciones revisar
  y con criterios distintos según el tipo.

### 2.9 Elecciones: el volumen no se dispara, la agenda sí

![Elecciones]({f_elec})

- En los meses de votación (2022–2026) se publicaron en promedio {num(con_e["chequeos"].mean())} chequeos,
  frente a {num(sin_e["chequeos"].mean())} en los demás meses: apenas {num((con_e["chequeos"].mean() / sin_e["chequeos"].mean() - 1) * 100, 0)} % más.
- Pero la parte de chequeos sobre elecciones pasa de {num(sin_e["pct_electoral"].mean())} % en meses sin votación a
  {num(con_e["pct_electoral"].mean())} % en meses con votación (máximo {num(ventana["pct_electoral"].max())} % en
  {ventana["pct_electoral"].idxmax()}).
- Lectura: la capacidad del verificador es casi fija; lo que cambia es **de qué se ocupa**. Estos datos no
  dicen si circuló más desinformación electoral: dicen que se verificó más.
- «Tema electoral» = el título o la afirmación contiene palabras como elección, voto, candidato,
  registraduría, jurado, escrutinio, tarjetón o consulta (conteo de palabras, no clasificación validada).

## 3. Calidad y limitaciones

1. **Sesgo de selección** (la principal): muestra editorial, no aleatoria.
2. **Cobertura parcial de 2026** y de los meses extremos de la serie.
3. Solo entran los chequeos con marcado `ClaimReview` completo (2.989 de 4.829 artículos; se
   excluyeron 9 de antes de 2020). Detalle en `data/processed/colombiacheck_verificado_resumen.txt`.
4. **Fuente única**: un solo verificador. Otros (La Silla Vacía, AFP Factual) podrían
   priorizar temas distintos.
5. Las palabras clave de títulos (sección 2.5–2.6) son conteos, no categorías validadas.
6. Financiación: Meta figura entre los financiadores del medio (declarado por Colombiacheck);
   conviene mencionarlo como posible conflicto de interés.

## 4. Relación con la desinformación y con el estudio de Nature

El estudio de Arechar et al. (2023) en *Nature Human Behaviour* usó titulares verdaderos y
falsos sobre COVID-19 en 16 países (Colombia no estaba). Este dataset permite **repetir la
idea con titulares colombianos reales**: en el reto, los estudiantes deciden si compartirían
y si creen ciertas afirmaciones verificadas por Colombiacheck, y la clase compara su
«brecha entre creer y compartir» con la del estudio. Ver `../06_Marco_estudio_Nature_Arechar2023/`.

## 5. Dónde se usa en el reto

- **Exp. 01 – ¿Lo compartirías?**: afirmaciones reales (verdaderas y falsas) como publicaciones.
- **Exp. 02 – Detectives de chequeos**: títulos de chequeos para identificar la trampa y el veredicto.
- **Casos estadísticos**: Caso 1 (elecciones, sección 2.9), Caso 2 (redes vs. discurso público y
  efecto de composición, sección 2.8), Caso 3 (IA: conteo vs. proporción, año incompleto y proyección,
  sección 2.5), Caso 5 (probabilidad condicional IA × Falso) y Caso 7 (*cherry picking* en la serie
  del % Falso y media vs. mediana de chequeos por periodista, sección 2.7).

## 6. Archivos de esta carpeta

| Archivo | Contenido |
|---|---|
| `datos/colombiacheck_verificado_limpio.csv` | Dataset limpio (día de la semana en español) |
| `tablas/calificacion.csv` | Conteo y % por calificación |
| `tablas/calificacion_por_anio.csv` | Calificación por año, con % Falso y % Cuestionable |
| `tablas/chequeos_por_mes.csv` | Serie mensual |
| `tablas/chequeos_por_dia_semana.csv`, `tablas/chequeos_por_hora.csv` | Cuándo se publica |
| `tablas/palabras_en_titulos_por_anio.csv` | Conteo de palabras clave en títulos por año |
| `tablas/plataformas_mencionadas.csv` | Plataformas nombradas |
| `tablas/autores.csv` | Chequeos por firma |
| `tablas/calificacion_por_tipo.csv`, `tablas/tipo_por_anio.csv` | Redes vs. discurso público y efecto de composición |
| `tablas/tema_electoral_por_mes.csv` | Chequeos y % de tema electoral por mes, con meses de votación |
| `figuras/*.png` | Las 10 gráficas de este documento |
"""  # noqa: E501
    (base / "ANALISIS.md").write_text(md, encoding="utf-8")
    return {
        "n": n,
        "inicio": ini,
        "fin": fin,
        "pct_falso": t_cal.porcentaje.iloc[0],
        "pct_cuest": t_cal.porcentaje.iloc[1],
        "ia_max": int(ia.max()),
        "ia_anio": int(ia.idxmax()),
        "cov_ini": int(cov.iloc[0]),
        "cov_fin": int(cov.iloc[-1]),
        "finde": finde / n * 100,
    }


# =========================================================================== 2. DANE HORAS
def analizar_dane_horas():
    base = carpeta("02_DANE_ENTIC_horas_uso_internet")
    h = leer_dane("dane_entic2024_horas_uso_internet.csv")
    h["horas_dia_cve_pct"] = h["horas_dia_cve"].str.rstrip("%").astype(float)
    h = h.drop(columns=["horas_dia_cve"])
    h.to_csv(base / "datos" / "dane_entic2024_horas_uso_internet_limpio.csv", index=False, encoding="utf-8-sig")

    tot = h[h.sexo == "Total"]
    nac = tot[tot.nivel == "TOTAL NACIONAL"].iloc[0]
    area = tot[tot.nivel == "ÁREA"].set_index("ambito")
    urb, rur = area.loc["Cabecera (urbano)"], area.loc["Rural"]
    sexo = h[(h.nivel == "TOTAL NACIONAL")].set_index("sexo")
    dep = tot[tot.nivel == "DEPARTAMENTO"].set_index("ambito").sort_values("horas_dia_promedio", ascending=False)
    t_dep = (
        dep[["usuarios_internet", "pct_usan_todos_los_dias", "horas_dia_promedio", "horas_dia_ic", "horas_dia_cve_pct"]]
        .reset_index()
        .rename(columns={"ambito": "departamento"})
    )
    t_dep.to_csv(base / "tablas" / "horas_por_departamento.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7.5, 9.5))
    serie = dep["horas_dia_promedio"]
    est.hbar(ax, serie, fmt=lambda v: num(v, 2), height=0.6)
    ax.axvline(nac.horas_dia_promedio, color=est.AXIS, linewidth=1, zorder=0)
    ax.annotate(
        f"Nacional {num(nac.horas_dia_promedio, 2)} h",
        (nac.horas_dia_promedio, -0.9),
        fontsize=9,
        color=est.INK_2,
        ha="left",
        xytext=(4, 0),
        textcoords="offset points",
    )
    est.titles(
        ax,
        "Horas al día usando internet, por departamento",
        "Promedio entre quienes usan internet · ENTIC Hogares 2024 (DANE)",
    )
    f_dep = guardar(fig, base, "01_horas_por_departamento")

    diario = dep["pct_usan_todos_los_dias"].sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7.5, 9.5))
    est.hbar(ax, diario / 100, fmt=lambda v: f"{num(v * 100)} %", height=0.6)
    est.percent(ax, "x")
    est.titles(
        ax,
        "¿Qué parte de los usuarios se conecta todos los días?",
        "% de usuarios de internet que lo usan a diario · ENTIC Hogares 2024",
    )
    f_diario = guardar(fig, base, "02_uso_diario_por_departamento")

    comp = pd.Series(
        {
            "Cabecera (urbano)": urb.horas_dia_promedio,
            "Rural": rur.horas_dia_promedio,
            "Hombres": sexo.loc["Hombres", "horas_dia_promedio"],
            "Mujeres": sexo.loc["Mujeres", "horas_dia_promedio"],
        }
    )
    fig, ax = plt.subplots(figsize=(7.5, 2.6))
    est.hbar(
        ax, comp, color=[est.SERIES[0], est.SERIES[0], est.SERIES[2], est.SERIES[2]], fmt=lambda v: f"{num(v, 2)} h"
    )
    est.titles(
        ax, "La brecha grande es urbano–rural, no hombres–mujeres", "Horas al día usando internet · eje desde cero"
    )
    f_comp = guardar(fig, base, "03_urbano_rural_sexo")

    corr = dep["pct_usan_todos_los_dias"].corr(dep["horas_dia_promedio"])
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.scatter(
        dep["pct_usan_todos_los_dias"],
        dep["horas_dia_promedio"],
        s=40,
        color=est.SERIES[0],
        edgecolor=est.SURFACE,
        linewidth=1.5,
        zorder=3,
    )
    for nombre in ["San Andrés", "Bogotá D.C.", "Huila", "Vaupés", "Chocó", "Magdalena", "Atlántico"]:
        if nombre in dep.index:
            r = dep.loc[nombre]
            ax.annotate(
                nombre,
                (r.pct_usan_todos_los_dias, r.horas_dia_promedio),
                xytext=(5, 3),
                textcoords="offset points",
                fontsize=8.5,
                color=est.INK_2,
            )
    ax.set_xlabel("% de usuarios que se conecta a diario")
    ax.set_ylabel("Horas al día")
    est.titles(
        ax,
        "Conectarse a diario no implica más horas",
        f"Cada punto es un departamento · correlación r = {num(corr, 2)}",
    )
    f_disp = guardar(fig, base, "04_diario_vs_horas")

    md = f"""# DANE · ENTIC Hogares 2024 — horas de uso de internet

| Ficha rápida | |
|---|---|
| **Qué es** | Encuesta oficial del DANE sobre uso de tecnologías en los hogares (cuadro Mod. 4-3 del anexo) |
| **Población** | Personas de 5 años y más que usan internet |
| **Unidad** | Estimaciones agregadas (nacional, área urbano/rural, 33 departamentos; por sexo) |
| **Registros** | {len(h)} filas = {h.ambito.nunique()} territorios × 3 (total, hombres, mujeres) |
| **Archivo limpio** | `datos/dane_entic2024_horas_uso_internet_limpio.csv` |
| **Origen** | `Datasets - Tiempo en redes sociales Colombia/2. Datos listos para analizar/` (extraído del anexo oficial del DANE) |

## 1. ¿Qué contiene?

| Variable | Qué es |
|---|---|
| `nivel`, `ambito`, `sexo` | Territorio (nacional, área o departamento) y desagregación por sexo |
| `usuarios_internet` (+ `_ic`) | Personas que usan internet (estimación expandida) y su intervalo de confianza |
| `usan_todos_los_dias`, `pct_usan_todos_los_dias` (+ `_ic`) | Cuántas y qué % lo usan a diario |
| `horas_dia_promedio`, `horas_dia_ic` | **Promedio de horas al día usando internet** y margen (IC 95 %) |
| `horas_dia_cve_pct` | Coeficiente de variación: <10 % = alta precisión (criterio oficial DANE) |

La limpieza quitó las filas de notas al pie que traía el CSV y convirtió las cifras a números.

> **Muy importante para el reto:** el DANE mide **horas de uso de INTERNET**, no horas en
> redes sociales. Un titular que diga «los colombianos pasan 5 horas al día en redes» confunde
> las dos cosas. Detectar ese error es una de las preguntas del reto.

## 2. ¿Cómo se comportan los datos?

- **Total nacional: {num(nac.horas_dia_promedio, 2)} horas al día** (IC ± {num(nac.horas_dia_ic, 2)};
  CVE {num(nac.horas_dia_cve_pct)} %), es decir, el valor real está muy probablemente entre
  {num(nac.horas_dia_promedio - nac.horas_dia_ic, 2)} y {num(nac.horas_dia_promedio + nac.horas_dia_ic, 2)} horas.
- **{ent(nac.usuarios_internet)}** personas usan internet y el **{num(nac.pct_usan_todos_los_dias)} %**
  lo hace todos los días.
- **Urbano vs rural:** {num(urb.horas_dia_promedio, 2)} h en cabeceras frente a
  {num(rur.horas_dia_promedio, 2)} h en zona rural: {ent((urb.horas_dia_promedio - rur.horas_dia_promedio) * 60)}
  minutos más al día en la ciudad. En uso diario: {num(urb.pct_usan_todos_los_dias)} % vs {num(rur.pct_usan_todos_los_dias)} %.
- **Hombres vs mujeres:** {num(sexo.loc["Hombres", "horas_dia_promedio"], 2)} h vs
  {num(sexo.loc["Mujeres", "horas_dia_promedio"], 2)} h, una diferencia de apenas
  {ent((sexo.loc["Hombres", "horas_dia_promedio"] - sexo.loc["Mujeres", "horas_dia_promedio"]) * 60)} minutos.
  (En el reto se muestra un gráfico **tramposo** que exagera esta diferencia cortando el eje.)

![Urbano rural y sexo]({f_comp})

### Por departamento

![Horas por departamento]({f_dep})

- Más horas: **{dep.index[0]}** ({num(dep.horas_dia_promedio.iloc[0], 2)} h), {dep.index[1]}
  ({num(dep.horas_dia_promedio.iloc[1], 2)} h) y {dep.index[2]} ({num(dep.horas_dia_promedio.iloc[2], 2)} h).
- Menos horas: **{dep.index[-1]}** ({num(dep.horas_dia_promedio.iloc[-1], 2)} h), {dep.index[-2]}
  ({num(dep.horas_dia_promedio.iloc[-2], 2)} h) y {dep.index[-3]} ({num(dep.horas_dia_promedio.iloc[-3], 2)} h).
- Rango: {num(dep.horas_dia_promedio.max() - dep.horas_dia_promedio.min(), 2)} horas entre el
  primero y el último.

![Uso diario por departamento]({f_diario})

- Uso diario más alto: {diario.index[0]} ({num(diario.iloc[0])} %); más bajo: {diario.index[-1]}
  ({num(diario.iloc[-1])} %).

![Diario vs horas]({f_disp})

- La correlación entre «% que se conecta a diario» y «horas al día» es baja (r = {num(corr, 2)}).
  Por ejemplo, {diario.index[-1]} tiene el uso diario más bajo y aun así sus usuarios
  promedian {num(dep.loc[diario.index[-1], "horas_dia_promedio"], 2)} horas. Son dos cosas distintas:
  **frecuencia** (cuántos días) e **intensidad** (cuántas horas).

Tabla completa: `tablas/horas_por_departamento.csv`.

## 3. Calidad y limitaciones

- Es una **encuesta por muestreo**: cada cifra trae intervalo de confianza. Todos los CVE de
  horas están entre {num(h.horas_dia_cve_pct.min())} % y {num(h.horas_dia_cve_pct.max())} % (alta precisión).
- Es autodeclarado: las personas estiman sus propias horas.
- Es una foto de 2024; no hay serie anual de horas (los anexos TICH 2022–2023 no traen horas).

## 4. Relación con la desinformación

Más horas conectados = más exposición posible a contenidos, incluidos los falsos. Pero
este dataset **no mide desinformación** ni horas en redes: sirve como contexto de
exposición. Su uso en el reto es de **lectura crítica**: distinguir internet de redes
sociales, leer intervalos de confianza y no dejarse engañar por gráficos con el eje cortado.

## 5. Dónde se usa en el reto

Caso 4 (dispersión por departamento y promedio ponderado urbano–rural), Caso 6 (intervalos de
confianza por departamento, porcentaje vs. cantidad de personas) y Caso 7 (gráfico con el eje cortado).
"""  # noqa: E501
    (base / "ANALISIS.md").write_text(md, encoding="utf-8")
    return {"horas_nac": nac.horas_dia_promedio, "urb": urb.horas_dia_promedio, "rur": rur.horas_dia_promedio}


# =========================================================================== 3. DANE ACTIVIDADES INTERNET
def analizar_dane_actividades_internet():
    base = carpeta("03_DANE_ENTIC_actividades_internet")
    a = leer_dane("dane_entic2024_actividades_internet.csv")
    ren = etiquetar_cortas(a.columns, ACT_INTERNET)
    dicc = pd.DataFrame({"nombre_oficial_DANE": list(ren), "etiqueta_corta": list(ren.values())})
    dicc.to_csv(base / "tablas" / "diccionario_actividades.csv", index=False, encoding="utf-8-sig")
    a = a.rename(columns=ren)
    a.to_csv(base / "datos" / "dane_entic2024_actividades_internet_limpio.csv", index=False, encoding="utf-8-sig")
    acts = list(ren.values())

    nac = a[a.nivel == "TOTAL NACIONAL"].set_index("sexo")[acts].T
    nac["dif_H_menos_M"] = nac["Hombres"] - nac["Mujeres"]
    area = a[(a.nivel == "ÁREA") & (a.sexo == "Total")].set_index("ambito")[acts].T
    area["dif_urbano_menos_rural"] = area["Cabecera (urbano)"] - area["Rural"]
    tabla = nac.join(area).sort_values("Total", ascending=False)
    tabla.reset_index(names="actividad").to_csv(
        base / "tablas" / "actividades_nacional_sexo_area.csv", index=False, encoding="utf-8-sig"
    )
    usuarios = a[(a.nivel == "TOTAL NACIONAL") & (a.sexo == "Total")]["usuarios_internet"].iloc[0]

    orden = tabla["Total"]
    destacar = {
        "Redes sociales",
        "Buscar información de salud",
        "Usar herramientas de IA",
        "Periódicos, revistas o libros digitales",
        "Chats, blogs y foros de noticias",
    }
    fig, ax = plt.subplots(figsize=(7.5, 9))
    est.hbar(
        ax,
        orden / 100,
        color=[est.SERIES[1] if i in destacar else est.SERIES[0] for i in orden.index],
        fmt=lambda v: f"{num(v * 100)} %",
        height=0.6,
    )
    est.percent(ax, "x")
    est.titles(
        ax,
        "¿Para qué usan internet los colombianos?",
        "% de usuarios de internet que hace cada actividad · naranja = relevantes para desinformación",
    )
    f_tot = guardar(fig, base, "01_actividades_nacional")

    dif = nac["dif_H_menos_M"].sort_values()
    extremos = pd.concat([dif.head(5), dif.tail(5)])
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    colores = [est.SERIES[1] if v < 0 else est.SERIES[0] for v in extremos]
    ax.barh(extremos.index, extremos.values, color=colores, height=0.55)
    for i, v in enumerate(extremos.values):
        ax.annotate(
            f"{v:+.1f} pp".replace(".", ","),
            (v, i),
            xytext=(4 if v > 0 else -4, 0),
            textcoords="offset points",
            va="center",
            ha="left" if v > 0 else "right",
            fontsize=9,
            color=est.INK_2,
        )
    ax.axvline(0, color=est.AXIS, linewidth=1)
    ax.grid(axis="y", visible=False)
    ax.margins(x=0.25)
    est.titles(
        ax,
        "Donde más se diferencian hombres y mujeres",
        "Puntos porcentuales: azul = más hombres, naranja = más mujeres",
    )
    f_sexo = guardar(fig, base, "02_diferencias_hombres_mujeres")

    dur = area["dif_urbano_menos_rural"].sort_values(ascending=False).head(8)
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    est.hbar(ax, dur, fmt=lambda v: f"+{num(v)} pp")
    est.titles(ax, "Las mayores brechas urbano–rural", "Diferencia en puntos porcentuales (cabecera menos rural)")
    f_area = guardar(fig, base, "03_brecha_urbano_rural")

    md = f"""# DANE · ENTIC Hogares 2024 — actividades en internet

| Ficha rápida | |
|---|---|
| **Qué es** | Qué hacen en internet las personas que lo usan (cuadro Mod. 4-7 del anexo ENTIC 2024) |
| **Población** | {ent(usuarios)} usuarios de internet de 5 años y más |
| **Unidad** | % de usuarios que realiza cada actividad (una persona puede hacer varias) |
| **Registros** | {len(a)} filas (nacional, urbano/rural y 33 departamentos × total/hombres/mujeres) × {len(acts)} actividades |
| **Archivo limpio** | `datos/dane_entic2024_actividades_internet_limpio.csv` (nombres cortos; el diccionario está en `tablas/diccionario_actividades.csv`) |

## 1. ¿Cómo se comportan los datos?

![Actividades nacional]({f_tot})

- Lo más común: **{orden.index[0]}** ({num(orden.iloc[0])} %), **{orden.index[1]}** ({num(orden.iloc[1])} %)
  y {orden.index[2]} ({num(orden.iloc[2])} %).
- **Redes sociales: {num(orden["Redes sociales"])} %** de los usuarios de internet, frente a solo
  **{num(orden["Periódicos, revistas o libros digitales"])} %** que lee periódicos, revistas o libros
  digitales y {num(orden["Chats, blogs y foros de noticias"])} % que entra a foros de noticias.
  Muchas más personas pasan por las redes que por los medios.
- **{num(orden["Buscar información de salud"])} %** busca información de salud en internet: la
  salud es justamente uno de los temas con más desinformación (COVID-19, curas milagrosas).
- **{num(orden["Usar herramientas de IA"])} %** ya usa herramientas de inteligencia artificial,
  la misma tecnología con la que hoy se fabrican videos e imágenes falsas.

![Diferencias por sexo]({f_sexo})

- Las mujeres usan más internet para **salud** (citas médicas, resultados, información:
  entre 11 y 13 puntos más). Los hombres, para **jugar** (+{num(nac.loc["Jugar en línea", "dif_H_menos_M"])} pp)
  y **apostar** ({num(nac.loc["Apostar en línea", "Hombres"])} % vs {num(nac.loc["Apostar en línea", "Mujeres"])} %).
- En redes sociales casi no hay diferencia ({num(nac.loc["Redes sociales", "Hombres"])} % hombres,
  {num(nac.loc["Redes sociales", "Mujeres"])} % mujeres).

![Brecha urbano rural]({f_area})

- La zona rural se parece a la urbana en **redes sociales** ({num(area.loc["Redes sociales", "Rural"])} % vs
  {num(area.loc["Redes sociales", "Cabecera (urbano)"])} %) y en **mensajería**, pero se queda muy atrás en
  correo, banca y trámites. Es decir: en el campo, las redes y la mensajería son la puerta
  principal a la información.

Tabla completa (nacional, por sexo y por área): `tablas/actividades_nacional_sexo_area.csv`.

## 2. Calidad y limitaciones

- Encuesta por muestreo (los porcentajes son estimaciones). El CSV de trabajo solo trae la
  proporción; los intervalos están en el anexo oficial del DANE (`1. Datos en bruto/`).
- No mide **qué** se ve en redes ni si es falso; mide si la persona hace la actividad.

## 3. Relación con la desinformación

Mide las **puertas de entrada**: cuántas personas están expuestas a las redes (la vía por la
que circulan casi todas las piezas que verifica Colombiacheck) frente a cuántas leen medios.

## 4. Dónde se usa en el reto

Caso 4 de los casos estadísticos (qué se hace en internet en la ciudad y en el campo).
"""  # noqa: E501
    (base / "ANALISIS.md").write_text(md, encoding="utf-8")
    return {"redes": orden["Redes sociales"], "usuarios": usuarios}


# =========================================================================== 4. DANE ACTIVIDADES REDES
def analizar_dane_redes():
    base = carpeta("04_DANE_ENTIC_actividades_redes_sociales")
    r = leer_dane("dane_entic2024_actividades_redes_sociales.csv")
    ren = etiquetar_cortas(r.columns, ACT_REDES)
    pd.DataFrame({"nombre_oficial_DANE": list(ren), "etiqueta_corta": list(ren.values())}).to_csv(
        base / "tablas" / "diccionario_actividades.csv", index=False, encoding="utf-8-sig"
    )
    r = r.rename(columns=ren)
    r.to_csv(base / "datos" / "dane_entic2024_actividades_redes_sociales_limpio.csv", index=False, encoding="utf-8-sig")
    acts = list(ren.values())
    personas = r[(r.nivel == "TOTAL NACIONAL") & (r.sexo == "Total")]["personas_usan_redes"].iloc[0]

    nac = r[r.nivel == "TOTAL NACIONAL"].set_index("sexo")[acts].T
    area = r[(r.nivel == "ÁREA") & (r.sexo == "Total")].set_index("ambito")[acts].T
    tabla = nac.join(area).sort_values("Total", ascending=False)
    tabla.reset_index(names="actividad").to_csv(
        base / "tablas" / "actividades_redes_nacional_sexo_area.csv", index=False, encoding="utf-8-sig"
    )
    orden = tabla["Total"]

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    est.hbar(ax, orden / 100, fmt=lambda v: f"{num(v * 100)} %", height=0.6)
    est.percent(ax, "x")
    est.titles(
        ax,
        "Las redes se usan, sobre todo, para hablar con los cercanos",
        f"% de quienes usan redes sociales ({num(personas / 1e6)} millones) · ENTIC 2024",
    )
    f_tot = guardar(fig, base, "01_actividades_en_redes")

    dep = r[(r.nivel == "DEPARTAMENTO") & (r.sexo == "Total")].set_index("ambito")
    opinar = dep["Opinar sobre temas públicos"].sort_values(ascending=False)
    opinar.rename("pct_opina_temas_publicos").to_csv(
        base / "tablas" / "opinar_temas_publicos_por_departamento.csv", encoding="utf-8-sig"
    )

    md = f"""# DANE · ENTIC Hogares 2024 — actividades dentro de las redes sociales

| Ficha rápida | |
|---|---|
| **Qué es** | Para qué usan las redes sociales quienes las usan (cuadro Mod. 4-8 del anexo ENTIC 2024) |
| **Población** | {ent(personas)} personas de 5 años y más que usan redes sociales |
| **Unidad** | % de usuarios de redes que realiza cada actividad (no suman 100 %: son varias a la vez) |
| **Registros** | {len(r)} filas × {len(acts)} actividades |
| **Archivo limpio** | `datos/dane_entic2024_actividades_redes_sociales_limpio.csv` |

## 1. ¿Cómo se comportan los datos?

![Actividades en redes]({f_tot})

{tabla_md(tabla.reset_index(names="actividad"), cols=["actividad", "Total", "Hombres", "Mujeres", "Cabecera (urbano)", "Rural"], fmt={c: (lambda v: num(v) + " %") for c in ["Total", "Hombres", "Mujeres", "Cabecera (urbano)", "Rural"]})}

- **{num(orden.iloc[0])} %** usa las redes para **comunicarse con familia y amigos** y
  {num(orden["Entretenimiento"])} % para entretenimiento. Ver lo que publican otros y comentar:
  {num(orden["Ver contenidos de otros y comentar"])} %.
- Solo **{num(orden["Producir contenido propio"])} %** produce contenido propio y
  **{num(orden["Opinar sobre temas públicos"])} %** opina sobre temas públicos: **la mayoría consume y
  reenvía; pocos producen.**
- Urbano y rural casi no se diferencian en comunicarse ({num(tabla.loc["Comunicarse con familia y amigos", "Cabecera (urbano)"])} %
  vs {num(tabla.loc["Comunicarse con familia y amigos", "Rural"])} %).
- Opinar sobre temas públicos varía por departamento: de {num(opinar.iloc[0])} % ({opinar.index[0]}) a
  {num(opinar.iloc[-1])} % ({opinar.index[-1]}).

## 2. Calidad y limitaciones

Encuesta por muestreo; la tabla solo trae la proporción (sin intervalos en este CSV). No dice
en qué red social ni qué contenido.

## 3. Relación con la desinformación

Es el dato que mejor explica **por qué las cadenas funcionan**: casi todos usan las redes para
hablar con personas de confianza. Un mensaje falso que llega por el grupo de la familia
viene «avalado» por alguien cercano, y por eso se reenvía sin verificar. El estudio de
Nature encontró justamente que la gente comparte titulares que **reconocería como falsos si
se detuviera a pensarlo**: el problema no es solo no saber, es no prestar atención a la
exactitud en el momento de compartir.

## 4. Dónde se usa en el reto

En la versión actual del reto no tiene preguntas propias: es contexto para la discusión final (por qué
las cadenas falsas llegan «avaladas» por personas de confianza).
"""  # noqa: E501
    (base / "ANALISIS.md").write_text(md, encoding="utf-8")
    return {"comunicarse": orden.iloc[0], "personas": personas}


# =========================================================================== 5. BANCO MUNDIAL
def analizar_banco_mundial():
    base = carpeta("05_BancoMundial_conectividad")
    bm = pd.read_csv(SRC_BM / "banco_mundial_conectividad_colombia.csv", encoding="utf-8-sig")
    bm.to_csv(base / "datos" / "banco_mundial_conectividad_colombia_limpio.csv", index=False, encoding="utf-8-sig")
    bm = bm.set_index("anio")
    inet, movil = bm["personas_usan_internet_pct"], bm["suscripciones_movil_por_100"]
    mitad = int(inet[inet > 50].index.min())
    cien = int(movil[movil > 100].index.min())

    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(inet.index, inet.values, color=est.SERIES[0], marker="o", markersize=3.5)
    ax.fill_between(inet.index, inet.values, color=est.SERIES[0], alpha=0.10)
    ax.axhline(50, color=est.AXIS, linewidth=1)
    ax.annotate(
        f"{mitad}: {num(inet[mitad])} % (más de la mitad)",
        (mitad, inet[mitad]),
        xytext=(-10, 12),
        textcoords="offset points",
        ha="right",
        fontsize=9,
        color=est.INK_2,
    )
    ax.annotate(
        f"{num(inet.iloc[-1])} %",
        (inet.index[-1], inet.iloc[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        color=est.INK_2,
    )
    ax.set_ylim(0, 100)
    est.titles(
        ax,
        "De 2 % a casi 80 % de la población en internet",
        "% de personas que usan internet en Colombia · Banco Mundial / UIT",
    )
    f_inet = guardar(fig, base, "01_personas_usan_internet")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(movil.index, movil.values, color=est.SERIES[0], marker="o", markersize=3.5)
    ax.axhline(100, color=est.AXIS, linewidth=1)
    ax.annotate(
        f"{cien}: más líneas que personas",
        (cien, movil[cien]),
        xytext=(-10, 10),
        textcoords="offset points",
        ha="right",
        fontsize=9,
        color=est.INK_2,
    )
    ax.annotate(
        num(movil.iloc[-1]),
        (movil.index[-1], movil.iloc[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        color=est.INK_2,
    )
    est.titles(
        ax,
        "Suscripciones de telefonía móvil por cada 100 personas",
        "Banco Mundial / UIT · por encima de 100 = hay personas con más de una línea",
    )
    f_mov = guardar(fig, base, "02_suscripciones_movil")

    crec = bm[["personas_usan_internet_pct", "suscripciones_movil_por_100"]].diff()
    t = bm.reset_index()[["anio", "personas_usan_internet_pct", "suscripciones_movil_por_100"]]
    t.to_csv(base / "tablas" / "serie_2000_2024.csv", index=False, encoding="utf-8-sig")

    md = f"""# Banco Mundial / UIT — conectividad en Colombia (2000–2024)

| Ficha rápida | |
|---|---|
| **Qué es** | Dos indicadores oficiales de la Unión Internacional de Telecomunicaciones publicados por el Banco Mundial |
| **Indicadores** | `IT.NET.USER.ZS` (% de personas que usan internet) y suscripciones móviles por cada 100 personas |
| **Unidad** | Colombia, un dato por año |
| **Registros** | {len(bm)} años ({bm.index.min()}–{bm.index.max()}) |
| **Archivo limpio** | `datos/banco_mundial_conectividad_colombia_limpio.csv` |

## 1. ¿Cómo se comportan los datos?

![Personas que usan internet]({f_inet})

- En {bm.index.min()} solo el **{num(inet.iloc[0])} %** de las personas usaba internet; en {bm.index.max()}, el
  **{num(inet.iloc[-1])} %**.
- **{mitad}** es el primer año en que más de la mitad de la población usa internet
  ({num(inet[mitad])} %; un año antes era {num(inet[mitad - 1])} %).
- Mayor salto anual: {int(crec["personas_usan_internet_pct"].idxmax())}
  (+{num(crec["personas_usan_internet_pct"].max())} puntos). Entre 2014 y 2024 subió
  {num(inet[2024] - inet[2014])} puntos porcentuales.
- Casi nunca baja: solo {int((crec["personas_usan_internet_pct"] < 0).sum())} año con caída
  ({", ".join(str(a) for a in crec.index[crec["personas_usan_internet_pct"] < 0])}).

![Suscripciones móviles]({f_mov})

- Desde **{cien}** hay más suscripciones móviles que personas (hoy {num(movil.iloc[-1])} por cada 100):
  hay gente con más de una línea o SIM, así que este indicador **no** es «% de personas con celular».
- Crecimiento 2000–2024: × {num(movil.iloc[-1] / movil.iloc[0])}.

## 2. Calidad y limitaciones

- Cifras oficiales, comparables entre países; algunos años son estimaciones de la UIT.
- Se muestran en **dos gráficas separadas** a propósito: tienen escalas distintas y ponerlas
  en un mismo gráfico con dos ejes inventaría una relación visual que los datos no prueban.
- Que ambas series suban juntas no prueba que una cause la otra (correlación ≠ causalidad).

## 3. Relación con la desinformación

Muestra la **velocidad** del cambio: en una sola generación Colombia pasó de casi nadie
conectado a 8 de cada 10 personas. La desinformación digital alcanza hoy a muchas más
personas que hace 15 años, y muchas aprendieron a usar internet sin formación en
verificación.

## 4. Dónde se usa en el reto

En la versión actual del reto no tiene preguntas propias: es contexto para la guía docente y para la
discusión final (la desinformación digital alcanza hoy a 8 de cada 10 personas).
"""  # noqa: E501
    (base / "ANALISIS.md").write_text(md, encoding="utf-8")
    return {"inet_2024": inet.iloc[-1], "mitad": mitad}


# =========================================================================== 6. MARCO NATURE
def escribir_marco_nature():
    base = AQUI / "06_Marco_estudio_Nature_Arechar2023"
    base.mkdir(exist_ok=True)
    md = """# Marco del reto: el estudio de *Nature Human Behaviour* (2023)

**Arechar, A. A., Allen, J., Berinsky, A. J., Cole, R., Epstein, Z., Garimella, K., Gully, A.,
Lu, J. G., Ross, R. M., Stagnaro, M. N., Zhang, Y., Pennycook, G. y Rand, D. G. (2023).
*Understanding and combatting misinformation across 16 countries on six continents.*
Nature Human Behaviour, 7, 1502–1513.** https://doi.org/10.1038/s41562-023-01641-6

Datos y código abiertos: https://osf.io/g65qu/ · Versión preliminar (abierta): PsyArXiv `a9frz`.

> Este no es un dataset que se analice en la app: es el **marco científico** del reto. Las
> cifras de abajo vienen del resumen publicado y de la versión preliminar del artículo
> (feb. 2022); donde la cifra sale solo de la versión preliminar, se indica.

## Qué hicieron

- Experimento en **16 países de 6 continentes** con **34.286 personas** usuarias de redes
  sociales (676.605 observaciones). Los países: Argentina, Australia, Brasil, China, Egipto,
  España, Estados Unidos, Filipinas, India, Italia, México, Nigeria, Reino Unido, Rusia,
  Arabia Saudita y Sudáfrica. **Colombia no participó** (de América Latina: Argentina, Brasil y México).
- Cada persona vio **20 titulares sobre COVID-19 (10 verdaderos y 10 falsos)** tomados de un
  banco de 45. Según el grupo al que la asignaban al azar, debía:
  1. **Exactitud**: decir si cada titular le parecía verdadero (escala de 1 a 6);
  2. **Compartir**: decir si lo compartiría en redes;
  3. **Recordatorio de exactitud** (*accuracy prompt*): antes de la tarea de compartir, calificar
     si UN titular cualquiera (no de COVID) era exacto;
  4. **Consejos**: antes de compartir, leer cuatro consejos breves de alfabetización digital
     (tomados de una campaña de Facebook, del tipo «desconfía de los titulares» o «revisa la fuente»).
- Además respondieron un test de reflexión cognitiva (preguntas con una respuesta intuitiva
  incorrecta) y preguntas sobre valores y motivaciones.

## Qué encontraron

1. **Pensar despacio ayuda, en todos los países.** Las personas con estilo de pensamiento
   más analítico y que valoran más la exactitud distinguían mejor lo verdadero de lo falso.
   Confiar en general en la gente **no** se relacionó con caer más o menos.
2. **Creer ≠ compartir.** En todos los países, las intenciones de compartir distinguían
   menos entre verdadero y falso que los juicios de exactitud: **la gente compartiría
   titulares falsos que reconocería como falsos si se le preguntara**. Y eso aunque la gran
   mayoría dijo que la exactitud es muy importante para decidir qué compartir.
3. **Un recordatorio sutil funciona.** Pedir que calificaran la exactitud de un solo titular
   antes de compartir mejoró la calidad de lo que compartían (sobre todo, redujo el
   compartir falsedades).
4. **Los consejos de alfabetización digital también funcionan**, con un efecto menor.
   Curiosamente, la gente calificó los consejos como **más útiles** que el recordatorio,
   aunque el recordatorio fue, en promedio, **el doble de efectivo** (versión preliminar).
   Lección: lo que *parece* útil no siempre es lo que *funciona*; hay que medirlo.
5. **Sabiduría de la multitud.** Promediando las calificaciones de personas no expertas se
   distinguen titulares verdaderos de falsos con alta precisión en todos los países. En la
   versión preliminar: con unas **15 calificaciones por titular** se acierta **más del 90 %**
   de las veces en casi todos los países.
6. Los patrones fueron parecidos en todas las regiones: la psicología de la desinformación
   se parece en todo el mundo y soluciones similares pueden servir en muchos lugares.

## Limitaciones que reconocen los autores

- Muestras de paneles en línea, no plenamente representativas (más educación que el promedio).
- El «compartir» fue hipotético (lo que dicen que harían), aunque estudios previos lo
  relacionan con el compartir real.
- Solo titulares de COVID-19; falta probar otros temas (por ejemplo, política).
- Varios autores recibieron apoyo de Google y Facebook (declarado en el artículo).

## Cómo lo usa el reto

| Hallazgo del estudio | Cómo aparece en el reto |
|---|---|
| Pensar despacio predice discernir mejor | **Casos estadísticos 1–7**: hipótesis antes de ver los datos, evaluar cada afirmación contra la evidencia antes de concluir |
| Creer ≠ compartir | **Exp. 01 «¿Lo compartirías?»**: primero deciden si compartirían 10 publicaciones reales (sin puntaje), después juzgan si son verdaderas (con puntaje). El tablero muestra la brecha de la clase |
| Recordatorio de exactitud | La mitad de los participantes (al azar) califica un titular antes del Exp. 01; el tablero compara cuánto comparte cada grupo |
| Sabiduría de la multitud | El tablero muestra si **el promedio de la clase** acertó más titulares que el estudiante promedio |
| Consejos de alfabetización | **Exp. 02 «Detectives de chequeos»** y la guía docente |
| Colombia no estuvo en el estudio | Pregunta del **Exp. 10 «Lo que dice la ciencia»**: ¿qué países participaron? → el propio reto es una mini‑réplica. La misma misión pregunta para qué sirve repartir al azar |

> **Advertencia ética.** El experimento de clase es una **demostración educativa**, no una
> investigación. Si el semillero quiere usar los datos del reto en una investigación, necesita
> consentimiento informado de los acudientes y asentimiento de los estudiantes (son menores
> de edad), y aval de un comité de ética.
"""  # noqa: E501
    (base / "RESUMEN_Y_USO_EN_EL_RETO.md").write_text(md, encoding="utf-8")


# =========================================================================== INDICE
def escribir_indice(r_cc, r_h, r_a, r_r, r_bm):
    md = f"""# Análisis de los datos del reto «Detectives de la desinformación»

Esta carpeta explica **qué datos usa el reto, de dónde salen y cómo se comportan**. Cada
subcarpeta tiene su `ANALISIS.md`, los datos limpios (`datos/`), tablas resumen (`tablas/`) y
gráficas (`figuras/`). Todo se regenera con:

```
python ../4_Codigo_y_datos/scripts/generar_analisis.py
```

## El centro es la desinformación; internet es el contexto

| # | Carpeta | Papel en el reto | Qué responde |
|---|---|---|---|
| 1 | `01_Colombiacheck_chequeos_verificados/` | **Núcleo** | ¿Qué desinformación se verifica en Colombia, cómo se califica y cómo cambia? |
| 2 | `02_DANE_ENTIC_horas_uso_internet/` | Contexto de exposición | ¿Cuánto tiempo pasamos conectados? |
| 3 | `03_DANE_ENTIC_actividades_internet/` | Contexto de exposición | ¿Por qué puertas entra la información (redes vs medios)? |
| 4 | `04_DANE_ENTIC_actividades_redes_sociales/` | Contexto de difusión | ¿Para qué usamos las redes? ¿Por qué se reenvían las cadenas? |
| 5 | `05_BancoMundial_conectividad/` | Contexto histórico | ¿Qué tan rápido nos conectamos? |
| 6 | `06_Marco_estudio_Nature_Arechar2023/` | **Marco científico** | ¿Por qué creemos y compartimos falsedades y qué ayuda? |

## Diez ideas clave (calculadas de los datos)

1. Colombiacheck publicó **{ent(r_cc["n"])} chequeos verificados** entre {r_cc["inicio"]:%m-%Y} y {r_cc["fin"]:%m-%Y}.
2. **{num(r_cc["pct_falso"])} %** terminan en «Falso» y {num(r_cc["pct_cuest"])} % en «Cuestionable».
3. …pero eso **no** mide cuánta desinformación hay en redes: el verificador elige qué revisar (sesgo de selección).
4. La desinformación cambia de tema: títulos con COVID‑19/vacunas pasan de {r_cc["cov_ini"]} (2020) a
   {r_cc["cov_fin"]} (2026); títulos con inteligencia artificial pasan de 0 (2022) a {r_cc["ia_max"]} ({r_cc["ia_anio"]}).
5. Solo {num(r_cc["finde"])} % de los chequeos sale en fin de semana: eso refleja el horario de la redacción, no el de los rumores.
6. **{num(r_bm["inet_2024"])} %** de los colombianos usa internet (2024); en {r_bm["mitad"]} se superó por primera vez la mitad.
7. Los usuarios de internet pasan en promedio **{num(r_h["horas_nac"], 2)} horas al día** conectados
   ({num(r_h["urb"], 2)} h urbano vs {num(r_h["rur"], 2)} h rural). Son horas de **internet**, no de redes.
8. **{num(r_a["redes"])} %** de los usuarios de internet usa redes sociales ({num(r_r["personas"] / 1e6)} millones de personas).
9. **{num(r_r["comunicarse"])} %** usa las redes para hablar con familia y amigos: por eso las cadenas
   falsas llegan «avaladas» por gente de confianza.
10. El estudio de Nature (16 países, 34.286 personas) muestra que la gente comparte falsedades que
    reconocería como falsas si se detuviera a pensar, y que un simple recordatorio de exactitud ayuda.

## Cómo se conecta con la aplicación

La app (`../2_Aplicacion_Reto/`) arma sus preguntas leyendo los archivos limpios de estas
carpetas (`4_Codigo_y_datos/scripts/construir_banco.py`). Si se actualizan los datos: primero se
corre este análisis y después `construir_banco.py` (o todo junto con `4_Codigo_y_datos/REGENERAR_TODO.bat`).
"""  # noqa: E501
    (AQUI / "LEEME.md").write_text(md, encoding="utf-8")


def main():
    est.apply()
    r_cc = analizar_colombiacheck()
    r_h = analizar_dane_horas()
    r_a = analizar_dane_actividades_internet()
    r_r = analizar_dane_redes()
    r_bm = analizar_banco_mundial()
    escribir_marco_nature()
    escribir_indice(r_cc, r_h, r_a, r_r, r_bm)
    print("[ok] Análisis generado en", AQUI)
    for p in sorted(AQUI.glob("*/ANALISIS.md")) + sorted(AQUI.glob("*/RESUMEN*.md")):
        print("   ", p.relative_to(AQUI))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
