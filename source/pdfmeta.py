# -*- coding: utf-8 -*-
"""Writes document metadata into a finished PDF (links, outline and named destinations are kept)."""
import sys, warnings
from pypdf import PdfReader, PdfWriter
warnings.filterwarnings("ignore")

META = {
    "roadmap": {"/Title": "Статистика для Data Science — дорожная карта (версия 8)",
                "/Subject": "План самостоятельного изучения статистики для Data Science: этапы, источники, глоссарий"},
    "terms": {"/Title": "Статистика для Data Science — основные термины (версия 2)",
              "/Subject": "Справочник: определения, формулы, пояснения, примеры, код на Python и графики"},
}
COMMON = {"/Author": "Claude (Anthropic)", "/Creator": "Claude (Anthropic)",
          "/Keywords": "статистика, data science, теория вероятностей, проверка гипотез, регрессия, A/B-тесты, "
                       "машинное обучение, Python; лицензия CC BY 4.0"}

src, dst, kind = sys.argv[1], sys.argv[2], sys.argv[3]
reader = PdfReader(src)
n_links = sum(len([a for a in (p.get("/Annots") or []) if a.get_object().get("/Subtype") == "/Link"])
              for p in reader.pages)
writer = PdfWriter(clone_from=reader)
writer.add_metadata({**COMMON, **META[kind]})
with open(dst, "wb") as f:
    writer.write(f)
check = PdfReader(dst)
n_links2 = sum(len([a for a in (p.get("/Annots") or []) if a.get_object().get("/Subtype") == "/Link"])
               for p in check.pages)
print(kind, "pages", len(check.pages), "links", n_links, "->", n_links2, "| dests", len(check.named_destinations),
      "|", check.metadata.get("/Title"), "|", check.metadata.get("/Author"))
