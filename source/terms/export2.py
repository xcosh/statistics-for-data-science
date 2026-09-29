# -*- coding: utf-8 -*-
"""terms.html (print layout, v2) -> one self-contained HTML for screens:
only the font faces the page really uses (Inter, PT Serif, JetBrains Mono, KaTeX), subset to the page's characters
and embedded as data URIs; responsive screen layout; sticky search over term titles and full text."""
import base64, html as _html, io, pathlib, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
SRC = HERE / "terms.html"
OUT = HERE / "statistics_terms_v2.html"
KATEX_CSS = HERE / "node_modules/katex/dist/katex.min.css"

html = SRC.read_text(encoding="utf-8")

# ------------------------------------------------------------------ which faces does the page really load?
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(SRC.as_uri(), wait_until="load", timeout=120000)
    pg.evaluate("document.fonts.ready.then(() => 1)")
    pg.wait_for_timeout(800)
    loaded = pg.evaluate("""() => [...document.fonts].filter(f => f.status === 'loaded')
        .map(f => [f.family.replace(/["']/g, ''), String(f.weight), f.style])""")
    br.close()
LOADED = {(f, w, s) for f, w, s in loaded}
print("loaded faces:", sorted({(f, w, s) for f, w, s in LOADED}))

# ------------------------------------------------------------------ screen-only restructuring
# 1) search bar: out of the header, so that it stays sticky over the whole page
m = re.search(r'\s*<div class="search" role="search">.*?</div>', html, flags=re.S)
assert m, "search block not found"
search_block = m.group(0).strip()
html = html.replace(m.group(0), "", 1)
html = html.replace("</header>", "</header>\n" + search_block, 1)

# 2) wide and mini tables scroll horizontally on phones
n_dt = len(re.findall(r'<table class="dt">', html))
html = re.sub(r'(<table class="dt">.*?</table>)', r'<div class="dtw">\1</div>', html, flags=re.S)
n_mini = len(re.findall(r'<table class="mini', html))
html = re.sub(r'(<table class="mini[^"]*">.*?</table>)', r'<div class="dtw">\1</div>', html, flags=re.S)


# 3) search keys for the stand-alone tables (dists, choose)
def plain(s):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def add_key(mt):
    block = mt.group(0)
    title = re.search(r"<h3>(.*?)<span", block, flags=re.S)
    firsts = re.findall(r"<tr><td>(.*?)</td>", block, flags=re.S)
    key = " ".join([plain(title.group(1)) if title else ""] + [plain(c) for c in firsts])
    return block.replace('<div class="twide"', f'<div class="twide" data-k="{_html.escape(key, quote=True)}"', 1)


html = re.sub(r'<div class="twide" id="tab-(?:dists|choose)">.*?</table>', add_key, html, flags=re.S)
assert html.count('class="twide" data-k=') == 2

# 4) wording that refers to the printed pages
html, n_sub = re.subn(r"В\s+конце\s+—\s+указатель\s+русских\s+и\s+английских\s+терминов\s+со\s+страницами\.",
                     "В\u00a0конце\u00a0— указатель русских и английских терминов, а над разделами — строка поиска "
                     "(клавиша «/»).", html)
assert n_sub == 1, n_sub

