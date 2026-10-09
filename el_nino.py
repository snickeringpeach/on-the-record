"""El Niño 2026–27 and Rhode Island: the series page. B193, Oct 9 2026.
Rendered from ../el-nino (PLAN.md for the brief and piece list; figs/ for the four figures, their CSVs and README).
Called from build.py: el_nino.render(page, e, SITE, DATELINE). Not published until Liam says deploy.
Left out on purpose: all draft text (../el-nino/drafts are drafts; pieces are listed by title as "coming"),
PLAN.md's [C] readings and run order, and every number not printed in a figure.
Captions and source lines are figs/README.md's "Shows" and "Sources" columns, verbatim; figure 3 carries
the GSO data-use credit line. Only the derived CSVs are copied, never the raw trawl file."""
import pathlib, shutil

F = pathlib.Path(__file__).parent.parent / "el-nino" / "figs"

FIGS = [
    ("1_providence_winters", "Nov–Mar precipitation, season snowfall, Dec–Feb mean temperature, 1950–51 to 2025–26, by class",
     "NOAA CPC RONI; ACIS &#8220;Providence Area&#8221; via NRCC"),
    ("2_river_peaks", "Annual peak flow, Pawtuxet (Cranston), Woonasquatucket (Centerdale), Moshassuck (Providence), El Niño winters colored",
     "USGS peak streamflow 01116500, 01114500, 01114000; RONI"),
    ("3_flounder_vs_temperature", "Fox Island winter flounder per tow, and Jan–Mar bottom temperature, 1959–2024 (no survey 1967–77)",
     "URI Graduate School of Oceanography and RI DEM, Narragansett Bay Fish Trawl Survey"),
    ("4_heating_oil_vs_hdd", "RI heating oil, Oct–Mar average by season, El Niño seasons marked, with the Oct 5 2026 weekly price",
     "EIA weekly RI No. 2 heating oil residential price; RONI. The CSV also carries Nov–Mar HDD"),
]

PIECES = ["What&#8217;s coming", "Rivers, basements and who pays", "Homes and budgets", "Health",
          "On land: plants and animals", "In the bay", "Do they sense it?"]

def render(page, e, SITE, DATELINE):
    out = SITE / "el-nino"; (out / "figs").mkdir(parents=True, exist_ok=True)
    for f, _, _ in FIGS:
        for ext in (".png", ".csv"):
            shutil.copy(F / (f + ext), out / "figs" / (f + ext))
    b = ['<main><div class="dateline">PROVIDENCE · OCT. 9, 2026</div>',
         '<h1>El Niño 2026–27 and Rhode Island</h1>',
         '<p class="deck">A series on El Niño and its effects in Rhode Island, for people and for plants, animals and marine life.</p>',
         '<p>NOAA&#8217;s own page for Rhode Island: &#8220;Although El Niño may have an impact on Rhode Island, historically there has not been a consistent response.&#8221;</p>',
         '<p>Winters here are classed by December–February RONI, the Relative ONI, NOAA&#8217;s index since February 2026: strong at +1.5 or more, El Niño at +0.5 or more, La Niña at &#8722;0.5 or less.</p>',
         '<h2>The record</h2>']
    for i, (f, shows, src) in enumerate(FIGS, 1):
        b.append(f'<figure style="margin:24px 0"><img src="figs/{f}.png" alt="Figure {i}: {shows}" style="max-width:100%;height:auto;display:block" loading="lazy">'
                 f'<figcaption>{shows}</figcaption>'
                 f'<p class="cite">Source: {src}. Data: <a href="figs/{f}.csv">{f}.csv</a></p></figure>')
    b.append('<h2>The series</h2><div class="tablewrap"><table><tr><th></th><th>Piece</th><th>Status</th></tr>')
    for i, t in enumerate(PIECES, 1):
        b.append(f'<tr><td>{i}</td><td>{t}</td><td>Coming</td></tr>')
    b.append('</table></div></main>')
    (out / "index.html").write_text(page("El Niño — Providence, on the record",
        "El Niño 2026–27 and Rhode Island: four figures from the public record, and the series to come.", "../", "".join(b), "el-nino/"))
    return {"n_figs": len(FIGS), "n_pieces": len(PIECES)}
