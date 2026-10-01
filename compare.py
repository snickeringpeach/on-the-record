"""Providence and Boston side by side: what colleges and hospitals pay on exempt property.
Rendered from ../records/products/off-the-roll (pvd and bos, latest version of each).
Called from build.py: compare.render(page, e, SITE, DATELINE)."""
import csv, json, shutil, pathlib, re

REC = pathlib.Path(__file__).parent.parent / "records" / "products" / "off-the-roll"


def latest(city):
    vs = sorted((p for p in (REC / city).glob("v*") if p.is_dir()),
                key=lambda p: [int(x) for x in re.findall(r"\d+", p.name)])
    return vs[-1]


def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None


def rows():
    out = []
    pv = latest("pvd")
    for r in csv.DictReader(open(next(pv.glob("institutions_pvd_*.csv")))):
        if r["owner_type"] not in ("university", "hospital") or not num(r["agreement_cash"]): continue
        out.append(dict(city="Providence", name=r["name"], type=r["owner_type"], exempt=num(r["exempt_value"]),
                        cash=num(r["agreement_cash"]), credit=None, basis=None, requested=None, pct=None,
                        taxed=num(r["tax_billed"]) or 0, year=r["agreement_fiscal_year"]))
    bv = latest("bos")
    for r in csv.DictReader(open(next(bv.glob("institutions_bos_*.csv")))):
        if not r["agreement_requested"]: continue
        out.append(dict(city="Boston", name=r["name"], type=r["owner_type"], exempt=num(r["exempt_value"]) or 0,
                        cash=num(r["agreement_cash"]) or 0, credit=num(r["agreement_credit"]) or 0,
                        basis=num(r["agreement_value_basis"]), requested=num(r["agreement_requested"]),
                        pct=num(r["agreement_pct_met"]), taxed=num(r["tax_billed"]) or 0, year="FY" + r["agreement_fiscal_year"]))
    for x in out:
        # A Boston institution whose roll match is under half the City's own value basis is not ranked:
        # its property is probably held under names the adapter doesn't resolve yet (see DEFECTS.md).
        x["partial"] = bool(x["basis"]) and x["exempt"] < 0.5 * x["basis"]
        ok = x["exempt"] > 0 and not x["partial"]
        x["per"] = 1000 * x["cash"] / x["exempt"] if ok else None
        x["per_cr"] = 1000 * (x["cash"] + x["credit"]) / x["exempt"] if ok and x["credit"] is not None else None
    return out, pv, bv


def history(bv):
    f = next(bv.glob("pilot_history_bos_*.csv"), None)
    if not f: return None, []
    H = list(csv.DictReader(open(f)))
    for h in H:
        for k in ("value_basis", "requested_pilot", "community_benefit_credit", "cash_contribution"):
            h[k] = float(h[k] or 0)
    return f, H


