"""Housing section for providenceontherecord.org. Rendered from ../housing/data.
Called from build.py: housing.render(page, e, SITE, DATELINE).
Section name and slug ("Housing", /housing/) are placeholders pending Liam's call.
"""
import json, csv, shutil, pathlib

H = pathlib.Path(__file__).parent.parent / "housing" / "data"
FILES = ["statewide.json", "two-counts-by-town.csv", "census-permits-ri.csv", "state-survey-permits.csv", "permits-new-housing-2009-2019.csv",
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
    p25 = pv["doh_2025"]["permitted"]; co25 = pv["doh_2025"]["certificates_of_occupancy"]; c25 = pv["census"]["2025"]
    sw25 = st["doh_2025_statewide"]; sw_c25 = sum(t["census"]["2025"]["total"] for t in st["towns"])
    imputed25 = sorted(t["town"] for t in st["towns"] if t["census"]["2025"]["months"] < 12)
    inc25 = sw25["survey_incomplete"]
    N = lambda x: f"{x:,}"
    L = lambda xs: ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else "".join(xs)

    b = [f'<main><div class="dateline">{DATELINE}</div>']
    b.append('<p class="cite" style="border-left:3px solid var(--record);padding-left:10px">Correction, Oct. 1, 2026: An earlier version of this page was built on the State&#8217;s 2024 housing report and said the State estimates how many homes get built with a formula instead of counting them. The State&#8217;s 2025 report, published Apr. 15, 2026, counts certificates of occupancy reported by each city and town. This page now leads with the 2025 report; the 2024 figures remain below.</p>')
    b.append(f'<h1>Providence Permitted {N(p25["total"])} New Homes in 2025, or {N(c25["total"])}, Depending on Which Government Count You Read</h1>')
    b.append(f'<p class="deck">The State has set Providence a goal of {N(pv["goal_2026_2030"])} new homes over the next five years. The State&#8217;s housing report and the Census Bureau disagree on how many the City permits now, by more than two to one.</p>')
    b.append('<p class="byline">By Liam Freaney · from the Census Bureau, the RI Executive Office of Housing and the City&#8217;s own records</p>')
    b.append('<div class="big">'
             f'<div><b>{N(pv["goal_2026_2030"])}</b><span>homes the State expects Providence to permit, 2026&#8211;2030</span></div>'
             f'<div><b>{N(p25["total"])}</b><span>permitted in 2025, by the State&#8217;s survey of the City</span></div>'
             f'<div><b>{N(c25["total"])}</b><span>permitted in 2025, by the City&#8217;s reports to the Census</span></div>'
             f'<div><b>{N(co25["total"])}</b><span>certificates of occupancy in 2025, by the State&#8217;s survey of the City</span></div></div>')

    b.append('<h2>The goal</h2>')
    b.append(f'<p>Under Housing 2030, the State&#8217;s housing plan, each city and town is expected to permit new homes equal to a share of its housing each year: 0.4 percent for towns without many jobs or much transit, 0.6 percent for towns with more jobs, and 0.8 percent for places with both. Providence is in the third group. Its goal is {N(pv["goal_2026_2030"])} homes from 2026 through 2030, about {N(pv["goal_per_year"])} a year, of which {N(pv["affordable_goal_2026_2030"])} are to be affordable.</p>')
    b.append('<p class="cite">RI Department of Housing, Housing 2030 municipal growth categories and production goals (housing.ri.gov/media/3401). Providence&#8217;s goal is 0.8 percent of 75,257 homes, times five years.</p>')

    b.append('<h2>Two counts of the same permits</h2>')
    b.append(f'<p>Two government surveys count the building permits each city issues for new homes. The Census Bureau&#8217;s Building Permits Survey takes what each city reports, month by month. The State&#8217;s Department of Housing, renamed the Executive Office of Housing in 2025, surveys each city once a year, and its report says it uses that survey because it is &#8220;more accurate than the Census survey.&#8221; For Providence in 2025, the Census count is {N(c25["total"])} homes and the State count is {N(p25["total"])}. Measured against the goal&#8217;s yearly pace, which starts in 2026, the first is {c25["total"]/pv["goal_per_year"]:.0%} of it and the second {p25["total"]/pv["goal_per_year"]:.0%}. In 2024 the two counts were {N(c24["total"])} and {N(pd["permitted_total"])}.</p>')
    b.append(f'<p>The gap runs statewide. The Census count for all 39 cities and towns in 2025 is {N(sw_c25)} homes; the State&#8217;s is {N(sw25["permitted"]["total"])}. In {len(imputed25)} towns the Census figure is partly the Bureau&#8217;s own estimate, because the town did not report every month: {L(imputed25)}. The State&#8217;s 2025 report marks {len(inc25)} municipalities as not having completed its survey before publication, {L(inc25)}, and still prints permit and occupancy figures for each of them without saying where those came from. The Housing 2030 goals are written in permits, and the plan does not say which survey will be used to measure them.</p>')
    rows = sorted(st["towns"], key=lambda t: -t["goal_per_year"])
    s25 = lambda t: t["doh_2025"]["permitted"]["total"]
    same = [t for t in rows if t["census"]["2025"]["total"] == s25(t)]
    gap = lambda t: abs(s25(t) - t["census"]["2025"]["total"])
    gaps = sorted(rows, key=lambda t: -gap(t))
    g1, g2 = gaps[0], gaps[1]
    b.append(f'<p>In {len(same)} of the 39 the two counts match exactly. The widest gaps are in {g1["town"]}, {N(gap(g1))} homes, and {g2["town"]}, {N(gap(g2))}.</p>')
    b.append('<div class="tablewrap"><table><tr><th>City or town</th><th class="n">Goal per year</th><th class="n">2025, Census</th><th class="n">2025, State</th></tr>')
    for t in rows:
        cc = t["census"]["2025"]; mark = "*" if cc["months"] < 12 else ""
        smark = "&#8224;" if not t["doh_2025"]["survey_complete"] else ""
        b.append(f'<tr><td>{e(t["town"])}</td><td class="n">{N(t["goal_per_year"])}</td><td class="n">{N(cc["total"])}{mark}</td><td class="n">{N(s25(t))}{smark}</td></tr>')
    b.append(f'<tr class="total"><td>Statewide</td><td class="n">{N(sum(t["goal_per_year"] for t in rows))}</td><td class="n">{N(sw_c25)}</td><td class="n">{N(sw25["permitted"]["total"])}</td></tr></table></div>')
    b.append('<p class="cite">Goal per year: the five-year goal divided by five. Census: Building Permits Survey, annual place file for 2025, new privately owned housing units authorized; * the town reported fewer than 12 months and the figure includes the Bureau&#8217;s estimate. State: RI Executive Office of Housing, 2025 Integrated Housing Report (Apr. 15, 2026), Figure 2.1; &#8224; marked in Figure 2.3 as not having completed the survey before publication. Every town and year since 2000: <a href="data/census-permits-ri.csv">census-permits-ri.csv</a>.</p>')

    ms = lambda c: c.get("u2", 0) + c.get("u34", 0) + c.get("u5", 0)
    S2 = sum(ms(t["doh_2025"]["permitted"]) for t in st["towns"]); C2 = sum(ms(t["census"]["2025"]) for t in st["towns"])
    S1 = sum(t["doh_2025"]["permitted"]["u1"] for t in st["towns"]); C1 = sum(t["census"]["2025"]["u1"] for t in st["towns"])
    zeros = sorted(t["town"] for t in st["towns"] if ms(t["doh_2025"]["permitted"]) >= 20 and ms(t["census"]["2025"]) == 0)
    pk = towns["Pawtucket"]; mt = towns["Middletown"]
    pk_max = max(abs(pk["state_survey"][str(y)]["net_of_adu"] - pk["census"][str(y)]["total"]) for y in range(2018, 2024))
    assert all(mt["state_survey"][str(y)]["net_of_adu"] == mt["census"][str(y)]["total"] for y in range(2018, 2024))
    mgap = sorted(st["towns"], key=lambda t: -(ms(t["doh_2025"]["permitted"]) - ms(t["census"]["2025"])))[:10]
    b.append('<h2>The gap is apartments</h2>')
    b.append(f'<p>Split by building size, most of the 2025 difference is in buildings of two or more homes. Across the 39 cities and towns the State&#8217;s survey has {N(S2)} homes permitted in such buildings and the Census count has {N(C2)}, a difference of {N(S2 - C2)}. For single-family houses the two are {N(S1)} and {N(C1)}, a difference of {N(S1 - C1)}. In {len(zeros)} towns the State reports 20 or more homes in multifamily buildings and the Census reports none: {L(zeros)}.</p>')
    b.append(f'<p>It was not always so. Pawtucket&#8217;s two counts were never more than {pk_max} homes apart in any year from 2018 through 2023. In 2024 the State recorded {N(pk["doh_2024"]["permitted_multi"])} homes in its multifamily buildings and the Census recorded {N(ms(pk["census"]["2024"]))}; in 2025 the figures were {N(ms(pk["doh_2025"]["permitted"]))} and {N(ms(pk["census"]["2025"]))}. Middletown&#8217;s counts matched exactly every year from 2018 through 2023, then split by {N(mt["doh_2024"]["permitted_total"] - mt["census"]["2024"]["total"])} homes in 2024.</p>')
    b.append('<p>The two surveys do not say why. The Census count is built from what each city reports; the State&#8217;s comes from its own annual survey of each city. Records requests to Pawtucket for its reports to both, filed Oct. 2, 2026, are meant to show what the city sent each of them.</p>')
    b.append('<div class="tablewrap"><table><tr><th>City or town</th><th class="n">2024, State</th><th class="n">2024, Census</th><th class="n">2025, State</th><th class="n">2025, Census</th></tr>')
    for t in mgap:
        b.append(f'<tr><td>{e(t["town"])}</td><td class="n">{N(t["doh_2024"]["permitted_multi"])}</td><td class="n">{N(ms(t["census"]["2024"]))}</td><td class="n">{N(ms(t["doh_2025"]["permitted"]))}</td><td class="n">{N(ms(t["census"]["2025"]))}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">Homes permitted in buildings of two or more homes, the ten towns with the largest 2025 difference between the State and the Census. State 2025: RI Executive Office of Housing, 2025 Integrated Housing Report, Figure 2.1 (two-family, three-or-four-family and five-or-more columns). State 2024: RI Department of Housing, 2024 Integrated Housing Report, Figure 2.1, the &#8220;multi&#8221; column as printed. Census: Building Permits Survey annual place files, 2024 and 2025, buildings of two or more homes. Every town: <a href="data/two-counts-by-town.csv">two-counts-by-town.csv</a>.</p>')

    b.append('<h2>How the State counts what got built</h2>')
    b.append(f'<p>A permit is not a home. For 2025 the State counts homes finished by asking each city and town how many certificates of occupancy it issued, the document that lets people move in. Providence reported {N(co25["total"])}: {N(co25["u1"])} single-family houses, {N(co25["u2"])} homes in two-family buildings, {N(co25["u34"])} in buildings of three or four, and {N(co25["u5"])} in buildings of five or more. Statewide the count is {N(sw25["certificates_of_occupancy"]["total"])}. The report says the State had not tracked this before, &#8220;so there is no historical data available for comparison.&#8221;</p>')
    b.append(f'<p>The 2024 report used a formula instead. For single-family houses it took the year before&#8217;s permits and multiplied by 0.66, the share of New England single-family permits that become houses within a year in a national Census survey. For apartments it counted certificates of occupancy, but only for developments with affordable units, and said the method &#8220;does not capture the full set of multifamily completions in the state.&#8221; For Providence in 2024 that gave {N(pd["completed_single_est"])} houses and {N(pd["completed_multi_cos"])} apartments, {N(pd["completed_total"])} in all; the {N(pd["completed_multi_cos"])} apartments were four affordable developments: Copley Chambers II and III (124), Joseph Caffey Apartments (39), Portland Homes (5) and one unit at 1192 Westminster St. The two years are not comparable.</p>')
    b.append('<p class="cite">RI Executive Office of Housing, 2025 Integrated Housing Report (Apr. 15, 2026), pp. 15&#8211;20, Figures 2.1, 2.3 and 2.4. RI Department of Housing, 2024 Integrated Housing Report (Apr. 15, 2025), pp. 5, 16 and 19&#8211;20, Figures 2.1 and 2.4.</p>')

    BY = st["two_counts_by_year"]
    ss = pv["state_survey"]
    stv = lambda y: p25["total"] if y == 2025 else (pd["permitted_total"] if y == 2024 else ss[str(y)]["net_of_adu"]) if (y == 2024 or str(y) in ss) else None
    gap_all = sum(v["state"] - v["census"] for v in BY.values())
    gap_pv = sum(v["providence_state"] - v["providence_census"] for v in BY.values())
    pc7 = sum(v["providence_census"] for v in BY.values()); ps7 = sum(v["providence_state"] for v in BY.values())
    b.append('<h2>What Providence told the Census and the State</h2>')
    b.append(f'<p>Both surveys get their numbers from the City. From 2018 through 2025, Providence&#8217;s reports to the Census add to {N(pc7)} homes and its answers to the State&#8217;s survey add to {N(ps7)}. They matched once, in 2022. In 2018 the City reported 1 new home to the Census and {N(stv(2018))} to the State; its own published permit records for that year add to {N(city["2018"])}. In 2023 it reported 5 to the Census, with all 12 months filed, and {N(stv(2023))} to the State. In 2017, a year it reported 4 homes to the Census, its permit records include a 15-story, 202-apartment building at 169 Canal St.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Year</th><th class="n">To the Census</th><th class="n">To the State</th><th class="n">City permit records</th><th class="n">Built, by the assessor</th></tr>')
    for y in range(2010, 2026):
        cy = pv["census"].get(str(y), {}).get("total"); sy = stv(y) if 2018 <= y <= 2025 else None
        b.append(f'<tr><td>{y}</td><td class="n">{N(cy) if cy is not None else "–"}</td><td class="n">{N(sy) if sy is not None else "–"}</td><td class="n">{N(city[str(y)]) if str(y) in city else "–"}</td><td class="n">{N(built[str(y)]["units"]) if str(y) in built else "–"}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">To the Census: Building Permits Survey, Providence, units authorized. To the State: HousingWorks RI Housing Fact Books 2019&#8211;2024 (each reports the year before; the State&#8217;s survey was run by HousingWorks RI until the Department of Housing took it over), not counting accessory dwelling units, for 2024 the Department of Housing&#8217;s 2024 report, Figure 2.3, and for 2025 the Executive Office of Housing&#8217;s 2025 report, Figure 2.1. City permit records: Department of Inspections and Standards permits, 2009&#8211;2019 (data.providenceri.gov), building permits for new housing; homes counted from each permit&#8217;s class and description, renewals and foundation-only permits not counted, a project filed on several lots counted once. Every permit, with how its homes were counted: <a href="data/permits-new-housing-2009-2019.csv">permits-new-housing-2009-2019.csv</a>. Built: see below. The City stopped publishing permits after 2019.</p>')
    b.append(f'<p>More than half of the statewide difference between the two surveys is Providence, though less of it in 2025 than before. Over the eight years the State&#8217;s count runs {N(gap_all)} homes above the Census count for Rhode Island as a whole; {N(gap_pv)} of those, {gap_pv/gap_all:.0%}, are in Providence.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Year</th><th class="n">Rhode Island, Census</th><th class="n">Rhode Island, State</th><th class="n">Towns where the two agree</th><th class="n">Providence&#8217;s share of the gap</th></tr>')
    for y, v in BY.items():
        sh = "–" if v["providence_share_of_gap"] is None else f'{v["providence_share_of_gap"]:.0%}'
        b.append(f'<tr><td>{y}</td><td class="n">{N(v["census"])}</td><td class="n">{N(v["state"])}</td><td class="n">{v["match"]} of 39</td><td class="n">{sh}</td></tr>')
    b.append(f'<tr class="total"><td>2018&#8211;2025</td><td class="n">{N(sum(v["census"] for v in BY.values()))}</td><td class="n">{N(sum(v["state"] for v in BY.values()))}</td><td class="n"></td><td class="n">{gap_pv/gap_all:.0%}</td></tr></table></div>')
    b.append('<p class="cite">Same sources, summed over all 39 cities and towns. A share above 100 percent means other towns&#8217; differences ran the other way. Every town and year, both counts: <a href="data/statewide.json">statewide.json</a> and <a href="data/state-survey-permits.csv">state-survey-permits.csv</a>.</p>')

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
             '<li>What Pawtucket reported to the Census and to the State for 2023 through 2025, and every permit and certificate of occupancy it has issued for new homes since 2018. Asked Oct. 2, 2026.</li>'
             '<li>Every building permit for new homes in Providence since 2020, with its parcel and number of homes. The City keeps them in an online permit system whose public search is one record at a time.</li>'
             f'<li>Every certificate of occupancy the City has issued since 2020, by address. The State now publishes a yearly total, {N(co25["total"])} for 2025, but not the buildings behind it.</li>'
             f'<li>Which permits make up the {N(p25["total"])} homes the City reported to the State for 2025, and why its Census reports for the same year add to {N(c25["total"])}. The City and the State were asked about 2024 on Oct. 1, 2026, and the State again about 2025 the same day.</li>'
             f'<li>Where the State&#8217;s 2025 figures come from for the {len(inc25)} towns that had not completed its survey. Asked Oct. 1, 2026.</li>'
             '<li>Which count the State will use to judge the Housing 2030 goals. Asked Oct. 1, 2026.</li></ul>')
    b.append('<h2>Data</h2><p>' + " · ".join(f'<a href="data/{f}">{f}</a>' for f in FILES) + '</p></main>')

    (SITE / "housing/data").mkdir(parents=True, exist_ok=True)
    (SITE / "housing/index.html").write_text(page("Housing — Providence, on the record",
        "How many homes Providence permits and builds, by three government counts that disagree, and what the State's Housing 2030 goal asks.",
        "../", "".join(b), "housing/"))
    for f in FILES:
        shutil.copy(H / f, SITE / "housing/data" / f)
    return dict(goal=pv["goal_2026_2030"], doh=p25["total"], census=c25["total"])
