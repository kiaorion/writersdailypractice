#!/usr/bin/env python3
"""
WDC weekly performance report.

Pulls three live sources and writes reports/weekly-YYYY-MM-DD.md:
  - Google Search Console (Google search slice ~14% of traffic): clicks, impressions,
    CTR, position, week-over-week and 28d month-over-month, top queries + pages.
  - Plausible (all traffic, public dashboard, no key): goal conversions; total
    visitors back-solved from goal conversion_rate.
  - ConvertKit (Kit): total subscribers + WDC form 9155962 active + new-this-week.

Tracks every run against the goal: 10 signups/day, which at the current ~1.5%
visitor->signup rate means ~670 visitors/day.

Stdlib only (urllib). Reads creds locally:
  - GSC refresh token: MAIN BRAIN/Business/clients/WDC/cowork-index-wave3.md
  - ConvertKit secret: ~/.claude/api-keys.md (CONVERTKIT_API_SECRET)
Run: python3 scripts/weekly_report.py
"""
import os, re, json, urllib.request, urllib.parse, urllib.error
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
GSC_CRED = os.path.join(HOME, "CLAUDE CODE PARENT", "MAIN BRAIN", "Business", "clients", "WDC", "cowork-index-wave3.md")
KEYS = os.path.join(HOME, ".claude", "api-keys.md")
SITE = "https://writersdailypractice.com/"
DOMAIN = "writersdailypractice.com"
GOAL_SIGNUPS_PER_DAY = 10
CONV_RATE = 0.015  # current visitor -> signup rate
GOAL_VISITORS_PER_DAY = round(GOAL_SIGNUPS_PER_DAY / CONV_RATE)

TODAY = date.today()
def d(n): return (TODAY - timedelta(days=n)).isoformat()


def http_json(url, data=None, headers=None, form=False, method=None):
    h = dict(headers or {})
    body = None
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode(); h.setdefault("Content-Type", "application/x-www-form-urlencoded")
        else:
            body = json.dumps(data).encode(); h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, headers=h, method=method or ("POST" if body else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:300]}
    except Exception as e:
        return {"_error": str(e)}


# ---------- GSC ----------
def gsc_section():
    try:
        txt = open(GSC_CRED).read()
        cid = re.search(r"client_id=([0-9A-Za-z\-]+\.apps\.googleusercontent\.com)", txt).group(1)
        csec = re.search(r"client_secret=(GOCSPX-[0-9A-Za-z_\-]+)", txt).group(1)
        rtok = re.search(r"refresh_token=([0-9A-Za-z_\-/.]+)", txt).group(1)
    except Exception as e:
        return f"_Search Console unavailable (creds not found: {e})._"
    tok = http_json("https://oauth2.googleapis.com/token",
                    {"client_id": cid, "client_secret": csec, "refresh_token": rtok, "grant_type": "refresh_token"}, form=True)
    if "access_token" not in tok:
        return f"_Search Console auth failed: {tok}._"
    H = {"Authorization": "Bearer " + tok["access_token"]}
    enc = urllib.parse.quote(SITE, safe="")
    def q(start, end, dims=None, rl=25):
        b = {"startDate": start, "endDate": end, "rowLimit": rl}
        if dims: b["dimensions"] = dims
        return http_json(f"https://searchconsole.googleapis.com/webmasters/v3/sites/{enc}/searchAnalytics/query", b, H)
    def tot(s, e):
        rows = q(s, e).get("rows", [])
        if not rows: return None
        x = rows[0]; return (x["clicks"], x["impressions"], x["ctr"]*100, x["position"])
    tw, pw = tot(d(7), d(1)), tot(d(14), d(8))
    m, pm = tot(d(28), d(1)), tot(d(56), d(29))
    out = ["### Google Search (GSC — the ~14% Google slice)\n"]
    out.append("| Window | Clicks | Impressions | CTR | Avg position |")
    out.append("|---|---|---|---|---|")
    for lbl, t in [("This week (7d)", tw), ("Prior week", pw), ("Last 28d", m), ("Prior 28d", pm)]:
        if t: out.append(f"| {lbl} | {t[0]:.0f} | {t[1]:.0f} | {t[2]:.2f}% | {t[3]:.1f} |")
        else: out.append(f"| {lbl} | (no data) | | | |")
    if m and pm and pm[1]:
        out.append(f"\n_Month over month: impressions {((m[1]-pm[1])/pm[1]*100):+.0f}%, clicks {((m[0]-pm[0])/max(pm[0],1)*100):+.0f}%, position {pm[3]:.1f} -> {m[3]:.1f}._")
    qr = sorted(q(d(28), d(1), ["query"], 100).get("rows", []), key=lambda z: -z["impressions"])[:10]
    out.append("\n**Top queries (28d):**")
    for x in qr:
        out.append(f"- {x['impressions']:.0f} impr, {x['clicks']:.0f} clk, pos {x['position']:.1f} — {x['keys'][0]}")
    pg = sorted(q(d(28), d(1), ["page"], 100).get("rows", []), key=lambda z: -z["impressions"])[:12]
    out.append("\n**Top pages (28d):**")
    for x in pg:
        out.append(f"- {x['impressions']:.0f} impr, {x['clicks']:.0f} clk, pos {x['position']:.1f} — {x['keys'][0].replace('https://writersdailypractice.com','')}")
    return "\n".join(out)


