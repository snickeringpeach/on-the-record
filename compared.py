"""Compared: Providence against other places on sewer overflows, dams and the line against the sea. B340, Oct 10 2026; B388 (coast), Oct 12 2026.
From ../barriers/COMPARE.md (B278), ../bulletin/data/sewer-burden/COMPARE.md (B276),
../dams/NATIONAL.md and ../dams/FUNDING.md (B273). Every row carries its sources on the page.
Left out on purpose: COMPARE.md's [C] one-line readings, and the barrier row, which waits on the
City's own gate spending (records request held). Called from build.py: compared.render(...).
Not published until Liam says deploy."""

S = {  # sources
    "nbc_hist": ("NBC, CSO abatement history and future (2024)", "https://narrabay.com/wp-content/uploads/2024/04/Narragansett-Bay-Commission-CSO-Abatement-History-and-Future.pdf"),
    "nbc_eval": ("NBC, evaluating the CSO program (2024)", "https://www.narrabay.com/wp-content/uploads/2024/04/Evaluating-the-Success-of-the-Narragansett-Bay-Commissions-CSO-Abatement-Program.pdf"),
    "nbc_acfr": ("NBC annual financial report FY2017 (residential accounts)", "https://narrabay.com/wp-content/uploads/2022/08/Comprehensive-Annual-Financial-Report-FY-2017.pdf"),
    "nbc_puc": ("PUC Docket 25-32-WW compliance filing (2026 rates)", "https://ripuc.ri.gov/sites/g/files/xkgbur841/files/2026-07/25-32-WW%20NBC%20Compliance%20Filing%20Revised%20%2800404435xBDDFF%29.PDF"),
    "nyc_ltcp": ("NYC DEP, Flushing Bay LTCP meeting, Dec 2025", "https://www.nyc.gov/assets/dep/downloads/pdf/water/nyc-waterways/flushing-bay/flushing-bay-ltcp-cso-tunnel-public-meeting-12-16-2025.pdf"),
    "nyc_rate": ("NYC DEP, FY2026 proposed rate", "https://www.nyc.gov/site/dep/news/25-017/department-environmental-protection-proposes-fiscal-year-2026-water-rate"),
    "nyc_hh": ("Census QuickFacts, New York City households", "https://www.census.gov/quickfacts/fact/table/newyorkcitynewyork/INC110224"),
    "phl_cost": ("Circle of Blue (2024), Green City, Clean Waters cost", "https://www.circleofblue.org/2024/supply/water-management/billions-over-budget-questions-swirl-over-phillys-green-fix-for-sewers/"),
    "phl_rate": ("Philadelphia Rate Board, July 23 2025", "https://www.phila.gov/media/20250723172348/7.23.25-General-Rate-Determination.pdf"),
    "phl_tap": ("Philadelphia TAP 2025 annual report", "https://www.phila.gov/media/20260512142535/Tiered-Assistance-Program-TAP-2025-annual-report.pdf"),
    "phl_hh": ("Census QuickFacts, Philadelphia households", "https://www.census.gov/quickfacts/fact/table/philadelphiacitypennsylvania,DC,westchestercountynewyork/INC110224"),
    "dc_cost": ("ASCE (2023), DC Water final CSO tunnel", "https://www.asce.org/publications-and-news/civil-engineering-source/civil-engineering-magazine/article/2023/11/819-million-contract-awarded-for-dc-waters-final-cso-tunnel"),
    "dc_rate": ("DC Water 2026 ratepayer town halls", "https://www.dcwater.com/sites/default/files/DC%20Water%20Ratepayer%20Town%20Halls%20Presentation%202026.pdf"),
    "dc_hh": ("Census QuickFacts, DC households", "https://www.census.gov/quickfacts/fact/table/DC/INC110224"),
    "nid": ("USACE National Inventory of Dams, national export (pulled 2026)", "https://nid.sec.usace.army.mil/"),
    "ma_fund": ("Mass. Dam and Seawall program awards, Sept 2025", "https://www.mass.gov/news/healey-driscoll-administration-awards-nearly-11-million-in-funding-for-dams-levees-and-coastal-infrastructure"),
    "ma_reg": ("301 CMR 15.04 (who may get grants and loans)", "https://regulations.justia.com/states/massachusetts/301-cmr/title-301-cmr-15-00/section-15-04"),
    "ri_bond": ("2018 Green Economy bond, Article 5", "https://webserver.rilegislature.gov/BillText18/HouseText18/Article-005-SUB-A.htm"),
    "ri_eco": ("ecoRI on RI dam funding", "https://ecori.org/?p=28252"),
    "ct_bond": ("CT Public, Jan 2 2024, state-owned dam repairs", "https://ctpublic.org/news/2024-01-02/ct-allocates-6-37m-for-state-owned-dam-repairs-middletown-a-key-beneficiary"),
    "hhpd": ("FEMA High Hazard Potential Dams grant allocations", "https://fema.gov/ht/node/604754"),
    "mi_cost": ("Four Lakes Task Force, total capital amount to be assessed", "https://www.four-lakes-taskforce-mi.com/updates/total-capital-amount-to-be-assessed"),
    "mi_pub": ("Michigan Public, May 19 2025", "https://www.michiganpublic.org/environment-climate-change/2025-05-19/mid-michigan-dam-restorations-are-picking-back-up-with-residents-to-pay-nearly-218m"),
    "mi_ag": ("Michigan AG, Apr 23 2026, Court of Claims dismissal", "https://www.michigan.gov/ag/news/press-releases/2026/04/23/michigan-court-of-claims-dismisses-lawsuit-against-state-over-edenville-dam-failure"),
    # B388, Oct 12 2026: the coast table
    "cerc": ("US Army Corps of Engineers, Coastal Engineering Research Center, Bulletin FY1967-69 (Fox Point: $16 million, 30 percent non-federal; five pumps, 7,000 cfs; completed 1966)", "https://apps.dtic.mil/sti/pdfs/AD0711940.pdf"),
    "reed2010": ("Sen. Reed, Feb. 19, 2010: transfer of the Fox Point Hurricane Barrier to the Corps (280 acres; up to $500,000 a year saved by the city)", "https://www.reed.senate.gov/news/releases/providence-enhances-public-safety-and-saves-taxpayer-dollars-with-transfer-hurricane-barrier-to-feds"),
    "nae": ("US Army Corps of Engineers, New England District: Fox Point Hurricane Barrier", "https://www.nae.usace.army.mil/Missions/Projects-Topics/Fox-Point-Hurricane-Barrier/"),
    "corps_wp": ("US Army Corps of Engineers, Civil Works FY2026 Work Plan, Operation and Maintenance (Fox Point: $6,348,000)", "https://www.usace.army.mil/Missions/Civil-Works/Budget/"),
    "itl": ("Inside the Line: who and what is inside the barrier (2020 Census blocks, 2025 tax roll), flood insurance by block group", "https://insidetheline.org/"),
    "mb_swmp": ("City of Miami Beach, Stormwater Master Plan presentation to the Commission, Mar. 13, 2024 ($103 million completed since 2011; $3.7-4.74 billion to finish)", "https://miamibeachfl.gov/wp-content/uploads/2024/07/March_13_2024_CMB_Commission_Presentation_SWMP.pdf"),
    "mb_cd": ("City of Miami Beach, continuing disclosures FY2023 (stormwater rate per ERU; stormwater bonds outstanding)", "https://miamibeachfl.gov/cmb-rda-continuing-disclosures-fy2023-final"),
    "mb_eru": ("City of Miami Beach, stormwater utility fee calculation worksheet (one ERU = 791 sq ft of impervious surface)", "https://www.miamibeachfl.gov/wp-content/uploads/2023/03/Stormwater-Utility-Fee-Calculation-Worksheet.pdf"),
    "backbay": ("US Army Corps of Engineers, Miami-Dade Back Bay Chief's Report, Aug. 26, 2024 ($2.66 billion, nonstructural)", "https://transportation.house.gov/UploadedFiles/MDBB_Chiefs_Report_signed.pdf"),
    "dare_fund": ("Dare County, occupancy tax distributions (Beach Nourishment Fund)", "https://darenc.gov/about/tax-info/gross-collections/occupancy-distributions"),
    "dare_proj": ("Dare County, beach nourishment completed projects", "https://www.darenc.gov/government/beach-nourishment/completed-projects"),
    "nags2026": ("Outer Banks Voice, Feb. 4, 2026: Nags Head's $36.4 million 2026 nourishment contract", "https://www.outerbanksvoice.com/2026/02/04/nags-head-approves-36-4m-contract-for-2026-beach-nourishment/"),
    "ncdot_rod": ("NCDOT, Jul. 28, 2022: Rodanthe bridge opens ($155 million)", "https://www.ncdot.gov/news/press-releases/Pages/2022/2022-07-28-rodanthe-bridge-opens.aspx"),
    "nps": ("National Park Service, Cape Hatteras: threatened oceanfront structures (32 collapses since 2020)", "https://www.nps.gov/caha/learn/news/threatened-oceanfront-structures.htm"),
    "ifp_nc12": ("Island Free Press: NC 12 closures on Pea Island (more than $72 million since 2010)", "https://islandfreepress.org/blog/n-c-12-closures-on-pea-island-why-do-they-keep-happening-and-what-can-actually-be-done-about-them/"),
    "ifp_buxton": ("Island Free Press, May 2026: Dare County buys and demolishes a Buxton house ($250,000)", "https://islandfreepress.org/outer-banks-news/oceanfront-home-proactively-demolished-in-buxton-ahead-of-planned-beach-nourishment-and-dune-construction-project/"),
    "qf_mb": ("Census QuickFacts, Miami Beach city, Fla. (households 2020-24)", "https://www.census.gov/quickfacts/fact/table/miamibeachcityflorida/HSD410224"),
    "qf_dare": ("Census QuickFacts, Dare County, N.C. (households 2020-24; housing units 2025)", "https://www.census.gov/quickfacts/fact/table/darecountynorthcarolina/HSD410224"),
    "nfip_v2": ("FEMA OpenFEMA, NFIP policies (in force June 30, 2025) and claims, Miami-Dade and Dare", "https://www.fema.gov/openfema-data-page/fima-nfip-redacted-policies-v2"),
    "ccrif": ("CCRIF, system summary, July 2026 ($483.1 million paid since 2007)", "https://www.wfcatprogrammes.com/documents/20142/71017/CCRIF_System_Summary_Update_Jul2026.pdf/ee61b596-3c9a-939a-9925-377f6e761d46"),
    "wb_melissa": ("World Bank, Nov. 7, 2025: Hurricane Melissa triggers a 100 percent payout of Jamaica's $150 million catastrophe bond", "https://www.worldbank.org/en/news/press-release/2025/11/07/hurricane-melissa-triggers-100-payout-of-150-million-world-bank-catastrophe-bond-"),
    "wb_damage": ("World Bank and IDB, Nov. 19, 2025: Hurricane Melissa damage to Jamaica, an all-time high", "https://www.worldbank.org/en/news/press-release/2025/11/19/world-bank-idb-estimate-hurricane-melissa-damage-to-jamaica-totals-all-time-high-"),
    "openfema_pa": ("FEMA OpenFEMA, Public Assistance funded projects (Puerto Rico, Maria: $35.6 billion federal obligated)", "https://www.fema.gov/openfema-data-page/public-assistance-funded-projects-details-v1"),
    "gao_prepa": ("GAO-26-107772, Dec. 2025: PREPA, $11.1 billion obligated, $2.7 billion disbursed", "https://www.gao.gov/products/gao-26-107772"),
}

