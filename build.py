"""Builds the static Mind Booster site into public/.

Run:  python3 build.py
All page text lives in content.py; this file only turns it into HTML.
"""
import html
import json
import os
from content import SITE, PAGES, POSTS, PROJECTS, NAV, UI, CUSTOM_AI

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
BASE = "https://www.mbco.es"


def esc(s):
    return html.escape(s, quote=True)


def url(lang, slug):
    """Site path for a page slug in a language ('' = home)."""
    prefix = "" if lang == "en" else "/es"
    if not slug:
        return prefix + "/" if prefix else "/"
    return f"{prefix}/{slug}"


def write(path, text):
    full = os.path.join(ROOT, path.lstrip("/"))
    if path.endswith("/") or "." not in os.path.basename(path):
        full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def header(lang, slug, alt_href):
    t = UI[lang]
    items = []
    for key, label in NAV[lang]:
        if key.startswith("http"):
            items.append(f'<a href="{key}" target="_blank" rel="noopener">{esc(label)}</a>')
        else:
            cur = ' aria-current="page"' if key == slug else ""
            items.append(f'<a href="{url(lang, key)}"{cur}>{esc(label)}</a>')
    en_cur = ' aria-current="true"' if lang == "en" else ""
    es_cur = ' aria-current="true"' if lang == "es" else ""
    en_href = alt_href if lang == "es" else url("en", slug)
    es_href = alt_href if lang == "en" else url("es", slug)
    return f"""<a class="skip" href="#main">{esc(t['skip'])}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{url(lang, '')}" aria-label="Mind Booster"><img src="/assets/img/logo.png" alt="Mind Booster" width="206" height="40"></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">{esc(t['menu'])}</button>
    <nav class="nav" id="nav" aria-label="{esc(t['menu'])}">
      {''.join(items)}
      <span class="lang"><a href="{en_href}" hreflang="en" lang="en"{en_cur}>EN</a><a href="{es_href}" hreflang="es" lang="es"{es_cur}>ES</a></span>
    </nav>
  </div>
</header>"""


def footer(lang):
    t = UI[lang]
    links = "".join(
        f'<li><a href="{k if k.startswith("http") else url(lang, k)}">{esc(v)}</a></li>' for k, v in NAV[lang]
    )
    social = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SITE["social"])
    thanks = url(lang, t["thanks_slug"])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <h2>{esc(t['news_title'])}</h2>
        <p>{esc(t['news_sub'])}</p>
        <form name="newsletter" method="POST" action="{thanks}" data-netlify="true" netlify-honeypot="company_url">
          <input type="hidden" name="form-name" value="newsletter">
          <p class="hidden-field"><label>Leave empty <input name="company_url"></label></p>
          <label class="skip" for="nl-email">{esc(t['email'])}</label>
          <input id="nl-email" type="email" name="email" required placeholder="{esc(t['email'])}" autocomplete="email">
          <button class="btn" type="submit">{esc(t['subscribe'])}</button>
        </form>
      </div>
      <div>
        <h2>MIND BOOSTER</h2>
        <ul>{links}</ul>
      </div>
      <div>
        <p>Carrer Calabria 16<br>08015 Barcelona, {esc(t['country'])}</p>
        <p><a href="tel:+34656775083">+34 656 775 083</a><br><a href="mailto:info@mbco.es">info@mbco.es</a></p>
        <ul>{social}</ul>
      </div>
    </div>
    <p class="small">© 2026 Mind Booster S.L. · {esc(t['rights'])}</p>
  </div>
</footer>
<script>
(function(){{var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');if(!b)return;b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');}});}})();
</script>"""


def page(lang, slug, title, description, body, alt_href, og_image="/assets/img/logo.png", extra_head=""):
    canon = BASE + url(lang, slug)
    alt_lang = "es" if lang == "en" else "en"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="{lang}" href="{canon}">
<link rel="alternate" hreflang="{alt_lang}" href="{BASE + alt_href}">
<link rel="alternate" hreflang="x-default" href="{BASE + (url('en', slug) if lang == 'en' else alt_href)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE + og_image}">
<link rel="icon" href="/assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}
</head>
<body>
{header(lang, slug, alt_href)}
<main id="main">
{body}
</main>
{footer(lang)}
</body>
</html>
"""


