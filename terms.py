"""Asked and paid: Providence's agreements on Boston's terms.

One page, per institution: exempt assessed value on the roll, what was asked, what was paid.
Boston's formula (2010 PILOT Task Force: a quarter of the tax at the commercial rate, nonprofits
over $15M, up to half payable in credited community programs) is applied to Providence's roll
and set beside Providence's agreements; Boston's own 38 are shown on the same terms.
Then the 66 stabilization agreements (asked = tax at full rate, paid = billed), with the
CC-15 "39 New York Avenue (Tangible)" row carried UNCONFIRMED.

Reads ../records/products/off-the-roll (pvd, bos: latest), ../records/core/pvd/2025/agreements_stabilization.csv,
site/off-the-roll/data/{roll-summary,tsa-ledger}.json. Boston's commercial rate is read from its roll.

Status: DRAFT (B63, Oct 5 2026). LIVE = False writes a self-contained copy to drafts/off-the-roll/terms/
and nothing under site/. To publish: set LIVE = True, add `import terms; terms.render(page, e, SITE, DATELINE)`
to build.py after compare, link it from the Off the Roll page, ./sync.

Claude's choices, marked here so they can be struck: (1) the formula is applied at each city's own
commercial rate to exempt value on its own roll, so both sides are measured the same way; (2) the table of
Providence nonprofits over Boston's $15M line that have no agreement; (3) sorting the stabilization
agreements by tax at full rate. Everything else is the record as the two cities publish it.
"""
import csv, json, pathlib, re, gzip, sys, html

HERE = pathlib.Path(__file__).parent
SITE = HERE / "site"
REC = HERE.parent / "records" / "products" / "off-the-roll"
CORE = HERE.parent / "records" / "core"
U = SITE / "off-the-roll" / "data"
LIVE = True
SHARE = 0.25          # Boston asks a quarter of the tax at full rate
THRESHOLD = 15_000_000  # of nonprofit institutions holding more than $15 million

e = html.escape


def latest(city):
    vs = sorted((p for p in (REC / city).glob("v*") if p.is_dir()), key=lambda p: [int(x) for x in re.findall(r"\d+", p.name)])
    return vs[-1]


def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None


def boston_rate():
    """Boston's FY2026 commercial rate, read from the roll: the modal tax/value on taxed commercial parcels."""
    import collections
    c = collections.Counter()
    with gzip.open(CORE / "bos/2026/parcels.csv.gz", "rt") as f:
        for r in csv.DictReader(f):
            if r["tax_regime"] != "taxed" or r["land_use_std"] != "commercial": continue
            v, t = num(r["taxable_value"]), num(r["tax_billed"])
            if v and t and v > 0: c[round(1000 * t / v, 2)] += 1
    return c.most_common(1)[0][0]


