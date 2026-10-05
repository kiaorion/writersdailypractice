#!/usr/bin/env python3
"""Read the public Plausible dashboard without a browser or an API key.

The dashboard is public, so the same POST endpoint its own JavaScript calls
answers plain HTTP. Usage:

    python3 scripts/plausible.py                 # last 30 days, everything
    python3 scripts/plausible.py 7d
    python3 scripts/plausible.py 2026-09-01 2026-09-30
"""
import json, sys, urllib.request, datetime

SITE = "writersdailypractice.com"
URL = f"https://plausible.io/api/stats/{SITE}/query/"
BOOK = "https://a.co/d/0aZhyb86"


def q(date_range, dimensions=(), metrics=("visitors",), filters=(), limit=None, compare=False):
    body = {
        "date_range": date_range,
        "relative_date": datetime.date.today().isoformat(),
        "dimensions": list(dimensions),
        "metrics": list(metrics),
        "filters": [list(f) for f in filters],
        "order_by": [[metrics[-1], "desc"]] if dimensions else None,
        "pagination": {"limit": limit, "offset": 0} if limit else None,
        "include": {"imports": True, "compare": "previous_period" if compare else None,
                    "compare_match_day_of_week": True},
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "accept": "application/json",
        "referer": f"https://plausible.io/{SITE}", "user-agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))["results"]


def table(title, rows, width=60):
    print(f"\n{title}")
    for r in rows:
        print(f"  {str(r['dimensions'][0])[:width]:<{width}} {'  '.join(str(m) for m in r['metrics'])}")


def main(argv):
    dr = [argv[0], argv[1]] if len(argv) == 2 else (argv[0] if argv else "30d")
    top = q(dr, metrics=("visitors", "visits", "pageviews", "bounce_rate", "visit_duration"), compare=True)[0]
    names = ("visitors", "visits", "pageviews", "bounce %", "duration s")
    print(f"Plausible, {SITE}, {dr}")
    for n, v, c in zip(names, top["metrics"], top["comparison"]["change"]):
        print(f"  {n:<11} {v:>7}  ({c:+}% vs previous period)")

    table("Sources", q(dr, ["visit:source"], limit=12))
    table("Top pages", q(dr, ["event:page"], limit=20))

    goal = [["is", "event:goal", ["Outbound Link: Click"]]]
    links = q(dr, ["event:props:url"], ("visitors", "events"), goal, limit=200)
    book = [r for r in links if r["dimensions"][0].startswith(BOOK)]
    print(f"\nBook clicks (visitors, clicks): {sum(r['metrics'][0] for r in book)}, {sum(r['metrics'][1] for r in book)}")
    for r in book:
        u = r["dimensions"][0]
        slot = u.split("?p=", 1)[1] if "?p=" in u else "(untagged)"
        print(f"  {slot:<14} {r['metrics'][0]:>4} {r['metrics'][1]:>4}")

    pages = [["is", "event:goal", ["Outbound Link: Click"]], ["contains", "event:props:url", [BOOK]]]
    table("Pages that sent the book clicks", q(dr, ["event:page"], ("visitors", "events"), pages, limit=15))
    table("Goals", q(dr, ["event:goal"], ("visitors", "events"), limit=15))


if __name__ == "__main__":
    main(sys.argv[1:])
