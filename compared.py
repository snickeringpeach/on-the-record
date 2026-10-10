"""Compared: Providence against other places on sewer overflows and dams. B340, Oct 10 2026.
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
}


def render(page, e, SITE, DATELINE):
    n = [0]; used = []
    def c(*keys):
        out = []
        for k in keys:
            if k not in used: used.append(k)
            out.append(f'<sup><a href="#s{used.index(k)+1}">{used.index(k)+1}</a></sup>')
        return "".join(out)

    b = ['<main><div class="dateline">PROVIDENCE · OCT. 2026</div>', '<h1>Compared</h1>',
         '<p class="deck">Two of the bills Providence households pay, set against other places: the sewer-overflow tunnels, and the dams upstream.</p>',
         '<p class="byline">By Liam Freaney · from utility filings, rate decisions, the National Inventory of Dams and state and federal grant records. Every row carries its sources.</p>']

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

    b.append('<h2>Sources</h2><ol class="cite">')
    for k in used:
        t, u = S[k]; b.append(f'<li id="s{used.index(k)+1}"><a href="{u}">{e(t)}</a></li>')
    b.append('</ol></main>')

    out = SITE / "compared"; out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page("Compared — Providence, on the record",
        "Providence's sewer-overflow bill and Rhode Island's dams, set against New York, Philadelphia, DC and the neighboring states.", "../", "".join(b), "compared/"))
    return {"rows": len(rows)}
