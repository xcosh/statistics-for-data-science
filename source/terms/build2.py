# -*- coding: utf-8 -*-
"""Builds terms.html (print layout, v2): KaTeX formulas, single-column term cards, figures, tables, index."""
import html as _html, json, pathlib, re, subprocess, sys
from content2 import SECTIONS, TABLES, FIGS, NOTATION, STAGE

HERE = pathlib.Path(__file__).parent
VERSION = "2"

# ------------------------------------------------------------------ math registry
MATH = {}          # key -> (tex, display)
_counter = [0]


def _reg(tex, display):
    _counter[0] += 1
    k = f"m{_counter[0]}"
    MATH[k] = (tex, display)
    return f"\x01{k}\x02"


def inline(text):
    """$...$ -> placeholder tokens (inline math)."""
    if not text:
        return text
    parts = re.split(r"(\$[^$]+\$)", text)
    out = []
    for p in parts:
        if len(p) > 1 and p.startswith("$") and p.endswith("$"):
            out.append(_reg(p[1:-1], False))
        else:
            if "$" in p:
                raise ValueError(f"unbalanced $ in: {text[:120]}")
            out.append(p)
    return "".join(out)


def display(tex):
    return _reg(tex, True)


def split_top(tex, seps=(r"\qquad", r"\quad")):
    """Split a display formula at top-level \\qquad / \\quad (outside braces and \\left...\\right)."""
    parts, depth, lr, cur, i = [], 0, 0, "", 0
    while i < len(tex):
        if tex[i] == "\\":
            cmd = re.match(r"\\([A-Za-z]+|.)", tex[i:]).group(0)
            lr += (cmd == r"\left") - (cmd == r"\right")
            if depth == 0 and lr == 0 and cmd in seps:
                parts.append((cur.strip(), cmd))
                cur = ""
            else:
                cur += cmd
            i += len(cmd)
            continue
        depth += (tex[i] == "{") - (tex[i] == "}")
        cur += tex[i]
        i += 1
    parts.append((cur.strip(), ""))
    # a connector such as \\text{т. е.} stays with the next part
    out, carry = [], ""
    for k, (s, sep) in enumerate(parts):
        if re.fullmatch(r"\\text\{[^{}]*\}", s) and k < len(parts) - 1:
            carry += f"{s} {sep} "
            continue
        out.append((carry + s, sep))
        carry = ""
    return out


def display_flow(tex):
    """Display formula as a row of display-style pieces that can wrap on narrow screens; each piece keeps its
    trailing \\qquad / \\quad, so the printed spacing is the same as in a single display formula."""
    DS = "\\displaystyle "
    out = []
    for s, sep in split_top(tex):
        token = _reg(DS + s + (" " + sep if sep else ""), False)
        out.append('<span class="fp">' + token + "</span>")
    return "".join(out)


# ------------------------------------------------------------------ validation
ENTRIES = {}
for sec in SECTIONS:
    for e in sec["items"]:
        assert e["id"] not in ENTRIES, f"duplicate id {e['id']}"
        e["sec"] = sec
        ENTRIES[e["id"]] = e
for e in ENTRIES.values():
    for t in e.get("see", []):
        assert t in ENTRIES, f"{e['id']} -> unknown see {t}"
    if e.get("fig"):
        assert e["fig"] in FIGS and (HERE / "fig" / f"{e['fig']}.svg").exists(), e["fig"]
    if e.get("table"):
        assert e["table"] in TABLES, e["table"]
    assert "idx" in e, f"no idx for {e['id']}"
    for fld in ("d", "n", "u", "x", "w"):
        v = e.get(fld, "")
        for ref in re.findall(r"\{(fig|tab):([a-z_0-9]+)\}", v):
            assert (ref[0] == "fig" and ref[1] in FIGS) or (ref[0] == "tab" and ref[1] in TABLES), (e["id"], ref)

# figure numbering in order of appearance
FIGNUM = {}
for sec in SECTIONS:
    for e in sec["items"]:
        if e.get("fig"):
            FIGNUM[e["fig"]] = len(FIGNUM) + 1
        for blk in sec.get("after", {}).get(e["id"], []):
            kind, key = blk.split(":")
            if kind == "fig":
                FIGNUM[key] = len(FIGNUM) + 1