def render(page, e, SITE, DATELINE):
    X, pv, bv = rows()
    M = lambda v: "&#8212;" if v is None else (f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M" if v >= 1e6 else f"${round(v, -3):,.0f}" if v >= 1e4 else f"${v:,.0f}")
    D = lambda v: "&#8212;" if v is None else f"${v:.2f}"
    W = lambda n: ["zero","one","two","three","four","five","six","seven","eight","nine"][n] if n < 10 else str(n)
    pct = lambda v: "&#8212;" if v is None else f"{v:.0f}%"
    ranked = sorted((x for x in X if x["per"] is not None), key=lambda x: -x["per"])
    def tot(city):
        xs = [x for x in ranked if x["city"] == city]
        ex, ca = sum(x["exempt"] for x in xs), sum(x["cash"] for x in xs)
        cr = sum(x["credit"] or 0 for x in xs)
        return dict(n=len(xs), exempt=ex, cash=ca, per=1000 * ca / ex, per_cr=1000 * (ca + cr) / ex)
    P, B = tot("Providence"), tot("Boston")
    brown = next(x for x in ranked if x["name"] == "Brown University")
    rank = ranked.index(brown) + 1
    above_cr = [x for x in ranked if x["city"] == "Boston" and x["per_cr"] > brown["per"]]
    skipped = [x for x in X if x["per"] is None]
    big4 = [x for x in ranked if x["name"] in ("Boston University", "Harvard University", "Massachusetts General Hospital", "Northeastern University")]

    b = [f'<main><div class="dateline">{DATELINE}</div>',
         '<h1>What Colleges and Hospitals Pay on Their Exempt Property, in Providence and in Boston</h1>',
         f'<p class="deck">For every $1,000 of exempt property on the tax roll, the {W(P["n"])} Providence colleges and hospitals paid the City {D(P["per"])} in cash in fiscal 2025. Boston&#8217;s {B["n"]} PILOT institutions paid Boston {D(B["per"])}. Boston also credits community programs against what it asks; counted that way, its figure is {D(B["per_cr"])}.</p>',
         '<p class="byline">From both cities&#8217; tax rolls, Providence&#8217;s payment agreements and Boston&#8217;s PILOT recap</p>',
         '<div class="big">'
         f'<div><b>{D(P["per"])}</b><span>cash per $1,000 of exempt property, Providence, {P["n"]} institutions</span></div>'
         f'<div><b>{D(B["per"])}</b><span>cash per $1,000 of exempt property, Boston, {B["n"]} institutions</span></div>'
         f'<div><b>{D(brown["per"])}</b><span>Brown University, '
         + ("the highest" if rank == 1 else f"number {rank}") + f' of the {len(ranked)} in either city</span></div>'
         f'<div><b>{D(B["per_cr"])}</b><span>Boston, counting the community-benefit credits it allows</span></div></div>']
    b.append(f'<p>These institutions hold {M(P["exempt"])} of exempt property in Providence and {M(B["exempt"])} in Boston. In cash, the Providence institutions paid {M(P["cash"])} and the Boston institutions {M(B["cash"])}. '
             f'Brown paid {M(brown["cash"])} on {M(brown["exempt"])}, or {D(brown["per"])} per $1,000. '
             + "Of Boston&#8217;s four largest holders, " + ", ".join(f'{e(x["name"])} paid {D(x["per"])}' for x in big4) + '. '
             f'Counting Boston&#8217;s credits, {W(len(above_cr))} Boston institution{"s" if len(above_cr) != 1 else ""} come out above Brown&#8217;s cash figure'
             + (": " + ", ".join(e(x["name"]) for x in above_cr) if above_cr else "") + '.</p>')

    b.append('<h2>Every institution, ranked by cash per $1,000 of exempt property</h2>'
             '<div class="tablewrap"><table><tr><th>Institution</th><th>City</th><th class="n">Exempt property on the roll</th>'
             '<th class="n">Cash paid</th><th class="n">Per $1,000</th><th class="n">Per $1,000 with Boston&#8217;s credit</th>'
             '<th class="n">Boston&#8217;s own % met</th><th class="n">Tax billed on its taxable parcels</th></tr>')
    for x in ranked:
        st = ' style="background:var(--hl,rgba(0,0,0,.05))"' if x["city"] == "Providence" else ""
        b.append(f'<tr{st}><td>{e(x["name"])}</td><td>{x["city"]}</td><td class="n">{M(x["exempt"])}</td><td class="n">{M(x["cash"])}</td>'
                 f'<td class="n"><b>{D(x["per"])}</b></td><td class="n">{D(x["per_cr"])}</td>'
                 f'<td class="n">{pct(x["pct"])}</td><td class="n">{M(x["taxed"])}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">Providence rows are shaded. Exempt property is the assessed value of fully exempt parcels the roll lists under the institution&#8217;s name. '
             'Cash is what the institution paid the City in fiscal 2025 (July 2024 through June 2025) under its agreement or, in Boston, the PILOT program. '
             'Boston&#8217;s &#8220;% met&#8221; is the City&#8217;s own measure, cash plus credit against what it asked. '
             'The last column is ordinary property tax on parcels the institution owns that are not exempt; it is not part of the payment. '
             + "".join(f'{e(x["name"])}&#8217;s payment is the latest on record, for fiscal {x["year"]}. ' for x in ranked if x["city"] == "Providence" and x["year"] != "FY2025")
             + (f'Not ranked, because the roll under their names holds less than half the property Boston&#8217;s recap counts for them: {", ".join(e(x["name"]) for x in skipped)}. ' if skipped else "")
             + '</p>')

    hf, H = history(bv)
    if H:
        years = sorted({int(h["fiscal_year"]) for h in H})
        b.append(f'<h2>Five years of Boston&#8217;s PILOT, FY{years[0]} to FY{years[-1]}</h2>'
                 '<div class="tablewrap"><table><tr><th>Fiscal year</th><th class="n">Institutions</th><th class="n">Asked</th>'
                 '<th class="n">Credited for community programs</th><th class="n">Paid in cash</th><th class="n">Cash as share of ask</th></tr>')
        for y in years:
            hs = [h for h in H if int(h["fiscal_year"]) == y]
            rq = sum(h["requested_pilot"] for h in hs); cr = sum(h["community_benefit_credit"] for h in hs); ca = sum(h["cash_contribution"] for h in hs)
            b.append(f'<tr><td>FY{y}</td><td class="n">{len(hs)}</td><td class="n">{M(rq)}</td><td class="n">{M(cr)}</td><td class="n">{M(ca)}</td><td class="n">{ca/rq:.0%}</td></tr>')
        b.append('</table></div>')
        by = {}
        for h in H: by.setdefault(h["institution"], {})[int(h["fiscal_year"])] = h
        full = {i: d for i, d in by.items() if len(d) == len(years)}
        frozen = sorted(i for i, d in full.items() if len({d[y]["value_basis"] for y in years}) == 1)
        ex = [i for i in ("Berklee College of Music", "Boston College", "Emerson College") if i in frozen]
        grow = sorted((d[years[-1]]["requested_pilot"] / d[years[0]]["requested_pilot"]) ** (1 / (len(years) - 1)) - 1
                      for i, d in full.items() if i in frozen and d[years[0]]["requested_pilot"])
        g = grow[len(grow) // 2] if grow else 0
        b.append(f'<p>What Boston asks has risen every year; cash has not. The ask grew from {M(sum(h["requested_pilot"] for h in H if int(h["fiscal_year"]) == years[0]))} to '
                 f'{M(sum(h["requested_pilot"] for h in H if int(h["fiscal_year"]) == years[-1]))}, while cash stayed near $35 million. The difference was made up in credits. '
                 f'Six museums left the table in FY2024, when the City moved them to what its recap calls &#8220;an alternative system&#8221; of reporting community benefits, so the earlier years count more institutions.</p>')
        b.append(f'<p>The valuation behind the asks has barely moved. For {len(frozen)} of the {len(full)} institutions listed in all five years, the City&#8217;s value basis is the same to the dollar in FY{years[0]} and FY{years[-1]}: '
                 + ", ".join(f'{e(i)} at {M(full[i][years[-1]]["value_basis"])}' for i in ex)
                 + f'. Their asks rose about {g:.1%} a year all the same. The recaps do not say what year&#8217;s values the basis comes from.</p>')

    b.append('<h2>How Boston asks</h2>'
             '<p>Boston asks every nonprofit holding more than $15 million in property to pay a quarter of what it would owe if the property were taxed, the share of the City&#8217;s budget its 2010 PILOT Task Force tied to police, fire, snow removal and other basic services. '
             'Generally up to half of that request can be met with community programs the City credits as directly benefiting Boston residents. '
             'The City sets each institution&#8217;s request on a &#8220;value basis&#8221; of its own and publishes the request, the cash, the credit and the share met every year. '
             'Providence has no formula. Each institution&#8217;s payment is set by its own agreement with the City, and the State separately reimburses the City for part of the tax it does not collect from colleges and hospitals. Massachusetts has no such payment for private colleges and hospitals.</p>')
    b.append('<h2>What doesn&#8217;t line up</h2><ul class="open">'
             '<li>The two rolls value property as of nearly the same day, Dec. 31, 2024 in Providence and Jan. 1, 2025 in Boston, but under two states&#8217; laws, by two assessors&#8217; offices, with two different practices for exempt property, which neither city taxes and so has less reason to value closely.</li>'
             '<li>Boston&#8217;s value basis runs well below the exempt property on its own roll for most institutions: Boston University&#8217;s is $2.62 billion against $4.11 billion on the roll. For most institutions it has not changed in five years (above). Every per-$1,000 figure here uses the roll, in both cities, so the comparison measures the same thing on each side.</li>'
             '<li>Payments are for fiscal 2025. Boston&#8217;s roll is fiscal 2026&#8217;s, the first one that values property as of the start of 2025.</li>'
             '<li>Harvard&#8217;s figures are for its Boston property only, mostly in Allston. What it pays Cambridge is not here.</li>'
             '<li>Providence&#8217;s rows are the six colleges and hospitals that pay the City. Other exempt owners, and Providence Place, are on <a href="../">Off the Roll</a>.</li></ul>')
    b.append('<h2>Not yet on the record</h2><ul class="open">'
             '<li>How Boston sets each institution&#8217;s value basis: which parcels it counts, whether it leaves out student housing, and which year&#8217;s values it uses.</li>'
             + (f'<li>The parcels behind the Boston institutions not ranked above.</li>' if skipped else '')
             + '<li>Three Boston owners are matched by address and history rather than by name: Franciscan Children&#8217;s, listed as &#8220;Joseph P Kennedy Jr,&#8221; its original name; Joslin, listed as &#8220;Diabetes Foundation Inc&#8221;; and part of MCPHS, listed as &#8220;Massachusetts College of.&#8221;</li></ul>')

    out = SITE / "off-the-roll/boston"; (out / "data").mkdir(parents=True, exist_ok=True)
    cols = ["city", "name", "type", "exempt", "cash", "credit", "basis", "requested", "pct", "taxed", "year", "per", "per_cr", "partial"]
    with open(out / "data/compare_pvd_bos.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["city", "name", "owner_type", "exempt_value", "cash_paid", "boston_credit", "boston_value_basis",
                                      "boston_requested", "boston_pct_met", "tax_billed_taxable_parcels", "payment_year",
                                      "cash_per_1000_exempt", "cash_plus_credit_per_1000_exempt", "roll_match_incomplete"])
        for x in X: w.writerow(["" if x[c] is None else (round(x[c], 4) if isinstance(x[c], float) else x[c]) for c in cols])
    files = ["compare_pvd_bos.csv"]
    for d in (pv, bv):
        for p in list(d.glob("institutions_*.csv")) + list(d.glob("pilot_history_*.csv")): shutil.copy(p, out / "data" / p.name); files.append(p.name)
    b.append('<h2>Data</h2><p>' + " · ".join(f'<a href="data/{f}">{f}</a>' for f in files) + '</p>'
             '<p class="cite">Sources: City of Providence 2025 tax roll and payment agreements; City of Boston FY2026 Property Assessment file (data.boston.gov) and PILOT Recaps, FY2021 through FY2025; City of Boston PILOT Task Force final report, 2010. '
             f'Built from Off the Roll {pv.name} (Providence) and {bv.name} (Boston). Data licensed CC BY 4.0: credit &#8220;Providence, on the record.&#8221;</p></main>')
    (out / "index.html").write_text(page("Providence and Boston — Off the Roll — Providence, on the record",
        "What colleges and hospitals pay on their exempt property, in Providence and in Boston, from both cities' tax rolls.",
        "../../", "".join(b), "off-the-roll/boston/"))
    return dict(P=P, B=B, brown=brown, rank=rank, n=len(ranked))
