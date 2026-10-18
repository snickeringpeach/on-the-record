# Who pays for the next flood (B693, draft for Liam)

*Oct 18 2026, bench session. Rules held: first person, no personas, every number traced to a public record named where it's used, models labeled MODEL. **[C]** marks Claude's framing or wording where the argument isn't yet yours. Blanks in brackets are yours. Nothing is built or deployed. The data lives in ~/Projects/datasets/derived/openfema/kent_2010/ (README sections B638, B667, B688–B692), which has no public home yet; a page would need its CSVs copied to site/flood/data/ the way /housing/ carries its own.*

*Hold point: RIEMA's answer to the repetitive-loss APRA (sent Oct 18; due about Nov 2) would settle whether the 2023–24 claims hit the same buildings as 2010. The page can go up before it, with that question stated as open.*

---

**[C] Working title:** Who Pays for the Next Flood

**[C] Deck:** In 2010, Rhode Island rebuilt from the March floods more on loans than on flood insurance. Since then, the places that flooded have dropped a third of their flood policies.

## 1. What 2010 cost, and who paid

In March and April 2010, rivers in Kent and Providence counties flooded thousands of homes. The federal disaster declaration was DR-1894. Here is who paid for the rebuilding, by program:

| | Paid |
|---|---|
| FEMA aid to households (IHP) | $37.1M |
| FEMA aid to towns and the state (Public Assistance) | $26.0M |
| Flood insurance (NFIP), 1,747 claims | $43.5M |
| SBA disaster loans, homes and businesses | $46.8M |

Sources: OpenFEMA Individual and Households Program and Public Assistance summaries; OpenFEMA NFIP redacted claims, losses dated March 12 to April 12, 2010; SBA disaster loan data, FY2010 workbook, FEMA 1894 rows. [links]

The largest single source was loans. People borrowed more to rebuild than flood insurance paid out. In Kent County, homeowners and businesses borrowed $18.1M against $14.7M from flood insurance. In Warwick, half the 2010 recovery money was debt. In Coventry, three quarters.

Since then, FEMA has obligated $1.05M in hazard mitigation in the Kent County towns. It went to four buildings. [link: OpenFEMA HMA subapplications]

**[C]** The buildings that flooded in 2010 were mostly rebuilt where they stood, on borrowed money.

## 2. It happened again, in the same places

In December 2023 and January 2024, two more federal declarations followed (DR-4765, DR-4766). They were smaller: 205 flood insurance claims, against 1,747 in 2010. They landed in the same towns: Warwick, West Warwick, Cranston, Johnston.

They landed in the same neighborhoods too. The public claims file has no addresses, but it does give each claim's census block group. In the Kent towns, 77 of the 85 claims in 2023–24 were in block groups that also claimed in 2010. Every one was in a census tract that claimed in 2010. [link: NFIP redacted claims]

Whether they are the same buildings is a question only the state can answer. RIEMA keeps the list of properties that flood again and again. I asked for it on Oct 18. [Update with the answer.]

## 3. Fewer of them are insured now

In 2010, Rhode Island had 16,217 flood insurance policies. In 2024 it had 11,791, down 27%. In the areas that flooded in 2010 the drop is about 30%. Warwick lost 47% of its policies, Cranston 50%. [link: OpenFEMA NFIP redacted policies, by effective year]

Premiums alone don't explain it. Policies kept falling after 2018 even where the typical premium went down. **[C]** The public file can't say why people dropped coverage: whether a mortgage was paid off, the bill went up, or something else. It shows when.

It shows up in the 2023–24 storms. This time FEMA grants to households ($19.4M) were nearly double what flood insurance paid ($10.2M). In 2010 it was the other way around.

## 4. The next one — MODEL

**MODEL.** Here is the 2010 flood again, on today's insurance. Assumptions:
- The same homes flood.
- The share still insured follows each tract's drop in policies.
- Each newly uninsured home loses what NFIP paid per claim in that area in 2010, in 2025 dollars. That undercounts damage.
- FEMA gives each household the 2010 average, $3,719 in today's dollars.

| | Damaged homes | No longer insured | Their loss (at least) | FEMA grants | Left to the household |
|---|---|---|---|---|---|
| Rhode Island | 1,760 | about 660 | $26.8M | $2.5M | $24.4M |
| Kent County towns | 485 | about 210 | $8.1M | $0.8M | $7.3M |
| Cranston | 226 | about 136 | $10.2M | $0.5M | $9.7M |

**[C]** Most of what a repeat of 2010 would cost these households would land on them, not on insurance or FEMA: about nine dollars in ten. They would cover it with an SBA loan if they qualify, and out of pocket if they don't. This leaves out homes that weren't insured in 2010 either, so the real figure is higher.

## 5. What would change it

[Yours. The data points at three things without choosing among them: (a) mitigation of the specific buildings that flood again and again, which needs RIEMA's list; (b) insurance take-up in the 2010 tracts; (c) the cost of the loans, which SBA's files show only through FY2022.]

---

## Sources, in order
- OpenFEMA: Disaster Declarations Summaries; Housing Assistance Owners and Renters (IHP); Public Assistance Funded Projects Summaries; Hazard Mitigation Assistance Subapplications v2; NFIP redacted claims; NFIP redacted policies (v3). Pulled Oct 18 2026.
- SBA Disaster Loan Data, FY2000–FY2022 workbooks (data.sba.gov).
- BLS CPI-U, annual averages (2025 dollars).
- APRA to RIEMA, Oct 18 2026 (repetitive-loss and severe repetitive-loss properties; pending).

## Before it goes up
- Every bracket filled; section 5 is yours.
- The CSVs it cites copied into site/flood/data/ and linked.
- [C] wording either taken, rewritten, or cut.
- Decide the slug (/flood/?) and where it sits in the feed.
