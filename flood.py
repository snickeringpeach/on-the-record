"""Who pays for the next flood. B694, Oct 19 2026, from Liam's draft drafts/flood/flood-page-v1.md (B693).
Rendered from ../datasets/derived/openfema/kent_2010 (README sections B638, B667, B688-B692);
the Providence section (B1396) from ../datasets/derived/openfema/providence_floods via flood_pvd.py.
Called from build.py: flood.render(page, e, SITE, DATELINE) -- ONLY when RELEASE is True, or for a local look
with FLOOD_PREVIEW=1 python3 build.py (./deploy wipes site/ and rebuilds without it, so a preview never ships).

HELD. RELEASE stays False until Liam says "ship it". Before that:
  - section 5 ("What would change it") is his: fill SECTION_5 below;
  - every [C] line (Claude's framing, marked class="cmark" on the preview) is taken, rewritten or cut;
  - RIEMA's repetitive-loss answer (APRA Oct 18, due ~Nov 2) goes into section 2, or the open question stays;
  - slug (/flood/) and its place in the home feed are his call.
render() refuses to build with RELEASE=True while any [C] mark or empty section 5 remains.
"""
import csv, json, pathlib, shutil
import flood_pvd

K = pathlib.Path(__file__).parent.parent / "datasets" / "derived" / "openfema" / "kent_2010"
RELEASE = False
SECTION_5 = ""   # Liam's. Plain HTML paragraphs.
FILES = ["then_and_now.json", "then_and_now_towns.csv", "summary.json", "summary_sba.json", "sba_1894_by_town.csv",
         "hma_ri_towns.csv", "hma_ri_projects.csv", "summary_bg.json", "bg_2010_vs_2023_24.csv",
         "takeup.json", "takeup_town_year.csv", "why_fell.csv", "replay.json", "replay_by_town.csv"]

def C(s):
    """Claude's framing, still waiting on Liam's read."""
    return f'<span class="cmark" style="background:var(--harbor-soft)" title="Claude&#8217;s wording, not yet Liam&#8217;s">[C] {s}</span>'

