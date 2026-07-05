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


# ---------- Plausible (official Stats API v2) ----------
# NOTE: Plausible removed the undocumented public-dashboard endpoints we used to
# scrape (they 404 as of 2026-07-05). Historical stats now live behind the official
# /api/v2/query API, which needs a key. current-visitors still works, proving the
# dashboard is public and collecting; only the free historical route closed.
def _plausible_key():
    try:
        txt = open(KEYS).read()
    except Exception:
        return None
    m = re.search(r"PLAUSIBLE_API_KEY[`*:=\s]+([A-Za-z0-9_\-./+=]{20,})", txt)
    return m.group(1) if m else None

def plausible_section():
    key = _plausible_key()
    if not key:
        return ("### Plausible\n\n_Unavailable: Plausible retired the old public-dashboard endpoints "
                "(they 404 now). The site is still collecting data and the dashboard is still public; "
                "only the free scrape route closed. Fix: add `PLAUSIBLE_API_KEY: <key>` to "
                "~/.claude/api-keys.md (Plausible > Settings > API Keys, included in the plan) and this "
                "section switches to the official v2 API._"), None
    H = {"Authorization": "Bearer " + key}
    def query(body):
        return http_json("https://plausible.io/api/v2/query", data={**body, "site_id": DOMAIN}, headers=H)
    tot = query({"metrics": ["visitors", "pageviews", "bounce_rate", "visit_duration"], "date_range": "30d"})
    if not (isinstance(tot, dict) and tot.get("results")):
        return f"_Plausible v2 API error: {tot}._", None
    v, pv, bounce, dur = tot["results"][0]["metrics"]
    goals = query({"metrics": ["visitors", "events"], "date_range": "30d", "dimensions": ["event:goal"]})
    out = ["### Plausible (all traffic, last 30d)\n"]
    out.append(f"**Unique visitors: {v:,}** (~{round(v/30)}/day) | Pageviews: {pv:,} | "
               f"Bounce: {round(bounce)}% | Avg visit: {int(dur//60)}m{int(dur%60):02d}s\n")
    out.append("| Goal | Visitors | Events | Conv. rate |")
    out.append("|---|---|---|---|")
    for row in sorted(goals.get("results", []), key=lambda r: -r["metrics"][0]):
        name = row["dimensions"][0]; gv, ge = row["metrics"]
        out.append(f"| {name} | {gv} | {ge} | {(gv/v*100 if v else 0):.1f}% |")
    return "\n".join(out), v


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
