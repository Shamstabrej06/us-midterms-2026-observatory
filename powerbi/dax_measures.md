# DAX Measures — US Midterms Observatory 2026

Every measure below is written out in full. Paste each one into
**Modeling → New measure** in Power BI Desktop, keeping the name
exactly as shown. All measures are written against the tables in
`powerbi/gold/` (11 CSVs) with the relationships listed in
`docs/data_dictionary.md`.

Conventions used throughout:

- `fact_results` holds BOTH national rows (`geography_level =
  "national"`) and state rows (`geography_level = "state"`). Every
  House/Senate/Governor measure filters `geography_level` explicitly
  — a measure without that filter double-counts.
- `vote_share_pct` and `turnout_rate_pct` are stored as plain numbers
  (55.8 means 55.8%). Format them as numbers with a `"%"` suffix, not
  as Power BI percentages (which would multiply by 100).
- Money is stored in dollars. Format money measures as currency with
  zero decimals.
- 2026 figures are preliminary. Any card or visual showing a 2026
  number must carry the text "(preliminary)" — see the build guide.
- Two numbers on the dashboard CANNOT be built in DAX and are given
  as **static KPI cards** at the end of this file (top-spender win
  rate, split-outcome count). They are computed values from
  `docs/findings.md` — paste them, do not try to calculate them.

## Page 1 — The Night

```dax
House Seats D 2026 =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Democratic"
)
```

```dax
House Seats R 2026 =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Republican"
)
```

```dax
House Seats Uncalled 2026 =
435 - [House Seats D 2026] - [House Seats R 2026]
```

```dax
House Net Change D 2026 =
CALCULATE (
    SUM ( fact_results[net_change] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Democratic"
)
```

```dax
House Net Change R 2026 =
CALCULATE (
    SUM ( fact_results[net_change] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Republican"
)
```

```dax
House Popular Vote D 2026 =
CALCULATE (
    MAX ( fact_results[vote_share_pct] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Democratic"
)
```

```dax
House Popular Vote R 2026 =
CALCULATE (
    MAX ( fact_results[vote_share_pct] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Republican"
)
```

```dax
House Popular Vote Margin 2026 =
[House Popular Vote D 2026] - [House Popular Vote R 2026]
```

```dax
Senate Seats D 2026 =
CALCULATE (
    SUM ( fact_senate_composition[seats_after] ),
    fact_senate_composition[cycle] = 2026,
    fact_senate_composition[party_name] = "Democratic"
)
```

```dax
Senate Seats R 2026 =
CALCULATE (
    SUM ( fact_senate_composition[seats_after] ),
    fact_senate_composition[cycle] = 2026,
    fact_senate_composition[party_name] = "Republican"
)
```

```dax
Senate Seats I 2026 =
CALCULATE (
    SUM ( fact_senate_composition[seats_after] ),
    fact_senate_composition[cycle] = 2026,
    fact_senate_composition[party_name] = "Independent"
)
```

```dax
Senate Net Change D 2026 =
CALCULATE (
    SUM ( fact_senate_composition[net_change] ),
    fact_senate_composition[cycle] = 2026,
    fact_senate_composition[party_name] = "Democratic"
)
```

```dax
Gov Wins D 2026 =
COUNTROWS (
    FILTER (
        fact_results,
        fact_results[cycle] = 2026
            && fact_results[office_key] = "GOV"
            && fact_results[winner_party] = "Democratic"
    )
)
```

```dax
Gov Wins R 2026 =
COUNTROWS (
    FILTER (
        fact_results,
        fact_results[cycle] = 2026
            && fact_results[office_key] = "GOV"
            && fact_results[winner_party] = "Republican"
    )
)
```

```dax
Gov Races Uncalled 2026 =
COUNTROWS (
    FILTER (
        fact_results,
        fact_results[cycle] = 2026
            && fact_results[office_key] = "GOV"
            && ISBLANK ( fact_results[winner_party] )
    )
)
```

Expected values (check the cards against these): House D 254, R 162,
uncalled 19; House net D +40, R −56; House popular vote D 55.8%,
R 42.7%, margin +13.1 pts; Senate D 53, R 45, I 2, net D +8;
Governors D 22, R 12, uncalled 2.

## Page 2 — The Comeback, Measured

```dax
House Seats D =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[party_name] = "Democratic"
)
```

```dax
House Seats R =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[party_name] = "Republican"
)
```

```dax
House Net Change D =
CALCULATE (
    SUM ( fact_results[net_change] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[party_name] = "Democratic"
)
```

```dax
Dem House Vote Share =
CALCULATE (
    MAX ( fact_results[vote_share_pct] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[party_name] = "Democratic"
)
```