assert set(FIGNUM) == set(FIGS), set(FIGS) ^ set(FIGNUM)

TAB_TITLES = {"choose": "таблица «Какой критерий выбрать»", "dists": "таблица «Основные распределения»",
              "scales": "таблица шкал измерения"}


def refs(s):
    s = re.sub(r"\{fig:([a-z0-9_]+)\}", lambda m: f'<a class="fr" href="#fig-{m.group(1)}">рис.&nbsp;{FIGNUM[m.group(1)]}</a>', s)
    s = re.sub(r"\{tab:([a-z0-9_]+)\}", lambda m: f'<a class="fr" href="#tab-{m.group(1)}">{TAB_TITLES[m.group(1)]}</a>', s)
    return s


def txt(s):
    return inline(refs(s)) if s else s


PAGES = {}
try:
    PAGES = json.loads((HERE / "pages.json").read_text())
except Exception:
    pass


# ------------------------------------------------------------------ blocks
def figure_html(key, owner):
    kind, cap = FIGS[key]
    svg = (HERE / "fig" / f"{key}.svg").read_text(encoding="utf-8")
    return (f'<figure class="fig {kind}" id="fig-{key}" data-for="{owner}">{svg}'
            f'<figcaption id="{key}-cap"><b>Рис. {FIGNUM[key]}.</b> {txt(cap)}</figcaption></figure>')


