# -*- coding: utf-8 -*-
"""Builds the v8 statistics roadmap (HTML -> PDF via Chromium)."""
import re, json, pathlib

HERE = pathlib.Path(__file__).parent
VERSION = "8"

# ---------------------------------------------------------------- links
U = dict(
    karpov1="https://stepik.org/course/76/promo",
    karpov2="https://stepik.org/course/524/promo",
    karpov3="https://stepik.org/course/2152/promo",
    sq="https://statquest.org/video_index.html",
    st="https://seeing-theory.brown.edu/",
    ts="https://allendowney.github.io/ThinkStats/",
    msab="https://github.com/FUlyankin/matstat-AB",
    yamc="https://github.com/FUlyankin/yet_another_matstat_course",
    islp="https://www.statlearning.com/",
    bruce_en="https://www.oreilly.com/library/view/practical-statistics-for/9781492072935/",
    bruce_ru="https://bhv.ru/product/prakticheskaya-statistika-dlya-spetsialistov-data-science-2-e-izd/",
    dlai="https://www.coursera.org/learn/machine-learning-probability-and-statistics",
    umich="https://www.coursera.org/specializations/statistics-with-python",
    lagutin="https://litres.com/book/m-b-lagutin/naglyadnaya-matematicheskaya-statistika-6713832/",
    chernova="https://tvims.nsu.ru/chernova/",
    chernova_ms="https://tvims.nsu.ru/chernova/ms/index.html",
    chernova_tv="https://tvims.nsu.ru/chernova/tv/index.html",
    korsh="https://old.math.nsc.ru/LBRT/v1/general/ExerciseStatistics2.pdf",
    ya="https://education.yandex.ru/handbook/math",
    ya3="https://contest.yandex.ru/tracks/math/mathematical-analysis/chapter-overview",
    ya4="https://contest.yandex.ru/tracks/math/linear-algebra/chapter-overview",
    ya6="https://contest.yandex.ru/tracks/math/probability-theory/chapter-overview",
    b3_calc="https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr",
    b3_la="https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
    pyda="https://wesmckinney.com/book/",
    msu="https://cmp.phys.msu.ru/ru/study/math-ms",
    ims="https://openintro-ims.netlify.app/",
    psu414="https://online.stat.psu.edu/stat414/",
    psu415="https://online.stat.psu.edu/stat415/",
    stat110="https://projects.iq.harvard.edu/stat110/home",
    mit="https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
    mit_ps="https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/pages/problem-sets",
    mit650="https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/",
    mit650s="https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/pages/lecture-slides/",
    gmurman="https://urait.ru/book/rukovodstvo-k-resheniyu-zadach-po-teorii-veroyatnostey-i-matematicheskoy-statistike-449645",
    stepik326="https://stepik.org/course/326/promo",
    stepik182381="https://stepik.org/course/182381/promo",
    dnk="https://github.com/bdemeshev/probability_dna",
    kohavi="https://experimentguide.com/",
    fpppy="https://otexts.com/fpppy/",
    nielsen="https://www.labirint.ru/books/786694/",
    facure="https://matheusfacure.github.io/python-causality-handbook/landing-page.html",
    tb="https://allendowney.github.io/ThinkBayes2/",
    dp_ru="https://www.piter.com/product/veroyatnostnoe-programmirovanie-na-python-bayesovskiy-vyvod-i-algoritmy",
    dp_en="https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers",
    raschka="https://arxiv.org/abs/1811.12808",
    wass="https://www.stat.cmu.edu/~larry/all-of-statistics/",
    cb="https://www.routledge.com/Statistical-Inference/Casella-Berger/p/book/9781032593036",
    esl="https://hastie.su.domains/ElemStatLearn/",
    cv="https://stats.stackexchange.com/",
    scipy="https://docs.scipy.org/doc/scipy/reference/stats.html",
    sm="https://www.statsmodels.org/stable/index.html",
    spieg="https://www.mann-ivanov-ferber.ru/catalog/product/iskusstvo-statistiki/",
    wheelan="https://www.mann-ivanov-ferber.ru/catalog/product/golaya-statistika/",
    cats="https://www.chitai-gorod.ru/product/statistika-i-kotiki-2855264",
    # university programmes (section 4)
    stan_curr="https://statistics.stanford.edu/academic-programs/graduate-programs/statistics-data-science-curriculum",
    stan200="https://web.stanford.edu/class/stats200/index.html",
    stan203="https://online.stanford.edu/courses/stats203-introduction-regression-models-and-analysis-variance",
    harv111="https://qrd.college.harvard.edu/directory/stat-111",
    cmu705="https://www.stat.cmu.edu/~siva/teaching/705/syllabus.pdf",
    col_ms="https://datascience.columbia.edu/education/ms-data-science",
    col_bul="https://www.engineering.columbia.edu/sites/default/files/2024-02/data_science_institute_2021.pdf",
    col5703="https://doc.sis.columbia.edu/subj/STAT/GR5703-20261-001/",
    data100="https://ds100.org/sp26/",
)
SQ = dict(  # StatQuest videos (from statquest.org/video_index.html)
    hist="https://youtu.be/qBigTkBLU6g", box="https://youtu.be/fHLhBnmwUM0",
    cov="https://youtu.be/qtaqvPAeEJY", corr="https://youtu.be/xZ_z8KWkhXE",
    varN="https://youtu.be/sHRBg6BhKjI", cond="https://youtu.be/_IgyaD7vOOA",
    bayes="https://youtu.be/9wCnvr7Xw4E", ev="https://youtu.be/KLs_7b7SKi4",
    clt="https://youtu.be/YAlJCEDH2uY", sdse="https://youtu.be/A82brFpdr9g",
    ml="https://youtu.be/XepXtl9YKwc", ci="https://youtu.be/TqOeMYtOc1w",
    boot="https://youtu.be/Xz0x-8-cgaQ", ht="https://youtu.be/0oc49DyA3hU",
    p="https://youtu.be/vemZtEM63GY", phack="https://youtu.be/HDCOUXE3HMM",
    power="https://youtu.be/Rsc5znwR5FA", poweran="https://youtu.be/VX_M3tIyiYk",
    fdr="https://youtu.be/K8LQSvtjcEo", anova="https://youtu.be/NF5_btOaCig",
    linreg="https://youtu.be/7ArmBVF2dCs", r2="https://youtu.be/2AQKmw14mHM",
    logreg="https://youtu.be/yIYKR4sgzI8", odds="https://youtu.be/8nm0G-1uJzA",
    bv="https://youtu.be/EuBBz3bI-aA", cvid="https://youtu.be/fSytzGwwBVw",
    entropy="https://youtu.be/YtebGVx-Fxw",
)
ST = dict(  # Seeing Theory chapters
    c1="https://seeing-theory.brown.edu/basic-probability/index.html",
    c3="https://seeing-theory.brown.edu/probability-distributions/index.html",
    c4="https://seeing-theory.brown.edu/frequentist-inference/index.html",
    c5="https://seeing-theory.brown.edu/bayesian-inference/index.html",
)
MSAB_W = {2: "week02_descreptive_statistics", 4: "week04_eda", 5: "week05_LLN_CLT",
          6: "week06_matstat_sh", 7: "week07_estimators", 8: "week08_confInt",
          9: "week09_hypo", 10: "week10_nonparam_bootstrap", 11: "week11_AB",
          12: "week12_likelihood", 13: "week13_linreg", 14: "week14_timeseries",
          15: "week15_timeseries", 16: "week16_bayes"}
FPP_CH = {1: "01-intro.html", 7: "07-regression.html"}


def a(url, text):
    return f'<a href="{url}">{text}</a>'


def sq(key, title):
    return a(SQ[key], title)


def ts(*chs):
    parts = [a(f"{U['ts']}chap{c:02d}.html", str(c)) for c in chs]
    return f'{a(U["ts"], "<b>Think Stats</b>")}, гл. ' + ", ".join(parts)


def msab(*weeks):
    parts = [a(f"{U['msab']}/tree/main/{MSAB_W[w]}", str(w)) for w in weeks]
    return f'{a(U["msab"], "<b>MatStat-AB</b>")}, нед. ' + ", ".join(parts)


def b(url, name):
    return a(url, f"<b>{name}</b>")


def code(s):
    return f"<code>{s}</code>"


TAGS = {"RU": "t-ru", "EN": "t-en", "Py": "t-py", "R": "t-r", "задачи": "t-task",
        "решения": "t-task", "бесплатно": "t-free", "платно*": "t-paid", "видео": "t-vid"}


def tags(*ts_):
    return "".join(f'<span class="tag {TAGS.get(t, "t-free")}">{t}</span>' for t in ts_)


LEVELS = {1: "вводный", 2: "базовый", 3: "средний", 4: "продвинутый"}


def lvl(n, word=True):
    dots = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(4))
    w = f'<span class="lw">{LEVELS[n]}</span>' if word else ""
    return f'<span class="lv l{n}">{dots}{w}</span>'


STAR = '<span class="star">★</span>'
CIRC = '<span class="circ">○</span>'

# ---------------------------------------------------------------- plan
BLOCKS = {
    0: ("0", "Подготовка", "по необходимости: если математика подзабылась или вы пришли из программирования", "b5"),
    1: ("I", "Фундамент", "язык описания данных и вероятности", "b1"),
    2: ("II", "Статистический вывод", "как по выборке делать выводы о генеральной совокупности", "b2"),
    3: ("III", "Модели и применение", "регрессия, эксперименты, временные ряды", "b3"),
}