from compared_coast import S as _COAST_S, section as _coast_section  # B407
S.update(_COAST_S)


def render(page, e, SITE, DATELINE):
    n = [0]; used = []
    def c(*keys):
        out = []
        for k in keys:
            if k not in used: used.append(k)
            out.append(f'<sup><a href="#s{used.index(k)+1}">{used.index(k)+1}</a></sup>')
        return "".join(out)

    b = ['<main><div class="dateline">PROVIDENCE · OCT. 2026</div>', '<h1>Compared</h1>',
         '<p class="deck">Three of the bills Providence pays, set against other places: the sewer-overflow tunnels, the dams upstream, and the line against the sea.</p>',
         '<p class="byline">By Liam Freaney · from utility filings, rate decisions, the National Inventory of Dams, Army Corps records, city capital plans and county tax distributions. Every row carries its sources.</p>']

    b.append('<h2>Sewer overflow programs</h2>')
    b.append('<p>Each system below is building tunnels or green infrastructure to stop sewage overflowing into rivers in storms, and each is paying for it through customers&#8217; bills.</p>')
    b.append('<div class="tablewrap"><table><tr><th>System</th><th class="n">Program cost</th><th class="n">Per household</th><th class="n">Typical yearly bill</th><th>Help for low-income households</th></tr>')
    rows = [
        ("Narragansett Bay Commission (Providence area)", "~$1.72 billion" + c("nbc_eval", "nbc_hist"), "~$22,400 per residential account" + c("nbc_acfr"),
         "$638, sewer only (2026)" + c("nbc_puc"), "None"),
        ("New York City DEP", "~$14.9 billion" + c("nyc_ltcp"), "~$4,500" + c("nyc_hh"), "~$1,224, water and sewer (FY2026 proposed)" + c("nyc_rate"),
         "$159 credit for 96,500 households; $250 per unit in 65,000 apartments" + c("nyc_rate")),
        ("Philadelphia Water", "at least $4.5 billion" + c("phl_cost"), "~$6,600" + c("phl_hh"), "~$1,132, water, sewer and stormwater (from Sept 2026)" + c("phl_rate"),
         "Tiered Assistance Program caps the bill at a share of income" + c("phl_tap")),
        ("DC Water", "~$2.7&#8211;3.0 billion" + c("dc_cost"), "~$9,200" + c("dc_hh"), "$1,766 (FY2026)" + c("dc_rate"),
         "CAP tiers discount water and sewer and cut the impervious-area charge 50&#8211;75%" + c("dc_rate")),
    ]
    for r in rows:
        b.append("<tr>" + "".join(f'<td{" class=\"n\"" if 0 < i < 4 else ""}>{x}</td>' for i, x in enumerate(r)) + "</tr>")
    b.append('</table></div>')
    b.append('<p class="cite">Per household is our arithmetic: program cost over households (Census, 2020&#8211;24). For the Bay Commission it is over 76,460 residential accounts, which undercounts renter households in multifamily buildings. The Bay Commission&#8217;s bill is sewer only; the others include water.</p>')

    b.append('<h2>Dams</h2>')
    b.append('<p>High-hazard dams are those whose failure would likely kill people downstream.</p>')
    b.append('<div class="tablewrap"><table><tr><th></th><th class="n">Rhode Island</th><th class="n">Connecticut</th><th class="n">Massachusetts</th><th class="n">New York</th></tr>')
    b.append(f'<tr><td>High-hazard dams with an emergency action plan{c("nid")}</td><td class="n"><b>52%</b></td><td class="n">93%</td><td class="n">99%</td><td class="n">99%</td></tr>')
    b.append(f'<tr><td>High-hazard dams with a last-inspection date on file{c("nid")}</td><td class="n"><b>7 of 95</b></td><td class="n">273 of 282</td><td class="n">339 of 342</td><td class="n">450 of 451</td></tr>')
    b.append(f'<tr><td>State repair money for dam owners</td><td class="n">None dedicated; $4.4M in the 2018 bond, for state-owned dams only{c("ri_bond", "ri_eco")}</td>'
             f'<td class="n">Bond money for state-owned dams{c("ct_bond")}</td><td class="n">Nearly $146M in grants and loans since 2013; loans open to private owners{c("ma_fund", "ma_reg")}</td><td class="n">&#8212;</td></tr>')
    b.append(f'<tr><td>FEMA high-hazard dam rehabilitation grant, Fall 2024{c("hhpd")}</td><td class="n"><b>Not listed</b></td><td class="n">$3.04M</td><td class="n">$6.98M</td><td class="n">&#8212;</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">National Inventory of Dams figures are what each state has filed; Rhode Island&#8217;s federal record is partly out of date, and the state&#8217;s own 2024 report counts 87 of 173 required emergency plans approved. FEMA lists only allocations to states that applied.</p>')

    b.append('<h2>When a dam fails: Michigan, 2020</h2>')
    b.append(f'<p>After the Edenville and Sanford dams failed in May 2020, restoring the four lakes was put at $398.9 million. After state and other offsets, $217.7 million is being assessed on property owners around the lakes{c("mi_cost", "mi_pub")}. Downstream residents&#8217; suit against the state was dismissed on April 23, 2026; the court found the private owners, not the state, controlled the dam{c("mi_ag")}.</p>')

    # B388: three coasts, one question
    b.append('<h2>The line against the sea: three coasts</h2>')
    b.append('<p>Providence sits behind a federal surge barrier. Miami Beach built pumps and raised its roads. The Outer Banks buys sand and bridges over the inlets. Three ways a coast gets paid for, set side by side.</p>')
    b.append('<div class="tablewrap"><table><tr><th></th><th>Fox Point, Providence</th><th>Miami Beach</th><th>The Outer Banks (Dare County, N.C.)</th></tr>')
    crows = [
        ("The defense",
         "A surge barrier across the Providence River with five pumps (7,000 cubic feet a second), built 1960&#8211;66; river gates and street and sewer gates" + c("cerc", "nae"),
         "Pump stations (48 built, 83 planned), raised roads, seawalls and one-way valves, since 2014" + c("mb_swmp"),
         "Sand: about $306 million placed on town beaches 2011&#8211;2026; NC 12 kept open; two bridges over the inlets" + c("dare_proj", "nags2026", "ncdot_rod")),
        ("Who built it",
         "The Army Corps, 70 percent federal, 30 percent non-federal" + c("cerc"),
         "The city, from its own capital program" + c("mb_swmp"),
         "The towns and the county (sand); NCDOT (the road and bridges). The Corps&#8217; 2001 project was never built" + c("dare_proj")),
        ("Who runs it",
         "The Corps since February 2010: the barrier, river gates and pumps. The city: its street and sewer gates" + c("reed2010"),
         "The city" + c("mb_swmp"),
         "The towns and county contract the dredges; NCDOT the road" + c("dare_proj")),
        ("Capital cost",
         "$16 million in 1966" + c("cerc") + ", about $160 million in today&#8217;s dollars [MODEL]",
         "$103 million of stormwater projects completed since 2011 (the city&#8217;s figure); $3.7&#8211;4.74 billion to finish the 2024 master plan" + c("mb_swmp"),
         "Sand about $306 million (2011&#8211;26; the 2026 round not final); bridges about $407 million; the Pea Island corridor more than $72 million since 2010" + c("dare_proj", "nags2026", "ncdot_rod", "ifp_nc12")),
        ("Yearly cost",
         "Corps operation and maintenance, FY2026: $6,348,000 ($3,808,800 to the project, $2,539,200 to the district)" + c("corps_wp") + ". The city&#8217;s own line for its gates isn&#8217;t published",
         "A stormwater fee of $30.14 a month per 791 square feet of roof and pavement (FY2023), about $362 a year; $241.1 million of stormwater bonds outstanding (Sept. 2023)" + c("mb_cd", "mb_eru"),
         "Two of the county&#8217;s six occupancy-tax points, $16.3 million in FY2024, to the Beach Nourishment Fund; FEMA reimbursement after storms" + c("dare_fund")),
        ("Who pays",
         "Congress, through the Corps; the city for its gates. The households behind the barrier pay nothing direct",
         "Every property, in proportion to its impervious area, citywide; passed through to renters",
         "Visitors (the occupancy tax); owners through service districts and property tax, about half of each project; FEMA after each storm; NCDOT for the road"),
        ("Protected households",
         "1,782 occupied households inside the line; 18,582 jobs; $2.81 billion of assessed value, more than half of it exempt" + c("itl"),
         "41,600 households" + c("qf_mb"),
         "16,836 households; 36,495 housing units, most of them second homes and rentals" + c("qf_dare")),
        ("Per protected household [MODEL]",
         "Capital about $90,000 (the local 30 percent share about $27,000); yearly $3,560, or $2,140 for the project alone; per job, $340",
         "Capital $2,500 (the city&#8217;s $103 million) to $89,000&#8211;114,000 (the master plan); yearly, the fee on the property&#8217;s roof and pavement",
         "Sand $18,000 per household, $8,400 per housing unit; bridges $24,000 and $11,000; yearly $968 per household from visitors"),
        ("Outside the line",
         "75 coastal-zone parcels on 301 acres of lower ground, the Fields Point treatment plant among them. 589 flood policies citywide; behind the barrier, 329 in zone X at a median $4,120, one on a primary residence" + c("itl"),
         "The mainland waits on the Corps&#8217; Back Bay plan: walls dropped, $2.66 billion of house-lifting and floodproofing, authorized in December 2024, unfunded" + c("backbay") + ". Flood premiums run eightfold from inland Hialeah ($357&#8211;402) to the beach ($2,480&#8211;3,080)" + c("nfip_v2"),
         "Rodanthe and north Buxton, between sand cycles: 32 houses have fallen into the sea since 2020, 20 of them since September 2025" + c("nps") + ". The county now buys one at a time ($250,000)" + c("ifp_buxton") + ". Flood premiums there run $493&#8211;669 against $11,513 of claims paid per policy" + c("nfip_v2")),
    ]
    for r in crows:
        b.append("<tr>" + "".join(f'<td>{x}</td>' for x in r) + "</tr>")
    b.append('</table></div>')
    b.append('<p class="cite">Per household is our arithmetic, and the denominator is a choice. Providence: occupied households in the 2020 Census blocks inside the barrier&#8217;s levee-credited area, from Inside the Line; the barrier protects more jobs and tax base than homes. Miami Beach: households, 2020&#8211;24. Dare County: households and housing units; the sand protects the units, 54 percent of which are nobody&#8217;s household. The 1966 cost is scaled to today by the consumer price index, about tenfold. Press figures of $400&#8211;600 million for Miami Beach&#8217;s program are not reconciled with the city&#8217;s $103 million and are left out.</p>')
    b.append(f'<p>An island buys cash, not protection. Jamaica&#8217;s parametric insurance and catastrophe bond paid about $242 million within weeks of Hurricane Melissa (2025){c("ccrif", "wb_melissa")}, against damage the World Bank and IDB put at $8.8 billion{c("wb_damage")}: about three cents on the dollar. Puerto Rico after Maria was obligated $35.6 billion in FEMA public assistance, about $22,700 per housing unit [MODEL]{c("openfema_pa")}; its power authority had spent $2.7 billion of $11.1 billion by December 2025{c("gao_prepa")}.</p>')

    b += _coast_section(c)  # B407: up the coast

    b.append('<h2>Sources</h2><ol class="cite">')
    for k in used:
        t, u = S[k]; b.append(f'<li id="s{used.index(k)+1}"><a href="{u}">{e(t)}</a></li>')
    b.append('</ol></main>')

    out = SITE / "compared"; out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page("Compared — Providence, on the record",
        "Providence's sewer-overflow bill, Rhode Island's dams and the Fox Point barrier, set against New York, Philadelphia, DC, the neighboring states, Miami Beach and the Outer Banks.", "../", "".join(b), "compared/"))
    return {"rows": len(rows) + len(crows) + 8}
