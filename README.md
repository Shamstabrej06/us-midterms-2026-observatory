# US Midterms Observatory 2026

**Take someone who heard "the midterms were different this time" and
show them — with computed, sourced data — what happened, how it
happened, and why this cycle broke or confirmed the historical
patterns of US midterm elections.**

> **Status: 2026 figures are preliminary.** 19 House races and 2
> governor races were still uncalled, the Senate composition is given
> as a range on the source page, and the FEC file is a mid-cycle
> snapshot (coverage to 2026-10-14). All 2026 numbers below are
> labelled preliminary and will move as races are called and filings
> arrive.

## Headline findings

All numbers are computed by the pipeline in `src/` from the gold
layer (`outputs/midterms.db`). Full tables and explainers:
[`docs/findings.md`](docs/findings.md).

- **House (preliminary):** Democrats won **254 seats** (from 214
  before), Republicans **162** (from 218) — net **Democrats +40,
  Republicans −56**, with 19 races uncalled. Popular vote:
  Democrats **64,014,623 (55.8%)**, Republicans 48,995,107 (42.7%),
  margin **D +13.1 points** — the highest Democratic House
  popular-vote share in the 1994–2026 series.
- **Senate (preliminary):** Democrats **53**, Republicans **45**,
  Independents **2** — net **Democrats +8, Republicans −8**. Seven
  seats flipped Republican → Democratic; none flipped the other way.
- **Governors (preliminary):** Democrats won **22 of 36** races,
  Republicans 12, 2 uncalled. Seats after: Democrats 28–30,
  Republicans 20–22. Net: Democrats +4 to +6.
- **The midterm pattern:** the president's party lost House seats in
  **7 of 9** midterms from 1994 to 2026. Exceptions: 1998 (Democrats
  +5) and 2002 (Republicans +8). 2026 — Republicans −56 under
  President Trump — confirms the pattern and is the second-largest
  loss in the series after 2010 (Democrats −64).
- **The comeback, measured:** in 2018 Democrats gained 41 House
  seats with 53.4% of the vote; in 2022 they lost 9 seats with
  47.29%. In 2026 they gained **40 seats with 55.8%** of the vote.
- **Turnout:** national VEP turnout 2018 **50.05%**, 2022 **46.12%**.
  The 2026 rate is **not yet published** — no comparison is possible
  yet.
- **Competitiveness:** House races decided by under 10 points —
  2018: **89** (43 under 5); 2022: **74** (37 under 5). 2026: not
  computable yet (no district-margin source published).
- **Money:** total House + Senate candidate receipts — 2018:
  **$3,125,950,077**; 2022: **$4,139,563,155**; 2026:
  **$4,199,069,691** (preliminary). The top spender won 29 of 35
  Senate races in 2018 (82.9%), 28 of 35 in 2022 (80.0%) and 29 of
  31 in 2026 (93.5%).
- **Split outcomes:** states whose governor and House-delegation
  majority went to different parties — 2022: **7**; 2026: **4**
  (Georgia, New Hampshire, Texas, Vermont).
- **Texas:** Democrats won all three statewide races on the 2026
  ballot — Governor **D +7.1** (Hinojosa 52.8% beat Abbott 45.7%),
  Senate **D +12.1** (Talarico 55.1% beat Paxton 43.0%), Attorney
  General **D +6.5** (Johnson 52.4% beat Middleton 45.9%) — the
  first break in Republicans holding every Texas statewide office
  since the 1990s. The presidential picture runs the other way:
  Texas voted Republican for president by 13.9 points in 2024.

## Pipeline architecture

```
bronze (raw, untouched) ──► silver (cleaned, harmonised) ──► gold (star schema)
data/raw/                   data/silver/                      outputs/gold/ + outputs/midterms.db
```

1. **`src/01_acquire.py`** — downloads the sources, parses the
   Wikipedia results tables and the FEC bulk files, writes
   size-safe extracts to `data/sample/`. Logs every source in
   `data/SOURCES.md`.
