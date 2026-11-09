# Power BI Build Guide — US Midterms Observatory 2026

Assemble this dashboard in Power BI Desktop in one sitting. The data
is in `powerbi/gold/` (11 CSVs). The measures are in
`powerbi/dax_measures.md` — create every measure listed there before
building the pages. The theme is `powerbi/theme.json`. This guide is
the supported path: there is no PBIP/TMDL project file. If you are
new to Power BI, do the setup section first and check each page's
"expected values" against `docs/findings.md` as you go.

## Design standard (applies to every page)

- **Theme:** Browse for `powerbi/theme.json` (View → Themes → Browse
  for themes) before building anything. Palette: muted blue #5B7FA6,
  muted red #B56A5E, grey #8A8D93, on a white background. No default
  Power BI blue anywhere. If a visual comes out default blue, the
  theme was not applied — reapply it.
- **Layout grid:** 1280 × 720 canvas (View → Page settings → Type:
  16:9). Every page has the same skeleton, top to bottom: headline
  band → KPI row → main visual → supporting visual → "How to read
  this" box. Align the KPI cards on one row with equal widths and
  equal gaps; use View → Gridlines and Snap to grid.
- **Headline band:** a text box across the top of the page with the
  page's ONE-LINE TAKEAWAY (given per page below). Font Segoe UI
  Semibold, 16 pt, dark grey #2F3337. The takeaway is a sentence the
  data supports — never an adjective or a prediction.
- **Chart titles as conclusions:** every visual's title states what
  the visual shows, e.g. "Turnout beat every midterm since 2018"
  is wrong (2026 is unpublished) — the correct title is given per
  visual below. Never use a bare field name as a title.
- **Data labels:** on for every bar chart (values at the end of the
  bars). On for the turnout line's 2018 and 2022 points.
- **Preliminary labels:** every card, visual title or footnote that
  shows a 2026 figure carries "(preliminary)". Put it in the visual
  title or in a small text box directly under the visual — not only
  in a footnote at the bottom of the page.
- **"How to read this" box:** a small text box at the bottom of
  every page, grey text 9 pt, in plain language for non-technical
  readers. The text is given per page below.
- **No party-colour dominance:** Democratic series use muted blue,
  Republican series use muted red, and the two are never the only
  colours on a page — grey is always present (axes, labels, the
  "other" category). Do not use bright red/blue.

## Setup

1. **Get the data.** Home → Get data → Text/CSV. Import all 11
   files from `powerbi/gold/`:
   `dim_cycle`, `dim_geography`, `dim_office`, `dim_party`,
   `fact_results`, `fact_finance`, `fact_turnout`,
   `fact_texas_statewide`, `fact_senate_composition`,
   `fact_senate_flips_2026`, `fact_house_closest_races`.
   Keep the file names as the table names. In Power Query, check
   that `cycle` is Whole Number and `seats_after` / `net_change` /
   `vote_share_pct` / `margin_pts` / `total_receipts` are Decimal
   Number. Close & Apply.
2. **Relationships** (Model view, single direction, one-to-many):
   - `dim_cycle[cycle]` → `fact_results[cycle]`
   - `dim_cycle[cycle]` → `fact_finance[cycle]`
   - `dim_cycle[cycle]` → `fact_turnout[cycle]`
   - `dim_cycle[cycle]` → `fact_senate_composition[cycle]`
   - `dim_geography[state_abbr]` → `fact_results[state_abbr]`
   - `dim_geography[state_abbr]` → `fact_finance[state_abbr]`
   - `dim_party[party_key]` → `fact_results[party_key]`
   - `dim_party[party_key]` → `fact_finance[party_key]`
   - `dim_office[office_key]` → `fact_results[office_key]`
   - `fact_texas_statewide`, `fact_senate_flips_2026` and
     `fact_house_closest_races` stay unconnected (standalone tables).
     Their visuals filter on their own columns.
3. **Measures.** Create every measure in `dax_measures.md`
   (Modeling → New measure). After each page's measures, check the
   card values against the "Expected values" in that file.
4. **Page size and theme.** Set 16:9 canvas, apply `theme.json`.

## Page 1 — The Night

**Headline band:** "Democrats took the House, the Senate and 22
governor races in 2026 — with 19 House races still uncalled."

**KPI row (4 cards, left to right):**

1. Card — measure `[House Seats D 2026]`. Title: "House seats —
   Democrats (preliminary)". Expected: **254**.
