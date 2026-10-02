# on-the-record

providenceontherecord.org. Static site; push = deploy (Vercel serves `site/` from snickeringpeach/on-the-record).
Read first: `SLATE.md` (what runs, what's coming, what each project is missing). Common rules: ~/Projects/START.md.

## Commands
- `./sync "msg"`: `python3 build.py`, commit, push (as snickeringpeach, then back to lfreaney).
- `python3 housing.py`, `python3 compare.py`: the Housing page and Off the Roll's Providence–Boston page.

## Rules
- Every number on the site traces to a public record named where it's used. Models are labeled MODEL.
- Off the Roll reads products from ../records; the build stops if ../untaxed disagrees.
- Corrections go at the top of the page they correct, dated.
- `data/coming-up.json` is refreshed every Monday (dates: C = a source states it, L = likely).
- Pieces for the Substack live in ../civic-writing, not here.