2. **`src/02_bronze_to_silver.py`** — standardises county names and
   FIPS codes, normalises party labels, coerces vote/money fields to
   numeric with parse-failure audit counts, validates every table,
   writes silver tables + a quarantine CSV. **Quarantine: 0 rows.**
   Negative FEC money values are legitimate (refunds/debt) and are
   audited, not quarantined.
3. **`src/03_build_gold.py`** (+ `src/03b_senate_composition.py`,
   `src/03c_dashboard_tables.py`) — builds the star schema and the
   SQLite database.
4. **`src/04_findings.py`** — computes every finding from the gold
   layer and writes `docs/findings.md` +
   `outputs/Findings_Scorecard.xlsx` (11 sheets, one per metric
   family).

### Star schema

```
dim_cycle ─┐
dim_party ─┼─► fact_results ◄─ dim_geography     (race-state-cycle grain)
dim_office ┘
dim_party ───► fact_finance (candidate-cycle)
dim_geography ─┘
dim_cycle ────► fact_turnout (national + state 2022)
fact_texas_statewide (standalone, Texas offices)
fact_senate_composition (standalone, Congress-party)
fact_senate_flips_2026 (standalone, 6 flipped seats)
fact_house_closest_races (standalone, district margins 2018/2022)
```

**Grain note:** the brief specifies `fact_results` at
race-county-cycle grain. No public county-level vote data could be
obtained (the MEDSL county files are guestbook-gated; see
`docs/data_inventory.md`), so `fact_results` is built at
race-STATE-cycle grain instead, and the county-level metrics are
dropped rather than estimated. See `docs/data_dictionary.md`.

### The redistricting caveat (3 lines)

Congressional district boundaries changed after the 2020 census, and
California and Texas redrew maps again mid-decade before 2026. So a
2022-to-2026 comparison of a redrawn district's results is not a
swing in the same geography. This project compares at state level or
carries the caveat — it never presents a redrawn district's "swing"
as if the geography were unchanged.

## Repo structure

```
us-midterms-2026-observatory/
├── README.md
├── data/
│   ├── SOURCES.md            # every source: URL, retrieval date, size, rows, status
│   ├── raw/                  # bronze: raw downloads (full files out of git via .gitignore)
│   ├── sample/               # size-safe extracts the scripts actually run on
│   └── silver/               # cleaned, harmonised tables
├── docs/
│   ├── PROJECT_STATE.md      # the running project state (sources, row counts, headline metrics)
│   ├── data_inventory.md     # what each file contains, quality problems on first inspection
│   ├── data_dictionary.md    # every gold table and column, grain, source
│   ├── findings.md           # the findings pack: tables + plain-language explainers
│   └── linkedin_and_portfolio.md
├── outputs/
│   ├── midterms.db           # SQLite gold layer (11 tables)
│   ├── gold/                 # gold CSVs (also copied to powerbi/gold/)
│   └── Findings_Scorecard.xlsx
├── powerbi/
│   ├── gold/                 # import-ready gold CSVs
│   ├── dax_measures.md       # every DAX measure, grouped by dashboard page
│   ├── build_guide.md        # page-by-page assembly for the 6-page dashboard
│   └── theme.json            # muted blue / muted red / grey theme
└── src/
    ├── 01_acquire.py
    ├── 02_bronze_to_silver.py
    ├── 03_build_gold.py
    ├── 03b_senate_composition.py
    ├── 03c_dashboard_tables.py
    └── 04_findings.py
```

## Quickstart

```bash
# 1. Python 3.10+; install the only dependencies:
pip install pandas openpyxl lxml

# 2. Run the pipeline in order (each script prints what it wrote):
python3 src/01_acquire.py
python3 src/02_bronze_to_silver.py
python3 src/03_build_gold.py
python3 src/03b_senate_composition.py
python3 src/03c_dashboard_tables.py
python3 src/04_findings.py

# 3. Open the gold layer:
#    - SQLite: outputs/midterms.db
#    - Excel scorecard: outputs/Findings_Scorecard.xlsx
#    - Findings: docs/findings.md

# 4. Build the dashboard in Power BI Desktop:
#    follow powerbi/build_guide.md (import powerbi/gold/, create the
#    measures in powerbi/dax_measures.md, apply powerbi/theme.json).
```

