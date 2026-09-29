# -*- coding: utf-8 -*-
"""Figures for the statistics terms reference v2 (single-column layout).
Output: fig/<key>.svg + fig/<key>.png (preview) and facts.json with every number shown on a figure."""
import io, json, pathlib, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE / "fig"
OUT.mkdir(exist_ok=True)
for f in ("Inter-400.ttf", "Inter-600.ttf"):  # optional: without them the figures fall back to DejaVu Sans
    if (HERE / "fonts" / f).exists():
        font_manager.fontManager.addfont(str(HERE / "fonts" / f))
    else:
        print(f"fonts/{f} not found: figures will use DejaVu Sans")

INK, INK2, MUTED, AXIS, GRID = "#1b2330", "#323c4a", "#5d6775", "#b3bcc6", "#e6e9ed"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8d97a3"
BLUE_L, BLUE_M, BLUE_D = "#9ec5f4", "#5598e7", "#184f95"
MM = 1 / 25.4
COLW, WIDE, FULL = 100 * MM, 151 * MM, 182 * MM

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 7, "svg.fonttype": "none", "svg.hashsalt": "stats-terms-2",
    "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.labelcolor": MUTED, "axes.labelsize": 6.6,
    "axes.titlesize": 7, "axes.titleweight": 600, "axes.titlecolor": INK, "axes.titlelocation": "left",
    "axes.titlepad": 3,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 6.2, "ytick.labelsize": 6.2,
    "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
    "xtick.major.pad": 1.5, "ytick.major.pad": 1.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-",
    "lines.linewidth": 1.3, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    "legend.frameon": False, "legend.fontsize": 6.3, "legend.handlelength": 1.5, "legend.borderaxespad": 0,
    "text.color": INK, "axes.unicode_minus": True, "figure.dpi": 150,
})

FACTS = {}


def comma(x, pos=None):
    s = f"{x:g}"
    return s.replace("-", "−").replace(".", ",")


def num(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def clean(ax, y=False, x=True):
    if not y:
        ax.spines["left"].set_visible(False)
        ax.set_yticks([])
    if not x:
        ax.spines["bottom"].set_visible(False)
        ax.set_xticks([])
    ax.xaxis.set_major_formatter(FuncFormatter(comma))
    ax.yaxis.set_major_formatter(FuncFormatter(comma))


def save(fig, key):
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True)
    svg = buf.getvalue()
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg)
    svg = re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S)
    svg = re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=re.S)
    svg = re.sub(r'(<svg[^>]*?)\s+width="[^"]+"\s+height="[^"]+"', r"\1", svg, count=1)
    svg = re.sub(r'id="([^"]+)"', rf'id="{key}-\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#{key}-\1)", svg)
    svg = re.sub(r'(xlink:href|href)="#([^"]+)"', rf'\1="#{key}-\2"', svg)
    svg = svg.replace("<svg ", f'<svg class="chart" role="img" aria-labelledby="{key}-cap" ', 1)
    (OUT / f"{key}.svg").write_text(svg, encoding="utf-8")
    fig.savefig(OUT / f"{key}.png", dpi=300, facecolor="white")
    plt.close(fig)


def lum(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


# ================================================================== 1. box plot anatomy
def fig_box():
    r = np.random.default_rng(11)
    x = np.concatenate([r.gamma(3.0, 1.0, 118), [9.4, 10.8]])
    q1, med, q3 = np.percentile(x, [25, 50, 75])
    iqr = q3 - q1
    lo_f, hi_f = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    wl, wh = x[x >= lo_f].min(), x[x <= hi_f].max()
    outs = np.sort(x[(x < lo_f) | (x > hi_f)])
    mean = x.mean()
    FACTS["box"] = dict(n=len(x), q1=q1, med=med, q3=q3, iqr=iqr, whisker_lo=wl, whisker_hi=wh, fence_hi=hi_f,
                        mean=mean, outliers=outs.tolist())
    XMAX = 11.6
    fig = plt.figure(figsize=(COLW, 50 * MM))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.3], hspace=0.05, left=0.03, right=0.97, top=0.97, bottom=0.12)
    ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1])
    bins = np.arange(0, XMAX, 0.6)
    ax.hist(x, bins=bins, color=BLUE, alpha=0.16, edgecolor="white", linewidth=0.8)
    ax.hist(x, bins=bins, histtype="step", color=BLUE, linewidth=0.8)
    ax.set_xlim(0, XMAX)
    clean(ax, x=False)
    ax.text(0.99, 0.95, f"гистограмма тех же данных (n = {len(x)})", transform=ax.transAxes, ha="right", va="top",
            fontsize=6.2, color=MUTED)
    y0, h = 0.48, 0.26
    bx.add_patch(plt.Rectangle((q1, y0 - h / 2), iqr, h, facecolor=BLUE, alpha=0.14, edgecolor=INK2, linewidth=0.8))
    bx.plot([med, med], [y0 - h / 2, y0 + h / 2], color=INK2, linewidth=1.8)
    bx.plot([wl, q1], [y0, y0], color=INK2, linewidth=0.8)
    bx.plot([q3, wh], [y0, y0], color=INK2, linewidth=0.8)
    for w in (wl, wh):
        bx.plot([w, w], [y0 - h / 4, y0 + h / 4], color=INK2, linewidth=0.8)
    bx.scatter(outs, [y0] * len(outs), s=10, facecolor="white", edgecolor=INK2, linewidth=0.8, zorder=3)
    bx.scatter([mean], [y0], marker="D", s=13, color=ORANGE, zorder=4, edgecolor="white", linewidth=0.6)
    bx.set_ylim(0, 1.12)
    bx.set_xlim(0, XMAX)
    clean(bx)
    bx.set_xticks([0, 2, 4, 6, 8, 10])
    top1, top2 = y0 + h / 2 + 0.05, y0 + h / 2 + 0.3
    kw = dict(fontsize=6.1, color=INK2, ha="center", va="bottom")
    bx.text(q1, top1, "Q1", **kw)
    bx.text(q3, top1, "Q3", **kw)
    bx.plot([med, med], [y0 + h / 2, top2 - 0.02], color=MUTED, linewidth=0.5)
    bx.text(med, top2, "медиана", **kw)
    bx.annotate("", xy=(q1, y0 - h / 2 - 0.1), xytext=(q3, y0 - h / 2 - 0.1),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.6, shrinkA=0, shrinkB=0))
    bx.text((q1 + q3) / 2, y0 - h / 2 - 0.15, "IQR", fontsize=6.1, color=INK2, ha="center", va="top")
    bx.text(wl, y0 - h / 2 - 0.06, "ус", fontsize=6.1, color=INK2, ha="center", va="top")
    bx.text(wh, y0 - h / 2 - 0.06, "ус", fontsize=6.1, color=INK2, ha="center", va="top")
    bx.text(outs.mean(), y0 - h / 2 - 0.06, "выбросы", fontsize=6.1, color=INK2, ha="center", va="top")
    bx.scatter([6.55], [top2 + 0.07], marker="D", s=9, color=ORANGE, edgecolor="white", linewidth=0.4)
    bx.text(6.8, top2, "среднее", fontsize=6.1, color=INK2, ha="left", va="bottom")
    save(fig, "box")