STAGES = [
    dict(block=0, num="0", title="Математика и Python для статистики", time="по необходимости",
         topics="производные (в том числе логарифма и частные), интегралы как площадь под кривой, суммы и знак Σ; "
                "векторы, матрицы и их умножение; Python для данных: NumPy, pandas, графики.",
         rows=[
             ("Интуиция", f"3Blue1Brown: {a(U['b3_calc'], 'Essence of calculus')}, "
                          f"{a(U['b3_la'], 'Essence of linear algebra')} (видео)"),
             ("Теория", f"{b(U['ya3'], 'Хендбук Яндекса')}, гл. 3 (матанализ) и {a(U['ya4'], 'гл. 4')} (линейная алгебра)"),
             ("Код", f"{b(U['pyda'], 'McKinney «Python for Data Analysis»')}, 3-е изд. — бесплатно онлайн"),
             ("Чтение", "научно-популярные книги для первого знакомства — раздел 7"),
         ],
         check="найдите p, при котором L(p) = p³(1 − p)⁷ максимальна (через производную ln L), и умножьте "
               "матрицу 2 × 3 на вектор из трёх чисел."),
    dict(block=1, num="1", title="Описательная статистика и EDA", time="≈ 1–2 нед.",
         topics="типы данных и шкалы; среднее, медиана, мода, квантили; дисперсия, стандартное отклонение, "
                "размах и IQR, выбросы; гистограмма и boxplot; ковариация, корреляция Пирсона и Спирмена; "
                "корреляция ≠ причинность.",
         rows=[
             ("Интуиция", f"{b(U['karpov1'], 'Карпов, ч. 1')} (описательные статистики, корреляция) · "
                          f"StatQuest: {sq('hist', 'Histograms')}, {sq('box', 'Boxplots')}, "
                          f"{sq('varN', 'Why Dividing by N Underestimates the Variance')}, "
                          f"{sq('cov', 'Covariance')}, {sq('corr', 'Pearson’s Correlation')}"),
             ("Теория", f"{ts(1, 2, 7)} · {b(U['ims'], 'OpenIntro')}, гл. 4–5 · "
                        f"{b(U['bruce_en'], 'Брюс')}, гл. 1 — как те же понятия называют в DS"),
             ("Код", f"{msab(2, 4)} · pandas: {code('describe()')}, {code('corr(method=&quot;spearman&quot;)')}"),
             ("Задачи", f"{b(U['ims'], 'OpenIntro')}, гл. 4–5 (ответы к нечётным) · упражнения Think Stats"),
         ],
         check="может ли корреляция Пирсона быть ≈ 0 при сильной зависимости? Приведите пример."),
    dict(block=1, num="2", title="Теория вероятностей", time="≈ 2–3 нед.",
         topics="вероятность, условная вероятность, формула Байеса, независимость; случайные величины, "
                "функция распределения, плотность; матожидание, дисперсия и ковариация случайных величин "
                "и их свойства; распределения: Бернулли, биномиальное, Пуассона, равномерное, "
                "экспоненциальное, нормальное.",
         rows=[
             ("Интуиция", f"StatQuest: {sq('cond', 'Conditional Probability')}, {sq('bayes', 'Bayes’ Theorem')}, "
                          f"{sq('ev', 'Expected Values')} · {b(U['st'], 'Seeing Theory')}, "
                          f"гл. {a(ST['c1'], '1')}–{a(ST['c3'], '3')}"),
             ("Теория", f"{b(U['ya6'], 'Хендбук Яндекса')}, гл. 6 (с кодом на Python) · "
                        f"{b(U['chernova_tv'], 'Чернова')} «Теория вероятностей» · "
                        f"{b(U['stat110'], 'Stat 110')} или {b(U['psu414'], 'STAT 414')}"),
             ("Код", f"{ts(3, 4, 5, 6)} · scipy.stats: {code('norm')}, {code('binom')}, {code('poisson')} "
                     f"→ {code('.pmf/.pdf')}, {code('.cdf')}, {code('.rvs')}"),
             ("Задачи", f"{b(U['mit_ps'], 'MIT 18.05')} (задания с решениями) · "
                        f"{b(U['gmurman'], 'Гмурман')}, части про события и случайные величины · "
                        f"тесты {b(U['stepik182381'], 'Stepik 182381')}"),
         ],
         deeper=f"совместные распределения и многомерное нормальное, производящие функции моментов, "
                f"неравенства Маркова и Чебышёва — {b(U['stat110'], 'Stat 110')}, {b(U['psu414'], 'STAT 414')}, "
                f"{b(U['chernova_tv'], 'Чернова')}",
         check="чем независимость случайных величин отличается от некоррелированности?"),
    dict(block=1, num="3", title="ЗБЧ, ЦПТ и выборочные распределения", time="≈ 1 нед.",
         topics="генеральная совокупность и выборка; закон больших чисел; центральная предельная теорема; "
                "выборочное распределение статистики, стандартная ошибка; распределения χ², Стьюдента, Фишера.",
         rows=[
             ("Интуиция", f"StatQuest: {sq('clt', 'The Central Limit Theorem')}, "
                          f"{sq('sdse', 'Standard Deviation vs Standard Error')} · "
                          f"{b(U['st'], 'Seeing Theory')}, гл. {a(ST['c3'], '3')}"),
             ("Теория", f"{b(U['lagutin'], 'Лагутин')} · {b(U['bruce_en'], 'Брюс')}, гл. 2 · {ts(8)} (начало)"),
             ("Код", f"{msab(5)} · симуляция ЦПТ: {code('np.random.default_rng()')} → гистограмма выборочных средних"),
             ("Задачи", f"{b(U['mit_ps'], 'MIT 18.05')} (задачи на ЦПТ) · задачи Лагутина"),
         ],
         check="чем стандартное отклонение отличается от стандартной ошибки?"),
    dict(block=2, num="4", title="Оценивание и доверительные интервалы", time="≈ 2 нед.",
         topics="точечные оценки и их свойства: несмещённость, состоятельность, эффективность; метод моментов, "
                "метод максимального правдоподобия (ММП); доверительные интервалы для среднего, доли, "
                "разности; бутстрэп.",
         rows=[
             ("Интуиция", f"StatQuest: {sq('ml', 'Maximum Likelihood')}, {sq('ci', 'Confidence Intervals')}, "
                          f"{sq('boot', 'Bootstrapping')} · {b(U['st'], 'Seeing Theory')}, гл. {a(ST['c4'], '4')}"),
             ("Теория", f"{b(U['lagutin'], 'Лагутин')} · {b(U['chernova_ms'], 'Чернова')} «Математическая статистика» · "
                        f"{b(U['psu415'], 'STAT 415')} (оценивание и ДИ)"),
             ("Код", f"{msab(6, 7, 8, 10, 12)} · {ts(8)} · {code('scipy.stats.bootstrap')}"),
             ("Задачи", f"{b(U['korsh'], 'Коршунов, Чернова')} · {b(U['ims'], 'OpenIntro')}, гл. 12 · "
                        f"{b(U['mit_ps'], 'MIT 18.05')}"),
         ],
         deeper=f"достаточные статистики, информация Фишера и неравенство Рао–Крамера, асимптотическая "
                f"нормальность оценок ММП, дельта-метод — {b(U['chernova_ms'], 'Чернова')}, "
                f"{b(U['yamc'], 'YAMC')} (темы 5–7), {b(U['wass'], 'Wasserman')}, гл. 9",
         check="что именно означает «95%-й доверительный интервал»? Почему про уже построенный интервал "
               "неверно говорить «параметр лежит в нём с вероятностью 95%»?"),
    dict(block=2, num="5", title="Проверка гипотез", time="≈ 2 нед.",
         topics="H₀ и H₁, статистика критерия, уровень значимости α, p-value; ошибки I и II рода, "
                "мощность, размер эффекта; z- и t-критерии (Стьюдента, Уэлча, парный); непараметрические: "
                "Манна–Уитни, перестановочные тесты; множественные сравнения: Бонферрони, Холм, FDR.",
         rows=[
             ("Интуиция", f"StatQuest: {sq('ht', 'Hypothesis Testing')}, {sq('p', 'p-values')}, "
                          f"{sq('phack', 'p-hacking')}, {sq('power', 'Statistical Power')}, "
                          f"{sq('fdr', 'FDR')} · {b(U['karpov1'], 'Карпов, ч. 1')}"),
             ("Теория", f"{b(U['lagutin'], 'Лагутин')} · {b(U['ims'], 'OpenIntro')}, гл. 11, 13–14, 19–21 · "
                        f"{b(U['psu415'], 'STAT 415')} (гипотезы, непараметрика)"),
             ("Код", f"{msab(9, 10)} · {ts(9)} · {code('ttest_ind(a, b, equal_var=False)')} — тест Уэлча; "
                     f"{code('multipletests')} (statsmodels)"),
             ("Задачи", f"{b(U['ims'], 'OpenIntro')}, гл. 11–21 · {b(U['korsh'], 'Коршунов, Чернова')} · "
                        f"{b(U['mit_ps'], 'MIT 18.05')}"),
         ],
         deeper=f"лемма Неймана–Пирсона, тест отношения правдоподобия, критерий Вальда — "
                f"{b(U['yamc'], 'YAMC')} (тема 12), {b(U['wass'], 'Wasserman')}, гл. 10, "
                f"{b(U['mit650s'], 'MIT 18.650')} (лекции 7–10)",
         check="почему p-value — не вероятность того, что H₀ верна?"),
    dict(block=2, num="6", title="Несколько групп и таблицы сопряжённости", time="≈ 1 нед.",
         topics="дисперсионный анализ (ANOVA) и попарные сравнения после него; критерий Краскела–Уоллиса; "
                "χ²-критерии независимости и согласия; точный тест Фишера.",
         rows=[
             ("Интуиция", f"{b(U['karpov1'], 'Карпов, ч. 1')} (ANOVA) и {b(U['karpov2'], 'ч. 2')} "
                          f"(номинативные данные, непараметрика) · StatQuest: {sq('anova', 't-tests and ANOVA')}"),
             ("Теория", f"{b(U['bruce_en'], 'Брюс')}, гл. 3 · {b(U['ims'], 'OpenIntro')}, гл. 18, 22 · "
                        f"{b(U['psu415'], 'STAT 415')} (χ²-критерии)"),
             ("Код", f"{msab(10)} (критерии согласия) · scipy.stats: {code('f_oneway')}, {code('kruskal')}, "
                     f"{code('chi2_contingency')}, {code('fisher_exact')}"),
             ("Задачи", f"{b(U['ims'], 'OpenIntro')}, гл. 18, 22"),
         ],
         check="почему нельзя сравнить пять групп попарными t-тестами без поправки?"),
    dict(block=3, num="7", title="Регрессия", time="≈ 2 нед.",
         topics="МНК; интерпретация коэффициентов, R²; значимость коэффициентов и корреляции; "
                "категориальные признаки; диагностика: остатки, гетероскедастичность, мультиколлинеарность; "
                "логистическая регрессия, отношение шансов.",
         rows=[
             ("Интуиция", f"StatQuest: {sq('linreg', 'Linear Regression')}, {sq('r2', 'R-squared')}, "
                          f"{sq('logreg', 'Logistic Regression')}, {sq('odds', 'Odds Ratios')} · "
                          f"{b(U['karpov1'], 'Карпов, ч. 1')} (корреляция и регрессия)"),
             ("Теория", f"{b(U['islp'], 'ISLP')}, гл. 3–4 · {ts(10, 11)} · {b(U['bruce_en'], 'Брюс')}, гл. 4"),
             ("Код", f"{msab(13)} · лабораторные ISLP · statsmodels: {code('smf.ols')}, {code('smf.logit')}"),
             ("Задачи", f"{b(U['islp'], 'ISLP')}, упражнения гл. 3–4 · {b(U['ims'], 'OpenIntro')}, гл. 7–9, 24–26"),
         ],
         deeper=f"обобщённые линейные модели (GLM), регуляризация (ridge, lasso), выбор модели — "
                f"{b(U['islp'], 'ISLP')}, гл. 4 и 6, {b(U['mit650s'], 'MIT 18.650')} (лекции 21–24)",
         check="почему значимый коэффициент регрессии — ещё не причинный эффект?"),
    dict(block=3, num="8", title="A/B-тесты и дизайн экспериментов", time="≈ 1–2 нед.",
         topics="рандомизация и контрольная группа; выбор метрики; мощность, MDE и размер выборки; "
                "«подглядывание» (peeking); метрики-отношения (дельта-метод, линеаризация); "
                "снижение дисперсии (CUPED); множественное тестирование в экспериментах.",
         rows=[
             ("Интуиция", f"StatQuest: {sq('poweran', 'Power Analysis')} · {b(U['bruce_en'], 'Брюс')}, гл. 3 "
                          f"(A/B-тесты, мощность и размер выборки)"),
             ("Теория", f"{b(U['kohavi'], 'Кохави, Тан, Сюй')} «Доверительное A/B-тестирование»"),
             ("Код", f"{msab(11)} · {b(U['yamc'], 'YAMC')}, темы 8–9 и 14 (асимптотический A/B, "
                     f"метрики-отношения, CUPED) · {code('statsmodels.stats.power')}"),
             ("Задачи", f"домашние задания {b(U['yamc'], 'YAMC')}"),
         ],
         check="почему нельзя остановить тест, как только p-value опустилось ниже 0,05?"),
    dict(block=3, num="9", title="Временные ряды · отдельный трек", time="≈ 2–3 нед.",
         topics="тренд, сезонность, декомпозиция; автокорреляция (ACF, PACF); стационарность, белый шум; "
                "простые прогнозы (наивный, сезонный наивный) как точка отсчёта; экспоненциальное "
                "сглаживание (ETS), ARIMA; валидация по времени, метрики MAE, RMSE, MASE; интервалы прогноза; "
                "ложная корреляция рядов с трендом. Можно начинать сразу после этапа 7.",
         rows=[
             ("Интуиция", f"{ts(12)} — мягкое введение"),
             ("Теория", f"{b(U['fpppy'], 'FPP, the Pythonic Way')}, гл. "
                        f"{a(U['fpppy'] + FPP_CH[1], '1–5')}, {a(U['fpppy'] + FPP_CH[7], '7–9')} · "
                        f"{b(U['nielsen'], 'Нильсен')} (на русском; R и Python)"),
             ("Код", f"FPP (statsforecast) · {msab(14, 15)} · {code('statsmodels.tsa')}: "
                     f"{code('acf')}, {code('adfuller')}"),
             ("Задачи", f"упражнения в конце глав {b(U['fpppy'], 'FPP')}"),
         ],
         check="почему для временного ряда нельзя делать обычную кросс-валидацию с перемешиванием?"),
]

