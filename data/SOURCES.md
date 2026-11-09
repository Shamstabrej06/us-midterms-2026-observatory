# Data sources

All files retrieved **2026-11-09** by the build (see `src/01_acquire.py`).
Full raw files live in `data/raw/` and are **excluded from git** (see
`.gitignore`); the committed extracts in `data/sample/` are derived from
them by `src/01_acquire.py` and are all the pipeline needs to run.

Status words: **certified** = final/official results; **preliminary** =
results still being counted or reported; **blocked** = the source could
not be downloaded and a substitute is documented.

## Election results — MIT Election Data and Science Lab (MEDSL, Harvard Dataverse)

| File | Source | Size | Rows | Status |
|---|---|---|---|---|
| `1976-2024-president.csv` | doi:10.7910/DVN/42MVDX — U.S. President 1976–2024 (state-level) | 514,108 B | 4,823 | certified |
| `1976-2024-senate-state.tab` | doi:10.7910/DVN/PEJ5QU — U.S. Senate statewide 1976–2024 | 530,501 B | 3,945 | certified |

Terms: MEDSL data is released for public research use; cite the Dataverse
DOI. The president file is **state-level, not county-level** (no county
column) — that is why county geography comes from the Census file only.

### Attempted but blocked — MEDSL guestbook gate

| Dataset | DOI | What happened |
|---|---|---|
| U.S. House 1976–2024 | doi:10.7910/DVN/IG0UN2 | Dataverse refuses the download without a guestbook response (guestbookID 458, requires a name and email). Not submitted — no user email on file and no consent to file one. |
| County Presidential Election Returns 2000–2024 | doi:10.7910/DVN/VOQCHQ | Same guestbook gate. |
| Presidential county elections returns data, 2000–2020 | doi:10.7910/DVN/8RFBRF | Same guestbook gate. |

**Consequence (recorded in PROJECT STATE):** no public county-level vote
data could be obtained. County-level House vote shift 2022 → 2026,
county flips, and the Texas county shift table are dropped. The House
district-level results below are the substitute for the House file.

## Election results — Wikipedia (district/state-level results tables)

Wikipedia election pages are used as the **closest equivalent public
source** for House district-level results (the MEDSL House file is gated)
and for all 2026 outcomes (MEDSL has no 2026 data yet). Every number in
the findings traces to a named table on one of these pages; the parser
(`src/01_acquire.py`) records which table index and column layout it used.

| File | Page | Size | Status |
|---|---|---|---|
| `wiki1994house.html` | 1994 United States House of Representatives elections | 2,071,760 B | certified |
| `wiki1998house.html` | 1998 United States House of Representatives elections | 2,147,956 B | certified |
| `wiki2002house.html` | 2002 United States House of Representatives elections | 2,096,504 B | certified |
| `wiki2006house.html` | 2006 United States House of Representatives elections | 2,394,013 B | certified |
| `wiki2010house.html` | 2010 United States House of Representatives elections | 2,781,098 B | certified |
| `wiki14house.html` | 2014 United States House of Representatives elections | 2,849,234 B | certified |
| `wiki18house.html` | 2018 United States House of Representatives elections | 3,052,278 B | certified |
| `wiki22house.html` | 2022 United States House of Representatives elections | 3,331,269 B | certified |
| `wiki26.html` | 2026 United States House of Representatives elections | 3,619,553 B | **preliminary** — 19 races uncalled; 95.6% of votes declared as of Nov 6, 2026, 11:15 PM EST; popular-vote totals are the page's infobox snapshot |
| `wiki26sen.html` | 2026 United States Senate elections | 2,370,308 B | **preliminary** — page infobox gives the final composition as a range (D 52–54) because 2 races remain uncalled |
| `wiki26gov.html` | 2026 United States gubernatorial elections | 2,144,900 B | **preliminary** — 2 of 36 state races uncalled; seats-after given as a range (D 28–30) |
| `wiki_control.html` | Party divisions of United States Congresses | 768,037 B | reference table (transcribed by the parser; see inventory) |
| `wiki26elex.html` | 2026 United States elections (overview) | 2,239,541 B | context only |
| `wiki_midterm.html` | United States midterm election | 457,521 B | context only |