# ================================================================== 2. variance: same mean, different spread
def fig_variance():
    r = np.random.default_rng(21)
    a = r.normal(40, 5, 60)
    b = r.normal(40, 15, 60)
    a = a - a.mean() + 40
    b = b - b.mean() + 40
    sa, sb = a.std(ddof=1), b.std(ddof=1)
    FACTS["variance"] = dict(mean_a=a.mean(), mean_b=b.mean(), s_a=sa, s_b=sb, n=60)
    fig, ax = plt.subplots(figsize=(COLW, 36 * MM))
    fig.subplots_adjust(left=0.2, right=0.97, top=0.95, bottom=0.25)
    for yc, data, s, name in ((1.0, a, sa, "курьер A"), (0.0, b, sb, "курьер B")):
        jit = r.uniform(-0.17, 0.17, len(data))
        ax.scatter(data, yc + jit, s=7, color=BLUE, alpha=0.55, linewidth=0)
        ax.plot([40, 40], [yc - 0.3, yc + 0.3], color=ORANGE, linewidth=1.4)
        ax.annotate("", xy=(40 - s, yc + 0.36), xytext=(40 + s, yc + 0.36),
                    arrowprops=dict(arrowstyle="|-|", color=INK2, lw=0.7, mutation_scale=2.2, shrinkA=0, shrinkB=0))
        ax.text(40 + s + 1, yc + 0.36, f"среднее ± s,  s = {num(s, 1)} мин", fontsize=6.1, color=INK2, va="center")
    ax.set_yticks([1.0, 0.0])
    ax.set_yticklabels(["курьер A", "курьер B"])
    ax.tick_params(axis="y", length=0, labelsize=6.4, labelcolor=INK2)
    ax.spines["left"].set_visible(False)
    ax.set_ylim(-0.45, 1.55)
    ax.set_xlim(0, 80)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.xaxis.set_major_formatter(FuncFormatter(comma))
    ax.set_xlabel("время доставки, мин; оранжевая линия — среднее 40 мин")
    save(fig, "variance")


# ================================================================== 3. correlation panels
def fig_corr():
    r = np.random.default_rng(5)
    n = 60

    def biv(rho):
        z = r.standard_normal((n, 2))
        return z[:, 0], rho * z[:, 0] + np.sqrt(1 - rho ** 2) * z[:, 1]

    panels = [(t, *biv(rho)) for t, rho in (("сильная", 0.9), ("умеренная", 0.5), ("нет связи", 0.0),
                                            ("отрицательная", -0.7))]
    x = np.linspace(-2, 2, n)
    y = x ** 2 + np.random.default_rng(3).normal(0, 0.25, n)
    panels.append(("y = x²", x, y))
    x = r.normal(0, 1, n - 1); y = r.normal(0, 1, n - 1)
    y = y - np.cov(x, y)[0, 1] / np.var(x, ddof=1) * (x - x.mean())
    panels.append(("один выброс", np.append(x, 8.5), np.append(y, 8.5)))
    fig, axes = plt.subplots(1, 6, figsize=(WIDE, 34 * MM))
    fig.subplots_adjust(left=0.005, right=0.995, top=0.86, bottom=0.25, wspace=0.16)
    facts = {}
    for ax, (title, x, y) in zip(axes, panels):
        rr = stats.pearsonr(x, y)[0]
        rs = stats.spearmanr(x, y)[0]
        ax.scatter(x, y, s=4, color=BLUE, alpha=0.75, linewidth=0)
        if title == "один выброс":
            ax.scatter([x[-1]], [y[-1]], s=11, color=ORANGE, edgecolor="white", linewidth=0.5, zorder=3)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=6.4, pad=2.5)
        ax.text(0.5, -0.07, f"r = {num(rr)}", transform=ax.transAxes, ha="center", va="top", fontsize=6.2, color=INK)
        ax.text(0.5, -0.24, f"rₛ = {num(rs)}", transform=ax.transAxes, ha="center", va="top", fontsize=6.0,
                color=MUTED)
        facts[title] = dict(r=rr, rs=rs)
    FACTS["corr"] = facts
    save(fig, "corr")


# ================================================================== 4. heatmaps
def diverging_cmap():
    return LinearSegmentedColormap.from_list(
        "div", [(0.0, "#104281"), (0.25, "#5598e7"), (0.5, "#f0efec"), (0.75, "#e66767"), (1.0, "#9e2a2a")])


def sequential_cmap():
    return LinearSegmentedColormap.from_list("seq", ["#eef4fc", "#9ec5f4", "#3987e5", "#184f95", "#0d366b"])


def fig_heatmap():
    r = np.random.default_rng(8)
    n = 400
    area = r.normal(60, 18, n).clip(25, 140)
    rooms = np.clip(np.round(area / 22 + r.normal(0, 0.5, n)), 1, 6)
    dist = r.uniform(1, 25, n)
    age = r.uniform(0, 60, n)
    floor = r.integers(1, 17, n).astype(float)
    price = 2.0 + 0.12 * area - 0.18 * dist - 0.035 * age + r.normal(0, 1.6, n)
    names = ["площадь", "комнаты", "цена", "до центра", "возраст", "этаж"]
    M = np.corrcoef(np.vstack([area, rooms, price, dist, age, floor]))
    FACTS["heatmap_corr"] = {f"{names[i]}–{names[j]}": M[i, j] for i in range(6) for j in range(i)}
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    hours = np.arange(12) * 2
    base = 2.0 + 1.6 * np.exp(-((hours + 1 - 20) / 3.5) ** 2) + 0.9 * np.exp(-((hours + 1 - 13) / 2.5) ** 2)
    base[hours < 6] -= 1.2
    daymult = np.array([1.0, 1.02, 1.0, 1.05, 1.15, 1.35, 1.3])
    P = np.clip(np.outer(daymult, base) + r.normal(0, 0.12, (7, 12)), 0.3, None)
    FACTS["heatmap_pivot"] = dict(max=float(P.max()), argmax=[days[int(np.argmax(P) // 12)], int(hours[np.argmax(P) % 12])],
                                  min=float(P.min()))
    fig = plt.figure(figsize=(WIDE, 64 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.3], left=0.085, right=0.935, top=0.9, bottom=0.2, wspace=0.3)
    ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1])
    cm = diverging_cmap()
    k = len(names)
    for i in range(k):
        for j in range(k):
            if j >= i:
                continue
            v = M[i, j]
            col = cm((v + 1) / 2)
            hexc = matplotlib.colors.to_hex(col)
            ax.add_patch(plt.Rectangle((j, k - 1 - i), 1, 1, facecolor=col, edgecolor="white", linewidth=1.2))
            ax.text(j + 0.5, k - 1 - i + 0.5, num(v), ha="center", va="center", fontsize=6.0,
                    color="white" if lum(hexc) < 0.35 else INK)
    ax.set_xlim(0, k - 1); ax.set_ylim(0, k - 1)
    ax.set_xticks(np.arange(k - 1) + 0.5); ax.set_xticklabels(names[:-1], rotation=40, ha="right")
    ax.set_yticks(np.arange(k - 1) + 0.5); ax.set_yticklabels(names[1:][::-1])
    ax.tick_params(length=0, labelsize=6.1, labelcolor=INK2)
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_title("Корреляции признаков квартир", fontsize=6.8, pad=4)
    sm = plt.cm.ScalarMappable(cmap=cm, norm=plt.Normalize(-1, 1))
    pos = ax.get_position()
    cax = fig.add_axes([pos.x0 + pos.width * 0.83, pos.y0 + pos.height * 0.42, 0.012, pos.height * 0.56])
    cb = fig.colorbar(sm, cax=cax, ticks=[-1, -0.5, 0, 0.5, 1])
    cb.ax.tick_params(labelsize=5.8, length=1.5, pad=1, labelcolor=MUTED)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(comma))
    cb.outline.set_visible(False)
    cs = sequential_cmap()
    im = bx.imshow(P, cmap=cs, aspect="auto", vmin=0, vmax=np.ceil(P.max()))
    bx.set_xticks(np.arange(12)); bx.set_xticklabels([str(h) for h in hours])
    bx.set_yticks(np.arange(7)); bx.set_yticklabels(days)
    bx.tick_params(length=0, labelsize=6.1, labelcolor=INK2)
    for s in ("left", "bottom"):
        bx.spines[s].set_visible(False)
    bx.set_xlabel("начало двухчасового интервала, ч")
    bx.set_title("Конверсия по дням недели и часам, %", fontsize=6.8, pad=4)
    pos2 = bx.get_position()
    cax2 = fig.add_axes([pos2.x1 + 0.012, pos2.y0, 0.012, pos2.height])
    cb2 = fig.colorbar(im, cax=cax2)
    cb2.ax.tick_params(labelsize=5.8, length=1.5, pad=1, labelcolor=MUTED)
    cb2.outline.set_visible(False)
    cb2.ax.yaxis.set_major_formatter(FuncFormatter(comma))
    save(fig, "heatmap")


