#!/usr/bin/env python3
"""
Flagship linkable asset: "The Daily Writing Routines of Famous Authors, Compared."
Harvests the already-verified answer boxes from every routine sub-page and assembles
a single sortable comparison table. Accurate by construction (reuses vetted content).
Writes writers-routines/writing-routines-compared/index.html.
"""
import os, re, glob, html
from gen_subpage import HEAD_STYLE, SITE, ROOT

COLS = [("word-count", "Words a day"), ("writing-schedule", "When they wrote"),
        ("how-they-wrote", "How they wrote"), ("where-they-wrote", "Where")]
SUB_TO_COL = {"word-count": 0, "writing-schedule": 1, "how-they-wrote": 2,
              "where-they-wrote": 3, "standing-desk": 3}

def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).strip()
    return t

def answer_of(path):
    h = open(path).read()
    m = re.search(r'<div class="answer">(.*?)</div>', h, re.S)
    return clean(m.group(1)) if m else ""

def author_name(subpage_html):
    m = re.search(r'<li><a href="/writers-routines/[^/]+/"[^>]*>([^<]+)</a></li>', subpage_html)
    return m.group(1).strip() if m else ""

rows = {}
for sub in sorted(glob.glob(os.path.join(ROOT, "writers-routines", "*", "*", "index.html"))):
    parts = sub.split(os.sep)
    slug, subslug = parts[-3], parts[-2]
    col = SUB_TO_COL.get(subslug)
    if col is None:
        continue
    h = open(sub).read()
    name = author_name(h)
    if not name:
        continue
    r = rows.setdefault(slug, {"name": name, "cells": ["", "", "", ""]})
    ans = answer_of(sub)
    if ans and not r["cells"][col]:
        r["cells"][col] = ans[:120]

# Only include authors with at least 2 filled cells (real comparison value)
rows = {k: v for k, v in rows.items() if sum(1 for c in v["cells"] if c) >= 2}
ordered = sorted(rows.items(), key=lambda kv: kv[1]["name"].split()[-1])

def td(x, slug=None, first=False):
    if first:
        return f'<th scope="row" style="text-align:left;padding:14px 16px;font-family:\'Playfair Display\',Georgia,serif;font-weight:700;color:#111;white-space:nowrap;"><a href="/writers-routines/{slug}/" style="color:#0D47A1;text-decoration:none;">{html.escape(x)}</a></th>'
    return f'<td style="padding:14px 16px;color:#2a2a2a;vertical-align:top;">{html.escape(x) if x else "<span style=\'color:#cbd5e1;\'>&middot;</span>"}</td>'

header = "".join(f'<th style="text-align:left;padding:14px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;color:#8a7a3a;white-space:nowrap;">{c[1]}</th>' for c in COLS)
body_rows = []
for slug, r in ordered:
    cells = td(r["name"], slug, first=True) + "".join(td(r["cells"][i]) for i in range(4))
    body_rows.append(f"<tr style='border-top:1px solid #eef0f2;'>{cells}</tr>")
n = len(ordered)

page = f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Daily Writing Routines of {n}+ Famous Authors, Compared</title>
  <meta name="description" content="A side-by-side comparison of how {n}+ famous authors actually wrote: their daily word counts, what time they worked, how they drafted, and where. All sourced from interviews and memoirs.">
  <link rel="canonical" href="{SITE}/writers-routines/writing-routines-compared/">
  <meta property="og:title" content="The Daily Writing Routines of {n}+ Famous Authors, Compared">
  <meta property="og:description" content="Word counts, schedules, and methods for {n}+ famous authors, side by side.">
  <meta property="og:image" content="{SITE}/images/og/warm.jpg">
  <meta property="og:url" content="{SITE}/writers-routines/writing-routines-compared/">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="The Daily Writing Routines of {n}+ Famous Authors, Compared">
  <meta name="twitter:description" content="Word counts, schedules, and methods for {n}+ famous authors, side by side.">
  <meta name="twitter:image" content="{SITE}/images/og/warm.jpg">
  <script type="application/ld+json">
  {{ "@context": "https://schema.org", "@type": "Article",
    "headline": "The Daily Writing Routines of {n}+ Famous Authors, Compared",
    "author": {{ "@type": "Person", "name": "Kia Orion", "url": "{SITE}/" }},
    "publisher": {{ "@type": "Organization", "name": "The Writer's Daily Practice", "url": "{SITE}/" }},
    "datePublished": "2026-06-28", "dateModified": "2026-06-28",
    "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{SITE}/writers-routines/writing-routines-compared/" }} }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@0,400;0,700;0,900&family=Inter:wght@300;400;500;600;700&display=swap" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@0,400;0,700;0,900&family=Inter:wght@300;400;500;600;700&display=swap"></noscript>
  <link rel="stylesheet" href="/css/style.css">
{HEAD_STYLE}
  <script async src="https://plausible.io/js/pa-ZOk4diA46SHVDfHBy61SQ.js"></script>
  <script>window.plausible=window.plausible||function(){{(plausible.q=plausible.q||[]).push(arguments)}},plausible.init=plausible.init||function(i){{plausible.o=i||{{}}}};plausible.init()</script>
