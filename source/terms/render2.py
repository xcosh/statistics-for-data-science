# -*- coding: utf-8 -*-
import json, pathlib, subprocess, sys, warnings
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

warnings.filterwarnings("ignore")
HERE = pathlib.Path(__file__).parent
OUT = HERE / "statistics_terms_v2.pdf"

FOOTER = """
<div style="width:100%;font-family:'DejaVu Sans',sans-serif;font-size:7px;color:#9aa3ae;
 padding:0 14mm;display:flex;justify-content:space-between;">
 <span>Статистика для Data Science · основные термины · составитель — Claude (Anthropic) · CC BY 4.0 · xcosh.github.io/statistics-for-data-science</span>
 <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>"""


def build():
    r = subprocess.run([sys.executable, str(HERE / "build2.py")], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        print(r.stderr)
        sys.exit(1)


def pdf():
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        pg.goto((HERE / "terms.html").as_uri(), wait_until="load", timeout=120000)
        pg.evaluate("document.fonts.ready.then(() => 1)")
        pg.wait_for_timeout(500)
        pg.emulate_media(media="print")
        pg.set_viewport_size({"width": 688, "height": 1000})
        ov = pg.evaluate("""() => {
          const d = document.documentElement, W = d.clientWidth, bad = {};
          const clipped = el => { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
              const cs = getComputedStyle(a);
              if (cs.overflowX === 'hidden' || cs.overflowX === 'clip' || a.tagName.toLowerCase() === 'svg') return true; }
            return false; };
          for (const el of document.querySelectorAll('body *')) {
            if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
            const r = el.getBoundingClientRect();
            if (r.right > W + 1 && !clipped(el)) { const h = el.closest('[id]'); const k = h ? h.id : '?';
              bad[k] = Math.max(bad[k] || 0, Math.round(r.right)); } }
          return [d.scrollWidth, W, bad]; }""")
        print("overflow check:", ov)
        pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True,
               header_template="<div></div>", footer_template=FOOTER,
               margin=dict(top="13mm", bottom="15mm", left="14mm", right="14mm"))
        br.close()


def page_map():
    r = PdfReader(str(OUT))
    out = {}
    for name, dest in r.named_destinations.items():
        try:
            out[name.lstrip("/")] = str(r.get_destination_page_number(dest) + 1)
        except Exception:
            pass
    return out, len(r.pages)


build(); pdf()
pages, n = page_map()
for _ in range(3):
    old = json.loads((HERE / "pages.json").read_text()) if (HERE / "pages.json").exists() else {}
    if pages == old:
        break
    (HERE / "pages.json").write_text(json.dumps(pages, ensure_ascii=False))
    build(); pdf()
    pages, n = page_map()
print("pages:", n, {k: v for k, v in pages.items() if k.startswith("s-") or k == "index"})