TOPICS = [
    dict(num="А", title="Причинный вывод (causal inference)", time="после этапов 7–8",
         why="в DS часто спрашивают «что будет, если изменить X?», а корреляция и регрессия "
             "сами на это не отвечают.",
         topics="конфаундеры, парадокс Симпсона; рандомизация как «золотой стандарт»; разность разностей "
                "(diff-in-diff), мэтчинг и propensity score, инструментальные переменные.",
         where=f"{b(U['facure'], 'Facure')} «Causal Inference for the Brave and True», ч. I (Python) · "
               f"{b(U['yamc'], 'YAMC')}, тема 14 (ATE, uplift) · {b(U['ims'], 'OpenIntro')}, гл. 3 (парадокс Симпсона) · "
               f"глубже — {b(U['wass'], 'Wasserman')}, гл. 16",
         check="что такое конфаундер? Приведите пример парадокса Симпсона."),
    dict(num="Б", title="Байесовская статистика", time="после этапа 4",
         why="другой взгляд на неопределённость; основа байесовских A/B-тестов и вероятностных моделей в ML.",
         topics="априорное и апостериорное распределения, правдоподобие; сопряжённые априорные; "
                "байесовский интервал; основы MCMC.",
         where=f"{b(U['tb'], 'Think Bayes')}, 2-е изд. (Python) · {msab(16)} · "
               f"{b(U['dp_ru'], 'Дэвидсон-Пайлон')} (PyMC, есть перевод) · "
               f"{b(U['st'], 'Seeing Theory')}, гл. {a(ST['c5'], '5')} · глубже — {b(U['wass'], 'Wasserman')}, гл. 11",
         check="чем байесовский интервал (credible) отличается от доверительного (confidence)?"),
    dict(num="В", title="Статистика в оценке ML-моделей", time="вместе с курсами по ML",
         why="метрика модели на тесте — тоже случайная величина: без ДИ и корректного сравнения легко "
             "«найти» улучшение, которого нет.",
         topics="смещение и разброс (bias–variance); кросс-валидация и бутстрэп; ДИ для метрик; сравнение "
                "моделей (парные тесты, критерий Мак-Немара); утечки данных; связь ММП и функций потерь "
                "(MSE ↔ нормальный шум, log-loss ↔ правдоподобие Бернулли); энтропия и KL-дивергенция.",
         where=f"{b(U['islp'], 'ISLP')}, гл. 5 и 13 · {msab(13)} (функции потерь из ММП) · "
               f"{b(U['raschka'], 'Raschka')} (2018), обзор методов оценки и сравнения моделей · "
               f"StatQuest: {sq('bv', 'Bias and Variance')}, {sq('cvid', 'Cross Validation')}, "
               f"{sq('entropy', 'Entropy')} · {b(U['ya6'], 'Хендбук Яндекса')}, гл. 6 (информационные меры)",
         check="как получить доверительный интервал для accuracy модели на тестовой выборке?"),
]


def stage_card(s, bc):
    rows = "".join(f'<div class="rl">{l}</div><div class="rc">{c}</div>' for l, c in s["rows"])
    deeper = ""
    if s.get("deeper"):
        deeper = (f'<div class="deeper"><div class="dl">Глубже</div>'
                  f'<div class="dc">{lvl(4, word=False)}{s["deeper"]}</div></div>')
    return f"""
<div class="card {bc}">
  <div class="card-h"><span class="num">{s['num']}</span><span class="ct">{s['title']}</span>
    <span class="time">{s['time']}</span></div>
  <div class="topics"><span class="lbl">Темы</span>{s['topics']}</div>
  <div class="rows">{rows}</div>
  {deeper}
  <div class="check"><span class="ck">✓ Проверь себя:</span> {s['check']}</div>
</div>"""


def topic_card(t):
    return f"""
<div class="card b4">
  <div class="card-h"><span class="num">{t['num']}</span><span class="ct">{t['title']}</span>
    <span class="time">{t['time']}</span></div>
  <div class="rows">
    <div class="rl">Зачем</div><div class="rc">{t['why']}</div>
    <div class="rl">Темы</div><div class="rc">{t['topics']}</div>
    <div class="rl">Где</div><div class="rc">{t['where']}</div>
  </div>
  <div class="check"><span class="ck">✓ Проверь себя:</span> {t['check']}</div>
</div>"""


def block_header(n):
    r, t, d, bc = BLOCKS[n]
    return (f'<div class="block-h {bc}"><span class="roman">{r}</span>'
            f'<span class="bt">{t}</span> <span class="bd">— {d}</span></div>')


plan_parts = []
for n in (0, 1, 2, 3):
    bc = BLOCKS[n][3]
    cards = [s for s in STAGES if s["block"] == n]
    plan_parts.append(f'<div class="keep">{block_header(n)}{stage_card(cards[0], bc)}</div>')
    plan_parts += [stage_card(c, bc) for c in cards[1:]]
plan_html = "\n".join(plan_parts)

# ---------------------------------------------------------------- map (page 1)
MAP = [
    ("b1", "I", "Фундамент", [("1", "Описательная статистика и EDA", "1–2 нед."),
                             ("2", "Теория вероятностей", "2–3 нед."),
                             ("3", "ЗБЧ, ЦПТ, выборочные распределения", "1 нед.")], True),
    ("b2", "II", "Статистический вывод", [("4", "Оценивание и доверительные интервалы", "2 нед."),
                                         ("5", "Проверка гипотез", "2 нед."),
                                         ("6", "Несколько групп и таблицы", "1 нед.")], True),
    ("b3", "III", "Модели и применение", [("7", "Регрессия", "2 нед."),
                                         ("8", "A/B-тесты и эксперименты", "1–2 нед."),
                                         ("9", "Временные ряды", "2–3 нед.")], True),
    ("b4", "IV", "Важные темы для DS&nbsp;&amp;&nbsp;AI", [("А", "Причинный вывод", "после 7–8"),
                                                ("Б", "Байесовская статистика", "после 4"),
                                                ("В", "Статистика в оценке ML-моделей", "вместе с ML")], False),
]


def map_html():
    rows = ['<div class="maprow b5"><div class="maplabel"><span class="roman">0</span>'
            '<span>Подготовка</span></div><div class="flow deep">'
            'Математика и Python — этап 0 · вводное чтение: научно-популярные книги — раздел 7'
            '<span class="deep-n">по необходимости</span></div></div>']
    for bc, r, name, chips, arrows in MAP:
        parts = []
        for i, (n, t, w) in enumerate(chips):
            if i:
                parts.append('<span class="arr">→</span>' if arrows else '<span class="arr dot">·</span>')
            parts.append(f'<div class="chip"><span class="cn">{n}</span>'
                         f'<span class="cx">{t}<span class="cw">{w}</span></span></div>')
        rows.append(f'<div class="maprow {bc}"><div class="maplabel"><span class="roman">{r}</span>'
                    f'<span>{name}</span></div><div class="flow">{"".join(parts)}</div></div>')
    rows.append('<div class="maprow b5"><div class="maplabel"><span class="roman">+</span>'
                '<span>Углубление</span></div><div class="flow deep">'
                'строки «Глубже» в этапах · All of Statistics · Casella &amp; Berger · ESL'
                '<span class="deep-n">университетский уровень строгости</span></div></div>')
    return "\n".join(rows)


