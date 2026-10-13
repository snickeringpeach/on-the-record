"""Address lookup for the rent stabilization page (B16, Oct 13 2026, Claude for Liam).
Writes site/rent-stabilization/lookup/index.html + lookup.json from ../rent-coverage
(merged_v2.csv, the 2025 roll). Same rules as ../rent-coverage/lookup.py. No owner names.
Called from rent.render(). Not published until Liam says deploy.
"""
import csv, json, pathlib

RC = pathlib.Path(__file__).parent.parent / "rent-coverage"

CODES = {  # CLASS_V2 -> short code shown by the page
    "covered": "C",
    "exempt 13-78(n) owner-occupied 1-4": "OO",
    "exempt 13-78(n) second property": "SP",
    "exempt 13-78(m) built 2022+": "NC",
    "exempt 13-78(j) HUD project-based": "HUD",
    "no CAMA match (excluded)": "NM",
}


def build(src_roll):
    cov = {r["TAX_MAP"]: r for r in csv.DictReader(open(RC / "merged_v2.csv", newline=""))}
    rows, seen = [], set()
    for r in csv.DictReader(open(src_roll, newline="", encoding="utf-8-sig", errors="replace")):
        a = (r.get("FORMATED_ADDRESS") or "").strip()
        tm, levy = r["TAX_MAP"], r.get("LEVY_CODE_1", "")
        if not a or (a, tm) in seen:
            continue
        seen.add((a, tm))
        c = cov.get(tm)
        if c:
            code = CODES.get(c["CLASS_V2"], "NM")
            u, y, d = c["ResidentialUnits"], c["YearBuilt"], c["SHORT_DESC"]
        else:
            code = "8L" if levy == "8LAW" else "X"
            u = y = d = ""
        rows.append([a, tm, code, u, y, levy, d])
    rows.sort()
    return rows


