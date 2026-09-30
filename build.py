#!/usr/bin/env python3
"""Providence, on the record — the umbrella site for Liam Freaney's public-record
projects. Static build: site/index.html (home) and site/off-the-roll/ (Off the Roll),
rendered from ../untaxed/data. Design: the approved paper-and-ink system
(Source Serif 4 / Public Sans / Roboto Mono; record red only where it means something).
"""
import json, csv, html, shutil, pathlib, datetime, re
HERE = pathlib.Path(__file__).parent
SITE = HERE / "site"
U = HERE.parent / "untaxed" / "data"
DATELINE = "PROVIDENCE · SEPT. 30, 2026"

def money(x, d=1):
    x = float(x)
    if abs(x) >= 1e9: return f"${x/1e9:.{d+1}f}B"
    if abs(x) >= 1e6: return f"${x/1e6:.{d}f}M"
    if abs(x) >= 1e3: return f"${x/1e3:,.0f}K"
    return f"${x:,.0f}"
e = html.escape
KEEP = {"LLC","LP","L.P.","CV","BAC","CVP","WCM-MP","II","III","RI","RWMC,LLC","SJHSRI","CBWC","PO","CC","EM","N"}
def tc(s):
    return " ".join(w if w in KEEP else w.capitalize() for w in s.split())

