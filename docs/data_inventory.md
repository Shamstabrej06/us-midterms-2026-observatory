# Data inventory

First inspection of every acquired file, 2026-11-09. Row counts are the
counts the pipeline must reproduce (checked in `src/02_bronze_to_silver.py`).

## MEDSL — president (state-level)

`1976-2024-president.csv` — 4,823 data rows, 15 columns:
`year, state, state_po, state_fips, state_cen, state_ic, office,
candidate, party_detailed, writein, candidatevotes, totalvotes, version,
notes, party_simplified`.

- **State-level, not county-level.** One row per candidate per state per
  presidential election. 2020: 547 rows; 2024: 535 rows. No county column
  exists in this file.
- `party_simplified` values: DEMOCRAT, REPUBLICAN, LIBERTARIAN, GREEN,
  OTHER. `party_detailed` has long labels (e.g. "DEMOCRATIC-FARMER-LABOR").
- `candidatevotes` / `totalvotes` are integers; no missing values in the
  2016–2024 slice.
- Quality problem: `version` is a datestamp (e.g. 20210113), not a version
  number. `notes` is empty for nearly all rows.

## MEDSL — Senate (statewide)

`1976-2024-senate-state.tab` — 3,945 data rows (comma-separated despite
the `.tab` name), 19 columns: `year, state, state_po, state_fips,
state_cen, state_ic, office, district, stage, special, candidate,
party_detailed, writein, mode, candidatevotes, totalvotes, unofficial,
version, party_simplified`.

- One row per candidate per statewide Senate race. `district` is always
  "statewide". `stage` is "gen" (general) or "runoff" — the pipeline keeps
  general elections only, plus runoffs where they decided the seat (none
  in the 2014–2024 window except the 2021 Georgia runoffs, which are
  out of scope for midterm cycles).
- 2021 has 4 rows (the two Georgia runoff races, January 2021) — kept
  out of the midterm tables.
- `mode` is "total" for all rows in the window. `unofficial` is False
  throughout the window.

## FEC — candidate summaries (weball)

`weball18.txt` 3,687 rows; `weball22.txt` 4,153 rows; `weball26.txt`
4,370 rows. Pipe-delimited, no header, 30 fields per row.

- The 2022 zip first downloaded truncated (175,355 bytes, bad central
  directory); re-downloaded cleanly (190,724 bytes, 4,153 rows).
- Column order verified against the FEC API (see SOURCES.md). Money
  fields are plain decimals with no currency symbols or commas.
- `cand_ici`: I = incumbent, C = challenger, O = open seat.
- Coverage end dates in the 2026 file run to 2026-10-14 — the file is a
  snapshot, not the final cycle totals.
- Quality problem: a small number of rows have a blank party affiliation
  or a nonstandard code (e.g. "08", "NNE"); these map to "Other" in
  silver. Rows with != 30 fields (if any) go to quarantine.

## Wikipedia — House election pages (1994–2026)

One HTML page per cycle. The results summary table is table index 4 on
every page except 1994 (index 6); column layouts differ by cycle and are
handled per-cycle in `src/01_acquire.py`.

- **The `+/-` (net change) column is unsigned** in every summary table
  (e.g. 2014 Democrats show "13", not "−13"). Net change is always
  computed as seats-after minus seats-before.
- 2018 and 2022 pages each carry a "closest races" table (District /
  Winner / Margin): 89 rows in 2018, 74 rows in 2022. Both list only
  races decided by under 10 points (max margin 9.86 in 2018, 9.95 in
  2022) — so the tables ARE the under-10-points set, and the under-5
  subset is counted from the margin column (43 in 2018, 37 in 2022).
- The 2026 page has **no closest-races table** and its results table's
  seat columns are still blank; seats and popular vote come from the
  infobox (19 races uncalled, 95.6% declared as of Nov 6, 2026).
