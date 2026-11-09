# Data dictionary

Gold layer: `outputs/gold/*.csv` and `outputs/midterms.db` (SQLite, same
tables). Built by `src/03_build_gold.py` from `data/silver/`.

## Grain note

`fact_results` is specified in the brief at race-county-cycle grain. No
public county-level vote data could be obtained (the MEDSL county files
are guestbook-gated; see `data/SOURCES.md`), so `fact_results` is built
at **race-state-cycle grain** (with national rows for the House popular
vote). The grain is explicit in every row via `geography_level`. County
population still appears in `dim_geography`; county-level vote shift
and county flips are dropped metrics (see `docs/PROJECT_STATE.md`).

## dim_geography — 56 rows

One row per state, DC, and territory.

| Column | Type | Meaning | Source |
|---|---|---|---|
| state_fips | int | State FIPS code (1–56; territories 60–78) | Census popest (county FIPS ÷ 1000); territories fixed |
| state_abbr | text | USPS abbreviation | Census / FEC |
| state_name | text | State name | Census popest |
| region | text | Census region (Northeast/Midwest/South/West) or "Territory" | Census popest SUMLEV 40 rows |
| division | text | Census division, or "Territory" | Census popest SUMLEV 40 rows |
| population_2024 | int | Vintage 2024 county population estimate, summed to the state; null for territories (not in the Census file) | Census popest |

## dim_cycle — 18 rows

One row per election cycle, 1992–2026. The majorities are the composition
of the Congress seated by that election.

