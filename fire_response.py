"""Who waits longest for the fire department. B1411b, Oct 31 2026, from ../records-co/PVD-RESPONSE.md (B1411, B1411a).
Every number is read from records-co's outputs and pinned by an assert, so a rerun upstream that moves a figure stops the
build instead of silently changing a sentence:
  data/pvd_response_rows.csv   incident rows (git-ignored in records-co; rebuilt by pvd_response.py)
  data/pvd_response_tracts.csv, pvd_response_income.csv, pvd_closure.csv, pvd_closure_detail.json
Called from build.py ONLY when RELEASE is True, or for a local look with FIRE_PREVIEW=1 python3 build.py
(./deploy wipes site/ and rebuilds without it, so a preview never ships).

HELD. RELEASE stays False until Liam says "ship it". Before that:
  - every [C] line (class="cmark" on the preview) is taken, rewritten or cut;
  - the station list (Wikipedia, not checked against the City) is checked or the caveat stays;
  - slug (/fire-response/) and its place in the home feed are his call.
render() refuses to build with RELEASE=True while any [C] mark remains.
"""
import json, pathlib, shutil

R = pathlib.Path(__file__).parent.parent / "records-co" / "data"
RELEASE = False
FILES = ["pvd_response_tracts.csv", "pvd_response_income.csv", "pvd_closure.csv", "pvd_closure_detail.json"]


def C(s):
    """Claude's framing, still waiting on Liam's read."""
    return f'<span class="cmark" style="background:var(--harbor-soft)" title="Claude&#8217;s wording, not yet Liam&#8217;s">[C] {s}</span>'


def MODEL():
    return '<span class="tag model">MODEL</span>'


def facts():
    import pandas as pd   # only the held page needs it; the normal build runs on plain python3
    X = pd.read_csv(R / "pvd_response_rows.csv")
    E = X[X.cls == "ems"]; F = X[X.cls == "fire"]
    W = E.groupby("ward").agg(n=("resp_min", "size"), median=("resp_min", "median"), mean=("resp_min", "mean"),
                              over8=("resp_min", lambda s: (s > 8).mean()), km=("station_km", "median")).reset_index()
    W["ward"] = W.ward.astype(int)
    W["km_all"] = W.ward.map(X.dropna(subset=["ward"]).groupby("ward").station_km.median().rename(int))
    T = pd.read_csv(R / "pvd_response_tracts.csv"); T = T[(T.cls == "ems") & (T.n >= 200) & T.median_income.notna()]  # as pvd_response.py
    I = pd.read_csv(R / "pvd_response_income.csv"); I = I[I.cls == "ems"]
    K = pd.read_csv(R / "pvd_closure.csv"); K = K[K.cls == "ems"].set_index(["area", "era"])
    D = json.load(open(R / "pvd_closure_detail.json"))
    return dict(n_all=len(X), n=len(E), med=E.resp_min.median(), p90=E.resp_min.quantile(.9), over8=(E.resp_min > 8).mean(),
                f_n=len(F), f_med=F.resp_min.median(), f_p90=F.resp_min.quantile(.9), W=W,
                rho_ward=W["mean"].rank().corr(W.km_all.rank()),   # mean EMS wait vs median distance of all incidents [C]
                rho_tract_km=T["median"].rank().corr(T.station_km_median.rank()),
                rho_tract_inc=T["median"].rank().corr(T.median_income.rank()), I=I, K=K, D=D,
                exact=(X.how == "exact").mean())