# ================================================================== 5. distributions
class Mix:
    def __init__(self, m=2.0, s=0.7):
        self.a, self.b = stats.norm(-m, s), stats.norm(m, s)
        self.m, self.s = m, s

    def pdf(self, x): return 0.5 * self.a.pdf(x) + 0.5 * self.b.pdf(x)
    def cdf(self, x): return 0.5 * self.a.cdf(x) + 0.5 * self.b.cdf(x)
    def sf(self, x): return 1 - self.cdf(x)
    def support(self): return (-np.inf, np.inf)
    def mean(self): return 0.0
    def median(self): return 0.0

    def ppf(self, q):
        from scipy.optimize import brentq
        q = np.atleast_1d(q)
        res = np.array([brentq(lambda t: self.cdf(t) - qq, -20, 20) for qq in q])
        return res

    def rvs(self, size, random_state):
        k = random_state.random(size) < 0.5
        return np.where(k, random_state.normal(-self.m, self.s, size), random_state.normal(self.m, self.s, size))


def outlier_share(d, discrete=False):
    q1, q3 = (float(v) for v in np.atleast_1d(d.ppf([0.25, 0.75])))
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    if discrete:
        return float(d.cdf(np.ceil(lo) - 1) + d.sf(np.floor(hi)))
    return float(d.cdf(lo) + d.sf(hi))


def fig_dists():
    specs = [
        ("Нормальное", "N(0; 1)", stats.norm(), (-4, 4), False),
        ("Равномерное", "U(0; 1)", stats.uniform(), (-0.25, 1.25), False),
        ("Экспоненциальное", "Exp(1)", stats.expon(), (0, 5), False),
        ("Логнормальное", "ln X ~ N(0; 0,8²)", stats.lognorm(0.8), (0, 5), False),
        ("Стьюдента", "t(3)", stats.t(3), (-6, 6), False),
        ("Бимодальное", "смесь N(±2; 0,7²)", Mix(), (-4.5, 4.5), False),
        ("Биномиальное", "B(10; 0,3)", stats.binom(10, 0.3), (-0.8, 10.8), True),
        ("Пуассона", "Pois(1,5)", stats.poisson(1.5), (-0.8, 7.8), True),
    ]
    fig = plt.figure(figsize=(FULL, 96 * MM))
    outer = fig.add_gridspec(2, 4, left=0.012, right=0.988, top=0.885, bottom=0.12, hspace=0.8, wspace=0.12)
    r = np.random.default_rng(2026)
    facts = {}
    for i, (name, par, d, (xa, xb), disc) in enumerate(specs):
        g = outer[i // 4, i % 4].subgridspec(2, 1, height_ratios=[2.1, 1], hspace=0.05)
        ax = fig.add_subplot(g[0]); bx = fig.add_subplot(g[1])
        mean, med = float(d.mean()), float(np.atleast_1d(d.median())[0])
        if disc:
            ks = np.arange(0, int(xb) + 1)
            pm = d.pmf(ks)
            ax.bar(ks, pm, width=0.62, color=BLUE, alpha=0.2, edgecolor=BLUE, linewidth=0.7)
            top = pm.max()
        else:
            xs = np.linspace(xa, xb, 600)
            ys = d.pdf(xs)
            ax.fill_between(xs, ys, color=BLUE, alpha=0.12, linewidth=0)
            ax.plot(xs, ys, color=BLUE, linewidth=1.2)
            top = ys.max()
        ax.set_ylim(0, top * 1.45)
        ax.plot([med, med], [0, top * 1.12], color=INK2, linewidth=1.1)
        ax.plot([mean, mean], [0, top * 1.12], color=ORANGE, linewidth=1.1)
        ax.set_xlim(xa, xb)
        clean(ax, x=False)
        ax.set_title(f"{name} · {par}", fontsize=6.6, pad=2)
        sample = d.rvs(size=1000, random_state=r)
        q1, bmed, q3 = (float(v) for v in np.atleast_1d(d.ppf([0.25, 0.5, 0.75])))
        iqr = q3 - q1
        lo_f, hi_f = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        inside = sample[(sample >= lo_f) & (sample <= hi_f)]
        wl, wh = inside.min(), inside.max()
        outs = sample[(sample < lo_f) | (sample > hi_f)]
        y0, h = 0.5, 0.5
        bx.add_patch(plt.Rectangle((q1, y0 - h / 2), iqr, h, facecolor=BLUE, alpha=0.12, edgecolor=INK2, linewidth=0.7))
        bx.plot([bmed, bmed], [y0 - h / 2, y0 + h / 2], color=INK2, linewidth=1.5)
        bx.plot([wl, q1], [y0, y0], color=INK2, linewidth=0.7)
        bx.plot([q3, wh], [y0, y0], color=INK2, linewidth=0.7)
        for w in (wl, wh):
            bx.plot([w, w], [y0 - h / 4, y0 + h / 4], color=INK2, linewidth=0.7)
        if len(outs):
            jit = r.uniform(-0.16, 0.16, len(outs))
            vis = (outs >= xa) & (outs <= xb)
            bx.scatter(outs[vis], y0 + jit[vis], s=4, facecolor="white", edgecolor=MUTED, linewidth=0.5, zorder=3)
        bx.scatter([mean], [y0], marker="D", s=12, color=ORANGE, edgecolor="white", linewidth=0.5, zorder=4)
        bx.set_ylim(0, 1)
        clean(bx)
        bx.set_xlim(xa, xb)
        bx.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=disc))
        if name == "Равномерное":
            bx.set_xticks([0, 0.25, 0.5, 0.75, 1])
        share = outlier_share(d, discrete=disc)
        if abs(mean - med) < 1e-9:
            txt = f"среднее = медиана = {num(med, 1)}"
        else:
            txt = f"среднее {num(mean)} {'>' if mean > med else '<'} медиана {num(med)}"
        pct = num(share * 100, 1)
        txt2 = "за усами 0%" if share < 1e-6 else f"за усами ≈ {pct}%"
        bx.set_xlabel(f"{txt}\n{txt2}", fontsize=6.0, color=INK2, labelpad=2, linespacing=1.35)
        facts[name] = dict(mean=mean, median=med, q1=q1, q3=q3, outlier_share=share,
                           sample_outlier_share=float(len(outs)) / len(sample))
    handles = [Patch(facecolor=BLUE, alpha=0.2, edgecolor=BLUE, linewidth=0.7, label="плотность / вероятности значений"),
               Line2D([], [], color=INK2, lw=1.2, label="медиана"),
               Line2D([], [], color=ORANGE, lw=1.2, label="среднее"),
               Line2D([], [], color="none", marker="D", markerfacecolor=ORANGE, markeredgecolor="white", markersize=4,
                      label="среднее на ящике"),
               Line2D([], [], color="none", marker="o", markerfacecolor="white", markeredgecolor=MUTED, markersize=3.2,
                      label="выбросы в выборке n = 1000")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.012, 1.0), ncol=5, fontsize=6.2,
               handletextpad=0.5, columnspacing=1.6)
    FACTS["dists"] = facts
    save(fig, "dists")