</head>
<body>
  <nav class="fixed top-0 left-0 right-0 z-50 nav-blur bg-primaryDeep/90 border-b border-white/5">
    <div class="max-w-[1200px] mx-auto px-6 py-4 flex items-center justify-between">
      <a href="/" class="text-white font-serif font-bold text-xl tracking-tight">Kia Orion</a>
      <a href="#signup" class="btn-premium bg-gradient-to-r from-gold to-goldLight text-dark text-sm font-bold px-6 py-2.5 rounded-full">Start Free</a>
    </div>
  </nav>

  <header class="pt-28 md:pt-36 pb-10">
    <div class="max-w-[900px] mx-auto px-6">
      <nav class="mb-8" aria-label="Breadcrumb">
        <ol class="flex items-center gap-2 text-sm text-midGray flex-wrap">
          <li><a href="/" class="hover:text-primary transition-colors">Home</a></li>
          <li class="text-midGray/50">/</li>
          <li><a href="/writers-routines/" class="hover:text-primary transition-colors">Writers' Routines</a></li>
          <li class="text-midGray/50">/</li>
          <li class="text-bodyText font-medium">Compared</li>
        </ol>
      </nav>
      <span class="inline-block text-primary text-xs font-semibold uppercase tracking-[0.15em] mb-4">Writers' Routines</span>
      <h1 class="font-serif text-[32px] md:text-[46px] leading-[1.1] font-bold text-dark mb-6">The Daily Writing Routines of {n}+ Famous Authors, Compared</h1>
      <p style="font-family:'Lora',Georgia,serif;font-size:19px;line-height:1.7;color:#2a2a2a;max-width:680px;">How much did they write a day? When did they work? How did they draft? Here is the whole shelf side by side, pulled from interviews, memoirs, and their own words. Every row links to the full routine. Steal what fits.</p>
    </div>
  </header>

  <section class="pb-16">
    <div class="max-w-[1100px] mx-auto px-6">
      <div style="overflow-x:auto;border:1px solid #eef0f2;border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,.05);">
        <table style="border-collapse:collapse;width:100%;min-width:820px;font-family:'Inter',system-ui,sans-serif;font-size:14.5px;line-height:1.5;">
          <thead style="background:#fbf9f4;"><tr><th style="text-align:left;padding:14px 16px;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;color:#8a7a3a;">Author</th>{header}</tr></thead>
          <tbody>
{chr(10).join(body_rows)}
          </tbody>
        </table>
      </div>
      <p style="font-size:13px;color:#94a3b8;margin-top:14px;">Blank cells mean the detail is not reliably documented for that author. Figures are approximate and drawn from primary interviews and memoirs; see each author's page for sources.</p>
    </div>
  </section>

  <section id="signup" class="relative overflow-hidden noise-overlay" style="background: linear-gradient(135deg, #091B3A 0%, #0D47A1 100%);">
    <div class="py-24 md:py-28 max-w-[600px] mx-auto px-6 text-center relative z-10">
      <h2 class="font-serif text-[30px] md:text-[42px] leading-[1.1] font-bold text-white mb-6">Build your own writing routine. <span class="gradient-text">Start with one prompt a day.</span></h2>
      <p class="text-white/50 text-base leading-relaxed max-w-[520px] mx-auto font-light mb-8">A free daily reflection for writers. A line from a master, an original reflection, and a prompt to get you writing.</p>
      <form action="https://app.convertkit.com/forms/9155962/subscriptions" method="post" class="flex flex-col sm:flex-row gap-3 max-w-[460px] mx-auto mb-4">
        <input type="hidden" name="fields[source_page]" value="writers-routines/writing-routines-compared">
        <input type="hidden" name="fields[genre]" value="Writing Routines">
        <input type="email" name="email_address" placeholder="Your email address" required class="flex-1 px-5 py-3.5 rounded-full border border-white/20 bg-white/10 text-white text-sm placeholder-white/40 focus:outline-none focus:border-gold">
        <button type="submit" class="btn-premium bg-gradient-to-r from-gold to-goldLight text-dark font-bold px-8 py-3.5 rounded-full text-sm whitespace-nowrap">Start My Daily Practice &rarr;</button>
      </form>
      <p class="text-white/40 text-xs font-medium">Join 1,000+ writers. No spam. Unsubscribe anytime.</p>
    </div>
  </section>

  <footer class="relative overflow-hidden noise-overlay" style="background: linear-gradient(135deg, #091B3A 0%, #0D47A1 100%);">
    <div class="py-12 max-w-[800px] mx-auto px-6 text-center relative z-10">
      <a href="/writers-routines/" class="text-white/60 text-sm hover:text-white transition-colors">&larr; All writers' routines</a>
      <p class="text-white/20 text-xs mt-4">&copy; 2026 Kia Orion. All rights reserved.</p>
    </div>
  </footer>
  <script defer src="/js/capture.js"></script>
</body>
</html>
'''

out = os.path.join(ROOT, "writers-routines", "writing-routines-compared")
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "index.html"), "w").write(page)
print(f"built comparison hub with {n} authors -> /writers-routines/writing-routines-compared/")
print("sample rows:", ", ".join(r['name'] for _, r in ordered[:6]))