2. Card — measure `[House Seats R 2026]`. Title: "House seats —
   Republicans (preliminary)". Expected: **162**.
3. Card — measure `[Senate Seats D 2026]`. Title: "Senate seats —
   Democrats (preliminary)". Expected: **53**.
4. Card — measure `[Gov Wins D 2026]`. Title: "Governor races won
   by Democrats (preliminary)". Expected: **22 of 36**.

**Main visual — clustered bar chart, "House seats by party, 2026
(preliminary)":** Y-axis (values): `[House Seats D 2026]` is not
plottable as a series — instead use a bar chart with
`fact_results[party_name]` on the Y-axis and
`SUM(fact_results[seats_after])` on the X-axis, with visual filters
`office_key = HOU`, `geography_level = national`, `cycle = 2026`.
Two bars (Democratic 254, Republican 162). Data labels on. Add a
constant line at 218 (Analytics pane → Constant line, value 218,
label "Majority = 218 seats"). Takeaway under the visual:
"Democrats cleared the 218-seat majority with 36 seats to spare;
19 races are still uncalled."

**Supporting visual — donut chart, "Senate composition, 2026
(preliminary)":** Legend `fact_senate_composition[party_name]`,
Values `SUM(fact_senate_composition[seats_after])`, visual filter
`cycle = 2026`. Three slices: Democratic 53, Republican 45,
Independent 2. Data labels on, showing values. Takeaway: "The
Senate flipped with it: Democrats hold 53 seats to 45, plus 2
Independents."

**How to read this:** "Seats are the races already called. 19 House
races and 2 governor races were still uncalled when this data was
collected, so the totals will move slightly. The Senate total adds
to 100 because all 100 seats are accounted for."

## Page 2 — The Comeback, Measured

**Headline band:** "The 2026 swing reversed 2022: Democrats gained
40 House seats on a 13.1-point popular-vote margin (preliminary)."

**KPI row (4 cards):**

1. `[House Net Change D 2026]` — "Net House seats, Democrats 2026
   (preliminary)". Expected: **+40**.
2. `[House Popular Vote Margin 2026]` — "House popular-vote margin,
   D minus R, 2026 (preliminary)". Expected: **+13.1 pts**.
3. Card (static text) — "Largest Democratic popular-vote share in
   the 1994–2026 series: 55.8% (preliminary)". Type this in as text;
   it is the `[House Popular Vote D 2026]` value.
4. `[Senate Net Change D 2026]` — "Net Senate seats, Democrats 2026
   (preliminary)". Expected: **+8**.

**Main visual — clustered column chart, "Net House seat change by
cycle, 2018 vs 2022 vs 2026":** X-axis `dim_cycle[cycle]`, values
`[House Net Change D]`, visual filter `cycle` in (2018, 2022, 2026)
and `office_key = HOU` is inside the measure. Three bars: 2018 +41,
2022 −9, 2026 +40. Data labels on. Takeaway: "2026 is the mirror
image of 2022 — and the second-largest Democratic midterm gain in
the series after 2018."

**Supporting visual — line chart, "National House popular-vote
share by party, 1994–2026 (preliminary for 2026)":** X-axis
`dim_cycle[cycle]` (filter `election_type = midterm`), values
`[Dem House Vote Share]` and `[Rep House Vote Share]`. Markers on.
Takeaway: "The Democratic vote share in 2026 (55.8%) is the highest
in the nine-cycle series; 2022 was 47.3%."

**Second supporting visual — filled map, "Democratic House seats
gained or lost by state, 2022 → 2026 (preliminary)":** Location
`dim_geography[state_abbr]` (set the data category to State or
Province), colour saturation `[Dem Seats Change 2022 to 2026]`.
Diverging scale: muted red for losses, grey at 0, muted blue for
gains. Tooltips: add `dim_geography[state_name]` and
`[Dem Seats Change 2022 to 2026]` to the Tooltips bucket, so
hovering a state shows its name and its seat change. Footnote under the map, 9 pt grey: "Alaska, Louisiana and
North Carolina have no 2026 seat split in the source table and are
blank. Seat changes partly reflect mid-decade redistricting in
California and Texas, not only votes." Takeaway: "The gains were
concentrated: California +8 and New York +5 account for 13 seats;
only Maine lost a Democratic seat."

**How to read this:** "Net change compares the seats each party
held before the election with the seats it won. The popular-vote
share is the share of all votes cast for House candidates
nationwide. A big seat gain and a big vote margin usually go
together — in 2026 they did."