def render(page, e, SITE, DATELINE):
    f = facts(); W = f["W"].set_index("ward"); K = f["K"]; D = f["D"]; I = f["I"]
    P = lambda x: f"{x:.0%}"
    N = lambda x: f"{x:,}"
    ca, rc = "closed houses' area", "rest of city"
    w2a, w2b = D["ward2"]["after"], D["ward2"]["before"]
    inst_n = sum(i["n_after"] for i in D["institutions"])
    q1 = I[I.q.str.startswith("Q1")].iloc[0]; q5 = I[I.q.str.startswith("Q5")].iloc[0]

    # pin the prose to the data (PVD-RESPONSE.md, B1411 / B1411a)
    assert (f["n_all"], f["n"], f["med"], f["p90"], round(f["over8"], 3)) == (135539, 90814, 6.0, 10.0, 0.177)
    assert (f["f_n"], f["f_med"], f["f_p90"]) == (2047, 5.0, 8.0)
    assert round(f["rho_ward"], 2) == 0.80 and round(f["rho_tract_km"], 2) == 0.58 and round(f["rho_tract_inc"], 2) == 0.19
    assert (q1["median_of_tract_medians"], q5["median_of_tract_medians"]) == (6.0, 7.0)
    exp = {2: (3696, 9, "55%", 2.05), 5: (5231, 7, "25%", 0.95), 4: (6842, 6, "20%", 1.15), 3: (5930, 6, "17%", 1.60),
           10: (7818, 5, "12%", 0.40), 13: (6077, 5, "14%", 0.43)}
    for w, (n, m, o, km) in exp.items():
        r = W.loc[w]
        assert (int(r.n), int(r["median"]), P(r.over8), round(r.km, 2)) == (n, m, o, km), (w, r.to_dict())
    assert (inst_n, w2a["n"]) == (1982, 3696)
    assert (round(K.loc[(ca, "before"), "mean"], 1), round(K.loc[(ca, "after"), "mean"], 1), P(K.loc[(ca, "before"), "over8"]), P(K.loc[(ca, "after"), "over8"])) == (7.3, 7.7, "24%", "33%")
    assert (round(K.loc[(rc, "before"), "mean"], 1), round(K.loc[(rc, "after"), "mean"], 1), P(K.loc[(rc, "before"), "over8"]), P(K.loc[(rc, "after"), "over8"])) == (7.0, 6.4, "19%", "16%")
    assert (D["did_mean"], D["did_over8"], D["ci_mean"][0], P(D["inst_share_before"]), P(D["inst_share_after"])) == (0.957, 0.118, 0.73, "16%", "21%")
    assert (D["excl_inst_area_mean"]["before"], D["excl_inst_area_mean"]["after"], round(D["excl_inst_did_mean"], 1), round(D["excl_inst_did_over8"] * 100)) == (6.83, 6.79, 0.5, 6)
    assert (round(w2b["mean"], 1), round(w2a["mean"], 1), P(w2b["over8"]), P(w2a["over8"])) == (8.1, 9.3, "37%", "55%")

    b = ['<main><div class="dateline">PROVIDENCE · DRAFT, OCT. 31, 2026</div>']
    b.append('<h1>Who Waits Longest for the Fire Department</h1>')
    b.append(f'<p class="deck">A Providence ambulance or engine reaches a medical call in a median {f["med"]:.0f} minutes. In Ward 2 it takes {W.loc[2, "median"]:.0f}, and more than half the calls wait longer than eight. The wait follows how far the nearest firehouse is, not how much the neighborhood earns.</p>')
    b.append('<p class="byline">By Liam Freaney · from the Providence Fire Department&#8217;s own incident reports in the federal fire-incident data</p>')
    b.append('<div class="big">'
             f'<div><b>{f["med"]:.0f} min</b><span>median wait for a medical call, citywide</span></div>'
             f'<div><b>{P(f["over8"])}</b><span>of medical calls wait more than 8 minutes</span></div>'
             f'<div><b>{P(W.loc[2, "over8"])}</b><span>in Ward 2</span></div>'
             f'<div><b>{f["rho_ward"]:.2f}</b><span>rank correlation, ward wait and distance to a firehouse</span></div></div>')

    b.append('<h2>The record</h2>')
    b.append(f'<p>The Fire Department files a report for every incident with the National Fire Incident Reporting System. In the five years it reported in full (2019, 2021, 2022, 2023 and 2025) it filed {N(f["n_all"])} incidents with both an alarm time and an arrival time; {N(f["n"])} were medical or rescue calls. The wait here is the time from the alarm to the first unit on scene, of any kind.</p>')
    b.append(f'<p>Citywide, a medical call waits a median {f["med"]:.0f} minutes; one in ten waits {f["p90"]:.0f} or more, and {P(f["over8"])} wait more than eight. Fires: a median {f["f_med"]:.0f} minutes, one in ten {f["f_p90"]:.0f} or more ({N(f["f_n"])} fires).</p>')
    b.append(f'<p class="cite">NFIRS public data release, Providence (FDID 02800), 2019&#8211;2025; 2020 and 2024 are partial years and left out. Waits kept between 0 and 60 minutes; mutual aid given to other towns dropped. Each incident placed at its address on the 2025 tax roll ({P(f["exact"])}) or the middle of its street. Eight minutes is a reading line chosen here, not a City or national standard. (B1411)</p>')

    b.append('<h2>By ward</h2>')
    b.append('<div class="tablewrap"><table><tr><th>Ward</th><th class="n">Medical calls</th><th class="n">Median wait</th><th class="n">Over 8 min</th><th class="n">Nearest firehouse, median km</th></tr>')
    for w, r in W.sort_values(["median", "over8"], ascending=False).iterrows():
        b.append(f'<tr><td>{w}</td><td class="n">{N(int(r.n))}</td><td class="n">{r["median"]:.0f} min</td><td class="n">{P(r.over8)}</td><td class="n">{r.km:.2f}</td></tr>')
    b.append(f'<tr><td><b>City</b></td><td class="n"><b>{N(f["n"])}</b></td><td class="n"><b>{f["med"]:.0f} min</b></td><td class="n"><b>{P(f["over8"])}</b></td><td class="n"></td></tr></table></div>')
    b.append(f'<p>Across the 15 wards, the average wait and the distance to the nearest engine house rank together (rank correlation {f["rho_ward"]:.2f}; across census tracts, {f["rho_tract_km"]:.2f}). Against tract income the relation is weak and runs the other way from the usual story: the richest fifth of tracts waits a median {q5["median_of_tract_medians"]:.0f} minutes, the poorest fifth {q1["median_of_tract_medians"]:.0f} (rank correlation +{f["rho_tract_inc"]:.2f}). {MODEL()}</p>')
    b.append(f'<p>Ward 2 is slowest by a distance, and farthest from a firehouse. About {N(round(inst_n, -1))} of its {N(w2a["n"])} medical calls go to three addresses at the north end of Blackstone Boulevard, one the tax roll codes as a psychiatric facility and two as 24-hour care homes. {C("The question for the City is how the far end of Blackstone Boulevard is covered, and whether those runs are emergencies or scheduled transfers; the federal record doesn&#8217;t say.")}</p>')
    b.append('<p class="cite">Wards: 2022 council wards. Tract income: Census Bureau ACS 2020&#8211;24 5-year median household income. Engine houses: the 12 active houses listed on Wikipedia&#8217;s Providence Fire Department page (not checked against the City), placed by the Census geocoder. Institution addresses from the tax roll&#8217;s land-use codes. <a href="data/fire_response_wards.csv">fire_response_wards.csv</a>, <a href="data/pvd_response_tracts.csv">pvd_response_tracts.csv</a>, <a href="data/pvd_response_income.csv">pvd_response_income.csv</a>. (B1411)</p>')

    b.append('<h2>Before and after the 2017 closures</h2>')
    b.append(f'<p>On January 8, 2017 the City closed two East Side engine houses, 280 Rochambeau Avenue and 155 Humboldt Avenue, under the new firefighters&#8217; contract. The area those two houses were nearest to waited a mean {K.loc[(ca, "before"), "mean"]:.1f} minutes on a medical call before ({P(K.loc[(ca, "before"), "over8"])} over eight) and {K.loc[(ca, "after"), "mean"]:.1f} after ({P(K.loc[(ca, "after"), "over8"])}). The rest of the city went the other way: {K.loc[(rc, "before"), "mean"]:.1f} to {K.loc[(rc, "after"), "mean"]:.1f} minutes, {P(K.loc[(rc, "before"), "over8"])} to {P(K.loc[(rc, "after"), "over8"])}.</p>')
    b.append(f'<p>Against the rest of the city, the closed houses&#8217; area lost about a minute ({D["did_mean"]:+.2f} minutes on the mean; 95% bootstrap {D["ci_mean"][0]:.2f}&#8211;{D["ci_mean"][1]:.2f}) and {D["did_over8"] * 100:.0f} points on the share over eight minutes. {MODEL()} Ward 2 went from {w2b["mean"]:.1f} to {w2a["mean"]:.1f} minutes, and from {P(w2b["over8"])} to {P(w2a["over8"])} over eight.</p>')
    b.append(f'<p>Two things make that gap. The rest of Providence got faster and the north East Side did not. And the slowest addresses grew: the three Blackstone Boulevard institutions went from {P(D["inst_share_before"])} to {P(D["inst_share_after"])} of the area&#8217;s medical calls. Leave those three addresses out and the area is flat, {D["excl_inst_area_mean"]["before"]:.1f} minutes before and {D["excl_inst_area_mean"]["after"]:.1f} after, while the city improved: a relative loss of {D["excl_inst_did_mean"]:.1f} minutes and {D["excl_inst_did_over8"] * 100:.0f} points.</p>')
    b.append(f'<p>{C("The fair reading: since the 2017 closures, the north East Side has not shared the citywide gain in response, and the calls that wait longest, to the three institutions on Blackstone Boulevard, are the ones the closed houses were closest to. Not that the closures slowed response by a set number of minutes: the before years are thin, and changes in dispatch or reporting between the two eras can&#8217;t be separated from the closures here.")}</p>')
    b.append('<p class="cite">Before: Providence rows in the NFIRS national public release, 2014 and January&#8211;May 2015 (Providence filed nothing for 2016); after: the same months of the five full years above. The area is every incident whose nearest engine house before 2017 was Rochambeau or Humboldt. Closure date and addresses: Hey Rhody, Feb. 27, 2017. <a href="data/pvd_closure.csv">pvd_closure.csv</a>, <a href="data/pvd_closure_detail.json">pvd_closure_detail.json</a>. (B1411a)</p>')

    b.append('<h2>Not yet on the record</h2><ul class="open">'
             '<li>The City&#8217;s own dispatch (CAD) response times by station first-due area, 2015&#8211;18, which would fill the missing years and replace the distance-based area.</li>'
             '<li>Whether the Blackstone Boulevard runs are emergencies or scheduled transfers.</li>'
             '<li>The engine-house list checked against the City.</li></ul>')
    b.append('</main>')
    body = "".join(b)
    if RELEASE and "cmark" in body:
        raise SystemExit("fire_response.py: RELEASE is on but [C] marks remain")
    out = SITE / "fire-response"; (out / "data").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page("Who waits longest for the fire department — Providence, on the record",
        "Providence Fire Department medical-call response by ward, from its own federal incident reports.", "../", body, "fire-response/"))
    f["W"].round(3).to_csv(out / "data" / "fire_response_wards.csv", index=False)
    for x in FILES:
        shutil.copy(R / x, out / "data" / x)
    return dict(med=f["med"], w2=W.loc[2, "median"])