```dax
Rep House Vote Share =
CALCULATE (
    MAX ( fact_results[vote_share_pct] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "national",
    fact_results[party_name] = "Republican"
)
```

```dax
House Vote Margin D minus R =
[Dem House Vote Share] - [Rep House Vote Share]
```

```dax
Dem Seats Change 2022 to 2026 =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "state",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Democratic"
)
    - CALCULATE (
        SUM ( fact_results[seats_after] ),
        fact_results[office_key] = "HOU",
        fact_results[geography_level] = "state",
        fact_results[cycle] = 2022,
        fact_results[party_name] = "Democratic"
    )
```

Use `[Dem Seats Change 2022 to 2026]` in the state map on this page
(`dim_geography[state_abbr]` as the location). Alaska, Louisiana and
North Carolina will be blank — they have no 2026 seat split in the
source table. Do not fill them in; the map's footnote says so.

Expected values: 2018 — D seats 235, net D +41, vote D 53.4%;
2022 — D seats 213, net D −9, vote D 47.29%; 2026 — D seats 254,
net D +40, vote D 55.8%, margin +13.1 pts. State swing: California
+8, New York +5, Iowa +3, Ohio +3, Maine −1.

## Page 3 — Texas Deep-Dive

`fact_texas_statewide` has no relationships to the dimension tables,
so these measures filter it directly. Do not expect a cycle slicer
from `dim_cycle` to filter this page's visuals — the visuals carry
their own `cycle` field.

```dax
Texas Dem Margin =
CALCULATE (
    MAX ( fact_texas_statewide[margin_pts] ),
    fact_texas_statewide[state] = "Texas"
)
```

```dax
Texas Dem Pct =
CALCULATE (
    MAX ( fact_texas_statewide[dem_pct] ),
    fact_texas_statewide[state] = "Texas"
)
```

```dax
Texas Rep Pct =
CALCULATE (
    MAX ( fact_texas_statewide[rep_pct] ),
    fact_texas_statewide[state] = "Texas"
)
```

```dax
Texas House Dem Seats =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "state",
    fact_results[state_abbr] = "TX",
    fact_results[party_name] = "Democratic"
)
```

```dax
Texas House Rep Seats =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "state",
    fact_results[state_abbr] = "TX",
    fact_results[party_name] = "Republican"
)
```

Expected values: Governor margin — 2014 −20.4, 2018 −13.3,
2022 −10.9, 2026 +7.1. Senate margin — 2014 −28.4, 2018 −2.6,
2020 −9.9, 2024 −8.7, 2026 +12.1. Attorney General 2026 +6.5.
Texas House delegation — 2022 D 13 / R 25; 2026 D 14 / R 24.
Margins are Democratic minus Republican; positive = Democratic lead.

## Page 4 — Why This One Was Different

```dax
Turnout Rate =
CALCULATE (
    MAX ( fact_turnout[turnout_rate_pct] ),
    fact_turnout[geography_level] = "national"
)
```

The 2026 row has a blank rate (`status` = "not yet published"), so
the line chart ends at 2022. That gap is the point — do not connect
the line across it and do not type in an estimate.

```dax
Races Under 5 Pts =
COUNTROWS (
    FILTER (
        fact_house_closest_races,
        fact_house_closest_races[margin_pts] < 5
    )
)
```

```dax
Races Under 10 Pts =
COUNTROWS ( fact_house_closest_races )
```

`fact_house_closest_races` IS the under-10-points set (largest
margin 9.86 in 2018, 9.95 in 2022), so the under-10 count is the
row count in the current filter context. Filter the visual to one
cycle at a time or use `cycle` on the axis.

```dax
Total Receipts =
SUM ( fact_finance[total_receipts] )
```

```dax
House Receipts =
CALCULATE (
    SUM ( fact_finance[total_receipts] ),
    fact_finance[office] = "H"
)
```

```dax
Senate Receipts =
CALCULATE (
    SUM ( fact_finance[total_receipts] ),
    fact_finance[office] = "S"
)
```

```dax
Candidates Count =
COUNTROWS ( fact_finance )
```

Expected values: turnout 2014 36.70%, 2018 50.05%, 2022 46.12%,
2026 blank. Competitiveness — 2018: 89 under 10 (43 under 5);
2022: 74 under 10 (37 under 5). Money (combined House + Senate) —
2018 $3,125,950,077; 2022 $4,139,563,155; 2026 $4,199,069,691
(preliminary, coverage to 2026-10-14).

## Page 5 — The Midterm Pattern