def table_html(key, in_row=False):
    t = TABLES[key]
    head = "".join(f"<th>{txt(h)}</th>" for h in t["head"])
    body = "".join("<tr>" + "".join(f"<td>{txt(c)}</td>" for c in row) + "</tr>" for row in t["rows"])
    note = f'<div class="tnote">{txt(t["note"])}</div>' if t.get("note") else ""
    if t["kind"] == "mini":
        return (f'<table class="mini{" in-row" if in_row else ""}"><thead><tr>{head}</tr></thead>'
                f'<tbody>{body}</tbody></table>{note}')
    cols = "".join(f'<col style="width:{w}%">' for w in t["widths"])
    title = ""
    if t.get("title"):
        sub = f' <span class="h3n">{txt(t["sub"])}</span>' if t.get("sub") else ""
        title = f"<h3>{t['title']}{sub}</h3>"
    return (f'<div class="twide" id="tab-{key}">{title}<table class="dt"><colgroup>{cols}</colgroup>'
            f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>{note}</div>')


def row(cls, label, content):
    return f'<div class="r {cls}"><div class="rl">{label}</div><div class="rc">{content}</div></div>'


def code_html(lines):
    if isinstance(lines, str):
        lines = [lines]
    return '<pre class="code">' + _html.escape("\n".join(lines), quote=False) + "</pre>"


def see_html(e):
    parts = [f'<a href="#t-{t}">{ENTRIES[t]["s"]}</a>' for t in e.get("see", [])]
    vids = [f'<a class="vid" href="{u}">▶&#xFE0E;&nbsp;{lab}</a>' for lab, u in e.get("vid", [])]
    return ' <span class="sep">·</span> '.join(parts + vids)


def entry_html(e):
    keys = " ".join([e["ru"], re.sub(r"\$[^$]*\$", " ", e["en"])] + e["idx"][0] + e["idx"][1])
    keys = _html.escape(re.sub(r"<[^>]+>", "", keys), quote=True)
    out = [f'<article class="t" id="t-{e["id"]}" data-k="{keys}">',
           f'<div class="th"><h3 class="tr">{e["ru"]}</h3><span class="te">{txt(e["en"])}</span></div>',
           row("r-d", "Определение", txt(e["d"]))]
    tpos = e.get("table_pos", "d")

    def put_table():
        t = TABLES[e["table"]]
        if t["kind"] == "wide":
            out.append(table_html(e["table"]))
        else:
            out.append(row("r-t", "Схема" if e["table"] in ("errors", "confusion") else "Таблица",
                           table_html(e["table"], in_row=True)))

    if e.get("table") and tpos == "d":
        put_table()
    if e.get("f"):
        fm = "".join(f'<div class="fm">{display_flow(f)}</div>' for f in e["f"])
        plural = len(e["f"]) > 1 or re.search(r"\\q?quad|,\s", e["f"][0])
        out.append(row("r-f", "Формулы" if plural else "Формула", fm))
    if e.get("table") and tpos == "f":
        put_table()
    if e.get("n"):
        out.append(row("r-n", "Пояснение", txt(e["n"])))
    if e.get("u"):
        out.append(row("r-u", "Применение", txt(e["u"])))
    if e.get("x"):
        out.append(row("r-x", "Пример", txt(e["x"])))
    if e.get("w"):
        out.append(row("r-w", "Ловушка", txt(e["w"])))
    if e.get("py"):
        out.append(row("r-py", "Python", code_html(e["py"])))
    s = see_html(e)
    if s:
        out.append(row("r-see", "Связи", s))
    out.append("</article>")
    html = "".join(out)
    if e.get("fig"):
        html += figure_html(e["fig"], "t-" + e["id"])
    return html


def section_html(sec):
    body = []
    for e in sec["items"]:
        body.append(entry_html(e))
        for blk in sec.get("after", {}).get(e["id"], []):
            kind, key = blk.split(":")
            body.append(table_html(key) if kind == "tab" else figure_html(key, "tab-dists" if key == "dists" else ""))
    return (f'<section class="sec {sec["block"]}" id="s-{sec["key"]}">'
            f'<div class="sh"><span class="sn">{sec["num"]}</span><h2>{sec["title"]}</h2>'
            f'<span class="stage">{STAGE[sec["num"]]} дорожной карты</span></div>'
            f'<p class="lead">{txt(sec["lead"])}</p>{"".join(body)}</section>')


# ------------------------------------------------------------------ index
def plain(s):
    return re.sub(r"<[^>]+>", "", s)


def ru_key(s):
    return plain(s).lower().replace("ё", "е").lstrip("«(\"'")


def is_cyr(s):
    c = ru_key(s)[:1]
    return "а" <= c <= "я"


def en_key(s):
    return re.sub(r"^[^a-z0-9]+", "", plain(s).lower())


RU_IDX = [(t, eid) for eid, e in ENTRIES.items() for t in e["idx"][0]]
EN_IDX = [(t, eid) for eid, e in ENTRIES.items() for t in e["idx"][1]]


def index_block(items, lang):
    merged = {}
    for t, eid in items:
        merged.setdefault(t, [])
        if eid not in merged[t]:
            merged[t].append(eid)
    items = list(merged.items())
    groups, cur = [], None
    if lang == "ru":
        cyr = sorted([i for i in items if is_cyr(i[0])], key=lambda i: ru_key(i[0]))
        lat = sorted([i for i in items if not is_cyr(i[0])], key=lambda i: en_key(i[0]))
        for t, eids in cyr:
            L = ru_key(t)[0].upper()
            if L != cur:
                groups.append((L, [])); cur = L
            groups[-1][1].append((t, eids))
        if lat:
            groups.append(("A–Z", lat))
    else:
        for t, eids in sorted(items, key=lambda i: en_key(i[0])):
            L = en_key(t)[:1].upper()
            if L != cur:
                groups.append((L, [])); cur = L
            groups[-1][1].append((t, eids))
    out = []
    for L, lst in groups:
        out.append(f'<div class="letter">{L}</div>')
        for t, eids in lst:
            pages = ", ".join(dict.fromkeys(PAGES.get("t-" + e, "") for e in eids if PAGES.get("t-" + e)))
            out.append(f'<div class="ie"><a href="#t-{eids[0]}">{t}</a><span class="pg">{pages}</span></div>')
    return "".join(out)


RU_N = len({t for t, _ in RU_IDX})
EN_N = len({t for t, _ in EN_IDX})


index_html = (f'<section class="index" id="index"><div class="sh"><span class="sn">≡</span><h2>Указатель терминов</h2>'
              f'<span class="stage">{RU_N} русских и {EN_N} английских названий · номер — страница</span></div>'
              f'<div class="ixw"><div><h3>По-русски</h3><div class="ix">{index_block(RU_IDX, "ru")}</div></div>'
              f'<div><h3>In English</h3><div class="ix">{index_block(EN_IDX, "en")}</div></div></div></section>')

# ------------------------------------------------------------------ front matter
toc_items = [(f"#s-{s['key']}", s["num"], s.get("toc", s["title"]), s["block"]) for s in SECTIONS] + \
            [("#index", "≡", "Указатель терминов", "")]
toc_html = "".join(f'<a class="ti {bc}" href="{h}"><span class="tn">{n}</span><span class="tt">{t}</span>'
                   f'<span class="tp">{PAGES.get(h[1:], "")}</span></a>' for h, n, t, bc in toc_items)
notation_html = ('<div class="notation"><h4>Обозначения</h4>' +
                 "".join(f'<div class="nt"><span class="s">{txt(a)}</span><span>{txt(b)}</span></div>'
                         for a, b in NOTATION) + "</div>")
N_TERMS = len(ENTRIES)
FRONT = f"""
<div class="front">
  <div class="box">
    <h4>Как устроена статья</h4>
    <div class="anat">
      <span class="l">Заголовок</span><span>термин по-русски; справа — английское название и обозначение</span>
      <span class="l def">Определение</span><span>точная формулировка в стиле учебника — главное в статье</span>
      <span class="l">Формулы</span><span>определяющие и расчётные формулы</span>
      <span class="l">Пояснение</span><span>как понимать, свойства, связь с другими понятиями</span>
      <span class="l">Применение</span><span>когда и для чего использовать</span>
      <span class="l">Пример</span><span>короткий расчёт; все числа проверены кодом</span>
      <span class="l">Ловушка</span><span>частая ошибка или путаница в терминах</span>
      <span class="l">Python</span><span>функции для расчёта</span>
      <span class="l">Связи</span><span>связанные статьи и ▶&#xFE0E; видео — ссылки кликабельны</span>
    </div>
  </div>
  <div class="box">
    <h4>Как пользоваться</h4>
    <p>Разделы идут в порядке дорожной карты: номер раздела совпадает с номером этапа, а материалы для подробного
      изучения собраны в карточках этапов карты.</p>
    <p>Для первого знакомства хватит определения, пояснения и примера; формулы, ловушки и код пригодятся при решении
      задач и в работе. В конце — указатель русских и английских терминов со страницами.</p>
    <p>Сокращения в коде: <code>np</code> — NumPy, <code>pd</code> — pandas, <code>stats</code> — scipy.stats,
      <code>optimize</code> — scipy.optimize, <code>sm</code>/<code>smf</code> — statsmodels.api/formula.api;
      функции sklearn и statsmodels — из их модулей (указаны в комментариях).</p>
  </div>
</div>"""

COLOPHON = """
<div class="colophon">
  <h4>О справочнике</h4>
  <p><b>Составитель — Claude (Anthropic).</b> Справочник подготовлен искусственным интеллектом: числа в примерах
    пересчитаны кодом, фрагменты Python запускаются, текст дважды проверен отдельными проверочными прогонами ИИ.
    Экспертом-человеком он не рецензировался, поэтому неточности возможны: если найдёте ошибку, сообщите о ней
    <a class="gh" data-gh="issues" href="https://github.com/xcosh/statistics-for-data-science/issues">в разделе Issues репозитория проекта на GitHub</a>. Актуальные
    версии справочника и дорожная карта к нему — на сайте <a class="url" href="https://xcosh.github.io/statistics-for-data-science/">xcosh.github.io/statistics-for-data-science</a>.</p>
  <p><b>Лицензия CC BY 4.0:</b> справочник можно копировать, распространять и переделывать, в том числе
    для коммерческого использования, указав источник.</p>
</div>"""

CSS = (HERE / "terms2.css").read_text()
FONT_LINKS = "\n".join(f'<link rel="stylesheet" href="node_modules/@fontsource/{f}.css">' for f in (
    "inter/400", "inter/500", "inter/600", "inter/700", "inter/400-italic",
    "pt-serif/400", "pt-serif/700", "pt-serif/400-italic", "jetbrains-mono/400"))

body_sections = "".join(section_html(s) for s in SECTIONS)
HTML = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Статистика для Data Science — основные термины</title>
{FONT_LINKS}
<link rel="stylesheet" href="node_modules/katex/dist/katex.min.css">
<style>{CSS}</style></head>
<body>
<header class="top" id="top">
  <div class="kicker">Справочник к дорожной карте · версия {VERSION} · сентябрь 2026 · составитель — Claude (Anthropic)</div>
  <h1>Статистика для Data Science: основные термины</h1>
  <div class="sub">{N_TERMS} ключевых понятий — точные определения, формулы, пояснения, примеры, код и графики: от типов данных до метрик ML</div>
  {FRONT}
  {notation_html}
  <nav class="toc">{toc_html}</nav>
  {COLOPHON}
  <div class="search" role="search"><input id="q" type="search" autocomplete="off" spellcheck="false"
    placeholder="Поиск: p-value, дисперсия, bootstrap…" aria-label="Поиск по терминам"><span id="qcount" aria-live="polite"></span></div>
</header>
<main>
{body_sections}
{index_html}
</main>
</body></html>
"""

# ------------------------------------------------------------------ typography (text nodes outside svg/style/pre/code)
NOWRAP = re.compile(r"(?<![\w/-])((?:A/B|ML|KL|AI|[A-Za-z])-[0-9A-Za-zА-Яа-яЁё]+|\d+-[а-яё]+)")


def typo_text(t):
    t = re.sub(r"(^|[\s(>])\+ (?=\w)", "\\1+\u00a0", t)
    t = re.sub(r"(?<![\w])(гл|нед|ч|изд|т|с|п|руб|тыс|мин|мс)\. ", "\\1.\u00a0", t)
    t = t.replace("≈ ", "≈\u00a0").replace(" —", "\u00a0—")
    t = re.sub(r"(\d) (нед|тыс|мс|мин|минут|задач|пар|п\.|раз|млн|%)", "\\1\u00a0\\2", t)
    t = re.sub(r"(\d) (\d{3})(?!\d)", "\\1\u00a0\\2", t)
    t = re.sub(r"(?<=\s)([вксуоиаВКСУОИА]) ", "\\1\u00a0", t)
    t = NOWRAP.sub(r'<span class="nw">\1</span>', t)
    return t


parts = re.split(r"(<svg.*?</svg>|<style>.*?</style>|<pre class=\"code\">.*?</pre>|<code>.*?</code>|<[^>]+>)",
                 HTML, flags=re.S)
for i, p in enumerate(parts):
    if not p or p.startswith("<"):
        continue
    parts[i] = typo_text(p)
HTML = "".join(parts)
# keep punctuation and brackets attached to inline formulas
HTML = re.sub(r"([(«\[]*)(\x01m\d+\x02)([,.;:!?)»\]]+)", r'<span class="nw">\1\2\3</span>', HTML)
HTML = re.sub(r"([(«]+)(\x01m\d+\x02)(?![,.;:!?)»\]])", r'<span class="nw">\1\2</span>', HTML)

# ------------------------------------------------------------------ render math with KaTeX
(HERE / "formulas.json").write_text(json.dumps({k: {"tex": t, "display": d} for k, (t, d) in MATH.items()},
                                               ensure_ascii=False))
r = subprocess.run(["node", str(HERE / "katex_render.js")], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout, r.stderr)
    sys.exit(1)
RENDERED = json.loads((HERE / "formulas_html.json").read_text())
HTML = re.sub(r"\x01(m\d+)\x02", lambda m: RENDERED[m.group(1)], HTML)
assert "\x01" not in HTML and "\x02" not in HTML

(HERE / "terms.html").write_text(HTML, encoding="utf-8")
print(f"terms.html: {len(HTML)//1024} KB | entries {N_TERMS} | figures {len(FIGNUM)} | formulas {len(MATH)} | "
      f"index ru {len(RU_IDX)} en {len(EN_IDX)}")
