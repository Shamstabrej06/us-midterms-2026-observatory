# LinkedIn & Portfolio Copy — US Midterms Observatory 2026

All numbers below come from `docs/PROJECT_STATE.md` only. 2026
figures are preliminary — say so wherever they appear.

## LinkedIn post

The 2026 midterms broke the pattern — and the data shows exactly how much.

Democrats gained 40 House seats (preliminary) on a 13.1-point popular-vote margin — the widest in the 1994–2026 series.

The Senate flipped too: Democrats +8, to 53 seats (preliminary).

Texas is the story inside the story: Democrats won the governorship, Senate seat and Attorney General's office — the first break in a Republican hold on every Texas statewide office since the 1990s.

But turnout? The 2026 rate isn't published yet — and I refused to estimate it. The honest gaps are in the repo, next to the findings.

I built the whole thing as a pipeline: hostile public sources → cleaned star schema → Power BI dashboard. Repo link in the comments.

What surprised you most about this cycle — the size of the House swing, or Texas?

Repo: https://github.com/Shamstabrej06/us-midterms-2026-observatory

#DataEngineering #PowerBI #Python #ElectionData #DataAnalysis

## 5-slide carousel — "5 charts that explain this midterm"

**Slide 1 — The Night**
Chart: House seats by party, 2026 (bar chart, 218-seat majority line).
Headline number: Democrats 254, Republicans 162 (preliminary, 19 races uncalled).
One line: Democrats cleared the majority with 36 seats to spare — and took the Senate 53–45 too.

**Slide 2 — The Comeback, Measured**
Chart: Net House seat change by cycle, 2018 vs 2022 vs 2026 (column chart).
Headline number: +40 Democratic seats in 2026, after −9 in 2022.
One line: 2026 is the mirror image of 2022 — the second-largest Democratic midterm gain since 2018's +41.

**Slide 3 — Texas Deep-Dive**
Chart: Texas statewide two-party margin, 2014–2026 (line chart, Governor / Senate / President).
Headline number: Governor D +7.1 in 2026, after R +10.9 in 2022.
One line: A decade of narrowing Republican margins ended in a flip — all three statewide offices on the ballot went Democratic.

**Slide 4 — The Midterm Pattern**
Chart: President's-party net House seat change, every midterm 1994–2026 (column chart).
Headline number: The president's party lost seats in 7 of 9 midterms.
One line: 2026 confirmed the pattern — Republicans −56 is the second-largest loss in the series after 2010's −64.

**Slide 5 — Money vs Votes**
Chart: Total House + Senate candidate receipts by cycle, stacked House/Senate (column chart).
Headline number: $4.20bn in 2026 (preliminary) vs $4.14bn in 2022 — and the top spender won 29 of 31 Senate races (93.5%).
One line: Money kept rising, and in 2026 it predicted the winner more often than in 2018 (82.9%) or 2022 (80.0%) — but the 2026 file is a mid-cycle snapshot.

## Upwork portfolio copy

**Title (≤70 chars):**
US Midterms Observatory 2026: Election Data Pipeline + Power BI

**Role line:**
Data Engineer — Python · pandas · SQLite · Power BI · DAX

**Description (540–580 characters):**
Built a full election-data pipeline from hostile public sources: MEDSL results, FEC bulk files, Census estimates and Wikipedia tables. Harmonised 12,210 candidate finance records and 1,214 race results into a star schema (SQLite + CSV) with validation and quarantine. Computed the findings — House +40 Democratic seats, Senate +8, a 13.1-point popular-vote margin — and built a six-page Power BI dashboard with DAX measures and a neutral theme. Where the data could not support a metric — 2026 turnout, county shifts — the project says so and drops it rather than estimating.

**About (longer text):**
The 2026 US midterms were described as "different this time", so I
built a project that tests that claim with computed, sourced data
instead of commentary.

The pipeline ingests hostile public sources — MEDSL election files,
FEC bulk candidate summaries, Census population estimates and
Wikipedia results tables — and turns them into a clean star schema
(SQLite + CSV) through a bronze → silver → gold medallion structure.
Silver standardises county names and FIPS codes across sources and
cycles, normalises party labels, coerces vote and money fields to
numeric with parse-failure audits, and quarantines bad rows with a
reason (0 rows quarantined; negative FEC money values are legitimate
refunds and debt, audited rather than dropped).

The findings are computed, never asserted: every headline number
traces to a gold table. Democrats gained 40 House seats on a
13.1-point popular-vote margin (preliminary), the Senate flipped
Democratic +8, and Texas — where Republicans have held every
statewide office since the 1990s — saw Democrats win the
governorship, the Senate seat and the Attorney General's office.
Where the data cannot support a metric (2026 turnout, county-level
shifts, district margins), the project says so and drops the metric
rather than estimating it.

The deliverables are a findings pack (markdown + Excel scorecard),
a six-page Power BI dashboard with full DAX measures and a neutral
theme, and a build guide a competent Power BI user can follow in
one sitting. The project also documents its limits honestly:
preliminary 2026 figures, post-2020 redistricting, and FEC coverage
cut off at 2026-10-14.

**Skills (exactly 5):**
1. Power BI
2. Data Analysis
3. Python
4. SQL
5. Data Visualization