BODY = """<main><div class="dateline">{dateline}</div>
<h1>Is My Building Covered?</h1>
<p class="deck">Type a Providence street address. The answer applies the rent stabilization ordinance&#8217;s final text to the City&#8217;s own records for that parcel &#8212; the same count behind the finding that the ordinance reaches roughly 60 to 65 percent of the city&#8217;s rental homes.</p>
<form class="lk" onsubmit="return false"><input id="q" type="search" autocomplete="off" placeholder="e.g. 120 Broad St" aria-label="Street address"></form>
<div id="out" aria-live="polite"><p class="cite">Loading the City&#8217;s records&#8230;</p></div>
<h2>What the answer rests on</h2>
<ul>
<li>The 2025 property tax roll (City open data, dataset 6ub4-iebe) for the address and the City&#8217;s owner-occupancy code; the Assessor&#8217;s parcel database for unit count and year built; HUD&#8217;s Multifamily database for federal project-based subsidy.</li>
<li>Owner-occupied buildings of 1 to 4 units are exempt (13-78(n)); so is a small landlord&#8217;s second building of 1 to 4 units, matched on owner name, so that test is approximate.</li>
<li>New construction: buildings the Assessor dates 2022 or later are treated as exempt (13-78(m)), assuming a 2027 effective date. Year built is the database&#8217;s weakest field.</li>
<li>Not screened: condominiums the parcel database doesn&#8217;t match, apartments in commercial or mixed-use buildings, and state-subsidized buildings other than 8 Law.</li>
</ul>
<p class="cite">This is an estimate for a first look, not a legal determination; the ordinance&#8217;s text and the City decide. <a href="../">The full count</a> &#183; <a href="lookup.json">the data behind this page (JSON)</a>.</p>
</main>
<style>
.lk input{{width:100%;font:inherit;font-size:1.1rem;padding:.6rem .7rem;border:1px solid currentColor;border-radius:4px;background:transparent;color:inherit;box-sizing:border-box}}
.hit{{border-top:1px solid rgba(127,127,127,.35);padding:.7rem 0}}
.hit b.v{{display:inline-block;margin:.15rem 0 .25rem;font-size:1.05rem}}
.hit .why{{font-size:.92rem;opacity:.85}}
</style>
<script>
(function(){{
var V={{
 C:["Covered","The ordinance&#8217;s rent limits would apply to the rented units in this building."],
 OO:["Exempt: owner lives here, 1 to 4 units","13-78(n). The City codes this parcel owner-occupied."],
 SP:["Exempt: small landlord&#8217;s second building","13-78(n). Owner holds no more than two parcels and lives in one (matched by name)."],
 NC:["Exempt: new construction","13-78(m). The Assessor dates the building 2022 or later."],
 HUD:["Exempt: federal project-based subsidy","13-78(j). Matched to HUD&#8217;s Multifamily database."],
 "8L":["Exempt: deed-restricted affordable (8 Law)","13-78(i). Taxed under the state&#8217;s affordable-housing rule."],
 NM:["Not screened","A residential parcel the Assessor&#8217;s database doesn&#8217;t match, usually a condominium unit. Check the unit count and the ordinance text directly."],
 X:["Not counted here","The City taxes this parcel as commercial, exempt or vacant. Apartments in a mixed-use building aren&#8217;t screened."]
}};
function norm(a){{a=(a||"").toUpperCase().replace(/[^0-9A-Z ]/g," ");
 a=a.replace(/\\bSTREET\\b/g,"ST").replace(/\\bAVENUE\\b/g,"AVE").replace(/\\bROAD\\b/g,"RD").replace(/\\bPLACE\\b/g,"PL").replace(/\\bBOULEVARD\\b/g,"BLVD").replace(/\\bDRIVE\\b/g,"DR");
 return a.replace(/\\s+/g," ").trim();}}
var D=null,N=null,q=document.getElementById("q"),out=document.getElementById("out");
function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]}})}}
function show(){{
 if(!D)return; var n=norm(q.value);
 if(n.length<3){{out.innerHTML='<p class="cite">Start with the house number.</p>';return;}}
 var h=[];for(var i=0;i<D.length&&h.length<12;i++)if(N[i].indexOf(n)===0)h.push(D[i]);
 if(!h.length){{out.innerHTML='<p>No match on the 2025 roll. Try the house number and street only, without the unit or apartment number.</p>';return;}}
 out.innerHTML=h.map(function(r){{var v=V[r[2]]||V.X;var f=[];
  if(r[6])f.push(esc(r[6]));if(r[3])f.push(esc(r[3])+" unit"+(r[3]=="1"?"":"s")+" on the Assessor&#8217;s record");
  if(r[4]&&r[4]!="0")f.push("built "+esc(r[4]));if(r[5])f.push("levy code "+esc(r[5]));
  return '<div class="hit"><div>'+esc(r[0])+' <span class="cite">plat-lot '+esc(r[1])+'</span></div><b class="v">'+v[0]+'</b><div class="why">'+v[1]+(f.length?' '+f.join(" &#183; ")+'.':'')+'</div></div>';}}).join("")+(h.length==12?'<p class="cite">More matches; add the house number.</p>':'');
}}
fetch("lookup.json").then(function(r){{return r.json()}}).then(function(d){{D=d;N=d.map(function(r){{return norm(r[0])}});
 out.innerHTML='<p class="cite">'+d.length.toLocaleString()+' Providence addresses loaded.</p>';q.focus();if(q.value)show();}})
 .catch(function(){{out.innerHTML='<p>The records didn&#8217;t load. Reload the page.</p>'}});
q.addEventListener("input",show);
}})();
</script>"""


def render(page, SITE, DATELINE, src_roll):
    rows = build(src_roll)
    out = SITE / "rent-stabilization" / "lookup"
    out.mkdir(parents=True, exist_ok=True)
    (out / "lookup.json").write_text(json.dumps(rows, separators=(",", ":")))
    (out / "index.html").write_text(page("Is my building covered? Rent stabilization lookup — Providence, on the record",
        "Type a Providence address: does the rent stabilization ordinance's final text reach it, from the City's own records.",
        "../../", BODY.format(dateline=DATELINE), "rent-stabilization/lookup/"))
    return len(rows)