def btn(lang, slug, label, ghost=False):
    href = slug if slug.startswith(("http", "mailto")) else url(lang, slug)
    return f'<a class="btn{" ghost" if ghost else ""}" href="{href}">{esc(label)}</a>'


def paras(items):
    return "".join(f"<p>{esc(p)}</p>" for p in items)


def post_card(lang, p):
    return f"""<a class="post-item" href="{url(lang, 'post/' + p['slug'][lang])}">
  <img src="/assets/img/{p['image']}" alt="" loading="lazy" width="200" height="140">
  <div><p class="meta">{esc(p['date'][lang])}</p><h3>{esc(p['title'][lang])}</h3><p class="muted">{esc(p['excerpt'][lang])}</p></div>
</a>"""


def posts_for(lang):
    return [p for p in POSTS if lang in p["title"]]


# ---------------- pages ----------------

def home(lang):
    c = PAGES["home"][lang]
    steps = "".join(
        f'<div class="card"><h2>{esc(s["h"])}</h2><p>{esc(s["p"])}</p>{btn(lang, s["slug"], s["btn"], True)}</div>'
        for s in c["steps"]
    )
    inds = "".join(
        f'<div class="card"><h3>{esc(i["h"])}</h3><h4>{esc(i["tag"])}</h4><p>{esc(i["p"])}</p></div>' for i in c["industries"]
    )
    svcs = "".join(
        f'<div class="card"><h3>{esc(s["h"])}</h3><h4>{esc(s["tag"])}</h4><p>{esc(s["p"])}</p></div>' for s in c["services"]
    )
    news = "".join(post_card(lang, p) for p in posts_for(lang)[:3])
    body = f"""<section class="hero"><div class="wrap split">
  <div><h1>{esc(c['h1'])}</h1><p class="lead">{esc(c['lead'])}</p><p style="margin-top:28px">{btn(lang, 'contact', c['cta'])}</p></div>
  <img src="/assets/img/home-services.jpg" alt="" width="800" height="600">
</div></section>
<section class="section band"><div class="wrap band-in"><div><p class="eyebrow">{esc(CUSTOM_AI[lang]['eyebrow'])}</p><h2>{esc(CUSTOM_AI[lang]['home_h'])}</h2><p>{esc(CUSTOM_AI[lang]['home_p'])}</p></div><p>{btn(lang, 'custom-ai-solutions', CUSTOM_AI[lang]['home_btn'])}</p></div></section>
<section class="section"><div class="wrap grid c3">{steps}</div></section>
<section class="section soft"><div class="wrap split">
  <img src="/assets/img/home-build.jpg" alt="{esc(c['story_alt'])}" loading="lazy" width="800" height="600">
  <div><p class="eyebrow">Mind Booster</p><h2>{esc(c['story_h'])}</h2>{paras(c['story'])}{btn(lang, 'about', c['story_btn'])}</div>
</div></section>
<section class="section"><div class="wrap"><h2>{esc(c['industries_h'])}</h2><div class="grid c3">{inds}</div></div></section>
<section class="section soft"><div class="wrap">
  <div class="split"><div><h2>{esc(c['services_h'])}</h2><p class="muted">{esc(c['services_lead'])}</p>{btn(lang, 'solutions', c['services_btn'])}</div><img src="/assets/img/svc-strategy.jpg" alt="" loading="lazy" width="800" height="600"></div>
  <div class="grid c3" style="margin-top:32px">{svcs}</div>
</div></section>
<section class="section"><div class="wrap"><h2>{esc(c['news_h'])}</h2><div class="post-list">{news}</div><p style="margin-top:20px">{btn(lang, 'insights', c['news_btn'], True)}</p></div></section>"""
    return page(lang, "", c["title"], c["desc"], body, url("es" if lang == "en" else "en", ""))