Licence: Wikipedia text and tables are CC BY-SA 4.0; attribute Wikipedia
and the underlying sources each page cites (Clerk of the House Election
Statistics; AP via Google for 2026 vote totals).

## Campaign finance — Federal Election Commission (fec.gov bulk data)

| File | URL | Size | Rows | Status |
|---|---|---|---|---|
| `weball18.zip` | https://www.fec.gov/files/bulk-downloads/2018/weball18.zip | 171,196 B | 3,687 | certified (final cycle) |
| `weball22.zip` | https://www.fec.gov/files/bulk-downloads/2022/weball22.zip | 190,724 B | 4,153 | certified (final cycle) |
| `weball26.zip` | https://www.fec.gov/files/bulk-downloads/2026/weball26.zip | 199,974 B | 4,370 | **preliminary** — filings continue; latest coverage end date in file is 2026-10-14 |

The candidate summary ("weball") file has no header row. Column order was
verified against the FEC API (`api.open.fec.gov`, DEMO_KEY) for two
candidates (H2AK01083, H2AK01158): field 6 = total receipts, field 8 =
total disbursements, field 10 = cash on hand at beginning of period
(verified arithmetically: end cash − receipts + disbursements = field 10
for both candidates), field 11 = cash on hand end of period, field 17 =
debts owed, field 18 = individual contributions, field 26 = other
committee contributions, field 27 = party committee contributions,
field 28 = coverage end date. Field 4 is a numeric party code (1 =
Democratic, 2 = Republican, 3 = other) — verified by crosstab against
field 5, the 3-letter party affiliation. Fields 9, 12–14, 16 are present
but unmatched to any API field and are not used. Terms: U.S. government
public data, no licence restriction.

## Turnout — University of Florida Election Lab (US Elections Project)

| File | URL | Size | Rows | Status |
|---|---|---|---|---|
| `Turnout_1980_2022_v1.2.csv` | https://election.lab.ufl.edu/data-downloads/turnoutdata/Turnout_1980_2022_v1.2.csv | 116,830 B | 1,144 | final through 2022 |
| `vep14b.csv` (`US_VEP_Turnout_Rates_v1.4.csv`) | https://election.lab.ufl.edu/data-downloads/turnoutdata/US_VEP_Turnout_Rates_v1.4.csv | 1,581 B | 119 | final through 2024; **no 2026 rate published yet** |

VEP = voting-eligible population (voting-age population minus ineligible
noncitizens and ineligible felons, plus eligible overseas citizens). The
v1.2 file's national rows for 1994 and 1996 are blank; the v1.4 long
series (1789–2024) supplies those years (1994: 41.1%, 1998: 38.1%).
The 2026 VEP rate has not been published by the Election Lab as of
2026-11-09. The only 2026 turnout figure found is the Wikipedia 2026
House infobox's "125 million (estimated)" total ballots — reported as an
estimate, with no VEP denominator, so no 2026 VEP rate is computed.

## Demographics — U.S. Census Bureau

| File | URL | Size | Rows | Status |
|---|---|---|---|---|
| `co-est2024-alldata.csv` | https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv | 1,769,182 B | 3,195 | final (Vintage 2024 county population estimates) |

The Census API (api.census.gov, ACS 5-year) returns a "Missing Key"
HTML error page from this environment for both ACS and decennial
endpoints — the API is key-gated here and no key is on file. ACS median
income and education are therefore **dropped** from dim_geography;
the dimension carries county population (2024 estimate) only.

## How to re-fetch

`src/01_acquire.py` documents the exact URLs in its header and in this
file. Re-downloading the Wikipedia pages will return newer revisions
(2026 figures will move as races are called) — that is expected; the
committed extracts in `data/sample/` are the frozen snapshot this
project's numbers were computed from.
