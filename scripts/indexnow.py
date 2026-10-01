#!/usr/bin/env python3
"""Push URLs to Bing and the other IndexNow engines.

Bing powers roughly half this site's search traffic (Bing, DuckDuckGo, Yahoo,
Ecosia) and there's no Bing Webmaster Tools account, so this is the direct line
into that index. The key file lives at the site root; IndexNow verifies it
before accepting a submission.

Usage:
  python3 scripts/indexnow.py --all              every URL in the sitemaps
  python3 scripts/indexnow.py --changed HEAD~1   pages whose HTML changed since a git ref
  python3 scripts/indexnow.py URL [URL ...]      specific URLs
  add --dry to print what would be sent
"""
import glob, json, os, re, subprocess, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "writersdailypractice.com"
SITE = f"https://{HOST}"
ENDPOINT = "https://api.indexnow.org/indexnow"


def find_key():
    for f in os.listdir(ROOT):
        if re.fullmatch(r"[0-9a-f]{32}\.txt", f):
            key = open(os.path.join(ROOT, f)).read().strip()
            if key == f[:-4]:
                return key
    sys.exit("no IndexNow key file at the repo root")


def sitemap_urls():
    urls = []
    for m in sorted(glob.glob(os.path.join(ROOT, "sitemap*.xml"))):
        if os.path.basename(m) == "sitemap-index.xml":
            continue
        urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", open(m, encoding="utf-8").read())
    return urls


def changed_urls(ref):
    out = subprocess.run(["git", "diff", "--name-only", ref, "--", "*.html"],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    urls = []
    for f in out:
        if not f.endswith("index.html") or not os.path.exists(os.path.join(ROOT, f)):
            continue
        d = os.path.dirname(f)
        urls.append(f"{SITE}/{d}/" if d else f"{SITE}/")
    return urls


def submit(urls, key, dry=False):
    urls = sorted({u for u in urls if u.startswith(SITE)})
    if not urls:
        print("nothing to submit"); return
    print(f"submitting {len(urls)} URLs to IndexNow")
    if dry:
        for u in urls[:15]:
            print("  ", u)
        if len(urls) > 15:
            print(f"   ... and {len(urls) - 15} more")
        return
    for i in range(0, len(urls), 10000):
        body = json.dumps({"host": HOST, "key": key,
                           "keyLocation": f"{SITE}/{key}.txt",
                           "urlList": urls[i:i + 10000]}).encode()
        req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                print(f"  HTTP {r.status}  ({'accepted' if r.status in (200, 202) else 'unexpected'})")
        except urllib.error.HTTPError as e:
            meaning = {400: "bad request", 403: "key not valid or key file not found",
                       422: "URLs don't match host or key", 429: "rate limited"}.get(e.code, "")
            print(f"  HTTP {e.code}  {meaning}  {e.read().decode()[:200]}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    key = find_key()
    if not args:
        sys.exit(__doc__)
    if args[0] == "--all":
        submit(sitemap_urls(), key, dry)
    elif args[0] == "--changed":
        submit(changed_urls(args[1] if len(args) > 1 else "HEAD~1"), key, dry)
    else:
        submit(args, key, dry)