def solutions(lang):
    c = PAGES["solutions"][lang]
    blocks = ""
    for i, b in enumerate(c["blocks"]):
        rev = " rev" if i % 2 else ""
        blocks += f'<div class="split{rev}"><div><h3>{esc(b["h"])}</h3>{paras(b["p"])}</div><img src="/assets/img/{b["img"]}" alt="{esc(b["h"])}" loading="lazy" width="700" height="525"></div>'
    body = f"""<section class="hero"><div class="wrap"><p class="eyebrow">{esc(c['h1'])}</p><h1>{esc(c['sub'])}</h1><p class="lead">{esc(c['lead'])}</p></div></section>
<section class="section band"><div class="wrap band-in"><div><p class="eyebrow">{esc(CUSTOM_AI[lang]['eyebrow'])}</p><h2>{esc(CUSTOM_AI[lang]['home_h'])}</h2><p>{esc(CUSTOM_AI[lang]['home_p'])}</p></div><p>{btn(lang, 'custom-ai-solutions', CUSTOM_AI[lang]['home_btn'])}</p></div></section>
<section class="section"><div class="wrap"><h2>{esc(c['what'])}</h2>{blocks}<p style="margin-top:40px">{btn(lang, 'contact', c['cta'])}</p></div></section>"""
    return page(lang, "solutions", c["title"], c["desc"], body, url("es" if lang == "en" else "en", "solutions"))


def about(lang):
    c = PAGES["about"][lang]
    cards = "".join(
        f'<div class="card"><img class="cover" src="/assets/img/{k["img"]}" alt="" loading="lazy" width="600" height="375"><h3>{esc(k["h"])}</h3><p>{esc(k["p"])}</p></div>'
        for k in c["cards"]
    )
    stats = "".join(f'<div><div class="n">{esc(n)}</div><p>{esc(l)}</p></div>' for n, l in c["stats"])
    body = f"""<section class="hero"><div class="wrap"><p class="eyebrow">{esc(c['eyebrow'])}</p><h1>{esc(c['h1'])}</h1><h4>{esc(c['h4'])}</h4>{paras(c['intro'])}</div></section>
<section class="section soft"><div class="wrap"><h2>{esc(c['cards_h'])}</h2><div class="grid c3">{cards}</div></div></section>
<section class="section"><div class="wrap"><h2>{esc(c['approach_h'])}</h2><h4>{esc(c['approach_tag'])}</h4><p class="lead muted" style="max-width:70ch">{esc(c['approach'])}</p></div></section>
<section class="section soft"><div class="wrap"><h2>{esc(c['stats_h'])}</h2><div class="stats">{stats}</div></div></section>"""
    return page(lang, "about", c["title"], c["desc"], body, url("es" if lang == "en" else "en", "about"))


def projects(lang):
    c = PAGES["projects"][lang]
    items = ""
    for p in PROJECTS:
        d = p[lang]
        bullets = ("<ul>" + "".join(f"<li>{esc(b)}</li>" for b in d.get("bullets", [])) + "</ul>") if d.get("bullets") else ""
        links = "".join(f'<a href="{u}" target="_blank" rel="noopener">{esc(l)}</a>' for l, u in p["links"][lang])
        items += f"""<div class="project" id="{p['id']}">
  <img src="/assets/img/{p['img']}" alt="{esc(p['name'])} logo" loading="lazy" width="220" height="220">
  <div><h3>{esc(p['name'])}</h3><p>{esc(d['p'])}</p>{bullets}{''.join(f'<p>{esc(x)}</p>' for x in d.get('after', []))}<div class="links">{links}</div></div>
</div>"""
    body = f"""<section class="hero"><div class="wrap"><p class="eyebrow">{esc(c['eyebrow'])}</p><h1>{esc(c['h1'])}</h1><p class="lead">{esc(c['lead'])}</p></div></section>
<section class="section"><div class="wrap"><h2>{esc(c['portfolio'])}</h2>{items}</div></section>"""
    return page(lang, "our-projects", c["title"], c["desc"], body, url("es" if lang == "en" else "en", "our-projects"))