## Page 3 — Texas Deep-Dive

**Headline band:** "Texas flipped in 2026: Democrats won the
governorship, the Senate seat and the Attorney General's office —
after losing the governorship by 11 points in 2022."

**KPI row (4 cards):**

1. Card — measure `[Texas Dem Margin]` filtered to
   `office = Governor`, `cycle = 2026`. Title: "Governor margin
   2026, D minus R (preliminary)". Expected: **+7.1 pts**.
2. Card — same measure filtered to `office = Senate`,
   `cycle = 2026`. Title: "Senate margin 2026 (preliminary)".
   Expected: **+12.1 pts**.
3. Card — same measure filtered to `office = Attorney General`,
   `cycle = 2026`. Title: "Attorney General margin 2026
   (preliminary)". Expected: **+6.5 pts**.
4. Card — `[Texas House Dem Seats]` filtered to `cycle = 2026`.
   Title: "Texas House delegation, Democratic seats 2026
   (preliminary)". Expected: **14 of 38**.

**Main visual — line chart, "Texas statewide two-party margin,
2014–2026 (preliminary for 2026)":** X-axis
`fact_texas_statewide[cycle]`, Y-axis `[Texas Dem Margin]`,
legend `fact_texas_statewide[office]`. Three lines (Governor,
Senate, President). Add a constant line at 0 (Analytics pane) and
label it "Even". Markers on. Takeaway: "The governor's race
narrowed for a decade — R +20.4 in 2014, R +13.3 in 2018,
R +10.9 in 2022 — then flipped to D +7.1 in 2026."

**Supporting visual — clustered column chart, "Texas House
delegation by party":** X-axis `fact_results[cycle]` (filter
2014, 2018, 2022, 2026), values `[Texas House Dem Seats]` and
`[Texas House Rep Seats]`, legend `fact_results[party_name]` is
not needed — the two measures are the series. Data labels on.
Takeaway: "The delegation moved one seat: 13 D / 25 R in 2022 to
14 D / 24 R in 2026 — but Texas redrew its maps before 2026, so
this is not a pure vote swing."

**Supporting table — "Flipped Texas races, 2026":** a table visual
with `fact_texas_statewide[office]`,
`fact_texas_statewide[dem_candidate]`,
`fact_texas_statewide[dem_pct]`,
`fact_texas_statewide[rep_candidate]`,
`fact_texas_statewide[rep_pct]`, visual filter `cycle = 2026`,
`office` in (Governor, Senate, Attorney General). Three rows.

**How to read this:** "The margin is the Democratic candidate's
share minus the Republican's, in points. A positive number means
the Democrat led. Republicans have held every Texas statewide
office since the 1990s — this page shows whether 2026 broke,
narrowed or confirmed that pattern, with margins, not adjectives.
Note the presidential line moved the other way: Texas voted
Republican for president by 13.9 points in 2024."

## Page 4 — Why This One Was Different

**Headline band:** "Turnout, competitiveness and money all moved —
but the 2026 turnout figure is not published yet, so that part of
the story is still open."

**KPI row (4 cards):**

1. Card — `[Turnout Rate]` filtered to `cycle = 2022`. Title:
   "National turnout (VEP), 2022". Expected: **46.12%**.
2. Card (static text) — "National turnout (VEP), 2026: **not yet
   published**". Type this in as text. Do not put a number here.
3. Card — `[Races Under 10 Pts]` filtered to `cycle = 2022`.
   Title: "House races decided by under 10 pts, 2022". Expected:
   **74**.
4. Card — `[Total Receipts]` filtered to `cycle = 2026`. Title:
   "House + Senate candidate receipts, 2026 (preliminary)".
   Expected: **$4,199,069,691**.

