"""New housing in the regimes: a held section for Off the Roll. B1556, Nov 9 2026, from ../untaxed/new_housing.py.
Called from build.py: new_housing_row.render() -- ONLY when RELEASE is True, or for a local look with
NEWHOUSING_PREVIEW=1 python3 build.py (./deploy wipes site/ and rebuilds without it, so a preview never ships).

HELD. RELEASE stays False until Liam says "ship it". Before that:
  - every [C] line (Claude's framing, class="cmark") is taken, rewritten or cut;
  - three rules in new_housing.py are Claude's calls: units from CAMA where the permits count none; 'unknown' class
    priced as a 1B-1D range; exempt lots kept only where CAMA calls the use Charitable; a lot billed at or above its
    class has no foregone tax. He may want any of them changed;
  - which scope leads (built before the roll date, or every permit) is his call.
render() refuses to build with RELEASE=True while any [C] mark remains.
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
    assert (b0["lots"], b0["units"], round(b0["pays"]), round(b0["at_class_lo"]), round(b0["at_class_hi"])) == (18, 213, 521811, 1301905, 1572977)
    assert (round(b0["foregone_lo"]), round(b0["foregone_hi"]), b0["unknown_class_lots"]) == (780091, 1051164, 6)
    assert (a0["lots"], a0["units"], round(a0["pays"]), round(a0["foregone_lo"]), round(a0["foregone_hi"])) == (51, 1010, 3456777, 3999648, 4467561)
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
    out.append(f'<p>{C("Ranges are where the roll does not say how many apartments a building has; those lots are priced between the two-to-five and eleven-or-more rates. Lots billed at or above their class rate count as nothing foregone. Schools, churches and City property that drew a housing permit are left out; their value is already in the fully exempt row above.")}</p>')
    out.append('<p class="cite">City of Providence building permits since 2010 joined to the 2025 tax roll and its assessor file (CAMA, Sept. 10, 2026); class rates from Code of Ordinances s.21-182 as amended by the FY26 tax ordinance. '
               f'The &#8220;every permit&#8221; row includes 2025&#8211;26 lots that may still be assessed as land or as the old building. Lot by lot: <a href="data/new-housing.csv">new-housing.csv</a>.</p>')
    html = "".join(out)
    if RELEASE and "cmark" in html:
        raise SystemExit("new_housing_row.py: RELEASE is on but [C] marks remain")
    return html
