"""Providence's basement floods: the section folded into the held /flood/ page. B1396, Oct 29 2026.
Folds four results from ../datasets/derived/openfema/providence_floods (README sections B951, B960, B962, B962a, B1034)
into flood.py's page, after "The next one". HELD with the rest of /flood/: flood.RELEASE governs it, and its [C] marks
block a release the same way. Every number is read from the JSON/CSV the blocks wrote; the asserts pin the figures the
prose states, so an upstream rerun that moves a number stops the build instead of silently changing a sentence.
"""
import json, pathlib

P = pathlib.Path(__file__).parent.parent / "datasets" / "derived" / "openfema" / "providence_floods"
FILES = ["pvd_summary.json", "b960.json", "b962.json", "b962a.json", "b1034.json",
         "pvd_bg.csv", "nfip_claims_bg.csv", "b962a_compare.csv", "renters_bg.csv"]


def section(C, M, N, P_):
    J = lambda f: json.load(open(P / f))
    s = J("pvd_summary.json"); a = J("b960.json"); t = J("b962.json"); x = J("b962a.json"); r = J("b1034.json")
    al = s["by_dr"]["all"]; c = s["city"]
    a18, ac = a["repeat18"], a["city"]
    t18, tc = t["repeat18"], t["city"]
    p10, p24 = x["pooled_18"]["2010"], x["pooled_18"]["2023-24"]
    r18, rc = r["repeat18"], r["city"]
    share45 = t18["flood_1894"] / tc["flood_1894"]; hh15 = t18["hh"] / tc["hh"]
    nfip_all = sum(v["paid"] for v in a["by_dr"].values()); nfip_n = sum(v["claims"] for v in a["by_dr"].values())
    bsm = [k for k in a["claims_rows"] if k["basementEnclosureCrawlspaceType"] in (1, 2)]
    bsm_paid = [k["paid"] for k in bsm if k["paid"] > 0]

    # pin the prose to the data
    assert (int(al["registrants"]), int(al["flood"]), int(al["basement"]), c["repeat_bgs"], c["repeat_bgs_flood"]) == (578, 143, 121, 18, 81)
    assert (ac["ihp_basement"], ac["ihp_basement_insured"], ac["nfip_claims"], ac["nfip_basement_claims"]) == (121, 3, 11, 3)
    assert (a18["nfip_claims"], a18["nfip_basement_claims"], a18["bgs_with_claims"], a["occupancy_counts"]["18"], a["zone_counts"]["AE"]) == (4, 0, 2, 8, 9)
    assert (M(a18["nfip_paid"], 2), M(nfip_all, 2), nfip_n, len(bsm), len(bsm_paid), round(sum(bsm_paid), -3)) == ("$1.06M", "$2.24M", 12, 3, 2, 112000)
    assert [k["occupancyType"] for k in bsm if k["paid"] > 0] == [18, 18] and [k["paid"] for k in bsm if k["occupancyType"] == 11] == [0.0]
    assert int(x["upper_bound_same_households_18"]) == 59 and int(p24["flood_n"]) == 81
    assert (round(tc["flood_1894"]), P_(tc["basement_1894"] / tc["flood_1894"]), t18["bgs_hit_1894"], P_(share45), P_(hh15)) == (538, "94%", 16, "45%", "15%")
    assert (t18["flood_1894_per_1000hh"], t["other"]["flood_1894_per_1000hh"], t["events4_counts"]["4"]) == (21.8, 4.92, 4)
    assert (P_(p24["homeowners_insured"]), P_(p24["flood_insured"]), P_(p10["water_6in_plus"]), P_(p24["water_6in_plus"])) == ("79%", "1%", "26%", "11%")
    assert (r18["fema_basement_renters"], r18["fema_basement"], P_(r18["renter_hh_share"]), r18["acs_renter_hh"], r18["tenant_pol_4766"], r18["tenant_pol_now"]) == (2, 64, "46%", 5096, 2, 1)

    b = ['<h2>Providence: the basements</h2>']
    b.append(f'<p>Providence flooded too, but not the way Kent County did. Three storms brought federal declarations between September 2023 and January 2024 (DR-4753, DR-4765, DR-4766). In the city, {N(int(al["registrants"]))} households registered with FEMA. FEMA recorded flood damage at {int(al["flood"])} of them, and for {int(al["basement"])} of those the water was in the basement.</p>')
    b.append(f'<p>The flooded basements were not by the rivers. Block groups whose center sits 100 feet or more above sea level had {s["by_elevation"]["100+"]["flood_per_1000hh"]:.1f} flood-damaged registrants per 1,000 households; those under 20 feet had {s["by_elevation"]["<20"]["flood_per_1000hh"]:.1f}. {C("Water in a basement on a hill came up through the floor drain or the foundation: the sewer backing up, or groundwater.")}</p>')
    b.append(f'<p>Eighteen of the city&#8217;s 153 block groups flooded in two or three of the storms. Those eighteen hold {c["repeat_bgs_flood"]} of the {int(al["flood"])} flood-damaged households.</p>')
    b.append('<p class="cite">OpenFEMA Individuals and Households Program valid registrations (v2), Providence tracts 0001&#8211;0037, by 2020 census block group; USGS 3DEP elevation at each block group&#8217;s internal point. <a href="data/pvd_bg.csv">pvd_bg.csv</a>, <a href="data/pvd_summary.json">pvd_summary.json</a>. (B951)</p>')

    b.append('<h3>Almost none of it was insured</h3>')
    b.append(f'<p>Of the {ac["ihp_basement"]} households with a flooded basement, {ac["ihp_basement_insured"]} had flood insurance. {P_(p24["homeowners_insured"])} of the flooded households in the eighteen block groups had homeowners insurance, which doesn&#8217;t cover flood; {P_(p24["flood_insured"])} had flood insurance.</p>')
    b.append(f'<p>Flood insurance did pay out in Providence on those storm dates: {nfip_n} claims, {M(nfip_all, 2)}. {a["occupancy_counts"]["18"]} of the 12 were non-residential buildings, and {a["zone_counts"]["AE"]} were in the high-risk river zone (AE). Citywide, {len(bsm)} claims involved a basement. The {len(bsm_paid)} that paid, ${round(sum(bsm_paid), -3):,.0f} between them, were both non-residential buildings. The one house with a basement claim was paid nothing. In the eighteen block groups, {a18["nfip_claims"]} claims paid {M(a18["nfip_paid"], 2)}, all in the AE river zone, and none for a basement. Sixteen of the eighteen had no claim at all.</p>')
    b.append(f'<p>{C("The flood insurance money went mostly to commercial and larger residential buildings on the rivers. The basements on the hills were paid for by the people who owned them.")}</p>')
    b.append('<p class="cite">OpenFEMA NFIP redacted claims (v3), Providence County, losses dated Sep 10&#8211;14 2023, Dec 17&#8211;20 2023 and Jan 9&#8211;14 2024; file as of Sep 8, 2026. One claim ($170,822) carries a 2010 block group and is counted in the city total but not placed. FEMA&#8217;s insurance flags from the IHP file above. <a href="data/b960.json">b960.json</a>, <a href="data/nfip_claims_bg.csv">nfip_claims_bg.csv</a>. (B960; homeowners-insurance share B962a)</p>')

    b.append('<h3>The same block groups flooded in 2010</h3>')
    b.append(f'<p>In March 2010 (DR-1894), about {round(tc["flood_1894"])} Providence households registered flood damage with FEMA, {P_(tc["basement_1894"] / tc["flood_1894"])} of them in the basement. {t18["bgs_hit_1894"]} of the eighteen block groups were hit then too. They took {P_(share45)} of the city&#8217;s 2010 flood registrations while holding {P_(hh15)} of its households: {t18["flood_1894_per_1000hh"]:.1f} per 1,000 households, against {t["other"]["flood_1894_per_1000hh"]:.1f} in the rest of the city. Four block groups flooded in all four storms: two in Elmhurst, one in Washington Park, one in Silver Lake.</p>')
    b.append('<p class="cite">OpenFEMA IHP valid registrations (v2), DR-1894, Providence County, 2010 block groups placed on 2020 block groups by land-area share (Census Bureau 2020&#8211;2010 block group relationship file), so 2010 counts are allocations. <a href="data/b962.json">b962.json</a>. (B962)</p>')

    b.append('<h3>Same homes, or same streets?</h3>')
    b.append(f'<p>FEMA&#8217;s public file can&#8217;t say. Its finest location is the block group: no address, no street, nothing that follows a household from one disaster to the next. What it can say is a limit. At most {int(x["upper_bound_same_households_18"])} of the {int(p24["flood_n"])} flood-damaged households of 2023&#8211;24 in the eighteen could have been 2010 registrants in the same block group. At least 22 were not.</p>')
    b.append(f'<p>Leave out one block group in Wanskuck, where 12 apartments flooded on the first floor in September 2023, and {C('the rest look like 2010: owner-occupied houses with water in the basement, in the same block groups.')} The water was shallower this time. {P_(p10["water_6in_plus"])} of 2010&#8217;s flooded households in the eighteen had six inches or more; {P_(p24["water_6in_plus"])} in 2023&#8211;24.</p>')
    b.append(f'<p>{C("FEMA&#8217;s damage dollars don&#8217;t compare across the two floods. They are inspection schedule values, and the schedule changed.")}</p>')
    b.append('<p class="cite">OpenFEMA IHP valid registrations (v2) field list (100 fields); the 2010 and 2023&#8211;24 registrants in the eighteen, side by side. <a href="data/b962a.json">b962a.json</a>, <a href="data/b962a_compare.csv">b962a_compare.csv</a>. (B962a)</p>')

    b.append('<h3>Renters</h3>')
    b.append(f'<p>Renters are {P_(r18["renter_hh_share"])} of the households in the eighteen block groups and {r18["fema_basement_renters"]} of the {r18["fema_basement"]} households FEMA recorded with a flooded basement there. {C("That is more likely a gap in who registers, and in how a shared basement gets recorded, than a sign renters were spared.")}</p>')
    b.append(f'<p>A renter&#8217;s own flood cover is a tenant (contents) policy. On the day of the January 2024 storm, the eighteen block groups held {r18["tenant_pol_4766"]} of them, for {N(r18["acs_renter_hh"])} renter households. On July 1, 2026, they held {r18["tenant_pol_now"]}. None of the {rc["fema_flood_renters"]} renters FEMA recorded with flood damage in the city had flood insurance.</p>')
    b.append('<p class="cite">Census Bureau ACS 2020&#8211;24 5-year, table B25003, by block group; OpenFEMA NFIP redacted policies (v3), tenant policies in force on each storm day and July 1, 2026. <a href="data/b1034.json">b1034.json</a>, <a href="data/renters_bg.csv">renters_bg.csv</a>. (B1034)</p>')

    b.append('<h2>Not yet on the record (Providence)</h2><ul class="open">'
             '<li>Which flooded streets are on the combined sewer. The Narragansett Bay Commission has the map; no public copy turned up.</li>'
             '<li>Whether the same houses flooded in 2010 and 2023&#8211;24. That needs addresses, which FEMA and the city hold and don&#8217;t publish.</li></ul>')
    return "".join(b)