The scripts run end-to-end on the committed extracts in
`data/sample/` — the full raw files are not needed. Raw files over
~10 MB are kept out of git (see `.gitignore`).

## Sources & attribution

| Data | Source | Retrieved |
|---|---|---|
| President (state-level) 1976–2024 | MIT Election Data and Science Lab, doi:10.7910/DVN/42MVDX | 2026-11-09 |
| Senate (statewide) 1976–2024 | MIT Election Data and Science Lab, doi:10.7910/DVN/PEJ5QU | 2026-11-09 |
| House / Senate / governor results 1994–2026 | Wikipedia election results tables (see `data/SOURCES.md` for the page list) | 2026-11-09 |
| Candidate finance 2018 / 2022 / 2026 | FEC bulk data, candidate summaries (weball) | 2026-11-09 |
| Party control 1994–2026 | Wikipedia, "Party divisions of United States Congresses" | 2026-11-09 |
| Turnout (VEP) 1994–2022 | UF Election Lab, US VEP Turnout Rates v1.4 | 2026-11-09 |
| County population 2024 | US Census Bureau, Vintage 2024 population estimates | 2026-11-09 |

Full per-source detail (exact URL, file size, row count,
certified-vs-preliminary status, licence/terms note) is in
[`data/SOURCES.md`](data/SOURCES.md). Substitutions forced by
unreachable sources are documented in
[`docs/data_inventory.md`](docs/data_inventory.md): the MEDSL House
and county files are guestbook-gated, so Wikipedia results tables
were substituted; the Census API is key-gated, so Vintage 2024
population estimates were substituted and the ACS income/education
fields were dropped.

## Methods & limitations (read before citing a number)

- **Preliminary 2026 figures.** The 2026 House, Senate and governor
  numbers come from Wikipedia results pages retrieved 2026-11-09,
  when 19 House races and 2 governor races were uncalled and the
  Senate composition was given as a range (D 52–54). The FEC 2026
  file covers filings to 2026-10-14 only. Every 2026 figure in this
  repo is labelled preliminary and will change.
- **District boundary changes.** See the redistricting caveat above.
  State-level seat changes 2022 → 2026 partly reflect the
  California and Texas mid-decade redraws, not only votes.
- **FEC coverage limits.** The 2026 money totals are a mid-cycle
  snapshot and will rise with post-election filings. Negative money
  values in the FEC files are legitimate (refunds, debt) and are
  kept, not removed.
- **No county data.** County-level vote shift and county flips are
  not in this repo — no public county-level vote data could be
  obtained.
- **No 2026 turnout.** The UF Election Lab had not published a 2026
  VEP turnout rate at retrieval time; no rate is estimated here.
- **No 2026 district margins.** No closest-races table or
  district-winner table for 2026 had been published, so 2026
  competitiveness, the 15 closest 2026 races, flipped House seats
  and a House top-spender win rate are all dropped, not guessed.
- **Per-state 2026 House seats.** The per-state table covers 47 of
  50 states — Alaska, Louisiana and North Carolina have no 2026
  seat split in the source table — so no state-level net total is
  reported. The 47 known states sum to 248 Democratic seats against
  the national infobox total of 254.
- **Senate composition convention.** `fact_senate_composition`
  records the change in chamber composition between Congresses,
  which includes special elections and party switches — not the
  election-night flip count (see the note in
  `docs/data_dictionary.md`).
- **Neutral analysis.** Parties are named factually, outcomes are
  reported as computed, and no predictions are presented as fact.

## About this project

This is a **self-directed portfolio / learning project** built on
public data by Shamstabrej Tamboli, a data engineer in Windsor,
Ontario, Canada (Microsoft Certified: Fabric Data Engineer Associate
DP-700, Azure Data Fundamentals DP-900; MSc Computer Science (AI),
University of Windsor). It is not client or employer work. It
showcases data ingestion from hostile public sources, cleaning and
harmonisation, dimensional modelling (star schema), data quality
validation with quarantine, and Power BI + DAX.