def field(name, label, kind="text", required=False, ac="", placeholder=""):
    req = " required" if required else ""
    star = "*" if required else ""
    a = f' autocomplete="{ac}"' if ac else ""
    ph = f' placeholder="{esc(placeholder)}"' if placeholder else ""
    fid = "f-" + name
    if kind == "textarea":
        return f'<div class="field"><label for="{fid}">{esc(label)}{star}</label><textarea id="{fid}" name="{name}"{req}{ph}></textarea></div>'
    return f'<div class="field"><label for="{fid}">{esc(label)}{star}</label><input id="{fid}" type="{kind}" name="{name}"{req}{a}{ph}></div>'


def contact(lang):
    c = PAGES["contact"][lang]
    f = c["fields"]
    thanks = url(lang, UI[lang]["thanks_slug"])
    body = f"""<section class="hero"><div class="wrap"><h1>{esc(c['h1'])}</h1><p class="lead">{esc(c['lead'])}</p></div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <form name="contact" method="POST" action="{thanks}" data-netlify="true" netlify-honeypot="company_url">
    <input type="hidden" name="form-name" value="contact">
    <p class="hidden-field"><label>Leave empty <input name="company_url"></label></p>
    <div class="row">{field('first_name', f['first'], required=True, ac='given-name')}{field('last_name', f['last'], required=True, ac='family-name')}</div>
    <div class="row">{field('email', f['email'], 'email', True, 'email')}{field('phone', f['phone'], 'tel', ac='tel')}</div>
    <div class="row">{field('industry', f['industry'])}{field('company', f['company'], ac='organization')}</div>
    {field('message', f['message'], 'textarea')}
    <button class="btn" type="submit">{esc(f['submit'])}</button>
  </form>
  <div class="card"><h3>Mind Booster</h3><p>Carrer Calabria 16<br>08015 Barcelona, {esc(UI[lang]['country'])}</p><p><a href="mailto:info@mbco.es">info@mbco.es</a><br><a href="tel:+34656775083">+34 656 775 083</a></p></div>
</div></section>"""
    return page(lang, "contact", c["title"], c["desc"], body, url("es" if lang == "en" else "en", "contact"))


def invest(lang):
    c = PAGES["invest"][lang]
    f = c["fields"]
    thanks = url(lang, UI[lang]["thanks_slug"])
    body = f"""<section class="hero"><div class="wrap"><p class="eyebrow">{esc(c['h1'])}</p><h1>{esc(c['q'])}</h1><p class="lead">{esc(c['lead'])}</p></div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <form name="investment" method="POST" action="{thanks}" data-netlify="true" netlify-honeypot="company_url">
    <input type="hidden" name="form-name" value="investment">
    <p class="hidden-field"><label>Leave empty <input name="company_url"></label></p>
    <h2>{esc(c['form_h'])}</h2>
    <div class="row">{field('first_name', f['first'], ac='given-name')}{field('last_name', f['last'], ac='family-name')}</div>
    <div class="row">{field('email', f['email'], 'email', True, 'email')}{field('phone', f['phone'], 'tel', ac='tel')}</div>
    {field('company', f['company'], ac='organization')}
    {field('interest', f['interest'], 'textarea', True, placeholder=f['interest_ph'])}
    <button class="btn" type="submit">{esc(f['submit'])}</button>
  </form>
  <div class="card"><h3>Mind Booster</h3><p><a href="mailto:info@mbco.es">info@mbco.es</a><br><a href="tel:+34656775083">+34 656 775 083</a></p><p><a href="{url(lang, 'our-projects')}">{esc(c['see_projects'])}</a></p></div>
</div></section>"""
    return page(lang, "investment-opportunities", c["title"], c["desc"], body, url("es" if lang == "en" else "en", "investment-opportunities"))


