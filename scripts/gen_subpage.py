#!/usr/bin/env python3
"""
WDC writers-routines sub-page generator.

Stamps long-tail Q&A sub-pages off an author's routine hub, using the exact
template that already ranks (the Stephen King /word-count/ page). Feed it a
content dict (the unique parts) and it writes a complete, schema-rich
index.html into writers-routines/<author>/<subslug>/.

This is the scale pipeline: author content blocks (accurate, per author),
the generator handles the consistent HTML, schema, breadcrumbs, and CTA.
"""
import os, html, json, sys

SITE = "https://writersdailypractice.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEAD_STYLE = """  <style>
    body { -webkit-text-size-adjust: 100%; box-sizing: border-box; color: #2a2a2a; background-color: #fff; min-height: 100%; margin: 0; font-family: 'Inter', system-ui, sans-serif; font-size: 16px; line-height: 1.6; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
    *, *::before, *::after { box-sizing: border-box; }
    .gradient-text { background: linear-gradient(135deg, #E8B931 0%, #F5D060 50%, #E8B931 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .btn-premium { position: relative; overflow: hidden; transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
    .btn-premium:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(232, 185, 49, 0.4); }
    .btn-premium::after { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: left 0.6s; }
    .btn-premium:hover::after { left: 100%; }
    .card-lift { transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
    .card-lift:hover { transform: translateY(-4px); box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
    .nav-blur { backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
    .font-review { font-family: 'Lora', Georgia, serif; }
    .noise-overlay { position: relative; }
    .noise-overlay::before { content: ''; position: absolute; inset: 0; opacity: 0.03; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E"); pointer-events: none; }
    .article-body p { font-family: 'Lora', Georgia, serif; font-size: 17px; line-height: 1.8; color: #2a2a2a; margin-bottom: 1.5em; }
    .article-body h2 { font-family: 'Playfair Display', Georgia, serif; font-size: 24px; font-weight: 700; color: #111111; margin-top: 3em; margin-bottom: 1em; line-height: 1.2; }
    @media (min-width: 768px) { .article-body h2 { font-size: 28px; } }
    .article-body blockquote { border-left: 4px solid #E8B931; padding-left: 1.5em; margin: 2em 0; }
    .article-body blockquote p { font-family: 'Lora', Georgia, serif; font-style: italic; color: #4a4a4a; }
    .article-body strong { font-weight: 600; color: #111111; }
    .article-body em { font-style: italic; }
    .article-body hr { border: none; border-top: 1px solid #e5e7eb; margin: 2.5em 0; }
    .article-body a { color: #1565C0; text-decoration: underline; text-underline-offset: 2px; }
    .article-body a:hover { color: #0D47A1; }
    .article-body ul { font-family: 'Lora', Georgia, serif; font-size: 17px; line-height: 1.8; color: #2a2a2a; margin-bottom: 1.5em; padding-left: 1.5em; }
    .article-body ul li { margin-bottom: 0.5em; }
    .answer-box { background: #fbf9f4; border: 1px solid #eee4c8; border-left: 4px solid #E8B931; border-radius: 12px; padding: 2em; margin: 2.5em 0; }
    .answer-box .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #8a7a3a; font-weight: 600; margin-bottom: 0.75em; }
    .answer-box .answer { font-family: 'Playfair Display', Georgia, serif; font-size: 22px; font-weight: 700; color: #111; line-height: 1.3; margin-bottom: 0.5em; }
    .answer-box .subtext { font-family: 'Inter', system-ui, sans-serif; font-size: 14px; color: #666; line-height: 1.6; }
  </style>"""


def esc(s):
    return html.escape(s, quote=True)


def render_blocks(blocks):
    out = []
    for b in blocks:
        if "h2" in b:
            out.append(f'      <h2>{b["h2"]}</h2>')
        elif "p" in b:
            out.append(f'      <p>{b["p"]}</p>')
        elif "quote" in b:
            by = b.get("by", "")
            out.append('      <blockquote>')
            out.append(f'        <p>{b["quote"]}</p>')
            if by:
                out.append(f'        <p style="font-style: normal; font-size: 14px; color: #888; margin-top: 0.5em;">{by}</p>')
            out.append('      </blockquote>')
        elif "ul" in b:
            out.append('      <ul>')
            for li in b["ul"]:
                out.append(f'        <li>{li}</li>')
            out.append('      </ul>')
        elif "hr" in b:
            out.append('      <hr>')
    return "\n\n".join(out)


def render(d):
    url = f"{SITE}/writers-routines/{d['author_slug']}/{d['subslug']}/"
    faq_items = ",\n".join(
        '      {\n        "@type": "Question",\n'
        f'        "name": {json.dumps(q["q"])},\n'
        '        "acceptedAnswer": {\n          "@type": "Answer",\n'
        f'          "text": {json.dumps(q["a"])}\n        }}\n      }}'
        for q in d["faq"]
    )
    related_cards = "\n".join(
        f'''        <a href="{c['href']}" class="card-lift block bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-primary/20 transition-colors">
          <p class="text-primary font-bold text-xs uppercase tracking-wider mb-1">{c['kicker']}</p>
          <p class="font-serif font-bold text-dark text-[15px]">{c['title']} &rarr;</p>
        </a>'''
        for c in d["related_cards"]
    )
    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(d["title"])}</title>
  <meta name="description" content="{esc(d["meta_desc"])}">
  <link rel="canonical" href="{url}">

  <meta property="og:title" content="{esc(d["og_title"])}">
  <meta property="og:description" content="{esc(d["og_desc"])}">
  <meta property="og:image" content="{SITE}/images/og/warm.jpg">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="The Writer's Daily Practice">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(d["og_title"])}">
  <meta name="twitter:description" content="{esc(d["tw_desc"])}">
  <meta name="twitter:image" content="{SITE}/images/og/warm.jpg">

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": {json.dumps(d["og_title"])},
    "author": {{ "@type": "Person", "name": "Kia Orion", "url": "{SITE}/" }},
    "publisher": {{ "@type": "Organization", "name": "The Writer's Daily Practice", "url": "{SITE}/" }},
    "datePublished": "{d["date_iso"]}",
    "dateModified": "{d["date_iso"]}",
    "description": {json.dumps(d["meta_desc"])},
    "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{url}" }}
  }}
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{faq_items}
    ]
  }}
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Writers' Routines", "item": "{SITE}/writers-routines/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{esc(d["author_name"])}", "item": "{SITE}/writers-routines/{d["author_slug"]}/" }},
      {{ "@type": "ListItem", "position": 4, "name": "{esc(d["crumb"])}" }}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400;1,600&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Inter:wght@300;400;500;600;700&display=swap">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400;1,600&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Inter:wght@300;400;500;600;700&display=swap" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400;1,600&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Inter:wght@300;400;500;600;700&display=swap"></noscript>
  <link rel="stylesheet" href="/css/style.css">
{HEAD_STYLE}
  <script async src="https://plausible.io/js/pa-ZOk4diA46SHVDfHBy61SQ.js"></script>
  <script>
    window.plausible=window.plausible||function(){{(plausible.q=plausible.q||[]).push(arguments)}},plausible.init=plausible.init||function(i){{plausible.o=i||{{}}}};
    plausible.init()
  </script>
</head>
<body>

  <!-- NAV -->
  <nav class="fixed top-0 left-0 right-0 z-50 nav-blur bg-primaryDeep/90 border-b border-white/5">
    <div class="max-w-[1200px] mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-10">
        <a href="/" class="text-white font-serif font-bold text-xl tracking-tight">Kia Orion</a>
        <div class="hidden md:flex items-center gap-8">
          <a href="/book/" class="text-white/50 text-sm font-medium hover:text-white transition-colors duration-300">The Book</a>
          <a href="/genres/" class="text-white/50 text-sm font-medium hover:text-white transition-colors duration-300">For Writers</a>
          <a href="/about/" class="text-white/50 text-sm font-medium hover:text-white transition-colors duration-300">About</a>
        </div>
      </div>
      <a href="#signup" class="btn-premium bg-gradient-to-r from-gold to-goldLight text-dark text-sm font-bold px-6 py-2.5 rounded-full">Start Free</a>
    </div>
  </nav>

  <!-- HEADER -->
  <header class="pt-28 md:pt-36 pb-12 md:pb-16">
    <div class="max-w-[680px] mx-auto px-6">
      <nav class="mb-8" aria-label="Breadcrumb">
        <ol class="flex items-center gap-2 text-sm text-midGray flex-wrap">
          <li><a href="/" class="hover:text-primary transition-colors">Home</a></li>
          <li class="text-midGray/50">/</li>
          <li><a href="/writers-routines/" class="hover:text-primary transition-colors">Writers' Routines</a></li>
          <li class="text-midGray/50">/</li>
          <li><a href="/writers-routines/{d["author_slug"]}/" class="hover:text-primary transition-colors">{esc(d["author_name"])}</a></li>
          <li class="text-midGray/50">/</li>
          <li class="text-bodyText font-medium">{esc(d["crumb"])}</li>
        </ol>
      </nav>

      <span class="inline-block text-primary text-xs font-semibold uppercase tracking-[0.15em] mb-4">Writers' Routines</span>

      <h1 class="font-serif text-[32px] md:text-[44px] leading-[1.12] font-bold text-dark mb-6">{esc(d["h1"])}</h1>

      <div class="flex items-center gap-4 text-sm text-midGray">
        <span class="font-medium text-bodyText">Kia Orion</span>
        <span class="text-midGray/40">|</span>
        <time datetime="{d["date_iso"]}">{d["date_disp"]}</time>
        <span class="text-midGray/40">|</span>
        <span>{d["read_time"]} min read</span>
      </div>

      <div class="mt-10 h-px bg-gradient-to-r from-primary/30 via-gold/30 to-transparent"></div>
    </div>
  </header>

  <!-- ARTICLE -->
  <article class="pb-16">
    <div class="max-w-[680px] mx-auto px-6 article-body">

      <p>{d["intro"]}</p>

      <div class="answer-box">
        <div class="label">The Direct Answer</div>
        <div class="answer">{d["answer"]}</div>
        <div class="subtext">{d["answer_sub"]}</div>
      </div>

{render_blocks(d["blocks"])}

    </div>
  </article>

  <!-- MORE ROUTINES -->
  <section class="py-16 bg-warmWhite">
    <div class="max-w-[680px] mx-auto px-6">
      <p class="text-xs uppercase tracking-[0.25em] text-primary font-semibold mb-6">More on {esc(d["author_name"])}</p>
      <a href="/writers-routines/{d["author_slug"]}/" class="card-lift block bg-gradient-to-br from-primaryDeep to-primary text-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all mb-4">
        <p class="text-gold font-bold text-xs uppercase tracking-wider mb-2">Full profile</p>
        <p class="font-serif font-bold text-[17px] mb-1">{esc(d["author_name"])}'s Complete Writing Routine &rarr;</p>
        <p class="text-white/70 text-[13px] leading-relaxed">{d["profile_blurb"]}</p>
      </a>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
{related_cards}
      </div>
    </div>
  </section>

  <!-- GENRE QUIZ CTA -->
  <section class="py-10">
    <div class="max-w-[680px] mx-auto px-6">
      <a href="/genre-quiz/" class="card-lift block bg-gradient-to-br from-primaryDeep to-primary text-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all">
        <p class="text-gold font-bold text-xs uppercase tracking-wider mb-2">Free 2-minute quiz</p>
        <p class="font-serif font-bold text-[18px] mb-1">Not sure what genre you should write? &rarr;</p>
        <p class="text-white/70 text-[13px] leading-relaxed">Answer 10 questions and get your genre, a personalized breakdown, and your first writing prompt.</p>
      </a>
    </div>
  </section>

  <!-- BOTTOM CTA -->
  <section id="signup" class="relative overflow-hidden noise-overlay" style="background: linear-gradient(135deg, #091B3A 0%, #0D47A1 100%);">
    <div class="py-24 md:py-32 max-w-[600px] mx-auto px-6 text-center relative z-10">
      <h2 class="font-serif text-[32px] md:text-[44px] leading-[1.1] font-bold text-white mb-6">Stop staring at the blank page. <span class="gradient-text">Start writing with purpose.</span></h2>
      <p class="text-white/50 text-base leading-relaxed max-w-[520px] mx-auto font-light mb-8">A free daily reflection for writers. Quotes from literary masters, an original reflection, and a prompt to get you writing.</p>
      <form action="https://app.convertkit.com/forms/9155962/subscriptions" method="post" class="flex flex-col sm:flex-row gap-3 max-w-[460px] mx-auto mb-4" onsubmit="plausible('signup', {{props: {{source: '{d["author_slug"]}-{d["subslug"]}'}}}})">
        <input type="hidden" name="fields[source_page]" value="writers-routines/{d["author_slug"]}/{d["subslug"]}">
        <input type="hidden" name="fields[genre]" value="Writing Routines">
        <input type="email" name="email_address" placeholder="Your email address" required class="flex-1 px-5 py-3.5 rounded-full border border-white/20 bg-white/10 text-white text-sm placeholder-white/40 focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20 transition-all">
        <button type="submit" class="btn-premium bg-gradient-to-r from-gold to-goldLight text-dark font-bold px-8 py-3.5 rounded-full text-sm whitespace-nowrap">Start My Daily Practice &rarr;</button>
      </form>
      <p class="text-white/40 text-xs font-medium">Join 1,000+ writers. No spam. Unsubscribe anytime.</p>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="relative overflow-hidden noise-overlay" style="background: linear-gradient(135deg, #091B3A 0%, #0D47A1 100%);">
    <div class="py-16 max-w-[800px] mx-auto px-6 text-center relative z-10">
      <a href="/" class="text-white font-serif font-bold text-xl tracking-tight">Kia Orion</a>
      <p class="text-white/40 text-sm mt-3 mb-6">The Writer's Daily Practice &middot; A free daily reflection for writers</p>
      <div class="flex justify-center gap-6 mb-6">
        <a href="/" class="text-white/50 text-sm hover:text-white transition-colors">Home</a>
        <a href="/book/" class="text-white/50 text-sm hover:text-white transition-colors">The Book</a>
        <a href="/genres/" class="text-white/50 text-sm hover:text-white transition-colors">For Writers</a>
        <a href="/about/" class="text-white/50 text-sm hover:text-white transition-colors">About</a>
      </div>
      <p class="text-white/20 text-xs">&copy; 2026 Kia Orion. All rights reserved.</p>
    </div>
  </footer>

  <script defer src="/js/capture.js"></script>
</body>
</html>
'''


def build(d):
    out_dir = os.path.join(ROOT, "writers-routines", d["author_slug"], d["subslug"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "index.html")
    with open(path, "w") as f:
        f.write(render(d))
    return f"/writers-routines/{d['author_slug']}/{d['subslug']}/"


if __name__ == "__main__":
    # Content data passed as a JSON file path: python gen_subpage.py data.json
    data = json.load(open(sys.argv[1]))
    pages = data if isinstance(data, list) else [data]
    for p in pages:
        print("wrote", build(p))