SCREEN_CSS = """
@media screen{
  html{background:#e9ecf0;scroll-padding-top:15mm;}
  body{max-width:210mm;margin:8mm auto;padding:12mm 14mm 18mm;background:#fff;border-radius:2mm;zoom:1.2;
    box-shadow:0 1px 3px rgba(20,30,45,.10),0 10px 30px rgba(20,30,45,.08);}
  a:hover{text-decoration:underline;}
  .ti .tp,.ie .pg,.index .stage{display:none;}
  .ti .tt::after{content:none;}
  .search{display:flex;align-items:center;gap:3mm;position:sticky;top:0;z-index:5;margin:4mm -14mm 0;
    padding:2.2mm 14mm;background:rgba(255,255,255,.96);border-bottom:.25mm solid var(--rule);
    -webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);}
  .search input{flex:1;min-width:0;font:inherit;font-size:8.6pt;padding:1.6mm 2.6mm;border:.3mm solid #c9d0d8;
    border-radius:1.6mm;background:#fff;color:var(--ink);outline:none;}
  .search input:focus{border-color:var(--c2);box-shadow:0 0 0 .6mm var(--c2bg);}
  #qcount{flex:none;font-size:7.4pt;color:var(--muted);min-width:26mm;text-align:right;}
  body.filtering .front,body.filtering .notation,body.filtering .toc,body.filtering .index{display:none;}
  body.filtering .sec{margin-top:5mm;}
  main>.sec:first-child{margin-top:6mm;}
  .index{margin-top:10mm;}
  article.t:target,.twide:target,figure.fig:target{animation:flash 2.4s ease-out;}
  @keyframes flash{0%{background:#fff5cc;}100%{background:transparent;}}
  .dtw{overflow-x:auto;-webkit-overflow-scrolling:touch;}
  .fig>svg{max-width:100%;}
  .fm{overflow-x:auto;overflow-y:hidden;padding:.5mm 0;}
  .nw .katex{white-space:normal;}
}
@media screen and (max-width:999px){
  html{background:#fff;}
  body{zoom:1;margin:0 auto;border-radius:0;box-shadow:none;}
}
@media screen and (max-width:760px){
  html{background:#fff;scroll-padding-top:62px;}
  body{margin:0;padding:12px 14px 24px;max-width:none;border-radius:0;box-shadow:none;zoom:1.15;}
  .search{margin:3mm -14px 0;padding:8px 14px;}
  #qcount{min-width:0;}
  #qcount:empty{display:none;}
  h1{font-size:18pt;}
  .front{grid-template-columns:minmax(0,1fr);gap:3mm;}
  .notation{grid-template-columns:minmax(0,1fr);}
  .toc{grid-template-columns:minmax(0,1fr);}
  .sh{flex-wrap:wrap;row-gap:1mm;}
  .sh h2{font-size:13pt;}
  .sh .stage{margin-left:0;}
  .r{display:block;padding:1.6mm 0;}
  .rl{margin-bottom:.9mm;}
  .fig.col{display:block;margin-left:0;}
  .fig.col>svg{width:100%;}
  .fig.col figcaption{margin-top:1.2mm;}
  .fig.wide,.fig.full{margin-left:0;overflow-x:auto;-webkit-overflow-scrolling:touch;}
  .fig.wide>svg{max-width:none;width:151mm;}
  .fig.full>svg{max-width:none;width:182mm;}
  .fig.wide figcaption,.fig.full figcaption{margin-left:0;position:sticky;left:0;}
  .dt{min-width:640px;}
  .mini{min-width:430px;}
  .ixw{grid-template-columns:minmax(0,1fr);gap:5mm;}
  .twide h3{display:block;} .twide h3 .h3n{display:block;margin-top:.6mm;}
}
@media screen and (max-width:430px){ .ix{columns:1;} }
"""

SEARCH_JS = r"""
<script>
(() => {
  const q = document.getElementById('q'), cnt = document.getElementById('qcount');
  if (!q) return;
  const norm = s => s.toLowerCase().replace(/ё/g, 'е').replace(/[   ]/g, ' ').replace(/\s+/g, ' ');
  const items = [...document.querySelectorAll('article.t, section.sec > .twide')];
  const figs = [...document.querySelectorAll('figure.fig')];
  const secs = [...document.querySelectorAll('section.sec')];
  const txt = new Map(items.map(el => [el, norm(el.textContent)]));
  const key = new Map(items.map(el => [el, norm(el.dataset.k || '')]));
  function run() {
    const words = norm(q.value).trim().split(' ').filter(Boolean);
    if (!words.length) {
      [...items, ...figs, ...secs].forEach(el => { el.hidden = false; });
      document.body.classList.remove('filtering');
      cnt.textContent = '';
      return;
    }
    document.body.classList.add('filtering');
    const inTitle = items.filter(el => words.every(w => key.get(el).includes(w)));
    const hits = new Set(inTitle.length ? inTitle : items.filter(el => words.every(w => txt.get(el).includes(w))));
    let n = 0;
    for (const el of items) { el.hidden = !hits.has(el); if (hits.has(el)) n++; }
    for (const f of figs) {
      const owner = f.dataset.for ? document.getElementById(f.dataset.for) : null;
      f.hidden = owner ? owner.hidden : true;
    }
    for (const s of secs) s.hidden = !s.querySelector(':scope > article.t:not([hidden]), :scope > .twide:not([hidden])');
    cnt.textContent = !hits.size ? 'ничего не найдено' : (inTitle.length ? 'найдено: ' + n : 'в тексте статей: ' + n);
  }
  q.addEventListener('input', run);
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
    else if (e.key === 'Escape' && document.activeElement === q) { q.value = ''; run(); }
  });
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]');
    if (a && q.value) { q.value = ''; run(); }
  });
})();
</script>
"""
GH_JS = (HERE.parent / "gh_link.js").read_text(encoding="utf-8")
html = html.replace("</body></html>", SEARCH_JS + GH_JS + "</body></html>", 1)