```dax
Presidents Party Net Change =
VAR PresParty =
    SELECTEDVALUE ( dim_cycle[president_party] )
RETURN
    CALCULATE (
        SUM ( fact_results[net_change] ),
        fact_results[office_key] = "HOU",
        fact_results[geography_level] = "national",
        fact_results[party_name] = PresParty
    )
```

Use this measure in a bar chart with `dim_cycle[cycle]` on the
axis, filtered to `dim_cycle[election_type] = "midterm"`. Each bar
is one cycle's president's-party net House change. Colour bars by
sign with conditional formatting (negative = muted red #B56A5E,
positive = muted blue #5B7FA6) — do not colour by party, the point
is the pattern, not the party.

```dax
Senate Net Change D =
CALCULATE (
    SUM ( fact_senate_composition[net_change] ),
    fact_senate_composition[party_name] = "Democratic"
)
```

Use in the supporting visual (Senate composition change by cycle).
Read the convention note in `docs/data_dictionary.md` before
presenting it: this is the change in chamber composition between
Congresses, not the election-night flip count (2006: +5 not +6;
2018: −1 not −2).

Expected values (House, president's party): 1994 D −54, 1998 D +5,
2002 R +8, 2006 R −30, 2010 D −64, 2014 D −13, 2018 R −42,
2022 D −9, 2026 R −56. The pattern held in 7 of 9 midterms.

## Page 6 — What Changes Now

```dax
House Majority 2026 =
CALCULATE (
    MAX ( dim_cycle[house_majority] ),
    dim_cycle[cycle] = 2026
)
```

```dax
Senate Majority 2026 =
CALCULATE (
    MAX ( dim_cycle[senate_majority] ),
    dim_cycle[cycle] = 2026
)
```

```dax
Trifecta 2026 =
CALCULATE (
    MAX ( dim_cycle[trifecta] ),
    dim_cycle[cycle] = 2026
)
```

`dim_cycle[trifecta]` is TRUE/FALSE. Format the card as Yes/No
(2026: No — the parties split control of the House and Senate, so
there is no trifecta).

```dax
Senate Flips 2026 =
COUNTROWS ( fact_senate_flips_2026 )
```

Expected value: 6 named flips (the 7th is counted in the Senate
composition but not named on the source page — see findings.md).
The flips table visual uses `fact_senate_flips_2026` columns
directly: state, winner, winner_party, incumbent, incumbent_party.

## State Detail page (drill-through target)

```dax
State Name =
SELECTEDVALUE ( dim_geography[state_name] )
```

```dax
State Dem Seats 2026 =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "state",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Democratic"
)
```

```dax
State Rep Seats 2026 =
CALCULATE (
    SUM ( fact_results[seats_after] ),
    fact_results[office_key] = "HOU",
    fact_results[geography_level] = "state",
    fact_results[cycle] = 2026,
    fact_results[party_name] = "Republican"
)
```

```dax
State Governor 2026 =
CALCULATE (
    MAX ( fact_results[winner_party] ),
    fact_results[office_key] = "GOV",
    fact_results[cycle] = 2026
)
```

## Static KPI cards (paste the value — do not build a DAX measure)

These two numbers cannot be calculated in DAX from the gold layer,
because they need candidate-name matching across sources (FEC vs
results tables) that lives in `src/04_findings.py`. They are computed
values, already verified. Make a card visual, type the value in as
the card's text, and add the source note underneath.

| Card text | Value | Source |
|---|---|---|
| Top-spender win rate, Senate 2026 | **29 of 31 races (93.5%)** | `docs/findings.md` → Money; `outputs/Findings_Scorecard.xlsx` → Money. Method: top FEC spender among the candidates listed for each race. 2018: 29/35 (82.9%). 2022: 28/35 (80.0%). The two 2026 misses: Minnesota (Tafoya outspent Flanagan) and Montana (Bodnar outspent Alme). |
| Split-ticket states 2026 | **4 states** | `docs/findings.md` → Split outcomes. 2022: 7 states. The 4: Georgia, New Hampshire, Texas, Vermont. Use **Home → Enter data** to build the 4-row table for this page (columns: state, governor party, House delegation majority) with the values from the scorecard's "Split outcomes" sheet. |

## Measures NOT to build

- A DAX top-spender win rate. The gold layer has no House winners
  and no 2026 Senate winner names, so any DAX version of it would
  silently count the wrong races. Use the static card above.
- A DAX split-outcome count. It needs a per-state join of governor
  winners to House delegation majorities that the star schema does
  not support cleanly. Use the static card and the Enter Data table.
- A 2026 turnout rate. No VEP denominator has been published. The
  card on page 4 must read "Not yet published", not a number.
