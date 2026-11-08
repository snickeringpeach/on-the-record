"""Who pays: the apartment line. B1447f, Nov 8 2026, from ../housing/class_line.py (B1447e).
Called from build.py: apartments.render(page, e, SITE, DATELINE) -- ONLY when RELEASE is True, or for a local look
with APT_PREVIEW=1 python3 build.py (./deploy wipes site/ and rebuilds without it, so a preview never ships).

HELD. RELEASE stays False until Liam says "ship it". Before that:
  - every [C] line (Claude's framing, class="cmark" on the preview) is taken, rewritten or cut;
  - the slug (/apartments/) and a home-feed card are his call;
  - the pass-through range is a MODEL choice of Claude's; he may want it out.
render() refuses to build with RELEASE=True while any [C] mark remains.
Every figure is read from ../housing/data/class_line*.csv and pinned by assert, so an upstream rerun that moves a number
stops the build before it reaches the page.
"""
import csv, pathlib, shutil

H = pathlib.Path(__file__).parent.parent / "housing" / "data"
RELEASE = False
FILES = ["class_line.csv", "class_line_surge.csv"]
# FY26 rates per $1,000, non-owner-occupied (Code of Ordinances s.21-182, FY26 tax ordinance) [V]
RATES = {"1A": 14.60, "1B": 14.00, "1C": 26.00, "1D": 28.50, "2A": 29.20}
# HUD FY2026 Fair Market Rents, Providence-Fall River, RI-MA HUD Metro FMR Area (huduser.gov FMR documentation system) [V]
FMR = {"1BR": 1402, "2BR": 1729}


def C(s):
    return f'<span class="cmark" style="background:var(--harbor-soft)" title="Claude&#8217;s wording, not yet Liam&#8217;s">[C] {s}</span>'