# ---------- Plausible ----------
def plausible_section():
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"
    H = {"User-Agent": ua, "Referer": f"https://plausible.io/{DOMAIN}"}
    r = http_json(f"https://plausible.io/api/stats/{DOMAIN}/conversions/?period=30d", headers=H)
    if "results" not in r:
        return f"_Plausible unavailable: {r}._", None
    results = r["results"]
    # back-solve total visitors from any goal with a rate
    visitors = None
    for g in results:
        if g.get("conversion_rate") and g.get("visitors"):
            visitors = round(g["visitors"] / (g["conversion_rate"]/100)); break
    out = [f"### Plausible (all traffic, 30d — {r.get('meta',{}).get('date_range_label','')})\n"]
    if visitors: out.append(f"**Estimated unique visitors (30d): ~{visitors:,}**  (~{round(visitors/30)}/day)\n")
    out.append("| Goal | Visitors | Events | Conv. rate |")
    out.append("|---|---|---|---|")
    for g in results:
        out.append(f"| {g['name']} | {g.get('visitors',0)} | {g.get('events',0)} | {g.get('conversion_rate',0)}% |")
    return "\n".join(out), visitors


# ---------- ConvertKit ----------
def ck_section():
    try:
        sec = re.search(r"CONVERTKIT_API_SECRET[`*: =]+([A-Za-z0-9_\-]{30,})", open(KEYS).read()).group(1)
    except Exception as e:
        return "_ConvertKit unavailable (secret not found)._", None
    base = "https://api.convertkit.com/v3"
    total = http_json(f"{base}/subscribers?api_secret={sec}&per_page=1").get("total_subscribers")
    formact = http_json(f"{base}/forms/9155962/subscriptions?api_secret={sec}&subscriber_state=active&per_page=1").get("total_subscriptions")
    new7 = http_json(f"{base}/subscribers?api_secret={sec}&from={d(7)}&to={d(0)}&per_page=1").get("total_subscribers")
    new28 = http_json(f"{base}/subscribers?api_secret={sec}&from={d(28)}&to={d(0)}&per_page=1").get("total_subscribers")
    out = ["### ConvertKit (email capture)\n"]
    out.append(f"- Total active subscribers (account): **{total}**")
    out.append(f"- WDC form 9155962 active: **{formact}**")
    out.append(f"- New this week (7d): **{new7}**   |   New last 28d: **{new28}**")
    return "\n".join(out), new7


def main():
    gsc = gsc_section()
    plaus, visitors = plausible_section()
    ck, new7 = ck_section()

    # goal tracking
    vpd = round(visitors/30) if visitors else None
    spd = round((new7 or 0)/7, 2)
    goal = ["### Goal tracking\n"]
    goal.append(f"Target: **{GOAL_SIGNUPS_PER_DAY} signups/day** (~{GOAL_VISITORS_PER_DAY} visitors/day at the current ~{CONV_RATE*100:.1f}% rate).\n")
    goal.append("| Metric | Now | Goal | Gap |")
    goal.append("|---|---|---|---|")
    if vpd: goal.append(f"| Visitors/day | ~{vpd} | {GOAL_VISITORS_PER_DAY} | {GOAL_VISITORS_PER_DAY/max(vpd,1):.0f}x to go |")
    goal.append(f"| Signups/day | ~{spd} | {GOAL_SIGNUPS_PER_DAY} | {GOAL_SIGNUPS_PER_DAY/max(spd,0.1):.0f}x to go |")

    report = f"""# WDC Weekly Report — {TODAY.isoformat()}

_Auto-generated by scripts/weekly_report.py. Sources: Google Search Console, Plausible (public), ConvertKit._

{chr(10).join(goal)}

{plaus}

{ck}

{gsc}
"""
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"weekly-{TODAY.isoformat()}.md")
    with open(path, "w") as f:
        f.write(report)
    print("wrote", path)
    print("---")
    print(report)


if __name__ == "__main__":
    main()