CSS = """
:root{--paper:#f7f5f0;--raised:#fff;--rule:#d9d4ca;--ink:#16181b;--muted:#5c5f66;--record:#b3261e;
--record-soft:#f6e3e0;--harbor:#1f4e6b;--harbor-soft:#e1ebf1;
--serif:"Source Serif 4",Georgia,"Times New Roman",serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
--mono:"Roboto Mono",ui-monospace,Menlo,monospace}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:400 18px/29px var(--serif)}
a{color:var(--harbor)}a:hover{color:var(--ink)}
.wrap{max-width:760px;margin:0 auto;padding:0 24px}
header.mast{border-bottom:1px solid var(--rule);padding:20px 0 14px}
header.mast a.name{font:600 24px/30px var(--serif);color:var(--ink);text-decoration:none}
header.mast .tag{font:500 13px/18px var(--sans);color:var(--muted);margin-top:2px}
nav.sections{font:500 14px/20px var(--sans);display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:10px}
nav.sections a{text-decoration:none}
.dateline{font:700 12px/16px var(--sans);letter-spacing:.06em;color:var(--record);margin:40px 0 8px}
h1{font:600 34px/40px var(--serif);margin:0 0 12px}
.deck{font:400 20px/28px var(--serif);color:var(--ink);margin:0 0 24px}
.byline{font:500 14px/20px var(--sans);color:var(--muted);margin:0 0 24px}
h2{font:600 24px/30px var(--serif);margin:40px 0 12px;padding-top:24px;border-top:1px solid var(--rule)}
p{margin:0 0 16px}
.cite{font:400 13px/20px var(--mono);color:var(--muted)}
.tag{display:inline-block;font:700 11px/16px var(--sans);letter-spacing:.06em;padding:2px 6px;border-radius:2px}
.tag.model{background:var(--harbor-soft);color:var(--harbor)}
.tablewrap{overflow-x:auto;margin:0 -24px 16px;padding:0 24px}
table{border-collapse:collapse;width:100%;font:400 14px/20px var(--sans)}
th{font-weight:700;text-align:left;border-bottom:1px solid var(--ink);padding:6px 10px 6px 0;vertical-align:bottom}
td{border-bottom:1px solid var(--rule);padding:6px 10px 6px 0;vertical-align:top}
td.n,th.n{text-align:right;font-family:var(--mono);font-size:13px;white-space:nowrap}
tr.total td{border-top:1px solid var(--ink);font-weight:700}
.big{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:0 0 24px}
.big div{border-top:1px solid var(--ink);padding-top:8px}
.big b{display:block;font:600 30px/36px var(--serif)}
.big span{display:block;font:500 13px/18px var(--sans);color:var(--muted)}
.open{background:var(--raised);border:1px solid var(--rule);padding:16px}
.open li{margin-bottom:8px}
.feed article{border-top:1px solid var(--rule);padding:24px 0}
.feed h3{font:600 26px/32px var(--serif);margin:4px 0 8px}
.feed h3 a{color:var(--ink);text-decoration:none}
.feed .kicker{font:700 12px/16px var(--sans);letter-spacing:.06em;color:var(--muted)}
footer{border-top:1px solid var(--rule);margin-top:40px;padding:20px 0 40px;font:400 13px/20px var(--sans);color:var(--muted)}
@media (min-width:720px){h1{font-size:44px;line-height:48px}.big{grid-template-columns:repeat(4,minmax(0,1fr))}}
"""
HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;700&family=Roboto+Mono&family=Source+Serif+4:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css"></head><body>
<div class="wrap"><header class="mast"><a class="name" href="{root}">Providence, on the record</a>
<div class="tag">Liam Freaney · reporting built on the public record</div>
<nav class="sections"><a href="{root}off-the-roll/">Off the Roll</a><a href="{root}downtown-ledger/">Downtown Ledger</a>
<a href="{root}inside-the-line/">Inside the Line</a><a href="https://providenceontherecord.substack.com">Reporting</a></nav></header>
"""
FOOT = """<footer>Every figure on this site comes from a public record, named where it is used. Corrections go at the top of the page they correct, dated.
Nothing here is opinion. Where a number is a model rather than a record, it is labeled <span class="tag model">MODEL</span>.</footer></div></body></html>"""

def page(title, desc, root, body):
    return HEAD.format(title=e(title), desc=e(desc), root=root) + body + FOOT

# ---------------------------------------------------------------- data
roll = json.load(open(U / "roll-summary.json"))
groups = json.load(open(U / "exempt-groups.json"))
tsa = json.load(open(U / "tsa-ledger.json"))
inc = json.load(open(U / "incidence.json"))
inst = list(csv.DictReader(open(U / "institutions.csv")))
sp = json.load(open(U / "state-pilot.json"))
rep = json.load(open(U / "tsa-report-fy2025.json"))
pil = json.load(open(U / "pilots.json"))
T = roll["totals"]; R = roll["by_regime"]

# ---------------------------------------------------------------- untaxed page
b = []
b.append(f'<main><div class="dateline">{DATELINE}</div>')
b.append(f'<h1>${T["exempt"]/1e9:.1f} Billion of Providence&#8217;s ${T["assessed"]/1e9:.0f} Billion in Property Is Exempt From Full Taxation</h1>')
b.append(f'<p class="deck">Colleges, hospitals, government, churches, a shopping mall and 80 owners under tax agreements pay the City less than the full rate. The rest of the city&#8217;s taxpayers carry the {money(T["taxes"],1)} levy.</p>')
b.append('<p class="byline">By Liam Freaney · Off the Roll · from the City&#8217;s 2025 tax roll</p>')
b.append('<div class="big">'
         f'<div><b>{T["exempt"]/T["assessed"]:.0%}</b><span>of assessed value exempt</span></div>'
         f'<div><b>{money(R["fully exempt"]["exempt"],1)}</b><span>fully exempt, {R["fully exempt"]["parcels"]:,} parcels</span></div>'
         f'<div><b>{money(tsa["abated"],1)}</b><span>abated under tax stabilization agreements, one year</span></div>'
         f'<div><b>{money(T["taxes"],1)}</b><span>levied on everyone else</span></div></div>')

b.append('<h2>Four ways property comes off the roll</h2>')
b.append('<p>The City&#8217;s 2025 roll lists every parcel with its assessed value, the part exempt from tax and the tax billed. Each reduced parcel falls under one of four regimes.</p>')
rows = [("Fully exempt: schools, hospitals, government, churches, charities", R["fully exempt"]),
        ("Tax stabilization agreements (RIGL 44-3-9)", R["tax stabilization agreement"]),
        ("8% affordable-housing law (RIGL 44-5-13.11)", R["8% affordable-housing law"]),
        ("Homestead exemption, owner-occupied homes", R["homestead exemption"])]
b.append('<div class="tablewrap"><table><tr><th>Regime</th><th class="n">Parcels</th><th class="n">Exempt value</th><th class="n">Tax billed</th></tr>')
for name, x in rows:
    b.append(f'<tr><td>{e(name)}</td><td class="n">{x["parcels"]:,}</td><td class="n">{money(x["exempt"])}</td><td class="n">{money(x["taxes"])}</td></tr>')
b.append(f'<tr class="total"><td>Whole city</td><td class="n">{T["parcels"]:,}</td><td class="n">{money(T["exempt"])}</td><td class="n">{money(T["taxes"])}</td></tr></table></div>')
b.append(f'<p class="cite">City of Providence 2025 Property Tax Roll (data.providenceri.gov), {T["parcels"]:,} parcels after removing duplicate rows. Full rate read from the roll: commercial ${roll["full_rate"]["commercial_per_1000"]:.2f}, residential ${roll["full_rate"]["residential_per_1000"]:.2f} per $1,000.</p>')

b.append('<h2>Who holds the fully exempt property</h2>')
b.append(f'<p>Of the {money(groups["total_exempt"])} that pays nothing, {money(groups["government"])} belongs to the City, the State, the federal government, public authorities and the railroad, none of which the City can tax. The other {money(groups["private"])} is private. At the full commercial rate it would owe {money(groups["private_full_rate_tax"])} a year.</p>')
b.append('<div class="tablewrap"><table><tr><th>Holder</th><th class="n">Parcels</th><th class="n">Exempt value</th><th class="n">At full rate</th></tr>')
for k, g in groups["groups"].items():
    b.append(f'<tr><td>{e(k[0].upper()+k[1:])}</td><td class="n">{g["parcels"]:,}</td><td class="n">{money(g["exempt"])}</td><td class="n">{money(g["full_rate_tax"])}</td></tr>')
b.append('</table></div>')

b.append('<h2>The institutions: full rate against what they pay</h2>')
b.append('<p>The largest private holders make voluntary payments to the City under negotiated agreements, called payments in lieu of taxes. Here is each one&#8217;s exempt property at the full rate, set against its payment.</p>')
b.append('<div class="tablewrap"><table><tr><th>Institution</th><th class="n">Exempt value</th><th class="n">At full rate</th><th class="n">Pays the City</th><th class="n">Share</th></tr>')
for r in inst:
    paid = float(r["pilot_paid"]); full = float(r["full_rate_tax"])
    ptxt = money(paid, 2) if paid else "none found"
    if r["institution"] == "Providence Place": ptxt = "~" + ptxt
    b.append(f'<tr><td>{e(r["institution"])}</td><td class="n">{money(r["exempt_value"])}</td><td class="n">{money(full)}</td><td class="n">{ptxt}</td><td class="n">{r["share_paid"]}</td></tr>')
b.append('</table></div>')
b.append('<p class="cite">Payments: colleges, 2023 agreements, first-year (FY2025) amounts, Rhode Island Current, Sept. 6, 2023; Brown University Health, agreement signed Nov. 15, 2024, $750,000 a year, City of Providence; Providence Place, 30-year agreement expiring 2028, about $500,000 a year, Providence Business News. RISD&#8217;s parcels carry no owner name on the roll and are matched by RISD&#8217;s mailing address, 2 College St.</p>')
b.append(f'<p>The State also pays Providence for part of what it loses on college and hospital property. The law sets the reimbursement at up to 27 percent of the tax the property would have paid. Providence reported {money(sp["reported_base"])} in such tax. The State paid the City {money(sp["fy2025_payment"])} in fiscal 2025, and the enacted budget for fiscal 2026 gives {money(sp["fy2026_enacted"])}. This is State aid to the City. It is not money from the institutions, and it does not change what they pay.</p>')
b.append('<p class="cite">House Fiscal Advisory Staff, Local Aid, 2025 edition, Appendix VII; FY 2026 Budget as Enacted: State Aid to Local Governments. RIGL 45-13-5.1. Full figures: <a href="data/state-pilot.json">state-pilot.json</a>.</p>')

b.append('<h2>Tax stabilization agreements</h2>')
b.append(f'<p>A tax stabilization agreement fixes a developer&#8217;s tax bill below the full rate for a set term, in exchange for building. The 2025 roll carries {tsa["parcels"]} parcels under these agreements, held by {tsa["owners"]} owners. They were billed {money(tsa["billed"])}; at the full rate they would owe {money(tsa["full_rate"])}. The difference is {money(tsa["abated"])} in one year.</p>')
a = tsa["city_audit_fy2025"]
b.append(f'<p>The City&#8217;s Internal Auditor counts it the same way. Its FY2025 report lists {a["agreements"]} agreements billed {money(a["billed"])} against {money(a["full_rate"])} at full rate: {money(a["abated"])} abated, at the rates before the 2025 revaluation.</p>')
b.append('<div class="tablewrap"><table><tr><th>Owner</th><th>Address</th><th class="n">Billed</th><th class="n">At full rate</th><th class="n">Abated</th></tr>')
for d in tsa["ledger"][:20]:
    b.append(f'<tr><td>{e(tc(d["owner"]))}</td><td>{e(tc(d["addresses"][0]))}</td><td class="n">{money(d["billed"])}</td><td class="n">{money(d["full_rate"])}</td><td class="n">{money(d["abated"])}</td></tr>')
b.append('</table></div><p class="cite">The 20 largest by abatement. Full list: <a href="data/tsa-ledger.json">tsa-ledger.json</a>. City of Providence, Office of the Internal Auditor, Report on Tax Stabilization Agreements, Fiscal Year 2025.</p>')
REQ = [("annual_report", "Annual report filed with the City Clerk"), ("parks_fee", "Parks fee paid"),
       ("monitoring_fee", "Monitoring fee paid"), ("first_source", "First Source hiring agreement"),
       ("mbe_wbe", "Minority- and women-owned business participation"), ("apprenticeship", "Apprenticeship requirement")]
def cnt(k, v): return sum(1 for r in rep if r["compliance_norm"][k] == v)
sav = [r["savings_to_date"] for r in rep if r.get("savings_to_date")]
b.append('<h3 style="font:600 20px/26px var(--serif);margin:28px 0 8px">Who kept the terms</h3>')
b.append(f'<p>Each agreement comes with conditions: an annual report, fees, hiring rules. The Internal Auditor checked each of the {len(rep)} agreements against its conditions. {cnt("annual_report","no")} owners did not file the required annual report. For most of the hiring conditions, the auditor could not say whether they were met. The report puts the owners&#8217; savings to date at {money(sum(sav))} across the {len(sav)} agreements where it gives a figure.</p>')
b.append('<div class="tablewrap"><table><tr><th>Condition</th><th class="n">Met</th><th class="n">Not met</th><th class="n">Could not tell</th><th class="n">Not required</th></tr>')
for k, label in REQ:
    b.append(f'<tr><td>{label}</td><td class="n">{cnt(k,"yes")}</td><td class="n">{cnt(k,"no")}</td><td class="n">{cnt(k,"unable to determine")+cnt(k,"not given")}</td><td class="n">{cnt(k,"not required")}</td></tr>')
b.append('</table></div><p class="cite">City of Providence, Office of the Internal Auditor, Report on Tax Stabilization Agreements, FY2025, Exhibit 1, one entry per agreement. &#8220;Could not tell&#8221; includes entries the report left blank. Every agreement, with its answers: <a href="data/tsa-report-fy2025.json">tsa-report-fy2025.json</a>.</p>')

b.append('<h2>Who carries it</h2>')
b.append(f'<p><span class="tag model">MODEL</span> The City sets its budget first and its tax rates second, so revenue not collected from one parcel is collected from the others. Holding the {money(inc["levy"])} levy fixed, this is what each regime means for the median owner-occupied home, billed ${inc["median_homestead_bill"]:,.0f}, and the median two-to-five-family building a landlord rents out, billed ${inc["median_2to5_rental_bill"]:,.0f}.</p>')
b.append('<div class="tablewrap"><table><tr><th>If this were collected</th><th class="n">Share of levy</th><th class="n">Homeowner</th><th class="n">2–5 family rental</th></tr>')
for r in inc["regimes"]:
    b.append(f'<tr><td>{e(r["regime"])}</td><td class="n">{r["share_of_levy"]:.1%}</td><td class="n">−${r["homestead_saves"]:,}</td><td class="n">−${r["rental2_5_saves"]:,}</td></tr>')
b.append('</table></div><p class="cite">Each row is computed on its own; the rows do not add. The model assumes the levy would not rise to absorb the money.</p>')

b.append('<h2>Not yet on the record</h2><ul class="open">'
         '<li>Whether Care New England (Women &amp; Infants, Butler) pays the City anything. No agreement was found.</li>'
         '<li>The Providence Place payment, now that the mall is in receivership.</li>'
         '<li>The year-by-year schedules in the 2023 college agreements.</li>'
         '<li>Why a few parcels under stabilization agreements are billed $0 this year.</li></ul>')
b.append('<h2>Data</h2><p>Every table above is built from these files: '
         '<a href="data/roll-summary.json">roll-summary.json</a> · <a href="data/exempt-groups.json">exempt-groups.json</a> · '
         '<a href="data/institutions.csv">institutions.csv</a> · <a href="data/tsa-ledger.json">tsa-ledger.json</a> · '
         '<a href="data/incidence.json">incidence.json</a> · <a href="data/state-pilot.json">state-pilot.json</a> · '
         '<a href="data/tsa-report-fy2025.json">tsa-report-fy2025.json</a>.</p></main>')

if SITE.exists(): shutil.rmtree(SITE)
(SITE / "off-the-roll/data").mkdir(parents=True, exist_ok=True)
(SITE / "off-the-roll/index.html").write_text(page("Off the Roll — Providence, on the record",
    "What Providence doesn't tax: exempt property, payments in lieu of taxes and tax stabilization agreements, from the City's 2025 tax roll.",
    "../", "".join(b)))
for f in ["roll-summary.json", "exempt-groups.json", "institutions.csv", "tsa-ledger.json", "incidence.json", "pilots.json", "state-pilot.json", "tsa-report-fy2025.json"]:
    shutil.copy(U / f, SITE / "off-the-roll/data" / f)

# ---------------------------------------------------------------- home
h = ['<main><div class="dateline">PROVIDENCE</div><h1>Providence, on the record</h1>'
     '<p class="deck">Reporting and public records on the City of Providence: what it owns, what it taxes, what it builds and who pays.</p>'
     '<div class="feed">']
items = [("off-the-roll/", "OFF THE ROLL · NEW", f'${T["exempt"]/1e9:.1f} billion of Providence&#8217;s ${T["assessed"]/1e9:.0f} billion in property is exempt from full taxation',
          "Colleges, hospitals, government, a mall and 80 owners under tax agreements, set against what they pay the City."),
         ("downtown-ledger/", "DOWNTOWN LEDGER", "What downtown has, what it lacks, and how long the missing takes to arrive",
          "Workers, storefronts, transit and the walk between them, measured."),
         ("inside-the-line/", "INSIDE THE LINE", "Who the hurricane barrier protects",
          "Elevation, parcels, people and jobs behind the Fox Point barrier, and the water on the other side."),
         ("https://providenceontherecord.substack.com", "REPORTING", "The stories", "Reporting built on the documents, on Substack.")]
for href, kicker, title, deck in items:
    h.append(f'<article><div class="kicker">{kicker}</div><h3><a href="{href}">{title}</a></h3><p>{deck}</p></article>')
h.append('</div></main>')
(SITE / "index.html").write_text(page("Providence, on the record",
    "Reporting and public records on the City of Providence, by Liam Freaney.", "", "".join(h)))
(SITE / "style.css").write_text(CSS)

# ---------------------------------------------------------------- folded sections
# Downtown Ledger and Inside the Line are built in their own folders (../downtown-ledger,
# ../inside-the-line; run their ./build first). Their built site/ is copied here under a
# path prefix, root-absolute links are re-pointed, and a one-line strip links back home.
NEW = "https://providenceontherecord.org"
ROOTS = r"(?:about|data|fonts|ledger|photos|places|streets|walks|style|og)"
LINK = re.compile(r'(["\'(`])/(?=' + ROOTS + r'\b|#|["\'])')
STRIP = ('<div style="font:500 13px/18px system-ui,-apple-system,sans-serif;padding:8px 16px;'
         'border-bottom:1px solid rgba(0,0,0,.15);background:#f7f5f0">'
         '<a href="/" style="color:#16181b;text-decoration:none">Providence, on the record</a></div>')
def fold(slug, old):
    src, dst, pre = HERE.parent / slug / "site", SITE / slug, f"/{slug}/"
    shutil.copytree(src, dst)
    photos = HERE.parent / slug / "data" / "photos"
    if slug == "downtown-ledger" and photos.exists():
        shutil.copytree(photos, dst / "photos", dirs_exist_ok=True)
    n = 0
    for f in dst.rglob("*"):
        if f.suffix not in (".html", ".css", ".js"): continue
        t = f.read_text()
        t = t.replace(old + "/", NEW + pre).replace(old, NEW + pre[:-1])
        t, k = LINK.subn(lambda m: m.group(1) + pre, t); n += k
        if f.suffix == ".html":
            t = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + STRIP, t, count=1)
        f.write_text(t)
    print(f"folded {slug}: {sum(1 for _ in dst.rglob('*.html'))} pages, {n} links re-pointed")
fold("downtown-ledger", "https://downtownledger.com")
fold("inside-the-line", "https://insidetheline.org")


print("built", sum(1 for p in SITE.rglob("*") if p.is_file()), "files")