# ================================================================== 6. LLN
def fig_lln():
    r = np.random.default_rng(3)
    n = np.arange(1, 1001)
    fig, ax = plt.subplots(figsize=(COLW, 42 * MM))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.96, bottom=0.21)
    band = 1.96 * np.sqrt(0.25 / n)
    ax.fill_between(n, 0.5 - band, 0.5 + band, color=GRAY, alpha=0.14, linewidth=0)
    finals = []
    for c in (BLUE, BLUE_M, BLUE_L):
        run = np.cumsum(r.integers(0, 2, 1000)) / n
        ax.plot(n, run, color=c, linewidth=1.0)
        finals.append(float(run[-1]))
    ax.axhline(0.5, color=INK2, linewidth=0.7)
    ax.set_xscale("log")
    ax.set_xlim(1, 1000); ax.set_ylim(0, 1)
    ax.set_xticks([1, 10, 100, 1000]); ax.set_xticklabels(["1", "10", "100", "1000"])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    clean(ax, y=True)
    ax.grid(axis="y")
    ax.set_xlabel("число бросков n (логарифмическая шкала)")
    ax.set_ylabel("доля орлов")
    ax.text(900, 0.5 + 0.2, "0,5 ± 1,96·SE", fontsize=6.1, color=MUTED, ha="right")
    FACTS["lln"] = dict(finals=finals)
    save(fig, "lln")


# ================================================================== 7. CLT
def fig_clt():
    r = np.random.default_rng(12)
    fig, axes = plt.subplots(1, 3, figsize=(COLW, 38 * MM))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.78, bottom=0.17, wspace=0.12)
    xs = np.linspace(0, 3.5, 400)
    for ax, n in zip(axes, (1, 5, 30)):
        means = r.exponential(1.0, (20000, n)).mean(axis=1)
        ax.hist(means, bins=np.arange(0, means.max() + 0.1, 0.1), density=True, color=BLUE, alpha=0.22,
                edgecolor="white", linewidth=0.5)
        ax.plot(xs, stats.norm(1, 1 / np.sqrt(n)).pdf(xs), color=ORANGE, linewidth=1.1)
        ax.set_title(f"n = {n}", fontsize=6.6, pad=2)
        ax.set_xlim(0, 3.5); ax.set_xticks([0, 1, 2, 3])
        clean(ax)
    fig.legend(handles=[Patch(facecolor=BLUE, alpha=0.22, label="средние 20 000 выборок из Exp(1)"),
                        Line2D([], [], color=ORANGE, lw=1.1, label="N(1; 1/n) по ЦПТ")],
               loc="upper left", bbox_to_anchor=(0.02, 1.0), ncol=2, fontsize=6.1, handletextpad=0.5, columnspacing=1.2)
    save(fig, "clt")


# ================================================================== 8. likelihood
def fig_lik():
    p = np.linspace(0, 1, 400)
    L = p ** 3 * (1 - p) ** 7
    Lmax = 0.3 ** 3 * 0.7 ** 7
    fig, ax = plt.subplots(figsize=(COLW, 34 * MM))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.93, bottom=0.27)
    ax.fill_between(p, L, color=BLUE, alpha=0.1, linewidth=0)
    ax.plot(p, L, color=BLUE, linewidth=1.3)
    ax.plot([0.3, 0.3], [0, Lmax], color=INK2, linewidth=0.7)
    ax.scatter([0.3], [Lmax], s=16, color=ORANGE, edgecolor="white", linewidth=0.8, zorder=3)
    ax.text(0.335, Lmax * 1.02, "максимум при p̂ = 0,3", fontsize=6.3, color=INK, va="center")
    ax.text(0.62, Lmax * 0.62, "L(p) = p³(1 − p)⁷", fontsize=6.3, color=INK2, ha="left")
    ax.set_xlim(0, 1); ax.set_ylim(0, Lmax * 1.25)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    clean(ax)
    ax.set_xlabel("параметр p — вероятность успеха")
    FACTS["lik"] = dict(Lmax=Lmax)
    save(fig, "lik")


# ================================================================== 9. CI coverage
def fig_ci():
    mu, sigma, n, K = 50, 10, 20, 40
    tq = stats.t.ppf(0.975, n - 1)
    chosen = None
    for s in range(1, 500):
        r = np.random.default_rng(s)
        X = r.normal(mu, sigma, (K, n))
        m = X.mean(1); se = X.std(1, ddof=1) / np.sqrt(n)
        lo, hi = m - tq * se, m + tq * se
        miss = (lo > mu) | (hi < mu)
        idx = np.where(miss)[0]
        if len(idx) == 2 and idx[0] > 4 and idx[1] < K - 5 and idx[1] - idx[0] > 8:
            chosen = s
            break
    fig, ax = plt.subplots(figsize=(COLW, 60 * MM))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.14)
    ys = np.arange(K, 0, -1)
    for y, a, b, mm_, ms in zip(ys, lo, hi, m, miss):
        c = ORANGE if ms else BLUE
        ax.plot([a, b], [y, y], color=c, linewidth=1.1 if ms else 0.85)
        ax.scatter([mm_], [y], s=5, color=c, zorder=3, linewidth=0)
    ax.axvline(mu, color=INK2, linewidth=0.8)
    ax.text(mu + 0.4, K + 1.3, "истинное μ = 50", fontsize=6.2, color=INK2, ha="left", va="bottom")
    for y, a, b, ms in zip(ys, lo, hi, miss):
        if ms:
            if a > mu:
                ax.text(b + 0.6, y, "не накрыл μ", fontsize=6.1, color=INK2, ha="left", va="center")
            else:
                ax.text(a - 0.6, y, "не накрыл μ", fontsize=6.1, color=INK2, ha="right", va="center")
    ax.set_ylim(0, K + 3.4)
    ax.set_xlim(mu - 17, mu + 17)
    clean(ax)
    covered = K - int(miss.sum())
    ax.set_xlabel(f"95%-е интервалы по {K} выборкам (n = {n}): {covered} из {K} накрыли μ")
    FACTS["ci"] = dict(seed=chosen, misses=int(miss.sum()), covered=covered, K=K, n=n, tq=tq)
    save(fig, "ci")