# ---------------------------------------------------------------- comparison (section 4)
CMP_COLS = [
    ("Этот план", "этапы 0–9, А–В", None),
    ("MIT", "18.05 + 18.650", U["mit650"]),
    ("Stanford", "MS Stat: DS — 200, 203, 202, 209/263", U["stan_curr"]),
    ("Harvard", "Stat 110 + 111", U["harv111"]),
    ("CMU", "36-705", U["cmu705"]),
    ("Columbia", "MS DS — GR5701–5703", U["col_ms"]),
    ("Berkeley", "Data 100", U["data100"]),
]
# F = есть, H = частично/по выбору, P = пререквизит, N = нет в описании
CMP_ROWS = [
    ("1", "Описательная статистика, EDA", "F H H H N F F"),
    ("2", "Теория вероятностей", "F F P F P F H"),
    ("3", "ЗБЧ, ЦПТ, выборочные распределения", "F F F F F F H"),
    ("4", "Оценивание, ММП, ДИ, бутстрэп", "F F F F F F F"),
    ("5", "Проверка гипотез, множественные сравнения", "F F F F F F H"),
    ("6", "ANOVA, χ²-критерии, непараметрика", "F F F N H N N"),
    ("7", "Регрессия (линейная, логистическая, GLM)", "F F F H F F F"),
    ("8", "A/B-тесты, дизайн экспериментов", "F N H N N H N"),
    ("9", "Временные ряды", "F N N N N H N"),
    ("А", "Причинный вывод", "F N H H H N N"),
    ("Б", "Байесовская статистика", "F F F F F F N"),
    ("В", "Статистика в ML: bias–variance, CV", "F N F H H N F"),
    ("+", "Строгая теория: Фишер, асимптотика, LRT", "H F F F F H N"),
]
MARK = {"F": '<span class="mk mf" title="есть"></span>', "H": '<span class="mk mh" title="частично"></span>',
        "P": '<span class="mk mp" title="пререквизит"></span>', "N": '<span class="mk mn" title="нет"></span>'}


def cmp_html():
    head = "".join(
        f'<th class="{"me" if i == 0 else ""}">{a(u, n) if u else n}<span class="csub">{s}</span></th>'
        for i, (n, s, u) in enumerate(CMP_COLS))
    body = []
    for num, name, marks in CMP_ROWS:
        cells = "".join(f'<td class="{"me" if i == 0 else ""}">{MARK[m]}</td>'
                        for i, m in enumerate(marks.split()))
        body.append(f'<tr><td class="ct1"><span class="cnum">{num}</span>{name}</td>{cells}</tr>')
    return (f'<table class="cmp"><colgroup><col style="width:31%"><col span="7"></colgroup>'
            f'<thead><tr><th class="ct1">Тема</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>')


CMP_LEGEND = (f'{MARK["F"]} есть в программе · {MARK["H"]} частично, кратко или курс по выбору · '
              f'{MARK["P"]} пререквизит — изучают до курса · {MARK["N"]} нет в описании (часто — отдельный курс)')

CMP_FINDINGS = [
    "<b>Ядро совпадает.</b> Оценивание, доверительные интервалы, проверка гипотез, регрессия и байесовский "
    "подход есть почти во всех программах — в плане это этапы 3–5, 7 и тема Б.",
    "<b>Теорвер — фундамент.</b> В Stanford и CMU он пререквизит, в MIT, Harvard и Columbia — первый курс "
    "(18.05, Stat 110, GR5701). В плане это этап 2, его не стоит пропускать.",
    "<b>Университеты глубже в теории.</b> Информация Фишера, асимптотика ММП, тест отношения правдоподобия и "
    "лемма Неймана–Пирсона — стандарт MIT 18.650, Stanford STATS 200, Harvard Stat 111 и CMU 36-705. "
    "В плане это строки «Глубже» в этапах 2, 4, 5, 7 и «Углубление».",
    "<b>DS-программы добавляют практику:</b> EDA и визуализацию (Columbia GR5702, Berkeley Data 100), "
    "statistical learning (Stanford STATS 202, Data 100), причинный вывод или планирование экспериментов "
    "(Stanford STATS 209 или 263). В плане это этапы 1, 8 и темы А, В.",
    "<b>A/B-тесты и временные ряды</b> в ядро статистики обычно не входят: это отдельные курсы или части "
    "прикладных (Columbia GR5703 упоминает дизайн экспериментов и данные, зависящие от времени). В плане они "
    "вынесены в этапы 8–9, потому что постоянно нужны в работе.",
]
CMP_LINKS = [("MIT 18.05", U["mit"]), ("MIT 18.650", U["mit650"]), ("Stanford: ядро MS Stat: DS", U["stan_curr"]),
             ("STATS 200", U["stan200"]), ("STATS 203", U["stan203"]), ("Harvard Stat 111", U["harv111"]),
             ("CMU 36-705", U["cmu705"]), ("Columbia MS DS", U["col_ms"]),
             ("Columbia GR5701–5703", U["col_bul"]), ("GR5703, весна 2026", U["col5703"]),
             ("Berkeley Data 100", U["data100"])]

# ---------------------------------------------------------------- terminology
GLOSSARY = [
    ("1", "Данные и описательная статистика", "b1", [
        ("генеральная совокупность", "population"), ("выборка; объём выборки", "sample; sample size"),
        ("наблюдение", "observation"), ("признак, переменная", "feature, variable"),
        ("количественный / категориальный признак", "numerical / categorical variable"),
        ("порядковая шкала", "ordinal scale"), ("среднее (арифметическое)", "mean"),
        ("медиана; мода", "median; mode"), ("квантиль; перцентиль; квартиль", "quantile; percentile; quartile"),
        ("размах", "range"), ("межквартильный размах", "interquartile range (IQR)"),
        ("дисперсия; стандартное отклонение", "variance; standard deviation"),
        ("коэффициент вариации", "coefficient of variation"), ("выброс", "outlier"),
        ("асимметрия; эксцесс", "skewness; kurtosis"), ("ящик с усами (диаграмма размаха)", "box plot"),
        ("диаграмма рассеяния", "scatter plot"), ("ковариация; коэффициент корреляции", "covariance; correlation coefficient"),
        ("ранговая корреляция Спирмена", "Spearman’s rank correlation"),
    ]),
    ("2", "Вероятность", "b1", [
        ("пространство элементарных исходов", "sample space"), ("случайное событие", "random event"),
        ("условная вероятность", "conditional probability"), ("формула полной вероятности", "law of total probability"),
        ("формула Байеса", "Bayes’ theorem"), ("независимость", "independence"),
        ("случайная величина", "random variable"), ("дискретная / непрерывная", "discrete / continuous"),
        ("функция распределения", "cumulative distribution function (CDF)"),
        ("плотность распределения", "probability density function (PDF)"),
        ("ряд распределения", "probability mass function (PMF)"),
        ("математическое ожидание", "expected value, expectation"),
        ("совместное / маргинальное распределение", "joint / marginal distribution"),
        ("нормальное (гауссово) распределение", "normal (Gaussian) distribution"),
        ("показательное (экспоненциальное) распределение", "exponential distribution"),
        ("производящая функция моментов", "moment generating function (MGF)"),
    ]),
    ("3–4", "Выборочные распределения и оценивание", "b2", [
        ("закон больших чисел", "law of large numbers (LLN)"),
        ("центральная предельная теорема", "central limit theorem (CLT)"),
        ("сходимость по вероятности / по распределению", "convergence in probability / in distribution"),
        ("параметр; статистика (функция выборки)", "parameter; statistic"),
        ("точечная / интервальная оценка", "point / interval estimate"),
        ("смещение; несмещённость", "bias; unbiasedness"), ("состоятельность", "consistency"),
        ("эффективность", "efficiency"), ("среднеквадратичная ошибка", "mean squared error (MSE)"),
        ("метод моментов", "method of moments"),
        ("метод максимального правдоподобия (ММП)", "maximum likelihood estimation (MLE)"),
        ("функция правдоподобия", "likelihood function"), ("информация Фишера", "Fisher information"),
        ("число степеней свободы", "degrees of freedom"),
        ("уровень доверия (доверительная вероятность)", "confidence level"), ("бутстрэп", "bootstrap"),
    ]),
    ("5–6", "Проверка гипотез и сравнение групп", "b2", [
        ("нулевая / альтернативная гипотеза", "null / alternative hypothesis"),
        ("статистика критерия", "test statistic"), ("критическая область", "critical (rejection) region"),
        ("односторонний / двусторонний критерий", "one-sided / two-sided test"),
        ("параметрический / непараметрический", "parametric / nonparametric"),
        ("критерий Манна–Уитни", "Mann–Whitney U test"), ("перестановочный тест", "permutation test"),
        ("размер эффекта", "effect size"), ("множественные сравнения", "multiple comparisons (testing)"),
        ("групповая вероятность ошибки I рода", "family-wise error rate (FWER)"),
        ("доля ложных отклонений", "false discovery rate (FDR)"),
        ("дисперсионный анализ", "analysis of variance (ANOVA)"),
        ("межгрупповая / внутригрупповая изменчивость", "between- / within-group variability"),
        ("попарные сравнения после ANOVA", "post hoc tests"),
        ("таблица сопряжённости", "contingency table"), ("критерий согласия", "goodness-of-fit test"),
    ]),
    ("7", "Регрессия", "b3", [
        ("зависимая переменная (отклик)", "dependent variable (response, target)"),
        ("независимая переменная (предиктор)", "independent variable (predictor, regressor)"),
        ("метод наименьших квадратов (МНК)", "ordinary least squares (OLS)"), ("остатки", "residuals"),
        ("коэффициент детерминации", "coefficient of determination (R²)"),
        ("мультиколлинеарность", "multicollinearity"), ("гетероскедастичность", "heteroscedasticity"),
        ("фиктивная переменная", "dummy variable"), ("взаимодействие признаков", "interaction"),
        ("шансы; отношение шансов", "odds; odds ratio"),
        ("обобщённая линейная модель", "generalized linear model (GLM)"),
        ("регуляризация (гребневая, лассо)", "regularization (ridge, lasso)"),
    ]),
    ("8–9", "Эксперименты и временные ряды", "b3", [
        ("контрольная / тестовая группа", "control / treatment group"), ("рандомизация", "randomization"),
        ("минимальный обнаруживаемый эффект", "minimum detectable effect (MDE)"),
        ("снижение дисперсии", "variance reduction"), ("временной ряд", "time series"),
        ("тренд; сезонность", "trend; seasonality"), ("лаг", "lag"),
        ("автокорреляционная функция (АКФ)", "autocorrelation function (ACF)"),
        ("частная АКФ (ЧАКФ)", "partial autocorrelation function (PACF)"),
        ("белый шум", "white noise"), ("стационарность", "stationarity"),
        ("экспоненциальное сглаживание", "exponential smoothing"), ("горизонт прогноза", "forecast horizon"),
    ]),
    ("А–В", "Причинность, байес, ML", "b4", [
        ("конфаундер (вмешивающийся фактор)", "confounder"), ("смещение отбора", "selection bias"),
        ("средний эффект воздействия", "average treatment effect (ATE)"),
        ("разность разностей", "difference-in-differences (DiD)"),
        ("априорное / апостериорное распределение", "prior / posterior distribution"),
        ("сопряжённое априорное распределение", "conjugate prior"),
        ("кросс-валидация (скользящий контроль)", "cross-validation"), ("переобучение", "overfitting"),
        ("компромисс смещения и разброса", "bias–variance tradeoff"), ("утечка данных", "data leakage"),
    ]),
]


