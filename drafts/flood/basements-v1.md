# Providence's three basement floods (B951, draft for Liam)

*Oct 20 2026, bench session. Page held: nothing built or deployed. Data and method: ~/Projects/datasets/derived/openfema/providence_floods/ (b951.py; pvd_bg.csv is the block-group table, pvd_summary.json the numbers below). **[C]** marks Claude's framing. Blanks in brackets are yours. Meant as a section of the flood page (flood-page-v1.md) or its own note.*

---

**[C] Working head:** Up the Hill, Down the Drain

## What happened

Between September 2023 and January 2024, three storms brought federal disaster declarations to Rhode Island: DR-4753 (September 2023), DR-4765 (December 2023) and DR-4766 (January 2024). In the city of Providence, 578 households registered with FEMA across the three. FEMA recorded flood damage at 143 of them.

| Storm | Registered | With flood damage | Water in basement or crawlspace | With flood insurance | FEMA-assessed damage | FEMA aid paid |
|---|---|---|---|---|---|---|
| Sep 2023 (DR-4753) | 163 | 34 | 64% | 0% | $97,347 | $174,924 |
| Dec 2023 (DR-4765) | 134 | 35 | 91% | 3% | $113,315 | $261,501 |
| Jan 2024 (DR-4766) | 281 | 74 | 92% | 3% | $196,725 | $658,817 |
| All three | 578 | 143 | 85% | 2% | $407,386 | $1,095,242 |

Source: OpenFEMA, Individuals and Households Program valid registrations (v2), Providence County, filtered to the city's census tracts. Basement share is among flood-damaged registrants with a recorded high-water location. [link]

Three of every 100 flooded households had flood insurance.

## Where

FEMA's public file gives each registration's census block group. 61 of the city's 153 block groups had at least one flood-damaged registrant. Eighteen had them in two or three of the storms, and those eighteen account for 81 of the 143, more than half.

| Neighborhood | Flood-damaged registrants | Per 1,000 households | Block groups hit in 2+ storms |
|---|---|---|---|
| Wanskuck | 22 | 4.5 | 2 |
| Elmhurst | 21 | 6.3 | 3 |
| Charles | 18 | 6.5 | 2 |
| Mount Pleasant | 14 | 3.2 | 1 |
| Silver Lake | 13 | 3.0 | 3 |
| Washington Park | 8 | 4.1 | 2 |
| Blackstone | 8 | 2.7 | 1 |
| Elmwood | 8 | 1.8 | 1 |
| Olneyville | 7 | 2.5 | 1 |

Households: Census Bureau, ACS 5-year table B25003, by block group. Neighborhood is where the block group's center point falls. [link]

Wanskuck's count is mostly one storm and one kind of damage: in September 2023, 12 renter households in one block group reported water on the first floor, not the basement. **[C]** That looks like one building or one street, and it's a different story from the rest.

## Not by the water

The flooded basements were not on low ground. Block groups whose center sits 100 feet or more above sea level had 3.2 flood-damaged registrants per 1,000 households; those under 20 feet had 0.2.

| Ground at the block group's center | Block groups | Households | Flood-damaged | Per 1,000 households |
|---|---|---|---|---|
| under 20 ft | 8 | 4,413 | 1 | 0.2 |
| 20–50 ft | 16 | 8,921 | 18 | 2.0 |
| 50–100 ft | 91 | 40,757 | 69 | 1.7 |
| 100 ft and up | 38 | 17,406 | 55 | 3.2 |

Elevation: USGS 3DEP, one point per block group (the Census Bureau's internal point), feet above NAVD88. A single point is a rough label for a block group, not its average.

**[C]** Water in a basement on a hill didn't come from a river. It came up through the floor drain or in through the foundation: the sewer backing up, or groundwater. Which one is the question the city's records can answer.

## The sewer question (open)

Most of Providence is on a combined sewer: storm runoff and sewage share one pipe, run by the Narragansett Bay Commission. When the pipe is full, it overflows to the rivers at 61 permitted outfalls (EPA Region 1 outfall map, 2022), or backs up into basements.

The flooded block groups are not clustered at the outfalls. The rate is lowest within half a kilometer of one (1.2 per 1,000 households) and roughly double farther away (2.0–2.5). **[C]** That fits backup in the upper reaches of the system, where the pipes fill but there is no outlet, though distance to an outfall is only a stand-in for where the combined system runs.

What would settle it is a map of which streets are combined and which are separated. NBC has one; no public copy turned up. [Ask NBC for its combined/separated sewer service-area map, or add it to the Oct 7 APRA.]

## What this doesn't show

- **Renters are undercounted.** Renters are 59% of Providence households but 13% of the flood-damaged registrants. FEMA records damage to the building for owners; renters' losses are mostly personal property and are often not inspected for flood. **[C]** The renter number here is a floor.
- **Registrants are not everyone.** These are households that applied to FEMA. Many with a wet basement didn't.
- Some outfalls on the 2022 map may have been closed since; the layer doesn't say which.
- FEMA's "PROVIDENCE" mailing city includes 135 registrants in North Providence and Johnston tracts. They're left out here.

[Your lead, your read on the hills, and whether this belongs on the flood page or with the sewer page.]
