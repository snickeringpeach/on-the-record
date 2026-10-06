"""build_wards.py: per-ward figures for Providence's 15 City Council wards (2022 lines).
Draft by Claude, Oct 6 2026. Writes wards.json. Nothing published until Liam says deploy.

Ward lines: City GIS Hosted/2022_PVD_Wards (ward_polys.txt, simplified ~8 m, lon=-71.xxxxx lat=41.xxxxx).
Parcel -> ward: ../rent-coverage/wards.py (City GIS Parcels_with_Ward_and_Zoning).
Inputs: 2025 tax roll (../untaxed/data/roll), rent coverage (../rent-coverage/merged_v2.csv),
RIDOT crash extract 26-373 via ../bulletin/scripts/crash_hotspots_373.py, hotspot corners (intersections.csv),
tax-sale lists (../tax-sale/data/sale_lists.csv; counts only, never names), speed cameras (../speed-cameras/data).
"""
import csv, json, sys, collections, pathlib
P = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P / "rent-coverage")); import wards as W
sys.path.insert(0, str(P / "bulletin" / "scripts")); import crash_hotspots_373 as CH

POLY = {}
for line in (P / "wards" / "ward_polys.txt").read_text().strip().splitlines():
    k, rings = line.split(":", 1)
    POLY[int(k)] = [[(-71 - int(a) / 1e5, 41 + int(b) / 1e5) for a, b in (pt.split(",") for pt in r.split())] for r in rings.split("|")]

def inside(x, y, ring):
    c = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def ward_at(lon, lat):
    for w, rings in POLY.items():
        if sum(inside(lon, lat, r) for r in rings) % 2: return w
    return None

M = lambda s: float(str(s).replace("$", "").replace(",", "") or 0)
out = {w: {"ward": w} for w in range(1, 16)}

# --- property: assessed, exempt (all regimes), fully exempt (E01) and top fully exempt owners
roll = list({r["P_ID"]: r for r in csv.DictReader(open(P / "untaxed/data/roll/2025_Property_Tax_Roll_20260910.csv", encoding="utf-8-sig", errors="replace"))}.values())  # dedup by P_ID, as Off the Roll does
own = collections.defaultdict(collections.Counter); disp = {}; miss = 0
for w in out: out[w].update(assessed=0, exempt=0, full_exempt=0, parcels=0)
for r in roll:
    w = W.ward(r["TAX_MAP"])
    if not w: miss += 1; continue
    a, e = M(r["TOTAL_ASSMT"]), M(r["TOTAL_EXEMPT"]); o = out[w]
    o["assessed"] += a; o["exempt"] += e; o["parcels"] += 1
    if r["LEVY_CODE_1"] == "E01":
        o["full_exempt"] += e
        name = (r["OWNER_COMPANY"] or f'{r["OWNER_FIRST_NAME"]} {r["OWNER_LAST_NAME"]}').strip() or "(no owner name on the roll)"
        k = " ".join(name.upper().replace(",", " ").replace(".", " ").split()); disp.setdefault(k, name)
        own[w][k] += e
for w in out: out[w]["top_exempt_owners"] = [[disp[n], round(v)] for n, v in own[w].most_common(3)]
print(f"roll: {len(roll):,} records, {miss} without a ward")

# --- rent coverage
for w in out: out[w].update(rent_covered=0, rent_exempt=0)
for r in csv.DictReader(open(P / "rent-coverage/merged_v2.csv")):
    if r["CAMA_MATCH"] != "Y": continue
    w = W.ward(r["TAX_MAP"]); u = int(float(r["RENTAL_UNITS"] or 0))
    if w: out[w]["rent_covered" if r["CLASS_V2"] == "covered" else "rent_exempt"] += u

# --- crashes 2019-2025 with a point, freeways out (same rules as the hotspot ranking)
recs, _, _ = CH.main()
for w in out: out[w].update(crashes=0, injury=0, ksi=0, ped=0, bike=0)
nopt = unw = 0
for x in recs:
    if x["y"] not in CH.FULL_YEARS or x["fwy"]: continue
    if x["la"] is None: nopt += 1; continue
    w = ward_at(x["lo"], x["la"])
    if not w: unw += 1; continue
    o = out[w]; o["crashes"] += 1; o["injury"] += x["sev"] >= 1; o["ksi"] += x["sev"] >= 3; o["ped"] += x["ped"]; o["bike"] += x["bike"]
print(f"crashes: {sum(o['crashes'] for o in out.values()):,} placed, {nopt:,} without a point, {unw} outside the ward lines")
corners = collections.defaultdict(list)
for r in csv.DictReader(open(P / "bulletin/data/crash-hotspots-373/intersections.csv")):
    try: w = ward_at(float(r["lon"]), float(r["lat"]))
    except ValueError: continue
    if w: corners[w].append((int(r["within_40m"]), r["location"], int(r["ksi"]), int(r["ped"]), int(r["bike"])))
for w in out: out[w]["top_corners"] = [list(c) for c in sorted(corners[w], reverse=True)[:3]]

# --- tax sale (counts only)
lists = collections.defaultdict(set); oo = collections.defaultdict(lambda: collections.defaultdict(set))
for r in csv.DictReader(open(P / "tax-sale/data/sale_lists.csv")):
    w = W.ward(r["key"])
    if not w: continue
    lists[r["key"]].add(r["year"])
    if r["levy"].startswith("OO"): oo[w][r["year"]].add(r["key"])
for w in out:
    keys = [k for k in lists if W.ward(k) == w]
    out[w]["tax_sale_2026"] = sum("2026" in lists[k] for k in keys)
    out[w]["tax_sale_2026_owner_occ"] = len(oo[w]["2026"])
    out[w]["tax_sale_all_three"] = sum(len(lists[k]) == 3 for k in keys)

# --- speed cameras (2022 list, placed by geocode or crash median)
for w in out: out[w]["cameras"] = []
for r in csv.DictReader(open(P / "speed-cameras/data/cameras_vs_crashes.csv")):
    w = ward_at(float(r["lon"]), float(r["lat"]))
    if w: out[w]["cameras"].append(r["school"])

json.dump(list(out.values()), open(P / "wards/wards.json", "w"), indent=1)
for o in out.values():
    print(o["ward"], f'{o["exempt"]/max(o["assessed"],1):.0%} exempt', o["rent_covered"], o["crashes"], o["ksi"], o["tax_sale_2026"], len(o["cameras"]))
