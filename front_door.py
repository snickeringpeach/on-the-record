"""311 section for providenceontherecord.org: what PVD311 publishes, what its form asks, and who files.
Rendered from ../pvd311/data. Called from build.py: front_door.render(page, e, SITE, DATELINE).
Section name and slug: "311", /311/ (Liam, Oct 1). Aggregates only: no case-level
addresses are republished, though the City shows them on its own site."""
import json, pathlib, collections, statistics as st

P = pathlib.Path(__file__).parent.parent / "pvd311" / "data"
LITTER = ["Trash on Streets and Public Property", "Trash on Private Property or Sidewalk", "Illegal Dumping",
          "Overflowing Dumpster", "Maintenance Issue in a City Park", "Street Sweeping Issue or Concern"]
ELSEWHERE = ("call ", "directly", "(401)", "401-", "(855)", "should be reported")

def latest(globpat):
    fs = sorted(P.glob(globpat)); return fs[-1] if fs else None

def render(page, e, SITE, DATELINE):
    N = lambda x: f"{x:,}"
    types = json.load(open(latest("case-types-*.json")))
    snapf = latest("public/*.json"); snap = json.load(open(snapf))
    an = json.load(open(latest("analytics/*.json")))
    bos = json.load(open(P / "boston" / "tracts-new-system.json"))
    asof = snapf.stem
    tdesc = {t["name"]: t["description"] for t in types}
    elsewhere = [t["name"] for t in types if any(w in t["description"].lower() for w in ELSEWHERE)]
    catch = next((t["name"] for t in types if t["name"].lower().startswith("i do not know")), None)
    origins = [(o["label"] or "(blank)", o["count"]) for o in an["origins_ytd"]]
    otot = sum(c for _, c in origins); od = dict(origins)
    status = collections.Counter(r["statuscode"] for r in snap)
    ctypes = collections.Counter((r["cop_casetype"] or "").strip() for r in snap)
    dates = sorted(r["createdon"] for r in snap)
    import datetime
    doy = datetime.date.fromisoformat(asof).timetuple().tm_yday - 1

    b = [f'<main><div class="dateline">{DATELINE}</div>',
         '<h1>Providence&#8217;s 311, on the Record</h1>',
         '<p class="deck">What the City&#8217;s service-request system publishes, what its form asks of a resident, and who files. Counted from the City&#8217;s own site.</p>',
         '<p class="byline">By Liam Freaney · from 311.providenceri.gov, Boston&#8217;s open 311 data and the Census Bureau</p>',
         '<div class="big">'
         f'<div><b>{N(otot)}</b><span>cases this year in the City&#8217;s six largest channels</span></div>'
         f'<div><b>{N(od.get("Web", 0))}</b><span>logged as &#8220;Web&#8221;; the site&#8217;s New Request button leads to a sign-in</span></div>'
         f'<div><b>{N(od.get("Guest Support", 0))}</b><span>logged as &#8220;Guest Support,&#8221; the form without an account</span></div>'
         f'<div><b>{len(types)}</b><span>case types, in one alphabetical list</span></div></div>']

    b.append('<h2>The front door</h2>')
    b.append('<p>The &#8220;New Request&#8221; button on PVD311&#8217;s home page leads to a sign-in screen. A resident without an account can report through &#8220;Guest Support,&#8221; which is in the site&#8217;s menu but not among the buttons on its home page. The guest form takes no photo attachments.</p>')
    b.append('<div class="tablewrap"><table><tr><th>How cases came in, this year</th><th class="n">Cases</th><th class="n">Share</th></tr>')
    for lab, c in origins:
        b.append(f'<tr><td>{e(lab)}</td><td class="n">{N(c)}</td><td class="n">{c/otot:.0%}</td></tr>')
    b.append('</table></div><p class="cite">Source: PVD311 &#8220;Top Service Requests&#8221; page (/analytics), calendar year to date, the six largest channels, read '
             + e(an.get("_asof", asof)) + '.</p>')

    b.append('<h2>The menu</h2>')
    b.append(f'<p>To file, a resident picks one of {len(types)} case types from a single alphabetical list, from &#8220;{e(types[0]["name"])}&#8221; to &#8220;{e(types[-1]["name"])}.&#8221; '
             f'{len(elsewhere)} of the descriptions tell the resident to call someone else, such as the police non-emergency line, Rhode Island Energy or Providence Water. '
             + (f'One type is a catch-all, listed as &#8220;{e(catch)}&#8221; ' if catch else '') + '</p>')
    b.append('<p>Litter is split by who owns the ground:</p><div class="tablewrap"><table><tr><th>Case type</th><th>The City&#8217;s description</th></tr>')
    for t in LITTER:
        if t in tdesc: b.append(f'<tr><td>{e(t)}</td><td>{e(tdesc[t])}</td></tr>')
    b.append('</table></div><p class="cite">Source: the case-type list on the PVD311 guest form. Full list: <a href="data/case-types.json">case-types.json</a>.</p>')

    b.append('<h2>The last seven days</h2>')
    b.append(f'<p>PVD311 shows a rolling seven-day list of cases on its &#8220;Public Requests&#8221; page. On {e(asof)} it showed {N(len(snap))} cases, created {e(dates[0][:10])} to {e(dates[-1][:10])}. '
             f'That is about {len(snap)/7:.0f} a day, against the year&#8217;s pace of about {otot/doy:.0f} a day, so the public list appears to be a subset. Which cases it shows is a question for the City.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Status</th><th class="n">Cases</th></tr>')
    for s_, c in status.most_common():
        b.append(f'<tr><td>{e(s_ or "")}</td><td class="n">{N(c)}</td></tr>')
    b.append('</table></div><div class="tablewrap"><table><tr><th>Most frequent case types, last seven days</th><th class="n">Cases</th></tr>')
    for t, c in ctypes.most_common(10):
        b.append(f'<tr><td>{e(t)}</td><td class="n">{N(c)}</td></tr>')
    b.append('</table></div><p class="cite">Source: PVD311 &#8220;Public Requests,&#8221; snapshotted daily. Counts only; the City&#8217;s list also shows street addresses, which this page does not republish.</p>')

    rr = sorted([r for r in bos if r["median_income"]], key=lambda r: r["median_income"]); n = len(rr)
    b.append('<h2>Who files: what Boston&#8217;s data shows</h2>')
    b.append(f'<p>Boston publishes every 311 case with its location and how it came in. Placing its resident-filed cases from August 2025 to September 2026 in census tracts ({n} tracts with at least 500 residents) and grouping the tracts by median household income:</p>')
    b.append('<div class="tablewrap"><table><tr><th>Tract median income</th><th class="n">Cases per 1,000 residents</th><th class="n">Litter cases per 1,000</th><th class="n">Median share by phone</th></tr>')
    labels = ["Lowest fifth", "Second", "Middle", "Fourth", "Highest fifth"]
    for q in range(5):
        g = rr[q * n // 5:(q + 1) * n // 5]; pop = sum(r["pop"] for r in g)
        b.append(f'<tr><td>{labels[q]} (${g[0]["median_income"]/1000:,.0f}K&#8211;${g[-1]["median_income"]/1000:,.0f}K)</td>'
                 f'<td class="n">{1000*sum(r["cases"] for r in g)/pop:.0f}</td><td class="n">{1000*sum(r["litter"] for r in g)/pop:.1f}</td>'
                 f'<td class="n">{st.median(r["phone_share"] for r in g):.0%}</td></tr>')
    b.append('</table></div><p class="cite">Source: Analyze Boston, 311 Service Requests (new system); 2020 census tracts (TIGERweb); American Community Survey 5-year estimates, 2020&#8211;2024. Litter = Litter &amp; Debris, Illegal Dumping or Disposal, Overflowing Trash, Park Litter &amp; Debris. Rates count residents only, so tracts with many visitors and commuters run high.</p>')
    b.append('<p>A count of reports per resident measures reporting, not need. Providence&#8217;s version of this table will be built from the daily snapshots and the City&#8217;s full case data, requested under the Access to Public Records Act.</p>')

    b.append('<h2>Records requested</h2><ul class="open">'
             '<li>26-2497: PVD311 configuration and design records (filed Sept. 26, 2026).</li>'
             '<li>26-2498: PVD311 case data, including requests started and never submitted (filed Sept. 26, 2026).</li>'
             '<li>26-2499: PVD311 procurement and contracts (filed Sept. 26, 2026).</li></ul>')
    b.append('<h2>Data</h2><p><a href="data/case-types.json">case-types.json</a> · <a href="data/origins-ytd.json">origins-ytd.json</a> · '
             '<a href="data/boston-tracts.json">boston-tracts.json</a>. Method and code: published with the reporting.</p></main>')

    out = SITE / "311"; (out / "data").mkdir(parents=True, exist_ok=True)
    json.dump(types, open(out / "data/case-types.json", "w"), indent=1)
    json.dump(an, open(out / "data/origins-ytd.json", "w"), indent=1)
    json.dump(bos, open(out / "data/boston-tracts.json", "w"))
    (out / "index.html").write_text(page("Providence’s 311, on the record — Providence, on the record",
        "What PVD311 publishes, what its form asks, and who files.", "../", "".join(b), "311/"))
    return dict(total=otot, web=od.get("Web", 0), guest=od.get("Guest Support", 0), types=len(types))
