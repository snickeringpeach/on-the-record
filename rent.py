"""Rent stabilization coverage section for providenceontherecord.org. Rendered from ../rent-coverage
(coverage_v2.py -> merged_v2.csv; coverage_8law.py -> output_8law.txt). Called from build.py:
rent.render(page, e, SITE, DATELINE). Draft by Claude, Oct 6 2026; not published until Liam says deploy.
Left out on purpose: anything from council staff's review (not for quoting) and the Sept 17 call (off the record).
"""
import csv, collections, os, pathlib, re, shutil, sys

RC = pathlib.Path(__file__).parent.parent / "rent-coverage"
sys.path.insert(0, str(RC)); import wards

def _src(name):
    """A file in ../rent-coverage; follows its symlink into ~/Downloads, also when run from the Cowork shell (~/mnt/Downloads)."""
    p = RC / name
    if p.exists(): return p
    t = pathlib.Path(os.readlink(p)).parts
    return pathlib.Path.home() / "mnt" / pathlib.Path(*t[3:]) if t[:2] == ("/", "Users") else p
LABEL = {"exempt 13-78(n) owner-occupied 1-4": "Owner lives in the building, 1 to 4 units (13-78(n))",
         "exempt 13-78(n) second property": "Small landlord&#8217;s second building, 1 to 4 units (13-78(n))",
         "exempt 13-78(j) HUD project-based": "Federal project-based subsidy (13-78(j))",
         "exempt 13-78(m) built 2022+": "New construction (13-78(m))"}

