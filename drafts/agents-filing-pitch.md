# Pitch: AI agents are filing public-records requests. I'm one of them. (B482)
*Oct 15 2026. Unsent. [C] = Claude's framing. First person is Liam's; every number below is checked against his Gmail or the City's own letters, or marked as needing a check.*

## The facts it rests on
- **Volume:** since Oct 1, at least 70 email threads on records requests, counting only subjects that say APRA, FOIA, FOAA, KORA, "public records" or "records request" (Gmail, Oct 15). The true count is higher: Providence's NextRequest portal filings and requests under other subject lines aren't in it. [Check before publishing: one hand count from the sent folder.]
- **Reach:** agencies in at least 13 states, from Rhode Island, Massachusetts, Maine, South Carolina, Georgia, Kansas, Louisiana, California, Arizona, Ohio, Florida, North Carolina and Pennsylvania, plus federal agencies (Army Corps, NOAA, Bureau of Reclamation). All statute-cited, fee-capped ("estimate first if over $50"), drafted with Claude and sent on Liam's OK.
- **The cost lands on the clerk:** Providence's extension letters cited 161, then 162, open requests (Oct 13–14), per the board note on file. [Check: quote the letters.] Arizona's water department called one request "quite extensive." South Carolina's emergency management lawyer asked him on Oct 15 to narrow one ("extremely broad … weeks to process"), and he did.
- **The honest part:** his requests are in that backlog of 162.

## Pitch paragraph (for the outlet Liam picks)
> In the first two weeks of October I sent more than seventy public-records requests to agencies in thirteen states and three federal departments, each one citing the right statute, capping fees and asking for machine-readable files. I didn't type them. An AI agent drafted every one, and I approved each before it went. Providence's records office is now extending its deadlines because it has 162 open requests, and some of them are mine. Transparency laws were written for a world where filing took effort, so few people did it. That world ended this fall, quietly, and the people who have agents are already at the front of the line. The same is coming for 311: whoever has an agent gets the pothole fixed first. I want to lay out what one person with an agent can do, what it costs the clerk on the other end, and the guardrail cities need before the agents multiply: published response times by neighborhood, so the line stays visible.

## Outlet [C]
**Pick: Globe Rhode Island commentary (Maria Caporizzo).** Your desk relationship is there, the 162 is a Providence number, and the equity point is a city-hall argument. Fallback for a national frame: Nieman Lab or Columbia Journalism Review, which cover AI and reporting practice. Providence on the Record can carry the long version with the counts either way.

## Data check: what an agent-filed 311 report would look like in Providence's data [C]
Planned before any data arrives, and tied to the funnel (pvd311/funnel.md):
1. **Known positives:** Liam's own reports once B485 runs, tagged at filing. That gives a labeled set to calibrate against.
2. **Text signature:** in 26-2498's `description` field, near-duplicate phrasing across cases from one submitter, full sentences with addresses and cross-streets, a consistent template. Measure with text similarity per submitter, if the export carries a submitter key; otherwise by account-level clustering the City can run.
3. **Completeness:** agent reports fill the optional fields (location details, photo) far more often than the median report.
4. **Timing:** submissions at hours and cadences people don't keep, such as bursts, or exact intervals.
5. **Channel:** web (signed-in) only; agents can't use phone, and the guest form has a CAPTCHA.
6. **The equity measure that matters:** resolution time for those reports vs others of the same type in the same block group. If agent-filed reports close faster, the line has moved.

## Open
- Liam picks the outlet.
- Confirm the 161/162 letters and the request count by hand before any send.
