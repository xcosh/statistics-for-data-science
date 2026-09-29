# -*- coding: utf-8 -*-
import json, pathlib, subprocess, sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
OUT = HERE / "statistics_learning_roadmap_v8.pdf"

FOOTER = """
<div style="width:100%;font-family:'DejaVu Sans',sans-serif;font-size:7px;color:#9aa3ae;
 padding:0 14mm;display:flex;justify-content:space-between;">
 <span>Статистика для Data Science · дорожная карта · версия 8 · составитель — Claude (Anthropic) · CC BY 4.0</span>
 <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>"""

MARKERS = {"#plan": "В карточке — темы этапа", "#topics": "Их часто нет в базовых курсах",
           "#compare": "Темы плана сопоставлены", "#terms": "Словарь по этапам плана",
           "#sources": "Группы идут в порядке этапа 0", "#reading": "Научно-популярные книги — хороший вход"}


def build():
    subprocess.run([sys.executable, str(HERE / "build.py")], check=True)


def pdf():
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        pg.goto((HERE / "roadmap.html").as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        pg.emulate_media(media="print")
        pg.set_viewport_size({"width": 688, "height": 1000})
        ov = pg.evaluate("""() => { const d = document.documentElement; const bad = [];
            for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect();
              if (r.right > d.clientWidth + 1) bad.push(el.tagName + '.' + el.className + ' ' + Math.round(r.right)); }
            return [d.scrollWidth, d.clientWidth, bad.slice(0, 8)]; }""")
        print("overflow check:", ov)
        pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True,
               header_template="<div></div>", footer_template=FOOTER,
               margin=dict(top="13mm", bottom="15mm", left="14mm", right="14mm"))
        br.close()


def page_map():
    n = int(subprocess.run(["pdfinfo", str(OUT)], capture_output=True, text=True).stdout
            .split("Pages:")[1].split()[0])
    found = {"#how": "1"}
    for i in range(1, n + 1):
        txt = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), str(OUT), "-"],
                             capture_output=True, text=True).stdout
        txt = " ".join(txt.split())
        for k, m in MARKERS.items():
            if k not in found and m in txt:
                found[k] = str(i)
    return found, n


build(); pdf()
pages, n = page_map()
old = json.loads((HERE / "pages.json").read_text()) if (HERE / "pages.json").exists() else {}
if pages != old:
    (HERE / "pages.json").write_text(json.dumps(pages))
    build(); pdf()
    pages, n = page_map()
print("pages:", n, pages)
