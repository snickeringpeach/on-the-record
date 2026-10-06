#!/usr/bin/env python3
"""Providence rent stabilization — exempt units, tax roll x CAMA merge.

Roll: data.providenceri.gov 2025 Property Tax Roll (levy code = the city's
      own owner-occupancy determination).
CAMA: assessor export from the Assessor's office, 2026-09-10 — ResidentialUnits
      and YearBuilt per parcel. He flagged YearBuilt as unreliable.
Join: plat-lot-unit.
"""
import csv, collections, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

ROLL = os.path.join(HERE, "2025_Property_Tax_Roll_20260910.csv")
CAMA = os.path.join(HERE, "CAMA_table(CAMA2).csv")
WINDOW = 2011          # 13-78(m): 15 years from initial occupancy


def key(plat, lot, unit):
    try:
        return "%03d-%04d-%04d" % (int(plat), int(lot), int(unit or 0))
    except (ValueError, TypeError):
        return None


cama = {}
for r in csv.DictReader(open(CAMA)):
    k = key(r["PlatNum"], r["LotNum"], r["UnitNum"])
    if k:
        cama[k] = r

rows = list(csv.DictReader(open(ROLL)))
RESIDENTIAL = ("OO01", "NO01", "OO2-5", "NOO2-5", "C610", "C11")
res = [r for r in rows if r["LEVY_CODE_1"] in RESIDENTIAL
       and r["SHORT_DESC"] != "Residential Vacant Land"]

# The roll lists a parcel once per street address, so a corner lot or a
# building with two entrances appears twice with the same P_ID. Keep the
# first row per parcel; otherwise its units are counted once per address.
_seen, _dedup = set(), []
for r in res:
    if r["P_ID"] in _seen:
        continue
    _seen.add(r["P_ID"]); _dedup.append(r)
repeat_rows = len(res) - len(_dedup)
res = _dedup


matched = miss = 0
for r in res:
    c = cama.get(r["TAX_MAP"])
    r["_units"] = r["_yb"] = None
    if c:
        matched += 1
        try:
            r["_units"] = int(c["ResidentialUnits"] or 0)
        except ValueError:
            pass
        try:
            r["_yb"] = int(c["YearBuilt"] or 0) or None
        except ValueError:
            pass
    else:
        miss += 1

print(f"residential parcels        {len(res):>7,}   (after dropping {repeat_rows:,} repeat rows — same parcel, second address)")
print(f"  matched to CAMA          {matched:>7,}  ({matched/len(res):.1%})")
print(f"  no CAMA record           {miss:>7,}\n")


def owner(r):
    co = (r["OWNER_COMPANY"] or "").strip().upper()
    if co:
        return ("ENTITY", re.sub(r"[^A-Z0-9]", "", co))
    nm = ((r["OWNER_LAST_NAME"] or "") + "|" + (r["OWNER_FIRST_NAME"] or "")).upper()
    return ("INDIV", re.sub(r"[^A-Z0-9|]", "", nm))


port = collections.Counter(owner(r) for r in res)
oo_owners = {owner(r) for r in res if r["LEVY_CODE_1"] in ("OO01", "OO2-5")}


def rentals(r):
    """Rental units in this parcel. Owner-occupied parcels house the owner
    in one of them, so that unit is not a rental."""
    u = r["_units"] or 0
    return max(u - 1, 0) if r["LEVY_CODE_1"].startswith("OO") else u


def new_construction(r):
    return r["_yb"] is not None and r["_yb"] >= WINDOW


exempt_n = exempt_2nd = exempt_m = covered = unknown = 0
oo_small = oo_big = 0

for r in res:
    if r["_units"] is None:
        unknown += rentals(r); continue
    u, lv = r["_units"], r["LEVY_CODE_1"]
    if lv.startswith("OO") and u <= 4:                 # 13-78(n) core, 1-4 as amended
        exempt_n += rentals(r); oo_small += 1
    elif (lv.startswith("NO") and u <= 4
          and owner(r)[0] == "INDIV" and port[owner(r)] <= 2
          and owner(r) in oo_owners):                  # 13-78(n) 2nd property
        exempt_2nd += rentals(r)
    elif new_construction(r):                          # 13-78(m)
        exempt_m += rentals(r)
    else:
        covered += rentals(r)
        if lv.startswith("OO"):
            oo_big += 1

tot = exempt_n + exempt_2nd + exempt_m + covered
print(f"EXEMPT 13-78(n) owner-occupied 1-4   {exempt_n:>7,}   ({oo_small:,} parcels)")
print(f"EXEMPT 13-78(n) second property      {exempt_2nd:>7,}")
print(f"EXEMPT 13-78(m) built {WINDOW}+         {exempt_m:>7,}")
print(f"COVERED                              {covered:>7,}")
print(f"  of which owner-occ 5+ unit         {oo_big:,} parcels")
print(f"unit count unknown                   {unknown:>7,}")
print(f"\nexempt share of classified rentals   "
      f"{(exempt_n+exempt_2nd+exempt_m)/tot:.1%}  covered {covered/tot:.1%}")


# ---- merged.csv: one row per residential parcel, roll joined to CAMA ----
def classify(r):
    if r["_units"] is None:
        return "no CAMA match (excluded)"
    u, lv = r["_units"], r["LEVY_CODE_1"]
    if lv.startswith("OO") and u <= 4:
        return "exempt 13-78(n) owner-occupied 1-4"
    if (lv.startswith("NO") and u <= 4
            and owner(r)[0] == "INDIV" and port[owner(r)] <= 2
            and owner(r) in oo_owners):
        return "exempt 13-78(n) second property"
    if new_construction(r):
        return "exempt 13-78(m) built %d+" % WINDOW
    return "covered"


with open(os.path.join(HERE, "merged.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["TAX_MAP", "LEVY_CODE_1", "SHORT_DESC", "OWNER_TYPE",
                "OWNER_PARCELS", "CAMA_MATCH", "ResidentialUnits", "YearBuilt",
                "RENTAL_UNITS", "CLASS"])
    for r in res:
        o = owner(r)
        w.writerow([r["TAX_MAP"], r["LEVY_CODE_1"], r["SHORT_DESC"], o[0],
                    port[o], "Y" if r["_units"] is not None else "N",
                    "" if r["_units"] is None else r["_units"],
                    r["_yb"] or "",
                    rentals(r) if r["_units"] is not None else "",
                    classify(r)])