def custom_ai(lang):
    c = CUSTOM_AI[lang]
    f = c["fields"]
    slug = "custom-ai-solutions"
    thanks = url(lang, UI[lang]["thanks_slug"])
    probs = "".join(f"<li>{esc(p)}</li>" for p in c["problems"])
    what = "".join(f'<div class="card"><h3>{esc(w["h"])}</h3><p>{esc(w["p"])}</p></div>' for w in c["what"])
    steps = "".join(f'<li class="card"><h3>{esc(s["h"])}</h3><p>{esc(s["p"])}</p></li>' for s in c["steps"])
    models = "".join(f'<div class="card"><h3>{esc(m["h"])}</h3><h4>{esc(m["tag"])}</h4><p>{esc(m["p"])}</p></div>' for m in c["models"])
    why = "".join(f'<div><h3>{esc(w["h"])}</h3><p class="muted">{esc(w["p"])}</p></div>' for w in c["why"])
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in c["faq"])
    ld = {"@context": "https://schema.org", "@type": "Service", "name": c["h1"], "description": c["desc"],
          "provider": {"@type": "Organization", "name": "Mind Booster", "url": BASE}, "areaServed": "ES",
          "serviceType": "Custom AI solutions", "inLanguage": lang}
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]}
    head = (f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
            f'<script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>')
    body = f"""<section class="hero"><div class="wrap split">
  <div><p class="eyebrow">{esc(c['eyebrow'])}</p><h1>{esc(c['h1'])}</h1><p class="lead">{esc(c['lead'])}</p>
  <p class="actions"><a class="btn" href="#plan">{esc(c['cta'])}</a> <a class="btn ghost" href="#how">{esc(c['cta2'])}</a></p></div>
  <img src="/assets/img/svc-software.jpg" alt="" width="800" height="600">
</div></section>
<section class="section soft"><div class="wrap"><h2>{esc(c['problem_h'])}</h2><ul class="checks">{probs}</ul></div></section>
<section class="section"><div class="wrap"><h2>{esc(c['what_h'])}</h2><p class="muted" style="max-width:65ch">{esc(c['what_lead'])}</p><div class="grid c3" style="margin-top:24px">{what}</div></div></section>
<section class="section soft" id="how"><div class="wrap"><h2>{esc(c['how_h'])}</h2><p class="muted">{esc(c['how_lead'])}</p><ol class="steps grid c3">{steps}</ol></div></section>
<section class="section"><div class="wrap"><h2>{esc(c['models_h'])}</h2><div class="grid c3">{models}</div></div></section>
<section class="section soft"><div class="wrap"><h2>{esc(c['why_h'])}</h2><div class="grid c4">{why}</div>
  <h3 style="margin-top:40px">{esc(c['sectors_h'])}</h3><p class="muted" style="max-width:75ch">{esc(c['sectors'])}</p></div></section>
<section class="section"><div class="wrap split" style="align-items:start">
  <div><h2>{esc(c['faq_h'])}</h2><div class="faq">{faq}</div></div>
  <form id="plan" class="card" name="custom-ai" method="POST" action="{thanks}" data-netlify="true" netlify-honeypot="company_url">
    <input type="hidden" name="form-name" value="custom-ai">
    <p class="hidden-field"><label>Leave empty <input name="company_url"></label></p>
    <h2>{esc(c['form_h'])}</h2><p class="muted">{esc(c['form_lead'])}</p>
    <div class="row">{field('name', f['name'], required=True, ac='name')}{field('email', f['email'], 'email', True, 'email')}</div>
    <div class="row">{field('phone', f['phone'], 'tel', ac='tel')}{field('company', f['company'], ac='organization')}</div>
    {field('sector', f['sector'])}
    {field('need', f['need'], 'textarea', True, placeholder=f['need_ph'])}
    <button class="btn" type="submit">{esc(f['submit'])}</button>
  </form>
</div></section>"""
    return page(lang, slug, c["title"], c["desc"], body, url("es" if lang == "en" else "en", slug), "/assets/img/svc-software.jpg", head)


