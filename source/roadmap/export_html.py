# -*- coding: utf-8 -*-
"""Turns roadmap.html (built for print) into one self-contained HTML file:
fonts subset to the characters in use and embedded as data URIs, plus screen styles."""
import base64, sys, io, pathlib, re
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = pathlib.Path(__file__).parent
SRC = HERE / "roadmap.html"
OUT = HERE / "statistics_learning_roadmap_v8.html"

html = SRC.read_text(encoding="utf-8")
used = {ord(c) for c in html} | {0x20, 0xA0}

SCREEN_CSS = """
@page{size:A4;margin:13mm 14mm 15mm;}
@media screen{
  html{background:#e9ecf0;}
  body{max-width:210mm;margin:10mm auto;padding:13mm 14mm 16mm;background:#fff;border-radius:2mm;
    box-shadow:0 1px 3px rgba(20,30,45,.10),0 10px 30px rgba(20,30,45,.08);}
  section{scroll-margin-top:8mm;}
  section.pb{break-before:auto;}
  section#plan,section#topics,section#compare,section#terms,section#sources,section#reading{
    margin-top:9mm;padding-top:1mm;border-top:.35mm solid var(--rule);}
  section#plan h2,section#topics h2,section#compare h2,section#terms h2,section#sources h2,section#reading h2{margin-top:4mm;}
  .tp{display:none;}
  .tt::after{content:none;}
  a:hover{text-decoration:underline;}
  .ti:hover .tt{text-decoration:underline;}
}
@media screen and (min-width:1000px){ body{zoom:1.22;} }
@media screen and (max-width:760px){
  html{background:#fff;}
  body{margin:0;padding:16px;max-width:none;border-radius:0;box-shadow:none;}
  h1{font-size:21pt;}
  .toc{grid-template-columns:1fr;}
  .cycle{flex-wrap:wrap;gap:1.4mm;} .step{flex:1 1 40%;} .carr{display:none;}
  .es{white-space:normal;}
  .maprow{grid-template-columns:1fr;gap:1mm;}
  .flow{flex-direction:column;} .flow .arr{display:none;}
  .flow.deep{align-items:flex-start;gap:.8mm;} .deep-n{margin-left:0;white-space:normal;}
  .kit{grid-template-columns:repeat(2,minmax(0,1fr));}
  .levels{grid-template-columns:1fr;}
  .card-h{flex-wrap:wrap;row-gap:.8mm;} .card-h .ct{flex:1 1 calc(100% - 8mm);min-width:0;}
  .card-h .time{margin-left:7.4mm;}
  .block-h{display:block;} .block-h::after{display:none;} .block-h .roman{margin-right:1.4mm;vertical-align:.2mm;}
  h3{display:block;} h3 .h3n{display:block;margin-top:.6mm;}
  .gloss,.keys{columns:1;}
  .tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch;}
  .tscroll table{min-width:620px;}
  table.src.hdr{display:none;}
  table.src,.src thead,.src tbody,.src tr,.src th,.src td{display:block;width:auto !important;}
  .src colgroup{display:none;}
  .src tbody tr{padding:1.6mm 0;border-bottom:.2mm solid var(--rule);}
  .src tbody td{padding:.4mm 0;border:0;}
  .terms thead{display:none;}
  .terms,.terms tbody,.terms tr,.terms td{display:block;width:auto !important;}
  .terms tr{padding:1.4mm 0;border-bottom:.2mm solid var(--rule);}
  .terms td{padding:.2mm 0;border:0;}
}
"""


def parse_ranges(spec):
    out = []
    for part in spec.split(","):
        part = part.strip().upper().replace("U+", "")
        if "-" in part:
            a, b = part.split("-")
            out.append((int(a, 16), int(b, 16)))
        elif "?" in part:
            out.append((int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16)))
        else:
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


faces, total = [], 0
links = re.findall(r'<link rel="stylesheet" href="(node_modules/@fontsource/[^"]+\.css)">\n?', html)
for css_rel in links:
    css_path = HERE / css_rel
    css = css_path.read_text()
    for block in re.findall(r"@font-face\s*\{[^}]*\}", css):
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", block).group(1)
        woff2 = re.search(r"url\((\./files/[^)]+\.woff2)\)", block).group(1)
        cps = {c for c in used for a, b in parse_ranges(rng) if a <= c <= b}
        if not cps:
            continue
        data = subset_woff2(css_path.parent / woff2, cps)
        total += len(data)
        uri = "data:font/woff2;base64," + base64.b64encode(data).decode()
        faces.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                     f"font-display:swap;src:url({uri}) format('woff2');unicode-range:{rng};}}")

html = re.sub(r'<link rel="stylesheet" href="node_modules/@fontsource/[^"]+\.css">\n?', "", html)
html = html.replace("<style>", "<style>\n" + "\n".join(faces) + "\n", 1)
html = html.replace("</style>", SCREEN_CSS + "</style>", 1)
html = html.replace("</body></html>", (HERE.parent / "gh_link.js").read_text(encoding="utf-8") + "</body></html>", 1)
assert "data-gh" in html and "github.io" in html
sys.path.insert(0, str(HERE.parent))
from site_nav import add_sitebar
html = add_sitebar(html, "roadmap")
OUT.write_text(html, encoding="utf-8")
print(f"faces: {len(faces)} | fonts: {total/1024:.0f} KB | html: {OUT.stat().st_size/1024:.0f} KB")
