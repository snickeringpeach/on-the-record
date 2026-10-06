#!/usr/bin/env python3
"""Coverage under the ordinance text as passed (Rent-Stabilization-Ordinance-Updated-040126.pdf), as a variant of coverage.py.
Does not change coverage.py or merged.csv; writes merged_v2.csv and prints both counts side by side. Draft by Claude, Oct 1 2026, for Liam to check.

Two changes from coverage.py:
 1. 13-78(m) new construction: 10 years from certificate of occupancy, and only units whose CO is on/after the effective date or
    not more than five years before it. With an effective date in 2027, that reaches COs from 2022 on. Proxy: CAMA YearBuilt >= 2022.
    (coverage.py used 15 years, YearBuilt >= 2011, the introduced text.)
 2. 13-78(j) project-based subsidized housing: parcels matched by address to HUD's Multifamily Assistance & Section 8 database
    (properties whose category says Subsidized). 13-78(i) deed-restricted LIHTC/LMIH units are NOT yet modeled beyond what the
    8LAW levy code already removes from the residential count.
"""
import csv, re, os, openpyxl, collections
HERE = os.path.dirname(os.path.abspath(__file__))
SUF = {"STREET": "ST", "AVENUE": "AVE", "ROAD": "RD", "PLACE": "PL", "COURT": "CT", "BOULEVARD": "BLVD", "DRIVE": "DR", "LANE": "LN",
       "TERRACE": "TER", "PLAZA": "PLZ", "SQUARE": "SQ", "PARKWAY": "PKWY", "HIGHWAY": "HWY"}
def akey(a):
    a = re.sub(r"[^A-Z0-9 \-]", " ", (a or "").upper()); a = re.sub(r"\s+", " ", a).strip()
    m = re.match(r"^(\d+)[A-Z]?(?:\s*-\s*(\d+))?\s+(.*)$", a)
    if not m: return []
    toks = [SUF.get(t, t) for t in m.group(3).split()]
    toks = [t for t in toks if t not in ("UNIT", "APT", "BLDG")]
    st = " ".join(toks[:-1] if toks and toks[-1] in SUF.values() else toks)
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    return [(n, st) for n in range(lo, min(hi, lo + 40) + 1)]

wb = openpyxl.load_workbook(os.path.join(HERE, "subsidized/hud-mf-properties.xlsx"), read_only=True); ws = wb.active
it = ws.iter_rows(values_only=True); h = next(it); ix = {k: i for i, k in enumerate(h)}
hud = [r for r in it if str(r[ix["state_code"]]).strip() == "RI" and str(r[ix["city_name_text"]]).strip().upper() == "PROVIDENCE"
       and "SUBSIDIZED" in str(r[ix["property_category_name"]]).upper()]
hudkeys = {}
for r in hud:
    for k in akey(r[ix["address_line1_text"]]): hudkeys[k] = (str(r[ix["property_name_text"]]).strip(), r[ix["property_total_unit_count"]])

addr = {}
for r in csv.DictReader(open(os.path.join(HERE, "2025_Property_Tax_Roll_20260910.csv"), encoding="utf-8-sig", errors="replace")):
    addr.setdefault(r["TAX_MAP"], []).append(r["FORMATED_ADDRESS"])

rows = list(csv.DictReader(open(os.path.join(HERE, "merged.csv"))))
matched = {}; out = []
for r in rows:
    c = r["CLASS"]; yb = int(r["YearBuilt"]) if (r["YearBuilt"] or "").isdigit() else None
    if c == "exempt 13-78(m) built 2011+": c = "covered"
    if c == "covered" and yb and yb >= 2022: c = "exempt 13-78(m) built 2022+"
    if c == "covered":
        hit = next((hudkeys[k] for a in addr.get(r["TAX_MAP"], []) for k in akey(a) if k in hudkeys), None)
        if hit: c = "exempt 13-78(j) HUD project-based"; matched[r["TAX_MAP"]] = hit
    r = dict(r, CLASS_V2=c); out.append(r)

with open(os.path.join(HERE, "merged_v2.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
def tally(key):
    t = collections.Counter()
    for r in out:
        if r[key].startswith("no CAMA"): continue
        t[r[key]] += int(r["RENTAL_UNITS"] or 0)
    return t
a, b = tally("CLASS"), tally("CLASS_V2")
for name, t in (("coverage.py (published)", a), ("coverage_v2.py (text as passed)", b)):
    cov = t["covered"]; tot = sum(t.values()); print(f"{name}: covered {cov:,} of {tot:,} = {cov/tot:.1%}")
    for k, v in sorted(t.items()): print(f"   {k:40s} {v:7,}")
print(f"HUD subsidized properties in Providence: {len(hud)}; matched to roll parcels: {len(set(matched.values()))}; parcels: {len(matched)}")
missing = sorted({str(r[ix['property_name_text']]).strip() + ' | ' + str(r[ix['address_line1_text']]).strip() for r in hud} - {f"{n} | " for n, _ in matched.values()})
open(os.path.join(HERE, "subsidized/hud-matches.txt"), "w").write("\n".join(f"{k} -> {v[0]} ({v[1]} units)" for k, v in sorted(matched.items())))