def load():
    roll = json.load(open(U / "roll-summary.json"))
    pr = roll["full_rate"]["commercial_per_1000"]
    br = boston_rate()
    pv, bv = latest("pvd"), latest("bos")
    P = list(csv.DictReader(open(next(pv.glob("institutions_pvd_*.csv")))))
    B = list(csv.DictReader(open(next(bv.glob("institutions_bos_*.csv")))))

    # Providence: the owners with a payment agreement.
    pvd = []
    for r in P:
        cash = num(r["agreement_cash"])
        if not cash: continue
        ex = num(r["exempt_value"]) or 0
        full = ex * pr / 1000
        pvd.append(dict(name=r["name"], type=r["owner_type"], exempt=ex, full=full, ask=SHARE * full, paid=cash,
                        year=r["agreement_fiscal_year"], nonprofit=r["owner_type"] in ("university", "hospital")))
    pvd.sort(key=lambda x: -x["exempt"])

    # Providence: nonprofits over Boston's line with no agreement. Named by hand from the roll's owner strings;
    # the owner typing in the product is a heuristic, so this list is the ones that can be classified by name.
    NAMES = {"PROVIDENCE PUBLIC LIBRARY": ("Providence Public Library", "library"),
             "NE YEARLY MEETING OF FRIENDS": ("New England Yearly Meeting of Friends (Moses Brown School)", "school"),
             "WHEELER SCHOOL": ("Wheeler School", "school"),
             "MEETING STREET": ("Meeting Street", "school"),
             "TIMES 2 INCORPORATED": ("Times2 STEM Academy", "charter school"),
             "PROVIDENCE BOYS CLUB": ("Boys & Girls Clubs of Providence", "youth"),
             }
    PCHC = ("PROVIDENCE COMMUNITY HEALTH CENTERS INC", "THE PROVIDENCE COMM HEALTH CENTERS, INC")
    others, pchc = [], 0.0
    for r in P:
        nm = r["name"].strip().upper()
        if nm in PCHC: pchc += num(r["exempt_value"]) or 0; continue
        if nm in NAMES:
            ex = num(r["exempt_value"]) or 0
            others.append(dict(name=NAMES[nm][0], kind=NAMES[nm][1], exempt=ex, ask=SHARE * ex * pr / 1000, note=""))
    if pchc > THRESHOLD:
        others.append(dict(name="Providence Community Health Centers", kind="health center", exempt=pchc, ask=SHARE * pchc * pr / 1000,
                           note="two spellings on the roll, combined here; it pays $150,000 a year under a stabilization agreement on another parcel (Beaman and Smith Mill)"))
    others = [o for o in others if o["exempt"] > THRESHOLD]
    others.sort(key=lambda x: -x["exempt"])

    # Boston: the 38 in the FY25 recap.
    bos = []
    for r in B:
        if not r["agreement_requested"]: continue
        ex = num(r["exempt_value"]) or 0; basis = num(r["agreement_value_basis"]) or 0
        bos.append(dict(name=r["name"], type=r["owner_type"], exempt=ex, basis=basis, asked=num(r["agreement_requested"]) or 0,
                        roll_ask=SHARE * ex * br / 1000, cash=num(r["agreement_cash"]) or 0, credit=num(r["agreement_credit"]) or 0,
                        pct=num(r["agreement_pct_met"]), partial=bool(basis) and ex < 0.5 * basis))
    bos.sort(key=lambda x: -x["exempt"])

    # Stabilization agreements: the auditor's 66, TY2024 at $35.10, plus the unconfirmed Tangible row.
    T = list(csv.DictReader(open(CORE / "pvd/2025/agreements_stabilization.csv")))
    tsa = []
    for r in T:
        rate = num(r["rate"]) or 35.1
        a, b_, f, ab = num(r["assessed"]), num(r["billed"]), num(r["full_rate_tax"]), num(r["abated"])
        note = []
        if a is None and r["address"].startswith("126 Adelaide"):
            a = 443_989; note.append("assessment cell blank in the report; implied by the bill at $35.10")
        if f is None and a is not None:
            f = a * rate / 1000; note.append("the report prints no full-rate column for this agreement; computed at $35.10")
        if ab is None and f is not None and b_ is not None: ab = f - b_
        tsa.append(dict(owner=r["owner_as_reported"], address=r["address"], ordinance=r["ordinance"], assessed=a, full=f, billed=b_,
                        abated=ab, report=r["annual_report"], note="; ".join(note), unconfirmed=False))
    tsa.append(dict(owner="McInnis USA Inc", address="39 New York Avenue (Tangible), CC-15", ordinance="2016-8 No. 99",
                    assessed=31_733_578, full=1_113_849, billed=16_311, abated=1_113_849 - 16_311, report="",
                    note="UNCONFIRMED. Listed in the report's index with no exhibit page; these figures are what the printed Table 1 totals leave over once the other 65 are subtracted (within $33 on assessed value). Not yet confirmed by the Internal Auditor.",
                    unconfirmed=True))
    tsa.sort(key=lambda x: -(x["full"] or 0))
    audit = json.load(open(U / "tsa-ledger.json"))["city_audit_fy2025"]
    return dict(pr=pr, br=br, pvd=pvd, others=others, bos=bos, tsa=tsa, audit=audit, pv=pv, bv=bv)


M = lambda v: "&#8212;" if v is None else (f"${v/1e9:.2f}B" if abs(v) >= 1e9 else f"${v/1e6:.1f}M" if abs(v) >= 1e6 else f"${round(v, -3):,.0f}" if abs(v) >= 1e4 else f"${v:,.0f}")
pct = lambda v: "&#8212;" if v is None else f"{v:.0%}"