def render(page, e, SITE, DATELINE):
    rows = [r for r in csv.DictReader(open(RC / "merged_v2.csv")) if r["CAMA_MATCH"] == "Y"]
    zips = {}; law8 = collections.Counter(); seen8 = set(); n8 = 0
    for r in csv.DictReader(open(_src("2025_Property_Tax_Roll_20260910.csv"), encoding="utf-8-sig", errors="replace")):
        zips.setdefault(r["TAX_MAP"], (r["ZIP_POSTAL"] or "")[:5])
        n8 += r["LEVY_CODE_1"] == "8LAW"
        if r["LEVY_CODE_1"] == "8LAW" and r["TAX_MAP"] not in seen8:
            seen8.add(r["TAX_MAP"]); law8[wards.ward(r["TAX_MAP"])] += 1
    u = lambda r: int(float(r["RENTAL_UNITS"] or 0))
    cls = collections.Counter()
    for r in rows: cls[r["CLASS_V2"]] += u(r)
    cov = cls["covered"]; tot = sum(cls.values()); ex = tot - cov
    o8 = open(RC / "output_8law.txt").read()
    lo = int(re.search(r"low \(CAMA floor\): \+([\d,]+)", o8).group(1).replace(",", ""))
    hi = int(re.search(r"high \(all Providence LIHTC units\): \+([\d,]+)", o8).group(1).replace(",", ""))
    p_lo, p_hi = cov / (tot + hi), cov / (tot + lo)
    N = lambda x: f"{x:,}"; P = lambda x: f"{x*100:.0f}"

    def bucket(n):
        n = int(float(n or 0))
        return "1" if n <= 1 else "2" if n == 2 else "3" if n == 3 else "4" if n == 4 else "5 to 10" if n <= 10 else "11 to 49" if n <= 49 else "50 or more"
    by_size = collections.defaultdict(lambda: [0, 0])
    by_zip = collections.defaultdict(lambda: [0, 0])
    by_ward = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        k = 0 if r["CLASS_V2"] == "covered" else 1
        by_size[bucket(r["ResidentialUnits"])][k] += u(r)
        z = zips.get(r["TAX_MAP"], "")
        if re.fullmatch(r"029\d\d", z): by_zip[z][k] += u(r)
        w = wards.ward(r["TAX_MAP"])
        if w: by_ward[w][k] += u(r)

    b = [f'<main><div class="dateline">{DATELINE}</div>']
    b.append(f'<h1>The Rent Stabilization Ordinance Would Reach Roughly 60 to 65 Percent of Providence&#8217;s Rental Homes</h1>')
    b.append('<p class="deck">The City&#8217;s chief financial officer told the Council fewer than 44 percent; the Council&#8217;s consultant assumed 60. This is a count, parcel by parcel, from the City&#8217;s own property records, against the ordinance&#8217;s final text.</p>')
    b.append('<p class="byline">By Liam Freaney · from the 2025 property tax roll, the Assessor&#8217;s parcel database and HUD&#8217;s subsidized-housing files</p>')
    b.append('<div class="big">'
             f'<div><b>{N(cov)}</b><span>rental units the final text covers</span></div>'
             f'<div><b>{N(ex)}</b><span>rental units its exemptions take out</span></div>'
             f'<div><b>{N(lo)}&#8211;{N(hi)}</b><span>more in deed-restricted affordable buildings, also exempt <span class="tag model">MODEL</span></span></div>'
             f'<div><b>{P(p_lo)}&#8211;{P(p_hi)}%</b><span>of rental units covered</span></div></div>')

    b.append('<h2>The count</h2>')
    b.append(f'<p>The City&#8217;s records place {N(tot)} rental units in residential buildings outside the state&#8217;s 8 Law affordable-housing program. The ordinance&#8217;s final text covers {N(cov)} of them, {cov/tot:.1%}. A rental unit here is every unit in a residential building, less one in a building whose owner lives there, since the owner&#8217;s own apartment isn&#8217;t rented.</p>')
    b.append(f'<p>That share leaves out buildings the Assessor taxes under the state&#8217;s affordable-housing rule, known as 8 Law, which the ordinance also exempts as deed-restricted housing. The roll carries 659 such records, but not how many apartments are in them. Counting the units the Assessor&#8217;s database lists for them adds {N(lo)}; counting every low-income tax-credit unit HUD lists in Providence adds {N(hi)}. With them, the covered share falls to between {p_lo:.1%} and {p_hi:.1%}. The true count has been requested from the Assessor; until it arrives, read the figure as roughly 60 to 65 percent.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Rental units</th><th class="n">Units</th><th class="n">Share</th></tr>')
    b.append(f'<tr><td>Covered</td><td class="n">{N(cov)}</td><td class="n">{cov/tot:.1%}</td></tr>')
    for k, lab in LABEL.items():
        b.append(f'<tr><td>Exempt: {lab}</td><td class="n">{N(cls[k])}</td><td class="n">{cls[k]/tot:.1%}</td></tr>')
    b.append(f'<tr><td><b>Total</b></td><td class="n"><b>{N(tot)}</b></td><td class="n"></td></tr></table></div>')
    b.append('<p class="cite">Section numbers are the ordinance&#8217;s, Chapter 13, Article IV, final text. The 8 Law range is a model: its low end undercounts (the Assessor&#8217;s database lists a median of one unit per 8 Law parcel) and its high end overcounts (some tax-credit projects carry no 8 Law record).</p>')

    b.append('<h2>By building size</h2>')
    b.append('<p>The exemptions fall almost entirely on small buildings. Apartment buildings of five units or more are covered unless they are new or federally subsidized.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Units in the building</th><th class="n">Covered</th><th class="n">Exempt</th><th class="n">Covered share</th></tr>')
    for k in ["1", "2", "3", "4", "5 to 10", "11 to 49", "50 or more"]:
        c, x = by_size[k]
        if c + x: b.append(f'<tr><td>{k}</td><td class="n">{N(c)}</td><td class="n">{N(x)}</td><td class="n">{c/(c+x):.0%}</td></tr>')
    b.append('</table></div>')

    b.append('<h2>By ward</h2>')
    b.append('<div class="tablewrap"><table><tr><th>Ward</th><th class="n">Covered</th><th class="n">Exempt</th><th class="n">Covered share</th><th class="n">8 Law parcels</th></tr>')
    for w in sorted(by_ward):
        c, x = by_ward[w]
        b.append(f'<tr><td>{w}</td><td class="n">{N(c)}</td><td class="n">{N(x)}</td><td class="n">{c/(c+x):.0%}</td><td class="n">{N(law8[w])}</td></tr>')
    b.append('</table></div>')
    b.append(f'<p class="cite">Wards are the City Council wards drawn in 2022, as the City&#8217;s GIS server assigns them to each parcel (layer Parcels_with_Ward_and_Zoning, read Oct. 6, 2026); all {N(sum(sum(v) for v in by_ward.values()))} rental units place in a ward. 8 Law parcels are the {N(len(seen8))} distinct parcels behind the roll&#8217;s {N(n8)} records taxed under the state&#8217;s affordable-housing rule, also exempt; the roll does not say how many apartments each holds, so they are counted as parcels, not units, and are not in the covered share.</p>')

    b.append('<h2>By ZIP code</h2>')
    b.append('<div class="tablewrap"><table><tr><th>ZIP</th><th class="n">Covered</th><th class="n">Exempt</th><th class="n">Covered share</th></tr>')
    for z in sorted(by_zip, key=lambda z: -sum(by_zip[z])):
        c, x = by_zip[z]
        if c + x >= 100: b.append(f'<tr><td>{z}</td><td class="n">{N(c)}</td><td class="n">{N(x)}</td><td class="n">{c/(c+x):.0%}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">ZIP codes as the 2025 roll records each property&#8217;s location. 8 Law buildings are not in this table or the one by building size.</p>')

    b.append('<h2>How it was counted</h2>')
    b.append('<ul>'
             '<li>The 2025 property tax roll, from the City&#8217;s open-data portal (dataset 6ub4-iebe, downloaded Sept. 10, 2026), joined to the Assessor&#8217;s parcel database export (provided Sept. 10, 2026) on plat, lot and unit. 96 percent of residential parcels match; the rest, mostly condominiums, are left out of both counts.</li>'
             '<li>Residential parcels are the roll&#8217;s owner-occupied and non-owner-occupied residential and apartment levy codes, excluding vacant land. The levy code carries the City&#8217;s own determination of whether the owner lives there.</li>'
             '<li>Owner-occupied buildings of 1 to 4 units are exempt, as is a small landlord&#8217;s second building of 1 to 4 units when the owner holds no more than two parcels and lives in one. Owners are matched by name, so that test is approximate.</li>'
             '<li>New construction is exempt for 10 years from its certificate of occupancy, reaching back 5 years from the effective date. Assuming the ordinance takes effect in 2027, buildings the Assessor dates 2022 or later are exempt; that year field is the database&#8217;s weakest.</li>'
             '<li>Federally subsidized, project-based buildings are matched by address to HUD&#8217;s Multifamily Assistance and Section 8 database (7 of 54 Providence properties matched).</li>'
             '<li>Not modeled: the 20-year exemption for new projects built with prevailing wages and apprentices, and state subsidy programs.</li></ul>')
    b.append('<p class="cite">Code and data: <a href="data/coverage-by-parcel.csv">coverage by parcel (CSV)</a>; the scripts that produce it, <a href="data/coverage.py">coverage.py</a>, <a href="data/coverage_v2.py">coverage_v2.py</a> and <a href="data/coverage_8law.py">coverage_8law.py</a>; the ward lookup, <a href="data/wards.py">wards.py</a> with <a href="data/ward_runs.txt">ward_runs.txt</a>. The CFO&#8217;s figure and the consultant&#8217;s 60 percent: Boston Globe, Feb. 20, 2026. HUD Multifamily Assistance and Section 8 database; HUD Low-Income Housing Tax Credit database, placed in service through 2024.</p>')
    b.append('</main>')

    out = SITE / "rent-stabilization"; (out / "data").mkdir(parents=True, exist_ok=True)
    for s in ("coverage.py", "coverage_v2.py", "coverage_8law.py", "wards.py"):
        (out / "data" / s).write_text((RC / s).read_text().replace("from David Dos Reis", "from the Assessor's office"))
    shutil.copy(RC / "ward_runs.txt", out / "data" / "ward_runs.txt")
    cols = ["TAX_MAP", "LEVY_CODE_1", "SHORT_DESC", "OWNER_TYPE", "ResidentialUnits", "YearBuilt", "RENTAL_UNITS", "CLASS_V2"]
    with open(out / "data" / "coverage-by-parcel.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols + ["WARD"])
        for r in csv.DictReader(open(RC / "merged_v2.csv")): w.writerow([r[c] for c in cols] + [wards.ward(r["TAX_MAP"]) or ""])
    (out / "index.html").write_text(page("Rent stabilization coverage — Providence, on the record",
        "How many of Providence's rental homes the rent stabilization ordinance covers, counted parcel by parcel.", "../", "".join(b), "rent-stabilization/"))
    return {"low": round(p_lo * 100), "high": round(p_hi * 100), "covered": cov}