# ================================================================== 10. p-value and critical region
def fig_pval():
    z = 2.4
    c = stats.norm.ppf(0.975)
    xs = np.linspace(-4, 4, 800)
    ys = stats.norm.pdf(xs)
    p = 2 * stats.norm.sf(z)
    fig, ax = plt.subplots(figsize=(COLW, 42 * MM))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.9, bottom=0.25)
    ax.plot(xs, ys, color=INK2, linewidth=1.2)
    for sel in (xs >= c, xs <= -c):
        ax.fill_between(xs[sel], ys[sel], color=ORANGE, alpha=0.2, linewidth=0)
    for sel in (xs >= z, xs <= -z):
        ax.fill_between(xs[sel], ys[sel], color=ORANGE, alpha=0.75, linewidth=0)
    for cv in (-c, c):
        ax.plot([cv, cv], [0, 0.2], color=MUTED, linewidth=0.7)
    ax.plot([z, z], [0, 0.29], color=ORANGE, linewidth=1.2)
    ax.text(z + 0.07, 0.30, "наблюдали z = 2,4", fontsize=6.2, color=INK, ha="left", va="bottom")
    ax.text(c - 0.08, 0.205, "1,96", fontsize=6.0, color=MUTED, ha="right", va="bottom")
    ax.text(-c + 0.08, 0.205, "−1,96", fontsize=6.0, color=MUTED, ha="left", va="bottom")
    ax.annotate("p/2", xy=(-2.62, 0.006), xytext=(-3.35, 0.085), fontsize=6.2, color=INK2, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
    ax.annotate("p/2", xy=(2.62, 0.006), xytext=(3.35, 0.085), fontsize=6.2, color=INK2, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
    ax.text(0, 0.15, "распределение\nz при H₀: N(0; 1)", fontsize=6.2, color=MUTED, ha="center", va="center")
    ax.set_xlim(-4, 4); ax.set_ylim(0, 0.44)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    clean(ax)
    ax.set_xlabel(f"светлая заливка — критическая область |z| > 1,96 (α = 0,05);\n"
                  f"тёмная — p-value = 2·P(Z ≥ 2,4) ≈ {num(p, 3)}", linespacing=1.4)
    FACTS["pval"] = dict(z=z, p=p, c=c)
    save(fig, "pval")


# ================================================================== 11. errors and power
def fig_power():
    d, c = 2.8, stats.norm.ppf(0.975)
    xs = np.linspace(-3.5, 6.5, 900)
    h0, h1 = stats.norm.pdf(xs), stats.norm.pdf(xs, d)
    fig, ax = plt.subplots(figsize=(COLW, 44 * MM))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.18)
    ax.fill_between(xs[xs >= c], h1[xs >= c], color=BLUE, alpha=0.18, linewidth=0)
    ax.fill_between(xs[xs <= c], h1[xs <= c], color=GRAY, alpha=0.32, linewidth=0)
    ax.fill_between(xs[xs >= c], h0[xs >= c], color=ORANGE, alpha=0.6, linewidth=0)
    ax.fill_between(xs[xs <= -c], h0[xs <= -c], color=ORANGE, alpha=0.6, linewidth=0)
    ax.plot(xs, h0, color=INK2, linewidth=1.1)
    ax.plot(xs, h1, color=BLUE, linewidth=1.2)
    ax.plot([c, c], [0, 0.43], color=INK2, linewidth=0.7)
    power = stats.norm.sf(c - d) + stats.norm.cdf(-c - d)
    beta = 1 - power
    ax.text(-0.25, 0.408, "H₀", fontsize=6.6, color=INK2, ha="right")
    ax.text(d + 0.25, 0.408, "H₁", fontsize=6.6, color=INK, ha="left")
    ax.legend(handles=[Patch(facecolor=ORANGE, alpha=0.6, label="α = 0,05 — ошибка I рода"),
                       Patch(facecolor=GRAY, alpha=0.32, label=f"β ≈ {num(beta)} — ошибка II рода"),
                       Patch(facecolor=BLUE, alpha=0.18, label=f"мощность 1 − β ≈ {num(power)}")],
              loc="upper right", bbox_to_anchor=(1.0, 1.0), fontsize=6.0, handlelength=1.2, handletextpad=0.5,
              labelspacing=0.3)
    ax.set_xlim(-3.5, 6.5); ax.set_ylim(0, 0.6)
    clean(ax)
    ax.set_xticks([-2, 0, c, 2.8, 4, 6])
    ax.set_xticklabels(["−2", "0", "1,96", "2,8", "4", "6"])
    ax.set_xlabel("статистика критерия в единицах SE; истинный эффект δ = 2,8·SE")
    FACTS["power"] = dict(power=power, beta=beta, c=c)
    save(fig, "power")


# ================================================================== 12. QQ plots
def fig_qq():
    r = np.random.default_rng(31)
    n = 120
    data = [("нормальные данные", r.normal(0, 1, n)), ("скошенные вправо", r.lognormal(0, 0.6, n))]
    fig, axes = plt.subplots(1, 2, figsize=(COLW, 42 * MM))
    fig.subplots_adjust(left=0.1, right=0.98, top=0.88, bottom=0.2, wspace=0.28)
    facts = {}
    for ax, (title, x) in zip(axes, data):
        (osm, osr), (slope, inter, rr) = stats.probplot(x, dist="norm")
        ax.scatter(osm, osr, s=5, color=BLUE, alpha=0.8, linewidth=0)
        xx = np.array([osm.min(), osm.max()])
        ax.plot(xx, inter + slope * xx, color=ORANGE, linewidth=1.0)
        ax.set_title(title, fontsize=6.5, pad=2)
        ax.set_xlabel("теоретические квантили N(0; 1)")
        clean(ax, y=True)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        facts[title] = dict(shapiro_p=float(stats.shapiro(x).pvalue))
    axes[0].set_ylabel("выборочные квантили")
    FACTS["qq"] = facts
    save(fig, "qq")


# ================================================================== 13. ANOVA: between vs within
def fig_anova():
    r = np.random.default_rng(44)
    groups = {"A": r.normal(20, 3, 15), "B": r.normal(23, 3, 15), "C": r.normal(26, 3, 15)}
    allv = np.concatenate(list(groups.values()))
    gm = allv.mean()
    F, p = stats.f_oneway(*groups.values())
    ssb = sum(len(v) * (v.mean() - gm) ** 2 for v in groups.values())
    ssw = sum(((v - v.mean()) ** 2).sum() for v in groups.values())
    eta2 = ssb / (ssb + ssw)
    fig, ax = plt.subplots(figsize=(COLW, 46 * MM))
    fig.subplots_adjust(left=0.1, right=0.97, top=0.96, bottom=0.17)
    for i, (g, v) in enumerate(groups.items()):
        xc = i * 1.0
        jit = r.uniform(-0.16, 0.16, len(v))
        ax.scatter(xc + jit, v, s=7, color=BLUE, alpha=0.6, linewidth=0)
        ax.plot([xc - 0.28, xc + 0.28], [v.mean(), v.mean()], color=ORANGE, linewidth=1.5)
    ax.axhline(gm, color=INK2, linewidth=0.7)
    ax.text(-1.0, gm + 0.35, "общее среднее", fontsize=6.0, color=INK2, va="bottom", ha="left")
    v = groups["C"]
    ax.annotate("", xy=(2 + 0.34, v.min()), xytext=(2 + 0.34, v.max()),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.6, shrinkA=0, shrinkB=0))
    ax.text(2.4, v.max(), "внутри-\nгрупповой\nразброс", fontsize=6.0, color=INK2, va="top", ha="left")
    va = groups["A"]
    ax.annotate("", xy=(-0.34, va.mean()), xytext=(-0.34, gm),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(-0.4, (va.mean() + gm) / 2, "между-\nгрупповой", fontsize=6.0, color=INK2, va="center", ha="right")
    ax.set_xlim(-1.05, 3.05)
    clean(ax, y=True)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["группа A", "группа B", "группа C"])
    ax.tick_params(axis="x", length=0, labelsize=6.3, labelcolor=INK2)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax.set_ylabel("значение")
    ptxt = "p < 0,001" if p < 0.001 else f"p = {num(p, 3)}"
    ax.set_xlabel(f"F = {num(F, 1)}, {ptxt}, η² = {num(eta2)}; оранжевые линии — средние групп")
    FACTS["anova"] = dict(F=F, p=p, eta2=eta2, grand=gm, means={k: v.mean() for k, v in groups.items()})
    save(fig, "anova")


