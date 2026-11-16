#!/usr/bin/env python3
"""B1756 (Nov 15 2026, Claude for Liam): what is live against what the record says.

  python3 live_check.py            # fetch every live page, build fresh in a scratch dir, diff the numerals
  python3 live_check.py --no-build # reuse the last scratch build (faster rerun of the diff only)

Read-only for this repo: the fresh build happens in /tmp/b1756-scratch (a copy of this repo beside symlinks
to every sibling repo), never in site/. Nothing is deployed. Writes only out/live_check_<date>.md and
out/live_check_<date>.csv.

Per page, three copies of the text:
  live    - the page as served now (plain GET)
  pushed  - origin/main's site/ (what the last push deployed)
  fresh   - a plain build of today's code and data (no *_PREVIEW flags, so held sections stay out)
Only sentences with a numeral are compared. Each sentence that differs is classed:
  NOT DEPLOYED    fresh has it, live doesn't, and it is already in the local commits' site/ (built, not pushed)
  DATA MOVED      fresh has it, live doesn't, and no committed build has it (the data or code moved since)
  STALE ON LIVE   live has it, fresh doesn't (the converse of one of the above)
  LIVE != PUSHED  live differs from origin/main's own file (Vercel serving something else - should not happen)
Dates and counters that change on every build (the dateline, 'updated', visit counts) are listed but marked
volatile [C on the volatile rule: sentences matching VOLATILE below].
"""
import html, os, re, subprocess, sys, csv, datetime, urllib.request, pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
PROJ = HERE.parent
SCR = pathlib.Path("/tmp/b1756-scratch")
BASE = "https://providenceontherecord.org"
TODAY = datetime.date.today().isoformat()
UA = "on-the-record live_check (Liam Freaney; providenceontherecord.org)"
NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")
VOLATILE = re.compile(r"(?i)updated|as of|views|visits|generated|last (pulled|built|run)|pulled on|this week")


def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|li|td|th|h[1-6]|div|tr|figcaption|caption)>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    out = []
    for line in t.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        for s in re.split(r"(?<=[.;:!?])\s+(?=[A-Z$(])", line):
            if NUM.search(s):
                out.append(s.strip())
    return out


