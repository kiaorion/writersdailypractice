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

def insert_parent(slug, author_name, items):
    p = os.path.join(ROOT, "writers-routines", slug, "index.html")
    if not os.path.exists(p): return f"  ! parent missing: {slug}"
    html = open(p).read()
    if "WDC-QUICK-ANSWERS" in html: return f"  = {slug} parent already linked (skip)"
    block = quick_answers_block(author_name, items)
    for anchor in ["  <!-- MORE ROUTINES -->", "  <!-- BOTTOM CTA -->", '  <section id="signup"', "  <!-- FOOTER -->"]:
        i = html.find(anchor)
        if i != -1:
            html = html[:i] + block + html[i:]
            open(p, "w").write(html)
            return f"  + {slug} parent linked (before {anchor.strip()})"
    return f"  ! {slug} no anchor found, parent NOT linked"

def update_sitemap(urls):
    xml = open(SITEMAP).read()
    existing = set(re.findall(r"<loc>(.*?)</loc>", xml))
    new = [u for u in urls if u not in existing]
    if not new: return 0
    entries = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>2026-06-28</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
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