def glossary_html():
    out = []
    for num, title, bc, pairs in GLOSSARY:
        items = "".join(f'<div class="gp"><span class="gru">{r}</span><span class="gen">{e}</span></div>'
                        for r, e in pairs)
        out.append(f'<div class="gg {bc}"><div class="ggh"><span class="ggn">{num}</span>{title}</div>{items}</div>')
    return "".join(out)


N_GLOSS = sum(len(g[3]) for g in GLOSSARY)


def ru_plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


GLOSS_PAIRS = f"{N_GLOSS} {ru_plural(N_GLOSS, 'пара', 'пары', 'пар')}"

TERMS = [
    ("дисперсия", "variance", "<i>dispersion</i> в английском — «разброс» вообще; дисперсионный анализ = ANOVA"),
    ("стандартное (среднеквадратическое) отклонение", "standard deviation, SD",
     "у Гмурмана — «среднее квадратическое отклонение»"),
    ("стандартная ошибка", "standard error, SE",
     "разброс <i>оценки</i> (например, среднего), а не данных: SE = σ/√n"),
    ("выборочная дисперсия", "sample variance",
     "в русских учебниках часто делят на n, а деление на n − 1 называют «исправленной»; в английских "
     "<i>sample variance</i> обычно уже с n − 1. В Python: " + code("np.var") + ", " + code("np.std") +
     " по умолчанию " + code("ddof=0") + " <span class='nw'>(÷ n)</span>, а pandas " + code(".var()") + ", " +
     code(".std()") + " — " + code("ddof=1") + " <span class='nw'>(÷ (n − 1))</span>"),
    ("эксцесс", "kurtosis", code("scipy.stats.kurtosis") + " и pandas " + code(".kurt()") +
     " по умолчанию дают <i>избыточный</i> эксцесс (kurtosis − 3): у нормального распределения он равен 0"),
    ("квантиль", "quantile",
     "квантиль уровня 0,9 = 90-й перцентиль: " + code("np.quantile(x, 0.9)") + " = " + code("np.percentile(x, 90)") +
     "; способы интерполяции у программ разные (параметр " + code("method") + ")"),
    ("выборка", "sample", "в ML-жаргоне <i>sample</i> часто означает одно наблюдение (строку), "
                          "в статистике — весь набор наблюдений"),
    ("статистика", "statistics / statistic",
     "наука — <i>statistics</i>; функция от выборки (например, среднее) — <i>a statistic</i>"),
    ("оценка", "estimate / estimator", "число, посчитанное по выборке / правило его расчёта (случайная величина)"),
    ("правдоподобие", "likelihood",
     "≠ <i>probability</i>: функция параметра при фиксированных данных, в сумме не обязана давать 1"),
    ("выборочное распределение (распределение статистики)", "sampling distribution",
     "распределение оценки по многим выборкам, а не распределение самих данных"),
    ("статистический критерий", "statistical test", "«критерий Стьюдента» = Student’s t-test"),
    ("уровень значимости α; p-значение", "significance level; p-value",
     "p-value в строгих учебниках — «достигаемый уровень значимости»; это не вероятность того, что H₀ верна"),
    ("статистически значимый", "statistically significant",
     "≠ практически важный: смотрите на размер эффекта (effect size) и ДИ"),
    ("ошибка I / II рода; мощность", "type I / II error; power",
     "ошибка I рода — ложноположительный вывод (false positive); мощность = 1 − β"),
    ("доверительный интервал", "confidence interval",
     "<i>trustworthy</i> — «надёжный», а не «доверительный»; байесовский <i>credible interval</i> — "
     "«байесовский (достоверный) интервал»"),
    ("интервал прогноза", "prediction interval",
     "шире доверительного интервала для среднего отклика: учитывает разброс отдельного наблюдения"),
    ("шансы", "odds", "не вероятность: odds = p / (1 − p); при p = 0,8 шансы 4 : 1"),
    ("функция распределения", "cumulative distribution function, CDF",
     "в советских учебниках <span class='nw'>F(x) = P(X &lt; x)</span>, в англоязычных — <span class='nw'>P(X ≤ x)</span>"),
    ("стационарность в широком смысле", "weak (covariance) stationarity",
     "«в узком смысле» = strict stationarity"),
    ("прогноз", "forecast", "<i>forecast</i> — прогноз будущих значений ряда; <i>prediction</i> — любой ответ модели"),
]
terms_html = "\n".join(f"<tr><td class='ru'>{r}</td><td class='en'>{e}</td><td>{n}</td></tr>"
                       for r, e, n in TERMS)


# ---------------------------------------------------------------- sources
def src(mark, name, sub, level, need, tg, why, links):
    m = STAR if mark == "*" else CIRC
    lk = "<br>".join(f'<a href="{u}">{t.replace("/", "/<wbr>")}</a>' for t, u in links)
    need_html = f"<span class='need'>нужно: {need}</span>" if need else ""
    lv = lvl(level) if level else ""
    return (f"<tr><td class='sname'>{m}<b>{name}</b><span class='ssub'>{sub}</span>{need_html}"
            f"<span class='stags'>{lv}{tags(*tg)}</span></td><td>{why}</td><td class='slink'>{lk}</td></tr>")


def grp(title, note=""):
    return ("GRP", title, note)


