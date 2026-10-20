"""Estilo comun de las graficas del EDA (matplotlib).

Paleta validada (colorblind-safe) con el validador de la guia de visualizacion:
- Categorica, maximo 3 series: azul, naranja, aqua.
- Ordinal para la calificacion de veracidad: un solo tono azul, mas oscuro = mas falso;
  "Inchequeable" queda en gris neutro porque no pertenece a la escala.
- Secuencial (mapas de calor): rampa azul clara -> oscura.
"""
import matplotlib as mpl
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, Normalize

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # slots 1-3
NEUTRAL = "#c3c2b7"

CALIF_COLORS = {
    "Falso": "#104281",
    "Engañoso": "#104281",
    "Cuestionable": "#256abf",
    "Sin evidencia": "#256abf",
    "Verdadero pero": "#5598e7",
    "Verdadero": "#86b6ef",
    "Inchequeable": NEUTRAL,
    "Chequeo múltiple": NEUTRAL,
    "Sin veredicto único": NEUTRAL,  # múltiple + inchequeable, agrupados en graficas apiladas
}

BLUE_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
             "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
SEQ_CMAP = LinearSegmentedColormap.from_list("azul_secuencial", BLUE_RAMP)

MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def apply():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "figure.dpi": 110,
        "savefig.dpi": 160,
        "savefig.bbox": "tight",
        "font.family": ["Segoe UI", "DejaVu Sans", "sans-serif"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.titlepad": 26,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "legend.frameon": False,
        "legend.labelcolor": INK_2,
        "legend.fontsize": 9,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
    })


def n_fmt(v):
    return f"{v:,.0f}".replace(",", ".")


def pct_fmt(v, dec=0):
    return f"{v:.{dec}%}"


def mes_es(ts):
    return f"{MESES_ES[ts.month - 1]} {ts.year}"


def titles(ax, title, sub=None):
    """Titulo en tinta primaria y subtitulo gris justo debajo."""
    ax.set_title(title)
    if sub:
        ax.annotate(sub, (0, 1), xycoords="axes fraction", xytext=(0, 7), textcoords="offset points",
                    color=INK_2, fontsize=9.5, va="bottom", ha="left")


def thousands(ax, axis="y"):
    fmt = mpl.ticker.FuncFormatter(lambda v, _: n_fmt(v))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def percent(ax, axis="y"):
    fmt = mpl.ticker.FuncFormatter(lambda v, _: f"{v:.0%}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def hbar(ax, s, color=SERIES[0], fmt=n_fmt, height=0.55):
    """Barras horizontales en el orden de `s` (primer elemento arriba), valor en la punta."""
    s = s.iloc[::-1]
    colors = list(color)[::-1] if isinstance(color, (list, tuple)) else color
    bars = ax.barh([str(i) for i in s.index], s.to_numpy(dtype=float), height=height, color=colors)
    for b, v in zip(bars, s.to_numpy(dtype=float)):
        ax.annotate(fmt(v), (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=9, color=INK_2)
    ax.grid(axis="y", visible=False)
    ax.margins(x=0.16)
    ax.spines["left"].set_visible(False)
    thousands(ax, "x")  # para porcentajes, llamar percent(ax, "x") despues
    return bars


def stacked(ax, comp, colors, horizontal=False, width=0.55):
    """Barras apiladas al 100 % con separacion de 2px en color de superficie entre segmentos."""
    base = np.zeros(len(comp))
    pos = np.arange(len(comp))
    for col in comp.columns:
        vals = comp[col].to_numpy(dtype=float)
        kw = dict(color=colors.get(col, NEUTRAL), edgecolor=SURFACE, linewidth=1.5, label=str(col))
        if horizontal:
            ax.barh(pos, vals, left=base, height=width, **kw)
        else:
            ax.bar(pos, vals, bottom=base, width=width, **kw)
        base += vals
    labels = [str(i) for i in comp.index]
    if horizontal:
        ax.set_yticks(pos, labels)
        ax.set_xlim(0, 1)
        percent(ax, "x")
        ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
    else:
        ax.set_xticks(pos, labels)
        ax.set_ylim(0, 1)
        percent(ax, "y")
        ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), handlelength=1, handleheight=1)


def heatmap(ax, tab, fmt=lambda v: f"{v:.0%}", vmax=None, cbar_label=None, cbar_fmt=lambda v, _: f"{v:.0%}"):
    """Mapa de calor secuencial (azul) con celdas separadas por 2px y texto con contraste suficiente."""
    vals = tab.to_numpy(dtype=float)
    norm = Normalize(0, vmax if vmax is not None else np.nanmax(vals))
    im = ax.imshow(vals, cmap=SEQ_CMAP, norm=norm, aspect="auto")
    ax.set_xticks(range(tab.shape[1]), [str(c) for c in tab.columns])
    ax.set_yticks(range(tab.shape[0]), [str(i) for i in tab.index])
    ax.grid(which="major", visible=False)
    ax.set_xticks(np.arange(-0.5, tab.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, tab.shape[0]), minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    ax.tick_params(which="minor", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            v = vals[i, j]
            if np.isnan(v):
                continue
            r, g, b, _ = SEQ_CMAP(norm(v))
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            ax.text(j, i, fmt(v), ha="center", va="center", fontsize=8, color="white" if lum < 0.5 else INK)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, labelcolor=INK_2, length=0)
    cb.ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(cbar_fmt))
    if cbar_label:
        cb.set_label(cbar_label, color=INK_2, fontsize=9)
    return im


def save(fig, name, folder):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.png"
    fig.savefig(path)
    return path
