"""New housing in the regimes: a held section for Off the Roll. B1556, Nov 9 2026, from ../untaxed/new_housing.py.
Called from build.py: new_housing_row.render() -- ONLY when RELEASE is True, or for a local look with
NEWHOUSING_PREVIEW=1 python3 build.py (./deploy wipes site/ and rebuilds without it, so a preview never ships).

HELD. RELEASE stays False until Liam says "ship it". Before that:
  - every [C] line (Claude's framing, class="cmark") is taken, rewritten or cut;
  - three rules in new_housing.py are Claude's calls: units from CAMA where the permits count none; 'unknown' class
    priced as a 1B-1D range (none left after B1556a; a repeat-filed permit's stated units now count for its lot's class); exempt lots kept only where CAMA calls the use Charitable; a lot billed at or above its
    class has no foregone tax. He may want any of them changed;
  - which scope leads (built before the roll date, or every permit) is his call.
render() refuses to build with RELEASE=True while any [C] mark remains.
Re-pinned Nov 10 2026 after B1555's CO-extract unit fallback moved the row (finished before the roll: 18 lots / 213
apartments / $0.78-1.05M not collected -> 19 / 354 / $1.32-1.37M). Re-pinned Nov 13 2026 (B1556a): the five 'unknown'
lots are a 2021 scattered-site filing (BLDG-21-1381..1390), two units each by the permits' own count -> 1B; the range
closes at its low end: 19 / 364 / $1.32M; every permit 51 / 1,164 / $4.42M.
Every figure is read from ../untaxed/data/new-housing.json and pinned by assert, so a rerun that moves a number stops
the build before it reaches the page.
"""
import json, pathlib

U = pathlib.Path(__file__).parent.parent / "untaxed" / "data"
RELEASE = False
RATES = {"1A": 14.60, "1B": 14.00, "1C": 26.00, "1D": 28.50}      # s.21-182, FY26 tax ordinance [V]


def C(s):
    return f'<span class="cmark" style="background:var(--harbor-soft)" title="Claude&#8217;s wording, not yet Liam&#8217;s">[C] {s}</span>'


def M(x):
    return f"${x/1e6:.2f} million" if x >= 1e6 else f"${x:,.0f}"


def rng(a, b):
    return M(a) if round(a, -3) == round(b, -3) else f"{M(a)}&#8211;{M(b)}"


