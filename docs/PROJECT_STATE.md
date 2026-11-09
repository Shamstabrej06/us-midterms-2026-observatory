# PROJECT STATE — US Midterms Observatory 2026

Updated after Part 7 (LinkedIn + portfolio copy), 2026-11-09.
This block is reused verbatim in the README, findings, and portfolio copy.

## Sources (retrieved 2026-11-09)

| Source | Status | Rows |
|---|---|---|
| MEDSL U.S. President 1976–2024 (state-level) | certified | 4,823 |
| MEDSL U.S. Senate statewide 1976–2024 | certified | 3,945 |
| MEDSL U.S. House 1976–2024 | BLOCKED — Dataverse guestbook gate | — |
| MEDSL County Presidential 2000–2024 / 2000–2020 | BLOCKED — Dataverse guestbook gate | — |
| FEC candidate summaries 2018 / 2022 / 2026 | 2018, 2022 certified; 2026 preliminary (coverage to 2026-10-14) | 3,687 / 4,153 / 4,370 |
| Wikipedia House pages 1994–2026 (9 cycles) | 1994–2022 certified; 2026 preliminary | — |
| Wikipedia 2026 Senate / governor pages | preliminary | — |
| Wikipedia Party divisions of US Congresses | reference table | 17 Congresses kept (103rd–119th) |
| UF Election Lab VEP turnout (v1.2 + v1.4) | final through 2022; 2026 not yet published | 1,144 / 119 |
| Census Vintage 2024 county population estimates | final | 3,195 (3,144 counties) |
| Census API (ACS income/education) | BLOCKED — key-gated ("Missing Key") | — |

## Row counts per layer

| Layer | Rows |
|---|---|
| Bronze (raw files in data/raw/) | 13,231 lines across the 5 tabular files + 14 Wikipedia HTML pages (plus 4 Texas pages + 2022 governor page added during Part 2) |
| Silver (cleaned, harmonised, data/silver/) | house_summary 18; house_seats_by_state 200; house_closest_races 163; senate_2026 3; control 17; turnout_national 9; turnout_state_2022 51; finance 12,210 (2018: 3,687, 2022: 4,153, 2026: 4,370); president_state 153; senate_state 208; governors 72; senate_flips_2026 6; texas_statewide 13; counties 3,144 |
| Gold (star schema, outputs/gold/ + outputs/midterms.db) | dim_geography 56; dim_cycle 18; dim_party 4; dim_office 5; fact_results 1,214 (HOU 418, SEN 416, PRE 306, GOV 72, ATG 2); fact_finance 12,210; fact_turnout 60; fact_texas_statewide 13; fact_senate_composition 37 (added after Part 4, src/03b — Senate seat counts per Congress, 103rd–120th; 2026: D 53 / R 45 / I 2, preliminary); fact_senate_flips_2026 6 and fact_house_closest_races 163 (promoted from silver after Part 4, src/03c, for the dashboard). Grain note: fact_results is race-STATE-cycle, not race-county-cycle (no county vote data obtainable). |
| Quarantine | **0 rows** — nothing failed validation. Audit notes: 24 negative total_receipts, 9 negative total_disbursements, 246 negative cash-on-hand (BOP), 643 negative cash-on-hand (end), 33 negative individual contributions in the FEC files — all legitimate (refunds/debt), kept in silver and counted here, not quarantined. |

## Headline metrics (computed by src/01_acquire.py — verified)

**2026 House (PRELIMINARY — 19 races uncalled, 95.6% declared):**
Democrats 254 seats won (from 214 before), Republicans 162 (from 218).
Net change: Democrats +40, Republicans −56. Popular vote: Democrats
64,014,623 (55.8%), Republicans 48,995,107 (42.7%), margin D +13.1 pts.

**2026 Senate (PRELIMINARY — page infobox gives final composition as a
range, D 52–54):** Democrats 53, Republicans 45, Independents 2.
Net change: Democrats +8, Republicans −8. 7 seats flipped Republican →
Democratic; 0 flipped the other way.

**2026 governors (PRELIMINARY — 2 of 36 races uncalled):** Democrats won
22 of 36, Republicans 12. Seats after: Democrats 28–30, Republicans
20–22 (range). Net change: Democrats +4 to +6.

