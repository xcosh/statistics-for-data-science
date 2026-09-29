# Исходные файлы

Из этих файлов собираются оба документа: PDF (печать через Chromium) и самодостаточные HTML-версии
(шрифты встроены, формулы отрисованы KaTeX заранее).

## Где что править

| Что | Где |
|---|---|
| Статьи справочника: определения, формулы, пояснения, примеры, код | `terms/c1.py` (разделы 1–2), `terms/c2.py` (3–6), `terms/c3.py` (7–9), `terms/c4.py` (А, Б, В) |
| Порядок разделов, подписи к рисункам | `terms/content2.py` |
| Графики справочника (готовые SVG лежат в `terms/fig/`) | `terms/charts2.py` |
| Вёрстка справочника | `terms/build2.py`, `terms/terms2.css` |
| Всё содержание дорожной карты и её вёрстка | `roadmap/build.py`, `roadmap/style.css` |

В текстах справочника формулы пишутся в TeX между `$…$`; поле `f` статьи — список выключных формул.

## Что нужно для сборки

- Python 3.11+ и пакеты: `pip install numpy scipy matplotlib playwright pypdf fonttools brotli`
  (для проверки фрагментов кода из справочника — ещё `pandas statsmodels scikit-learn seaborn`);
- браузер для Playwright: `python -m playwright install chromium`;
- Node.js 18+ и npm;
- утилиты `pdfinfo` и `pdftotext` из пакета poppler (`poppler-utils`).

## Сборка

```bash
# справочник терминов
cd source/terms
npm install
python charts2.py      # только если меняли графики: перерисует fig/*.svg
python render2.py      # сборка terms.html и PDF (номера страниц в оглавлении уточняются автоматически)
python export2.py      # самодостаточная HTML-версия
python ../pdfmeta.py statistics_terms_v2.pdf ../../terms.pdf terms
cp statistics_terms_v2.html ../../terms.html

# дорожная карта
cd ../roadmap
npm install
python render.py
python export_html.py
python ../pdfmeta.py statistics_learning_roadmap_v8.pdf ../../roadmap.pdf roadmap
cp statistics_learning_roadmap_v8.html ../../roadmap.html
```

Скрипты `render*.py` сообщают о выходе содержимого за поля (`overflow check`). После пересборки проверьте
изменённые страницы глазами. HTML-версии из `export*.py` сразу готовы для сайта: в них уже есть верхняя строка
навигации («все материалы», другой документ, PDF-версия).

## Лицензии

Тексты документов, в том числе хранящиеся в этих исходниках (`terms/c1.py`–`c4.py`, `terms/content2.py`,
строки в `roadmap/build.py`), распространяются по лицензии CC BY 4.0 (файл `LICENSE` в корне репозитория).
Код скриптов и стилей сборки можно использовать по лицензии MIT (`source/LICENSE`).
Шрифты Inter, PT Serif и JetBrains Mono (SIL OFL 1.1) и KaTeX (MIT) устанавливаются через npm.
