"""wards.py: Providence parcel -> City Council ward (2022 boundaries).

Source: City of Providence GIS, Hosted/Parcels_with_Ward_and_Zoning FeatureServer layer 0
(fields propid, districtn; 44,283 parcels; pulled Oct 6 2026 through a browser because the shell
can't reach webgis.providenceri.gov). Stored run-length encoded in ward_runs.txt: parcels sorted by
propid with dashes removed, each run "first:last=ward" (or "id=ward"), ';'-separated.
A TAX_MAP inside a run gets that run's ward. One outside every run falls back to its plat-lot
(unit 0000) and is otherwise left unassigned. Draft by Claude, Oct 6 2026.
"""
import bisect, pathlib
HERE = pathlib.Path(__file__).parent
_S, _E, _W = [], [], []
for tok in (HERE / "ward_runs.txt").read_text().strip().split(";"):
    k, w = tok.rsplit("=", 1)
    s, e = (k.split(":") + [k])[:2]
    _S.append(s); _E.append(e); _W.append(None if w in ("null", "x") else int(w))

def _look(key):
    i = bisect.bisect_right(_S, key) - 1
    return _W[i] if i >= 0 and _S[i] <= key <= _E[i] else None

def ward(tax_map):
    key = tax_map.replace("-", "")
    w = _look(key)
    if w is None and len(key) == 11: w = _look(key[:7] + "0000")
    return w

if __name__ == "__main__":
    import csv, collections
    rows = [r for r in csv.DictReader(open(HERE / "merged_v2.csv")) if r["CAMA_MATCH"] == "Y"]
    u = lambda r: int(float(r["RENTAL_UNITS"] or 0))
    t = collections.defaultdict(lambda: [0, 0]); miss = 0
    for r in rows:
        w = ward(r["TAX_MAP"]); k = 0 if r["CLASS_V2"] == "covered" else 1
        if w is None: miss += u(r); continue
        t[w][k] += u(r)
    for w in sorted(t):
        c, x = t[w]; print(f"ward {w:2}: covered {c:6,} exempt {x:6,} share {c/(c+x):.1%}")
    tc = sum(v[0] for v in t.values()); tx = sum(v[1] for v in t.values())
    print(f"assigned {tc+tx:,} rental units; unassigned {miss:,}")
