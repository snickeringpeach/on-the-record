"""Providence by ward: the site's records cut by the 15 City Council wards (2022 lines).
Reads ../wards/wards.json (build_wards.py). Draft by Claude, Oct 6 2026.
Tax-sale figures are counts only; owner names never appear. Nothing from council staff or the Sept 17 call.
"""
import json, pathlib, shutil
WD = pathlib.Path(__file__).parent.parent / "wards"
N = lambda x: f"{x:,}"
B = lambda x: f"${x/1e9:.1f} billion" if x >= 1e9 else f"${x/1e6:,.0f} million"

def render(page, e, SITE, DATELINE):
    D = json.load(open(WD / "wards.json"))
    b = [f'<main><div class="dateline">{DATELINE}</div>']
    b.append('<h1>Providence, Ward by Ward</h1>')
    b.append('<p class="deck">The records on this site, cut along the 15 City Council wards: who the rent stabilization ordinance reaches, where the crashes are, how much property pays no tax, and which homes are on the tax-sale list.</p>')
    b.append('<p class="byline">From the City&#8217;s 2025 property tax roll and GIS ward lines, RIDOT crash records (request 26-373), the Tax Collector&#8217;s tax-sale lists and the City&#8217;s school-zone camera list</p>')
    b.append('<p class="jump">' + " ".join(f'<a href="#ward-{o["ward"]}">{o["ward"]}</a>' for o in D) + '</p>')
    b.append('<h2>All 15 wards</h2>')
    b.append('<div class="tablewrap"><table><tr><th>Ward</th><th class="n">Rental units covered</th><th class="n">Covered share</th>'
             '<th class="n">Crashes 2019&#8211;25</th><th class="n">Killed or seriously hurt</th><th class="n">Pedestrian</th><th class="n">Bicycle</th>'
             '<th class="n">Property fully exempt</th><th class="n">On 2026 tax-sale list</th></tr>')
    for o in D:
        rc, rx = o["rent_covered"], o["rent_exempt"]
        b.append(f'<tr><td><a href="#ward-{o["ward"]}">{o["ward"]}</a></td><td class="n">{N(rc)}</td><td class="n">{rc/(rc+rx):.0%}</td>'
                 f'<td class="n">{N(o["crashes"])}</td><td class="n">{N(o["ksi"])}</td><td class="n">{N(o["ped"])}</td><td class="n">{N(o["bike"])}</td>'
                 f'<td class="n">{o["full_exempt"]/o["assessed"]:.0%}</td><td class="n">{N(o["tax_sale_2026"])}</td></tr>')
    b.append('</table></div>')
    for o in D:
        w = o["ward"]; rc, rx = o["rent_covered"], o["rent_exempt"]
        b.append(f'<h2 id="ward-{w}">Ward {w}</h2><ul>')
        b.append(f'<li><b>Rent stabilization.</b> The final text covers {N(rc)} of the ward&#8217;s {N(rc+rx)} rental units, {rc/(rc+rx):.0%}. <a href="../rent-stabilization/">How it was counted</a>.</li>')
        c = "; ".join(f'{x[1].title().replace(" @ ", " at ")} ({N(x[0])})' for x in o["top_corners"])
        b.append(f'<li><b>Crashes.</b> Police reported {N(o["crashes"])} crashes off the highways from 2019 through 2025: {N(o["ksi"])} killed or seriously hurt someone, {N(o["ped"])} involved a pedestrian, {N(o["bike"])} a bicycle. Busiest corners, by crashes within 40 meters: {c}.</li>')
        own = "; ".join(f'{n} ({B(v)})' for n, v in o["top_exempt_owners"])
        b.append(f'<li><b>Untaxed property.</b> {B(o["full_exempt"])} of the ward&#8217;s {B(o["assessed"])} in assessed property is fully exempt, {o["full_exempt"]/o["assessed"]:.0%}. Largest: {own}. <a href="../off-the-roll/">Off the Roll</a>.</li>')
        b.append(f'<li><b>Tax sale.</b> {N(o["tax_sale_2026"])} parcels on the 2026 list, {N(o["tax_sale_2026_owner_occ"])} of them taxed as owner-occupied; {N(o["tax_sale_all_three"])} {"has" if o["tax_sale_all_three"] == 1 else "have"} been on all three lists, 2024 through 2026.</li>')
        cams = ", ".join(o["cameras"]) if o["cameras"] else "None on the 2022 list"
        b.append(f'<li><b>School-zone speed cameras.</b> {cams}.</li></ul>')
    b.append('<h2>How it was counted</h2><ul>'
             '<li>Wards are the City Council wards drawn in 2022. Parcels take the ward the City&#8217;s GIS server assigns them (layer Parcels_with_Ward_and_Zoning); crash points and cameras take the ward whose line, from the City&#8217;s 2022 ward layer simplified to about 8 meters, they fall inside. Both read Oct. 6, 2026.</li>'
             '<li>Property: the 2025 tax roll, one record per property ID; 48 of 44,062 have no ward. Fully exempt means the roll&#8217;s E01 levy code. Owner names as the roll prints them; one large record carries none.</li>'
             '<li>Crashes: every crash in RIDOT&#8217;s extract for request 26-373 with a point inside Providence, 2019 through 2025, leaving out interstates, expressways and their ramps. 942 crashes without a point and 202 just outside the simplified lines are not placed. Corners are the same name-free 40-meter clusters as the city ranking.</li>'
             '<li>Tax sale: the Tax Collector&#8217;s published lists for the 2024, 2025 and 2026 sales, joined to the roll by plat and lot. Owner-occupied means an owner-occupied levy code. No names are published here.</li>'
             '<li>Cameras: the City&#8217;s 2022 list of 20 school-zone camera sites, placed by address. 311 cases are not here yet: the City&#8217;s public feed does not carry locations.</li></ul>')
    b.append('<p class="cite">Code and data: <a href="data/wards.json">wards.json</a>, <a href="data/build_wards.py">build_wards.py</a>, <a href="data/ward_polys.txt">ward lines</a>.</p></main>')
    out = SITE / "wards"; (out / "data").mkdir(parents=True, exist_ok=True)
    for f in ("wards.json", "build_wards.py", "ward_polys.txt"): shutil.copy(WD / f, out / "data" / f)
    (out / "index.html").write_text(page("Providence, ward by ward — Providence, on the record",
        "Rent coverage, crashes, untaxed property and the tax-sale list for each of Providence's 15 City Council wards.", "../", "".join(b), "wards/"))
    sh = sorted(D, key=lambda o: o["rent_covered"] / (o["rent_covered"] + o["rent_exempt"]))
    pc = lambda o: round(100 * o["rent_covered"] / (o["rent_covered"] + o["rent_exempt"]))
    return {"hi_ward": sh[-1]["ward"], "hi": pc(sh[-1]), "lo_ward": sh[0]["ward"], "lo": pc(sh[0])}