**Main visual — line chart, "National turnout (VEP) by midterm,
1994–2022":** X-axis `fact_turnout[cycle]`, values `[Turnout
Rate]`, visual filter `geography_level = national`,
`election_type` is not in this table — filter `cycle` to the nine
midterms (1994–2022) in the visual filter pane. Markers on, data
labels on for 2018 (50.05%) and 2022 (46.12%). The line ends at
2022 because 2026 is blank. Takeaway: "Turnout peaked in 2018 at
50.05% and stayed high in 2022 at 46.12%. Whether 2026 beat them
is not yet knowable."

**Supporting visual — clustered column chart, "House races decided
by under 5 / under 10 points":** X-axis
`fact_house_closest_races[cycle]`, values `[Races Under 5 Pts]`
and `[Races Under 10 Pts]`. Two bars per cycle (2018: 43 under 5 /
89 under 10; 2022: 37 under 5 / 74 under 10). Data labels on. Takeaway: "Close races got rarer: 89 races were
decided by under 10 points in 2018, 74 in 2022. No 2026 figures
exist yet."

**Supporting visual — clustered column chart, "Total candidate
receipts by cycle":** X-axis `fact_finance[cycle]`, values
`[House Receipts]` and `[Senate Receipts]`, stacked. Three bars
(2018, 2022, 2026). Format the Y-axis as $ billions (display
units: billions, 1 decimal). Takeaway: "Money kept rising — $3.1bn
in 2018, $4.1bn in 2022, $4.2bn in 2026 — but the 2026 figure is
a mid-cycle snapshot (filings to 2026-10-14) and will rise."

**How to read this:** "VEP turnout counts ballots against the
voting-eligible population, not all adults. 'Under 10 points'
means the winner's margin was less than 10 percentage points.
Receipts are what candidates reported to the FEC; the 2026 file
is incomplete because post-election reports had not arrived."

## Page 5 — The Midterm Pattern

**Headline band:** "The president's party has lost House seats in
7 of the last 9 midterms. 2026 confirmed the pattern — and was the
second-largest loss in the series."

**KPI row (3 cards):**

1. Card (static text) — "Midterms where the president's party lost
   seats: **7 of 9** (1994–2026)".
2. Card (static text) — "Exceptions: **1998 (+5) and 2002 (+8)** —
   the only midterms where the president's party gained seats."
3. Card — `[Presidents Party Net Change]` filtered to
   `cycle = 2026`. Title: "President's-party net House change,
   2026 (preliminary)". Expected: **−56**.

**Main visual — clustered column chart, "President's-party net
House seat change, every midterm 1994–2026 (preliminary for
2026)":** X-axis `dim_cycle[cycle]`, values
`[Presidents Party Net Change]`, visual filter
`dim_cycle[election_type] = midterm`. Nine bars. Conditional
formatting on the bars by value: negative → muted red #B56A5E,
positive → muted blue #5B7FA6 (Format → Columns → Colors → fx →
Rules, based on the measure). Data labels on, showing the signed
number. Takeaway: "Losses range from 9 seats (2022) to 64 (2010).
2026's loss of 56 is the second-largest."

**Supporting visual — clustered column chart, "Senate net change
(Democratic), by midterm":** X-axis `fact_senate_composition[cycle]`,
values `[Senate Net Change D]`, visual filter
`election_type` is not in this table — filter `cycle` to the nine
midterms in the visual filter pane. Takeaway: "The Senate does not
follow the same pattern — it moved by small amounts in most
midterms, then +8 for Democrats in 2026." Footnote under the
visual, 9 pt grey: "Change in chamber composition between
Congresses, not the election-night flip count — see the data
dictionary note on fact_senate_composition (2006: +5 not +6;
2018: −1 not −2)."

**How to read this:** "Each bar is one midterm. A negative bar
means the president's party ended the election with fewer House
seats than it had before it. The pattern is a description of nine
elections, not a law — two of the nine broke it."

## Page 6 — What Changes Now

**Headline band:** "Democrats control the House and the Senate in
2026, but not the presidency — so there is no trifecta
(preliminary)."

**KPI row (4 cards):**

1. Card — `[House Majority 2026]`. Title: "House majority, 2026
   (preliminary)". Expected: **Democratic**.
2. Card — `[Senate Majority 2026]`. Title: "Senate majority, 2026
   (preliminary)". Expected: **Democratic**.
3. Card — `[Trifecta 2026]` formatted as Yes/No. Title: "Single-
   party control of House, Senate and presidency (trifecta), 2026".
   Expected: **No**.
4. Card — `[Senate Flips 2026]`. Title: "Senate seats that flipped
   party, 2026 (preliminary)". Expected: **6 named**.

**Main visual — table, "Control by cycle":** a table visual with
`dim_cycle[cycle]`, `dim_cycle[president_party]`,
`dim_cycle[house_majority]`, `dim_cycle[senate_majority]`,
`dim_cycle[trifecta]`, filtered to `election_type = midterm` and
sorted by cycle descending. Nine rows (1994–2026). Takeaway:
"Control of the House and Senate has split in most midterms;
2026 gives Democrats both chambers."

**Supporting visual — table, "Flipped Senate seats, 2026
(preliminary)":** a table visual with
`fact_senate_flips_2026[state]`,
`fact_senate_flips_2026[winner]`,
`fact_senate_flips_2026[winner_party]`,
`fact_senate_flips_2026[incumbent]`,
`fact_senate_flips_2026[incumbent_party]`. Six rows. Footnote
under the table, 9 pt grey: "A seventh seat flipped Republican
to Democratic in the composition table but is not named on the
source page — see docs/findings.md."

**Supporting visual — table, "Split-ticket states, 2026
(preliminary)" (Enter Data):** Home → Enter data. Columns: state,
governor party, House delegation majority. Four rows, from the
scorecard's "Split outcomes" sheet: Georgia / Democratic /
Republican; New Hampshire / Republican / Democratic; Texas /
Democratic / Republican; Vermont / Republican / Democratic. Title
the visual "States where the governor and the House delegation
went to different parties, 2026". Takeaway: "Four states split
their ticket in 2026, down from seven in 2022."

**How to read this:** "Control means which party holds the
majority of seats. A trifecta is one party holding the House, the
Senate and the presidency at the same time. The flips table names
the six Senate seats the results page identifies; the seventh is
counted in the composition but not named."

## Page 7 — State Detail (hidden drill-through target)

This page is NOT one of the six dashboard pages. Build it, then
right-click the page tab → Hide page. It is the drill-through
target for the maps on pages 2 and 6.

**Drill-through field:** drag `dim_geography[state_abbr]` into
the Drill through → "Drill through on" bucket, and turn on
"Keep all filters".

**Headline band:** a text box: "State detail — " followed by the
state name. Use a card with `SELECTEDVALUE(dim_geography
[state_name])` as its value if you want the name to update, or
type the field into the text box with the field well (Insert →
Text box → select the field). Simplest reliable method: a card
visual with measure `State Name =
SELECTEDVALUE ( dim_geography[state_name] )`.

**Visuals (all filtered by the drill-through field):**

1. Two cards — `State Dem Seats 2026` and `State Rep Seats 2026`
   (measures below, in `dax_measures.md` under "State Detail page").
   Democratic seats 2026, Republican seats 2026.
2. Card — `State Governor 2026` (measure below).
3. Table — presidential two-party share: `fact_results` filtered
   to `office_key = PRE`, `party_name = Democratic`, columns
   `cycle`, `vote_share_pct`, sorted by cycle. Shows 2020 vs 2024.
4. Card — 2022 turnout: `[Turnout Rate]` with a visual filter
   `geography_level = state` (the drill-through state filters it).

**Tooltips:** on the page 2 map, add `dim_geography[state_name]`
and `[Dem Seats Change 2022 to 2026]` to the Tooltips bucket, so
hovering a state shows its name and its seat change before the
user drills through.

**To wire drill-through:** on page 2's map, right-click a state →
Drill through → State Detail. Test it on California (should show
Democratic seats 48 in 2026) and on Maine (should show Democratic
seats 1 in 2026, down from 2).

## Final QA checklist (run before screenshotting for LinkedIn)

- [ ] Theme applied: no default Power BI blue on any visual; all
      pages have a white background.
- [ ] Every page has a headline band, a KPI row, a main visual, a
      supporting visual and a "How to read this" box.
- [ ] Every 2026 figure carries "(preliminary)" in its title or in
      a text box directly under the visual.
- [ ] KPI cards match the expected values in `dax_measures.md`
      (House D 254 / R 162; Senate D 53 / R 45 / I 2; Governors
      D 22 / R 12; House net D +40; popular-vote margin +13.1 pts).
- [ ] The page 2 map leaves Alaska, Louisiana and North Carolina
      blank and carries the footnote explaining why.
- [ ] The page 4 turnout line ends at 2022 and the 2026 card says
      "not yet published" (no invented number).
- [ ] The page 5 Senate chart carries the composition-convention
      footnote.
- [ ] The page 6 flips table has 6 rows and the footnote about the
      7th unnamed flip.
- [ ] Drill-through works from the page 2 map to State Detail and
      back (right-click → Drill through → State Detail; the back
      button returns).
- [ ] Chart titles are conclusions, not field names.
- [ ] No visual shows a 2026 competitiveness figure, a county map,
      or a 2026 turnout rate — none of those exist in the data.
- [ ] Spellcheck the headline bands: the takeaways must match
      `docs/findings.md` word for word in their numbers.