# ================================================================== 14. regression + residuals
def fig_reg():
    r = np.random.default_rng(21)
    n = 25
    x = np.sort(r.uniform(0, 10, n)); y = 2 + 0.8 * x + r.normal(0, 1.5, n)
    b1, b0 = np.polyfit(x, y, 1)
    yh = b0 + b1 * x
    r2 = 1 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)
    fig, ax = plt.subplots(figsize=(COLW, 48 * MM))
    fig.subplots_adjust(left=0.09, right=0.97, top=0.96, bottom=0.17)
    for xi, yi, yhi in zip(x, y, yh):
        ax.plot([xi, xi], [yi, yhi], color=GRAY, linewidth=0.6)
    xx = np.linspace(0, 10, 50)
    ax.plot(xx, b0 + b1 * xx, color=ORANGE, linewidth=1.3)
    ax.scatter(x, y, s=10, color=BLUE, edgecolor="white", linewidth=0.5, zorder=3)
    ax.scatter([x.mean()], [y.mean()], s=18, marker="D", color=INK2, zorder=4, edgecolor="white", linewidth=0.6)
    ax.text(x.mean() + 0.25, y.mean() - 1.1, f"точка средних ({num(x.mean(), 1)}; {num(y.mean(), 1)})",
            fontsize=6.0, color=INK2, ha="left", va="top")
    ax.text(0.3, 12.4, f"ŷ = {num(b0, 2)} + {num(b1, 2)}·x;  R² = {num(r2)}", fontsize=6.4, color=INK)
    ax.text(0.3, 11.1, "серые отрезки — остатки eᵢ = yᵢ − ŷᵢ", fontsize=6.1, color=INK2)
    ax.set_xlim(0, 10); ax.set_ylim(0, 13.5)
    ax.set_xticks([0, 2, 4, 6, 8, 10]); ax.set_yticks([0, 4, 8, 12])
    clean(ax, y=True)
    ax.grid(axis="y")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    FACTS["reg"] = dict(b0=b0, b1=b1, r2=r2, xbar=x.mean(), ybar=y.mean())
    save(fig, "reg")


def fig_resid():
    r = np.random.default_rng(9)
    n = 120
    fig, axes = plt.subplots(1, 3, figsize=(WIDE, 40 * MM))
    fig.subplots_adjust(left=0.055, right=0.99, top=0.85, bottom=0.22, wspace=0.22)
    x = r.uniform(0, 10, n)
    cases = []
    y = 1 + 2 * x + r.normal(0, 1.5, n)
    cases.append(("предположения выполнены", x, y, 1))
    y = 1 + 0.4 * (x - 5) ** 2 + 2 * x + r.normal(0, 1.0, n)
    cases.append(("пропущена нелинейность", x, y, 1))
    y = 1 + 2 * x + r.normal(0, 0.15 + 0.35 * x, n)
    cases.append(("гетероскедастичность", x, y, 1))
    facts = {}
    for ax, (title, x, y, _) in zip(axes, cases):
        b1, b0 = np.polyfit(x, y, 1)
        fit = b0 + b1 * x
        res = y - fit
        ax.axhline(0, color=INK2, linewidth=0.7)
        ax.scatter(fit, res, s=5, color=BLUE, alpha=0.75, linewidth=0)
        ax.set_title(title, fontsize=6.6, pad=2)
        clean(ax, y=True)
        lim = np.abs(res).max() * 1.1
        ax.set_ylim(-lim, lim)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True, symmetric=True))
        ax.set_xlabel("прогноз ŷ")
        facts[title] = dict(b0=b0, b1=b1)
    axes[0].set_ylabel("остаток e")
    FACTS["resid"] = facts
    save(fig, "resid")


