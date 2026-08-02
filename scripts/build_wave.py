#!/usr/bin/env python3
"""
Build a wave of author sub-pages from agent JSON outputs.
- Validates each JSON file (schema + house-style: no em/en dashes).
- Stamps pages via gen_subpage.build().
- Inserts an idempotent "Quick answers about <Author>" block into each parent.
- Appends new URLs to sitemap-posts.xml (deduped).
Usage: python3 scripts/build_wave.py <wave_dir>
"""
import os, re, sys, json, glob
from datetime import date
from gen_subpage import build, ROOT

WAVE_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
SITEMAP = os.path.join(ROOT, "sitemap-posts.xml")
REQUIRED = {"author_slug","author_name","subslug","date_iso","date_disp","read_time","crumb",
            "title","meta_desc","og_title","og_desc","tw_desc","h1","intro","answer","answer_sub",
            "blocks","faq","profile_blurb","related_cards"}
DASHES = ["—", "–"]  # em, en

def dash_scan(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return [d for d in DASHES if d in s]

def quick_answers_block(author_name, items):
    cards = "\n".join(
        f'''        <a href="/writers-routines/{it['slug']}/{it['subslug']}/" class="card-lift block bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-primary/20 transition-colors">
          <p class="text-primary font-bold text-xs uppercase tracking-wider mb-1">{it['crumb']}</p>
          <p class="font-serif font-bold text-dark text-[15px]">{it['q']} &rarr;</p>
        </a>''' for it in items)
    return f'''  <!-- WDC-QUICK-ANSWERS -->
  <section class="py-12">
    <div class="max-w-[680px] mx-auto px-6">
      <p class="text-xs uppercase tracking-[0.25em] text-primary font-semibold mb-6">Quick answers about {author_name}</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
{cards}
      </div>
    </div>
  </section>

'''

def card_html(it):
    return f'''        <a href="/writers-routines/{it['slug']}/{it['subslug']}/" class="card-lift block bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:border-primary/20 transition-colors">
          <p class="text-primary font-bold text-xs uppercase tracking-wider mb-1">{it['crumb']}</p>
          <p class="font-serif font-bold text-dark text-[15px]">{it['q']} &rarr;</p>
        </a>'''


def insert_parent(slug, author_name, items):
    """Link new sub-pages from the author hub.

    A hub that already has a quick-answers grid gets the new cards appended to it.
    The old behaviour skipped those hubs outright, which silently orphaned every
    page in the wave: built, in the sitemap, and linked from nowhere.
    """
    p = os.path.join(ROOT, "writers-routines", slug, "index.html")
    if not os.path.exists(p): return f"  ! parent missing: {slug}"
    html = open(p).read()

    # Don't re-add a card that's already on the page (idempotent per sub-page).
    fresh = [it for it in items
             if f'href="/writers-routines/{it["slug"]}/{it["subslug"]}/"' not in html]
    if not fresh:
        return f"  = {slug} all {len(items)} card(s) already present"

    # Append into an existing grid if there is one. Matches both the generated
    # block and the hand-written "Quick answers about ..." sections.
    marker = html.find("<!-- WDC-QUICK-ANSWERS -->")
    if marker == -1:
        m = re.search(r'Quick answers about [^<]*</p>', html)
        marker = m.start() if m else -1
    if marker != -1:
        g = html.find('class="grid grid-cols-1 sm:grid-cols-2 gap-4">', marker)
        if g != -1:
            close = html.find("\n      </div>", g)
            if close != -1:
                add = "\n" + "\n".join(card_html(it) for it in fresh)
                html = html[:close] + add + html[close:]
                open(p, "w").write(html)
                return f"  + {slug} appended {len(fresh)} card(s) to existing grid"

    block = quick_answers_block(author_name, fresh)
    for anchor in ["  <!-- MORE ROUTINES -->", "  <!-- BOTTOM CTA -->", '  <section id="signup"', "  <!-- FOOTER -->"]:
        i = html.find(anchor)
        if i != -1:
            html = html[:i] + block + html[i:]
            open(p, "w").write(html)
            return f"  + {slug} new block, {len(fresh)} card(s) (before {anchor.strip()})"
    return f"  ! {slug} no anchor found, parent NOT linked"

def update_sitemap(urls):
    xml = open(SITEMAP).read()
    existing = set(re.findall(r"<loc>(.*?)</loc>", xml))
    new = [u for u in urls if u not in existing]
    if not new: return 0
    # Stamp today, not a hardcoded date. A stale lastmod tells Google the page
    # hasn't changed and suppresses recrawl, which is what left 1041 URLs
    # claiming an April date on July content.
    stamp = date.today().isoformat()
    entries = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{stamp}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
        for u in new)
    xml = xml.replace("</urlset>", entries + "</urlset>")
    open(SITEMAP, "w").write(xml)
    return len(new)

def main():
    files = sorted(glob.glob(os.path.join(WAVE_DIR, "*.json")))
    print(f"found {len(files)} author files\n")
    by_author = {}
    all_urls = []
    problems = []
    built = 0
    for f in files:
        name = os.path.basename(f)
        try:
            pages = json.load(open(f))
        except Exception as e:
            problems.append(f"{name}: INVALID JSON ({e})"); continue
        if not isinstance(pages, list): pages = [pages]
        for pg in pages:
            missing = REQUIRED - set(pg.keys())
            if missing:
                problems.append(f"{name}/{pg.get('subslug','?')}: missing {missing}"); continue
            d = dash_scan(pg)
            if d:
                problems.append(f"{name}/{pg['subslug']}: DASH found {d}"); continue
            url = build(pg); built += 1
            all_urls.append("https://writersdailypractice.com" + url)
            by_author.setdefault((pg["author_slug"], pg["author_name"]), []).append(
                {"slug": pg["author_slug"], "subslug": pg["subslug"], "crumb": pg["crumb"], "q": pg["og_title"]})
            print(f"  built {url}")
    print(f"\n=== parents ===")
    for (slug, an), items in by_author.items():
        print(insert_parent(slug, an, items))
    n = update_sitemap(all_urls)
    print(f"\nsitemap: +{n} urls")
    print(f"built {built} pages across {len(by_author)} authors")
    if problems:
        print("\n!!! PROBLEMS:")
        for p in problems: print("   ", p)
    else:
        print("\nno problems.")

if __name__ == "__main__":
    main()