| Column | Type | Meaning | Source |
|---|---|---|---|
| cycle | int | Election year | Control table / results |
| congress | int | Congress seated (e.g. 120th for 2026) | Control table |
| election_type | text | midterm / presidential | Derived (year % 4 == 2 → midterm) |
| president | text | President in office at the election | Control table |
| president_party | text | President's party | Control table |
| senate_majority | text | Party holding the Senate after the election | Control table; 2006 corrected to Democratic (49 D + 2 independents caucusing with Democrats = 51); 2000 is "Even" (50–50, decided by the Vice President's tie-breaking vote) |
| house_majority | text | Party holding the House after the election | Control table / results tables |
| trifecta | bool | True when the president's party also holds both chambers | Computed |

## dim_party — 4 rows

| party_key | party_name |
|---|---|
| DEM | Democratic |
| REP | Republican |
| OTH | Other |
| IND | Independent |

## dim_office — 5 rows

| office_key | office_name | chamber | seats_total |
|---|---|---|---|
| HOU | House | House | 435 |
| SEN | Senate | Senate | 100 |
| PRE | President | Executive | 1 |
| GOV | Governor | State executive | 50 |
| ATG | Attorney General | State executive | 50 |

## fact_results — 1,214 rows

One row per race-geography-party. A race with two parties has two rows
(Democratic and Republican) sharing a `race_id`.

| Column | Type | Meaning | Source |
|---|---|---|---|
| race_id | text | Race key: `{OFFICE}-{STATE}-{CYCLE}` (e.g. `HOU-TX-2026`, `SEN-TX-2026-SP` for specials, `HOU-NAT-2026` for the national House popular vote) | Built |
| cycle | int | Election year | All sources |
| office_key | text | HOU / SEN / PRE / GOV / ATG → dim_office | Built |
| geography_level | text | national / state | Built |
| state_fips | int | State FIPS (null for national rows) | dim_geography |
| state_abbr | text | State abbreviation (null for national rows) | All sources |
| party_key | text | DEM / REP / OTH / IND | dim_party |
| party_name | text | Democratic / Republican / Other / Independent | Standardised in silver |
| candidate | text | Candidate name where the source gives it (Texas AG 2026); null otherwise | Wikipedia infoboxes |
| votes | int | Votes for this party in this race/geography; null where the source gives seats only (House by state) | MEDSL / Wikipedia |
| vote_share_pct | float | Party share of the two-party vote (Senate/President) or of all votes (House national, Texas) — see note below | Computed |
| seats_before | int | Seats held before the election (House national rows only) | Wikipedia results tables |
| seats_after | int | Seats won/held after the election (House rows only) | Wikipedia results tables |
| net_change | int | seats_after − seats_before (House rows only; always computed, never copied from the source +/- column, which is unsigned) | Computed |
| margin_pts | float | Democratic margin in points (positive = Democratic lead); for the Republican row it is the negative of the Democratic row's margin | Computed |
| winner_party | text | Winning party, where known | MEDSL / Wikipedia |
| status | text | certified / preliminary | Source status |

Vote-share note: for Senate and presidential races, `vote_share_pct` is
the **two-party** share (Democratic votes ÷ (Democratic + Republican
votes)); the Republican row's share is 100 minus the Democratic share.
For the national House popular vote and Texas races, it is the share of
**all** votes (including third parties), as reported by the source.

Row counts by office: HOU 418 (18 national + 400 state), SEN 416
(208 races × 2), PRE 306 (153 state-years × 2), GOV 72, ATG 2.

## fact_finance — 12,210 rows

One row per candidate-cycle, from the FEC candidate summary files.

| Column | Type | Meaning | Source |
|---|---|---|---|
| candidate_id | text | FEC candidate ID (first letter = office: H/S/P) | FEC weball |
| candidate_name | text | Candidate name (LAST, FIRST) | FEC weball |
| cycle | int | Election cycle (2018/2022/2026) | FEC weball |
| office | text | H / S / P | FEC weball |
| office_name | text | House / Senate / President | Derived |
| state_abbr | text | Office state (territories included) | FEC weball |
| state_name | text | State name | dim_geography |
| district | text | House district (00 = at-large) | FEC weball |
| incumbent_status | text | I = incumbent, C = challenger, O = open seat | FEC weball |
| party_raw | text | Original 3-letter party code | FEC weball |
| party_name | text | Democratic / Republican / Other (standardised) | Silver |
| party_key | text | DEM / REP / OTH | dim_party |
| total_receipts | decimal | Total receipts, two-year cycle | FEC weball field 6 (verified vs FEC API) |
| total_disbursements | decimal | Total disbursements | FEC weball field 8 |
| cash_on_hand_bop | decimal | Cash on hand, beginning of period | FEC weball field 10 (verified arithmetically) |
| cash_on_hand_end | decimal | Cash on hand, end of period | FEC weball field 11 |
| debts_owed_by | decimal | Debts owed by the committee | FEC weball field 17 |
| individual_contributions | decimal | Contributions from individuals | FEC weball field 18 |
| other_committee_contributions | decimal | Contributions from other committees (PACs) | FEC weball field 26 |
| party_committee_contributions | decimal | Contributions from party committees | FEC weball field 27 |
| coverage_end_date | date | End date of the most recent report in the file | FEC weball field 28 |
| status | text | certified (2018/2022) / preliminary (2026) | Source status |

Negative money values are legitimate in FEC data (refunds exceed
receipts; a committee can owe more than it holds) and are kept, not
quarantined. See `docs/PROJECT_STATE.md` for the audit counts.

## fact_turnout — 60 rows

| Column | Type | Meaning | Source |
|---|---|---|---|
| cycle | int | Election year | UF Election Lab |
| geography_level | text | national / state | Built |
| state_abbr | text | State (null for national rows) | UF v1.2 |
| turnout_rate_pct | float | VEP (voting-eligible population) turnout rate, % | UF Election Lab v1.4 (national 1994–2022) and v1.2 (states, 2022) |
| status | text | final / not yet published | Source status |

National rows: 9 (1994–2022 final, 2026 with a null rate and status
"not yet published"). State rows: 51 (2022 only).

## fact_texas_statewide — 13 rows

One row per Texas statewide race in the deep-dive.

| Column | Type | Meaning | Source |
|---|---|---|---|
| cycle | int | Election year | MEDSL / Wikipedia |
| state | text | Texas | Built |
| office | text | Governor / Senate / President / Attorney General | Built |
| dem_candidate / rep_candidate | text | Candidate names (null for MEDSL rows, which are vote totals) | Wikipedia infoboxes |
| dem_votes / rep_votes | int | Votes | MEDSL / Wikipedia |
| dem_pct / rep_pct | float | Share of all votes (governor/AG) or two-party share (Senate/President from MEDSL) | Computed / source |
| margin_pts | float | Democratic margin in points (positive = Democratic lead) | Computed |
| winner_party | text | Winning party | Source |
| status | text | certified / preliminary | Source status |

Rows: Governor 2014/2018/2022/2026; Senate 2014/2018/2020/2024/2026;
President 2016/2020/2024; Attorney General 2026.

## fact_senate_composition — 37 rows (added after Part 4, src/03b)

One row per Congress per party: the Senate's composition, built because
the gold layer held Senate votes but no Senate seat counts.

| Column | Type | Meaning | Source |
|---|---|---|---|
| cycle | int | Election year that seated the Congress | Computed from `years` |
| congress | int | Congress number (103–120) | Wikipedia party-divisions table |
| party_name | text | Democratic / Republican / Independent | Source |
| seats_before | int | That party's seats in the previous Congress (null for the 103rd, the baseline) | Computed |
| seats_after | int | That party's seats in this Congress | Source |
| net_change | int | seats_after − seats_before (null for the 103rd) | Computed |
| status | text | certified / preliminary (2026 only) | Source status |

Rows: 103rd–119th Congresses, Democratic and Republican (34 rows),
plus the 120th Congress (2026): Democratic 53, Republican 45,
Independent 2 (3 rows, preliminary).

Convention — read before using `net_change`: it is the change in the
chamber's COMPOSITION between Congresses, not the election-night seat
flip count. It includes special elections, resignations and party
switches that happen inside a Congress. Two cases where it differs
from the flip count: 2006 shows Democratic +5 (not +6) because Joe
Lieberman won Connecticut as an Independent and sits in the table
nowhere; 2018 shows Democratic −1 (not −2) because Doug Jones's
December 2017 special-election win in Alabama is inside the 115th
Congress baseline. Also, where the source table gives a RANGE for a
Congress (composition changed mid-Congress), the recorded value is the
LOW end of the range — the parse rule from Part 1 (e.g. the 115th
Senate is recorded as Republican 50, the low end of "50–52"). The
2026 rows are exact and unaffected.

## fact_senate_flips_2026 — 6 rows (promoted from silver, src/03c)

The flipped 2026 Senate seats named on the Wikipedia results table.
Columns: cycle, chamber, state, state_abbr, incumbent,
incumbent_party, winner, winner_party, result_text, status. All
preliminary. The 7th R→D flip recorded in the composition table is
not named here — the page does not identify it individually (see
docs/findings.md).

## fact_house_closest_races — 163 rows (promoted from silver, src/03c)

The closest House races of 2018 (89 rows) and 2022 (74 rows), from the
Wikipedia closest-races tables. Columns: cycle, district, winner
(winning party; "Democratic (flip)" where the seat changed hands),
margin_pts, margin_band ("<5 pts" / "5–10 pts"). The table IS the
under-10-points set (largest margin 9.86 in 2018, 9.95 in 2022). No
2026 rows — no district-margin source has been published yet.

## Schema diagram (text)

```
dim_cycle ─┐
dim_party ─┼─► fact_results ◄─ dim_geography
dim_office ┘      (race-state-cycle grain)
                     │
dim_party ───► fact_finance (candidate-cycle, via party_key)
dim_geography ─┘      (via state_abbr)
dim_cycle ────► fact_turnout (national + state 2022)
fact_texas_statewide (standalone, Texas offices)
fact_senate_composition (standalone, Congress-party)
fact_senate_flips_2026 (standalone, 6 flipped seats)
fact_house_closest_races (standalone, district margins 2018/2022)
```

Relationships for Power BI: `fact_results[cycle]` → `dim_cycle[cycle]`;
`fact_results[state_abbr]` → `dim_geography[state_abbr]`;
`fact_results[party_key]` → `dim_party[party_key]`;
`fact_finance[cycle]` → `dim_cycle[cycle]`;
`fact_finance[state_abbr]` → `dim_geography[state_abbr]`;
`fact_turnout[cycle]` → `dim_cycle[cycle]`;
`fact_senate_composition[cycle]` → `dim_cycle[cycle]`.