# ================================================================== 15. gradient descent: scaling matters
def fig_gd():
    r = np.random.default_rng(5)
    n = 100
    x = r.uniform(0, 4, n)
    y = 1 + 2 * x + r.normal(0, 1, n)

    def run(X, y, eta, steps, start):
        b = np.array(start, dtype=float)
        path = [b.copy()]
        for _ in range(steps):
            grad = -2 / len(y) * X.T @ (y - X @ b)
            b = b - eta * grad
            path.append(b.copy())
        return np.array(path)

    X1 = np.column_stack([np.ones(n), x])
    H1 = 2 / n * X1.T @ X1
    lam1 = np.linalg.eigvalsh(H1)
    eta1 = 0.9 * 2 / lam1.max()
    ols1 = np.linalg.lstsq(X1, y, rcond=None)[0]
    p1 = run(X1, y, eta1, 30, (-1.5, -0.5))
    xs = (x - x.mean()) / x.std()
    X2 = np.column_stack([np.ones(n), xs])
    H2 = 2 / n * X2.T @ X2
    lam2 = np.linalg.eigvalsh(H2)
    eta2 = 0.9 * 2 / lam2.max()
    ols2 = np.linalg.lstsq(X2, y, rcond=None)[0]
    p2 = run(X2, y, eta1, 30, (-1.5, -0.5))

    def mse(X, b0g, b1g):
        B = np.stack([b0g.ravel(), b1g.ravel()])
        R = y[:, None] - X @ B
        return (R ** 2).mean(0).reshape(b0g.shape)

    def steps_to(X, eta, start, ols, tol=0.01, cap=100000):
        b = np.array(start, dtype=float)
        for k in range(1, cap + 1):
            b = b - eta * (-2 / len(y) * X.T @ (y - X @ b))
            if np.linalg.norm(b - ols) < tol:
                return k
        return cap

    k1 = steps_to(X1, eta1, (-1.5, -0.5), ols1)
    k2 = steps_to(X2, eta1, (-1.5, -0.5), ols2)
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 62 * MM))
    fig.subplots_adjust(left=0.06, right=0.99, top=0.83, bottom=0.16, wspace=0.18)
    facts = {}
    for ax, X, ols, path, title, lam, k in ((axes[0], X1, ols1, p1, "Исходный x ∈ [0; 4]", lam1, k1),
                                             (axes[1], X2, ols2, p2, "Стандартизованный x", lam2, k2)):
        lo0, hi0 = min(path[:, 0].min(), ols[0]) - 1, max(path[:, 0].max(), ols[0]) + 1
        lo1, hi1 = min(path[:, 1].min(), ols[1]) - 1, max(path[:, 1].max(), ols[1]) + 1
        B0, B1 = np.meshgrid(np.linspace(lo0, hi0, 240), np.linspace(lo1, hi1, 240))
        Z = mse(X, B0, B1)
        zmin = Z.min()
        levels = zmin + (Z.max() - zmin) * np.array([0.004, 0.015, 0.04, 0.09, 0.17, 0.3, 0.5, 0.75])
        ax.contour(B0, B1, Z, levels=levels, colors=GRAY, linewidths=0.5)
        ax.plot(path[:, 0], path[:, 1], color=ORANGE, linewidth=0.9, marker="o", markersize=2.2,
                markerfacecolor=ORANGE, markeredgewidth=0)
        ax.scatter([path[0, 0]], [path[0, 1]], s=14, color=INK2, zorder=4)
        ax.scatter([ols[0]], [ols[1]], s=40, marker="*", color=BLUE, zorder=5, edgecolor="white", linewidth=0.4)
        word = "шаг" if k % 10 == 1 and k % 100 != 11 else ("шага" if 2 <= k % 10 <= 4 and not 12 <= k % 100 <= 14 else "шагов")
        ax.set_title(f"{title}: до минимума {k} {word}", fontsize=6.7, pad=3)
        ax.set_xlabel("β₀ — свободный член")
        clean(ax, y=True)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        dist_end = float(np.linalg.norm(path[-1] - ols))
        facts[title] = dict(ols=ols.tolist(), end30=path[-1].tolist(), dist_after_30=dist_end, steps_to_001=k,
                            cond=float(lam.max() / lam.min()), eta=float(eta1))
    axes[0].set_ylabel("β₁ — наклон")
    fig.legend(handles=[Line2D([], [], color="none", marker="o", markerfacecolor=INK2, markeredgewidth=0,
                               markersize=4, label="старт"),
                        Line2D([], [], color=ORANGE, lw=0.9, marker="o", markersize=2.2, markeredgewidth=0,
                               label="первые 30 шагов градиентного спуска"),
                        Line2D([], [], color="none", marker="*", markerfacecolor=BLUE, markeredgecolor="white",
                               markersize=7, label="минимум MSE (решение МНК)"),
                        Line2D([], [], color=GRAY, lw=0.5, label="линии уровня MSE")],
               loc="upper left", bbox_to_anchor=(0.06, 1.0), ncol=4, fontsize=6.0, handletextpad=0.4,
               columnspacing=1.4)
    FACTS["gd"] = facts
    save(fig, "gd")


# ================================================================== 16. logistic regression
def fig_logit():
    import statsmodels.api as sm
    r = np.random.default_rng(8)
    n = 90
    x = r.uniform(-4, 6, n)
    p = 1 / (1 + np.exp(-(-1 + 0.9 * x)))
    y = (r.random(n) < p).astype(int)
    m = sm.Logit(y, sm.add_constant(x)).fit(disp=0)
    b0, b1 = m.params
    fig, ax = plt.subplots(figsize=(COLW, 42 * MM))
    fig.subplots_adjust(left=0.1, right=0.97, top=0.96, bottom=0.2)
    jit = r.uniform(-0.035, 0.035, n)
    ax.scatter(x, y + jit, s=7, color=BLUE, alpha=0.6, linewidth=0)
    xx = np.linspace(-4, 6, 300)
    ax.plot(xx, 1 / (1 + np.exp(-(b0 + b1 * xx))), color=ORANGE, linewidth=1.4)
    ax.axhline(0.5, color=GRID, linewidth=0.7, zorder=0)
    x50 = -b0 / b1
    ax.plot([x50, x50], [0.5 - 0.04, 0.5 + 0.04], color=INK2, linewidth=0.7)
    ax.text(x50 + 0.2, 0.44, f"P = 0,5 при x = {num(x50, 1)}", fontsize=6.0, color=INK2, va="top")
    ax.text(2.4, 0.26, "кривая: P(y = 1 | x) = σ(β₀ + β₁x)", fontsize=6.1, color=INK2, va="center")
    ax.set_xlim(-4, 6); ax.set_ylim(-0.08, 1.08)
    ax.set_yticks([0, 0.5, 1])
    clean(ax, y=True)
    ax.set_xlabel("признак x"); ax.set_ylabel("y (0 или 1)")
    FACTS["logit"] = dict(b0=b0, b1=b1, or_=float(np.exp(b1)), x50=x50)
    save(fig, "logit")


# ================================================================== 17. time series + ACF
def fig_ts():
    r = np.random.default_rng(4)
    T = 84
    t = np.arange(T)
    week = np.array([0, -2, -1, 0, 3, 9, 7], dtype=float)
    y = 100 + 0.25 * t + week[t % 7] + r.normal(0, 2.2, T)
    fig = plt.figure(figsize=(COLW, 66 * MM))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1], hspace=0.75, left=0.1, right=0.97, top=0.9, bottom=0.12)
    ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1])
    ax.plot(t, y, color=BLUE, linewidth=0.9)
    trend = np.convolve(y, np.ones(7) / 7, mode="valid")
    ax.plot(t[3:-3], trend, color=ORANGE, linewidth=1.4)
    ax.set_xlim(0, T - 1)
    ax.set_xticks([0, 14, 28, 42, 56, 70, 84])
    ax.set_yticks([100, 110, 120, 130])
    clean(ax, y=True)
    ax.grid(axis="y")
    ax.set_title("Ряд: тренд + недельная сезонность + шум", fontsize=6.7, pad=12)
    ax.legend(handles=[Line2D([], [], color=BLUE, lw=0.9, label="наблюдения"),
                       Line2D([], [], color=ORANGE, lw=1.4, label="скользящее среднее за 7 дней")],
              loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, fontsize=6.0, handletextpad=0.5, columnspacing=1.2)
    ax.set_xlabel("день", labelpad=1)
    lags = np.arange(1, 29)
    yc = y - y.mean()
    acf = np.array([np.sum(yc[k:] * yc[:-k]) / np.sum(yc ** 2) for k in lags])
    band = 1.96 / np.sqrt(T)
    bx.fill_between([0.3, 28.7], -band, band, color=GRAY, alpha=0.18, linewidth=0)
    bx.vlines(lags, 0, acf, colors=[ORANGE if k % 7 == 0 else BLUE for k in lags], linewidth=1.3)
    bx.axhline(0, color=AXIS, linewidth=0.6)
    bx.set_xlim(0.3, 28.7); bx.set_ylim(-0.3, 1)
    bx.set_xticks([1, 7, 14, 21, 28]); bx.set_yticks([0, 0.5, 1])
    clean(bx, y=True)
    bx.spines["bottom"].set_visible(False)
    bx.set_title("ACF: пики на лагах 7, 14, 21, 28 (оранжевые)", fontsize=6.7, pad=3)
    bx.set_xlabel("лаг, дней", labelpad=1)
    FACTS["ts"] = dict(acf=dict(zip([int(v) for v in lags], [float(v) for v in acf])), band=band)
    save(fig, "ts")