def fetch(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa
        return f"ERR {type(e).__name__}", ""


def git_show(ref, path):
    r = subprocess.run(["git", "-C", str(HERE), "show", f"{ref}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def scratch_build():
    if SCR.exists():
        shutil.rmtree(SCR)
    SCR.mkdir(parents=True)
    for p in PROJ.iterdir():
        if p.name != HERE.name and not p.name.startswith("."):
            (SCR / p.name).symlink_to(p)
    dst = SCR / HERE.name
    subprocess.run(["rsync", "-a", "--exclude", ".git", "--exclude", "site", str(HERE) + "/", str(dst) + "/"], check=True)
    # seed site/ with the committed tree (static assets the build expects to find), then build over it
    subprocess.run(f"git -C '{HERE}' archive HEAD site | tar -x -C '{dst}'", shell=True, check=True)
    env = {k: v for k, v in os.environ.items() if not k.endswith("_PREVIEW") and k != "OFFER_PREVIEW"}
    r = subprocess.run([sys.executable, "build.py"], cwd=dst, env=env, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        raise SystemExit("live_check: scratch build failed")
    return dst / "site"


def pages(site):
    locs = set()
    for src in [site / "sitemap.xml"]:
        if src.exists():
            locs |= set(re.findall(r"<loc>([^<]+)</loc>", src.read_text()))
    s, live_map = fetch("/sitemap.xml")
    locs |= set(re.findall(r"<loc>([^<]+)</loc>", live_map))
    return sorted(l.replace(BASE, "") or "/" for l in locs)


def main():
    site = (SCR / HERE.name / "site") if "--no-build" in sys.argv else scratch_build()
    subprocess.run(["git", "-C", str(HERE), "fetch", "-q", "origin"], capture_output=True)
    rows, per_page = [], []
    for path in pages(site):
        rel = path.strip("/")
        f = (rel + "/index.html") if rel else "index.html"
        status, live_h = fetch(path)
        fresh_p = site / f
        fresh_h = fresh_p.read_text() if fresh_p.exists() else None
        pushed_h = git_show("origin/main", "site/" + f)
        head_h = git_show("HEAD", "site/" + f)
        L = text_of(live_h) if live_h else []
        F = text_of(fresh_h) if fresh_h else []
        P = set(text_of(pushed_h)) if pushed_h else set()
        H = set(text_of(head_h)) if head_h else set()
        Ls, Fs = set(L), set(F)
        n = 0
        for s in sorted(Fs - Ls):
            cls = "NOT DEPLOYED" if s in H else "DATA MOVED"
            rows.append((path, cls, "fresh", bool(VOLATILE.search(s)), s)); n += 1
        for s in sorted(Ls - Fs):
            cls = "LIVE != PUSHED" if pushed_h is not None and s not in P else "STALE ON LIVE"
            rows.append((path, cls, "live", bool(VOLATILE.search(s)), s)); n += 1
        per_page.append((path, status, len(Ls), len(Fs), fresh_h is not None, pushed_h is not None, n))
    return rows, per_page


def report(rows, per_page):
    out = HERE / "out"; out.mkdir(exist_ok=True)
    with open(out / f"live_check_{TODAY}.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["page", "class", "side", "volatile", "sentence"]); w.writerows(rows)
    real = [r for r in rows if not r[3]]
    by = {}
    for r in real:
        by.setdefault(r[0], []).append(r)
    L = [f"# Live check, {TODAY}", "",
         "providenceontherecord.org as served, against a plain fresh build of today's code and data (scratch; nothing",
         "deployed) and against origin/main's site/. Only sentences that carry a numeral are compared. Script: live_check.py.", "",
         f"Pages: {len(per_page)}. Fetch failures: {sum(1 for p in per_page if p[1] != 200)}. "
         f"Pages with a non-volatile difference: {len(by)}. Differing sentences: {len(real)} "
         f"(plus {len(rows) - len(real)} volatile - dates, counters).", "",
         "| class | sentences |", "|---|---|"]
    for c in ["NOT DEPLOYED", "DATA MOVED", "STALE ON LIVE", "LIVE != PUSHED"]:
        L.append(f"| {c} | {sum(1 for r in real if r[1] == c)} |")
    L += ["", "## Pages that fetch badly or have no fresh build", ""]
    for p in per_page:
        if p[1] != 200 or not p[4]:
            L.append(f"- {p[0]}: live {p[1]}, fresh build {'yes' if p[4] else 'NO'}, in origin/main {'yes' if p[5] else 'no'}")
    L += ["", "## Differences by page (volatile lines left out; all in the csv)", ""]
    for page, rs in by.items():
        L.append(f"### {page}")
        for r in rs:
            L.append(f"- **{r[1]}** ({r[2]}): {r[4][:300]}")
        L.append("")
    L += literals()
    (out / f"live_check_{TODAY}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:16]))


PROSE_NUM = re.compile(r"(?<![\w.{\[%-])(\$\d[\d,.]*\s*(?:million|billion|[KMB])?|\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s?(?:percent|%))")


def literals():
    """Numerals typed into prose in the page modules (string literals with letters around them) that no
    assert in the same file mentions. 'No producer' is a heuristic [C]: a literal may be sourced in a comment
    or be a fixed fact (a statute's rate); the list is for a person to walk, not a verdict."""
    L = ["", "## Numerals typed into page-module prose with no assert beside them [C heuristic]", ""]
    tot = 0
    for py in sorted(HERE.glob("*.py")):
        if py.name in ("live_check.py",):
            continue
        src = py.read_text()
        asserts = " ".join(l for l in src.splitlines() if l.strip().startswith("assert") or "_pin(" in l or "pin(" in l)
        hits = []
        for i, line in enumerate(src.splitlines(), 1):
            st = line.strip()
            if st.startswith("#") or st.startswith("assert") or "CSS" in st:
                continue
            for lit in re.findall(r"(['\"])((?:(?!\1).){12,})\1", line):
                s = lit[1]
                if not re.search(r"[a-z]{3,} [a-z]{3,}", s):
                    continue
                for m in PROSE_NUM.findall(s):
                    if m.strip() and m.strip() not in asserts:
                        hits.append((i, m.strip(), s[:120]))
        if hits:
            tot += len(hits)
            L.append(f"### {py.name} ({len(hits)})")
            L += [f"- line {i}: `{m}` in \"{s}\"" for i, m, s in hits[:25]]
            if len(hits) > 25:
                L.append(f"- ... {len(hits) - 25} more")
            L.append("")
    L.insert(3, f"{tot} in all. Many are fixed facts or dates; the list is for walking, not a verdict.")
    return L


if __name__ == "__main__":
    report(*main())