- The 2026 summary table's vote totals (48.3M D / 40.9M R) exclude 98
  districts with 95% or less reporting and disagree with the infobox
  (64.0M D / 49.0M R). The infobox is used as the primary figure and
  the discrepancy is recorded here.
- Seats-by-state tables (table index 5) exist on all four recent pages:
  50 states × 4 cycles = 200 rows.

## Wikipedia — 2026 Senate and governor pages

- Senate composition table (table index 3): before D45/I2/R53; 35 seats
  up (13 D, 22 R); overall result row D20/R13 general + D1/R1 special.
  The retiring + running sub-rows sum to 31, not 33 — two races' outcomes
  appear only in the overall result row (footnote [f][g] on the running
  row). The infobox gives the final composition as a range (D 52–54),
  i.e. 2 races remain uncalled. The pipeline uses the overall result
  row (D 53 / R 45 / I 2) and records the range.
- Governor infobox: 36 states up (18 D-held, 18 R-held); D won 22, R won
  12, 2 uncalled; seats after D 28–30 / R 20–22 (range).

## Wikipedia — party divisions (control table)

`wiki_control.html` — one wikitable, 128 rows (2 header rows + 119
Congresses + era header rows). Columns are Senate (Total, party 1,
party 2, Others, Vacancies), House (same), President, Trifecta.

- The party columns change names by era ("Democratic-Republicans /
  Federalists", "Jacksonian / Anti-Jackson", "Democrats / Whigs",
  "Democrats / Republicans"). The parser tracks the most recent header
  row and only the modern (Democrats/Republicans) era is kept.
- The President cell uses rowspan: rows that omit it inherit the
  previous row's president.
- Several Senate/House counts are ranges ("46–48", "200/199") because
  seats changed mid-Congress (deaths, resignations, late seatings,
  special elections). The parser takes the first number of a range and
  the inventory notes the ranges; the midterm-pattern metric does NOT
  use this table (it uses the results tables instead).
- Spot checks: 103rd (1993–95) Senate 57 D / 43 R, House 258 D / 176 R;
  104th Senate 47 D / 53 R, House 204 D / 230 R — both match the
  historical record.

## Turnout — UF Election Lab

- `US_VEP_Turnout_Rates_v1.4.csv` — 119 rows, 1789–2024, national VEP
  turnout rates for presidential and midterm years. Midterm VEP rates
  used: 1994: 41.10%, 1998: 38.10%, 2002: 39.50%, 2006: 40.40%,
  2010: 41.00%, 2014: 36.70%, 2018: 50.05%, 2022: 46.12%.
  **No 2026 row exists** — the file ends at 2024.
- `Turnout_1980_2022_v1.2.csv` — 1,144 rows: national + state VEP
  turnout, 1980–2022. National rows for 1994 and 1996 are blank (NaN);
  the v1.4 series supplies those years. State-level 2022 VEP rates:
  50 states + DC (51 rows).
- No state-level 2026 turnout has been published by the Election Lab
  as of 2026-11-09, so the state-level 2026-vs-2022 turnout comparison
  is dropped.

## Census — county population estimates

`co-est2024-alldata.csv` — 3,195 rows (3,144 counties + states).
Columns used: `STATE`, `COUNTY`, `STNAME`, `CTYNAME`,
`POPESTIMATE2024`. The file is Latin-1 encoded (a byte 0xf1 appears in
a county name) — the parser reads it as Latin-1. County FIPS is
`STATE * 1000 + COUNTY`.

## Known gaps (carried into PROJECT STATE)

1. No county-level vote data (MEDSL county files guestbook-gated).
2. No ACS income/education (Census API key-gated).
3. No 2026 VEP turnout rate; no state-level 2026 turnout.
4. No 2026 House district margins / closest-races table (races uncalled).
5. No district-level winner-party list for flipped 2026 House seats.
6. FEC 2026 is a mid-cycle snapshot (coverage through 2026-10-14).