SOURCES = [
    grp("Подготовка: математика и Python", "этап 0"),
    src("o", "3Blue1Brown «Essence of calculus», «Essence of linear algebra»", "YouTube", 1, "",
        ("EN", "видео", "бесплатно"),
        "Геометрическая интуиция для производных, интегралов, векторов и матриц: 12 и 16 коротких видео.",
        [("youtube.com (calculus)", U["b3_calc"]), ("youtube.com (linear algebra)", U["b3_la"])]),
    src("o", "Хендбук Яндекса «Математика для анализа данных»", "Яндекс Образование и ФКН ВШЭ", 3,
        "основы высшей математики и Python (по словам авторов)", ("RU", "Py", "задачи", "бесплатно"),
        "Гл. 3 — матанализ (производные, градиент), гл. 4 — линейная алгебра, гл. 6 — теория вероятностей; "
        "с задачами и кодом. Матстата нет.",
        [("education.yandex.ru/handbook/math", U["ya"])]),
    src("o", "McKinney «Python for Data Analysis», 3-е изд.", "книга автора pandas · открытая онлайн-версия", 2,
        "основы Python", ("EN", "Py", "бесплатно"),
        "NumPy, pandas, очистка данных и графики — инструменты для всех этапов плана.",
        [("wesmckinney.com/book", U["pyda"])]),

    grp("Интуиция и визуализация", "шаг 1 цикла"),
    src("*", "Карпов «Основы статистики», ч. 1", "Stepik, Институт биоинформатики", 1, "",
        ("RU", "видео", "задачи", "бесплатно"),
        "Одно из лучших объяснений базы на русском; более 6 тыс. отзывов. Ч. 2 (номинативные данные, "
        "непараметрика) и ч. 3 (регрессия подробнее, смешанные модели) — по желанию, уровень базовый, местами R.",
        [("stepik.org/course/76 (ч. 1)", U["karpov1"]), ("…/524 (ч. 2)", U["karpov2"]),
         ("…/2152 (ч. 3)", U["karpov3"])]),
    src("*", "StatQuest", "Josh Starmer", 1, "", ("EN", "видео", "бесплатно"),
        "Короткие визуальные объяснения; плейлист «Statistics Fundamentals» идёт от простого к сложному. "
        "Конкретные видео указаны в карточках этапов.",
        [("statquest.org/video_index", U["sq"])]),
    src("o", "Seeing Theory", "Brown University", 1, "", ("EN", "бесплатно"),
        "Интерактивные визуализации: вероятность, ЦПТ, ДИ, бутстрэп, байес, регрессия. Сайт в архивном режиме, "
        "но работает.",
        [("seeing-theory.brown.edu", U["st"])]),

    grp("Теория с точными формулировками", "шаг 2 цикла"),
    src("*", "Лагутин «Наглядная математическая статистика»", "Лаборатория знаний, 9-е и 10-е изд.", 3,
        "начала матанализа", ("RU", "задачи", "решения"),
        "Теорвер и матстат через примеры и задачи с решениями. Главный учебник на русском в этом плане; "
        "его рекомендуют и курс ФКН ВШЭ, и Ульянкин.",
        [("litres.com (электронная версия)", U["lagutin"])]),
    src("o", "Чернова «Теория вероятностей», «Математическая статистика»", "НГУ, лекции", 4,
        "матанализ; для матстата — теорвер",
        ("RU", "бесплатно"),
        "Короткие ёмкие лекции с доказательствами. Автор просит не выкладывать их на других сайтах — "
        "скачивайте со страницы НГУ.",
        [("tvims.nsu.ru/chernova", U["chernova"])]),
    src("o", "МГУ, физфак: пособия по оцениванию и проверке гипотез", "кафедра математического моделирования и информатики",
        4, "матанализ, теорвер", ("RU", "бесплатно"),
        "Справочник со строгими формулировками; есть отдельная лекция про p-value.",
        [("cmp.phys.msu.ru/ru/study/math-ms", U["msu"])]),
    src("*", "OpenIntro «Introduction to Modern Statistics», 2-е изд.", "Çetinkaya-Rundel, Hardin", 2,
        "школьная алгебра", ("EN", "задачи", "решения", "бесплатно"),
        "Тщательные формулировки, реальные данные, бутстрэп и рандомизация; ответы к нечётным упражнениям. "
        "Код на R, но читать можно без него. «Statistically discernible» вместо «significant» — выбор авторов.",
        [("openintro-ims.netlify.app", U["ims"])]),
    src("o", "Penn State STAT 414 / STAT 415", "открытые конспекты", 3, "матанализ; для 415 — STAT 414",
        ("EN", "бесплатно"),
        "414 — вероятность; 415 — оценивание, ДИ, гипотезы, непараметрика, байес. Хорошо написанные "
        "«статьи» по отдельным темам.",
        [("online.stat.psu.edu/stat414", U["psu414"]), ("online.stat.psu.edu/stat415", U["psu415"])]),
    src("o", "Harvard Stat 110", "J. Blitzstein", 3, "матанализ", ("EN", "видео", "задачи", "бесплатно"),
        "Теорвер с нуля и глубоко: видеолекции, книга, листки с упражнениями. Задачи непростые.",
        [("projects.iq.harvard.edu/stat110", U["stat110"])]),

    grp("Python: учебники и курсы", "шаг 3 цикла"),
    src("*", "Downey «Think Stats», 3-е изд.", "2025 · O’Reilly / Green Tea Press", 2, "основы Python",
        ("EN", "Py", "задачи", "бесплатно"),
        "Основная книга с кодом: каждая глава — ноутбук для Colab, от EDA до регрессии и временных рядов. "
        "Формальных выводов мало — формулировки сверяйте с Лагутиным или OpenIntro.",
        [("allendowney.github.io/ThinkStats", U["ts"])]),
    src("*", "MatStat-AB", "Ф. Ульянкин", 3, "основы матанализа и Python", ("RU", "Py", "видео", "бесплатно"),
        "Курс по неделям: описательная статистика → ЦПТ → оценки, ДИ, гипотезы, бутстрэп, A/B → регрессия, "
        "временные ряды, байес. Записи лекций — по ссылке в README.",
        [("github.com/FUlyankin/matstat-AB", U["msab"])]),
    src("o", "Yet Another MatStat Course (YAMC)", "Ф. Ульянкин, ФКН ВШЭ", 4, "теорвер (этап 2)",
        ("RU", "видео", "задачи"),
        "Прикладной матстат и A/B университетского уровня: темы «База» — средний уровень, «Про» — продвинутый. "
        "Записи 2022–2026; материалы и ДЗ — в телеграм-канале курса.",
        [("github.com/FUlyankin/<wbr>yet_another_matstat_course", U["yamc"])]),
    src("*", "ISLP — An Introduction to Statistical Learning with Python",
        "James, Witten, Hastie, Tibshirani, Taylor · 2023", 3, "этапы 1–5; матрицы — на уровне обозначений",
        ("EN", "Py", "задачи", "бесплатно"),
        "Регрессия, классификация, ресэмплинг, регуляризация, множественное тестирование; лабораторные на Python "
        "в каждой главе, бесплатный PDF, онлайн-курсы авторов.",
        [("statlearning.com", U["islp"])]),
    src("o", "Брюс, Брюс, Гедек «Практическая статистика для специалистов Data Science», 2-е изд.",
        "O’Reilly 2020 · БХВ 2021", 2, "основы Python или R", ("EN", "RU", "Py", "R"),
        "Справочник: как статистические понятия называются в DS (гл. 1–4). Упражнений нет. В переводе "
        "нестандартные термины (см. раздел 5) — лучше оригинал. 3-е изд. (2026) вышло как "
        "«AI-Assisted Statistics for Data Scientists».",
        [("oreilly.com (2-е изд.)", U["bruce_en"]), ("bhv.ru (перевод)", U["bruce_ru"])]),
    src("o", "Coursera: Probability &amp; Statistics for ML &amp; Data Science", "DeepLearning.AI, Luis Serrano", 2,
        "Python; школьная математика", ("EN", "Py", "платно*"),
        "Распределения, оценивание, проверка гипотез с лабораторными на Python; 93% слушателей довольны.",
        [("coursera.org (DeepLearning.AI)", U["dlai"])]),
    src("o", "Coursera: Statistics with Python", "University of Michigan", 2, "школьная алгебра",
        ("EN", "Py", "платно*"),
        "Три курса начального уровня: визуализация, ДИ, гипотезы, регрессия, байесовские методы.",
        [("coursera.org (Michigan)", U["umich"])]),

    grp("Задачи с решениями", "шаг 4 цикла"),
    src("*", "MIT 18.05 Introduction to Probability and Statistics", "MIT OpenCourseWare, 2022", 3,
        "матанализ, включая кратные интегралы", ("EN", "задачи", "решения", "бесплатно"),
        "Задания с решениями и онлайн-проверкой ответов, экзамены с решениями; R нужен лишь в отдельных "
        "заданиях.",
        [("ocw.mit.edu (18.05)", U["mit"])]),
    src("o", "Коршунов, Чернова «Сборник задач и упражнений по математической статистике»",
        "Институт математики СО РАН, 2-е изд., 2004", 4, "уверенный теорвер", ("RU", "задачи", "бесплатно"),
        "461 задача: оценки, ММП, ДИ, проверка гипотез — от простых к сложным.",
        [("old.math.nsc.ru (PDF)", U["korsh"])]),
    src("o", "Гмурман «Руководство к решению задач по теории вероятностей и математической статистике»",
        "Юрайт, 11-е изд.", 2, "интегралы — для непрерывных величин", ("RU", "задачи", "решения"),
        "Тренажёр типовых задач с решениями и ответами. Обозначения старые (<span class='nw'>F(x) = P(X &lt; x)</span>, "
        "«исправленная» дисперсия), расчёты вручную — для понимания и кода берите другие источники.",
        [("urait.ru", U["gmurman"])]),
    src("o", "Stepik «Теория вероятностей и математическая статистика» (курс 182381)",
        "КФУ · рейтинг 4,8 (26 отзывов) · около 10 тыс. учащихся", 2, "основы матанализа",
        ("RU", "задачи", "бесплатно"),
        "368 тестов с автопроверкой: события, распределения, оценки, гипотезы, корреляция. Курс начального "
        "уровня для экономистов 2-го курса, без Python — тренажёр перед Stepik 326.",
        [("stepik.org/course/182381", U["stepik182381"])]),
    src("o", "Stepik «Математическая статистика» (курс 326)", "рейтинг 4,7 · около 43 тыс. учащихся", 3,
        "матанализ и теорвер", ("RU", "задачи", "бесплатно"),
        "187 тестов для самопроверки: описательная статистика, ДИ, гипотезы, регрессия.",
        [("stepik.org/course/326", U["stepik326"])]),
    src("o", "Демешев «Культурный код»", "сборник задач", 4, "уверенный теорвер", ("RU", "задачи", "бесплатно"),
        "Красивые нетривиальные задачи по теорверу и матстату — если хочется сложнее.",
        [("github.com/bdemeshev/probability_dna", U["dnk"])]),

    grp("Специализации", "этапы 8–9 и важные темы"),
    src("*", "Кохави, Тан, Сюй «Доверительное A/B-тестирование»",
        "ДМК Пресс, 2021 · ориг. «Trustworthy Online Controlled Experiments», 2020", 2, "этапы 4–5",
        ("RU", "EN"),
        "Главная книга по онлайн-экспериментам. На сайте книги — бесплатная гл. 1 и errata.",
        [("experimentguide.com", U["kohavi"])]),
    src("*", "Hyndman, Athanasopoulos и др. «Forecasting: Principles and Practice, the Pythonic Way»",
        "OTexts, онлайн с 2025", 2, "регрессия (этап 7)", ("EN", "Py", "задачи", "бесплатно"),
        "Python-версия классического учебника fpp3: statsforecast, упражнения в конце глав, новые главы про "
        "нейросети и foundation-модели.",
        [("otexts.com/fpppy", U["fpppy"])]),
    src("o", "Нильсен «Практический анализ временных рядов»", "Диалектика, 2021", 2, "Python или R",
        ("RU", "Py", "R"),
        "Прикладной обзор на русском: от подготовки данных до ML и глубокого обучения для рядов.",
        [("labirint.ru", U["nielsen"])]),
    src("*", "Facure «Causal Inference for the Brave and True»", "онлайн-книга", 3, "регрессия (этап 7)",
        ("EN", "Py", "бесплатно"),
        "Причинный вывод простым языком: рандомизация, регрессия, мэтчинг, diff-in-diff, синтетический контроль.",
        [("matheusfacure.github.io/<wbr>python-causality-handbook", U["facure"])]),
    src("*", "Downey «Think Bayes», 2-е изд.", "Green Tea Press", 2, "основы Python, этап 2",
        ("EN", "Py", "решения", "бесплатно"),
        "Байесовская статистика через вычисления; ноутбуки для Colab и решения упражнений.",
        [("allendowney.github.io/ThinkBayes2", U["tb"])]),
    src("o", "Дэвидсон-Пайлон «Вероятностное программирование на Python»",
        "Питер, 2019 · ориг. «Bayesian Methods for Hackers»", 2, "основы Python", ("RU", "EN", "Py"),
        "Байес на PyMC; английский оригинал бесплатно на GitHub.",
        [("piter.com (перевод)", U["dp_ru"]), ("github.com (оригинал)", U["dp_en"])]),
    src("o", "Raschka «Model Evaluation, Model Selection, and Algorithm Selection in Machine Learning»",
        "arXiv, 2018", 3, "основы ML", ("EN", "бесплатно"),
        "Обзор: отложенная выборка, кросс-валидация, бутстрэп, статистическое сравнение моделей.",
        [("arxiv.org/abs/1811.12808", U["raschka"])]),

    grp("Для углубления и справки", "после плана"),
    src("o", "Wasserman «All of Statistics»", "Springer, 2004", 4, "матанализ, линейная алгебра, теорвер",
        ("EN",),
        "Весь матстат сжато и строго; удобен как справочник, когда база уже есть.",
        [("stat.cmu.edu/~larry/all-of-statistics", U["wass"])]),
    src("o", "Casella, Berger «Statistical Inference», 2-е изд.", "переиздание Routledge, 2024", 4,
        "матанализ, теорвер уровня Stat 110", ("EN", "задачи"),
        "Строгая теория статистического вывода — классический университетский учебник.",
        [("routledge.com", U["cb"])]),
    src("o", "Hastie, Tibshirani, Friedman «The Elements of Statistical Learning»", "Springer", 4,
        "линейная алгебра, ISLP", ("EN", "бесплатно"),
        "Продвинутый statistical learning — после ISLP.",
        [("hastie.su.domains/ElemStatLearn", U["esl"])]),
    src("o", "CrossValidated", "Q&amp;A по статистике", None, "", ("EN", "бесплатно"),
        "Ответы на конкретные «почему» — ищите по названию критерия или понятия.",
        [("stats.stackexchange.com", U["cv"])]),
    src("o", "Документация scipy.stats и statsmodels", "официальная", None, "", ("EN", "Py", "бесплатно"),
        "Какие критерии реализованы и с какими допущениями — сверяйтесь перед использованием.",
        [("docs.scipy.org (scipy.stats)", U["scipy"]), ("statsmodels.org", U["sm"])]),
]