def body(D, DATELINE):
    pvd, bos, others, tsa, au = D["pvd"], D["bos"], D["others"], D["tsa"], D["audit"]
    six = [x for x in pvd if x["nonprofit"]]
    mall = [x for x in pvd if not x["nonprofit"]]
    S = lambda xs, k: sum(x[k] for x in xs)
    p_ask, p_paid, p_ex = S(six, "ask"), S(six, "paid"), S(six, "exempt")
    b_ex, b_asked, b_roll, b_cash, b_cr = S(bos, "exempt"), S(bos, "asked"), S(bos, "roll_ask"), S(bos, "cash"), S(bos, "credit")
    brown = next(x for x in six if x["name"] == "Brown University")
    rest = [x for x in six if x is not brown]
    b = [f'<main><div class="dateline">{DATELINE}</div>',
         '<h1>Asked and Paid: Providence&#8217;s Agreements on Boston&#8217;s Terms</h1>',
         f'<p class="deck">Boston asks its colleges and hospitals for a quarter of the tax their exempt property would owe. Asked that way, on the 2025 roll at Providence&#8217;s commercial rate, Providence&#8217;s six paying colleges and hospitals would be asked {M(p_ask)} a year. Under their agreements they paid {M(p_paid)}, {pct(p_paid/p_ask)} of it. Boston asked its 38 institutions {M(b_asked)} in fiscal 2025 and was paid {M(b_cash)} in cash, {pct(b_cash/b_asked)}; the rest was met in credited community programs or not at all.</p>',
         '<p class="byline">From both cities&#8217; tax rolls, Providence&#8217;s payment agreements and the City Internal Auditor&#8217;s FY2025 report, and Boston&#8217;s FY25 PILOT recap</p>',
         '<div class="big">'
         f'<div><b>{M(p_ask)}</b><span>what Boston&#8217;s formula would ask of Providence&#8217;s six, a year</span></div>'
         f'<div><b>{M(p_paid)}</b><span>what the six paid the City in fiscal 2025, {pct(p_paid/p_ask)} of that ask</span></div>'
         f'<div><b>{pct(brown["paid"]/brown["ask"])}</b><span>Brown&#8217;s payment as a share of the formula ask; the other five together, {pct(S(rest,"paid")/S(rest,"ask"))}</span></div>'
         f'<div><b>{pct(b_cash/b_asked)}</b><span>cash share of Boston&#8217;s own ask, fiscal 2025, across 38 institutions</span></div></div>']

    b.append('<h2>Providence: the six that pay, on Boston&#8217;s terms</h2>'
             f'<p>Exempt value is the assessed value of fully exempt parcels the 2025 roll lists under the institution. The tax at full rate prices it at the commercial rate the roll bills, ${D["pr"]:.2f} per $1,000. Boston&#8217;s formula asks a quarter of that. The last two columns are what the institution actually paid the City under its agreement, and that payment as a share of the formula ask.</p>'
             '<div class="tablewrap"><table><tr><th>Institution</th><th class="n">Exempt value on the roll</th><th class="n">Tax at full rate</th><th class="n">A quarter of it (Boston&#8217;s ask)</th><th class="n">Paid under agreement</th><th class="n">Paid as share of ask</th></tr>')
    for x in six:
        b.append(f'<tr><td>{e(x["name"])}</td><td class="n">{M(x["exempt"])}</td><td class="n">{M(x["full"])}</td><td class="n"><b>{M(x["ask"])}</b></td><td class="n">{M(x["paid"])}{"" if x["year"]=="FY2025" else " <small>(" + e(x["year"]) + ")</small>"}</td><td class="n"><b>{pct(x["paid"]/x["ask"])}</b></td></tr>')
    b.append(f'<tr style="border-top:2px solid var(--ink)"><td><b>Six institutions</b></td><td class="n"><b>{M(p_ex)}</b></td><td class="n"><b>{M(S(six,"full"))}</b></td><td class="n"><b>{M(p_ask)}</b></td><td class="n"><b>{M(p_paid)}</b></td><td class="n"><b>{pct(p_paid/p_ask)}</b></td></tr>')
    for x in mall:
        b.append(f'<tr style="color:var(--muted)"><td>{e(x["name"])} <small>(not a nonprofit; exempt by Council vote)</small></td><td class="n">{M(x["exempt"])}</td><td class="n">{M(x["full"])}</td><td class="n">{M(x["ask"])}</td><td class="n">{M(x["paid"])} <small>({e(x["year"])})</small></td><td class="n">{pct(x["paid"]/x["ask"])}</td></tr>')
    b.append('</table></div>')
    b.append('<p class="cite">Payments: Brown, $11.1 million in direct voluntary payments in fiscal 2025 (Brown&#8217;s Community Contributions report; Brown Daily Herald, Dec. 2025). RISD, Providence College and Johnson &amp; Wales, the fiscal 2025 payments scheduled in Exhibit A of the 2023 agreement. Brown University Health, $750,000 under the agreement signed Nov. 15, 2024. Care New England, $350,000 in 2024, the latest on record (Boston Globe, Oct. 1, 2024). Providence Place, about $1 million a year under its agreement (Boston Globe, Apr. 30 and Aug. 20, 2026); the mall is shown because it has an agreement, not because Boston&#8217;s program would reach it. '
             'The State separately paid Providence $37.3 million in fiscal 2025 for the tax its colleges and hospitals do not pay; that is not in this table, and Massachusetts makes no such payment to Boston.</p>')

    if others:
        b.append('<h2>Who else Boston&#8217;s line would reach</h2>'
                 f'<p>Boston asks every educational, medical and cultural nonprofit holding more than $15 million in property, so its 38 include day schools, a conservatory, an orchestra and a public broadcaster. On Providence&#8217;s roll these nonprofits hold more than $15 million of exempt property and have no payment agreement with the City. Religious owners are left out, as Boston leaves them out.</p>'
                 '<div class="tablewrap"><table><tr><th>Owner on the roll</th><th>Kind</th><th class="n">Exempt value</th><th class="n">A quarter of the tax at full rate</th></tr>')
        for o in others:
            b.append(f'<tr><td>{e(o["name"])}{" <small>(" + e(o["note"]) + ")</small>" if o["note"] else ""}</td><td>{e(o["kind"])}</td><td class="n">{M(o["exempt"])}</td><td class="n">{M(o["ask"])}</td></tr>')
        b.append(f'<tr style="border-top:2px solid var(--ink)"><td><b>{len(others)} owners</b></td><td></td><td class="n"><b>{M(S(others,"exempt"))}</b></td><td class="n"><b>{M(S(others,"ask"))}</b></td></tr></table></div>'
                 '<p class="cite">Owners are named from the roll&#8217;s owner strings; the roll does not type them, so this is the set that can be classified by name. Rhode Island Health and Educational Building Corporation, a state financing agency, holds $38.5 million of exempt property as a conduit for the nonprofits it finances and is not listed.</p>')

    b.append('<h2>Boston: the 38, on the same terms</h2>'
             f'<p>Boston publishes what it asked, on a &#8220;value basis&#8221; it sets itself, and what each institution paid in cash and in credited community programs. Beside the City&#8217;s own ask is what the same formula gives on Boston&#8217;s FY2026 roll: a quarter of the tax on the exempt value listed under the institution, at the commercial rate the roll bills, ${D["br"]:.2f} per $1,000.</p>'
             '<div class="tablewrap"><table><tr><th>Institution</th><th class="n">Exempt value on the roll</th><th class="n">City&#8217;s value basis</th><th class="n">City asked (FY25)</th><th class="n">A quarter of the tax on the roll</th><th class="n">Paid in cash</th><th class="n">Credited</th><th class="n">City&#8217;s % met</th></tr>')
    for x in bos:
        flag = ' <small>(roll match incomplete)</small>' if x["partial"] else ''
        pm = "&#8212;" if x["pct"] is None else f'{x["pct"]:.0f}%'
        b.append(f'<tr><td>{e(x["name"])}{flag}</td><td class="n">{M(x["exempt"])}</td><td class="n">{M(x["basis"])}</td><td class="n"><b>{M(x["asked"])}</b></td><td class="n">{M(x["roll_ask"])}</td><td class="n">{M(x["cash"])}</td><td class="n">{M(x["credit"])}</td><td class="n">{pm}</td></tr>')
    b.append(f'<tr style="border-top:2px solid var(--ink)"><td><b>38 institutions</b></td><td class="n"><b>{M(b_ex)}</b></td><td class="n"><b>{M(S(bos,"basis"))}</b></td><td class="n"><b>{M(b_asked)}</b></td><td class="n"><b>{M(b_roll)}</b></td><td class="n"><b>{M(b_cash)}</b></td><td class="n"><b>{M(b_cr)}</b></td><td class="n"><b>{(b_cash+b_cr)/b_asked:.0%}</b></td></tr></table></div>')
    b.append(f'<p class="cite">City of Boston FY25 PILOT Recap (Apr. 1, 2026) and FY2026 Property Assessment file (data.boston.gov). The value basis is the City&#8217;s own figure and is not recomputed here; for most institutions it has not changed since FY2021 and runs well below exempt value on the roll (Off the Roll&#8217;s <a href="../boston/">Providence and Boston</a> page). '
             f'On the roll, the formula would ask {M(b_roll)} against the City&#8217;s {M(b_asked)}; in cash the 38 paid {M(b_cash)}, {pct(b_cash/b_roll)} of the roll figure. Boston&#8217;s roll is fiscal 2026&#8217;s and values property as of Jan. 1, 2025; the recap is fiscal 2025&#8217;s.</p>')

    b.append('<h2>Providence&#8217;s stabilization agreements: asked and billed</h2>'
             f'<p>A tax stabilization agreement fixes a developer&#8217;s bill below the full rate for a set term. The City Internal Auditor&#8217;s FY2025 report lists {au["agreements"]} agreements covering {M(au["assessed"])} of property, billed {M(au["billed"])} against {M(au["full_rate"])} at the full rate, {M(au["abated"])} abated in one year, at the 2024 rates ($35.10 commercial) before the 2025 revaluation. Those printed totals are the record. The rows below are the report&#8217;s exhibit pages, one per agreement, which add to within 0.1% of the printed bill; one agreement in the report&#8217;s index has no exhibit page and is carried as unconfirmed.</p>'
             '<div class="tablewrap"><table><tr><th>Agreement</th><th class="n">Assessed (2024)</th><th class="n">Tax at full rate</th><th class="n">Billed</th><th class="n">Abated</th><th>Annual report filed</th></tr>')
    for t in tsa:
        st = ' style="background:var(--record-soft)"' if t["unconfirmed"] else ''
        tag = '<span class="tag" style="background:var(--record);color:#fff">UNCONFIRMED</span> ' if t["unconfirmed"] else ''
        note = f'<br><small>{e(t["note"])}</small>' if t["note"] else ''
        b.append(f'<tr{st}><td>{tag}{e(t["owner"])}, {e(t["address"])}{note}</td><td class="n">{M(t["assessed"])}</td><td class="n">{M(t["full"])}</td><td class="n">{M(t["billed"])}</td><td class="n">{M(t["abated"])}</td><td>{e(t["report"]) or "&#8212;"}</td></tr>')
    conf = [t for t in tsa if not t["unconfirmed"]]
    b.append(f'<tr style="border-top:2px solid var(--ink)"><td><b>{len(conf)} agreements with exhibit pages</b></td><td class="n"><b>{M(sum(t["assessed"] or 0 for t in conf))}</b></td><td class="n"><b>{M(sum(t["full"] or 0 for t in conf))}</b></td><td class="n"><b>{M(sum(t["billed"] or 0 for t in conf))}</b></td><td class="n"><b>{M(sum(t["abated"] or 0 for t in conf))}</b></td><td></td></tr>'
             f'<tr><td><b>Printed Table 1 totals, {au["agreements"]} agreements</b></td><td class="n"><b>{M(au["assessed"])}</b></td><td class="n"><b>{M(au["full_rate"])}</b></td><td class="n"><b>{M(au["billed"])}</b></td><td class="n"><b>{M(au["abated"])}</b></td><td></td></tr></table></div>')
    b.append('<p class="cite">City of Providence Internal Auditor, Tax Stabilization Agreements report, FY2025 (August 2025): Table 1 and the exhibit page for each agreement, tax year 2024. &#8220;Annual report filed&#8221; is the report&#8217;s own compliance answer. '
             'Prospect CharterCare&#8217;s page prints no full-rate column, so its full-rate tax is computed at $35.10 on its printed assessment; 126 Adelaide Avenue&#8217;s assessment cell is blank and is implied from its bill. '
             'The 2025 roll, after revaluation, carries 137 parcels under these agreements billed $14.9 million against $33.9 million at the new $29.20 rate (<a href="../">Off the Roll</a>).</p>')

    b.append('<h2>How the two cities ask</h2>'
             '<p>Boston&#8217;s 2010 PILOT Task Force set the terms its recap still reports against: every educational, medical and cultural nonprofit holding more than $15 million in property is asked for a quarter of what the property would owe if taxed, the share of the City budget the Task Force tied to police, fire, snow removal and other basic services; generally up to half of the ask can be met with community programs the City credits; the City sets the value basis and publishes the ask, the cash, the credit and the share met every year. '
             'Providence has no formula. Each payment is set by its own agreement: the 2023 twenty-year agreement with Brown, RISD, Providence College and Johnson &amp; Wales fixes every year&#8217;s payment through fiscal 2043; Brown&#8217;s separate ten-year agreement adds $46 million; the hospitals and the mall have agreements of their own. Stabilization agreements are ordinances, one per project, each with its own schedule. The State reimburses Providence for part of the college and hospital tax it does not collect; Massachusetts does not.</p>')
    b.append('<h2>What doesn&#8217;t line up</h2><ul class="open">'
             '<li>The formula columns are arithmetic, not a record: a quarter of exempt value times each city&#8217;s commercial rate. Boston itself does not compute its ask on the roll. It computes it on a value basis of its own that runs at about half of roll value, so Boston&#8217;s published ask is lower than its own formula on its own roll.</li>'
             '<li>Years. Providence&#8217;s roll is tax year 2025, after revaluation, at $29.20; its payments are fiscal 2025; the stabilization report is tax year 2024 at $35.10. Boston&#8217;s roll is fiscal 2026 at $26.96; its recap is fiscal 2025.</li>'
             '<li>Boston&#8217;s roll lists some institutional property under names its adapter does not yet resolve, so a Boston row&#8217;s exempt value can run low; rows under half the City&#8217;s own basis are flagged. Providence&#8217;s six match the live Off the Roll page figure for figure.</li>'
             '<li>Both cities&#8217; agreements include things this table cannot price: Brown&#8217;s credits for development that returns property to the roll, Boston&#8217;s community-benefit credits, and the State of Rhode Island&#8217;s PILOT payment to Providence.</li></ul>')
    b.append('<h2>Not yet on the record</h2><ul class="open">'
             '<li>The CC-15 &#8220;39 New York Avenue (Tangible)&#8221; agreement: confirmation from the Internal Auditor of its assessment, bill and full-rate tax.</li>'
             '<li>How Boston sets each institution&#8217;s value basis, and which year&#8217;s values it uses.</li>'
             '<li>Brown University Health&#8217;s payment for 2026 (none is scheduled), Care New England&#8217;s renewal, and whether CharterCare&#8217;s hospitals, now nonprofit, have a payment agreement.</li></ul>')
    return b, dict(six=six, others=others, bos=bos, tsa=tsa, p_ask=p_ask, p_paid=p_paid, b_asked=b_asked, b_roll=b_roll, b_cash=b_cash, b_cr=b_cr)


