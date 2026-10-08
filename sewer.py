"""Who pays for the sewer: the Narragansett Bay Commission bill in Providence. B145, Oct 8 2026.
Rendered from ../bulletin/data/sewer-burden (tariffs.csv, burden.csv; memo.md is the sourced draft).
Called from build.py: sewer.render(page, e, SITE, DATELINE). Not published until Liam says deploy.
Left out on purpose: the memo's [C] readings (renter pass-through, where benefits land vs who pays)
and its rate-redesign illustration; only sourced figures and labeled MODELs are on the page."""
import csv, pathlib, shutil

SB = pathlib.Path(__file__).parent.parent / "bulletin" / "data" / "sewer-burden"

def render(page, e, SITE, DATELINE):
    tar = list(csv.DictReader(open(SB / "tariffs.csv")))
    bur = list(csv.DictReader(open(SB / "burden.csv")))
    m = lambda x: f"${float(x):,.2f}"
    b = ['<main><div class="dateline">PROVIDENCE · OCT. 8, 2026</div>']
    b.append('<h1>Who Pays for the Sewer</h1>')
    b.append('<p class="deck">Every Providence home pays the Narragansett Bay Commission $309.87 a year per apartment before using a drop of water. About half of what the bill raises goes to debt, and the biggest debt is the combined-sewer tunnel now estimated at $1.4 billion. The Commission has no discount for households that can&#8217;t pay, and it can have their water shut off.</p>')
    b.append('<p class="byline">By Liam Freaney · from the Public Utilities Commission&#8217;s rate dockets, the Commission&#8217;s own filings and tariffs, and the Census Bureau</p>')
    b.append('<div class="big">'
             '<div><b>$638</b><span>a year, the average residential bill, July 2026</span></div>'
             '<div><b>49%</b><span>of it is the fixed charge per apartment</span></div>'
             '<div><b>41%</b><span>of what the Commission raises goes to principal and interest; 51% with required coverage</span></div>'
             '<div><b>$1.4 billion</b><span>the Commission&#8217;s current figure for the Phase III overflow project, up from $678 million in 2014</span></div></div>')

    b.append('<h2>The bill</h2>')
    b.append('<p>Since July 1, 2026, a Providence home pays $309.87 a year for each dwelling unit, plus $4.972 for every hundred cubic feet of water used. At the Commission&#8217;s own average use, 5.5 hundred cubic feet a month, that comes to $638.02 a year, and the fixed charge is 49% of it. A three-family house owes $929.61 a year in fixed charges alone. The fixed charge is billed to the owner of the account, not to the tenant.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Rate year</th><th class="n">Per unit per year</th><th class="n">Per hundred cubic feet</th><th class="n">Average bill</th><th class="n">Light user <span class="tag model">MODEL</span></th></tr>')
    for r in tar:
        b.append(f'<tr><td>{e(r["year"])}</td><td class="n">{m(r["customer_charge_per_unit"])}</td><td class="n">${float(r["consumption_per_hcf"]):.3f}</td>'
                 f'<td class="n">{m(r["bill_at_66_hcf"])}</td><td class="n">{m(r["bill_at_36_hcf"])}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">Residential tariffs, NBC Schedule A, FY2017&#8211;FY2027; FY2027 from PUC Docket 25-32-WW, Compliance Exhibits 2 and 3 (filed July 1, 2026). Average bill at 66 hundred cubic feet a year, the Commission&#8217;s average customer. Light user at 36 a year (3 a month) is an assumption: at that use the household pays $13.58 for each hundred cubic feet it uses, against $9.67 at average use.</p>')

    b.append('<h2>What the bill pays for</h2>')
    b.append('<p>The Public Utilities Commission set the Bay Commission&#8217;s revenue for fiscal 2027 at $137.85 million. The Commission had asked for an 11.35% increase; it got 8.3%.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Fiscal 2027</th><th class="n">Dollars</th><th class="n">Share</th></tr>'
             '<tr><td>Principal</td><td class="n">$35,530,513</td><td class="n"></td></tr>'
             '<tr><td>Interest</td><td class="n">$20,817,858</td><td class="n"></td></tr>'
             '<tr><td><b>Debt service</b></td><td class="n"><b>$56,348,371</b></td><td class="n"><b>40.9%</b></td></tr>'
             '<tr><td>Debt-service coverage, 1.25 times</td><td class="n">$14,087,093</td><td class="n">10.2%</td></tr>'
             '<tr><td>Operating expenses</td><td class="n">$66,978,905</td><td class="n">48.6%</td></tr></table></div>')
    b.append('<p class="cite">PUC Docket 25-32-WW, Compliance Exhibit 1 (filed July 1, 2026). Coverage is revenue lenders require above debt service. The Commission asked to raise it to 1.30 times; the PUC denied that without prejudice (Order 25601, Feb. 2, 2026).</p>')
    b.append('<p>The Commission carries about $1.2 billion in long-term debt and projects about $1.43 billion by fiscal 2035. Its capital needs through fiscal 2027 run $67.9 million past its sources, a gap to be filled by more borrowing. On the average bill, the debt share comes to about $261 a year, $326 with coverage <span class="tag model">MODEL</span>.</p>')
    b.append('<p class="cite">Debt: PUC Order 25601, pp. 6&#8211;7. Capital gap: Division of Public Utilities memo, Nov. 14, 2025. Per-bill figure assumes residential bills carry debt in proportion to revenue.</p>')

    b.append('<h2>Phase III</h2>')
    b.append('<p>Phase III is the last stage of the Commission&#8217;s combined-sewer overflow program: a 2.2-mile tunnel under Pawtucket and Central Falls holding 58.5 million gallons, with interceptors, storage and sewer separation. Its stated cost has more than doubled.</p>')
    b.append('<div class="tablewrap"><table><tr><th>When</th><th class="n">Figure</th><th>What it covers</th><th>Source</th></tr>'
             '<tr><td>Oct. 2014</td><td class="n">$678 million</td><td>Phase III</td><td>NBC affordability presentation, Oct. 23, 2014</td></tr>'
             '<tr><td>2014&#8211;15</td><td class="n">$750 million</td><td>Phase III, on a 2038 schedule</td><td>NBC Phase III re-evaluation</td></tr>'
             '<tr><td>2019</td><td class="n">$548.4 million</td><td>Phase III facilities: tunnel, shafts, pump station</td><td><a href="https://www.epa.gov/wifia/providence-combined-sewer-overflow-phase-iii-facilities">EPA WIFIA</a></td></tr>'
             '<tr><td>Sept. 2021</td><td class="n">$813 million</td><td>Phase IIIA</td><td><a href="https://www.asce.org/publications-and-news/civil-engineering-source/civil-engineering-magazine/article/2021/09/storage-tunnel-will-improve-narragansett-bay-water-quality">ASCE <i>Civil Engineering</i></a></td></tr>'
             '<tr><td>Dec. 2025</td><td class="n">$1.4 billion</td><td>&#8220;CSO project Phase 3&#8221;; about $850 million spent by the tunnel&#8217;s start, Feb. 2028</td><td>NBC testimony, PUC Order 25601, p. 6</td></tr></table></div>')
    b.append('<p>Phase III is about half of the Commission&#8217;s $511.9 million capital plan for fiscal 2026&#8211;31. The record does not say how much of the $56.3 million in annual debt service it accounts for; that has been asked of the Commission.</p>')
    b.append('<p class="cite">Capital plan: Bowen testimony, Order 25601, p. 4. The figures above measure different scopes and are not adjusted for inflation.</p>')

    b.append('<h2>What it buys</h2>')
    b.append('<p>At full build-out, EPA projects 98% less overflow volume and 80% fewer shellfish-bed closures; overflows would fall from 80 to 90 a year to about four. The Commission&#8217;s own 2014 model of days the water fails its standard, after Phase III against after Phase II:</p>')
    b.append('<div class="tablewrap"><table><tr><th>Water</th><th>Use</th><th class="n">Change</th></tr>'
             '<tr><td>Upper bay, Area B</td><td>Shellfishing</td><td class="n">&#8722;100%</td></tr>'
             '<tr><td>Upper bay, Area A</td><td>Shellfishing</td><td class="n">&#8722;82%</td></tr>'
             '<tr><td>Providence River (SB)</td><td>Shellfishing</td><td class="n">&#8722;79%</td></tr>'
             '<tr><td>Conimicut Triangle</td><td>Shellfishing</td><td class="n">&#8722;60%</td></tr>'
             '<tr><td>Providence River (SB1)</td><td>Swimming</td><td class="n">&#8722;36%</td></tr>'
             '<tr><td>Seekonk River (SB1)</td><td>Swimming</td><td class="n">&#8722;16%</td></tr></table></div>')
    b.append('<p class="cite">Acre-days not meeting standard, post-Phase II to post-Phase III (2038), NBC Phase III re-evaluation, 2014&#8211;15. EPA WIFIA project page; ASCE <i>Civil Engineering</i>, Sept. 2021. These are projections, not yet checked against RIDEM&#8217;s closure records, which have been requested.</p>')

    b.append('<h2>Who can&#8217;t pay</h2>')
    b.append('<p>The Commission has no low-income discount, tiered rate or hardship credit. A customer who can&#8217;t pay on time may ask for a payment arrangement. Late balances carry 1% interest a month. Under state law the Commission can order a customer&#8217;s water supplier to shut off the water within 14 days for an unpaid sewer bill; a tenant who pays to restore service may deduct it from the rent.</p>')
    b.append('<p class="cite">NBC tariffs, FY2027 Schedules A and B; <a href="https://regulations.justia.com/states/rhode-island/title-835/chapter-20/subchapter-00/part-2/section-835-ricr-20-00-2-16">835-RICR-20-00-2.16</a>; <a href="https://www.narrabay.com/customer-care/pay-bill/">NBC, Pay Your Bill</a>; R.I. Gen. Laws <a href="https://webserver.rilegislature.gov/Statutes/TITLE46/46-25/46-25-22.1.htm">&#167; 46-25-22.1</a>; <a href="https://www.narrabay.com/customer-care/water-shut-off/">NBC, Water Shut-Off</a>.</p>')
    b.append('<p>The Commission measured the burden itself in 2014. Following EPA guidance, it counted households paying more than 2% of income for sewer: with Phase III, 64,046 across its service area, 29,067 of them in Providence. It then set a target bill of $626 a year. The fiscal 2027 average bill is $638.</p>')
    b.append('<p class="cite">NBC affordability presentation, Oct. 23, 2014; NBC Phase III re-evaluation, 2014&#8211;15. The $626 target is in 2014 dollars.</p>')
    b.append('<p>Today, the average bill passes 2% of income for any Providence household earning less than about $31,900. By the Census Bureau&#8217;s count, 2,725 owner households and 13,134 renter households fall entirely below that line <span class="tag model">MODEL</span>.</p>')
    b.append('<div class="tablewrap"><table><tr><th>Household income</th><th class="n">Owners</th><th class="n">Renters</th><th class="n">Average bill as share of income</th></tr>')
    for r in bur:
        b.append(f'<tr><td>{e(r["income"])}</td><td class="n">{int(r["owner_households"]):,}</td><td class="n">{int(r["renter_households"]):,}</td><td class="n">{float(r["bill_pct_of_income_at_midpoint_avg_use"]):.1f}%</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">Households: American Community Survey 2020&#8211;2024, table B25118, Providence. Share of income at each bracket&#8217;s midpoint, at average use. A renter&#8217;s share assumes the bill reaches the tenant in full through the rent; there is no Providence record of how much does.</p>')
    b.append('<p>A 50% discount for Providence households under $25,000 would cost about $5.06 million a year. Spread across the Commission&#8217;s residential units, that adds about $42.63 a unit, 6.7% on the average bill <span class="tag model">MODEL</span>.</p>')
    b.append('<p class="cite">15,859 households &#215; $638.02 &#215; 50%, over 118,683 residential units, the Commission&#8217;s 2014 count, the latest in hand. Providence only; Pawtucket and Central Falls households would add to it.</p>')

    b.append('<h2>Asked of the Commission</h2><ul>'
             '<li>Phase III&#8217;s share of fiscal 2027 debt service, and of the $1.2 billion outstanding.</li>'
             '<li>Whether $1.4 billion covers Phases IIIA through IIID, and spending on Phase III to date.</li>'
             '<li>Water shutoffs ordered for unpaid sewer bills, by year and city.</li>'
             '<li>Whether the Commission has costed a low-income rate since 2014.</li>'
             '<li>Overflow events by outfall since 2015, requested under the Access to Public Records Act, Oct. 7, 2026.</li></ul>')
    b.append('<p class="cite">Data: <a href="data/tariffs.csv">tariffs (CSV)</a>, <a href="data/burden.csv">burden by income (CSV)</a>.</p>')
    b.append('</main>')

    out = SITE / "sewer"; (out / "data").mkdir(parents=True, exist_ok=True)
    for f in ("tariffs.csv", "burden.csv"): shutil.copy(SB / f, out / "data" / f)
    (out / "index.html").write_text(page("Who pays for the sewer — Providence, on the record",
        "The Narragansett Bay Commission bill in Providence: what it pays for, what Phase III costs, and who can't pay.", "../", "".join(b), "sewer/"))
    return {"bill": 638}