COLGROUP = "<colgroup><col style='width:33%'><col><col style='width:24%'></colgroup>"


def _sources_tables():
    out, cur, head = [], [], None

    def flush():
        if head is None:
            return
        _, t, n = head
        note = f"<span class='gnote'>{n}</span>" if n else ""
        out.append(f"<table class='src'>{COLGROUP}"
                   f"<thead><tr><th class='g' colspan='3'>{t}{note}</th></tr></thead>"
                   f"<tbody>{''.join(cur)}</tbody></table>")

    for item in SOURCES:
        if isinstance(item, tuple):
            flush()
            head, cur = item, []
        else:
            cur.append(item)
    flush()
    return "\n".join(out)


sources_html = _sources_tables()

READING = [
    ("Шпигельхалтер «Искусство статистики. Как находить ответы в данных»", "МИФ, 2021",
     "Лучший вход в тему: разборы реальных исследований, есть определения и формулы.",
     ("mann-ivanov-ferber.ru", U["spieg"])),
    ("Уилан «Голая статистика»", "МИФ",
     "Лёгкое чтение о том, как работают ЦПТ, регрессия и опросы и как статистикой манипулируют.",
     ("mann-ivanov-ferber.ru", U["wheelan"])),
    ("Савельев «Статистика и котики»", "АСТ",
     "Очень короткое введение на вечер; отзывы расходятся — от «понятно и без воды» до «пустая». "
     "Удобно, чтобы объяснить азы тем, кто далёк от статистики.",
     ("chitai-gorod.ru", U["cats"])),
]
reading_html = "\n".join(
    f"<div class='leis'><div class='lt'><b>{t}</b> <span class='ssub'>{s}</span> {lvl(1)}</div>"
    f"<div class='ld'>{d} <a href='{u}'>{lt}</a></div></div>" for t, s, d, (lt, u) in READING)

KEYS = [
    ("0", "ln L = 3 ln p + 7 ln(1 − p); производная 3/p − 7/(1 − p) = 0 даёт p = 0,3 — это оценка максимального "
          "правдоподобия доли «успехов» (3 из 10). Матрица 2 × 3, умноженная на вектор длины 3, даёт вектор длины 2."),
    ("1", "Да. Например, y = x² при x, симметричном относительно нуля: зависимость полная, а r ≈ 0 — "
          "Пирсон измеряет только линейную связь."),
    ("2", "Из независимости следует некоррелированность, но не наоборот (тот же пример y = x²). "
          "Для совместно нормальных величин понятия совпадают."),
    ("3", "SD — разброс данных; SE — разброс оценки (например, среднего) от выборки к выборке: "
          "SE = σ/√n, уменьшается с ростом n."),
    ("4", "Процедура построения даёт интервалы, которые накрывают истинный параметр в 95% выборок. "
          "Параметр не случаен: конкретный интервал его либо содержит, либо нет."),
    ("5", "p-value — вероятность получить такие или более экстремальные данные, <i>если</i> H₀ верна. "
          "Это вероятность данных при H₀, а не H₀ при данных."),
    ("6", "Пар будет 10; если все H₀ верны, шанс хотя бы одной ложной находки при α = 0,05 — порядка "
          "1 − 0,95¹⁰ ≈ 40%. Нужны ANOVA и поправка на множественные сравнения (Холм, Тьюки)."),
    ("7", "Коэффициент описывает связь при фиксированных остальных признаках. Без рандомизации её может "
          "создавать неучтённый конфаундер или обратная причинность."),
    ("8", "Многократная проверка по ходу теста раздувает долю ложноположительных результатов далеко выше α. "
          "Размер выборки фиксируют заранее или используют последовательные методы."),
    ("9", "Перемешивание пускает будущие наблюдения в обучение (утечка), а соседние точки зависимы. "
          "Валидируют «по времени»: обучение на прошлом, проверка на следующем отрезке."),
    ("А", "Конфаундер влияет и на воздействие, и на результат. Парадокс Симпсона: в каждой подгруппе эффект "
          "одного знака, а в объединённых данных — другого (классический пример — приём в Беркли, 1973)."),
    ("Б", "Доверительный интервал — свойство процедуры (95% таких интервалов накрывают параметр). "
          "Байесовский — прямое утверждение «параметр в интервале с вероятностью 95%» при выбранном "
          "априорном распределении."),
    ("В", "Бутстрэп по тестовым объектам (перевыборка с возвращением → перцентили метрики) или биномиальный "
          "интервал для доли верных ответов, например интервал Уилсона."),
]
KEY_BLOCK = {"0": 5, "1": 1, "2": 1, "3": 1, "4": 2, "5": 2, "6": 2, "7": 3, "8": 3, "9": 3,
             "А": 4, "Б": 4, "В": 4}
keys_html = "\n".join(f"<div class='key b{KEY_BLOCK[n]}'><span class='kn'>{n}</span><span>{t}</span></div>"
                      for n, t in KEYS)


# ---------------------------------------------------------------- page 1–2 blocks
CYCLE = [
    ("1", "Интуиция", "Видео на 10–20 минут — понять идею.", "StatQuest, Карпов"),
    ("2", "Теория", "Определения по учебнику, на русском и английском.", "Лагутин, OpenIntro"),
    ("3", "Код", "Повторить расчёты и симуляции в Python.", "Think Stats, MatStat-AB"),
    ("4", "Задачи", "5–10 задач со сверкой ответов.", "MIT 18.05, OpenIntro, Лагутин"),
    ("5", "Проверь себя", "Вопрос из карточки и свой глоссарий RU ↔ EN.", "ключи — в конце файла"),
]
cycle_html = '<span class="carr">›</span>'.join(
    f'<div class="step"><div class="sh"><span class="sn">{n}</span>{t}</div><div class="sd">{d}</div>'
    f'<div class="ss">{s}</div></div>' for n, t, d, s in CYCLE)

KIT = [
    ("Интуиция", [(U["karpov1"], "Карпов «Основы статистики», ч. 1", ("RU", "бесплатно"), 1),
                  (U["sq"], "StatQuest", ("EN", "бесплатно"), 1)]),
    ("Теория", [(U["lagutin"], "Лагутин «Наглядная математическая статистика»", ("RU", "задачи"), 3),
                (U["ims"], "OpenIntro «Introduction to Modern Statistics»", ("EN", "бесплатно"), 2)]),
    ("Код", [(U["ts"], "Think Stats, 3-е изд.", ("EN", "Py", "бесплатно"), 2),
             (U["msab"], "MatStat-AB (Ульянкин)", ("RU", "Py", "бесплатно"), 3)]),
    ("Задачи", [(U["mit"], "MIT 18.05", ("EN", "решения", "бесплатно"), 3),
                (None, "задачи Лагутина и упражнения OpenIntro", (), None)]),
]


def kit_html():
    cols = []
    for h, items in KIT:
        lis = []
        for u, t, tg, lv in items:
            name = a(u, f"<b>{t}</b>") if u else t
            mark = STAR if u else "+"
            extra = f"<br>{lvl(lv)}{tags(*tg)}" if u else ""
            lis.append(f'<div class="ki"><span class="km">{mark}</span><span>{name}{extra}</span></div>')
        cols.append(f'<div class="kcol"><div class="kh">{h}</div>{"".join(lis)}</div>')
    return "".join(cols)


LEVEL_SCALE = [
    (1, "без высшей математики: интуиция, картинки, примеры."),
    (2, "школьная алгебра и немного кода; формулы без доказательств."),
    (3, "нужны производные, интегралы и основы теорвера; выводы формул."),
    (4, "строгие доказательства; уверенные матанализ, линейная алгебра и теорвер."),
]
levels_html = "".join(f'<div class="lsc">{lvl(n)}<span class="lsd">{d}</span></div>' for n, d in LEVEL_SCALE)

RULES = [
    "<b>Параллельно с университетским курсом</b> план работает как карта: найдите тему лекции среди этапов "
    "и берите материалы из карточки.",
    "<b>Определения — только из учебников</b>, не из блогов и научпопа. Если формулировки расходятся, "
    "сверьте русский и английский учебник (подсказки — в разделе 5).",
    "<b>Уровень источника — под свою подготовку.</b> Если математики не хватает, начните с этапа 0 и "
    "источников базового уровня; строки «Глубже» при первом проходе можно пропустить.",
    "<b>Не нужно проходить всё:</b> на каждый шаг цикла достаточно одного источника; ○ — запасные варианты.",
    "<b>После каждого блока — мини-проект</b> в Jupyter на реальных данных: I — разведочный анализ датасета; "
    "II — сравнение групп (размер эффекта, ДИ, p-value); III — регрессия или прогноз с честной валидацией.",
]
rules_html = "".join(f"<li>{r}</li>" for r in RULES)

LEGEND = (tags("RU") + tags("EN") + " язык · " + tags("Py") + tags("R") + " код · " + tags("задачи") +
          " упражнения · " + tags("решения") + " с ответами · " + tags("бесплатно") + tags("платно*") +
          f" · {STAR} основной комплект · {CIRC} дополнительно")

TOC = [("#how", "1", "Как работать"), ("#plan", "2", "План: этапы 0–9"),
       ("#topics", "3", "Важные темы для DS&nbsp;&amp;&nbsp;AI"), ("#compare", "4", "Сравнение с университетами"),
       ("#terms", "5", "Термины RU ↔ EN"), ("#sources", "6", "Источники"),
       ("#reading", "7", "Вводное чтение и ключи")]
PAGES = {h: "?" for h, _, _ in TOC}
try:
    PAGES.update(json.loads((HERE / "pages.json").read_text()))
except Exception:
    pass
toc_html = "".join(f'<a class="ti" href="{h}"><span class="tn">{n}</span><span class="tt">{t}</span>'
                   f'<span class="tp">{PAGES.get(h, "?")}</span></a>' for h, n, t in TOC)

SCOPE = ("<div class='scope'>"
         "<div><b>Уровень:</b> курс «Статистика для Data Science» в магистратуре. Подходит и тем, кто пришёл "
         "в DS из программирования: недостающая математика собрана в этапе 0, у каждого источника указаны "
         "уровень сложности и что нужно знать заранее.</div>"
         "<div><b>Темы:</b> описательная статистика и EDA · теория вероятностей · ЗБЧ и ЦПТ · оценивание и "
         "доверительные интервалы · проверка гипотез · сравнение групп · регрессия · A/B-тесты · временные ряды · "
         "причинный вывод · байесовская статистика · статистика в оценке ML-моделей.</div>"
         "<div><b>Сверено:</b> набор тем сопоставлен с программами MIT, Stanford, Harvard, CMU, Columbia и "
         "Berkeley (раздел 4); ссылки проверены в сентябре 2026.</div></div>")