def render(page, e, SITE, DATELINE):
    J = lambda f: json.load(open(K / f))
    tn = J("then_and_now.json"); sm = J("summary.json"); sb = J("summary_sba.json"); bg = J("summary_bg.json")
    tk = J("takeup.json"); rp = J("replay.json")
    sba_town = {r["town"]: r for r in csv.DictReader(open(K / "sba_1894_by_town.csv"))}
    M = lambda x, d=1: f"${x/1e6:.{d}f}M"
    N = lambda x: f"{x:,}"
    P = lambda x: f"{abs(x):.0%}"

    y10 = tn["2010 (DR-1894)"]; d23 = tn["Dec 2023 (DR-4765)"]; j24 = tn["Jan 2024 (DR-4766)"]
    claims_2324 = d23["nfip_claims"] + j24["nfip_claims"]
    ihp_2324 = d23["ihp"] + j24["ihp"]; nfip_2324 = d23["nfip_paid"] + j24["nfip_paid"]
    kb = bg["kent_towns"]; st = tk["statewide"]; ch = tk["change_2010_to_2024"]
    ar = rp["areas"]

    # the draft's figures, held to the data so a rerun upstream can't silently change the page
    assert (M(y10["ihp"]), M(y10["pa_obligated"]), y10["nfip_claims"], M(y10["nfip_paid"]), M(y10["sba_loans"])) == \
           ("$37.1M", "$26.0M", 1747, "$43.5M", "$46.8M")
    assert (M(sb["kent"]["sba_approved"]), M(sm["dr1894_by_county_2010"]["Kent"]["nfip_paid"])) == ("$18.1M", "$14.7M")
    assert (claims_2324, kb["claims_2023_24_in_2010_bgs"], kb["claims_2023_24"], kb["share_2023_24_in_2010_tracts"]) == (205, 77, 85, 1.0)
    assert (st["2010"], st["2024"], P(ch["in_2010_block_groups"]), P(ch["Warwick"]), P(ch["Cranston"])) == (16217, 11791, "30%", "47%", "50%")
    assert (M(ihp_2324), M(nfip_2324), rp["ihp_per_household_2010_in_2025usd"]) == ("$19.4M", "$10.2M", 3719)

    b = [f'<main><div class="dateline">{DATELINE}</div>']
    if not RELEASE:
        b.append('<p class="cite" style="border-left:3px solid var(--record);padding-left:10px">PREVIEW, not published. '
                 'Section 5 is Liam&#8217;s; lines marked [C] are Claude&#8217;s wording awaiting his read.</p>')
    b.append('<h1>Who Pays for the Next Flood</h1>')
    b.append(f'<p class="deck">{C("In 2010, Rhode Island rebuilt from the March floods more on loans than on flood insurance. Since then, the places that flooded have dropped a third of their flood policies.")}</p>')
    b.append('<p class="byline">By Liam Freaney · from FEMA&#8217;s and the Small Business Administration&#8217;s public disaster files</p>')
    b.append('<div class="big">'
             f'<div><b>{M(y10["sba_loans"])}</b><span>in SBA disaster loans after the 2010 floods</span></div>'
             f'<div><b>{M(y10["nfip_paid"])}</b><span>paid by flood insurance on {N(y10["nfip_claims"])} claims</span></div>'
             f'<div><b>{kb["claims_2023_24_in_2010_bgs"]} of {kb["claims_2023_24"]}</b><span>2023&#8211;24 claims in the Kent towns, in block groups that also claimed in 2010</span></div>'
             f'<div><b>{P(ch["in_2010_block_groups"])}</b><span>fewer flood policies in the 2010 areas, 2010 to 2024</span></div></div>')

    b.append('<h2>What 2010 cost, and who paid</h2>')
    b.append('<p>In March and April 2010, rivers in Kent and Providence counties flooded thousands of homes. The federal disaster declaration was DR-1894. Here is who paid for the rebuilding, by program:</p>')
    b.append('<div class="tablewrap"><table><tr><th>Program</th><th class="n">Paid</th></tr>'
             f'<tr><td>FEMA aid to households (IHP)</td><td class="n">{M(y10["ihp"])}</td></tr>'
             f'<tr><td>FEMA aid to towns and the state (Public Assistance)</td><td class="n">{M(y10["pa_obligated"])}</td></tr>'
             f'<tr><td>Flood insurance (NFIP), {N(y10["nfip_claims"])} claims</td><td class="n">{M(y10["nfip_paid"])}</td></tr>'
             f'<tr><td>SBA disaster loans, homes and businesses</td><td class="n">{M(y10["sba_loans"])}</td></tr></table></div>')
    b.append('<p class="cite">OpenFEMA Individuals and Households Program and Public Assistance funded-projects summaries, DR-1894; OpenFEMA NFIP redacted claims, losses dated March 12 to April 12, 2010; SBA Disaster Loan Data, FY2010 workbook, FEMA 1894 rows. Pulled Oct. 18, 2026. <a href="data/then_and_now.json">then_and_now.json</a>.</p>')
    w = float(sba_town["Warwick"]["sba_share_of_2010_recovery"]); c = float(sba_town["Coventry"]["sba_share_of_2010_recovery"])
    b.append(f'<p>The largest single source was loans. People borrowed more to rebuild than flood insurance paid out. In Kent County, homeowners and businesses borrowed {M(sb["kent"]["sba_approved"])} against {M(sm["dr1894_by_county_2010"]["Kent"]["nfip_paid"])} from flood insurance. In Warwick, {"half" if round(w, 1) == 0.5 else P(w)} the 2010 recovery money was debt. In Coventry, {"three quarters" if round(c * 4) == 3 else P(c)}.</p>')
    b.append(f'<p>Since then, FEMA has obligated {M(sm["kent_hma_obligated_2010_26"], 2)} in hazard mitigation in the Kent County towns. It went to {sm["kent_property_buildings"]} buildings.</p>')
    b.append('<p class="cite">Loans as a share of 2010 recovery: SBA approved loans over SBA loans plus NFIP payments, by town, <a href="data/sba_1894_by_town.csv">sba_1894_by_town.csv</a>. Mitigation: OpenFEMA Hazard Mitigation Assistance subapplications v2, Rhode Island, 2010&#8211;2026, <a href="data/hma_ri_towns.csv">hma_ri_towns.csv</a> and <a href="data/hma_ri_projects.csv">hma_ri_projects.csv</a>.</p>')
    b.append(f'<p>{C("The buildings that flooded in 2010 were mostly rebuilt where they stood, on borrowed money.")}</p>')

    b.append('<h2>It happened again, in the same places</h2>')
    b.append(f'<p>In December 2023 and January 2024, two more federal declarations followed (DR-4765, DR-4766). They were smaller: {N(claims_2324)} flood insurance claims, against {N(y10["nfip_claims"])} in 2010. They landed in the same towns: Warwick, West Warwick, Cranston, Johnston.</p>')
    b.append(f'<p>They landed in the same neighborhoods too. The public claims file has no addresses, but it does give each claim&#8217;s census block group. In the Kent towns, {kb["claims_2023_24_in_2010_bgs"]} of the {kb["claims_2023_24"]} claims in 2023&#8211;24 were in block groups that also claimed in 2010. Every one was in a census tract that claimed in 2010.</p>')
    b.append('<p class="cite">OpenFEMA NFIP redacted claims, Rhode Island, by census block group. Every block group, both periods: <a href="data/bg_2010_vs_2023_24.csv">bg_2010_vs_2023_24.csv</a>; totals: <a href="data/summary_bg.json">summary_bg.json</a>; by town: <a href="data/then_and_now_towns.csv">then_and_now_towns.csv</a>.</p>')
    b.append('<h2>Not yet on the record</h2><ul class="open"><li>Whether the 2023&#8211;24 claims hit the same buildings as 2010. The Rhode Island Emergency Management Agency keeps the list of properties that flood again and again. I asked for it on Oct. 18, 2026.</li></ul>')

    b.append('<h2>Fewer of them are insured now</h2>')
    b.append(f'<p>In 2010, Rhode Island had {N(st["2010"])} flood insurance policies. In 2024 it had {N(st["2024"])}, down {P(ch["statewide"])}. In the areas that flooded in 2010 the drop is about {P(ch["in_2010_block_groups"])}. Warwick lost {P(ch["Warwick"])} of its policies, Cranston {P(ch["Cranston"])}.</p>')
    b.append('<p class="cite">OpenFEMA NFIP redacted policies (v3), policies in force by effective year. By town and year: <a href="data/takeup_town_year.csv">takeup_town_year.csv</a>; totals: <a href="data/takeup.json">takeup.json</a>.</p>')
    b.append(f'<p>Premiums alone don&#8217;t explain it. Policies kept falling after 2018 even where the typical premium went down. {C("The public file can&#8217;t say why people dropped coverage: whether a mortgage was paid off, the bill went up, or something else. It shows when.")}</p>')
    b.append('<p class="cite">Policies and median cost in 2025 dollars, by year, mandatory or voluntary purchase, and flood zone: <a href="data/why_fell.csv">why_fell.csv</a>.</p>')
    b.append(f'<p>It shows up in the 2023&#8211;24 storms. This time FEMA grants to households ({M(ihp_2324)}) were nearly double what flood insurance paid ({M(nfip_2324)}). In 2010 it was the other way around.</p>')

    b.append('<h2>The next one <span class="tag model">MODEL</span></h2>')
    b.append(f'<p>Here is the 2010 flood again, on today&#8217;s insurance. The same homes flood. The share still insured follows each tract&#8217;s drop in policies. Each newly uninsured home loses what flood insurance paid per claim in that area in 2010, in 2025 dollars, which undercounts damage. FEMA gives each household the 2010 average, ${N(rp["ihp_per_household_2010_in_2025usd"])} in today&#8217;s dollars.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Area</th><th class="n">Damaged homes</th><th class="n">No longer insured</th><th class="n">Their loss (at least)</th><th class="n">FEMA grants</th><th class="n">Left to the household</th></tr>')
    for k, lab in (("Rhode Island", "Rhode Island"), ("Kent towns", "Kent County towns"), ("Cranston", "Cranston")):
        a = ar[k]
        b.append(f'<tr><td>{lab}</td><td class="n">{N(a["claims_2010"])}</td><td class="n">about {N(a["newly_uninsured_homes"])}</td><td class="n">{M(a["uninsured_loss_floor"])}</td><td class="n">{M(a["ihp_at_2010_avg"])}</td><td class="n">{M(a["left_to_households"])}</td></tr>')
    b.append('</table></div>')
    b.append(f'<p class="cite">MODEL, from the claims, policies and IHP files above; CPI-U annual averages, 2010 to 2025 ({rp["cpi_2010_to_2025"]}). Every town: <a href="data/replay_by_town.csv">replay_by_town.csv</a>; inputs: <a href="data/replay.json">replay.json</a>.</p>')
    b.append(f'<p>{C("Most of what a repeat of 2010 would cost these households would land on them, not on insurance or FEMA: about nine dollars in ten. They would cover it with an SBA loan if they qualify, and out of pocket if they don&#8217;t.")} This leaves out homes that weren&#8217;t insured in 2010 either, so the real figure is higher.</p>')

    b.append(flood_pvd.section(C, M, N, P))   # B1396: Providence's basement floods (B951/B960/B962/B962a/B1034)
    b.append('<h2>What would change it</h2>')
    b.append(SECTION_5 or '<p class="cmark" style="background:var(--harbor-soft)">[Liam&#8217;s section, not written yet.]</p>')
    b.append('<h2>Data</h2><p>' + " · ".join(f'<a href="data/{f}">{f}</a>' for f in FILES + flood_pvd.FILES) + '</p></main>')

    body = "".join(b)
    if RELEASE and ("cmark" in body or not SECTION_5):
        raise SystemExit("flood.py: RELEASE is on but [C] marks or an empty section 5 remain")
    (SITE / "flood/data").mkdir(parents=True, exist_ok=True)
    (SITE / "flood/index.html").write_text(page("Who pays for the next flood — Providence, on the record",
        "Rhode Island rebuilt from the 2010 floods more on loans than on flood insurance, the same neighborhoods flooded again in 2023–24, and fewer of them are insured now.",
        "../", body, "flood/"))
    for f in FILES:
        shutil.copy(K / f, SITE / "flood/data" / f)
    for f in flood_pvd.FILES:
        shutil.copy(flood_pvd.P / f, SITE / "flood/data" / f)
    return dict(left=ar["Rhode Island"]["left_to_households"], share=ar["Rhode Island"]["share_left_to_households"])
