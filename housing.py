"""Housing section for providenceontherecord.org. Rendered from ../housing/data.
Called from build.py: housing.render(page, e, SITE, DATELINE).
Section name and slug ("Housing", /housing/) are placeholders pending Liam's call.
"""
import json, csv, shutil, pathlib

H = pathlib.Path(__file__).parent.parent / "housing" / "data"
FILES = ["statewide.json", "census-permits-ri.csv", "permits-new-housing-2009-2019.csv",
         "built-since-2010.csv", "built-summary.json"]

def render(page, e, SITE, DATELINE):
    st = json.load(open(H / "statewide.json"))
    bs = json.load(open(H / "built-summary.json"))
    towns = {t["town"]: t for t in st["towns"]}
    pv = towns["Providence"]; pd = pv["doh_2024"]; c24 = pv["census"]["2024"]
    permits = list(csv.DictReader(open(H / "permits-new-housing-2009-2019.csv")))
    city = {}
    for p in permits:
        if p["year"]: city[p["year"]] = city.get(p["year"], 0) + int(p["counted_units"])
    built = bs["by_year"]
    sw_c24 = sum(t["census"]["2024"]["total"] for t in st["towns"])
    sw_d = st["doh_2024_statewide"]
    imputed24 = sorted(t["town"] for t in st["towns"] if t["census"]["2024"]["months"] < 12)
    N = lambda x: f"{x:,}"

    b = [f'<main><div class="dateline">{DATELINE}</div>']
    b.append(f'<h1>Providence Permitted {N(pd["permitted_total"])} New Homes in 2024, or {N(c24["total"])}, Depending on Which Government Count You Read</h1>')
    b.append(f'<p class="deck">The State has set Providence a goal of {N(pv["goal_2026_2030"])} new homes over the next five years. The State&#8217;s housing report and the Census Bureau disagree on how many the City permits now, and the State estimates how many get built with a formula instead of a count.</p>')
    b.append('<p class="byline">By Liam Freaney · from the Census Bureau, the RI Department of Housing and the City&#8217;s own records</p>')
    b.append('<div class="big">'
             f'<div><b>{N(pv["goal_2026_2030"])}</b><span>homes the State expects Providence to permit, 2026&#8211;2030</span></div>'
             f'<div><b>{N(pd["permitted_total"])}</b><span>permitted in 2024, by the State&#8217;s survey of the City</span></div>'
             f'<div><b>{N(c24["total"])}</b><span>permitted in 2024, by the City&#8217;s reports to the Census</span></div>'
             f'<div><b>{N(pd["completed_total"])}</b><span>completed in 2024, by the State&#8217;s estimate</span></div></div>')

    b.append('<h2>The goal</h2>')
    b.append(f'<p>Under Housing 2030, the State&#8217;s housing plan, each city and town is expected to permit new homes equal to a share of its housing each year: 0.4 percent for towns without many jobs or much transit, 0.6 percent for towns with more jobs, and 0.8 percent for places with both. Providence is in the third group. Its goal is {N(pv["goal_2026_2030"])} homes from 2026 through 2030, about {N(pv["goal_per_year"])} a year, of which {N(pv["affordable_goal_2026_2030"])} are to be affordable.</p>')
    b.append('<p class="cite">RI Department of Housing, Housing 2030 municipal growth categories and production goals (housing.ri.gov/media/3401). Providence&#8217;s goal is 0.8 percent of 75,257 homes, times five years.</p>')

    b.append('<h2>Two counts of the same permits</h2>')
    b.append(f'<p>Two government surveys count the building permits each city issues for new homes. The Census Bureau&#8217;s Building Permits Survey takes what each city reports, month by month. The State&#8217;s Department of Housing surveys each city once a year. For Providence in 2024, the Census count is {N(c24["total"])} homes and the State count is {N(pd["permitted_total"])}. At the first rate, Providence is permitting {c24["total"]/pv["goal_per_year"]:.0%} of what its goal asks. At the second, it is on pace.</p>')
    b.append(f'<p>The gap runs statewide. The Census count for all 39 cities and towns in 2024 is {N(sw_c24)} homes; the State&#8217;s is {N(sw_d["permitted"][2])}. In {len(imputed24)} towns the Census figure is partly the Bureau&#8217;s own estimate, because the town did not report every month: {", ".join(imputed24)}. The State&#8217;s report says its survey covered 38 of the 39 municipalities and used the Census figure for the last one. It does not say which. The Housing 2030 goals are written in permits, and the plan does not say which survey will be used to measure them.</p>')
    rows = sorted(st["towns"], key=lambda t: -t["goal_per_year"])
    same = [t for t in rows if t["census"]["2024"]["total"] == t["doh_2024"]["permitted_total"]]
    gaps = sorted(rows, key=lambda t: -abs(t["doh_2024"]["permitted_total"] - t["census"]["2024"]["total"]))
    g1, g2 = gaps[0], gaps[1]
    gap = lambda t: abs(t["doh_2024"]["permitted_total"] - t["census"]["2024"]["total"])
    b.append(f'<p>In {len(same)} of the 39 the two counts match exactly. The widest gaps are in {g1["town"]}, {N(gap(g1))} homes, and {g2["town"]}, {N(gap(g2))}.</p>')
    b.append('<div class="tablewrap"><table><tr><th>City or town</th><th class="n">Goal per year</th><th class="n">2024, Census</th><th class="n">2024, State</th></tr>')
    for t in rows:
        cc = t["census"]["2024"]; mark = "*" if cc["months"] < 12 else ""
        b.append(f'<tr><td>{e(t["town"])}</td><td class="n">{N(t["goal_per_year"])}</td><td class="n">{N(cc["total"])}{mark}</td><td class="n">{N(t["doh_2024"]["permitted_total"])}</td></tr>')
    b.append(f'<tr class="total"><td>Statewide</td><td class="n">{N(sum(t["goal_per_year"] for t in rows))}</td><td class="n">{N(sw_c24)}</td><td class="n">{N(sw_d["permitted"][2])}</td></tr></table></div>')
    b.append('<p class="cite">Goal per year: the five-year goal divided by five. Census: Building Permits Survey, annual place file for 2024, new privately owned housing units authorized; * the town reported fewer than 12 months and the figure includes the Bureau&#8217;s estimate. State: RI Department of Housing, 2024 Integrated Housing Report, Figure 2.3. Every town and year since 2000: <a href="data/census-permits-ri.csv">census-permits-ri.csv</a>.</p>')

    b.append('<h2>How the State counts what got built</h2>')
    b.append(f'<p>A permit is not a home. To count homes finished, the State&#8217;s 2024 report uses a formula. For single-family houses it takes the year before&#8217;s permits and multiplies by 0.66, the share of New England single-family permits that become houses within a year in a national Census survey. For apartments it counts certificates of occupancy, but only those reported for developments with affordable units. For Providence that gives {N(pd["completed_single_est"])} houses and {N(pd["completed_multi_cos"])} apartments, {N(pd["completed_total"])} in all. The {N(pd["completed_multi_cos"])} apartments are four affordable developments: Copley Chambers II and III (124), Joseph Caffey Apartments (39), Portland Homes (5) and one unit at 1192 Westminster St. An apartment building with no affordable units that opened in 2024 is not in the count.</p>')
    b.append('<p>The report says so itself: the method &#8220;does not capture the full set of multifamily completions in the state.&#8221;</p>')
    b.append('<p class="cite">RI Department of Housing, 2024 Integrated Housing Report (Apr. 15, 2025), pp. 5, 16 and 19&#8211;20, Figures 2.1 and 2.4.</p>')

    b.append('<h2>What Providence told the Census</h2>')
    b.append('<p>The City&#8217;s own permit records, published through 2019, can be set against what it reported to the Census in the same years. In 2017 the City reported 4 new homes to the Census. Its permit records for 2017 include a 15-story, 202-apartment building at 169 Canal St. In 2018 it reported 1. In 2023, reporting all 12 months, it reported 5.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Year</th><th class="n">Reported to the Census</th><th class="n">City permit records</th><th class="n">Built, by the assessor</th></tr>')
    for y in range(2010, 2026):
        cy = pv["census"].get(str(y), {}).get("total")
        b.append(f'<tr><td>{y}</td><td class="n">{N(cy) if cy is not None else "–"}</td><td class="n">{N(city[str(y)]) if str(y) in city else "–"}</td><td class="n">{N(built[str(y)]["units"]) if str(y) in built else "–"}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">Census: Building Permits Survey, Providence, units authorized. City permit records: Department of Inspections and Standards permits, 2009&#8211;2019 (data.providenceri.gov), building permits for new housing; homes counted from each permit&#8217;s class and description, renewals and foundation-only permits not counted, a project filed on several lots counted once. Every permit, with how its homes were counted: <a href="data/permits-new-housing-2009-2019.csv">permits-new-housing-2009-2019.csv</a>. Built: see below. The City stopped publishing permits after 2019.</p>')

    b.append('<h2>What got built, parcel by parcel</h2>')
    R = bs["by_regime"]; tsa = R.get("tax stabilization agreement", {"parcels": 0, "units": 0})
    big = [x for x in bs["largest"] if x["kind"] != "student housing"]
    big_units = sum(x["units"] for x in big); big_tsa = sum(x["units"] for x in big if x["levy_code"] == "TSA")
    b.append(f'<p>The Tax Assessor records the year each building went up and how many homes it holds. By that record, {N(bs["units"])} homes in Providence are in buildings put up from 2010 through 2023, on {N(bs["parcels"])} parcels. That includes {N(bs["student_units"])} the assessor records in student housing; it leaves out {len(bs["lodging_set_aside"])} hotel parcels. {N(tsa["units"])} of the homes, {tsa["units"]/bs["units"]:.0%}, sit on {tsa["parcels"]} parcels under tax stabilization agreements. In the {len(big)} new buildings with 20 or more homes, not counting student housing, {N(big_tsa)} of {N(big_units)} homes, {big_tsa/big_units:.0%}, are on parcels with an agreement.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Address</th><th class="n">Built</th><th class="n">Homes</th><th>Taxed under</th></tr>')
    for x in bs["largest"]:
        reg = "student housing, exempt" if x["kind"] == "student housing" else x["regime"]
        b.append(f'<tr><td>{e(x["address"])}</td><td class="n">{x["year_built"]}</td><td class="n">{x["units"]}</td><td>{e(reg)}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">City of Providence assessor&#8217;s parcel extract, provided Sept. 10, 2026, from data pulled early in 2025; joined by parcel to the 2025 tax roll. The assessor&#8217;s office cautions that year built is the least reliable field it keeps. A building converted to apartments keeps its original year and does not appear here, and a parcel renumbered after its permit was issued may not match. Every parcel: <a href="data/built-since-2010.csv">built-since-2010.csv</a>. Tax agreements: <a href="../off-the-roll/">Off the Roll</a>.</p>')

    b.append('<h2>Not yet on the record</h2><ul class="open">'
             '<li>Every building permit for new homes in Providence since 2020, with its parcel and number of homes. The City keeps them in an online permit system whose public search is one record at a time.</li>'
             '<li>Every certificate of occupancy the City has issued since 2020: the count of homes actually finished.</li>'
             f'<li>Which permits make up the {N(pd["permitted_total"])} homes the City reported to the State for 2024, and why its Census reports for the same year add to {N(c24["total"])}.</li>'
             '<li>Which count the State will use to judge the Housing 2030 goals.</li></ul>')
    b.append('<h2>Data</h2><p>' + " · ".join(f'<a href="data/{f}">{f}</a>' for f in FILES) + '</p></main>')

    (SITE / "housing/data").mkdir(parents=True, exist_ok=True)
    (SITE / "housing/index.html").write_text(page("Housing — Providence, on the record",
        "How many homes Providence permits and builds, by three government counts that disagree, and what the State's Housing 2030 goal asks.",
        "../", "".join(b), "housing/"))
    for f in FILES:
        shutil.copy(H / f, SITE / "housing/data" / f)
    return dict(goal=pv["goal_2026_2030"], doh=pd["permitted_total"], census=c24["total"])