# ================================================================== 18. Bayes
def fig_bayes():
    post = stats.beta(31, 171)
    xs = np.linspace(0, 0.4, 600)
    lo, hi = post.ppf([0.025, 0.975])
    fig, ax = plt.subplots(figsize=(COLW, 38 * MM))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.24)
    ys = post.pdf(xs)
    sel = (xs >= lo) & (xs <= hi)
    ax.fill_between(xs[sel], ys[sel], color=BLUE, alpha=0.2, linewidth=0)
    ax.plot(xs, ys, color=BLUE, linewidth=1.3)
    ax.plot(xs, np.ones_like(xs), color=GRAY, linewidth=1.1)
    ax.text(0.395, 1.6, "априорное Beta(1; 1)", fontsize=6.2, color=MUTED, ha="right")
    ax.text(0.21, 11.5, "апостериорное Beta(31; 171)", fontsize=6.2, color=INK, ha="left")
    ax.text(post.mean(), 4.0, "95%", fontsize=6.2, color=INK2, ha="center")
    ax.set_xlim(0, 0.4); ax.set_ylim(0, 16)
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
    clean(ax)
    ax.set_xlabel(f"конверсия θ; 95%-й байесовский интервал [{num(lo, 3)}; {num(hi, 3)}]")
    FACTS["bayes"] = dict(lo=lo, hi=hi, mean=post.mean())
    save(fig, "bayes")


# ================================================================== 19. bias-variance (schematic)
def fig_bv():
    c = np.linspace(1, 10, 300)
    test = 1.6 / c + 0.006 * c ** 2 + 0.25
    train = 1.6 / c * 0.9 + 0.25 * (1 - c / 11)
    k = int(np.argmin(test))
    fig, ax = plt.subplots(figsize=(COLW, 42 * MM))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.8, bottom=0.17)
    ax.plot(c, train, color=BLUE, linewidth=1.4)
    ax.plot(c, test, color=ORANGE, linewidth=1.4)
    ax.scatter([c[k]], [test[k]], s=16, color=ORANGE, edgecolor="white", linewidth=0.8, zorder=3)
    ax.text(c[k], test[k] + 0.13, "оптимальная сложность", fontsize=6.1, color=INK2, ha="center")
    ax.text(1.15, 0.06, "← недообучение: высокое смещение", fontsize=6.0, color=MUTED, ha="left")
    ax.text(9.95, 1.1, "переобучение: высокая дисперсия →", fontsize=6.0, color=MUTED, ha="right")
    ax.set_xlim(1, 10); ax.set_ylim(0, 1.95)
    clean(ax)
    ax.set_xticks([])
    ax.set_xlabel("сложность модели (схема)")
    ax.legend(handles=[Line2D([], [], color=BLUE, lw=1.4, label="ошибка на обучающей выборке"),
                       Line2D([], [], color=ORANGE, lw=1.4, label="ошибка на новых данных")],
              loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2, fontsize=6.1, handletextpad=0.5, columnspacing=1.4)
    save(fig, "bv")


# ================================================================== 20. ROC and PR curves
def fig_roc():
    from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score
    r = np.random.default_rng(17)
    n_pos, n_neg = 250, 4750
    y = np.r_[np.ones(n_pos), np.zeros(n_neg)]
    sA = np.r_[r.normal(2.4, 1, n_pos), r.normal(0, 1, n_neg)]
    sB = np.r_[r.normal(1.0, 1, n_pos), r.normal(0, 1, n_neg)]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 62 * MM))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.9, bottom=0.17, wspace=0.22)
    facts = {}
    for s, col, name in ((sA, BLUE, "модель A"), (sB, ORANGE, "модель B")):
        fpr, tpr, _ = roc_curve(y, s)
        auc = roc_auc_score(y, s)
        prec, rec, _ = precision_recall_curve(y, s)
        ap = average_precision_score(y, s)
        axes[0].plot(fpr, tpr, color=col, linewidth=1.3, label=f"{name}: ROC-AUC = {num(auc)}")
        axes[1].plot(rec, prec, color=col, linewidth=1.3, label=f"{name}: AP = {num(ap)}")
        facts[name] = dict(auc=auc, ap=ap)
    prev = n_pos / (n_pos + n_neg)
    axes[0].plot([0, 1], [0, 1], color=GRAY, linewidth=0.8, label="случайный классификатор: AUC = 0,5")
    axes[1].axhline(prev, color=GRAY, linewidth=0.8, label=f"случайный: AP ≈ {num(prev)}")
    axes[0].set_xlabel("FPR = FP / (FP + TN)"); axes[0].set_ylabel("TPR (recall) = TP / (TP + FN)")
    axes[1].set_xlabel("recall"); axes[1].set_ylabel("precision")
    axes[0].set_title("ROC-кривая", fontsize=6.8, pad=3)
    axes[1].set_title("PR-кривая", fontsize=6.8, pad=3)
    for ax in axes:
        ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
        clean(ax, y=True)
        ax.grid(True)
    axes[0].legend(loc="lower right", fontsize=6.1, handlelength=1.4)
    axes[1].legend(loc="center left", bbox_to_anchor=(0.14, 0.42), fontsize=6.1, handlelength=1.4)
    facts["prevalence"] = prev
    FACTS["roc"] = facts
    save(fig, "roc")


ALL = [fig_box, fig_variance, fig_corr, fig_heatmap, fig_dists, fig_lln, fig_clt, fig_lik, fig_ci, fig_pval,
       fig_power, fig_qq, fig_anova, fig_reg, fig_resid, fig_gd, fig_logit, fig_ts, fig_bayes, fig_bv, fig_roc]

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for f in ALL:
        if not only or f.__name__[4:] in only:
            f()
    old = json.loads((HERE / "facts.json").read_text()) if (HERE / "facts.json").exists() else {}

    def conv(o):
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple, np.ndarray)):
            return [conv(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        return o
    old.update(conv(FACTS))
    (HERE / "facts.json").write_text(json.dumps(old, ensure_ascii=False, indent=1))
    print("figures:", sorted(p.stem for p in OUT.glob("*.svg")))
