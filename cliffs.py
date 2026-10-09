"""Providence in stages: what changes who pays, and when. Stage 1, 2028. B186, Oct 8 2026.
From ../who-pays/cliffs/EVENTS.md, each line checked against its record before it went on the page.
Called from build.py: cliffs.render(page, e, SITE, DATELINE). Not published until Liam says deploy.
Left out on purpose: EVENTS.md's [C] readings (that the stages stack, which stage is 'the real cliff'),
and its own computed $26.8M mall bill (the page uses RI Current's published $24.9M)."""
import csv, json, pathlib
U = pathlib.Path(__file__).parent.parent / "untaxed" / "data"

def render(page, e, SITE, DATELINE):
    col = {r["fy"]: r for r in json.load(open(U / "college-schedule.json"))["rows"]}
    tsa = [r for r in csv.DictReader(open(U / "tsa-terms.csv")) if r["last"] == "2028"]
    ab = sum(float(r["abated_2024"]) for r in tsa)
    M = lambda x: f"${x/1e6:,.1f} million" if x >= 1e6 else f"${x:,.0f}"
    b = ['<main><div class="dateline">PROVIDENCE · OCT. 8, 2026</div>',
         '<h1>2028: The Mall Agreement Ends, Every Assessment Resets, and Two Institutional Payments Change</h1>',
         '<p class="deck">The events that change who pays for Providence arrive on dates, not on a smooth curve. This page lists them by stage, starting with the nearest. Each line names its record.</p>',
         '<p class="byline">By Liam Freaney · from the City&#8217;s agreements, the Internal Auditor&#8217;s tax-stabilization report, state law and published reporting</p>',
         '<h2>Stage 1: 2028</h2>',
         '<div class="tablewrap"><table><tr><th>What</th><th>When</th><th>What it moves</th><th>Record</th></tr>']
    rows = [
        ("Providence Place&#8217;s tax agreement ends", "2028",
         "The 30-year agreement expires. The mall pays $500,000 a year in City property tax; at fiscal 2026 commercial rates its $730.8 million assessment would bill about $24.9 million. It sold this year for $133 million; the buyer&#8217;s bid did not depend on a new tax deal.",
         '<a href="https://rhodeislandcurrent.com/2026/04/30/providence-place-in-line-for-a-makeover-under-133m-sale-and-maybe-a-costco/">Rhode Island Current, Apr. 30, 2026</a>'),
        ("Citywide revaluation", "Values as of Dec. 31, 2027; likely first billed in fiscal 2029",
         "Every assessment resets, the mall&#8217;s included. The City contracted Vision Government Solutions for the full revaluation at $2,044,000.",
         '<a href="https://ProvidenceRI.IQM2.com/Citizens/Detail_Meeting.aspx?ID=15735">Board of Contract and Supply, Oct. 5, 2026, item #53977</a>'),
        ("Brown University Health: the payment agreement runs out", "No payment scheduled after fiscal 2026",
         "The 2024 agreement pays $1.5 million: $750,000 in fiscal 2025 and $750,000 in fiscal 2026. Brown Health agreed to negotiate a successor in the agreement&#8217;s third year. No payment is scheduled after that.",
         '<a href="https://www.providenceri.gov/mayor-smiley-signs-pilot-agreement-with-brown-university-health/">City of Providence, 2024</a>; <a href="https://www.browndailyherald.com/article/2024/10/lifespan-soon-brown-university-health-agrees-to-pay-15-million-to-city-in-lieu-of-taxes">Brown Daily Herald, Oct. 2024</a>'),
        ("Brown&#8217;s separate agreement steps down", "Fiscal 2028",
         f"Brown&#8217;s payments under its own 10-year agreement fall from {M(col[2027]['brown_moa'])} to {M(col[2028]['brown_moa'])} a year. The four colleges&#8217; scheduled payments under the 2023 memorandum rise to {M(col[2028]['total'])}.",
         '<a href="https://www.brown.edu/sites/default/files/2023_MOA_amended.pdf">2023 Memorandum of Agreement</a>; <a href="https://www.brown.edu/sites/default/files/2023_MOU_proposed.pdf">2023 MOU, Exhibit A</a>'),
        (f"{len(tsa)} tax-stabilization agreements end", "Tax year 2028",
         f"Together they were abated {M(ab)} in tax year 2024. " + "; ".join(f"{r['header']} ({e(r['owner'])})" for r in tsa) + ".",
         "City of Providence Internal Auditor, tax stabilization agreement report, FY2025, Exhibit 1 (the last tax year each agreement lists)"),
    ]
    for w, t, m, s in rows:
        b.append(f"<tr><td><b>{w}</b></td><td>{t}</td><td>{m}</td><td>{s}</td></tr>")
    b.append("</table></div>")
    b.append('<p class="cite">Tax-year 2024 dollars for the tax-stabilization agreements, at 2024 rates, before the revaluation. An agreement&#8217;s end year is the last year the Auditor&#8217;s table lists for it, not yet checked against each ordinance. When an agreement ends, an owner may seek an extension; each end date is also a date for that request.</p>')
    b.append("<h2>Later stages</h2><p>Later stages will be added here as each is checked against its records: fiscal 2030 (twenty tax-stabilization agreements end), fiscal 2034 (Brown&#8217;s separate agreement ends), the pension plan&#8217;s target year, and the end of the colleges&#8217; agreement after fiscal 2043. Events with no date, such as a storm, a FEMA remap or a change in the barrier&#8217;s certification, will be listed with what sets them off.</p>")
    b.append("</main>")
    out = SITE / "cliffs"; out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page("2028 — Providence, on the record",
        "What changes who pays for Providence in 2028: the mall agreement, the revaluation, Brown Health, Brown's agreement, and four tax-stabilization agreements.", "../", "".join(b), "cliffs/"))
    return {"n_tsa": len(tsa)}
