# -*- coding: utf-8 -*-
"""Navigation bar for the published web versions: link to the site's start page and to the other document."""

SITEBAR_CSS = """
.sitebar{display:none;}
@media screen{
  .sitebar{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:1mm 5mm;
    margin:0 0 5mm;padding:0 0 2.2mm;border-bottom:.25mm solid var(--rule);font-size:7.6pt;line-height:1.4;color:var(--muted);}
  .sitebar a{color:var(--link);}
  .sitebar .here{color:var(--ink);font-weight:600;}
  .sitebar .sb-docs{display:flex;flex-wrap:wrap;gap:1mm 3.2mm;}
}
"""
DOCS = [("roadmap", "Дорожная карта"), ("terms", "Справочник терминов")]
ICON_LINKS = ('<link rel="icon" href="favicon.ico" sizes="32x32">\n'
              '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
              '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n')


def add_icons(html):
    """Site icon (made by make_icons.py) for the browser tab and bookmarks."""
    if 'href="favicon.svg"' in html:
        return html
    return html.replace("</head>", ICON_LINKS + "</head>", 1)


def add_sitebar(html, current):
    """current: 'roadmap' or 'terms'. Inserts the bar after <body> and its styles at the end of the head styles."""
    parts = [f'<span class="here">{t}</span>' if k == current else f'<a href="{k}.html">{t}</a>' for k, t in DOCS]
    parts.append(f'<a href="{current}.pdf">PDF-версия</a>')
    bar = (f'<nav class="sitebar" aria-label="Материалы"><a href="index.html">← Статистика для Data Science: '
           f'все материалы</a><span class="sb-docs">{"".join(parts)}</span></nav>')
    assert html.count("<body>") == 1 and 'class="sitebar"' not in html
    html = html.replace("<body>", "<body>\n" + bar, 1)
    head_end = html.index("</head>")
    last_style = html.rindex("</style>", 0, head_end)
    return add_icons(html[:last_style] + SITEBAR_CSS + html[last_style:])