**The midterm pattern (president's-party net House change):**
1994 D −54, 1998 D +5, 2002 R +8, 2006 R −30, 2010 D −64, 2014 D −13,
2018 R −42, 2022 D −9, 2026 R −56. The pattern (president's party loses
seats) held in 7 of 9 midterms; the exceptions are 1998 and 2002.
2026 confirms the pattern and is the second-largest loss in the series
after 2010.

**National House popular-vote share (Democratic %):**
1994: 44.7%, 1998: 47.3%, 2002: 45.2%, 2006: 52.3%, 2010: 44.9%,
2014: 45.5%, 2018: 53.4%, 2022: 47.29%, 2026: 55.8% (preliminary).
2026 is the highest Democratic share in the series.

**Turnout (national VEP rate, UF Election Lab):**
1994: 41.10%, 1998: 38.10%, 2002: 39.50%, 2006: 40.40%, 2010: 41.00%,
2014: 36.70%, 2018: 50.05%, 2022: 46.12%, 2026: not yet published.
Wikipedia's 2026 House infobox reports an estimated 125 million total
ballots (preliminary; no VEP denominator published, so no rate computed).

**Competitiveness (House races decided by under 10 points, from
Wikipedia closest-races tables):** 2018: 89 races; 2022: 74 races.
Under 5 points: 2018: 43; 2022: 37. 2026: not computable yet (no
closest-races table published; races still uncalled).

**Money (FEC total candidate receipts, House + Senate):**
2018: $3,125,950,077 (House $1,975,950,662; Senate $1,149,999,415;
3,570 candidates). 2022: $4,139,563,155 (House $2,230,985,665; Senate
$1,908,577,490; 4,022). 2026: $4,199,069,691 (House $2,580,734,841;
Senate $1,618,334,850; 4,249) — preliminary, coverage to 2026-10-14.
**Top-spender win rate, Senate** (method settled in Part 4: the FEC top
spender is taken among the candidates listed for that race, so a
regular and a special election in the same state-year are not
conflated, and primary losers / senators not up for re-election are
excluded; names matched on last name with suffixes and accents
normalised): 2018: 29/35 = 82.9%; 2022: 28/35 = 80.0%; 2026: 29/31 =
93.5% (31 decided races; Alaska and Mississippi uncalled). The two
2026 misses: Minnesota (Tafoya outspent Flanagan) and Montana (Bodnar
outspent Alme). An earlier party-based join gave different rates
(25/33, 22/32, 30/31) and is superseded — it counted races without a
D/R winner row inconsistently and, for 2026, included primary losers.

**Split outcomes (governor party vs House-delegation majority):**
2022: 7 states. 2026: 4 states — Georgia (D governor, R delegation),
New Hampshire (R, D), Texas (D, R), Vermont (R, D). Alaska and Kansas
excluded in 2026 (governor races uncalled); evenly split delegations
excluded in both years.

**State House seat swings 2022 → 2026 (Democratic seats, per-state
table):** California +8 (40 → 48), New York +5 (15 → 20), Iowa +3
(0 → 3), Ohio +3 (5 → 8), New Jersey / Arizona / Colorado / Michigan /
Pennsylvania / Virginia / Wisconsin +2 each, Texas +1 (13 → 14).
Only Democratic loss: Maine −1 (2 → 1). **Caveat:** the per-state
table covers 47 of 50 states — Alaska, Louisiana and North Carolina
have no 2026 seat split in the source table — so no state-level net
is reported; the 47 known states sum to 248 Democratic seats against
the national infobox total of 254. Seat changes partly reflect
mid-decade redistricting (California Prop 50, Texas redraw), not only
vote swings.

**State presidential two-party share shift 2020 → 2024 (MEDSL,
state-level):** Democratic share fell in every state; mean −2.19 pts,
median −1.91. Largest falls: New York −5.38, New Jersey −5.06,
Florida −4.92, California −4.51, Massachusetts −4.16. Smallest:
Utah −0.42.

**Texas deep-dive (two-party margins, Democratic minus Republican):**
Governor — 2014: R +20.37; 2018: R +13.30; 2022: R +10.89; 2026:
**D +7.1** (Hinojosa 52.8% beat Abbott 45.7%). Senate — 2014: R +28.35;
2018: R +2.59; 2020: R +9.90; 2024: R +8.71; 2026: **D +12.1**
(Talarico 55.1% beat Paxton 43.0%; Cornyn lost the Republican
renomination runoff to Paxton). Attorney General 2026: **D +6.5**
(Johnson 52.4% beat Middleton 45.9%, 99% reporting). President (TX
two-party) — 2016: R +9.43; 2020: R +5.66; 2024: R +13.88. Texas House
delegation: 2014 D 11 / R 25; 2018 D 13 / R 23; 2022 D 13 / R 25;
2026 D 14 / R 24. Democrats won all three Texas statewide races on
the 2026 ballot — the first break in Republicans holding every Texas
statewide office since the 1990s.

**Senate flips 2026 (6 named, 7th counted but not identified):**
Iowa (Turek beat Ernst), Kansas (Hamilton beat Marshall), Maine
(Jackson beat Collins), North Carolina (Cooper beat Tillis), South
Carolina special (Andrews beat Graham), Texas (Talarico beat Paxton).
The 7th flip is recorded in the composition table; the page does not
identify it individually (Alaska and Mississippi outcomes appear
only in the overall row).

## Dropped metrics (data cannot support them — recorded, not hidden)

1. County-level two-party vote shift 2022 → 2026 and county flips —
   no public county-level vote data (MEDSL county files guestbook-gated).
2. Texas county-level shift table — same reason.
3. Texas county map data — same reason.
4. ACS median income / education in dim_geography — Census API key-gated.
5. 2026 VEP turnout rate and state-level 2026 vs 2022 turnout — not
   yet published.
6. 2026 House competitiveness (<5 / <10 points) and the 15 closest
   races of 2026 — no district-margin source published yet.
7. Flipped 2026 House seats table (district, winner, party, margin) —
   no district-level winner-party source published yet. (Senate flips:
   kept — 7 seats, from the Senate composition table.)
8. State-level House two-party vote-share shift 2022 → 2026 — no
   state House vote totals in the obtained sources. Delivered instead
   as the state seat-swing table (computed) plus the state presidential
   two-party share shift 2020 → 2024 (computed, labelled presidential).