def write_data(out, D, Z):
    (out / "data").mkdir(parents=True, exist_ok=True)
    with open(out / "data/terms_pvd_bos.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "institution", "owner_type", "exempt_value_on_roll", "commercial_rate_per_1000", "tax_at_full_rate", "quarter_of_tax",
                    "city_value_basis", "city_asked", "paid_cash", "credited", "payment_year", "city_pct_met", "roll_match_incomplete"])
        for x in D["pvd"]:
            w.writerow(["Providence", x["name"], x["type"], round(x["exempt"]), D["pr"], round(x["full"]), round(x["ask"]), "", "", round(x["paid"]), "", x["year"], "", ""])
        for x in D["bos"]:
            w.writerow(["Boston", x["name"], x["type"], round(x["exempt"]), D["br"], round(x["exempt"] * D["br"] / 1000), round(x["roll_ask"]),
                        round(x["basis"]), round(x["asked"]), round(x["cash"]), round(x["credit"]), "FY2025", x["pct"], x["partial"]])
    with open(out / "data/terms_pvd_no_agreement.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["owner", "kind", "exempt_value_on_roll", "quarter_of_tax_at_full_rate", "note"])
        for o in D["others"]: w.writerow([o["name"], o["kind"], round(o["exempt"]), round(o["ask"]), o["note"]])
    with open(out / "data/terms_tsa_fy2025.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["owner", "address", "ordinance", "assessed_2024", "tax_at_full_rate", "billed", "abated", "annual_report_filed", "status", "note"])
        for t in D["tsa"]:
            w.writerow([t["owner"], t["address"], t["ordinance"], t["assessed"] and round(t["assessed"]), t["full"] and round(t["full"]), t["billed"] and round(t["billed"]),
                        t["abated"] and round(t["abated"]), t["report"], "UNCONFIRMED" if t["unconfirmed"] else "report exhibit page", t["note"]])
    return ["terms_pvd_bos.csv", "terms_pvd_no_agreement.csv", "terms_tsa_fy2025.csv"]


def render(page, e_, SITE_, DATELINE):
    D = load()
    b, Z = body(D, DATELINE)
    out = (SITE_ / "off-the-roll/terms") if LIVE else (HERE / "drafts/off-the-roll/terms")
    files = write_data(out, D, Z)
    b.append('<h2>Data</h2><p>' + " · ".join(f'<a href="data/{f}">{f}</a>' for f in files) + '</p>'
             f'<p class="cite">Sources: City of Providence 2025 Property Tax Roll (data.providenceri.gov) and payment agreements; City of Providence Internal Auditor, Tax Stabilization Agreements report, FY2025; City of Boston FY2026 Property Assessment file and FY25 PILOT Recap; City of Boston PILOT Task Force final report, 2010. Built from Off the Roll {D["pv"].name} (Providence) and {D["bv"].name} (Boston). Data licensed CC BY 4.0: credit &#8220;Providence, on the record.&#8221;</p></main>')
    title = "Asked and Paid — Off the Roll — Providence, on the record"
    desc = "Providence's payment agreements on Boston's terms: exempt value, what was asked, what was paid, for every institution in both cities, and Providence's 66 stabilization agreements."
    if LIVE:
        (out / "index.html").write_text(page(title, desc, "../../", "".join(b), "off-the-roll/terms/"))
    else:
        css = (SITE_ / "style.css").read_text()
        banner = '<div style="background:#b3261e;color:#fff;font:700 12px/16px sans-serif;letter-spacing:.06em;padding:8px 24px">DRAFT · NOT PUBLISHED · built ' + __import__("datetime").date.today().isoformat() + ' · links to other pages will not work in this file</div>'
        html_ = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                 f'<title>{e(title)}</title><meta name="robots" content="noindex">'
                 '<link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;700&family=Roboto+Mono&family=Source+Serif+4:wght@400;600&display=swap" rel="stylesheet">'
                 f'<style>{css}</style></head><body>{banner}<div class="wrap"><header class="mast"><span class="name">Providence, on the record</span>'
                 '<div class="tag">Off the Roll · draft page</div></header>' + "".join(b) + '</div></body></html>')
        (out / "index.html").write_text(html_)
    return dict(out=out, Z=Z, D=D)


if __name__ == "__main__":
    R = render(None, e, SITE, "PROVIDENCE · DRAFT, OCT. 5, 2026")
    Z, D = R["Z"], R["D"]
    print("wrote", R["out"] / "index.html")
    print(f"rates: pvd ${D['pr']:.2f}  bos ${D['br']:.2f}")
    print(f"PVD six: ask {Z['p_ask']:,.0f}  paid {Z['p_paid']:,.0f}  share {Z['p_paid']/Z['p_ask']:.1%}")
    for x in Z["six"]: print(f"  {x['name']:26s} exempt {x['exempt']:>16,.0f} ask {x['ask']:>13,.0f} paid {x['paid']:>12,.0f} {x['paid']/x['ask']:.1%}")
    print("others over $15M:", [(o['name'][:30], round(o['exempt']/1e6,1), round(o['ask']/1e3)) for o in Z['others']])
    print(f"BOS 38: asked {Z['b_asked']:,.0f}  roll-formula {Z['b_roll']:,.0f}  cash {Z['b_cash']:,.0f}  credit {Z['b_cr']:,.0f}; partial: {[x['name'] for x in Z['bos'] if x['partial']]}")
    conf = [t for t in Z['tsa'] if not t['unconfirmed']]
    print(f"TSA 66: assessed {sum(t['assessed'] or 0 for t in conf):,.0f} full {sum(t['full'] or 0 for t in conf):,.0f} billed {sum(t['billed'] or 0 for t in conf):,.0f} abated {sum(t['abated'] or 0 for t in conf):,.0f}")
    print(f"  + CC-15: {[ (t['assessed'], t['full'], t['billed']) for t in Z['tsa'] if t['unconfirmed']]}")