CSS = (HERE / "style.css").read_text()

HTML = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Статистика для Data Science — дорожная карта v{VERSION}</title>
<link rel="stylesheet" href="node_modules/@fontsource/inter/400.css">
<link rel="stylesheet" href="node_modules/@fontsource/inter/500.css">
<link rel="stylesheet" href="node_modules/@fontsource/inter/600.css">
<link rel="stylesheet" href="node_modules/@fontsource/inter/700.css">
<link rel="stylesheet" href="node_modules/@fontsource/inter/400-italic.css">
<link rel="stylesheet" href="node_modules/@fontsource/pt-serif/400.css">
<link rel="stylesheet" href="node_modules/@fontsource/pt-serif/700.css">
<link rel="stylesheet" href="node_modules/@fontsource/jetbrains-mono/400.css">
<style>{CSS}</style></head>
<body>

<header class="top">
  <div class="kicker">Дорожная карта · версия {VERSION} · сентябрь 2026 · составитель — Claude (Anthropic)</div>
  <h1>Статистика для Data Science</h1>
  <div class="sub">План от простого к сложному и проверенные источники на русском и английском, с упором на Python</div>
  {SCOPE}
  <nav class="toc">{toc_html}</nav>
</header>

<section id="how">
  <h2><span class="hn">1</span>Как работать</h2>
  <p class="lead">Этапы идут сверху вниз; каждый проходите по одному циклу — источники для всех шагов уже подобраны в карточках.</p>
  <div class="cycle">{cycle_html}</div>
  <div class="example"><span class="exh">Пример — этап 4 (доверительные интервалы):</span>
    <span class="es"><span class="sn sm">1</span> StatQuest «Confidence Intervals»</span><span class="ea">→</span>
    <span class="es"><span class="sn sm">2</span> Лагутин, OpenIntro гл. 12</span><span class="ea">→</span>
    <span class="es"><span class="sn sm">3</span> MatStat-AB нед. 8, <code>scipy.stats.bootstrap</code></span><span class="ea">→</span>
    <span class="es"><span class="sn sm">4</span> задачи Коршунова и Черновой</span><span class="ea">→</span>
    <span class="es"><span class="sn sm">5</span> «что означает 95%-й ДИ?»</span></div>

  <h3>Карта этапов <span class="h3n">этапы 1–9 ≈ 14–18 недель при 5–6 часах в неделю</span></h3>
  <div class="map">{map_html()}</div>

  <div class="keep">
  <h3>Основной комплект {STAR} <span class="h3n">этого достаточно, чтобы пройти весь план; остальное — по необходимости</span></h3>
  <div class="kit">{kit_html()}</div>
  </div>

  <div class="keep">
  <h3>Уровни сложности источников <span class="h3n">учитывают математику, глубину и то, что нужно знать заранее</span></h3>
  <div class="levels">{levels_html}</div>
  </div>

  <div class="keep">
  <h3>Правила</h3>
  <ul class="rules">{rules_html}</ul>
  <div class="legend"><span class="lgh">Метки:</span> {LEGEND}</div>
  </div>
</section>

<section id="plan">
  <h2><span class="hn">2</span>План по этапам</h2>
  <p class="lead">В карточке — темы этапа и шаги цикла; строка «Глубже» — университетский уровень строгости, при первом проходе её можно пропустить. Главы указаны для изданий из раздела 6; названия источников и номера глав — кликабельные ссылки.</p>
  {plan_html}
</section>

<section id="topics">
  <div class="keep">
  <h2><span class="hn">3</span>Ещё важные темы для DS&nbsp;&amp;&nbsp;AI</h2>
  <p class="lead">Их часто нет в базовых курсах статистики, но в работе они нужны постоянно. Подключайте параллельно основному плану.</p>
  {topic_card(TOPICS[0])}
  </div>
  {''.join(topic_card(t) for t in TOPICS[1:])}
  <div class="deep keep">
    <div class="dh"><span class="roman">+</span>Для углубления <span class="h3n">после плана, по желанию</span></div>
    <ul>
      <li>{b(U['wass'], 'Wasserman «All of Statistics»')} — весь матстат сжато и строго; удобен как справочник.</li>
      <li>{b(U['cb'], 'Casella, Berger «Statistical Inference»')} — строгая теория статистического вывода.</li>
      <li>{b(U['esl'], 'Hastie, Tibshirani, Friedman «The Elements of Statistical Learning»')} — после ISLP.</li>
      <li>{b(U['yamc'], 'YAMC')}, темы «Про»: виды сходимости, ЦПТ без характеристических функций, лемма Неймана–Пирсона.</li>
    </ul>
  </div>
</section>

<section id="compare" class="pb">
  <h2><span class="hn">4</span>Сравнение с программами университетов</h2>
  <p class="lead">Темы плана сопоставлены с официальными описаниями и программами курсов статистики в сильных университетах (данные на сентябрь 2026). Для каждого университета взято ядро по статистике; названия столбцов — ссылки на программы.</p>
  <div class="tscroll">{cmp_html()}</div>
  <div class="cmp-legend">{CMP_LEGEND}</div>
  <h3>Выводы</h3>
  <ul class="findings">{"".join(f"<li>{f}</li>" for f in CMP_FINDINGS)}</ul>
  <div class="cmp-src"><b>Программы:</b> {" · ".join(a(u, t) for t, u in CMP_LINKS)}. Отметки сделаны по официальным описаниям и программам курсов: «нет в описании» не значит, что тему никогда не упоминают на лекциях.</div>
</section>

<section id="terms" class="pb">
  <h2><span class="hn">5</span>Термины RU&nbsp;↔&nbsp;EN</h2>
  <p class="lead">Словарь по этапам плана — {GLOSS_PAIRS}. Заведите свой глоссарий и дополняйте его по ходу; ниже словаря — места, где чаще всего путаются.</p>
  <div class="gloss">{glossary_html()}</div>
  <h3>Частые ловушки</h3>
  <table class="terms">
    <thead><tr><th style="width:24%">Русский</th><th style="width:21%">English</th><th>На что обратить внимание</th></tr></thead>
    <tbody>{terms_html}</tbody>
  </table>
  <div class="note"><b>Перевод Брюса (БХВ, 2021).</b> Встречаются нестандартные варианты: «разведывательный анализ» (принято — разведочный, EDA), «популяционное среднее» (среднее генеральной совокупности), «перекрёстный контроль» (кросс-валидация), «отношение перевесов» (отношение шансов), «переподгонка» (переобучение), «матрица путаницы» (матрица ошибок), «прецизионность» (точность, precision).</div>
</section>

<section id="sources">
  <h2><span class="hn">6</span>Источники</h2>
  <p class="lead">{STAR} — основной комплект, {CIRC} — дополнительно. Группы идут в порядке этапа 0 и шагов цикла.<br>Уровень сложности: {lvl(1)} {lvl(2)} {lvl(3)} {lvl(4)} — подробнее в разделе 1.</p>
  <table class="src hdr">{COLGROUP}<thead><tr><th>Источник</th><th>Зачем и что читать</th><th>Ссылка</th></tr></thead></table>
  {sources_html}
  <div class="foot">* На Coursera обычно бесплатно открыт первый модуль и есть 7-дневный пробный период; на часть программ можно подать заявку на финансовую помощь.</div>
</section>

<section id="reading">
  <div class="keep">
  <h2><span class="hn">7</span>Вводное чтение</h2>
  <p class="lead">Научно-популярные книги — хороший вход в тему до этапа 1 или параллельно с ним: они дают интуицию и «статистическое мышление». Определения и формулы берите из учебников.</p>
  {reading_html}
  </div>

  <div class="keep">
  <h3 class="kh3">Ключи к «Проверь себя»</h3>
  <div class="keys">{keys_html}</div>
  </div>

  <div class="colophon">
    <h4>О дорожной карте</h4>
    <p><b>Составитель — Claude (Anthropic).</b> Дорожная карта подготовлена искусственным интеллектом: источники
      и ссылки проверены в сентябре 2026 года, набор тем сверен с официальными программами курсов университетов.
      Экспертом-человеком она не рецензировалась, поэтому неточности возможны: об ошибках и неработающих
      ссылках сообщайте <a class="gh" data-gh="issues" href="https://github.com/xcosh/statistics-for-data-science/issues">в Issues на GitHub</a>. Актуальные версии
      карты и справочник терминов к ней — на сайте <a class="url" href="https://xcosh.github.io/statistics-for-data-science/">xcosh.github.io/statistics-for-data-science</a>.</p>
    <p><b>Лицензия CC BY 4.0:</b> текст и схемы можно копировать, распространять и переделывать, в том числе
      для коммерческого использования, указав источник. Права на упомянутые книги, курсы и видео принадлежат
      их авторам.</p>
  </div>

</section>

</body></html>
"""

# typographic non-breaking spaces
HTML = re.sub(r"\b(MIT|STAT|Stat|STATS|CMU|Data|GR) (?=\d)", "\\1\u00a0", HTML)
HTML = re.sub(r"(?<![\w-])(тема|темы|лекции|этап|этапы|этапа|этапов|этапах|этапе|раздел|разделе|раздела) (?=[\dА-В])",
              "\\1\u00a0", HTML)
HTML = re.sub(r"(?<![\w])(гл|нед|ч|изд|т|с)\. ", "\\1.\u00a0", HTML)
HTML = HTML.replace("≈ ", "≈\u00a0")
HTML = re.sub(r"(\d) (нед|тыс|часах|минут|задач|пар\b)", "\\1\u00a0\\2", HTML)

NOWRAP = re.compile(r"(?<![\w/-])((?:A/B|ML|KL|AI|[A-Za-z])-[0-9A-Za-zА-Яа-яЁё]+|\d+-е)")
_parts = re.split(r"(<[^>]+>)", HTML)
_in_style = False
for _i, _p in enumerate(_parts):
    if _p.startswith("<"):
        _low = _p.lower()
        if _low.startswith("<style"):
            _in_style = True
        elif _low.startswith("</style"):
            _in_style = False
        continue
    if not _in_style:
        _parts[_i] = NOWRAP.sub(r'<span class="nw">\1</span>', _p)
HTML = "".join(_parts)
(HERE / "roadmap.html").write_text(HTML, encoding="utf-8")
print("html written", len(HTML), "| glossary pairs:", N_GLOSS)