def render():
    J = json.load(open(U / "new-housing.json"))["scopes"]
    B, A = J["built before the roll date"], J["all permits with a plat-lot"]
    b0, a0 = B["row"], A["row"]
    # pins: a rerun of new_housing.py that moves any of these stops the build
    assert (b0["lots"], b0["units"], round(b0["pays"]), round(b0["at_class_lo"]), round(b0["at_class_hi"])) == (19, 364, 593560, 1915312, 1915312)
    assert (round(b0["foregone_lo"]), round(b0["foregone_hi"]), b0["unknown_class_lots"]) == (1321750, 1321750, 0)
    assert (a0["lots"], a0["units"], round(a0["pays"]), round(a0["foregone_lo"]), round(a0["foregone_hi"])) == (51, 1164, 3456777, 4422396, 4422396)
    assert (A["institutional_set_aside"]["lots"], round(A["institutional_set_aside"]["assessed"] / 1e6)) == (12, 188)
    assert (a0["lots_paying_at_or_above_class"], b0["lots_paying_at_or_above_class"]) == (7, 0)

    out = ['<h2>New housing in the regimes</h2>']
    if not RELEASE:
        out.append('<p class="cite" style="border-left:3px solid var(--record);padding-left:10px">PREVIEW, not published. '
                   'Lines marked [C] are Claude&#8217;s wording awaiting Liam&#8217;s read.</p>')
    out.append(f'<p>{C("Some of the housing Providence has permitted since 2010 sits under the 8% affordable-housing law, a tax stabilization agreement, or a nonprofit exemption. Those buildings pay less than an apartment building of the same size would.")}</p>')
    out.append('<p>The City taxes rental buildings by the number of apartments: $14.00 per $1,000 of value for two to five, $26.00 for six to ten, $28.50 for eleven or more, and $14.60 for a single unit. '
               f'Of the buildings finished on new-housing permits before the 2025 roll was set, {b0["lots"]} lots with {b0["units"]:,} apartments are in these regimes. '
               f'They were billed {M(b0["pays"])}. At their own class rates they would owe {rng(b0["at_class_lo"], b0["at_class_hi"])}.</p>')
    out.append('<div class="tablewrap"><table><tr><th>Permits</th><th class="n">Lots</th><th class="n">Apartments</th><th class="n">Billed, 2025</th><th class="n">At class rate</th><th class="n">Not collected</th></tr>')
    for label, s in (("Finished before the 2025 roll", b0), ("Every permit with a lot, 2010&#8211;26", a0)):
        out.append(f'<tr><td>{label}</td><td class="n">{s["lots"]}</td><td class="n">{s["units"]:,}</td><td class="n">{M(s["pays"])}</td>'
                   f'<td class="n">{rng(s["at_class_lo"], s["at_class_hi"])}</td><td class="n">{rng(s["foregone_lo"], s["foregone_hi"])}</td></tr>')
    out.append('</table></div>')
    out.append('<div class="tablewrap"><table><tr><th>Regime, every permit with a lot</th><th class="n">Lots</th><th class="n">Apartments</th><th class="n">Billed</th><th class="n">Not collected</th></tr>')
    for k, r in A["by_regime"].items():
        out.append(f'<tr><td>{"Tax stabilization agreement" if k == "TSA" else "8% affordable-housing law" if k == "8% law" else "Nonprofit, exempt"}</td>'
                   f'<td class="n">{int(r["lots"])}</td><td class="n">{int(r["units"]):,}</td><td class="n">{M(r["pays"])}</td><td class="n">{rng(r["foregone_lo"], r["foregone_hi"])}</td></tr>')
    out.append('</table></div>')
    # B1652 (Nov 14 2026): per apartment, per year, and the terms still running - held like the rest; pinned
    PU = json.load(open(U / "new-housing-per-unit.json"))
    pb, pa = PU["built before the roll date"], PU["all permits with a plat-lot"]
    assert (pb["per_unit_year_all"], pa["per_unit_year_all"]) == (3631, 3799)
    assert (pb["by_regime"]["8% affordable-housing law"]["per_unit_year"], pb["by_regime"]["tax stabilization agreement"]["per_unit_year"]) == (3852, 2995)
    assert pb["projection"]["by_regime"]["8% affordable-housing law"] == 30307686
    out.append(f'<p>Per apartment, the buildings finished before the roll pay about ${pb["per_unit_year_all"]:,} a year less than their class rate would charge: '
               f'${pb["by_regime"]["8% affordable-housing law"]["per_unit_year"]:,} under the 8% law and ${pb["by_regime"]["tax stabilization agreement"]["per_unit_year"]:,} under a stabilization agreement. '
               f'{C("Held at the 2025 rate and assessment, the 8% law lots finished before the roll would forgo about " + M(pb["projection"]["by_regime"]["8% affordable-housing law"]) + " more over their terms, if each runs 30 years from completion; the repo holds no restriction end dates, so the 30 years is an assumption.")}</p>')
    out.append(f'<p>{C("Where a building&#8217;s own permits don&#8217;t count its apartments, the assessor&#8217;s file does. Lots billed at or above their class rate count as nothing foregone. Schools, churches and City property that drew a housing permit are left out; their value is already in the fully exempt row above.")}</p>')
    out.append('<p class="cite">City of Providence building permits since 2010 joined to the 2025 tax roll and its assessor file (CAMA, Sept. 10, 2026); class rates from Code of Ordinances s.21-182 as amended by the FY26 tax ordinance. '
               f'The &#8220;every permit&#8221; row includes 2025&#8211;26 lots that may still be assessed as land or as the old building. Lot by lot: <a href="data/new-housing.csv">new-housing.csv</a>; per apartment: <a href="data/new-housing-per-unit.csv">new-housing-per-unit.csv</a>.</p>')
    html = "".join(out)
    if RELEASE and "cmark" in html:
        raise SystemExit("new_housing_row.py: RELEASE is on but [C] marks remain")
    return html