def render(page, e, SITE, DATELINE):
    S = {r["bldg_class"]: r for r in csv.DictReader(open(H / "class_line_surge.csv"))}
    L = {r["units_class"]: r for r in csv.DictReader(open(H / "class_line.csv"))}
    f = lambda r, k: float(r[k]); i = lambda r, k: int(float(r[k]))
    D = lambda x: f"${x:,.0f}"; R = lambda x: f"${x:,.2f}"; M = lambda x: f"${x/1e6:.1f}M"

    units = {k: i(S[k], "units") for k in S}; tot = sum(units.values())
    shift = sum(f(S[k], "shift_yr") for k in ("1C", "1D"))
    # the sixth-unit cost: the same building, same value per unit, taxed at 1C/1D vs 1B [MODEL]
    six = {k: f(S[k], "median_assessed_per_unit_2015on") * (RATES[k] - RATES["1B"]) / 1000 for k in ("1C", "1D")}
    assert (units["1D"], tot, i(S["1D"], "tax_per_unit_yr"), i(S["1B"], "tax_per_unit_yr")) == (765, 1735, 5621, 4461)
    assert (M(shift), M(f(S["1D"], "shift_yr")), round(six["1C"]), round(six["1D"])) == ("$2.4M", "$2.2M", 3161, 2860)
    assert (i(L["1C"], "1C"), i(L["1C"], "All"), i(L["1D"], "1D"), i(L["1D"], "All"), i(L["1B"], "1B"), i(L["1B"], "All")) == \
           (312, 382, 115, 155, 13778, 14280)

    b = [f'<main><div class="dateline">{DATELINE}</div>']
    if not RELEASE:
        b.append('<p class="cite" style="border-left:3px solid var(--record);padding-left:10px">PREVIEW, not published. '
                 'Lines marked [C] are Claude&#8217;s wording awaiting Liam&#8217;s read.</p>')
    b.append('<h1>The Sixth Apartment</h1>')
    b.append(f'<p class="deck">{C("Providence taxes a building with five apartments at the residential rate. Add a sixth and the whole building pays nearly the commercial rate.")}</p>')
    b.append('<p class="byline">By Liam Freaney · from the City&#8217;s tax ordinance and its 2025 tax roll</p>')
    b.append('<div class="big">'
             f'<div><b>{R(RATES["1B"])}</b><span>per $1,000 of value, two to five apartments</span></div>'
             f'<div><b>{R(RATES["1C"])}</b><span>six to ten apartments</span></div>'
             f'<div><b>{R(RATES["1D"])}</b><span>eleven or more</span></div>'
             f'<div><b>{M(shift)}</b><span>a year the 2024&#8211;26 apartments pay above the two-to-five rate</span></div></div>')

    b.append('<h2>Where the line is</h2>')
    b.append('<p>Providence sorts property into tax classes, and each class has its own rate. For rental housing the classes follow the number of apartments in the building:</p>')
    b.append('<div class="tablewrap"><table><tr><th>Class</th><th>Apartments in the building</th><th class="n">FY26 rate per $1,000</th></tr>'
             f'<tr><td>1A</td><td>one</td><td class="n">{R(RATES["1A"])}</td></tr>'
             f'<tr><td>1B</td><td>two to five</td><td class="n">{R(RATES["1B"])}</td></tr>'
             f'<tr><td>1C</td><td>six to ten</td><td class="n">{R(RATES["1C"])}</td></tr>'
             f'<tr><td>1D</td><td>eleven or more</td><td class="n">{R(RATES["1D"])}</td></tr>'
             f'<tr><td>2A</td><td>commercial and industrial</td><td class="n">{R(RATES["2A"])}</td></tr></table></div>')
    b.append('<p class="cite">Non-owner-occupied rates. Owner-occupied homes pay $8.40 (one unit) and $7.55 (two to five). Code of Ordinances &#167;21-182, as amended by the FY26 tax ordinance (FY26 Approved Ordinance Book, City of Providence), under R.I. Gen. Laws &#167;44-5-11.18; the same rates appear in the R.I. Division of Municipal Finance&#8217;s 2025 tax rate table.</p>')
    b.append('<p>The line sits between five and six apartments. A sixth apartment takes the whole building from $14.00 to $26.00 per $1,000, 89% of the commercial rate. A building of eleven or more pays 98% of it.</p>')
    b.append(f'<p>The City&#8217;s 2025 tax roll follows the rule. Of {i(L["1C"], "All"):,} parcels with six to ten apartments, {i(L["1C"], "1C"):,} are taxed in class 1C; of {i(L["1D"], "All"):,} with eleven or more, {i(L["1D"], "1D"):,} are in 1D. Most of the rest are taxed as commercial. Condominiums are different: each condo unit is its own parcel, so a condo building of any size pays the one-unit or two-to-five rate.</p>')
    b.append('<p class="cite">2025 tax roll and assessor (CAMA) file, data.providenceri.gov, pulled Sept. 10, 2026: each parcel&#8217;s levy code against its residential unit count, <a href="data/class_line.csv">class_line.csv</a>. The rates implied by the roll (taxes over net assessment) match the ordinance to the cent.</p>')

    b.append('<h2>The new apartments are on the high side <span class="tag model">MODEL</span></h2>')
    b.append(f'<p>Providence issued permits for {tot:,} new homes from 2024 through October 2026. {units["1D"]:,} of them are in buildings of eleven or more. Here is what each group pays at today&#8217;s rates, and what it would pay at the two-to-five rate:</p>')
    b.append('<div class="tablewrap"><table><tr><th>Building</th><th class="n">Permits</th><th class="n">Homes</th><th class="n">Tax per home, per year</th><th class="n">Taxes a year</th><th class="n">At the two-to-five rate</th></tr>')
    for k, lab in (("1A", "one home"), ("1B", "two to five"), ("1C", "six to ten"), ("1D", "eleven or more")):
        r = S[k]
        b.append(f'<tr><td>{lab}</td><td class="n">{i(r, "permits")}</td><td class="n">{i(r, "units"):,}</td><td class="n">{D(f(r, "tax_per_unit_yr"))}</td>'
                 f'<td class="n">{M(f(r, "taxes_yr"))}</td><td class="n">{M(f(r, "taxes_yr_if_taxed_as_1B"))}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">MODEL. Permits: Providence new-housing permits issued 2024 to Oct. 1, 2026 (APRA 26-2319), each building classed by its permitted units. Value per home: the median assessed value per unit of 2025-roll parcels built in 2015 or later in the same class (few in 1C and 1D: 4 and 6 parcels; parcels built since 2000 give close medians). <a href="data/class_line_surge.csv">class_line_surge.csv</a>.</p>')
    b.append(f'<p>A home in a building of eleven or more pays about {D(f(S["1D"], "tax_per_unit_yr"))} a year, about a quarter more than one in a two-to-five-family house ({D(f(S["1B"], "tax_per_unit_yr"))}), on a lower assessed value. Taxed at the two-to-five rate, the 2024&#8211;26 buildings of six or more would pay about {M(shift)} a year less, and the rest of the levy would carry it.</p>')

    b.append('<h2>What the sixth apartment costs a renter <span class="tag model">MODEL</span></h2>')
    b.append(f'<p>Take the same building, valued the same, on either side of the line. Crossing from five apartments to six adds about {D(six["1C"])} a year in tax per apartment ({D(six["1C"]/12)} a month). In a building of eleven or more the difference from the two-to-five rate is about {D(six["1D"])} a year per apartment ({D(six["1D"]/12)} a month).</p>')
    full = six["1C"] / 12 / FMR["2BR"]; half = full / 2
    b.append(f'<p>HUD&#8217;s fair market rent for the Providence area this year is {D(FMR["1BR"])} a month for a one-bedroom and {D(FMR["2BR"])} for a two-bedroom. '
             f'{C(f"If the whole six-to-ten difference reached the rent, it would be about {full:.0%} of a two-bedroom fair market rent; if half of it did, about {half:.0%}. How much of a property tax landlords pass to tenants is argued over, and this page does not settle it.")}</p>')
    b.append('<p class="cite">MODEL: value per apartment as in the table above, times the rate difference. HUD FY2026 Fair Market Rents, Providence-Fall River, RI-MA HUD Metro FMR Area (gross rent, utilities included), huduser.gov FMR documentation system.</p>')

    b.append('<h2>Not yet on the record</h2><ul class="open">'
             '<li>Why the line is at six. The class plan cites R.I. Gen. Laws &#167;44-5-11.18; the City&#8217;s reasons for the five/six break are not in the ordinance.</li>'
             '<li>Why some large apartment buildings are taxed as commercial (2A) rather than 1D. Some are mixed-use; the roll does not say which.</li></ul>')
    b.append('<h2>Data</h2><p>' + " · ".join(f'<a href="data/{x}">{x}</a>' for x in FILES) + '</p></main>')

    body = "".join(b)
    if RELEASE and "cmark" in body:
        raise SystemExit("apartments.py: RELEASE is on but [C] marks remain")
    (SITE / "apartments/data").mkdir(parents=True, exist_ok=True)
    (SITE / "apartments/index.html").write_text(page("The sixth apartment — Providence, on the record",
        "Providence taxes a five-apartment building at the residential rate and a six-apartment building at nearly the commercial rate.",
        "../", body, "apartments/"))
    for x in FILES:
        shutil.copy(H / x, SITE / "apartments/data" / x)
    return dict(shift=shift, six_1c=six["1C"])
