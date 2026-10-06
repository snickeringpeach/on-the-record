#!/usr/bin/env python3
"""Adds the 8 Law (levy code 8LAW) universe that coverage.py / coverage_v2.py drop. Draft by Claude, Oct 2 2026, for Liam to check.

Why: the assessor carries each 8 Law building as its own roll record (LEVY_CODE_1 = 8LAW, unit suffix 8LAW). Those plat-lots never appear in
merged_v2.csv, so v2's 37,703-unit universe leaves them out entirely. They are deed-restricted affordable housing, i.e. 13-78(i) exempt for the
restricted units, so leaving them out of the denominator raises the covered share.

Unit counts are NOT known. Two bounds:
  low  = CAMA ResidentialUnits on the 8LAW plat-lots (+1 per parcel with no CAMA match). CAMA undercounts these (median 1 per parcel).
  high = every LIHTC unit HUD lists for Providence (subsidized/lihtc-providence.csv, from HUD LIHTCPUB.ZIP, placed in service through 2024),
         which is almost all low-income units. It over-counts if some of those projects have no 8LAW record, and under-counts 8 Law
         buildings that are not LIHTC (about 34 roll records match HUD multifamily properties instead).
Needs 2025_Property_Tax_Roll_20260910.csv, CAMA_table(CAMA2).csv, subsidized/lihtc-providence.csv, output_v2.txt's counts (re-read from merged_v2.csv).
"""
import csv, collections
def I(s):
    try: return int(str(s).replace(",", "").strip())
    except: return None
def F(x):
    try: return float(x)
    except: return 0.0
# coverage.py counts residential UNITS, not parcels: reuse its published totals from output_v2.txt
COV, TOT = 26165, 37703
roll = [r for r in csv.DictReader(open("2025_Property_Tax_Roll_20260910.csv", encoding="utf-8-sig", errors="replace")) if r["LEVY_CODE_1"] == "8LAW"]
cama = collections.defaultdict(list)
for r in csv.DictReader(open("CAMA_table(CAMA2).csv", encoding="utf-8-sig", errors="replace")):
    k = (I(r["PlatNum"]), I(r["LotNum"]))
    if None not in k: cama[k].append(r)
seen, low = set(), 0.0
for r in roll:
    k = (I(r["plat"]), I(r["lot"]))
    if k in seen: continue
    seen.add(k); c = cama.get(k)
    low += max(F(x["ResidentialUnits"]) for x in c) if c else 1
high = sum(F(p["n_units"]) for p in csv.DictReader(open("subsidized/lihtc-providence.csv")))
print(f"8LAW roll records {len(roll)}, distinct plat-lots {len(seen)}")
print(f"v2 as published: covered {COV:,} of {TOT:,} = {COV/TOT:.1%}")
for name, add in (("low (CAMA floor)", low), ("high (all Providence LIHTC units)", high)):
    print(f"with 8 Law added as exempt 13-78(i), {name}: +{add:,.0f} units -> covered {COV:,} of {TOT+add:,.0f} = {COV/(TOT+add):.1%}")