# ------------------------------------------------------------------ fonts
used = {ord(c) for c in html} | {0x20, 0xA0}


def parse_ranges(spec):
    out = []
    for part in spec.split(","):
        part = part.strip().upper().replace("U+", "")
        if "-" in part:
            a, b = part.split("-")
            out.append((int(a, 16), int(b, 16)))
        elif part:
            out.append((int(part, 16), int(part, 16)))
    return out


def subset_woff2(path, codepoints):
    font = TTFont(str(path))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=codepoints)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return buf.getvalue()


def uri(data):
    return "data:font/woff2;base64," + base64.b64encode(data).decode()


faces, total = [], 0
for css_rel in re.findall(r'<link rel="stylesheet" href="(node_modules/@fontsource/[^"]+\.css)">', html):
    css_path = (HERE / css_rel).resolve()
    for block in re.findall(r"@font-face\s*\{[^}]*\}", css_path.read_text()):
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        if (fam, weight, style) not in LOADED:
            continue
        rng = re.search(r"unicode-range:\s*([^;]+);", block).group(1)
        cps = {c for c in used for a, b in parse_ranges(rng) if a <= c <= b}
        if not cps:
            continue
        woff2 = re.search(r"url\((\./files/[^)]+\.woff2)\)", block).group(1)
        data = subset_woff2(css_path.parent / woff2, cps)
        total += len(data)
        faces.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};font-display:swap;"
                     f"src:url({uri(data)}) format('woff2');unicode-range:{rng};}}")

katex_css = KATEX_CSS.read_text(encoding="utf-8")
k_kept = k_dropped = 0


def katex_face(mt):
    global total, k_kept, k_dropped
    block = mt.group(0)
    fam = re.search(r"font-family:([^;]+);", block).group(1).strip("'\" ")
    style = re.search(r"font-style:(\w+)", block).group(1)
    weight = re.search(r"font-weight:(\d+)", block).group(1)
    if (fam, weight, style) not in LOADED:
        k_dropped += 1
        return ""
    woff2 = re.search(r"url\((fonts/[^)]+\.woff2)\)", block).group(1)
    data = subset_woff2(KATEX_CSS.parent / woff2, used)
    total += len(data)
    k_kept += 1
    return re.sub(r"src:[^}]+", f"src:url({uri(data)}) format(\"woff2\")", block)


katex_css = re.sub(r"@font-face\{[^}]*\}", katex_face, katex_css)
assert "url(fonts/" not in katex_css

html = re.sub(r'<link rel="stylesheet" href="node_modules/@fontsource/[^"]+\.css">\n?', "", html)
html = html.replace('<link rel="stylesheet" href="node_modules/katex/dist/katex.min.css">',
                    "<style>" + katex_css + "</style>", 1)
assert "node_modules" not in html
html = html.replace("<style>", "<style>\n" + "\n".join(faces) + "\n", 1)
# screen CSS goes after the print CSS (the last <style> block of the head)
head_end = html.index("</head>")
last_style = html.rindex("</style>", 0, head_end)
html = html[:last_style] + SCREEN_CSS + html[last_style:]
sys.path.insert(0, str(HERE.parent))
from site_nav import add_sitebar
html = add_sitebar(html, "terms")
OUT.write_text(html, encoding="utf-8")
print(f"tables wrapped: dt {n_dt}, mini {n_mini} | faces: {len(faces)} fontsource + {k_kept} KaTeX "
      f"({k_dropped} KaTeX dropped) | fonts {total/1024:.0f} KB | html {OUT.stat().st_size/1024:.0f} KB")