def insights(lang):
    c = PAGES["insights"][lang]
    items = "".join(post_card(lang, p) for p in posts_for(lang))
    body = f"""<section class="hero"><div class="wrap"><h1>{esc(c['h1'])}</h1><p class="lead">{esc(c['lead'])}</p></div></section>
<section class="section"><div class="wrap"><div class="post-list">{items}</div></div></section>"""
    return page(lang, "insights", c["title"], c["desc"], body, url("es" if lang == "en" else "en", "insights"))


def render_blocks(blocks):
    out = ""
    for b in blocks:
        kind = b[0]
        if kind == "p":
            out += f"<p>{b[1]}</p>"
        elif kind == "h":
            out += f"<h2>{esc(b[1])}</h2>"
        elif kind == "q":
            out += f"<blockquote><p>{esc(b[1])}</p></blockquote>"
        elif kind in ("ul", "ol"):
            out += f"<{kind}>" + "".join(f"<li>{x}</li>" for x in b[1]) + f"</{kind}>"
    return out


def post_page(lang, p):
    other = "es" if lang == "en" else "en"
    alt = url(other, "post/" + p["slug"][other]) if other in p["slug"] else url(other, "insights")
    slug = "post/" + p["slug"][lang]
    t = UI[lang]
    ld = {
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": p["title"][lang],
        "datePublished": p["iso"], "inLanguage": lang, "image": BASE + "/assets/img/" + p["image"],
        "author": {"@type": "Organization", "name": "Mind Booster"},
        "publisher": {"@type": "Organization", "name": "Mind Booster", "logo": {"@type": "ImageObject", "url": BASE + "/assets/img/logo.png"}},
    }
    body = f"""<section class="section"><div class="wrap"><article class="post">
  <p class="meta"><a href="{url(lang, 'insights')}">{esc(t['all_news'])}</a> · {esc(p['category'])} · {esc(p['date'][lang])}</p>
  <h1>{esc(p['title'][lang])}</h1>
  <img class="cover" src="/assets/img/{p['image']}" alt="{esc(p['category'])}" width="760" height="360">
  {render_blocks(p['body'][lang])}
</article></div></section>"""
    head = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return page(lang, slug, p["title"][lang] + " | Mind Booster", p["excerpt"][lang], body, alt, "/assets/img/" + p["image"], head)


def thanks(lang):
    t = UI[lang]
    body = f"""<section class="hero"><div class="wrap"><h1>{esc(t['thanks_h'])}</h1><p class="lead">{esc(t['thanks_p'])}</p><p style="margin-top:24px">{btn(lang, '', t['back_home'])}</p></div></section>"""
    other = "es" if lang == "en" else "en"
    return page(lang, t["thanks_slug"], t["thanks_h"] + " | Mind Booster", t["thanks_p"], body, url(other, UI[other]["thanks_slug"]), extra_head='<meta name="robots" content="noindex">')


def notfound():
    t = UI["en"]
    body = f"""<section class="hero"><div class="wrap"><h1>Page not found</h1><p class="lead">The page you're looking for isn't here. <span lang="es">La página que buscas no existe.</span></p><p style="margin-top:24px">{btn('en', '', 'Mind Booster home')} {btn('es', '', 'Inicio en español', True)}</p></div></section>"""
    return page("en", "404", "Page not found | Mind Booster", "Page not found", body, "/es/", extra_head='<meta name="robots" content="noindex">')


def main():
    built = []
    for lang in ("en", "es"):
        for fn, slug in ((home, ""), (solutions, "solutions"), (custom_ai, "custom-ai-solutions"), (about, "about"), (projects, "our-projects"),
                         (contact, "contact"), (invest, "investment-opportunities"), (insights, "insights")):
            write(url(lang, slug) + ("/" if slug else ""), fn(lang))
            built.append(url(lang, slug))
        for p in posts_for(lang):
            write(url(lang, "post/" + p["slug"][lang]) + "/", post_page(lang, p))
            built.append(url(lang, "post/" + p["slug"][lang]))
        write(url(lang, UI[lang]["thanks_slug"]) + "/", thanks(lang))
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(notfound())
    sm = "".join(f"<url><loc>{BASE}{u}</loc></url>" for u in built)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print(len(built), "pages built")


if __name__ == "__main__":
    main()
